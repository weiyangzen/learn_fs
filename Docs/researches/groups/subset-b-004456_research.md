# subset-b-004456 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/i40e/i40e_dcb.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/i40e/i40e_dcb.c

## Purpose

`i40e_dcb.c` implements the core Data Center Bridging path for the Intel i40e driver. It translates LLDP/DCBX MIB data into `struct i40e_dcbx_config`, serializes local DCB configuration back into IEEE LLDP TLVs, initializes DCB state from firmware/NVM, and directly programs receive-side DCB/PFC packet-buffer registers used by software-controlled DCB.

## Important APIs, Types, And Functions

- `i40e_get_dcbx_status()` reads `I40E_PRTDCB_GENS` and extracts firmware DCBX engine status.
- `i40e_lldp_to_dcb_config()` walks an LLDPDU after the Ethernet header, dispatching organization TLVs to IEEE or CEE parsers until END TLV or `I40E_LLDPDU_SIZE`.
- IEEE parsers (`i40e_parse_ieee_etscfg_tlv()`, `i40e_parse_ieee_etsrec_tlv()`, `i40e_parse_ieee_pfccfg_tlv()`, `i40e_parse_ieee_app_tlv()`) populate ETS, PFC, and application priority tables.
- CEE parsers (`i40e_parse_cee_pgcfg_tlv()`, `i40e_parse_cee_pfccfg_tlv()`, `i40e_parse_cee_app_tlv()`) convert CEE feature TLVs into the same internal DCB config representation.
- `i40e_aq_get_dcb_config()`, `i40e_get_dcb_config()`, and `i40e_init_dcb()` are the firmware-facing retrieval and initialization entry points.
- `i40e_set_dcb_config()` and `i40e_dcb_config_to_lldp()` serialize local config into IEEE TLVs and submit it through `i40e_aq_set_lldp_mib()`.
- Hardware programming helpers configure Rx FIFO arbitration, command monitor thresholds, PFC registers, TC count, Rx ETS bandwidth, UP-to-TC mapping, packet-buffer sizing, and packet-buffer watermarks.
- `_i40e_read_lldp_cfg()` and `i40e_read_lldp_cfg()` read LLDP configuration variables from structured or flat NVM layouts.

## Control Flow

Initialization starts in `i40e_init_dcb()`: it checks DCB capability, reads LLDP admin status from persistent FW LLDP NVM data or older LLDP config storage, rejects disabled LLDP, reads current DCBX status, fetches DCB config when status is done or in progress, and optionally enables MIB-change events. `i40e_get_dcb_config()` chooses IEEE-only behavior for older XL710 firmware, a legacy CEE v1 response for XL710 4.33, or the newer CEE response otherwise; CEE `ENOENT` falls back to IEEE LLDP MIB retrieval. Remote MIB absence is explicitly non-fatal.

LLDP parsing is streaming and TLV-driven. Organization TLVs are identified by OUI: IEEE 802.1Qaz TLVs are parsed by subtype, while CEE TLVs parse up to `I40E_CEE_MAX_FEAT_TYPE` nested feature TLVs. Serialization runs the inverse path: `i40e_dcb_config_to_lldp()` iterates a fixed TLV id sequence for ETS config, ETS recommendation, PFC config, and app priority, appending only TLVs with non-zero length.

Software DCB register programming is split into small helpers. The packet-buffer path first computes target sizes and watermarks in `i40e_dcb_hw_calculate_pool_sizes()`, then `i40e_dcb_hw_rx_pb_config()` programs decreasing watermarks before pool-size changes and increasing watermarks after pool-size changes to preserve hardware ordering requirements.

## State And Persistence

Primary persistent driver state is `hw->local_dcbx_config`, `hw->desired_dcbx_config`, `hw->remote_dcbx_config`, and `hw->dcbx_status`. Persistent LLDP admin status is read from NVM or firmware settings; local DCB updates are persisted into firmware LLDP MIB through admin queue calls, not into local files. Hardware state is written directly through `rd32()`/`wr32()` to port DCB, packet-buffer, and PFC registers.

## Dependencies And Integration Points

The file depends on `i40e_adminq.h`, `i40e_alloc.h`, `i40e_dcb.h`, `i40e_prototype.h`, LLDP/DCBX constants from `i40e_type.h`, and Linux bitfield helpers. It integrates with firmware admin queue calls such as `i40e_aq_get_lldp_mib()`, `i40e_aq_set_lldp_mib()`, `i40e_aq_get_cee_dcb_config()`, `i40e_aq_cfg_lldp_mib_change_event()`, NVM access helpers, and low-level register access macros.

## Risks

- TLV parsing trusts the firmware-provided LLDPDU buffer shape within the global `I40E_LLDPDU_SIZE`; malformed lengths can truncate parsing but there is limited per-sub-TLV validation.
- `i40e_dcb_config_to_lldp()` assumes the caller provided a zeroed buffer; an app TLV with zero apps leaves length zero and relies on prior buffer contents being harmless.
- `i40e_dcb_hw_rx_up2tc_config()` ORs new mapping bits into the existing register value without clearing all UP-to-TC fields first, so callers must ensure old values are not significant or hardware reset state is known.
- Packet-buffer sizing logs but does not fill `pb_cfg` when shared pool size is negative, leaving correctness dependent on callers avoiding invalid configurations.
- DCB behavior is firmware-version specific, so regression risk is high around XL710 4.33 and older firmware branches.

## Test Signals

Useful tests include synthetic IEEE and CEE LLDPDU parser fixtures, round-trip serialization checks for ETS/PFC/app TLVs, firmware-mocked `ENOENT` fallback tests, DCB init tests for enabled/disabled LLDP admin status, register programming tests that verify mask/field writes, and hardware or emulator tests for PFC and packet-buffer programming under 1/2/4-port and low/high TC counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/i40e/i40e_dcb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/i40e/i40e_dcb.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/i40e/i40e_dcb.h

## Purpose

`i40e_dcb.h` defines the DCB/LLDP/DCBX constants, packed wire-format TLV structures, packet-buffer calculation types, and public DCB function prototypes shared by the i40e DCB implementation and driver integration code.

## Important APIs, Types, And Functions

- DCBX status constants describe firmware states: not started, in progress, done, multiple peers, and disabled.
- TLV constants define LLDP type/length bit positions, IEEE 802.1Qaz OUIs/subtypes, CEE OUIs/subtypes, and fixed IEEE TLV lengths.
- Packed wire structs include `struct i40e_lldp_org_tlv`, `struct i40e_cee_tlv_hdr`, `struct i40e_cee_ctrl_tlv`, `struct i40e_cee_feat_tlv`, and `struct i40e_cee_app_prio`.
- `struct i40e_rx_pb_config` represents calculated shared and per-TC packet-buffer sizes, high/low watermarks, and thresholds.
- `enum i40e_dcb_arbiter_mode` models strict priority versus round-robin arbitration.
- Delay and conversion macros model bit-time to byte/KB conversions used for PFC headroom sizing.
- Public prototypes expose firmware DCB retrieval, LLDP serialization/parsing, DCB initialization, FW LLDP status query, and hardware DCB register programming.

## Control Flow

This header has no runtime control flow, but it defines the contract used by `i40e_dcb.c`: parser code relies on packed TLV layouts and bit masks, while register programming relies on delay constants and packet-buffer formulas. Public prototypes separate software DCB hardware programming from firmware LLDP/DCBX MIB management.

## State And Persistence

The header defines state shapes rather than owning state. `i40e_rx_pb_config` is transient calculation state used before writing packet-buffer registers. Packed TLV structs map persistent firmware/network LLDP data. Persistent behavior is implemented by the C file through NVM and admin queue access.

## Dependencies And Integration Points

The header includes `i40e_type.h` for hardware and DCB base definitions. It is consumed by `i40e_dcb.c`, DCB netlink code, and broader i40e driver paths that initialize or apply DCB configuration.

## Risks

- Packed structs must match LLDP/CEE wire layout exactly; changing field order or packing would break parser correctness.
- Bit-time constants are tuned for specific link assumptions, with comments noting missing delays for other speeds; packet-buffer calculations can be conservative or wrong if hardware/link assumptions change.
- Fixed TLV lengths and max application counts require parser and serializer updates if firmware supports broader DCBX data.

## Test Signals

Compile-time coverage should catch missing prototypes and type changes. Runtime coverage comes from `i40e_dcb.c` parser/serializer and packet-buffer tests. Static assertions around packed sizes and field offsets would be valuable if the codebase accepts them.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/i40e/i40e_dcb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/i40e/i40e_dcb_nl.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/i40e/i40e_dcb_nl.c

## Purpose

`i40e_dcb_nl.c` implements the kernel DCBNL interface for i40e when `CONFIG_I40E_DCB` is enabled. It exposes IEEE and CEE DCB operations to user space, mirrors firmware-negotiated app TLVs into the DCB app table, and routes host-managed DCB changes through `i40e_hw_dcb_config()`.

## Important APIs, Types, And Functions

- IEEE getters/setters: `i40e_dcbnl_ieee_getets()`, `i40e_dcbnl_ieee_getpfc()`, `i40e_dcbnl_ieee_setets()`, `i40e_dcbnl_ieee_setpfc()`, `i40e_dcbnl_ieee_setapp()`, and `i40e_dcbnl_ieee_delapp()`.
- CEE operations cover state, PG Tx mappings and bandwidth, PFC per-priority settings, capabilities, TC count queries, PFC state, and app lookup.
- `i40e_dcbnl_cee_set_all()` commits staged CEE config from `pf->tmp_cfg`.
- `i40e_dcbnl_setdcbx()` switches host DCBX mode between IEEE and CEE while rejecting firmware-managed and mixed modes.
- `dcbnl_ops` binds the file’s functions into `struct dcbnl_rtnl_ops`.
- `i40e_dcbnl_set_all()` pushes negotiated firmware DCB apps into the netdevice app table and sends `dcbnl_ieee_notify()`.
- `i40e_dcbnl_flush_apps()` removes stale app entries from all VSIs when the DCB configuration changes.
- `i40e_dcbnl_setup()` installs `dev->dcbnl_ops` and seeds initial app TLVs.

## Control Flow

User-space DCBNL calls enter through `dcbnl_ops`. Most write paths first check whether the PF supports the requested DCBX version and whether firmware LLDP management owns DCBX; firmware-managed modes reject host writes. IEEE setters copy `hw.local_dcbx_config` into `pf->tmp_cfg`, modify the requested ETS/PFC/app fields, and call `i40e_hw_dcb_config()`. CEE setters generally stage fields in `pf->tmp_cfg`, with `setall` performing the commit.

Firmware-negotiated DCB updates call `i40e_dcbnl_set_all()` to add app entries only when DCB is enabled, host DCB is not active, MFP restrictions allow it, and the app’s traffic class is enabled on the VSI. App flush compares old and new configs and deletes removed entries from every netdev-backed VSI.

## State And Persistence

State is held in `pf->dcbx_cap`, PF flags such as `I40E_FLAG_DCB_ENA`, `pf->hw.local_dcbx_config`, `pf->hw.desired_dcbx_config`, and `pf->tmp_cfg`. Netdevice DCB app state is maintained through `dcb_ieee_setapp()` and `dcb_ieee_delapp()`. Changes become hardware/firmware state only after `i40e_hw_dcb_config()` succeeds.

## Dependencies And Integration Points

The file depends on `<net/dcbnl.h>`, `i40e.h`, the i40e PF/VSI/netdev mapping helpers, DCB core helpers, `i40e_hw_dcb_config()`, and firmware/driver flags for DCB capability and MFP state. It is compiled out unless `CONFIG_I40E_DCB` is enabled.

## Risks

- Write paths return generic `-EINVAL` or DCBNL status errors, so callers can lose detailed firmware failure context except for logged AQ status.
- `pf->tmp_cfg` is shared staging state; concurrent DCBNL operations rely on higher-level DCBNL/RTNL serialization.
- `i40e_dcbnl_ieee_delapp()` intentionally keeps one firmware-required app, which can surprise user space that expects complete deletion.
- CEE Rx bandwidth and PG setters are no-ops because hardware does not support them, but the interface still exposes callbacks.
- MFP/iSCSI filtering means app propagation differs by PF role.

## Test Signals

Exercise `dcbtool`/`lldptool` or DCBNL netlink tests for IEEE and CEE modes, host versus firmware-managed rejection, app add/delete/flush behavior, MFP non-iSCSI suppression, and failure paths from `i40e_hw_dcb_config()`. Trace or assert emitted DCBNL notifications after firmware-negotiated app updates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/i40e/i40e_dcb_nl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/i40e/i40e_ddp.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/i40e/i40e_ddp.c

## Purpose

`i40e_ddp.c` implements Dynamic Device Personalization profile load and rollback through the ethtool flash callback. It validates DDP package structure, checks compatibility with already loaded profiles, writes or rolls back profile data in firmware, updates firmware profile tracking info, and keeps an in-memory rollback stack.

## Important APIs, Types, And Functions

- `struct i40e_ddp_profile_list` mirrors firmware’s loaded-profile list response.
- `struct i40e_ddp_old_profile_list` stores previously loaded profile buffers on `pf->ddp_old_prof` for rollback.
- `i40e_ddp_profiles_eq()` compares track id, version, and name.
- `i40e_ddp_does_profile_exist()` and `i40e_ddp_does_profile_overlap()` query firmware and enforce duplicate/overlap rules.
- `i40e_add_pinfo()` and `i40e_del_pinfo()` write profile info sections with add/remove track-id operations.
- `i40e_ddp_is_pkg_hdr_valid()` performs package header version, size, segment count, alignment, and bounds checks.
- `i40e_ddp_load()` performs the core add/remove flow.
- `i40e_ddp_restore()` rolls back one stored profile entry.
- `i40e_ddp_flash()` is the public ethtool flash entry point.

## Control Flow

`i40e_ddp_flash()` only accepts region `100` and only permits operations on physical function 0. A normal flash request builds a firmware path under `intel/i40e/ddp/`, calls `request_firmware()`, and loads the profile via `i40e_ddp_load(..., true)`. On success it allocates a rollback entry and copies the firmware image into `pf->ddp_old_prof`. A request whose data string is `"-"` invokes `i40e_ddp_restore()` to roll back the first stored profile.

`i40e_ddp_load()` validates the package, finds metadata and i40e profile segments, builds a profile identity, checks existence and overlap, writes or rolls back profile data using `i40e_write_profile()` or `i40e_rollback_profile()`, then updates firmware’s profile list using `i40e_add_pinfo()` or `i40e_del_pinfo()`.

## State And Persistence

Firmware stores the active DDP profile and loaded profile metadata. Driver rollback state is volatile memory in `pf->ddp_old_prof`; it is lost on driver unload/reset and can consume memory proportional to successfully loaded profile sizes. Firmware files are loaded from the kernel firmware search path, not from repository state.

## Dependencies And Integration Points

The file depends on `<linux/firmware.h>`, ethtool flash plumbing, i40e package/segment definitions, admin queue helpers `i40e_aq_get_ddp_list()` and `i40e_aq_write_ddp()`, and profile write/rollback helpers from the i40e common code.

## Risks

- Rollback is best effort: if allocation for rollback storage fails, the new profile remains loaded but cannot be restored through this in-memory stack.
- Package validation is structural but not cryptographic; trust ultimately rests on firmware acceptance and admin-controlled firmware file paths.
- Profile overlap semantics depend on track-id group encoding; wrong track-id interpretation can reject valid combinations or accept conflicting packages.
- Only PF0 can operate, so multi-function systems need clear operator handling.
- The rollback list removes one entry per restore; behavior is stack/list-order sensitive.

## Test Signals

Test invalid region, non-PF0 rejection, missing firmware file, malformed package headers, missing metadata/profile segments, duplicate profile detection, overlap detection, unsupported-device `-ENODEV` mapping to `-EPERM`, successful add plus rollback, and rollback allocation failure logging.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/i40e/i40e_ddp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/i40e/i40e_debug.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/i40e/i40e_debug.h

## Purpose

`i40e_debug.h` defines debug mask bits and lightweight logging macros for i40e hardware-level diagnostics. It centralizes category bits used by `hw->debug_mask` and maps hardware debug output to Linux device logging.

## Important APIs, Types, And Functions

- `enum i40e_debug_mask` defines categories such as init, release, link, PHY, HMC, NVM, LAN, flow, DCB, diagnostics, Flow Director, package, iWARP, AdminQ message/descriptor/buffer/command, user bits, and all bits.
- `i40e_hw_to_dev()` is declared as the bridge from `struct i40e_hw` to `struct device`.
- `hw_dbg()` and `hw_warn()` wrap `dev_dbg()` and `dev_warn()`.
- `i40e_debug()` conditionally emits `dev_info()` when the requested mask intersects `h->debug_mask`.

## Control Flow

There is no standalone control flow. Runtime gating occurs in the `i40e_debug()` macro: it tests the mask against a hardware structure’s `debug_mask` and emits only when enabled.

## State And Persistence

Debug state is the `debug_mask` field in `struct i40e_hw`; this header does not persist it. Messages are emitted to the kernel logging infrastructure.

## Dependencies And Integration Points

The header depends on `<linux/dev_printk.h>` and a driver-provided `i40e_hw_to_dev()`. It is used by diagnostics and DCB code for category-specific logging.

## Risks

- The `i40e_debug()` macro references `hw` inside `i40e_hw_to_dev(hw)` while its formal hardware argument is named `h`; this relies on call-site scope containing a `hw` variable and is fragile.
- Debug masks are broad bitfields, so accidental use of overlapping values would alter logging categories.
- `dev_info()` can be noisy for high-frequency paths if masks are enabled.

## Test Signals

Build coverage should catch macro call sites lacking a `hw` variable. Runtime smoke tests can toggle `debug_mask` and confirm category-gated output for DCB and diagnostic failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/i40e/i40e_debug.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/i40e/i40e_debugfs.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/i40e/i40e_debugfs.c

## Purpose

`i40e_debugfs.c` provides the i40e debugfs interface when `CONFIG_DEBUG_FS` is enabled. It creates per-PF debugfs files that accept textual commands for dumping internal state, manipulating test switch objects, reading/writing registers, sending AdminQ commands, controlling LLDP, reading NVM, and invoking selected netdev operations.

## Important APIs, Types, And Functions

- `i40e_dbg_init()` and `i40e_dbg_exit()` create/remove the driver root debugfs directory.
- `i40e_dbg_pf_init()` and `i40e_dbg_pf_exit()` create/remove per-PF `command` and `netdev_ops` files.
- `i40e_dbg_command_write()` is the main command parser.
- `i40e_dbg_netdev_ops_write()` parses debug-triggered `change_mtu`, `set_rx_mode`, and `napi` commands.
- Dump helpers include `i40e_dbg_dump_vsi_seid()`, `i40e_dbg_dump_aq_desc()`, `i40e_dbg_dump_desc()`, `i40e_dbg_dump_veb_seid()`, `i40e_dbg_dump_vf()`, and stats dump helpers.
- `enum ring_type` selects Rx, Tx, or XDP descriptor rings for descriptor dumps.

## Control Flow

Driver init creates the debugfs root, each PF creates a directory named by `pci_name()`, and two write-only style files are installed with mode `0600`. Write handlers reject partial writes, copy a single user command, trim a newline, and dispatch by prefix.

The `command` parser supports state dump commands (`dump switch`, `dump vsi`, `dump veb`, `dump vf`, `dump desc`, `dump port`, `dump reset stats`, `dump debug fwdata`), topology/test changes (`add/del vsi`, `add/del relay`, `add/del pvid`), resets (`pfr`, `corer`, `globr`), register `read`/`write`, stats clearing, raw direct and indirect AdminQ command submission, Flow Director count dump, LLDP start/stop/MIB/event operations, and NVM reads. The `netdev_ops` parser calls selected netdev operations after VSI lookup and RTNL acquisition where needed.

## State And Persistence

The file owns global `i40e_dbg_root` and per-PF `pf->i40e_dbg_pf` dentries. Most commands inspect or mutate live PF/VSI/VEB/VF/hardware state only. Persistent or semi-persistent effects can occur through NVM reads, LLDP firmware start/stop, control-packet filters, DCBX capability changes, AdminQ commands, register writes, resets, and topology changes. Output goes to kernel logs via `dev_info()` and hex dumps rather than read buffers.

## Dependencies And Integration Points

The file depends on debugfs, filesystem write callbacks, bridge definitions, i40e core PF/VSI/VEB/VF helpers, SR-IOV support, AdminQ helpers, LLDP AQ commands, NVM resource locking, XDP ring state, and netdev operations. It is compiled only under `CONFIG_DEBUG_FS`.

## Risks

- The command interface is powerful: raw register writes, raw AdminQ commands, resets, LLDP control, and topology changes can disrupt a live system.
- Prefix parsing with `strncmp()` and fixed offsets is brittle; malformed spacing can hit unexpected branches or produce confusing errors.
- Many dumps walk live driver structures; some use RCU or ring copies, but broader PF/VSI state can still race with teardown or reset.
- `i40e_dbg_dump_desc()` checks `vsi->tx_rings` even for Rx/XDP descriptor dumps, so allocation assumptions are coupled.
- Debug output can be very large, especially descriptor rings, NVM dumps, and firmware debug data.
- The interface is mode `0600`, but any privileged writer can bypass normal validation by using raw AQ/register commands.

## Test Signals

Manual debugfs smoke tests should cover each command family, invalid argument handling, descriptor dumps for Rx/Tx/XDP, no-VF and invalid-VF paths, LLDP start/stop/get/event flows, register bounds checks, NVM read lock/unlock behavior, reset command scheduling, and netdev op RTNL contention. Kernel log volume should be monitored during large dumps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/i40e/i40e_debugfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/i40e/i40e_devids.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/i40e/i40e_devids.h

## Purpose

`i40e_devids.h` defines PCI device IDs recognized by the i40e driver for XL710, X710, XXV710, X722, QEMU, N3000, backplane, QSFP, SFP, SFP28, and Base-T variants.

## Important APIs, Types, And Functions

- Device ID macros include `I40E_DEV_ID_SFP_XL710`, `I40E_DEV_ID_QEMU`, `I40E_DEV_ID_QSFP_*`, `I40E_DEV_ID_10G_BASE_T*`, `I40E_DEV_ID_25G_*`, and X722 variants.
- `I40E_IS_X710TL_DEVICE(d)` groups 1G/5G/10G Base-T backplane controller IDs for X710-TL handling.

## Control Flow

The header has no runtime control flow. Other driver tables and conditional paths include it to match PCI IDs and classify device variants.

## State And Persistence

No state is owned. These constants influence probe-time device matching and feature/device-family branching elsewhere in the driver.

## Dependencies And Integration Points

It is a standalone header consumed by PCI ID tables and hardware-variant logic in the i40e driver.

## Risks

- Missing or wrong IDs prevent devices from binding or can route them through incorrect variant handling.
- The grouping macro must stay aligned with hardware errata and feature differences for X710-TL devices.

## Test Signals

Probe tests on each supported PCI ID, static review against Intel device ID lists, and build checks for PCI ID table references are the main signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/i40e/i40e_devids.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/i40e/i40e_devlink.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/i40e/i40e_devlink.c

## Purpose

`i40e_devlink.c` integrates i40e PFs with Linux devlink. It allocates the PF inside a devlink private area, exposes firmware/device version information, registers a runtime `max_mac_per_vf` parameter, and creates a physical devlink port for each PF.

## Important APIs, Types, And Functions

- `i40e_max_mac_per_vf_get()` and `i40e_max_mac_per_vf_set()` implement the generic devlink `MAX_MAC_PER_VF` runtime parameter.
- Version helpers format DSN, management firmware version/build, API version, NVM version, EETRACK, CIVD, and PBA data.
- `i40e_devlink_info_get()` populates devlink info request fields.
- `i40e_alloc_pf()` and `i40e_free_pf()` allocate/free `struct i40e_pf` via devlink private storage.
- `i40e_devlink_register()` and `i40e_devlink_unregister()` register/unregister parameters and the devlink instance.
- `i40e_devlink_create_port()` and `i40e_devlink_destroy_port()` manage `pf->devlink_port`.

## Control Flow

Probe-time allocation calls `devlink_alloc()` with i40e ops and returns `devlink_priv()`. Registration first registers devlink params, logs errors, then registers devlink. Info requests call formatting helpers in sequence and short-circuit on devlink put errors. Port creation builds physical port attrs using `hw.pf_id` and a switch id derived from PCI DSN, then registers the port with the PF id as index. Teardown unregisters port, devlink, params, and finally frees devlink memory.

## State And Persistence

Runtime devlink state includes the devlink instance, registered parameter state, `pf->max_mac_per_vf`, and `pf->devlink_port`. The `max_mac_per_vf` parameter is runtime-only here and cannot be changed while SR-IOV VFs are allocated. Version information is read from hardware/adminq state and device identifiers.

## Dependencies And Integration Points

The file depends on `<net/devlink.h>`, PCI DSN helpers, unaligned big-endian formatting helpers, i40e PF hardware state, version formatting helpers declared elsewhere, and devlink core registration APIs.

## Risks

- `i40e_devlink_register()` logs parameter registration failure but still registers devlink, so parameter availability can differ from devlink availability.
- `max_mac_per_vf` changes are blocked only when `num_alloc_vfs > 0`; callers must ensure SR-IOV lifecycle serialization.
- Empty PBA strings are skipped, which is intentional but means board id can be absent.
- Switch id uses PCI DSN; hardware without a meaningful DSN may produce less useful devlink topology identity.

## Test Signals

Use `devlink dev info` to verify serial and version fields, `devlink dev param show/set` for `max_mac_per_vf`, tests that setting the parameter fails with SR-IOV enabled, and probe/remove tests validating devlink and port registration cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/i40e/i40e_devlink.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/i40e/i40e_devlink.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/i40e/i40e_devlink.h

## Purpose

`i40e_devlink.h` declares the i40e devlink lifecycle interface used by probe, remove, and PF setup code.

## Important APIs, Types, And Functions

- Forward declaration: `struct i40e_pf`.
- `i40e_alloc_pf()` allocates a devlink instance and PF private data.
- `i40e_free_pf()` frees PF/devlink storage.
- `i40e_devlink_register()` and `i40e_devlink_unregister()` manage devlink registration.
- `i40e_devlink_create_port()` and `i40e_devlink_destroy_port()` manage the PF devlink port.

## Control Flow

The header defines ordering expectations rather than implementing them: allocate PF, initialize hardware/PF fields, register devlink, create the port, then destroy/unregister/free on teardown.

## State And Persistence

No state is owned by the header. It exposes functions that manage devlink-backed PF memory and runtime devlink objects.

## Dependencies And Integration Points

The header includes `<linux/device.h>` for allocation context and is paired with `i40e_devlink.c`. Probe/remove code includes it to avoid direct devlink implementation coupling.

## Risks

- Call-order mistakes can leak devlink resources or unregister ports after parent devlink teardown.
- Because `struct i40e_pf` is opaque here, callers must use the implementation contract rather than stack allocation.

## Test Signals

Build coverage catches prototype drift. Probe/remove and fault-injection tests around each lifecycle step are the main runtime signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/i40e/i40e_devlink.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/i40e/i40e_diag.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/i40e/i40e_diag.c

## Purpose

`i40e_diag.c` implements low-level hardware diagnostics for selected registers and EEPROM/NVM validity. It is used by driver self-test paths to detect register access failures and invalid EEPROM checksum state.

## Important APIs, Types, And Functions

- `i40e_diag_reg_pattern_test()` writes a fixed pattern set through a mask, verifies reads, restores the original register value, and verifies restore.
- `i40e_reg_list[]` lists register offsets, writable/testable masks, element counts, and strides.
- `i40e_diag_reg_test()` iterates the register list and adapts element counts for dynamically allocated queues and MSI-X vectors.
- `i40e_diag_eeprom_test()` reads the NVM control word and validates checksum when the valid bit is set.

## Control Flow

Register testing loops over `i40e_reg_list[]` until the sentinel offset `0`. For queue/vector-backed registers, element counts are replaced with hardware capability values. Each selected register address is tested by writing `0x5A5A5A5A`, `0xA5A5A5A5`, zero, and all ones masked by the register’s safe mask, then restoring the original value. The first failure stops the scan and returns `-EIO`.

EEPROM testing reads `I40E_SR_NVM_CONTROL_WORD`; if the valid bit matches the expected control-word bit, it calls `i40e_validate_nvm_checksum()`, otherwise it returns `-EIO`.

## State And Persistence

The register test temporarily mutates hardware registers and attempts to restore their original values. EEPROM test reads NVM state and checksum but does not write persistent state. Diagnostic failures are logged through `i40e_debug()` when the diagnostic debug mask is enabled.

## Dependencies And Integration Points

The file depends on `i40e_diag.h`, `i40e_prototype.h`, register macros, hardware capability fields, `rd32()`/`wr32()`, NVM helpers, and debug logging. It is typically reached from ethtool self-test or internal diagnostic paths.

## Risks

- Register pattern tests are intrusive and should run only when hardware state can tolerate temporary writes.
- Masks must remain accurate; testing reserved or side-effect bits can destabilize hardware.
- Dynamic element calculation uses `num_msix_vectors - 1`, so zero is guarded but off-by-one behavior should match hardware vector layout.
- A failed restore leaves hardware in an unexpected state and reports `-EIO`.

## Test Signals

Run ethtool offline diagnostics on supported hardware, inject mocked `rd32()` mismatches for failure paths, verify masks against hardware documentation, and test EEPROM invalid control word and checksum failure cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/i40e/i40e_diag.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/i40e/i40e_diag.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/i40e/i40e_diag.h

## Purpose

`i40e_diag.h` declares diagnostic loopback modes, register-test metadata, the exported register list, and public diagnostic test entry points for the i40e driver.

## Important APIs, Types, And Functions

- `enum i40e_lb_mode` maps no loopback and PHY/MAC local/remote loopback modes to AdminQ loopback constants.
- `struct i40e_diag_reg_test_info` describes a base register, safe test mask, element count, and stride.
- `extern const struct i40e_diag_reg_test_info i40e_reg_list[]` exports the diagnostic register list.
- `i40e_diag_reg_test()` and `i40e_diag_eeprom_test()` are the public diagnostic test functions.

## Control Flow

No control flow is implemented in the header. It defines the metadata contract consumed by `i40e_diag.c` and any diagnostic callers.

## State And Persistence

The header owns no state. It describes diagnostic inputs and exposes tests that read/write hardware or NVM state in the implementation.

## Dependencies And Integration Points

It includes `<linux/types.h>` and `i40e_adminq_cmd.h` for fixed-width types and AdminQ loopback constants. It forward-declares `struct i40e_hw` to avoid pulling in the full hardware definition.

## Risks

- Loopback enum values must remain aligned with AdminQ definitions.
- The register test info structure is tightly coupled to hardware register stride and mask semantics.

## Test Signals

Build coverage catches enum/prototype drift. Runtime coverage comes from diagnostics invoking `i40e_diag_reg_test()` and `i40e_diag_eeprom_test()` on real or mocked hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/i40e/i40e_diag.h -->
