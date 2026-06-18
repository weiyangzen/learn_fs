# sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qed/qed_dcbx.c

## Purpose

`qed_dcbx.c` implements Data Center Bridging Exchange handling for QED PFs. It reads LLDP/DCBX MIBs from MCP public memory, parses operational/local/remote DCBX features, updates protocol traffic-class/priority state, triggers QM and firmware PF updates after negotiation changes, exposes DCBX state to protocol callbacks, and implements the Linux DCB netlink operations when `CONFIG_DCB` is enabled.

## Important APIs, Types, and Functions

- TLV classifiers: `qed_dcbx_*_tlv()` helpers identify ETH default, iSCSI, FCoE, RoCE, and RoCEv2 application TLVs from MFW app entries, including IEEE selector compatibility for older MFW values.
- Protocol result updates: `qed_dcbx_set_params()` and `qed_dcbx_update_app_info()` fill `struct qed_dcbx_results` per protocol, set offload TC for matching personalities, set VLAN0 behavior, and configure UFP/RoCE EDPM doorbell priority overrides.
- MIB parsing: `qed_dcbx_process_tlv()` parses app priority entries, falls back for missing ETH TLVs, and applies defaults. `qed_dcbx_process_mib_info()` updates active TC count, OOO TC, PF ID, enabled state, and cached results.
- MIB reading: `qed_dcbx_copy_mib()` retries until prefix/suffix sequence numbers match; `qed_dcbx_read_*_mib()` functions map each MIB type to MCP public memory offsets; `qed_dcbx_read_mib()` dispatches by `enum qed_mib_read_type`.
- Query/export helpers: `qed_dcbx_get_*_params()` populate `struct qed_dcbx_get` views for operational, local, remote, and LLDP data. `qed_dcbx_get_priority_tc()` maps a priority to the operational ETS TC.
- Event entry point: `qed_dcbx_mib_update_event()` is the core update path. For operational changes it reads the MIB, processes results, reconfigures QM, sends a PF update ramrod, updates RoCE DPM behavior, programs NIG EDPM TC enablement, refreshes cached get-data, and emits an AEN callback.
- Allocation and PF update: `qed_dcbx_info_alloc()`, `qed_dcbx_info_free()`, and `qed_dcbx_set_pf_update_params()` own the per-HWFN DCBX state and copy negotiated protocol data into slowpath ramrod payloads.
- `CONFIG_DCB` configuration path: `qed_dcbx_get_config_params()` and `qed_dcbx_config_params()` manage cached set parameters, local-admin MIB writes, and MCP `DRV_MSG_CODE_SET_DCBX` commits.
- DCB netlink operations: `qed_dcbnl_ops_pass` binds get/set callbacks for state, PFC, ETS, app entries, DCBX mode, CEE peer data, IEEE PFC/ETS/app data, and feature flags.

## Control Flow

For asynchronous firmware updates, `qed_dcbx_mib_update_event()` reads the requested MIB. Operational updates then parse app/ETS/PFC data into protocol results, reconfigure queue manager TCs through `qed_qm_reconf()`, notify firmware via `qed_sp_pf_update()`, adjust RoCE DPM if applicable, program NIG EDPM TC bits, refresh the cached `qed_dcbx_get` view, and notify upper-layer callbacks with `dcbx_aen`.

For user configuration under `CONFIG_DCB`, dcbnl setters call `qed_dcbx_get_config_params()` to get a mutable cached config derived from current operational data, set override flags and fields, acquire a PTT, and call `qed_dcbx_config_params(..., hw_commit=false)` to cache changes. `setall` later calls the same function with `hw_commit=true`, which builds a local-admin MIB, writes it to MCP public memory, and sends the MCP SET_DCBX command.

For dcbnl getters, callbacks allocate a temporary `qed_dcbx_get`, query the relevant MIB through PTT-protected reads, validate operational state/mode when necessary, translate QED internal params into Linux DCB/CEE/IEEE structures, and free the temporary buffer.

## State and Persistence Behavior

Per-HWFN DCBX state lives in `p_hwfn->p_dcbx_info`, allocated by `qed_dcbx_info_alloc()`. It caches local and remote LLDP parameters, local-admin config, operational and remote DCBX MIBs, negotiated `results`, pending set parameters, and the last `get` snapshot. Hardware/firmware state persists in MCP public memory and device registers; the driver-side cache is rebuilt on reload and refreshed by MIB reads. Pending dcbnl changes can remain cached in `p_dcbx_info->set` until committed by `setall`.

## Dependencies and Integration Points

The file integrates with MCP public memory (`qed_memcpy_from/to`, `qed_mcp_cmd`, `public_port` offsets), PTT/GRC access, QM reconfiguration, slowpath PF update ramrods, RoCE DPM policy, SR-IOV/VF restrictions, multi-function flags, Linux DCB netlink structures, and upper-layer common callbacks. It depends heavily on MFW bitfield macros from `qed_hsi.h` and public QED Ethernet interface types when `CONFIG_DCB` is enabled.

## Risks and Edge Cases

- `qed_dcbx_copy_mib()` retries up to 100 times for stable sequence numbers; repeated instability returns `-EIO`.
- `qed_dcbx_process_tlv()` uses `ffs(priority_map) - 1` and rejects empty priority maps. Some dcbnl setters store either priority numbers or priority bitmaps depending on CEE versus IEEE paths, so translations must stay consistent.
- Operational DCBX disabled state causes many getters to return no data or defaults.
- DCBX configuration is blocked for VFs in query paths.
- The local-admin write starts from operational features and applies override flags; missing override flags intentionally preserve negotiated/current data.
- `qed_dcbnl_setstate()` and many setters cache changes with `hw_commit=false`, so userspace must call the commit path (`setall`) to push to firmware.
- App table capacity is limited to `DCBX_CONFIG_MAX_APP_PROTOCOL`; setters return `-EBUSY` if no empty slot exists.
- IEEE-only getters/setters reject non-IEEE operational modes.

## Test Signals

Strong signals include kernel build with and without `CONFIG_DCB`, LLDP/DCBX negotiation tests against IEEE and CEE peers, MIB sequence retry/failure injection, dcbtool/lldptool/iproute2 DCB getter/setter coverage, `setall` commit verification through MCP-visible local-admin MIB changes, QM TC changes after operational updates, PF update ramrod payload inspection, RoCE DPM behavior after priority changes, and VF rejection tests.
