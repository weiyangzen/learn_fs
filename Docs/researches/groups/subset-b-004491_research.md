# Research Report: subset-b-004491

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/igc/igc_defines.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/igc/igc_defines.h

## Purpose
`igc_defines.h` is the low-level hardware contract for the Intel IGC Ethernet driver. It centralizes register bit definitions, masks, timeout constants, descriptor flags, advertised link modes, wake-on-LAN filters, NVM/PHY encodings, TSN/PTP/PTM fields, packet buffer sizing macros, EEE/LTR knobs, and common driver error codes used by the rest of the IGC sources.

## Important APIs, Types, And Constants
This header exports no functions or structs. Its important interfaces are macros consumed by register access code: descriptor alignment requirements `REQ_TX_DESCRIPTOR_MULTIPLE` and `REQ_RX_DESCRIPTOR_MULTIPLE`; register bit groups such as `IGC_CTRL_*`, `IGC_STATUS_*`, `IGC_ICR_*`, `IGC_IMS_*`, `IGC_RCTL_*`, `IGC_TCTL_*`; speed/duplex and advertise values such as `SPEED_2500` and `ADVERTISE_2500_FULL`; NVM values such as `NVM_CHECKSUM_REG`, `NVM_SUM`, and `IGC_EERD_EEWR_MAX_COUNT`; TSN and launch-time fields such as `IGC_TQAVCTRL_*`, `IGC_TXQCTL_*`, `IGC_TXOFFSET_SPEED_*`; PTP/PTM fields such as `IGC_TSYNCRXCTL_*`, `IGC_TSYNCTXCTL_*`, `IGC_PTM_*`; and EEE/LTR fields such as `IGC_IPCNFG_EEE_*`, `IGC_EEER_*`, and `IGC_LTR*`.

## Control Flow
There is no runtime control flow. The file shapes control flow elsewhere by providing the bit tests and register values used in reset, link setup, interrupt handling, ethtool operations, NVM updates, timestamping, TSN offload, and power-management paths.

## State And Persistence
The macros describe state stored in hardware registers, NVM/flash, descriptor rings, and cached driver fields. Values such as WOL masks can persist across suspend behavior through adapter configuration; NVM constants govern checksum and flash commit flows; EEE and LTR definitions affect link power state.

## Dependencies And Integration Points
The header includes `<linux/bitfield.h>` for `BIT`, `GENMASK`, `FIELD_PREP`, and related helpers. It is included by `igc_hw.h`, `igc_mac.h`, and many C files that access MMIO registers through `rd32`/`wr32`. Changes here have wide blast radius because most source files treat these macros as device specification.

## Risks
Wrong masks or shifts can silently program incorrect hardware bits, break link negotiation, corrupt NVM operations, misroute interrupts, or invalidate timestamp/TSN behavior. ABI-sensitive values used by ethtool register dumps and descriptors must remain consistent with hardware manuals and existing userspace expectations.

## Test Signals
Useful signals include successful driver probe/reset, `ethtool -d` register dumps, `ethtool -S` statistics, WOL suspend/resume tests, EEPROM checksum validation, link-mode negotiation at 10/100/1000/2500 Mbps, PTP timestamp tests, TSN qdisc offload tests, and self-tests that exercise register patterns and NVM validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/igc/igc_defines.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/igc/igc_diag.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/igc/igc_diag.c

## Purpose
`igc_diag.c` implements diagnostic helpers used by the driver's ethtool self-test path. It validates selected MMIO registers with write/read patterns, validates NVM checksum state, and checks physical link availability.

## Important APIs, Types, And Functions
The public functions are `igc_reg_test()`, `igc_eeprom_test()`, and `igc_link_test()`, declared in `igc_diag.h` and called by `igc_ethtool_diag_test()`. The static `reg_test[]` table names registers, array lengths, test type, readable mask, and writable mask. Static helpers `reg_pattern_test()` and `reg_set_and_check()` save the original register value, write a test value, read back, compare with masks, restore the original value, and report failures through `netdev_err()`.

## Control Flow
`igc_reg_test()` first treats `IGC_STATUS` as a special case because it has mixed read-only, toggle, and writable bits. It then walks `reg_test[]` until the zero terminator and dispatches each entry by test type: normal register arrays use `0x40` spacing, receive-address table halves use `8` byte spacing, and MTA tables use `4` byte spacing. On the first failure it stores the failing register or status marker in `*data` and returns false. `igc_eeprom_test()` calls `hw->nvm.ops.validate()`. `igc_link_test()` sleeps five seconds for autonegotiation and calls `igc_has_link()`.

## State And Persistence
Register tests temporarily mutate hardware registers but attempt to restore each original value immediately. NVM validation is read-only through the NVM operation table. Link testing waits but does not intentionally reconfigure link state.

## Dependencies And Integration Points
The file depends on `igc.h` for adapter, ring, register access, and logging infrastructure, and on `igc_diag.h` for the test table type and constants. It is integrated into ethtool offline and online self-tests; offline mode closes or resets the interface around these tests.

## Risks
Pattern tests touch live hardware registers, so they must be run only in the controlled offline path. A bad mask in `reg_test[]` can report false failures or leave state disturbed. `igc_eeprom_test()` assumes `validate` is non-NULL, which is safe only when NVM ops were initialized for the device path that supports validation.

## Test Signals
Signals are `ethtool -t <dev> offline` and `online`, expected self-test data values, kernel log messages for failing registers, preservation of link after test recovery, and no regressions in reset/open paths after offline diagnostics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/igc/igc_diag.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/igc/igc_diag.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/igc/igc_diag.h

## Purpose
`igc_diag.h` declares the diagnostic self-test entry points and the register-test table format shared by `igc_diag.c` and the ethtool self-test implementation.

## Important APIs, Types, And Functions
It declares `igc_reg_test(struct igc_adapter *, u64 *)`, `igc_eeprom_test(struct igc_adapter *, u64 *)`, and `igc_link_test(struct igc_adapter *, u64 *)`. It also defines `struct igc_reg_test` with fields `reg`, `array_len`, `test_type`, `mask`, and `write`. Test type constants are `PATTERN_TEST`, `SET_READ_TEST`, `TABLE32_TEST`, `TABLE64_TEST_LO`, and `TABLE64_TEST_HI`.

## Control Flow
The header itself has no runtime flow. Its table contract drives `igc_reg_test()` dispatch: regular arrays are spaced differently from 32-bit tables and 64-bit low/high table halves.

## State And Persistence
No state is stored in this header. Its declarations describe functions that may temporarily alter hardware registers during offline diagnostics and read NVM/link state.

## Dependencies And Integration Points
The prototypes rely on `struct igc_adapter` being visible through prior includes from callers such as `igc_ethtool.c`. The register table structure is tightly coupled to register spacing assumptions documented in the comment block.

## Risks
Because the header has no include guard in the displayed file, it relies on normal inclusion discipline and may be vulnerable to duplicate declarations if included through unusual paths. Any change to `struct igc_reg_test` or test constants must be synchronized with `igc_diag.c`.

## Test Signals
Build coverage is the main signal for prototype and structure consistency. Runtime signals come through ethtool self-tests that exercise all declared functions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/igc/igc_diag.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/igc/igc_dump.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/igc/igc_dump.c

## Purpose
`igc_dump.c` provides debug dumping for selected hardware registers and Tx/Rx descriptor rings. It is used when hardware debug message levels are enabled, primarily from reset or diagnostic logging paths.

## Important APIs, Types, And Functions
The exported functions are `igc_rings_dump(struct igc_adapter *)` and `igc_regs_dump(struct igc_adapter *)`. `struct igc_reg_info` maps register offsets to names for `igc_reg_info_tbl[]`. The static `igc_regdump()` helper reads scalar registers or four queue-indexed instances for ring register families such as `RDLEN`, `RDH`, `RDT`, `RXDCTL`, `TDBAL`, `TDLEN`, `TDH`, and `TXDCTL`.

## Control Flow
`igc_regs_dump()` prints a header and walks `igc_reg_info_tbl[]`, delegating formatting to `igc_regdump()`. `igc_rings_dump()` first checks `netif_msg_hw(adapter)`, prints device state, then returns early if the netdev is not running. It prints Tx summaries, optionally detailed Tx descriptors and packet data when `netif_msg_tx_done()` and `netif_msg_pktdata()` are enabled, then prints Rx summaries and optional detailed Rx descriptors when `netif_msg_rx_status()` is enabled.

## State And Persistence
The file is observational. It reads MMIO registers, descriptors, DMA metadata, SKB pointers, page-backed Rx buffers, and ring indices, but does not intentionally mutate device or driver state.

## Dependencies And Integration Points
It depends on `igc.h` for adapter/ring layout, descriptor access macros, netdev logging, `rd32`, DMA unmap metadata, and buffer sizing. `igc_main.c` calls the dump helpers from reset-task diagnostics when message flags request hardware logging.

## Risks
Verbose dumps can expose packet contents and pointer-like values in logs when packet data logging is enabled. Ring dumps race with live traffic unless called in controlled contexts, so values are diagnostic snapshots rather than stable state. Excess logging may affect performance or log volume.

## Test Signals
Signals include enabling driver message levels, triggering reset or dump paths, confirming register and queue formats are readable, validating no crashes when rings are absent or netdev is down, and checking packet hex dumps only appear under the expected message flags.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/igc/igc_dump.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/igc/igc_ethtool.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/igc/igc_ethtool.c

## Purpose
`igc_ethtool.c` is the IGC driver's ethtool control and reporting surface. It exposes driver information, register and EEPROM access, WOL, message levels, link state, ring sizing, pause parameters, statistics, interrupt coalescing, RSS and n-tuple filtering, channel count, timestamp capabilities, private flags, EEE, MAC Merge/FPE controls, link settings, and self-tests.

## Important APIs, Types, And Functions
The public entry point is `igc_ethtool_set_ops()`, which assigns the static `igc_ethtool_ops`. Important data tables are `igc_gstrings_stats[]`, `igc_gstrings_net_stats[]`, `igc_gstrings_test[]`, and `igc_priv_flags_strings[]`. Major callbacks include `igc_ethtool_get_drvinfo()`, `get_regs()`, `get_wol()`/`set_wol()`, EEPROM get/set, ringparam get/set, pause get/set, strings/stats handlers, coalesce get/set, RXNFC add/delete/query, RSS indirection get/set via `igc_write_rss_indir_tbl()`, channel get/set, timestamp info, private flags, EEE get/set, MAC Merge get/set/stats, link ksettings get/set, and `igc_ethtool_diag_test()`.

## Control Flow
Most callbacks translate ethtool requests into adapter state changes or register reads. Setters validate user input, update cached adapter/hardware fields, then either write hardware directly or reinitialize the interface. Ring changes allocate temporary rings, bring the device down, swap resources, and bring it back up. Link and pause setters serialize with `__IGC_RESETTING`. RXNFC insertion builds an `igc_nfc_rule`, validates masks and duplicates under `nfc_rule_lock`, and delegates hardware programming to main-driver helpers. Offline self-test powers PHY, tests link, closes/resets, runs register and EEPROM tests, resets again, then reopens if needed.

## State And Persistence
The file changes persistent in-memory driver state such as `adapter->wol`, `msg_enable`, `rx_ring_count`, `tx_ring_count`, `fc_autoneg`, `hw->fc.*`, `rx_itr_setting`, `tx_itr_setting`, RSS flags and indirection table, `rss_queues`, private flags, `hw->dev_spec._base.eee_enable`, and FPE configuration. EEPROM writes can persist to flash through `hw->nvm.ops.update()`. WOL state is also pushed to device wakeup settings.

## Dependencies And Integration Points
It depends on Linux ethtool/netdevice APIs, runtime PM, MDIO definitions, `igc_diag.h` self-tests, `igc_tsn.h` TSN/FPE helpers, NVM ops from `igc_i225.c`, register constants from `igc_defines.h`, and main driver helpers such as `igc_up()`, `igc_down()`, `igc_reset()`, `igc_reinit_locked()`, `igc_reinit_queues()`, `igc_add_nfc_rule()`, and `igc_tsn_offload_apply()`.

## Risks
This file is a high-risk user-facing mutation surface. EEPROM writes can partially modify NVM before checksum/flash update failures. Ring, channel, pause, EEE, private flag, and link setters can disrupt traffic through reset/reinit. UDP RSS warns about fragmented packet reordering. NFC rules have strict mask support and duplicate detection requirements. The register dump ABI contains a compatibility workaround where RAL/RAH values are written again after earlier index overlap.

## Test Signals
Useful signals include `ethtool -i`, `-d`, `-S`, `-s`, `-g/-G`, `-a/-A`, `-c/-C`, `-l/-L`, `-x/-X`, `-n/-N`, `--show-eee/--set-eee`, `--show-mm/--set-mm`, WOL suspend/resume tests, EEPROM read/write with checksum validation, offline and online `ethtool -t`, queue reinit under traffic, RSS distribution tests, and TSN/FPE offload validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/igc/igc_ethtool.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/igc/igc_hw.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/igc/igc_hw.h

## Purpose
`igc_hw.h` defines the hardware-facing object model for the IGC driver. It identifies supported device IDs, operation tables, per-device MAC/NVM/PHY/flow-control state, PCI bus information, device-specific flags, and the hardware statistics layout.

## Important APIs, Types, And Functions
Key types include `struct igc_mac_operations`, `struct igc_nvm_operations`, `struct igc_phy_operations`, `struct igc_info`, `struct igc_mac_info`, `struct igc_nvm_info`, `struct igc_phy_info`, `struct igc_fc_info`, `struct igc_dev_spec_base`, `struct igc_hw`, and `struct igc_hw_stats`. Enums define MAC type, media type, NVM type, and flow-control mode. The file declares `igc_get_hw_dev()` and `hw_dbg()`, and exposes `igc_base_info`.

## Control Flow
The header has no direct runtime flow, but its operation tables drive dynamic dispatch for reset, initialization, link checks, physical setup, RAR programming, MAC address reads, speed/duplex reads, SW/FW semaphore acquisition, NVM access, and PHY access.

## State And Persistence
`struct igc_hw` is the central persistent runtime state embedded in `struct igc_adapter`. It stores MMIO base, backpointer, MAC addresses, multicast table shadow, RAR counts, firmware flags, NVM geometry and ops, PHY addressing and advertisement, flow-control watermarks/modes, bus function, device IDs, and revision. `struct igc_hw_stats` is the software accumulation target for hardware counters.

## Dependencies And Integration Points
It includes Linux types, Ethernet/netdevice definitions, register definitions, hardware defines, MAC/PHY/NVM/I225/base headers. `igc_base.c` fills operation tables, `igc_main.c` embeds and initializes `struct igc_hw`, and ethtool/diagnostic/MAC/NVM code read and mutate its fields.

## Risks
Changing structure layout or operation contracts affects nearly every driver path. NULL operation pointers are possible for unsupported NVM write/update/validate paths, so callers must respect initialization outcomes. Cached fields such as flow-control mode, advertised link modes, and EEE enablement must stay synchronized with hardware programming.

## Test Signals
Signals include successful probe across supported PCI IDs, reset/init behavior, MAC address programming, NVM reads, PHY register access, link negotiation, flow-control configuration, statistics updates, and build coverage for all operation table users.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/igc/igc_hw.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/igc/igc_i225.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/igc/igc_i225.c

## Purpose
`igc_i225.c` implements I225/I226-specific hardware services for SW/FW semaphore coordination, NVM shadow RAM and flash access, checksum validation/update, EEE programming, and Latency Tolerance Reporting threshold calculation.

## Important APIs, Types, And Functions
Public functions are `igc_acquire_swfw_sync_i225()`, `igc_release_swfw_sync_i225()`, `igc_init_nvm_params_i225()`, `igc_get_flash_presence_i225()`, `igc_set_eee_i225()`, and `igc_set_ltr_i225()`. Static helpers include NVM acquire/release wrappers, `igc_get_hw_semaphore_i225()`, shadow RAM read/write helpers, checksum validate/update helpers, and flash update polling.

## Control Flow
NVM access first acquires driver/FW semaphores, then performs burst reads or writes capped by `IGC_EERD_EEWR_MAX_COUNT`, releasing between bursts to avoid holding synchronization too long. Checksum validation temporarily swaps `hw->nvm.ops.read` to a no-semaphore read while a semaphore is already held. Checksum update reads words up to `NVM_CHECKSUM_REG`, writes the complement to reach `NVM_SUM`, then commits shadow RAM to flash. EEE programming toggles advertisement bits and LPI enable bits. LTR calculation reads link speed, EEE timing, and Rx packet buffer size, computes min/max latency thresholds and scales, then writes LTR registers only when changed.

## State And Persistence
This file mutates hardware semaphore registers, `SW_FW_SYNC`, NVM shadow RAM, flash contents, EEE registers, LTR registers, and `hw->dev_spec._base.clear_semaphore_once`. Flash update and checksum paths are persistent device changes. EEE and LTR are runtime hardware state derived from driver settings and link state.

## Dependencies And Integration Points
It depends on `igc_hw.h` for register constants, operation structures, `rd32`/`wr32`, and shared helper declarations. `igc_base.c` calls `igc_init_nvm_params_i225()`. `igc_main.c`, `igc_mac.c`, and ethtool EEE paths call EEE/LTR helpers during reset, link, suspend/resume, and user configuration.

## Risks
Semaphore timeout handling is critical: failure can block PHY/NVM access or race firmware. NVM writes can partially complete, leaving shadow RAM inconsistent if a later word fails. The wrapper write path passes the original `offset` for each burst, which is worth reviewing if multi-burst writes are used. LTR arithmetic must avoid invalid thresholds and preserve expected power behavior.

## Test Signals
Signals include NVM read/write/checksum validation, flash commit completion, probe on flash and no-flash devices, forced semaphore contention tests, EEE enable/disable and advertised mode checks, link-up LTR programming at all supported speeds, suspend/resume power tests, and ethtool EEPROM/EEE workflows.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/igc/igc_i225.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/igc/igc_i225.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/igc/igc_i225.h

## Purpose
`igc_i225.h` declares the I225/I226-specific helper interface consumed by generic hardware, MAC, main-driver, and ethtool code.

## Important APIs, Types, And Functions
The declarations cover SW/FW synchronization (`igc_acquire_swfw_sync_i225()`, `igc_release_swfw_sync_i225()`), NVM parameter initialization and flash detection (`igc_init_nvm_params_i225()`, `igc_get_flash_presence_i225()`), EEE programming (`igc_set_eee_i225()`), and LTR programming (`igc_set_ltr_i225()`).

## Control Flow
No control flow is implemented here. The prototypes allow generic operation tables and user-facing paths to call I225-specific logic without including implementation details.

## State And Persistence
The declared functions mutate semaphores, NVM/flash operation tables and data, EEE registers, and LTR registers. This header itself stores no state.

## Dependencies And Integration Points
It depends on `struct igc_hw` and `s32` being available through including context, normally via `igc_hw.h`. `igc_hw.h` includes this header, while `igc_i225.c` provides the implementations.

## Risks
Prototype drift would break operation table initialization or cross-file calls. Since these functions include persistent NVM and power-management behavior, callers must handle errors and hardware capability checks correctly.

## Test Signals
Build coverage, successful probe, ethtool EEPROM and EEE operations, link-up LTR programming, and SW/FW semaphore acquisition paths are the relevant signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/igc/igc_i225.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/igc/igc_leds.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/igc/igc_leds.c

## Purpose
`igc_leds.c` integrates IGC hardware LEDs with the Linux LED class and netdev trigger hardware-control API. It exposes three LEDs that can be set on/off or offloaded to link/activity indications.

## Important APIs, Types, And Functions
The public functions are `igc_led_setup()` and `igc_led_free()`. `struct igc_led_classdev` binds a `net_device`, LED class device, and LED index. Static helpers select LEDCTL masks/shifts, read/write LED mode, set brightness, validate hardware-control flags, set/get hardware-control mode, return the controlled netdev device, generate LED names, and register one LED classdev.

## Control Flow
Setup initializes `adapter->led_mutex`, allocates three LED descriptors, and registers each class device. On failure it unregisters already registered LEDs and frees memory. Brightness and hardware-control callbacks translate LED class requests into LEDCTL mode and blink bits. Register access is wrapped by runtime PM get/put and serialized by `adapter->led_mutex`. Free unregisters all three class devices and releases the allocation.

## State And Persistence
The file stores `adapter->leds` and mutates the hardware `IGC_LEDCTL` register. LED class devices use `LED_RETAIN_AT_SHUTDOWN`, so final LED state may be retained by the LED subsystem/hardware across shutdown paths. No NVM state is changed.

## Dependencies And Integration Points
It depends on Linux LED, netdev trigger, runtime PM, PCI naming, and `igc.h` for adapter state and register access. `igc_main.c` calls setup during probe and free during remove. Hardware control supports link speeds 10/100/1000/2500 and combined Rx+Tx activity.

## Risks
`igc_setup_ldev()` assigns `led_cdev->name` to a stack buffer, which is a lifetime-sensitive pattern to review against LED core behavior. Unsupported trigger combinations must return `-EOPNOTSUPP` to avoid programming ambiguous modes. Runtime PM errors from `pm_runtime_get_sync()` are not checked. Incorrect LED selection would write wrong LEDCTL bits.

## Test Signals
Signals include LED class device registration under `/sys/class/leds`, brightness on/off writes, netdev trigger offload for single link modes and combined Rx+Tx activity, rejection of unsupported flag combinations, suspend/resume behavior, probe/remove cleanup, and concurrent LED updates without register corruption.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/igc/igc_leds.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/igc/igc_mac.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/igc/igc_mac.c

## Purpose
`igc_mac.c` provides generic MAC-level operations for PCIe master disable, receive address programming, link and flow-control setup, counter clearing, speed/duplex reporting, hardware semaphore release, management pass-through detection, and multicast table programming.

## Important APIs, Types, And Functions
Public functions include `igc_disable_pcie_master()`, `igc_init_rx_addrs()`, `igc_setup_link()`, `igc_force_mac_fc()`, `igc_clear_hw_cntrs_base()`, `igc_rar_set()`, `igc_check_for_copper_link()`, `igc_config_collision_dist()`, `igc_config_fc_after_link_up()`, `igc_get_auto_rd_done()`, `igc_get_speed_and_duplex_copper()`, `igc_put_hw_semaphore()`, `igc_enable_mng_pass_thru()`, and `igc_update_mc_addr_list()`. Static helpers are `igc_set_fc_watermarks()` and `igc_hash_mc_addr()`.

## Control Flow
Link setup checks for reset blocking, normalizes default flow control, calls the hardware physical-interface setup op, initializes pause frame registers, and writes flow-control watermarks. Copper link checks run only when `mac->get_link_status` is set, call PHY link detection, clear the flag on link, check downshift, configure collision distance, resolve negotiated pause mode, and update I225 LTR. Flow-control resolution reads local and partner advertisement registers and applies IEEE pause/asymmetric-pause rules before forcing MAC bits. Multicast updates rebuild the software MTA shadow and write the full hardware MTA table.

## State And Persistence
The file mutates `hw->fc.current_mode`, `hw->fc.requested_mode`, `hw->mac.get_link_status`, `hw->mac.mta_shadow`, RAR registers, MTA registers, flow-control registers, TCTL collision distance, CTRL flow-control bits, SWSM semaphore bits, and LTR registers through the I225 helper. Counter clearing reads hardware counters that clear on read.

## Dependencies And Integration Points
It depends on `igc_mac.h`, `igc_hw.h`, PHY helpers such as `igc_phy_has_link()` and `igc_check_downshift()`, and I225 LTR support. `igc_base.c` wires several functions into MAC operation tables. `igc_main.c` calls link setup, multicast programming, and reset flows; ethtool pause/link settings call flow-control and setup helpers.

## Risks
Flow-control negotiation has many branch combinations and must preserve requested versus current mode. Counter clearing by read has destructive semantics for hardware counters. RAR writes require flushes to avoid bridge write combining. Multicast hash behavior depends on `mta_reg_count` and `mc_filter_type`; invalid values can misprogram filters. Link checks overwrite `ret_val` with LTR result at exit, which can mask earlier success/failure semantics if changed carelessly.

## Test Signals
Signals include link-up/down at all speeds, pause negotiation combinations, half-duplex disabling flow control, multicast reception with many addresses, RAR programming for MAC address changes, management pass-through behavior, reset with PCIe master disable, counter reset/update behavior, and ethtool pause/link setting changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/igc/igc_mac.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/igc/igc_mac.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/igc/igc_mac.h

## Purpose
`igc_mac.h` declares the generic MAC helper interface and management-mode enum used by hardware setup, main driver code, and ethtool paths.

## Important APIs, Types, And Functions
It declares MAC helpers for PCIe master disable, copper link checking, flow-control configuration, receive address initialization, link setup, hardware counter clearing, NVM auto-read completion, semaphore release, RAR programming, collision-distance programming, speed/duplex reporting, management pass-through detection, and multicast address list updates. It also defines `enum igc_mng_mode` values for no management, ASF, pass-through, IPMI, and host-interface-only modes.

## Control Flow
The header contains declarations only. The function set describes the expected MAC control flow: reset paths disable master and wait for NVM auto-read, init paths program RAR and multicast filters, link paths resolve flow control and speed, and management paths inspect firmware mode.

## State And Persistence
Declared functions mutate hardware registers and cached `struct igc_hw` MAC/flow-control state. The header itself stores no state.

## Dependencies And Integration Points
It includes `igc_hw.h`, `igc_phy.h`, and `igc_defines.h`, creating a shared contract among `igc_mac.c`, `igc_base.c`, `igc_main.c`, and ethtool. The prototypes are used both directly and through `struct igc_mac_operations`.

## Risks
Because this header participates in circular-looking hardware includes, changes should preserve include guards and forward declarations. Prototype changes can break operation table assignments and reset/link code. New MAC helpers should keep generic versus I225-specific boundaries clear.

## Test Signals
Build coverage, reset/link setup, flow-control ethtool changes, multicast/RAR programming, management pass-through behavior, and counter clear/update paths validate this interface.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/igc/igc_mac.h -->
