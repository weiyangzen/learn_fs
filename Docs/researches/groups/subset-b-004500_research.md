# subset-b-004500 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ixgbe/ixgbe_type.h -->
# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ixgbe/ixgbe_type.h

## Purpose
`ixgbe_type.h` is the central hardware contract for the Intel ixgbe driver. It defines supported PCI device IDs, register offsets, register bitfields, descriptor formats, link/PHY/media enums, flow-control constants, mailbox and host-interface structures, and the main `struct ixgbe_hw` object that all MAC-, PHY-, EEPROM-, mailbox-, and link-specific implementations operate on. It also includes the E610-specific type header so newer firmware-admin and flash state can be embedded into the same shared `ixgbe_hw` model.

## Important APIs, Types, and Functions
- Device identity constants cover 82598, 82599, X540, X550, X550EM, E610, and VF device IDs used by PCI probe tables.
- Register macros cover global control/status, NVM/flash, interrupts, flow control, Rx/Tx queues, RSS, Flow Director, virtualization, wake-on-LAN, statistics, MACsec/FCoE, and sideband/IOSF/KR PHY access.
- `IXGBE_MVALS_INIT`, `enum ixgbe_mvals`, `IXGBE_BY_MAC`, and per-generation register aliases abstract register/value differences across 8259x, X540, X550, X550EM, and related variants.
- Descriptor contracts include `union ixgbe_adv_tx_desc`, `union ixgbe_adv_rx_desc`, `struct ixgbe_adv_tx_context_desc`, and the many `IXGBE_ADVTXD_*`/Rx status masks used by fast-path Tx/Rx code.
- Link and media contracts include `ixgbe_link_speed`, `ixgbe_physical_layer`, `enum ixgbe_media_type`, `enum ixgbe_fc_mode`, `enum ixgbe_sfp_type`, and `enum ixgbe_phy_type`.
- Flow Director support is represented by register masks, `enum ixgbe_fdir_pballoc_type`, `enum ixgbe_atr_flow_type`, `union ixgbe_atr_input`, and `union ixgbe_atr_hash_dword`.
- Host-interface and firmware command payloads include `struct ixgbe_hic_hdr`, `struct ixgbe_hic_hdr2_req/rsp`, firmware driver-info structures, shadow RAM commands, and PHY-token/activity command payloads.
- Operation tables are declared as `struct ixgbe_mac_operations`, `struct ixgbe_eeprom_operations`, `struct ixgbe_phy_operations`, `struct ixgbe_link_operations`, and `struct ixgbe_mbx_info`.
- Runtime state is organized by `struct ixgbe_addr_filter_info`, `struct ixgbe_bus_info`, `struct ixgbe_fc_info`, `struct ixgbe_hw_stats`, `struct ixgbe_eeprom_info`, `struct ixgbe_mac_info`, `struct ixgbe_phy_info`, `struct ixgbe_link_info`, `struct ixgbe_hw`, and `struct ixgbe_info`.
- Late-file KRM, sideband IOSF, and management interface macros support X550/X552 internal PHY/link programming paths.

## Control Flow
This header has no executable control flow, but it shapes nearly every ixgbe control path. Probe code chooses an `ixgbe_info` table for the PCI ID, copies its operation tables into `struct ixgbe_hw`, and then generic and generation-specific files call through those function pointers. Register macros are used directly by common code and generation files to configure reset, queues, interrupts, filters, link, EEPROM, virtualization, and statistics.

The control model is table-driven: `struct ixgbe_info` identifies the MAC type and supplies invariant setup plus pointers to MAC, EEPROM, PHY, mailbox, and link operations. Runtime code then invokes `hw->mac.ops.*`, `hw->eeprom.ops.*`, `hw->phy.ops.*`, and `hw->link.ops.*` instead of switching on every generation at each call site. Register aliases and `hw->mvals` let one operation implementation select the right register/value layout for the active MAC family.

Fast-path control is also defined here through descriptor layouts and queue register macros. Tx/Rx ring code programs descriptor base/length/head/tail registers, consumes the advanced Rx status/error fields, and emits advanced Tx data/context descriptors using the masks declared in this file.

## State and Persistence Behavior
Most definitions are compile-time constants, but the structures declared here define driver runtime state. `struct ixgbe_hw` stores MMIO base, device IDs, revision, MAC/PHY/EEPROM/link/bus/mailbox state, feature booleans, firmware/API versions, E610 ACI and flash state, device/function capabilities, and firmware logging state. `struct ixgbe_mac_info` caches permanent/SAN addresses, multicast table shadow, RAR/VLAN/filter sizes, queue limits, original link settings, thermal data, and reset flags. `struct ixgbe_phy_info` caches PHY identity, SFP type, advertised speeds, EEE settings, semaphore masks, current user PHY config, and E610 PHY type bitmaps. `struct ixgbe_fc_info` stores requested/current flow-control mode and watermarks.

Persistent hardware state is not stored by the header itself, but many macros address persistent NVM/flash/shadow RAM locations. EEPROM and flash operations in implementation files use these offsets and checksum constants to read and write nonvolatile configuration. Statistics structures hold runtime counters collected from hardware registers and are rebuilt or refreshed by driver code.

## Dependencies and Integration Points
The header depends on Linux kernel network and type APIs (`linux/types.h`, `linux/mdio.h`, `linux/netdevice.h`) and Intel shared firmware logging (`linux/net/intel/libie/fwlog.h`). It includes `ixgbe_type_e610.h`, bringing in libie AdminQ descriptors and E610-specific flash/admin command structures. It is included by virtually all ixgbe implementation files: common MAC logic, X540/X550/E610 generation files, PHY code, mailbox/SR-IOV, ethtool, PTP, devlink, sysfs, main probe/remove, and DCB code.

Integration with hardware is direct: macros encode MMIO addresses and bit masks, while function pointer tables define the internal ABI between common driver flows and generation-specific implementations. Integration with Linux networking occurs through `struct net_device` parameters in multicast update callbacks, MDIO state in `struct ixgbe_phy_info`, mailbox state for SR-IOV VFs, and firmware/devlink/PTP state embedded for newer E610 support.

## Risks and Edge Cases
- Register definitions are shared by many call sites; a wrong offset, mask, shift, or generation-specific `mvals` entry can break unrelated paths such as reset, EEPROM, I2C, interrupt moderation, or Rx/Tx queue setup.
- Several macros compute addresses from queue, VF, traffic-class, or register indices. Callers must enforce hardware bounds before indexing to avoid programming the wrong register window.
- `struct ixgbe_hw` is the central ABI across the driver. Adding fields or operation callbacks requires all generation operation tables to remain initialized consistently.
- Endianness-sensitive descriptor and firmware structures use `__le16`, `__le32`, `__le64`, and big-endian network fields. Fast-path and firmware code must convert at boundaries.
- E610 support is mixed into the legacy ixgbe type system through included E610 structs and new enum values. Paths that assume only legacy MACs must explicitly handle or reject `ixgbe_mac_e610`.
- Some constants represent persistent NVM layout and checksums; accidental reuse for runtime-only data can corrupt device configuration.
- Flow Director, RSS, SR-IOV, DCB, and PTP features share queue and filter resources, so register/table size constants must match hardware capabilities selected by `get_invariants`.

## Test Signals
- Full driver builds should cover every MAC family and catch missing operation-table fields or incompatible struct changes.
- Probe tests should validate PCI IDs map to the expected `ixgbe_info`, MAC type, `mvals`, queue limits, RAR/VFTA/MTA sizes, and operation tables.
- Hardware or emulated register tests should exercise reset, EEPROM, I2C, interrupt, queue, RSS, VLAN, Flow Director, SR-IOV mailbox, PTP, WoL, and statistics register paths.
- Static analysis should focus on index-derived register macros, descriptor bitfield use, endian conversions, and array bounds for queues, traffic classes, VFs, MTA/VFTA/VLVF, and Flow Director tables.
- Regression tests should include E610 and non-E610 builds because this header now bridges legacy ixgbe and libie/ACI-backed E610 state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ixgbe/ixgbe_type.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ixgbe/ixgbe_type_e610.h -->
# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ixgbe/ixgbe_type_e610.h

## Purpose
`ixgbe_type_e610.h` defines the E610-specific firmware Admin Command Interface, link/PHY command payloads, NVM/flash layout constants, capability structures, link status cache structures, and flash-bank metadata used by the ixgbe E610 implementation. It supplements the legacy ixgbe type system with libie AdminQ descriptors and E610 firmware-managed hardware contracts.

## Important APIs, Types, and Functions
- Shadow RAM and flash constants define NVM control word, PBA block, EETRACK, software checksum, PFA pointer, active-bank pointers and sizes, CSS header fields, authentication header length, and shadow RAM sizing.
- Netlist and Option ROM constants define topology TLV offsets, netlist ID block fields, CIV signature, OROM version masks, and active/inactive bank metadata.
- Firmware/global register macros include `GL_FWSTS`, `GLNVM_GENS`, `IXGBE_GL_MNG_FWSM`, `IXGBE_GLNVM_FLA`, and PF host-interface registers `IXGBE_PF_HIDA`, `IXGBE_PF_HIBA`, and `IXGBE_PF_HICR`.
- ACI constants define API version expectations, descriptor size, max buffer size, send/release timeouts, and command opcodes in `enum ixgbe_aci_opc`.
- ACI command structures cover expanded errors, disabling RXEN, PHY capabilities/configuration, restart autonegotiation, link status, event masks, topology queries, topology pins, port-ID LED control, SFF EEPROM access, NVM read/write/erase/activate/checksum/package/component-table operations.
- PHY and link bitmaps describe supported media/speeds, pause, low power, EEE, FEC, module qualification, link events, topology conflicts, power classes, link partner FEC/pause advertisement, and link-speed reporting.
- E610 runtime/cache structures include `struct ixgbe_link_status`, `struct ixgbe_hw_caps`, `struct ixgbe_hw_func_caps`, `struct ixgbe_hw_dev_caps`, `struct ixgbe_aci_event`, `struct ixgbe_aci_info`, `struct ixgbe_orom_info`, `struct ixgbe_nvm_info`, `struct ixgbe_netlist_info`, `struct ixgbe_bank_info`, and `struct ixgbe_flash_info`.

## Control Flow
This file is declarative, but it defines the request/response formats that drive E610 control flow in `ixgbe_e610.c` and related devlink/firmware update code. E610 initialization sends ACI commands using these opcodes and structs to negotiate firmware version, enumerate device/function capabilities, get PHY/link information, program link configuration, read NVM, validate checksums, determine active flash banks, and expose firmware/flash information to devlink and ethtool.

Runtime link control follows a firmware-mediated path: code fills `struct ixgbe_aci_cmd_get_phy_caps` or `struct ixgbe_aci_cmd_set_phy_cfg` descriptors, points them at data buffers such as `struct ixgbe_aci_cmd_get_phy_caps_data` or `struct ixgbe_aci_cmd_set_phy_cfg_data`, and interprets `struct ixgbe_aci_cmd_get_link_status_data` into `struct ixgbe_link_status`. NVM and update flows use `struct ixgbe_aci_cmd_nvm`, checksum, package-data, and component-table payloads, then cache parsed versions in `struct ixgbe_flash_info`.

## State and Persistence Behavior
The header defines both transient command payloads and persistent firmware/flash metadata. Transient ACI structs are stack or DMA-buffer command formats used for individual firmware transactions. Persistent device state lives in E610 flash/shadow RAM, represented by NVM, OROM, netlist, CSS, bank, and checksum offsets. Driver caches of that persistent state are stored in `struct ixgbe_flash_info` within `struct ixgbe_hw`.

`struct ixgbe_aci_info` holds runtime synchronization state for the Admin Command Interface, specifically a mutex and last firmware AdminQ error. `struct ixgbe_link_status` stores the current and previous link observations through `struct ixgbe_link_info` in `ixgbe_type.h`. Capability structures cache function and device capabilities such as queues, MSI-X vectors, RSS table size, DCB, WoL, external topology image support, update restrictions, and security/update management flags.

## Dependencies and Integration Points
The header includes `linux/net/intel/libie/adminq.h` and relies on libie AdminQ descriptors and status enums. It is included by `ixgbe_type.h`, which embeds E610 ACI, flash, capability, and link-status state into the generic ixgbe hardware object. It is consumed by `ixgbe_e610.c`, firmware update code, devlink region/info paths, PTP/link handling, ethtool E610 operations, and any path that needs to translate firmware-reported E610 capabilities into legacy ixgbe abstractions.

Its integration boundary is firmware rather than raw MMIO for most operations. Callers must marshal descriptors, buffers, and little-endian fields exactly as firmware expects. E610 link support also integrates with pluggable module/SFF EEPROM access, topology nodes and GPIO/LED pins, management protocols, NVM update activation, and devlink-visible flash component versions.

## Risks and Edge Cases
- ACI command structs are firmware ABI. Field ordering, packing, endian conversion, and buffer length must match firmware documentation or commands can fail or corrupt interpretation.
- Some opcodes intentionally share numeric values for different command contexts, such as NVM write activate and shadow RAM dump. Callers must select fields and flags according to the specific command.
- Link-speed and PHY-type bitmaps extend beyond legacy ixgbe speeds. Translation into legacy `ixgbe_link_speed` must reject or map unsupported bits carefully.
- Many capability flags are cached booleans derived from firmware bitfields. Parser mistakes can incorrectly enable firmware update, WoL, queue, DCB, or reset-avoidance behavior.
- Flash bank pointers and sizes describe persistent image layout. Incorrect active-bank selection or pointer-unit handling can report wrong versions or target the wrong bank during update.
- Timeouts are long for synchronous/admin operations and NVM updates; reset, remove, and firmware recovery paths must avoid deadlocks while the ACI lock is held.
- Topology and module commands depend on firmware-reported node handles, port numbers, and page/bank semantics; bad validation can lead to wrong module EEPROM reads or LED/GPIO actions.

## Test Signals
- Build E610-enabled ixgbe paths with libie AdminQ headers and validate all ACI structures compile with expected sizes and endianness annotations.
- Firmware-command tests should mock or exercise get-version, capability listing, PHY capability/configuration, link-status, link-event mask, SFF EEPROM, NVM read/checksum, and component-table commands.
- Devlink and ethtool tests should verify NVM/OROM/netlist version extraction, pending update flags, update-disabled/security flags, and flash bank selection.
- Link tests should cover copper, SFP, backplane, SGMII/USXGMII, pause, EEE, FEC, low-power, module qualification, topology conflict, and link-event transitions.
- Failure-injection should cover ACI lock contention, firmware expanded errors, timeout constants, invalid NVM pointers, blank NVM mode, rollback/recovery mode, and unsupported media/module responses.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ixgbe/ixgbe_type_e610.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ixgbe/ixgbe_x540.c -->
# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ixgbe/ixgbe_x540.c

## Purpose
`ixgbe_x540.c` implements the X540 generation-specific operation tables and helper routines for the ixgbe driver. It supplies X540 invariants, reset/start/link wrappers, EEPROM read/write/checksum/flash-update logic, software/firmware semaphore handling, LED blink control, and the exported `ixgbe_X540_info` descriptor used by probe-time board selection. Some logic is also conditionally shared with E610 paths, notably reset behavior that skips unsupported SAN/WWN handling for `ixgbe_mac_e610`.

## Important APIs, Types, and Functions
- X540 sizing constants define 128 Tx queues, 128 Rx queues, 128 RAR entries, 128 multicast table entries, 128 VFTA entries, and 384 KB Rx packet buffer size.
- Public generation hooks include `ixgbe_get_media_type_X540`, `ixgbe_get_invariants_X540`, `ixgbe_setup_mac_link_X540`, `ixgbe_reset_hw_X540`, `ixgbe_start_hw_X540`, `ixgbe_init_eeprom_params_X540`, `ixgbe_acquire_swfw_sync_X540`, `ixgbe_release_swfw_sync_X540`, `ixgbe_init_swfw_sync_X540`, `ixgbe_blink_led_start_X540`, and `ixgbe_blink_led_stop_X540`.
- EEPROM helpers wrap generic EERD/EEWR operations with X540 semaphore acquisition: `ixgbe_read_eerd_X540`, `ixgbe_read_eerd_buffer_X540`, `ixgbe_write_eewr_X540`, and `ixgbe_write_eewr_buffer_X540`.
- Checksum and persistence helpers include `ixgbe_calc_eeprom_checksum_X540`, `ixgbe_validate_eeprom_checksum_X540`, `ixgbe_update_eeprom_checksum_X540`, `ixgbe_update_flash_X540`, and `ixgbe_poll_flash_update_done_X540`.
- Semaphore internals include `ixgbe_get_swfw_sync_semaphore` and `ixgbe_release_swfw_sync_semaphore`.
- Static operation tables `mac_ops_X540`, `eeprom_ops_X540`, `phy_ops_X540`, `ixgbe_mvals_X540`, and exported `ixgbe_X540_info` connect this implementation to the core ixgbe probe and common code.

## Control Flow
Probe-time setup selects `ixgbe_X540_info`, calls `ixgbe_get_invariants_X540`, and installs the X540 operation tables into `struct ixgbe_hw`. Invariants set copper PHY power control, table sizes, queue counts, Rx packet buffer size, and MSI-X vector count from PCIe capabilities. Link setup is delegated to the PHY `setup_link_speed` operation, while media type is always copper.

`ixgbe_reset_hw_X540` first stops the adapter through the MAC ops table and clears pending Tx transactions. It acquires the PHY/NVM semaphore mask, sets `IXGBE_CTRL_RST`, flushes writes, releases the semaphore, then polls for reset completion and waits for post-reset stabilization. If `IXGBE_FLAGS_DOUBLE_RESET_REQUIRED` is set, it clears the flag and repeats the reset sequence. After reset it programs Rx packet buffer size, reads the permanent MAC address, initializes receive address registers and multicast tables, and, for non-E610 MACs, reads/programs SAN MAC and WWN prefix state.

EEPROM control initializes flash-backed EEPROM parameters once by reading `IXGBE_EEC(hw)` and deriving word size. Read/write operations acquire `IXGBE_GSSR_EEP_SM`, call generic EERD/EEWR helpers, and release the semaphore. Checksum validation first does a quick word-zero read to avoid long repeated failures, then takes the EEPROM semaphore, calculates the checksum by summing base words and valid pointer sections, reads the stored checksum directly with the generic helper, and compares. Updating writes the calculated checksum and triggers a flash update.

Software/firmware synchronization uses two levels of arbitration. `ixgbe_get_swfw_sync_semaphore` obtains the SMBI bit between software drivers and the REGSMP bit between software and firmware. `ixgbe_acquire_swfw_sync_X540` then checks requested software masks, corresponding firmware masks, and flash hardware masks in `SWFW_SYNC`, retrying with sleeps. If firmware or hardware appears stuck, it can assert the software bit anyway; if another software owner appears stuck, it clears known software bits and returns busy. Release clears owned bits and drops the underlying semaphores. `ixgbe_init_swfw_sync_X540` forcibly clears stale locks during initialization.

LED blink control checks index bounds, forces MAC link/speed if the link is down so LED blinking can work, updates the `IXGBE_LEDCTL` blink mode, and later restores default link-active LED mode and clears forced MAC link bits.

## State and Persistence Behavior
Most state changes are hardware register writes through MMIO. Reset mutates adapter hardware state, reinitializes Rx address/filter state, updates `hw->mac.perm_addr`, may reserve the last RAR for SAN MAC, and may decrement `hw->mac.num_rar_entries`. EEPROM initialization updates the runtime `hw->eeprom` cache. EEPROM write/checksum paths mutate shadow RAM and then request hardware to copy shadow RAM to persistent flash using `IXGBE_EEC_FLUP`; revision 0 hardware may require an additional sector update when `IXGBE_EEC_SEC1VAL` is set.

Semaphore functions mutate `SWFW_SYNC` and `SWSM` hardware bits and are critical for persistent NVM/flash and PHY accesses. LED blink functions temporarily alter MAC forced-link bits and LED control bits, restoring them on stop. There is no disk persistence.

## Dependencies and Integration Points
The file depends on Linux PCI/delay/scheduler APIs and ixgbe internal headers `ixgbe.h`, `ixgbe_mbx.h`, `ixgbe_phy.h`, and `ixgbe_x540.h`. It delegates much work to generic ixgbe helpers: adapter stop/start, Tx pending clear, PCIe MSI-X count, generic link and PHY operations, generic EEPROM EERD/EEWR, generic checksum/PBA helpers, RAR/MTA/VLAN/RSS/filter setup, flow control, firmware driver version, anti-spoofing, mailbox ops, and copper PHY power/overtemperature handling.

Its exported `ixgbe_X540_info` is consumed by the PCI board table in main driver code. X550 code includes `ixgbe_x540.h` and can reuse selected X540 operations. E610 code includes the X540 header as well, and `ixgbe_reset_hw_X540` has an explicit E610 branch that returns before unsupported SAN MAC and WWN work.

## Risks and Edge Cases
- Reset sequencing depends on semaphore acquisition and polling `IXGBE_CTRL_RST_MASK`. Timeout or semaphore failure leaves the adapter stopped or partially reset.
- Double-reset handling uses a MAC flag and `goto`; callers must ensure the flag is only set for conditions that really require one extra reset.
- The reset function sets `hw->mac.num_rar_entries = IXGBE_X540_MAX_TX_QUEUES`, which has the same value as RAR entries but is semantically odd; changing constants independently could introduce a bug.
- EEPROM checksum calculation intentionally bypasses synchronized EEPROM ops while already holding the semaphore. Calling it without proper outer synchronization would race with firmware or other software.
- Flash update polling uses fixed microsecond delays and returns `-EIO` on timeout; slow or busy flash hardware can cause checksum update failure after shadow RAM was already written.
- SW/FW semaphore recovery can force ownership when firmware/hardware appears stuck. This avoids permanent deadlock but risks conflicting with firmware if the apparent hang is only a long operation.
- LED blink start forces link bits when link is down; stop must run to restore MAC state. Error or removal paths should not leave forced-link settings active.
- E610 reuse of X540 reset behavior is guarded only for later SAN/WWN work; earlier register writes must remain valid for E610 users.

## Test Signals
- Probe tests should verify invariants: queue limits, table sizes, Rx packet buffer size, copper media type, MSI-X count, and operation table assignment.
- Reset tests should cover normal reset, semaphore failure, reset-bit timeout, double-reset flag, E610 skip path, SAN MAC programming, and RAR count adjustment.
- EEPROM tests should exercise read/write single and buffer paths, checksum validation success/failure, invalid pointer sections, word-zero read failure, flash update timeout, and revision-0 second-sector update.
- Concurrency tests should stress `ixgbe_acquire_swfw_sync_X540` and release with NVM, PHY, I2C, SW management, firmware-owned, hardware flash-owned, and stuck software-owner masks.
- LED tests should cover invalid indices, link-up blink, link-down forced blink, and restoration of `IXGBE_MACC` and `IXGBE_LEDCTL`.
- Build tests should ensure all operation table callbacks remain compatible with `struct ixgbe_mac_operations`, `struct ixgbe_eeprom_operations`, and `struct ixgbe_phy_operations`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ixgbe/ixgbe_x540.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ixgbe/ixgbe_x540.h -->
# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ixgbe/ixgbe_x540.h

## Purpose
`ixgbe_x540.h` declares the X540 generation-specific entry points exported by `ixgbe_x540.c` to the rest of the ixgbe driver. It is the small public interface for X540 invariants, reset/start/link setup, media reporting, LED blink control, SW/FW synchronization, and EEPROM parameter initialization.

## Important APIs, Types, and Functions
- `ixgbe_get_invariants_X540(struct ixgbe_hw *hw)` fills X540 MAC/PHY invariant limits and callback defaults.
- `ixgbe_setup_mac_link_X540(struct ixgbe_hw *hw, ixgbe_link_speed speed, bool autoneg_wait_to_complete)` delegates MAC link setup to PHY link-speed setup.
- `ixgbe_reset_hw_X540(struct ixgbe_hw *hw)` performs X540 reset and post-reset address/filter initialization.
- `ixgbe_start_hw_X540(struct ixgbe_hw *hw)` runs generic hardware start plus generation-2 start logic.
- `ixgbe_get_media_type_X540(struct ixgbe_hw *hw)` reports copper media.
- `ixgbe_blink_led_start_X540` and `ixgbe_blink_led_stop_X540` expose X540 LED identification behavior.
- `ixgbe_acquire_swfw_sync_X540`, `ixgbe_release_swfw_sync_X540`, and `ixgbe_init_swfw_sync_X540` expose X540 semaphore management for shared NVM/PHY/I2C/management resources.
- `ixgbe_init_eeprom_params_X540(struct ixgbe_hw *hw)` initializes flash-backed EEPROM metadata.

## Control Flow
The header itself has only include-guard and declaration flow. Consumers include it when installing X540 callbacks into operation tables or reusing X540 helper behavior from neighboring generation files. At runtime, calls enter the implementations in `ixgbe_x540.c` through direct references or through `struct ixgbe_mac_operations` and `struct ixgbe_eeprom_operations`.

## State and Persistence Behavior
The header owns no state. Declared functions mutate `struct ixgbe_hw`, hardware MMIO registers, EEPROM/shadow RAM/flash state, LED control, and SW/FW semaphore registers in their implementation. The included `ixgbe_type.h` supplies the `struct ixgbe_hw` definition and related enums used by every prototype.

## Dependencies and Integration Points
The header includes `ixgbe_type.h`, so any file including `ixgbe_x540.h` receives the full ixgbe hardware type model and E610 supplemental types. It is included by `ixgbe_x540.c`, X550 implementation code, and E610 code that shares selected X540 reset or synchronization behavior. It connects generation-specific implementation to common probe, reset, EEPROM, LED, and link-management paths.

## Risks and Edge Cases
- `ixgbe_setup_mac_link_X540` is declared twice in the header. The duplicate prototype is harmless in C but is maintenance noise and can hide prototype drift if one copy is edited and the other is not.
- Because the header exposes synchronization and reset functions used by other generation code, signature or semantic changes can affect X550/E610 callers as well as X540.
- Including `ixgbe_type.h` makes this header broad; changes to shared types can force recompilation or expose E610 dependencies to every X540 consumer.

## Test Signals
- Compile tests should catch prototype drift between this header and `ixgbe_x540.c`.
- Include-order tests should verify consumers can include this header without missing `bool`, `u32`, `ixgbe_link_speed`, or `struct ixgbe_hw` definitions.
- Static checks should flag the duplicate `ixgbe_setup_mac_link_X540` declaration if the project enforces duplicate-prototype warnings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ixgbe/ixgbe_x540.h -->
