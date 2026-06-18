# subset-b-004495 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ixgbe/ixgbe_e610.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ixgbe/ixgbe_e610.c

## Purpose

`ixgbe_e610.c` adds E610-specific hardware support to the ixgbe driver. It is the firmware-mediated control layer for Intel E610 adapters, centered on the Admin Command Interface (ACI), and binds E610 implementations into the common ixgbe MAC, PHY, and EEPROM operation tables. The file covers command transport over PF HICR/HIDA/HIBA registers, firmware event retrieval, common-resource arbitration, device/function capability discovery, link/media and flow-control setup, EEPROM/NVM/flash-bank access, reset behavior, PBA string reads, and `libie_fwlog` integration.

This file is not packet data-path code. Its callers are mostly probe/open/reset/link/ethtool paths and generic ixgbe operation callbacks. The data it persists lives in `struct ixgbe_hw` substructures such as `hw->aci`, `hw->dev_caps`, `hw->func_caps`, `hw->link`, `hw->phy`, `hw->fc`, `hw->eeprom`, `hw->flash`, and `hw->fwlog`.

## Important APIs, types, and functions

- ACI transport: `ixgbe_aci_send_cmd()`, `ixgbe_aci_send_cmd_execute()`, `ixgbe_fill_dflt_direct_cmd_desc()`, `ixgbe_should_retry_aci_send_cmd_execute()`.
- ACI events: `ixgbe_aci_check_event_pending()` reads `GL_FWSTS`; `ixgbe_aci_get_event()` issues `ixgbe_aci_opc_get_fw_event`.
- Resource arbitration: `ixgbe_acquire_res()`, `ixgbe_release_res()`, with private helpers for request/release ACI opcodes.
- Capability discovery: `ixgbe_aci_list_caps()`, `ixgbe_discover_dev_caps()`, `ixgbe_discover_func_caps()`, `ixgbe_get_caps()`, plus parse helpers for common, device, and function capability records.
- Link/PHY: `ixgbe_aci_get_phy_caps()`, `ixgbe_copy_phy_caps_to_cfg()`, `ixgbe_aci_set_phy_cfg()`, `ixgbe_aci_get_link_info()`, `ixgbe_update_link_info()`, `ixgbe_get_link_status()`, `ixgbe_get_media_type_e610()`, `ixgbe_setup_phy_link_e610()`, `ixgbe_check_link_e610()`, `ixgbe_identify_phy_e610()`, `ixgbe_identify_module_e610()`, `ixgbe_set_phy_power_e610()`, `ixgbe_enter_lplu_e610()`.
- Flow control: `ixgbe_cfg_phy_fc()`, `ixgbe_setup_fc_e610()`, `ixgbe_fc_autoneg_e610()`.
- NVM and flash: `ixgbe_init_eeprom_params_e610()`, `ixgbe_acquire_nvm()`, `ixgbe_release_nvm()`, `ixgbe_aci_read_nvm()`, `ixgbe_aci_update_nvm()`, `ixgbe_aci_erase_nvm()`, `ixgbe_nvm_write_activate()`, `ixgbe_nvm_validate_checksum()`, `ixgbe_read_flat_nvm()`, `ixgbe_read_ee_aci_e610()`, `ixgbe_read_ee_aci_buffer_e610()`, `ixgbe_get_flash_data()`, inactive version readers, and package/component update helpers.
- Reset and binding: `ixgbe_reset_hw_e610()`, `ixgbe_fwlog_init()`, `ixgbe_fwlog_deinit()`, `mac_ops_e610`, `phy_ops_e610`, `eeprom_ops_e610`, and exported `ixgbe_e610_info`.

The file depends on `libie_aq_desc` and related `libie` ACI constants, E610-specific structures and macros from `ixgbe_type.h`, generic ixgbe helpers from common/X540/X550 code, Linux locking/allocation/polling primitives, and register access macros `IXGBE_READ_REG()`/`IXGBE_WRITE_REG()`.

## Control flow

ACI command flow starts with a descriptor initialized by `ixgbe_fill_dflt_direct_cmd_desc()`. `ixgbe_aci_send_cmd()` optionally snapshots retryable descriptors and buffers, serializes access with `hw->aci.lock`, and calls `ixgbe_aci_send_cmd_execute()`. The execute helper validates the HICR command mechanism, encodes optional indirect buffers into HIBA registers, writes the descriptor dwords to HIDA, sets `PF_HICR.C`, polls for synchronous and asynchronous completion bits, reads the response descriptor back, checks opcode and firmware return value, copies response buffer dwords out, and updates `hw->aci.last_status`. A small opcode allowlist is retried on firmware `EBUSY` because link-state transitions can make the CSR path temporarily busy.

Firmware event flow uses `GL_FWSTS` pending bits keyed by PF function. `ixgbe_aci_get_event()` holds the same ACI mutex, checks the pending bit, sends the event command, treats an unchanged event opcode as no event, copies the response descriptor into the caller's `ixgbe_aci_event`, records message length, and optionally reports whether more events remain.

Capability flow sends `list_dev_caps` and `list_func_caps` into a 4 KiB buffer. Parse helpers walk `libie_aqc_list_caps_elem` records, filling common resources such as valid functions, SR-IOV, VMDq, DCB, RSS table size, RX/TX queue ranges, MSI-X vectors, pending NVM update flags, NVM management, MTU, reset restrictions, and external topology image metadata. Device-specific parsing records function count, exposed VFs, host VSIs, and flow-director filters. Function parsing records allocated VF ranges and guaranteed VSI count.

Link flow is firmware owned. `ixgbe_aci_get_link_info()` sends `get_link_status`, updates old/current link caches, speed, PHY type bitmaps, media status, FEC, topology conflict, pacing, LSE enablement, and negotiated flow-control mode. `ixgbe_get_link_status()` refreshes only when `hw->link.get_link_info` is set. `ixgbe_check_link_e610()` forces a fresh query, optionally polls for link up, then translates ACI link-speed codes into ixgbe link-speed flags. `ixgbe_get_media_type_e610()` updates link info, optionally queries PHY caps when media is present but link is down, picks the highest PHY type bit, and maps it to copper, fiber, direct attach, AUI, backplane, or unknown.

PHY setup reads supported topology/media capabilities, reads active config to preserve unrelated firmware-owned fields, intersects requested advertised speeds with supported PHY type bitmaps, then writes a new PHY configuration only when it changes. Flow control similarly reads active PHY config, copies capabilities to set-config format, adjusts pause bits for the requested mode, and writes back with auto-link-update when required.

NVM/flash flow uses firmware common-resource ownership unless the device is in blank NVM programming mode. Shadow RAM and flat NVM reads are chunked to 4 KiB ACI transfers and, for Shadow RAM, constrained to the configured EEPROM size. `ixgbe_get_flash_data()` reads SR size, detects blank mode, discovers flash size by bisection over readable offsets, determines active/inactive NVM/OROM/netlist banks from the SR control word and pointer/size words, then populates active NVM, OROM, and netlist version structures. Inactive version APIs reuse the same bank offset calculation for pending update reporting.

Reset flow stops the adapter, clears pending TX, initializes PHY ops, takes the SW/FW semaphore, writes `IXGBE_CTRL_RST`, polls for reset completion, optionally repeats for double-reset recovery, sets RX packet buffer size, refreshes the permanent MAC address, resets RAR count to 128, initializes receive addresses, and refreshes LAN ID.

## State and persistence behavior

`hw->aci.last_status` persists the last firmware Admin Queue return code and is used to distinguish transport errors from firmware statuses. `hw->aci.lock` is the serialization boundary for CSR-based ACI access.

Capability discovery populates `hw->dev_caps` and `hw->func_caps`; link operations mutate `hw->link.link_info`, `hw->link.link_info_old`, `hw->link.get_link_info`, and `hw->fc.current_mode`; PHY operations mutate `hw->phy.type`, `hw->phy.media_type`, supported and advertised speed masks, EEE masks, SFP type, PHY ID, and `curr_user_phy_cfg`; EEPROM/flash operations populate `hw->eeprom.word_size`, `hw->flash.sr_words`, `blank_nvm_mode`, `flash_size`, active bank offsets/sizes, and version structs.

NVM writes and activation commands affect persistent device flash through firmware. The code uses ACI ownership commands to avoid concurrent flash access by other agents, except when blank NVM mode leaves the flash lock unset. PHY configuration and low-power-link-up are persistent firmware/device state until changed again or reset by platform policy.

## Dependencies and integration points

The exported operation table `ixgbe_e610_info` is the primary integration point for probe-time device selection. It reuses many X540/X550/generic helpers while overriding E610-specific firmware-mediated behavior. `ixgbe_ethtool.c` calls E610 APIs for port-ID LED, pause behavior, firmware version refresh, and link settings through operation callbacks. `libie_fwlog` receives ACI commands via `__fwlog_send_cmd()`. NVM update tooling and ethtool EEPROM paths depend on the read/update/activate helpers. Link event setup flows through `ixgbe_configure_lse()` and `ixgbe_aci_get_event()`.

Register-level dependencies include PF HICR/HIDA/HIBA command registers, `GL_FWSTS`, NVM/flash registers such as `GLNVM_GENS` and `IXGBE_GLNVM_FLA`, link/topology ACI opcodes, and normal ixgbe MAC registers for reset/RX disable.

## Risks and edge cases

- In `ixgbe_aci_send_cmd()`, the retry buffer allocation copies only the first byte into `buf_cpy` before later restoring `buf_size` bytes from it. If this is not intentional or corrected elsewhere, retrying an indirect command can restore uninitialized memory into the caller's buffer.
- `ixgbe_discover_dev_caps()` and `ixgbe_discover_func_caps()` return `0` even when `ixgbe_aci_list_caps()` fails. That masks firmware discovery errors and can leave zeroed capability structures looking valid.
- ACI command execution has very long poll timeouts and holds command serialization across the whole register transaction; hung firmware can stall control-plane callers.
- Firmware opcode mismatch is ignored only for event retrieval. Any undocumented firmware response variation can become `-EIO`.
- Link/media detection collapses multiple PHY type bits to unknown, and down-link media detection picks the highest set PHY type bit. That is conservative but can misrepresent multi-mode modules.
- NVM read helpers explicitly allow partial buffer updates on failure. Callers must respect the returned length and error.
- Flash bank offset `0` is treated as invalid, so a valid bank at zero would be indistinguishable from error unless the platform layout guarantees nonzero module pointers.
- Reset uses only ten 1 usec polls for the reset bit after writing `IXGBE_CTRL_RST`; devices that need longer before self-clear will report failure.
- Many operations rely on correct endian conversions for flash metadata. Missing conversions in new paths would corrupt version parsing or offsets.

## Test signals

Useful validation signals include successful probe with `ixgbe_e610_info`, firmware version population, `ixgbe_get_caps()` showing nonzero queue/MSI-X/RSS capabilities, `ethtool` link settings matching advertised PHY speeds, link status events arriving via ACI, pause mode changes surviving reinit, EEPROM reads and checksum validation succeeding, `ixgbe_refresh_fw_version()` reporting active flash versions, inactive NVM/OROM/netlist version reads during a pending update, and fwlog debugfs initialization for E610 only. Negative tests should cover ACI busy retry, invalid indirect-buffer combinations, blank NVM mode, NVM lock contention, no-media SFP/module identification, and fallback RX disable when the firmware RXEN command fails.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ixgbe/ixgbe_e610.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ixgbe/ixgbe_e610.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ixgbe/ixgbe_e610.h

## Purpose

`ixgbe_e610.h` is the public internal header for E610-specific ixgbe support. It exposes the E610 Admin Command Interface, capability discovery, link/PHY/flow-control management, NVM/flash access, reset, and firmware log hooks implemented in `ixgbe_e610.c` to the rest of the ixgbe driver. It includes `ixgbe_type.h`, so its declarations are built around `struct ixgbe_hw`, ACI descriptors, E610 link/PHY/NVM data structures, and ixgbe enums.

## Important APIs and exported contract

The header exports ACI transport functions (`ixgbe_aci_send_cmd()`, event pending/get helpers, and descriptor initialization), resource ownership helpers (`ixgbe_acquire_res()`, `ixgbe_release_res()`), capability enumeration (`ixgbe_aci_list_caps()`, device/function discovery, `ixgbe_get_caps()`), link and PHY APIs (`ixgbe_aci_disable_rxen()`, PHY caps/config, restart autoneg, update/get link status, event masks, LED identification, media type, setup/check link, link capabilities, PHY flow control, RX disable, PHY ops init/identify/module/setup/power/LPLU), NVM and flash APIs (EEPROM params, netlist node lookup, NVM ownership, read/update/erase/activate/checksum, inactive image version reads, Shadow RAM reads, flat NVM reads, E610 EEPROM reads/checksum, reset, flash metadata discovery, PLDM-like package/component-table commands), and firmware logging (`ixgbe_fwlog_init()`, `ixgbe_fwlog_deinit()`).

The declarations intentionally mirror ixgbe operation-table slots and ethtool-facing helpers. For example, `ixgbe_check_link_e610()` and `ixgbe_get_link_capabilities_e610()` can be used through `hw->mac.ops`; `ixgbe_read_ee_aci_e610()` and `ixgbe_validate_eeprom_checksum_e610()` can be used through `hw->eeprom.ops`; `ixgbe_aci_set_port_id_led()` is used by the E610 ethtool physical-ID path.

## Control flow represented by the header

The header describes a layered control-plane contract. Generic ixgbe code can send raw ACI commands, then build higher-level discovery, link, PHY, and NVM flows on top of that transport. Link callers can either perform direct ACI status queries or call MAC/PHY operation callbacks that eventually land in the same E610 functions. NVM callers are expected to acquire ownership, perform bounded read/write/erase/update operations, then release ownership unless they use helper APIs that do this internally.

The grouping of prototypes also indicates initialization order: ACI command support must exist first; firmware version/capability discovery and flash data are probe/start dependencies; PHY/link setup depends on parsed PHY capabilities; EEPROM operations depend on initialized EEPROM params; fwlog initialization depends on adapter/debugfs state and E610 MAC type.

## State and persistence behavior

The header itself has no storage and no inline logic, but its API grants access to persistent hardware and driver state. Functions declared here can mutate firmware/device settings (PHY config, link restart, event masks, LEDs, RX enable state, NVM contents, NVM activation, EMPR), cached driver state (`hw->link`, `hw->phy`, `hw->fc`, `hw->flash`, `hw->eeprom`, capabilities), and debug/logging state (`hw->fwlog`). Several calls have persistent side effects outside driver memory, especially NVM update, erase, write-activate, package data, component table, and low-power PHY configuration operations.

## Dependencies and integration points

This header is consumed by E610 implementation users such as ethtool support, common ixgbe initialization, and any NVM update or fwlog paths that need E610 control. It depends on the type universe in `ixgbe_type.h`: `struct libie_aq_desc`, `struct ixgbe_aci_event`, ACI command data structures, `enum libie_aq_res_id`, `enum libie_aq_res_access_type`, `enum ixgbe_aci_opc`, link speed/media/flow-control enums, and flash version structures.

Because this is a private driver header rather than a UAPI header, source compatibility is controlled inside the ixgbe driver. Changes here require matching updates to `ixgbe_e610.c` and all callers using operation table assignments or direct E610 helpers.

## Risks and maintenance notes

- The header exposes many low-level NVM write/erase/update primitives. Callers must follow ownership, chunking, last-command, and activation rules from the implementation; the prototypes alone do not enforce those sequencing constraints.
- Several functions accept raw buffers and lengths. Mis-sized buffers can result in firmware errors or partial reads, so call sites need careful size validation.
- Link/PHY helpers mix cached state updates with hardware/firmware commands. Callers should not assume they are read-only unless the implementation guarantees it.
- Header drift is a risk: adding an implementation in `ixgbe_e610.c` without declaring it here limits reuse, while changing a prototype breaks operation-table users and ethtool integration.
- E610-specific behavior is partly presented through generic ixgbe names and partly through explicit `_e610` names. Maintainers need to verify that generic callers do not use these on non-E610 hardware unless guarded by MAC type or operation-table dispatch.

## Test signals

Build coverage is the main direct test signal for this header: all prototypes should match implementation definitions and callers without sparse/compiler warnings. Runtime signals come through users of the declared APIs: successful E610 probe/start, ethtool operations that call E610 helpers, EEPROM/NVM reads, link setup, LED identification, and fwlog initialization. API-level negative tests should compile with `W=1`/sparse-style checking for pointer type mismatches, missing declarations, and endian-annotated structure misuse.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ixgbe/ixgbe_e610.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ixgbe/ixgbe_ethtool.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ixgbe/ixgbe_ethtool.c

## Purpose

`ixgbe_ethtool.c` implements the ixgbe driver's `struct ethtool_ops` surface. It translates userspace ethtool requests into ixgbe state reads, register dumps, EEPROM access, ring resizing, statistics, diagnostics, Wake-on-LAN, LED identification, interrupt moderation, Flow Director rules, RSS configuration, timestamp capability reporting, channel counts, module EEPROM reads, EEE control, and private flags. It also defines an E610-specific ethtool ops table that mostly reuses the generic implementation but swaps in E610 behavior for pause configuration, WoL handling, and physical-ID LED control.

## Important APIs, types, and functions

The file defines `struct ixgbe_stats` plus static stat string tables for global, queue, packet-buffer, private-flag, and diagnostic-test stringsets. It exposes one non-static helper, `ixgbe_refresh_fw_version()`, and the public binder `ixgbe_set_ethtool_ops()`.

Major ethtool operations include:

- Link settings: `ixgbe_get_link_ksettings()`, `ixgbe_set_link_ksettings()`, and helpers for 10G backplane/copper advertising.
- Pause: `ixgbe_get_pause_stats()`, `ixgbe_get_pauseparam()`, `ixgbe_set_pauseparam()`, `ixgbe_set_pauseparam_e610()`, and the common finalizer.
- Register/EEPROM/driver info: `ixgbe_get_regs_len()`, `ixgbe_get_regs()`, `ixgbe_get_eeprom_len()`, `ixgbe_get_eeprom()`, `ixgbe_set_eeprom()`, `ixgbe_get_drvinfo()`.
- Ring and stats: `ixgbe_get_ringparam()`, `ixgbe_set_ringparam()`, `ixgbe_get_sset_count()`, `ixgbe_get_ethtool_stats()`, `ixgbe_get_strings()`.
- Diagnostics: `ixgbe_diag_test()` and helpers for link, register, EEPROM, interrupt, descriptor-ring, and loopback tests.
- WoL and LEDs: `ixgbe_get_wol()`, `ixgbe_set_wol()`, `ixgbe_set_wol_acpi()`, `ixgbe_set_wol_e610()`, `ixgbe_set_phys_id()`, `ixgbe_set_phys_id_e610()`.
- Coalescing/RSC: `ixgbe_get_coalesce()`, `ixgbe_set_coalesce()`, `ixgbe_update_rsc()`.
- Flow Director/RSS: FDIR get/add/delete/update helpers, `ixgbe_get_rxnfc()`, `ixgbe_set_rxnfc()`, `ixgbe_get_rxfh_fields()`, `ixgbe_set_rxfh_fields()`, `ixgbe_get_rxfh()`, `ixgbe_set_rxfh()`, key/indirection size helpers.
- Time stamping and channels: `ixgbe_get_ts_info()`, `ixgbe_max_channels()`, `ixgbe_get_channels()`, `ixgbe_set_channels()`.
- Module and EEE: `ixgbe_get_module_info()`, `ixgbe_get_module_eeprom()`, `ixgbe_get_eee_fw()`, `ixgbe_get_eee()`, `ixgbe_set_eee()`.
- Private flags: `ixgbe_get_priv_flags()`, `ixgbe_set_priv_flags()`.

## Control flow

`ixgbe_set_ethtool_ops()` selects `ixgbe_ethtool_ops_e610` when `adapter->hw.mac.type == ixgbe_mac_e610`, otherwise the generic `ixgbe_ethtool_ops`. Both tables wire most ethtool operations to the same functions; E610 uses `ixgbe_set_wol_e610()`, `ixgbe_set_pauseparam_e610()`, and `ixgbe_set_phys_id_e610()`.

Link-setting reads ask `hw->mac.ops.get_link_capabilities()` for supported speed/autoneg data, populate ethtool link modes based on media/PHY/SFP type and `hw->phy.autoneg_advertised`, report pause advertising from `hw->fc.requested_mode`, and report current speed from `adapter->link_speed` only when carrier is up. Link-setting writes validate the requested advertising mask, restrict forced modes, serialize against SFP initialization with `__IXGBE_IN_SFP_INIT`, set `hw->mac.autotry_restart`, and call `hw->mac.ops.setup_link()`, rolling back to the old advertised mask on failure.

Pause writes build a temporary copy of `hw->fc`, validate hardware/DCB/autoneg constraints, map rx/tx booleans to ixgbe flow-control modes, then call `ixgbe_set_pauseparam_finalize()`, which replaces `hw->fc` and resets/reinitializes the adapter only if anything changed. The E610 variant refuses to disable pause autoneg and requires autoneg-capable flow control.

Ring resizing clamps and aligns requested descriptor counts. If the device is down, it only updates ring counts. If running, it marks `__IXGBE_RESETTING`, allocates temporary ring structures, takes the adapter down, allocates new TX/XDP/RX resources before freeing old ones, copies successful temp rings into the adapter, brings the adapter back up, and clears the reset bit. This ordering preserves the old resources if allocation fails before replacement.

Statistics flow calls `ixgbe_update_stats()`, fetches netdev stats, copies global adapter/netdev stats by offset and size, then appends per-TX and per-RX queue packet/byte counters using `u64_stats_fetch_begin/retry`, followed by packet-buffer pause counters.

Diagnostics split online and offline modes. Offline tests reject active VFs, close or reset the interface, run link/register/EEPROM/interrupt/MAC-loopback tests with resets between them, skip loopback under SR-IOV or VMDq, then restore interface state. Online tests only run link and mark offline-only tests as passed. Register tests use hardware-specific test tables and restore register values after pattern/set checks.

FDIR rule insertion validates perfect-filter support, maps ring cookies to absolute queues or VF pools, enforces the hardware rule index range, converts ethtool flow specs to ATR flow types, builds a mask, enforces the driver's single-mask-per-port limitation, computes the perfect hash, writes the hardware filter, and stores a sorted software rule node under `fdir_perfect_lock`. Deletion removes the hardware filter and software node through the same list updater.

RSS configuration validates hash field combinations, updates UDP RSS flags and MRQC/PFVFMRQC bits when needed, warns that UDP RSS can reorder fragments, validates redirection table queue indices, then stores RETA and RSS key. Channel changes update FDIR/RSS/FCoE ring-feature limits and call `ixgbe_setup_tc()`.

Module EEPROM reads use PHY I2C callbacks, reject firmware-controlled PHYs (`ixgbe_phy_fw`), and avoid concurrent SFP initialization. EEE reads for firmware PHYs use `ixgbe_fw_phy_activity()` to derive link-partner advertised EEE and cached PHY EEE masks for local supported/advertised modes; writes only toggle full EEE enablement and reject unsupported fine-grained changes.

## State and persistence behavior

The file reads and mutates persistent adapter state: `adapter->msg_enable`, `adapter->wol`, `hw->wol_enabled`, `hw->fc`, `hw->phy.autoneg_advertised`, ring descriptor counts, RSS key/indirection table, RSS UDP flags, FDIR software filter list/count/mask, coalescing settings, RSC enable flag, channel feature limits, EEE flags and advertised speeds, private `flags2`, and test state bits.

Hardware persistent or semi-persistent side effects include EEPROM writes/checksum updates, WoL register programming and PCI wake enablement, link autoneg restarts, adapter resets, interrupt moderation register writes, MRQC/PFVFMRQC RSS field updates, FDIR hardware filter programming/erasure, LED identification state, and E610 ACI LED control. Many changes trigger `ixgbe_reinit_locked()`, `ixgbe_reset()`, or full queue scheme reallocation, so ethtool requests can disrupt traffic.

## Dependencies and integration points

The file integrates Linux ethtool core with ixgbe core state, PCI, netdevice features, PTP clock indexing, module EEPROM standards, Flow Director ATR helpers, RSS storage helpers, DCB/FCoE ring-feature limits, and E610 helpers from `ixgbe_e610.h`. It relies on `ixgbe_main.c` and `ixgbe_lib.c` for reset/open/close, queue allocation, interrupt schemes, TX/RX resource setup, TC setup, stats update, and feature flags. FCoE statistics and channel limits are compiled under `IXGBE_FCOE`.

## Risks and edge cases

- Ettool operations can reset or stop/start the device, so locking and state-bit discipline are important. Ring resize, link setup, diagnostics, EEE toggles, coalesce/RSC changes, and private flag changes all have traffic-impacting paths.
- `ixgbe_set_eeprom()` assumes `hw->eeprom.ops.write_buffer` and `update_checksum` exist. E610's EEPROM ops table in `ixgbe_e610.c` declares reads/checksum/init/PBA but not write/update callbacks, so set-eeprom support must be reviewed for E610 or other read-only operation tables.
- Register diagnostics write many hardware registers and should remain offline-only. Incorrect test tables can disturb live hardware state.
- The FDIR implementation supports only one input mask per port. Users adding incompatible rules receive `-EINVAL`; rule replacement also erases old filters if bucket hashes differ.
- UDP RSS enablement can reorder fragments, and the code only warns once at setting time.
- Module EEPROM paths return `-ENXIO` for firmware PHYs, so E610 module information may be unavailable through the legacy I2C ethtool path.
- `ixgbe_get_regs()` has a fixed register dump length and many MAC-type conditionals. Adding E610-only registers without updating length/layout could confuse diagnostics.
- `ixgbe_fdir_filter_list` traversal uses safe hlist iteration, but correctness depends on holding `fdir_perfect_lock` for mutations.

## Test signals

High-value tests include `ethtool -i`, `-k`, `-S`, `-g/-G`, `-c/-C`, `-l/-L`, `-x/-X`, `-n/-N`, `--show-eee/--set-eee`, module EEPROM reads on supported SFP PHYs, and `ethtool -t` online/offline diagnostics. E610-specific signals are `ethtool --identify` using ACI LED control, pause autoneg refusal when disabled, E610 WoL ACPI paths for unicast/multicast/broadcast, and firmware version refresh through `ixgbe_refresh_fw_version()`. Regression tests should verify ring-resize failure preserves old resources, FDIR single-mask enforcement, RSS invalid field rejection, SR-IOV channel limits, active-VF offline diagnostic rejection, and no crashes when module I2C operations are unavailable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ixgbe/ixgbe_ethtool.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ixgbe/ixgbe_fcoe.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ixgbe/ixgbe_fcoe.c

## Purpose

`ixgbe_fcoe.c` implements Fibre Channel over Ethernet offload support for ixgbe when `CONFIG_FCOE` enables the driver's FCoE integration. It covers Direct Data Placement (DDP) context setup/completion, FCoE sequence offload for transmit, FCoE/FIP hardware filter and queue programming, allocation/freeing of per-CPU DDP DMA pools, enable/disable transitions exposed through netdevice FCoE operations, WWN construction, HBA information reporting, and FCoE traffic-class lookup.

The file is a bridge between the Linux libfc/libfcoe stack and ixgbe hardware offloads. Its most sensitive responsibilities are DMA lifetime management for SCSI scatterlists and programming hardware DDP/filter contexts by XID.

## Important APIs, types, and functions

- DDP context lifecycle: `ixgbe_fcoe_clear_ddp()`, `ixgbe_fcoe_ddp_setup()`, `ixgbe_fcoe_ddp_get()`, `ixgbe_fcoe_ddp_target()`, `ixgbe_fcoe_ddp_put()`.
- Receive DDP completion: `ixgbe_fcoe_ddp()` examines FC status bits in RX descriptors, updates DDP lengths/errors, unmaps SG lists on FCP response, and decides whether the skb should continue to the upper layer.
- Transmit offload: `ixgbe_fso()` builds FCoE context descriptors for CRC/EOF/SOF and FCoE LSO.
- Resource management: `ixgbe_fcoe_dma_pool_alloc()`, `ixgbe_fcoe_dma_pool_free()`, `ixgbe_setup_fcoe_ddp_resources()`, `ixgbe_free_fcoe_ddp_resources()`.
- Hardware configuration: `ixgbe_configure_fcoe()` programs FCoE/FIP EtherType filters, FCoE redirection table entries, and receive control bits.
- Netdevice FCoE ops: `ixgbe_fcoe_enable()`, `ixgbe_fcoe_disable()`, `ixgbe_fcoe_get_wwn()`, `ixgbe_fcoe_get_hbainfo()`, and `ixgbe_fcoe_get_tc()`.

The code uses `struct ixgbe_fcoe`, `struct ixgbe_fcoe_ddp`, and `struct ixgbe_fcoe_ddp_pool` from `ixgbe_fcoe.h`; SCSI scatterlists; FC/FCoE headers from kernel SCSI/Fibre Channel headers; per-CPU DMA pools; ixgbe ring and descriptor structures; and numerous FCoE registers/macros from `ixgbe_type.h`.

## Control flow

DDP setup starts through `ixgbe_fcoe_ddp_get()` for initiator mode or `ixgbe_fcoe_ddp_target()` for target mode. Both call `ixgbe_fcoe_ddp_setup()`. Setup validates netdev and scatterlist, rejects out-of-range XIDs, refuses setup while the adapter is down or resetting, rejects an already active context, clears the DDP slot, picks the current CPU's DMA pool, maps the SCSI SG list for device writes, allocates a DMA pool buffer for the user descriptor list, and converts the SG DMA ranges into hardware buffer base entries. Hardware constraints require all buffers except the first to be aligned to the FCoE buffer size and all non-last buffers to end on a full buffer boundary. If the final segment exactly fills a buffer, an extra shared workaround buffer is appended so hardware sees a non-full last size.

Once the descriptor list is ready, setup builds `FCBUFF`, `FCDMARW`, and `FCFLTRW` values. Target mode sets `WRCONTX` and enables last-sequence indication in `FCRXCTRL` once. X550 uses direct per-XID DDP/filter context registers and does not take the FCoE spinlock; older hardware uses indirect context registers protected by `fcoe->lock`. Success returns `1`; failures unwind by freeing the DDP pool allocation, clearing the DDP slot, unmapping the SG list, dropping the CPU reference, and returning `0` for no DDP.

DDP put validates netdev/XID and active context, captures the DDP byte count, invalidates hardware DDP/filter context only when `ddp->err` is set, waits briefly if the context remains valid, unmaps the SG list if still present, frees the DMA pool descriptor list, clears the DDP slot, and returns the DDPed length. This is the `ndo_fcoe_ddp_done` release path expected from libfc/FCP.

Receive DDP completion in `ixgbe_fcoe_ddp()` sets skb checksum state from FC CRC status, locates the FC frame header with optional VLAN adjustment, derives XID from OX_ID or RX_ID depending on exchange context, validates the DDP slot, rejects FC EOF/CRC errors, and switches on descriptor FCSTAT. A DDP status records byte count and returns `0` so the skb is bypassed for data already placed by hardware. FCPRSP unmaps the SG list, stores error state, clears SG ownership, and falls through to the NODDP handling, which passes a nonzero DDP length up. Target-mode last data frames are linearized and given an FCoE EOF trailer so the upper layer can process completion semantics.

Transmit offload in `ixgbe_fso()` validates GSO type, resets skb network/transport headers to FCoE/FC, maps SOF and EOF values to advanced context descriptor flags, enables relative-offset increment when FC header F_CTL requests it, adjusts header length and byte counts for FCoE LSO, marks TX flags for FCoE and CRC context, and emits an ixgbe TX context descriptor.

`ixgbe_configure_fcoe()` always enables the FCoE EtherType filter when FCoE CRC offload is exposed, because CRC/DDP classification depends on it. If full FCoE is enabled, it programs the FCoE redirection table from `RING_F_FCOE`, enables FCRECTL, installs a FIP filter and sends FIP to the first FCoE queue, and configures FCoE RX control for CRC byte order and version.

Enable/disable flow is exposed through netdev FCoE operations. Enable increments the FCoE refcount, validates capability and disabled state, warns that PF FCoE conflicts with legacy VFs, stops the interface if running, allocates per-CPU DDP tracking, sets the enabled flag and `netdev->fcoe_mtu`, notifies feature changes, rebuilds the interrupt/queue scheme, and reopens if needed. Disable decrements the refcount and only proceeds when it reaches zero, stops the interface, frees DDP tracking, clears enabled state and MTU flag, notifies features, rebuilds queue/interrupt layout, and reopens if needed.

## State and persistence behavior

DDP state is per adapter in `adapter->fcoe.ddp[xid]`. Each active entry stores DDP length, error flag, DMA pool pointer, user descriptor list virtual/DMA address, SG list pointer, and SG count. Per-CPU DDP pools store allocation-failure counters `noddp` and `noddp_ext_buff`, which are later aggregated into hardware stats by the main ixgbe stats path. The shared extra DDP buffer is allocated and DMA-mapped at adapter open/resource setup time and freed during FCoE resource teardown.

Adapter-level feature state is held in `IXGBE_FLAG_FCOE_CAPABLE`, `IXGBE_FLAG_FCOE_ENABLED`, `adapter->fcoe.refcnt`, `adapter->fcoe.mode`, `adapter->fcoe.up`, ring-feature limits/offsets, and `netdev->fcoe_mtu`. Hardware state persists in FCoE filter tables, redirection tables, DDP contexts, and FCRXCTRL bits until reset/reconfiguration.

## Dependencies and integration points

The file integrates with `ixgbe_main.c` via netdevice ops (`ndo_fcoe_ddp_setup`, `ndo_fcoe_ddp_target`, `ndo_fcoe_ddp_done`, `ndo_fcoe_enable`, `ndo_fcoe_disable`, `ndo_fcoe_get_wwn`, `ndo_fcoe_get_hbainfo`), RX cleanup (`ixgbe_fcoe_ddp()`), TX offload (`ixgbe_fso()`), open/close resource setup/teardown, stats aggregation, and hardware configure paths. `ixgbe_lib.c` contributes FCoE queue allocation and ring-feature mapping. DCB code controls the user priority/traffic class for FCoE. SR-IOV paths adjust MTU and queue/pool behavior when FCoE is enabled. Linux libfc/libfcoe calls the netdevice FCoE hooks and consumes WWN/HBA metadata.

## Risks and edge cases

- `ixgbe_fcoe_enable()` increments `fcoe->refcnt` before capability/enabled-state validation and ignores the return from `ixgbe_fcoe_ddp_enable()`. Failed enable attempts can leave refcount skew, and DDP allocation failure may not stop feature enablement.
- `ixgbe_fcoe_disable()` returns `-EINVAL` when the decremented refcount is not zero; callers must avoid unbalanced enable/disable sequences.
- DDP setup uses `get_cpu()` and has several error labels that call `put_cpu()`. The success path drops the CPU reference before register programming; failure path coverage must remain exact when editing.
- DMA mapping and pool allocation errors must unwind in the right order. Leaking an SG mapping or descriptor-list DMA pool entry would corrupt later I/O.
- Hardware alignment constraints cause many valid SG layouts to fall back to no DDP. This is expected but should be reflected in `noddp` counters.
- X550 and pre-X550 context programming use different register models and locking. Any new MAC type must choose the correct path.
- Receive path calls `skb_linearize()` for target last-sequence frames but does not check its return before `skb_put()`.
- Enable/disable stops and reopens the interface and rebuilds queues, so it is disruptive and must coordinate with SR-IOV, DCB, and netdev feature changes.
- HBA model reporting defaults non-82599/non-X550 devices to "Intel X540"; newer supported FCoE-capable MACs would need explicit model handling.

## Test signals

Runtime signals include successful `ndo_fcoe_enable`/`disable`, `netdev->fcoe_mtu` toggling, FCoE/FIP filters programmed during open, FCoE queues assigned in ring features, libfc DDP setup returning `1` for aligned SG layouts and `0` for unsupported layouts, DDP byte counts appearing on completion, SG unmap on FCPRSP/done, `fcoe_noddp` counters increasing on fallback, FSO context descriptors emitted for `SKB_GSO_FCOE`, and valid WWNN/WWPN generation from SAN MAC and prefixes. Negative testing should cover out-of-range XIDs, adapter down/resetting, missing DDP pool, DMA map failure, exact-full final buffer workaround, target-mode last-sequence completion, SR-IOV warning path, and unbalanced enable/disable reference counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ixgbe/ixgbe_fcoe.c -->
