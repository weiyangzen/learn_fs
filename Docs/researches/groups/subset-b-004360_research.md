# subset-b-004360 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bnx2x/bnx2x_dcb.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bnx2x/bnx2x_dcb.c

## Purpose
Implements Data Center Bridging support for the Broadcom/QLogic `bnx2x` Ethernet driver. The file translates firmware/MFW DCBX negotiation results from shared LLDP/DCBX MIBs into driver state, traffic-class mapping, priority flow control programming, ETS scheduling, firmware TX-start parameters, and optional DCB netlink callbacks.

## Important APIs, Types, and Functions
The exported runtime entry points are `bnx2x_dcbx_set_params`, `bnx2x_dcbx_set_state`, `bnx2x_dcbx_init_params`, `bnx2x_dcbx_init`, `bnx2x_dcbx_pmf_update`, `bnx2x_dcbx_stop_hw_tx`, and `bnx2x_dcbx_resume_hw_tx`. When `BCM_DCBNL` is enabled, it also exports `bnx2x_dcbnl_ops` and `bnx2x_dcbnl_update_applist`.

The MIB path uses `bnx2x_dcbx_read_mib`, `bnx2x_dcbx_read_shmem_neg_results`, and `bnx2x_dcbx_read_shmem_remote_mib` to copy local/remote LLDP MIBs from shared memory with prefix/suffix sequence-number validation. Feature extraction is split across `bnx2x_dcbx_get_ap_feature`, `bnx2x_dcbx_get_pfc_feature`, `bnx2x_dcbx_get_ets_feature`, and `bnx2x_get_dcbx_drv_param`.

COS construction is the densest part of the file. The `bnx2x_dcbx_get_num_pg_traf_type`, `bnx2x_dcbx_fill_cos_params`, E2/E3A0 two-COS helpers, E3B0 three-COS helpers, `bnx2x_dcbx_join_pgs`, and `bnx2x_dcbx_spread_strict_pri` functions convert CEE priority groups, strict-priority PG 15, application priorities, and PFC pauseability into `bp->dcbx_port_params.ets.cos_params[]`.

Hardware programming is handled by `bnx2x_pfc_set`, `bnx2x_pfc_clear`, `bnx2x_pfc_set_pfc`, `bnx2x_dcbx_update_ets_params`, `bnx2x_dcbx_2cos_limit_update_ets_config`, `bnx2x_dcbx_update_ets_config`, and `bnx2x_dcbx_fw_struct`.

## Control Flow
The normal negotiation flow starts when attention handling in `bnx2x_main.c` calls `bnx2x_dcbx_set_params(..., BNX2X_DCBX_STATE_NEG_RECEIVED)`. That state deletes old dcbnl app TLVs, optionally reads the remote MIB, reads local negotiated results, logs them, derives software DCB parameters, marks `DRV_FLAGS_DCB_CONFIGURED`, re-adds app TLVs, schedules TC setup through `bnx2x_schedule_sp_rtnl`, notifies peer functions in multi-function mode, and schedules TX stop.

After TX is stopped, `BNX2X_DCBX_STATE_TX_PAUSED` applies PFC, applies ETS, and reinitializes local congestion management. After TX resumes, `BNX2X_DCBX_STATE_TX_RELEASED` sends `DRV_MSG_CODE_DCBX_PMF_DRV_OK` to firmware and emits a CEE dcbnl notification when built with DCBNL.

Initialization flows through `bnx2x_dcbx_init_params`, which seeds default admin CEE settings, and `bnx2x_dcbx_init`, which validates DCB enablement, takes `HW_LOCK_RESOURCE_DCBX_ADMIN_MIB`, updates the admin MIB if requested, sends `DRV_MSG_CODE_DCBX_ADMIN_PMF_MSG`, and releases the lock after MFW has acknowledged the read. PMF migration uses `bnx2x_dcbx_pmf_update` to reload previous PMF negotiation output from shared memory.

## State and Persistence Behavior
Persistent driver state is mostly in `struct bnx2x`: `dcb_state`, `dcbx_enabled`, `dcbx_mode_uset`, `dcbx_config_params`, `dcbx_port_params`, `dcbx_local_feat`, `dcbx_remote_feat`, `dcbx_error`, `dcbx_remote_flags`, `prio_to_cos`, and incrementing `dcb_version`. Firmware-visible persistence is in shmem2 LLDP/DCBX offsets, local/remote MIBs, admin MIBs, and driver flags such as `DRV_FLAGS_DCB_CONFIGURED` and `DRV_FLAGS_DCB_MFW_CONFIGURED`.

Hardware state is programmed through link/PHY helpers and function ramrods: PFC changes update NIG/MAC/BRB through `bnx2x_update_pfc`; ETS changes call `bnx2x_ets_disabled`, `bnx2x_ets_bw_limit`, `bnx2x_ets_strict`, or `bnx2x_ets_e3b0_config`; TX stop/start uses `bnx2x_func_state_change`.

## Dependencies and Integration Points
This file depends on `bnx2x.h`, `bnx2x_cmn.h`, `bnx2x_dcb.h`, `bnx2x_hsi.h` LLDP/DCBX layout definitions, DCB netlink APIs, shared-memory access macros, register access macros, PHY locks, hardware locks, link setup, slowpath rtnl scheduling, and firmware ramrod state machinery. Main-driver integration is visible in `bnx2x_main.c`: DCBX attention events call `bnx2x_dcbx_set_params`, rtnl work calls TX stop/resume and TC setup, PMF changes call `bnx2x_dcbx_pmf_update`, probe initializes DCB state, and `dev->dcbnl_ops` is set to `bnx2x_dcbnl_ops`.

## Risks
The main risk is incorrect reduction of negotiated ETS/PFC data into hardware-supported COS layouts, especially the E2/E3A0 two-COS limit, E3B0 three-COS limit, strict-priority PG 15, mixed pauseable/non-pauseable groups, and application priority defaults. MIB reads rely on sequence-number stability and fixed shared-memory offsets; stale or partially updated firmware data can disable features or program wrong priorities. DCBNL setters modify admin config in memory but only apply it through `setall`, so tests must verify the full set/commit path. Hardware programming is serialized through PHY/HW locks and TX stop/resume sequencing; regressions here can affect live traffic, PFC losslessness, ETS bandwidth, or multi-function synchronization.

## Test Signals
Useful signals include DCBX negotiation with FCoE/iSCSI/default app TLVs, CEE peer reads through dcbnl, `dcbtool`/`lldptool` setall flows, PMF migration, multi-function link sync, TX stop/resume completion, PFC frame counters, ETS bandwidth behavior under traffic, `setup_tc` queue count changes, and error injection for missing shmem offsets, mismatched MIB sequence numbers, remote MIB errors, and recovery-state rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bnx2x/bnx2x_dcb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bnx2x/bnx2x_dcb.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bnx2x/bnx2x_dcb.h

## Purpose
Defines the DCB/DCBX data model shared by the `bnx2x` core, DCB implementation, and optional DCB netlink support. It provides the software-side structures for application priorities, COS/ETS configuration, PFC masks, admin LLDP/DCBX configuration, and helper data used while converting negotiated CEE priority groups into hardware COS entries.

## Important APIs, Types, and Functions
Important public structs include `bnx2x_dcbx_app_params`, `bnx2x_dcbx_cos_params`, `bnx2x_dcbx_pg_params`, `bnx2x_dcbx_pfc_params`, `bnx2x_dcbx_port_params`, `bnx2x_config_lldp_params`, `bnx2x_admin_priority_app_table`, and `bnx2x_config_dcbx_params`. Internal algorithm helpers are represented by `cos_entry_help_data`, `cos_help_data`, `pg_entry_help_data`, and `pg_help_data`.

Important constants include `LLFC_DRIVER_TRAFFIC_TYPE_MAX`, `BNX2X_MAX_COS_SUPPORT`, `DCBX_COS_MAX_NUM`, strict-priority sentinel values, admin overwrite constants, `BNX2X_IS_ETS_ENABLED`, app protocol IDs for FCoE and iSCSI, PFC quanta/threshold values, illegal PG and invalid bandwidth sentinels, and macros that split priority masks into pauseable and non-pauseable sets.

The header declares `bnx2x_dcbx_update`, `bnx2x_dcbx_init_params`, `bnx2x_dcbx_set_state`, `bnx2x_dcbx_set_params`, `bnx2x_dcbx_pmf_update`, `bnx2x_dcbx_stop_hw_tx`, and `bnx2x_dcbx_resume_hw_tx`. Under `BCM_DCBNL`, it declares `bnx2x_dcbnl_ops` and `bnx2x_dcbnl_update_applist`.

## Control Flow
There is no direct runtime control flow in the header. Its macros drive branch decisions in `bnx2x_dcb.c`, especially pauseability checks such as `IS_DCBX_PFC_PRI_ONLY_PAUSE`, `IS_DCBX_PFC_PRI_ONLY_NON_PAUSE`, `IS_DCBX_PFC_PRI_MIX_PAUSE`, and `DCBX_IS_PFC_PRI_SOME_PAUSE`. The state enum gives the DCBX flow labels used by the attention/rtnl sequence: negotiated result received, TX paused for hardware reprogramming, and TX released.

## State and Persistence Behavior
The structs declared here are embedded in `struct bnx2x` and persisted for the lifetime of the PF instance. `bnx2x_config_dcbx_params` represents admin settings that can be copied into the firmware admin MIB. `bnx2x_dcbx_port_params` represents negotiated/effective runtime state. Sentinel values such as `BNX2X_DCBX_CONFIG_INV_VALUE`, `INVALID_TRAFFIC_TYPE_PRIORITY`, `DCBX_ILLEGAL_PG`, and `DCBX_INVALID_COS_BW` are part of the in-memory state contract.

## Dependencies and Integration Points
The header includes `bnx2x_hsi.h` for firmware-facing DCBX limits and MIB field helpers. It is consumed by `bnx2x_dcb.c`, `bnx2x.h`, `bnx2x_main.c`, and any build that wires DCBNL operations into `net_device`. Constants here must remain aligned with firmware CEE/DCBX definitions, hardware COS limits, and the queue setup path that maps priorities to COS/TC values.

## Risks
This header is hardware/firmware ABI-adjacent. Wrong COS limits, priority masks, invalid sentinels, or app protocol constants will make the implementation program bad PFC/ETS state while still compiling. The `bnx2x_dcbx_update` declaration appears without a matching definition in this source subset, which is a maintenance signal for stale API declarations or out-of-tree build variation. Macro type widths also matter because several masks are narrowed to `u8` in the implementation.

## Test Signals
Compile coverage with and without `BCM_DCBNL`, DCB-enabled and DCB-disabled probe paths, FCoE/iSCSI app priority mapping, PFC priority masks, E2/E3A0 versus E3B0 COS counts, and dcbnl operations that read/write `bnx2x_config_dcbx_params` are the primary validation signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bnx2x/bnx2x_dcb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bnx2x/bnx2x_dump.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bnx2x/bnx2x_dump.h

## Purpose
Provides the static register-dump metadata used by `bnx2x_ethtool.c` for ethtool register dumps and preset dumps. It describes supported chip masks, path markers, dump headers, regular register ranges, idle-check register ranges, CAM/windowed register descriptors, paged register selectors, and per-chip/per-preset register counts.

## Important APIs, Types, and Functions
The key exported-to-translation-unit definitions are `struct dump_header`, `struct reg_addr`, and `struct wreg_addr`. `BNX2X_DUMP_VERSION`, `DUMP_CHIP_E1`, `DUMP_CHIP_E1H`, `DUMP_CHIP_E2`, `DUMP_CHIP_E3A0`, `DUMP_CHIP_E3B0`, `DUMP_PATH_0`, `DUMP_PATH_1`, `NUM_PRESETS`, and `NUM_CHIPS` define the dump ABI consumed by ethtool users.

The large static tables are `reg_addrs`, `idle_reg_addrs`, chip-specific `wreg_addr_*` descriptors, `page_vals_e2/e3`, `page_write_regs_e2/e3`, `page_read_regs_e2/e3`, and `dump_num_registers`. `REGS_COUNT` and `IDLE_REGS_COUNT` wrap table sizes for the reader implementation.

## Control Flow
This header has no executable control flow except static initializers. Its data controls ethtool dump iteration in `bnx2x_ethtool.c`: chip/preset masks filter entries, `size` controls how many DWORDs are read from each base address, paged arrays define write-selector/read-window sequences for E2/E3, and `dump_num_registers[chip][preset]` is used to pre-size user buffers and advance output pointers.

## State and Persistence Behavior
All state is immutable static metadata compiled into the driver. Runtime dump state is produced by `bnx2x_ethtool.c` into user buffers and is not persisted here. The dump header written to userspace includes the preset, dump version, chip type, and path metadata so external decoders can interpret the raw register stream.

## Dependencies and Integration Points
`bnx2x_ethtool.c` includes this header directly and uses the tables in `get_regs_len`, `get_regs`, `set_dump`, `get_dump_flag`, and `get_dump_data`. The register addresses and masks must match the `bnx2x` hardware register map, the `REG_RD`/`REG_WR` access model, and any external diagnostic tooling that decodes `BNX2X_DUMP_VERSION` streams.

## Risks
The highest risk is table drift: a wrong register address, size, chip mask, preset mask, or count can cause invalid GRC reads, truncated dumps, oversized userspace reads, or false parity/GRC timeout reports. The implementation intentionally disables parity attentions around dumps because some reads can touch never-written registers; adding entries without understanding that behavior can create noisy or unsafe diagnostics. The `dump_num_registers` matrix must remain synchronized with the actual table expansion for every chip and preset.

## Test Signals
Validation signals include `ethtool -d` on E1/E1H/E2/E3A0/E3B0 hardware, preset-specific dump requests through `ETHTOOL_GET_DUMP_DATA`, matching output lengths against `get_regs_len`/`get_dump_flag`, absence of unhandled parity attentions after dump, and comparison of dump streams against known-good decoder expectations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bnx2x/bnx2x_dump.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bnx2x/bnx2x_ethtool.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bnx2x/bnx2x_ethtool.c

## Purpose
Implements the `bnx2x` ethtool interface for PFs and VFs. It exposes link settings, register dumps, firmware/driver info, wake-on-LAN, message levels, link reset, EEPROM/NVRAM and module EEPROM access, coalescing, ring sizes, pause settings, EEE, self-tests, statistics, physical identification LEDs, RSS hash configuration, RSS indirection, channel count, timestamp capabilities, and ethtool operation table selection.

## Important APIs, Types, and Functions
The top-level integration point is `bnx2x_set_ethtool_ops`, which installs either `bnx2x_ethtool_ops` for PFs or `bnx2x_vf_ethtool_ops` for VFs. Link operations include `bnx2x_get_link_ksettings`, `bnx2x_set_link_ksettings`, and the VF-specific `bnx2x_get_vf_link_ksettings`. Register dump operations include `bnx2x_get_regs_len`, `bnx2x_get_regs`, `bnx2x_set_dump`, `bnx2x_get_dump_flag`, and `bnx2x_get_dump_data`.

NVRAM/EEPROM helpers include `bnx2x_acquire_nvram_lock`, `bnx2x_release_nvram_lock`, `bnx2x_enable_nvram_access`, `bnx2x_disable_nvram_access`, `bnx2x_nvram_read_dword`, exported `bnx2x_nvram_read`, `bnx2x_nvram_read32`, `bnx2x_nvram_write_dword`, `bnx2x_nvram_write1`, `bnx2x_nvram_write`, `bnx2x_get_eeprom`, `bnx2x_set_eeprom`, `bnx2x_get_module_eeprom`, and `bnx2x_get_module_info`.

Self-test support is built around `bnx2x_test_registers`, `bnx2x_test_memory`, `bnx2x_run_loopback`, `bnx2x_test_loopback`, `bnx2x_test_ext_loopback`, `bnx2x_test_nvram`, `bnx2x_test_intr`, and `bnx2x_self_test`. Statistics and strings are driven by `bnx2x_q_stats_arr`, `bnx2x_stats_arr`, `bnx2x_tests_str_arr`, `bnx2x_private_arr`, `bnx2x_get_sset_count`, `bnx2x_get_strings`, and `bnx2x_get_ethtool_stats`.

RSS/channel operations include `bnx2x_get_rxfh_fields`, `bnx2x_set_rxfh_fields`, `bnx2x_get_rxfh_indir_size`, `bnx2x_get_rxfh`, `bnx2x_set_rxfh`, `bnx2x_get_channels`, `bnx2x_change_num_queues`, and `bnx2x_set_channels`.

## Control Flow
PF ethtool ops expose the full feature set; VF ops expose a reduced set that omits hardware-owned features such as register dumps, EEPROM writes, self-tests, WOL, pause, EEE, and module EEPROM. Link setting reads combine board-supported modes, active PHY media type, current link state, multi-function speed policy, autonegotiation state, and link-partner status. Link setting writes validate multi-function restrictions, requested port type, autoneg advertisements, forced speed/duplex support, and then update `link_params`; if the device is running, they stop stats, reset link, and call `bnx2x_link_set`.

Register dumps compute lengths from `bnx2x_dump.h`, write a `dump_header`, disable parity attentions, iterate idle/regular/windowed/paged register tables, then clear and re-enable parity. Preset dump operations use `ethtool_dump.flag` as a preset index.

NVRAM reads/writes serialize through a hardware NVRAM lock, request MCP NVM software arbitration, enable access bits, issue command registers with FIRST/LAST page flags, poll for DONE, and release access. Writes across 4 KiB page boundaries release the lock briefly so MFW can make progress. Module EEPROM operations use PHY I2C reads under the PHY lock and split A0/A2 SFP address spaces.

Self-test first runs online NVRAM CRC checks, then, if the device is up and offline tests are requested on non-MF PFs, unloads/reloads the NIC in diagnostic mode, runs register/memory/internal loopback tests, optionally runs external loopback, restores the normal load, then runs interrupt and link tests. Loopback sends a crafted packet through the first queue and validates TX completion, RX completion, length, and payload.

## State and Persistence Behavior
The file reads and mutates many fields in `struct bnx2x`: link parameters, advertised modes, flow-control requests, `wol`, `msg_enable`, `dump_preset_idx`, NVRAM flash size, coalescing ticks, ring sizes, EEE mode, RSS configuration, queue counts, stats blocks, and PTP clock state. It also changes persistent hardware/firmware state through NVRAM writes, PHY firmware-upgrade magic commands, LED control, link reset/init, RSS reconfiguration, interrupt mode changes, and NIC unload/load cycles.

## Dependencies and Integration Points
Depends on Linux ethtool, netdevice, PCI power-management state, CRC32, DMA mapping, SKB allocation, PHY/module EEPROM helpers, `bnx2x.h`, `bnx2x_cmn.h`, `bnx2x_dump.h`, `bnx2x_init.h`, firmware/shared-memory macros, register access, link management, queue state ramrods, RSS helpers, statistics events, and PTP APIs. Main-driver probe calls `bnx2x_set_ethtool_ops`; other driver files call exported `bnx2x_nvram_read` for firmware/NVM consumers.

## Risks
NVRAM access is high risk because lock ordering must protect PFs on the same port and MFW arbitration, while endian behavior is intentionally historical: reads convert to big-endian byte streams but writeback preserves old tool expectations. Link setting paths have many board, media, multi-phy, and multi-function restrictions; missing a validation branch can advertise or force unsupported modes. Register dump tables can produce false parity/GRC noise if parity is not disabled and restored correctly. Self-tests unload/reload the NIC and manipulate queues, DMA mappings, PHY locks, and loopback state, so failures can leave link or queue state disrupted if cleanup changes regress. RSS and channel setters reject VF/SRIOV cases and unsupported hash parameters; changing queue counts requires interrupt-mode teardown/rebuild.

## Test Signals
Useful coverage includes `ethtool -i`, `-k/-S/-g/-G/-c/-C/-a/-A`, `ethtool -d`, preset dump ioctls, WOL get/set, speed/autoneg/port switching on supported boards, SFP module info/eeprom reads, EEPROM read/write with alignment and one-byte writes, EEE get/set, offline and online self-tests, external loopback where cabled, VF ethtool behavior, RSS hash field changes, indirection table round-trips, channel count changes with and without VFs enabled, PTP timestamp info, and suspend/down-state NVM access rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bnx2x/bnx2x_ethtool.c -->
