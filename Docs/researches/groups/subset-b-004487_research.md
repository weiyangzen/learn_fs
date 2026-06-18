# Research: subset-b-004487

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/igb/e1000_nvm.c -->
# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/igb/e1000_nvm.c

## Purpose
`e1000_nvm.c` implements the igb driver's generic NVM access path for EEPROM/flash backed device data. It provides low-level SPI bit-banging helpers, EERD/EEWR register polling, NVM acquire/release arbitration, read/write primitives, PBA string extraction, permanent MAC address loading, checksum validation/update, and firmware version decoding. The functions operate on `struct e1000_hw`, mostly through `hw->nvm.ops`, `hw->nvm` geometry fields, and MMIO registers defined in `e1000_regs.h`.

## Important APIs, Types, and Functions
The exported functions are `igb_acquire_nvm`, `igb_release_nvm`, `igb_read_nvm_spi`, `igb_read_nvm_eerd`, `igb_write_nvm_spi`, `igb_read_part_string`, `igb_read_mac_addr`, `igb_validate_nvm_checksum`, `igb_update_nvm_checksum`, and `igb_get_fw_version`. Internal helpers include `igb_raise_eec_clk`, `igb_lower_eec_clk`, `igb_shift_out_eec_bits`, `igb_shift_in_eec_bits`, `igb_poll_eerd_eewr_done`, `igb_standby_nvm`, `e1000_stop_nvm`, and `igb_ready_nvm_eeprom`. The file depends on `struct e1000_nvm_info` fields such as `type`, `delay_usec`, `opcode_bits`, `address_bits`, `word_size`, and `page_size`.

## Control Flow
SPI reads and writes first validate offset and word count against `nvm->word_size`, then acquire the NVM grant bit through `nvm->ops.acquire`. The SPI ready path clears chip select/clock, repeatedly sends `NVM_RDSR_OPCODE_SPI`, reads the status byte, and waits for `NVM_STATUS_RDY_SPI` to clear. Reads send a read opcode plus byte address and shift in 16-bit words with endian swapping. Writes run in page-sized batches: acquire, wait-ready, send write-enable, send write opcode and address, shift out swapped words until the EEPROM page boundary, sleep for write completion, then release.

EERD reads avoid the bit-banged path and loop over words by writing `E1000_EERD` with start and address fields, polling `E1000_NVM_RW_REG_DONE`, and extracting the data field. Checksum validation sums words `0..NVM_CHECKSUM_REG` and expects `NVM_SUM`; update writes `NVM_SUM - partial_sum`. Firmware version decoding branches by MAC type, with i211 and flashless i210 using iNVM, older devices using `NVM_VERSION` unless an ETrack ID is present, and i210/i350 optionally decoding combo option ROM fields.

## State and Persistence
This file changes persistent NVM only through `igb_write_nvm_spi` and `igb_update_nvm_checksum`; all other reads populate volatile driver state. `igb_read_mac_addr` copies receive address register 0 into `hw->mac.perm_addr` and `hw->mac.addr`. `igb_get_fw_version` populates the caller supplied `struct e1000_fw_version`. NVM access is serialized with the hardware request/grant bits in `E1000_EECD`; failure to release would block other software/firmware users.

## Dependencies and Integration Points
The code depends on `wr32`, `rd32`, and `wrfl` register helpers, NVM constants from the MAC/NVM headers, and `igb_read_invm_version` / `igb_get_flash_presence_i210` from the i210/i211 support path. It is consumed by probe/setup code for MAC address and firmware display, by ethtool EEPROM read/write operations, and by diagnostics that call `hw->nvm.ops.validate`.

## Risks
The main risks are hardware timing sensitivity, page-boundary errors in SPI writes, endian handling of word-addressable EEPROM data, checksum invalidation after writes, and lock/grant leaks on error paths. Firmware version decoding also has part-specific assumptions and silently returns all-zero output on unsupported MAC types. `igb_read_part_string` must preserve legacy PBA formatting and guard against invalid string length fields.

## Test Signals
Useful signals include `ethtool -e` reads matching expected NVM bytes, guarded `ethtool -E` writes followed by checksum update and successful reload, `igb_eeprom_test` passing, firmware version strings matching vendor tooling, permanent MAC address consistency after reset, and debug logs reporting no NVM grant, status, or checksum failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/igb/e1000_nvm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/igb/e1000_nvm.h -->
# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/igb/e1000_nvm.h

## Purpose
`e1000_nvm.h` is the public NVM interface for the igb hardware layer. It declares the NVM access, checksum, MAC address, PBA string, and firmware version helpers implemented by `e1000_nvm.c`, plus the `struct e1000_fw_version` result type consumed by adapter code that formats firmware information.

## Important APIs, Types, and Functions
The header exports `igb_acquire_nvm`, `igb_release_nvm`, `igb_read_mac_addr`, `igb_read_part_string`, `igb_read_nvm_eerd`, `igb_read_nvm_spi`, `igb_write_nvm_spi`, `igb_validate_nvm_checksum`, `igb_update_nvm_checksum`, and `igb_get_fw_version`. `struct e1000_fw_version` carries ETrack ID, EEPROM major/minor/build values, iNVM major/minor/image type, and option ROM validity plus major/build/patch fields.

## Control Flow
This file has no executable control flow. Its role is compile-time wiring: MAC-specific initialization code can assign function pointers in `hw->nvm.ops`, ethtool can call generic EEPROM paths indirectly through those operations, and adapter setup can call firmware/MAC address helpers without including implementation details.

## State and Persistence
The header does not own state. The declared functions operate on `struct e1000_hw`, modifying hardware NVM grants, persistent NVM contents, or fields under `hw->mac` and caller-provided output buffers depending on the function. `struct e1000_fw_version` is purely transient output.

## Dependencies and Integration Points
It assumes common igb typedefs and structures such as `s32`, `u8`, `u16`, `u32`, `bool`, and `struct e1000_hw` are visible through including translation units. Integration points include `igb_ethtool.c` EEPROM access, `igb_main.c` firmware string setup, and hardware initialization files that populate NVM ops.

## Risks
Header risk is mainly ABI drift inside the driver: changing prototypes or `struct e1000_fw_version` fields affects every caller that stores or formats NVM data. The distinction between SPI and EERD read APIs is visible here, so MAC setup must choose the correct operation for the device's NVM type.

## Test Signals
Build coverage is the first signal: all igb objects should compile with consistent prototypes. Runtime signals come from callers: ethtool EEPROM access, firmware version reporting, NVM checksum diagnostics, and successful MAC address initialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/igb/e1000_nvm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/igb/e1000_phy.c -->
# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/igb/e1000_phy.c

## Purpose
`e1000_phy.c` implements the igb PHY support library for copper and SFP/SerDes related PHY access. It covers MDIC and I2C register transports, PHY ID discovery, copper link setup, autonegotiation advertisement, forced speed/duplex, low power link-up, downshift and polarity reporting, link polling, cable length estimation, PHY software/hardware reset, Marvell PHY init scripts, and copper PHY power control.

## Important APIs, Types, and Functions
Core exported APIs include `igb_get_phy_id`, `igb_read_phy_reg_mdic`, `igb_write_phy_reg_mdic`, `igb_read_phy_reg_i2c`, `igb_write_phy_reg_i2c`, `igb_read_sfp_data_byte`, `igb_read_phy_reg_igp`, `igb_write_phy_reg_igp`, `igb_copper_link_setup_82580`, `igb_copper_link_setup_m88`, `igb_copper_link_setup_m88_gen2`, `igb_copper_link_setup_igp`, `igb_setup_copper_link`, `igb_phy_force_speed_duplex_igp`, `igb_phy_force_speed_duplex_m88`, `igb_set_d3_lplu_state`, `igb_check_downshift`, `igb_check_polarity_m88`, `igb_phy_has_link`, cable length getters, PHY info getters, reset helpers, Marvell initialization helpers, and copper power up/down helpers. Important internal functions include `igb_phy_setup_autoneg`, `igb_copper_link_autoneg`, `igb_phy_force_speed_duplex_setup`, `igb_wait_autoneg`, `igb_check_polarity_igp`, `igb_check_polarity_82580`, and `igb_set_master_slave_mode`.

## Control Flow
Register access goes through the operation table in `hw->phy.ops`. Raw MDIC reads/writes program `E1000_MDIC`, poll `E1000_MDIC_READY`, and fail on timeout or `E1000_MDIC_ERROR`. I2C reads/writes program `E1000_I2CCMD` and byte-swap 16-bit data. IGP multi-page access acquires the PHY semaphore, writes the page-select register when needed, performs MDIC access, and releases.

Copper setup is PHY-family specific. The 82580 path optionally resets, enables CRS-on-TX and downshift, then configures MDI/MDIX. The M88 paths configure auto crossover, polarity correction, downshift, master/slave policy, and reset the PHY to commit changes. The IGP path resets, waits for NVM-driven configuration, disables LPLU for active driver operation, configures MDI/MDIX, and manages SmartSpeed/master-slave settings. `igb_setup_copper_link` then either runs autonegotiation or forced speed/duplex and polls link before collision distance and flow-control setup.

## State and Persistence
The file updates volatile driver state in `hw->phy`, including `id`, `revision`, `original_ms_type`, `speed_downgraded`, `cable_polarity`, `is_mdix`, cable-length fields, and receiver status. It also writes persistent-in-effect hardware state: PHY advertisement registers, master/slave control, power management bits, page-select registers, MAC `E1000_CTRL` speed/duplex bits, and PHY reset bits. Most changes last until reset or power cycle, while NVM-driven defaults may be reloaded by hardware after reset.

## Dependencies and Integration Points
It depends on `e1000_mac.h`, `e1000_phy.h`, register macros, PHY constants, `igb_config_collision_dist`, `igb_config_fc_after_link_up`, `igb_force_mac_fc`, and MAC-specific callbacks such as `get_cfg_done`. Ettool link setting changes, diagnostics loopback, probe initialization, watchdog link checks, and power management all depend on these functions.

## Risks
Risks include PHY page-select restoration failures, semaphore leaks, long hardware polling delays, invalid forced speed/duplex combinations, device-specific register writes applied to the wrong PHY ID, and link instability from master/slave or SmartSpeed changes. Cable-length algorithms are approximate and depend on link being up at 1000 Mbps. Some paths intentionally ignore reset-block errors by returning success when management firmware blocks reset, which avoids disruption but can hide inability to reconfigure hardware.

## Test Signals
Good signals include successful link up across autonegotiated and forced modes, correct MDI/MDIX reporting in ethtool, stable flow control after negotiation, cable length and polarity output only when link supports it, no MDIC/I2C timeout debug logs, successful loopback diagnostics, and suspend/resume or interface down/up preserving expected copper PHY power behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/igb/e1000_phy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/igb/e1000_phy.h -->
# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/igb/e1000_phy.h

## Purpose
`e1000_phy.h` is the public PHY interface and constant map for the igb hardware layer. It declares generic PHY control/diagnostic functions and defines register offsets, bit masks, enums, and SFP flag layout used by `e1000_phy.c`, MAC-specific setup code, ethtool module EEPROM access, and link management.

## Important APIs, Types, and Functions
The header defines `enum e1000_ms_type` for master/slave policy and `enum e1000_smart_speed` for SmartSpeed control. It exports all major PHY helpers: reset-block checks, copper setup functions for IGP/M88/82580 families, forced speed/duplex functions, cable length getters, PHY ID/info getters, reset helpers, IGP paged accessors, MDIC and I2C accessors, SFP byte reads, power controls, Marvell initialization scripts, and polarity checks. It also defines `struct e1000_sfp_flags`, a bitfield representation of 1 Gb and lower Ethernet compatibility flags from SFP EEPROM data.

## Control Flow
There is no runtime control flow in the header. Compile-time structure comes from grouping constants by hardware family: IGP01/IGP02 registers, 82580 registers, power management bits, AGC and cable length constants, and SFP EEPROM offsets. Implementation code uses these definitions to select read/write offsets and masks based on `hw->phy.type`, `hw->phy.id`, and MAC type.

## State and Persistence
The header does not store state. Its constants address state in PHY registers: port status/control, power management, link health, page select, MDI/MDIX, polarity, downshift, diagnostics, and SFP module data. The declared functions mutate or observe `struct e1000_hw` and the physical device.

## Dependencies and Integration Points
The header depends on common kernel integer types and `struct e1000_hw` declarations from included driver headers. It is included by `e1000_phy.c` and consumers that need direct helper prototypes. SFP constants integrate with `igb_ethtool.c` module info/eeprom paths; MDI/MDIX and power constants integrate with link setup and power management.

## Risks
Incorrect masks or offsets can cause writes to unrelated PHY registers. The header exposes family-specific constants with similar names, so implementation must avoid mixing IGP, M88, and 82580 definitions. `struct e1000_sfp_flags` uses C bitfield layout for byte interpretation, which is convenient but should be treated carefully when portability or exact wire layout is questioned.

## Test Signals
Build coverage should catch missing prototypes and renamed constants. Runtime signals include correct link setup on all supported PHY families, valid SFP module data reads, correct ethtool MDI/MDIX and EEE behavior, and diagnostics that exercise cable length, polarity, and loopback paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/igb/e1000_phy.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/igb/e1000_regs.h -->
# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/igb/e1000_regs.h

## Purpose
`e1000_regs.h` is the central MMIO register map for the igb family. It defines offsets for control/status, NVM, PHY MDIC/I2C, flow control, interrupts, TX/RX queue registers, statistics, filtering, wakeup, virtualization, RSS, PTP time sync, DMA coalescing, EEE, thermal sensors, i210 flash/iNVM, and helper macros for safe register reads/writes.

## Important APIs, Types, and Functions
Most content is `#define` constants. Important macro families include scalar register offsets such as `E1000_CTRL`, `E1000_STATUS`, `E1000_EECD`, `E1000_MDIC`, `E1000_RCTL`, `E1000_TCTL`, `E1000_MANC`, and `E1000_SW_FW_SYNC`; indexed register macros such as `E1000_RDBAL(_n)`, `E1000_TDBAL(_n)`, `E1000_EITR(_n)`, `E1000_RETA(_i)`, and `E1000_ETQF(_n)`; and access helpers `wr32`, `rd32`, `wrfl`, `array_wr32`, and `array_rd32`. It declares `struct e1000_hw` and `u32 igb_rd32(struct e1000_hw *hw, u32 reg)`.

## Control Flow
The only executable behavior is in the access macros. `wr32` reads `hw->hw_addr` with `READ_ONCE`, checks `E1000_REMOVED`, and writes with `writel` when the BAR is still mapped. `rd32` delegates to `igb_rd32`. `wrfl` forces a posted-write flush by reading `E1000_STATUS`. Indexed queue macros compute different register strides for queue numbers below and above four, matching hardware layout differences.

## State and Persistence
This header names hardware state rather than storing driver state. Many registers are read-clear counters or interrupt causes, some are write-one-clear or write-only, and many queue/control registers persist until reset. Because the macros are used across the driver, changing a register offset affects data path setup, diagnostics, ethtool dumps, filters, PTP, and power management.

## Dependencies and Integration Points
Every file in this work item indirectly relies on this map. `e1000_nvm.c` uses `E1000_EECD`, `E1000_EERD`, `E1000_EEWR`, and RAL/RAH access. `e1000_phy.c` uses `E1000_MDIC`, `E1000_I2CCMD`, `E1000_CTRL`, and status/control registers. `igb_ethtool.c` uses a broad set for register dumps, tests, RSS, EEE, filters, and loopback. `igb_hwmon.c` relies on thermal sensor register definitions through MAC callbacks.

## Risks
The main risk is semantic, not algorithmic: wrong offsets, duplicate definitions, or using a register with read-clear side effects can break runtime behavior. The ethtool register dump deliberately reads aliases like EICS/ICS to avoid clearing causes, showing that access semantics matter. Queue index macros must stay aligned with hardware generation differences. `wr32` silently skips writes after device removal, so callers must be robust to hardware disappearing.

## Test Signals
Signals include successful driver probe and reset, correct ethtool register dumps, passing register self-tests, stable queue operation beyond four queues, working RSS/filter/PTP/EEE paths, and absence of MMIO faults during hot unplug or device removal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/igb/e1000_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/igb/igb.h -->
# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/igb/igb.h

## Purpose
`igb.h` is the main private header for the Linux Intel igb driver. It centralizes driver constants, queue/ring data structures, adapter state, feature flags, inline helpers, and cross-file prototypes for the netdev data path, XDP/AF_XDP, PTP, ethtool, hwmon, filters, SR-IOV VF state, and hardware setup.

## Important APIs, Types, and Functions
Major types include `struct vf_data_storage`, `struct vf_mac_filter`, `struct igb_tx_buffer`, `struct igb_rx_buffer`, `struct igb_tx_queue_stats`, `struct igb_rx_queue_stats`, `struct igb_ring_container`, `struct igb_ring`, `struct igb_q_vector`, `struct hwmon_attr`, `struct hwmon_buff`, `struct igb_nfc_input`, `struct igb_nfc_filter`, `struct igb_mac_addr`, and `struct igb_adapter`. Important enums and flags include `enum igb_tx_flags`, `enum igb_tx_buf_type`, `enum e1000_ring_flags_t`, `enum igb_filter_match_flags`, `enum e1000_state_t`, adapter feature flags like `IGB_FLAG_HAS_MSIX`, `IGB_FLAG_EEE`, and `IGB_FLAG_RX_LEGACY`, plus PTP flags.

Inline helpers include RX buffer sizing and page order selection, descriptor status testing, descriptor unused calculation, PHY operation wrappers, XDP tail update, CPU-to-XDP TX ring mapping, and XDP enabled checks. The header also declares the major cross-file driver entry points such as `igb_open`, `igb_close`, `igb_up`, `igb_down`, `igb_reset`, queue resource setup/free/configure, stats update, ethtool ops setup, PTP hooks, hwmon init/exit, filter add/delete, and AF_XDP helpers.

## Control Flow
Most control flow is in static inline helpers. RX buffer sizing chooses 3K, build_skb, or 2K buffers based on page size and ring flags. `igb_desc_unused` computes ring free descriptors with wraparound. PHY wrappers no-op when the selected operation is absent, which simplifies callers but can hide missing initialization. `igb_xdp_ring_update_tail` asserts the TX queue lock, executes a write memory barrier, and writes the hardware tail pointer.

## State and Persistence
`struct igb_adapter` is the persistent per-device software state for the driver lifetime. It tracks netdev/pci handles, queue arrays, NAPI vectors, interrupt masks, timers, work items, rings, stats, hardware state (`struct e1000_hw`), VF data, RSS state, PTP clocks and timestamp state, firmware string, optional hwmon state, I2C adapter/client, EEE advertisement, NFC filter list, MAC filter table, and locks. Ring structures persist DMA descriptors, buffer info, queue indices, CBS/FQTSS settings, XDP program/pool links, and stats.

## Dependencies and Integration Points
The header includes `e1000_mac.h`, `e1000_82575.h`, Linux netdev/PCI/I2C/MDIO/PTP/XDP headers, and is included by most igb source files. It ties the low-level hardware layer to Linux subsystems: NAPI, ethtool, PTP clock, hwmon, I2C, SR-IOV, XDP, AF_XDP, VLAN, and traffic control offloads.

## Risks
Because this header defines shared state layout, changes have wide blast radius. Ring and adapter fields are touched from interrupt, NAPI, workqueue, ethtool, and netdev control paths, so locking and cacheline assumptions matter. Inline wrappers returning success when ops are missing can mask bugs. Queue count constants and fixed arrays must remain consistent with hardware limits and allocation code.

## Test Signals
Signals include clean builds across configs with and without `CONFIG_IGB_HWMON`, successful probe/open/close/reset, multiqueue TX/RX traffic, XDP and AF_XDP operation, ethtool stats and filter operations, PTP timestamping, SR-IOV VF behavior, and lockdep/KASAN/KCSAN runs around reset and queue reconfiguration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/igb/igb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/igb/igb_ethtool.c -->
# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/igb/igb_ethtool.c

## Purpose
`igb_ethtool.c` implements the driver's ethtool surface. It exposes link settings, pause parameters, message level, register dumps, EEPROM reads/writes, driver info, ring sizing, offline/online self tests, wake-on-LAN, LED identify, interrupt coalescing, statistics strings/values, timestamp capabilities, RX flow classification, RSS hash fields and indirection, EEE settings, SFP module EEPROM reads, channel counts, private flags, and installs the `struct ethtool_ops`.

## Important APIs, Types, and Functions
The file defines stat descriptor tables (`struct igb_stats`, `igb_gstrings_stats`, `igb_gstrings_net_stats`), diagnostic labels, private flags, register-test tables per MAC generation (`reg_test_i210`, `reg_test_i350`, `reg_test_82580`, `reg_test_82576`, `reg_test_82575`), and the exported `igb_write_rss_indir_tbl`, `igb_add_filter`, `igb_erase_filter`, and `igb_set_ethtool_ops`. Important ethtool callbacks include `igb_get_link_ksettings`, `igb_set_link_ksettings`, `igb_get_regs`, `igb_get_eeprom`, `igb_set_eeprom`, `igb_set_ringparam`, `igb_diag_test`, `igb_get_ethtool_stats`, `igb_get_ts_info`, RX NFC get/set helpers, EEE get/set, module info/eeprom helpers, RSS get/set, channel get/set, and private flag get/set.

## Control Flow
Configuration mutators generally serialize against resets using `__IGB_RESETTING` or by calling `igb_reinit_locked`. Link setting changes validate management reset blocks, MDI/MDIX restrictions, autoneg vs forced speed, then restart the running interface or reset a stopped device. Pause changes either re-negotiate via reset or directly force MAC flow control and refresh RX SRRCTL. Ring parameter changes allocate temporary ring structures while the interface is down, then swap resources to preserve MSI-X ISR ring pointers.

The self-test path sets `__IGB_TESTING`. Offline tests save link settings, power up link, run link, register, EEPROM, interrupt, and loopback tests across resets, restore settings, and reopen the interface if needed. Online tests only perform the link test and mark invasive tests as passed. RX NFC insertion parses limited `ETHER_FLOW` masks, programs scarce hardware filters, adds the software rule under `nfc_lock`, and rolls back hardware on list update failure.

## State and Persistence
The file reads and mutates many `struct igb_adapter` fields: ring counts, queue counts, stats, `msg_enable`, `wol`, `rx_itr_setting`, `tx_itr_setting`, flags, RSS indirection table, NFC filter list/count, EEE advertisement, link settings, test rings, and LED state. It can also write persistent EEPROM contents via `igb_set_eeprom`, updating checksum and firmware version afterward. Hardware filter, RSS, EEE, interrupt, register-test, and loopback changes write MMIO registers and PHY registers.

## Dependencies and Integration Points
It integrates Linux ethtool APIs with igb internals from `igb.h`, low-level NVM ops, PHY helpers, MAC setup functions, PTP support, PCI/runtime PM, I2C SFP access, netdev queue APIs, DMA mapping, and XDP-aware rings. It is the user-facing control plane for many capabilities implemented elsewhere.

## Risks
The highest risks are invasive diagnostics and live reconfiguration. Register tests intentionally overwrite hardware registers and must be run offline. Loopback allocates test rings, forces MAC/PHY loopback, disables some PHY receiver behavior, and must clean up reliably. EEPROM writes can corrupt device configuration if magic, alignment, checksum, or flash presence checks are wrong. RX NFC uses both software list state and hardware table state; partial failure requires careful rollback. Enabling UDP RSS warns about fragmented packet reordering. Channel/ring changes can race with traffic if reset serialization is broken.

## Test Signals
Signals include correct `ethtool -k/-i/-S/-g/-c/-l/-x/-n` output, successful link setting changes with expected link renegotiation, register dump length/version stability, EEPROM read/write and checksum validation, online/offline self-test results, WOL persistence through suspend, LED identify operation, RSS distribution matching indirection table, filter add/delete steering traffic to requested queues, EEE negotiation reporting, SFP EEPROM reads, and no leaks or crashes when ring/channel changes fail allocation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/igb/igb_ethtool.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/igb/igb_hwmon.c -->
# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/igb/igb_hwmon.c

## Purpose
`igb_hwmon.c` provides optional `CONFIG_IGB_HWMON` integration for exposing igb thermal sensor data through the Linux hwmon sysfs interface. It creates per-sensor attributes for label, temperature input, caution threshold, and max/critical threshold, creates an I2C client for the i350 thermal sensor endpoint, and registers a hwmon device with attribute groups.

## Important APIs, Types, and Functions
The file defines `i350_sensor_info` with I2C board info for `"i350bb"`. Sysfs show callbacks are `igb_hwmon_show_location`, `igb_hwmon_show_temp`, `igb_hwmon_show_cautionthresh`, and `igb_hwmon_show_maxopthresh`. `igb_add_hwmon_attr` constructs one `struct hwmon_attr` entry and appends it to the adapter's `struct hwmon_buff`. The externally used entry points are `igb_sysfs_init` and `igb_sysfs_exit`; `igb_sysfs_del_adapter` is currently empty because devm-managed resources handle teardown.

## Control Flow
`igb_sysfs_init` first checks whether `adapter->hw.mac.ops.init_thermal_sensor_thresh` exists. It calls that operation, exits if no sensors are present or initialization fails, allocates `struct hwmon_buff` with `devm_kzalloc`, and loops over `E1000_MAX_SENSORS`. For each sensor with nonzero location, it adds caution, label, input, and max attributes. It then creates an I2C client on `adapter->i2c_adap`, attaches the attribute group, and registers the hwmon device through `devm_hwmon_device_register_with_groups`. Attribute reads dereference the stored sensor pointer; temperature reads refresh sensor data by calling `get_thermal_sensor_data` before returning millidegrees.

## State and Persistence
State is stored in `adapter->igb_hwmon_buff`, `adapter->i2c_client`, and the MAC thermal sensor data under `adapter->hw.mac.thermal_sensor_data`. Sysfs attributes are read-only (`0444`) and do not persist configuration. Sensor thresholds come from MAC initialization and are reported in millidegrees Celsius. Resource lifetime is device-managed, so teardown is mostly implicit.

## Dependencies and Integration Points
This code depends on `igb.h` hwmon structs, `e1000_82575.h` thermal sensor definitions, MAC operations for initializing thresholds and fetching live sensor data, Linux I2C APIs, sysfs attribute APIs, and hwmon registration. It is called from main adapter setup/teardown when `CONFIG_IGB_HWMON` is enabled.

## Risks
Risks include stale or missing MAC thermal callbacks, incorrect sensor count assumptions, failure partway through attribute construction, and the empty explicit deletion helper relying on devm lifetime. Attribute names use a 12-byte buffer and must continue to fit strings like `tempN_input` for the supported sensor count. I2C client creation failure prevents hwmon registration even if internal thermal registers are readable.

## Test Signals
Signals include successful probe with hwmon enabled, `/sys/class/hwmon` entries named after the i350 client, correct `tempN_label`, `tempN_input`, `tempN_max`, and `tempN_crit` files for present sensors only, temperature values changing after `get_thermal_sensor_data`, clean removal/unbind without sysfs warnings, and successful builds with `CONFIG_IGB_HWMON` both enabled and disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/igb/igb_hwmon.c -->
