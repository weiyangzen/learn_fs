# Research Group: subset-b-004817

This grouped report covers Intel wireless legacy and iwlwifi configuration sources under `sources/distributed-fs/ceph-client/drivers/net/wireless/intel/`. Each file section is bounded for deterministic reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlegacy/common.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlegacy/common.h

## Purpose
`common.h` is the central iwlegacy driver contract shared by 3945/4965-era Intel wireless code. It defines the main driver state (`struct il_priv`), hardware and firmware configuration data, DMA queue layouts, EEPROM/regulatory structures, station/rate-scaling state, mac80211 callback declarations, operation hooks, register access helpers, debug categories, and key constants used throughout the legacy driver.

## Important APIs, Types, and Constants
- Logging and debug macros: `IL_ERR`, `IL_WARN`, `IL_INFO`, `IL_DBG`, `D_*` category wrappers, `il_print_hex_dump`, `il_get_debug_level`.
- RX/TX queue primitives: `struct il_rx_buf`, `struct il_queue`, `struct il_tx_queue`, `struct il_rx_queue`, `il_queue_used`, `il_get_cmd_idx`, queue wrap helpers, stop/wake helpers.
- Firmware command abstractions: `struct il_cmd_meta`, `struct il_device_cmd`, `struct il_device_cmd_huge`, `struct il_host_cmd`, command flags such as `CMD_ASYNC`, `CMD_WANT_SKB`, and `CMD_SIZE_HUGE`.
- EEPROM/regulatory definitions: `struct il_eeprom_channel`, calibration structures, channel-band offsets, SKU flags, and helpers such as `il_eeprom_query16`, `il_init_channel_map`, `il_get_channel_info`.
- Driver state: `struct il_priv` aggregates PCI/mac80211 objects, firmware images, RXON state, scan state, calibration data, station table, queues, work items, timers, debugfs state, LEDs, status bits, and per-family private substructures.
- Hardware abstraction: `struct il_ops` contains callbacks for TX queue handling, uCode loading, EEPROM semaphore access, RXON commit, scanning, station handling, power, LED commands, and hardware dumps.
- Configuration data: `struct il_hw_params`, `struct il_cfg`, `struct il_mod_params`, `struct il_power_mgr`.
- Rate and aggregation state: `struct il_ht_agg`, `struct il_tid_data`, `struct il_lq_sta`, `struct il_scale_tbl_info`, rate masks, PLCP/IEEE mapping constants, table type helpers, antenna masks.
- Register helpers: `_il_rd`, `_il_wr`, `il_rd`, `il_wr`, `_il_rd_prph`, `_il_wr_prph`, `il_set_bits_prph`, `il_clear_bits_prph`, `il_read_targ_mem`, `il_write_targ_mem`.

## Control Flow and Integration
The header does not implement the full driver, but it defines the control surfaces used by the implementation. Probe/configuration code binds a PCI ID to an `il_cfg`, fills `il_priv`, loads firmware through `fw_desc` DMA buffers, initializes RX/TX queues, then transitions status bits through init, alive, ready, scanning, RF kill, and error states. mac80211 callbacks declared here (`il_mac_config`, interface add/remove/change, scan, flush, BSS changes) drive RXON staging/commit, station table updates, queue flow control, and rate setup.

Hardware access is split deliberately. Plain CSR access uses `_il_rd`/`_il_wr` against PCI MMIO. Internal device resources require `il_rd`/`il_wr` or PRPH helpers, which take `reg_lock`, grab NIC access with `CSR_GP_CNTRL_REG_FLAG_MAC_ACCESS_REQ`, perform the access, and release NIC access. This contract is shared with `csr.h` and `prph.h`.

## State and Persistence Behavior
`struct il_priv` is the persistent in-memory state for a device lifetime. It stores firmware images and backup data for reload/recovery, EEPROM contents, regulatory channel tables, station keys and link-quality commands, queue descriptors and DMA memory, calibration accumulators, scan requests, workqueue/timer state, status bits, debugfs settings, traffic/interrupt counters, and LED state. Firmware images and queue memory are DMA coherent allocations and must be freed through matching helpers. EEPROM data is cached in `il->eeprom`; station and key state must be restored after firmware restart.

## Dependencies and Integration Points
The file depends on kernel PCI, DMA, workqueue/timer, LED, waitqueue, and MMIO APIs; on mac80211/cfg80211 types; and on local `commands.h`, `csr.h`, and `prph.h`. It exports contracts used by hw-specific 3945/4965 files, common RX/TX/scan/power/statistics code, debugfs, and rate control modules.

## Risks and Edge Cases
- Queue sizes are power-of-two assumptions; incorrect `n_bd`/`n_win` breaks wrap arithmetic.
- Register access helpers must match CSR versus internal/PRPH address space; using raw MMIO for powered-down internal resources can race sleep states.
- `il_priv` has many lock domains (`lock`, `hcmd_lock`, `reg_lock`, `sta_lock`, `mutex`); ordering mistakes can deadlock or expose stale station/queue state.
- Firmware API version and size limits are enforced through config fields; mismatches risk failed loads or uCode assertions.
- Debug and queue stop wrappers intentionally poison direct `ieee80211_stop_queue`/`wake_queue` use after local helpers, so new code must use refcounted stop/wake paths.

## Test Signals
Useful validation includes kernel build coverage for `CONFIG_IWL3945`, `CONFIG_IWL4965`, debug/debugfs variants, suspend/resume, firmware restart, scan cancel, RF kill/CT kill transitions, TX aggregation setup/teardown, station add/remove, EEPROM/channel-map parsing, and lockdep/KASAN runs around queue reclaim and debugfs reads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlegacy/common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlegacy/csr.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlegacy/csr.h

## Purpose
`csr.h` defines iwlegacy host-visible Control and Status Register (CSR) and Host Bus (HBUS) offsets and bit masks. It documents which registers are always PCI MMIO accessible and which HBUS registers are indirect access windows into internal memory or peripherals.

## Important APIs, Types, and Constants
- CSR offsets: `CSR_HW_IF_CONFIG_REG`, `CSR_INT`, `CSR_INT_MASK`, `CSR_FH_INT_STATUS`, `CSR_RESET`, `CSR_GP_CNTRL`, `CSR_HW_REV`, `CSR_EEPROM_REG`, `CSR_UCODE_DRV_GP*`, `CSR_LED_REG`, `CSR_DRAM_INT_TBL_REG`.
- Interrupt masks: `CSR_INT_BIT_FH_RX`, `CSR_INT_BIT_HW_ERR`, `CSR_INT_BIT_FH_TX`, `CSR_INT_BIT_SW_ERR`, `CSR_INT_BIT_RF_KILL`, `CSR_INT_BIT_WAKEUP`, `CSR_INT_BIT_ALIVE`, `CSR_INI_SET_MASK`, FH RX/TX masks for 3945 and 4965.
- Power and access bits: `CSR_GP_CNTRL_REG_FLAG_MAC_ACCESS_REQ`, `MAC_CLOCK_READY`, `GOING_TO_SLEEP`, `INIT_DONE`, `HW_RF_KILL_SW`.
- EEPROM bits: `CSR_EEPROM_REG_READ_VALID_MSK`, command/address/data masks, EEPROM signature masks.
- uCode mailbox bits: `CSR_UCODE_DRV_GP1_BIT_MAC_SLEEP`, `CSR_UCODE_SW_BIT_RFKILL`, `CSR_UCODE_DRV_GP1_BIT_CMD_BLOCKED`, CT-kill exit.
- HBUS windows: `HBUS_TARG_MEM_*` for SRAM, `HBUS_TARG_PRPH_*` for peripheral registers, `HBUS_TARG_WRPTR` for TX queue write pointer updates.

## Control Flow and Integration
CSR registers are accessed with raw `_il_rd()` and `_il_wr()` because the MAC does not need to be awake. Internal memory and PRPH windows under HBUS must be accessed through the higher-level access path after grabbing NIC access, because the target resources may be powered down. Interrupt handlers read/ack `CSR_INT` and `CSR_FH_INT_STATUS`, enable masks through `CSR_INT_MASK`, and use RF kill/CT kill bits to steer power/error handling.

## State and Persistence Behavior
The file is declarative; no state is stored here. The registers it describes expose persistent hardware state such as interrupt latch bits, RF kill state, EEPROM read data, firmware-driver mailbox state, reset state, and target memory access pointers. Many bits are write-one-to-clear or set/clear side-effect registers.

## Dependencies and Integration Points
`common.h` includes this header for inline register helpers and status macros. The implementation uses these constants in interrupt, EEPROM, APM, firmware load, RF kill, LED, and queue code. It pairs with `prph.h`, whose internal registers are accessed via the HBUS offsets defined here.

## Risks and Edge Cases
- CSR and HBUS have different access rules; mixing `_il_*` and `il_*` families can fail during low-power states.
- Interrupt bits are acknowledged by writing one, so careless writes can drop pending events.
- EEPROM reads require the device to be awake and initialized despite the register being in CSR space.
- MAC sleep, command-blocked, and RF kill mailbox bits are shared with firmware; ordering mistakes can strand queues or prevent recovery.

## Test Signals
Exercise interrupt enable/disable paths, EEPROM read polling, RF kill toggles, software reset, firmware alive transition, target SRAM/PRPH reads, and suspend/resume while lockdep or tracing verifies register access sequencing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlegacy/csr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlegacy/debug.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlegacy/debug.c

## Purpose
`debug.c` implements iwlegacy debugfs support and traffic accounting when `CONFIG_IWLEGACY_DEBUGFS` is enabled. It exposes runtime diagnostic files for TX/RX statistics, EEPROM/SRAM dumps, station and queue state, interrupt counters, firmware stats, calibration state, power-save status, force reset, watchdog timeout, missed beacon threshold, and RF calibration toggles.

## Important APIs, Types, and Functions
- `il_update_stats()` classifies TX/RX frame control values into management, control, and data counters and is exported.
- `il_dbgfs_register()` creates the debugfs directory tree and files under the wiphy debugfs directory.
- `il_dbgfs_unregister()` recursively removes the debugfs tree.
- Read handlers include `*_tx_stats_read`, `*_rx_stats_read`, `*_sram_read`, `*_nvm_read`, `*_stations_read`, `*_channels_read`, `*_status_read`, `*_interrupt_read`, `*_qos_read`, `*_tx_queue_read`, `*_rx_queue_read`, `*_sensitivity_read`, `*_chain_noise_read`, and `*_power_save_status_read`.
- Write handlers include clear traffic stats, interrupt stats reset, SRAM offset/length selection, disable HT40, clear firmware stats, missed beacon threshold, force reset, and watchdog timeout.
- `DEBUGFS_*` macros generate file operations and add files/booleans.

## Control Flow and Integration
The register function creates `data`, `rf`, and `debug` subdirectories. Read paths allocate a temporary buffer, format the current `il_priv` fields with `scnprintf`, call `simple_read_from_buffer`, and free the buffer. Write paths copy bounded user input, parse an integer or offset/length tuple, then mutate driver state or call driver operations. Firmware statistic reads dispatch through `il->debugfs_ops` for hardware-specific formatting.

## State and Persistence Behavior
The file reads and mutates live `il_priv` state: packet counters, ISR counters, EEPROM bytes, SRAM dump selection (`dbgfs_sram_offset`, `dbgfs_sram_len`), station aggregation state, channel tables, queue pointers, calibration structures, power state bits, missed beacon threshold, watchdog timeout, and force reset counters. Debugfs state lasts until unregister or device removal. Traffic and ISR counters can be reset through debugfs.

## Dependencies and Integration Points
It depends on `common.h`, mac80211 frame helpers, debugfs, copy-from-user, simple read helpers, and hardware-specific debug operations. It uses common functions such as `il_read_targ_mem`, `il_eeprom_query16`, `il_get_hw_mode`, `il_clear_isr_stats`, `il_send_stats_request`, `il_force_reset`, and `il_setup_watchdog`.

## Risks and Edge Cases
- Many reads traverse live state with minimal locking, so output is diagnostic and can race with device reset/removal.
- `sram_read` can allocate large buffers based on user-selected length and reads target memory; invalid ranges can be expensive or fail depending on device state.
- `disable_ht40` is rejected while associated, but other knobs such as force reset and watchdog updates are intentionally disruptive.
- Several buffer sizes are hand-estimated; future additions must keep `scnprintf` bounds and allocation calculations correct.

## Test Signals
Build with and without `CONFIG_IWLEGACY_DEBUGFS`, mount debugfs, read all files while associated and unassociated, exercise clear/reset writes, validate SRAM/EEPROM dump bounds, check force-reset behavior, run KASAN/lockdep while removing the device during debugfs access, and verify traffic counters with known management/control/data frames.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlegacy/debug.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlegacy/iwl-spectrum.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlegacy/iwl-spectrum.h

## Purpose
`iwl-spectrum.h` defines small IEEE 802.11 spectrum measurement report and request structures used by iwlegacy for measurement notifications and reports.

## Important APIs, Types, and Constants
- Basic report map bits: `IEEE80211_BASIC_MAP_BSS`, `OFDM`, `UNIDENTIFIED`, `RADAR`, and `UNMEASURED`.
- Measurement mode bits: `IEEE80211_MEASUREMENT_ENABLE`, `REQUEST`, and `REPORT`.
- Report type constants: `IEEE80211_REPORT_BASIC`, `CCA`, and `RPI`.
- Packed wire structures: `struct ieee80211_basic_report` and `struct ieee80211_measurement_params`.

## Control Flow and Integration
The header has no executable logic. The packed structures are used by code that parses or builds firmware/mac80211 spectrum measurement data. `struct il_priv` caches a spectrum measurement notification and status in `common.h`; handlers declared there consume these formats.

## State and Persistence Behavior
No state is stored in the header. Instances of the packed structures represent transient measurement request/report payloads with little-endian time and duration fields.

## Dependencies and Integration Points
It depends on Linux integer/endian types included before use. It integrates with iwlegacy command/notification handlers and 802.11h/spectrum-management behavior.

## Risks and Edge Cases
Because the structures are packed wire formats, alignment and endian handling matter. Reserved bits are not masked by helper functions in this header, so callers must validate mode and map fields themselves.

## Test Signals
Validation should cover measurement notification parsing, report generation, endian conversion on big-endian builds, and radar/unmeasured flag propagation into any mac80211-visible report path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlegacy/iwl-spectrum.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlegacy/prph.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlegacy/prph.h

## Purpose
`prph.h` defines iwlegacy internal peripheral register addresses and bit fields accessed indirectly through HBUS PRPH registers. It documents power management, bootstrap/uCode loading, data save/restore, and 4965 transmit scheduler register layout.

## Important APIs, Types, and Constants
- APMG power management registers and bits: `APMG_CLK_*`, `APMG_PS_CTRL_*`, `APMG_RFKILL_REG`, voltage and PCI L1 control masks.
- Bootstrap State Machine registers: `BSM_WR_CTRL_REG`, `BSM_DRAM_*`, `BSM_SRAM_LOWER_BOUND`, `BSM_SRAM_SIZE`, `BSM_DRAM_INST_LOAD`.
- 3945 scheduler registers under `ALM_SCD_*`.
- 4965 scheduler constants: `SCD_WIN_SIZE`, `SCD_FRAME_LIMIT`, `IL49_SCD_*` register offsets, queue write/read pointers, queue chain selection, interrupt mask, queue status bits, SRAM context offsets, translate table offsets.
- Queue and aggregation mapping helpers: `IL49_SCD_QUEUE_STATUS_BITS(x)`, `IL49_SCD_CONTEXT_QUEUE_OFFSET(x)`, `IL49_SCD_TRANSLATE_TBL_OFFSET_QUEUE(x)`.

## Control Flow and Integration
The long comments specify the firmware load sequence: write bootstrap instructions into BSM SRAM, program host DRAM pointers for init uCode, configure and start the BSM copy into instruction SRAM, enable future boot loads, release reset, wait for init alive, repoint DRAM registers to runtime images, then wait for runtime alive. During power-save, firmware can save data SRAM to host DRAM and BSM reloads runtime code/data on wake. Scheduler setup occurs after alive, when the driver can initialize queue context, byte count tables, queue modes, FIFO mapping, and RA/TID translation.

## State and Persistence Behavior
The header is declarative, but the described registers persist hardware state: clocks, power source, bootstrap memory, DMA image pointers, scheduler queue contexts, TX status bitmap, and RA/TID mappings. BSM SRAM can remain powered across certain low-power sleeps, while regular runtime data SRAM may be saved to host DRAM.

## Dependencies and Integration Points
`common.h` includes this file for PRPH helper users. Firmware loading, APM, scheduler initialization, aggregation setup, and internal SRAM access depend on these definitions. HBUS target PRPH and memory access offsets come from `csr.h`.

## Risks and Edge Cases
- Firmware load ordering is strict; programming instruction byte count is the trigger for runtime load.
- Saved runtime data in host DRAM can be modified firmware state, not a clean image; full reinitialization must use the original firmware data image.
- Scheduler ACK mode requires byte count tables and matching RA/TID queue mapping; wrong mode/fifo bits can break commands or aggregation.
- Internal register access requires NIC access and must not run while the MAC is asleep without wake sequencing.

## Test Signals
Use firmware boot/restart tests, suspend/resume power-save cycles, RF kill recovery, command queue bring-up after alive, aggregation start/stop, scheduler context dumps, and error injection around BSM load/poll timeouts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlegacy/prph.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/Kconfig

## Purpose
`Kconfig` defines build-time configuration for the modern Intel `iwlwifi` driver, operation modes, debug support, device tracing, KUnit tests, LED support, and the disabled-by-default MEI-over-WLAN companion module.

## Important APIs, Types, and Options
- `IWLWIFI`: main tristate driver, depending on PCI, I/O memory, CFG80211, and MEI compatibility.
- `IWLDVM`, `IWLMVM`, `IWLMLD`: firmware operation mode modules for DVM, MVM, and MLD-capable devices.
- `IWLWIFI_OPMODE_MODULAR`: internal boolean that becomes true when opmode modules or tests are modular.
- `IWLWIFI_KUNIT_TESTS`: optional KUnit tests.
- `IWLWIFI_LEDS`: LED class integration, selecting LED triggers and mac80211 LEDs when supported.
- `IWLWIFI_DEBUG`, `IWLWIFI_DEBUGFS`, `IWLWIFI_DEVICE_TRACING`: debug logging, debugfs state, and ftrace event tracing.
- `IWLMEI`: Intel Management Engine communication over WLAN, currently depending on `BROKEN`.

## Control Flow and Integration
Kconfig controls which objects the Makefile builds and whether runtime features are compiled in. Enabling `IWLWIFI` alone is insufficient for a useful driver unless at least one opmode (`IWLDVM`, `IWLMVM`, or `IWLMLD`) is enabled. Debug options add sysfs/debugfs/tracing surfaces used by the shared driver and opmodes.

## State and Persistence Behavior
There is no runtime state. The options persist in the kernel build configuration and determine the available module set and compiled feature surfaces.

## Dependencies and Integration Points
This file integrates with kernel kbuild, mac80211/cfg80211, PCI, firmware loader, LED class, event tracing, devcoredump, PTP clock optional support, KUnit, and MEI. The top-level `iwlwifi/Makefile` consumes these symbols.

## Risks and Edge Cases
- A build with `IWLWIFI=y/m` but all opmodes disabled yields a warning and no useful hardware support.
- `IWLMEI` is explicitly broken; enabling it on unsuitable platforms can affect Wi-Fi behavior.
- Debug/tracing options increase module size and runtime overhead.
- LED support depends on specific LED class combinations.

## Test Signals
Build matrix coverage should include built-in and modular `IWLWIFI`, each opmode, debugfs/debug/tracing enabled and disabled, KUnit all-tests mode, and configuration where opmodes are intentionally disabled to confirm the warning path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/Makefile

## Purpose
The top-level `iwlwifi/Makefile` composes the shared Intel wireless module and conditionally includes bus, firmware, configuration, opmode, debug, ACPI/EFI, MEI, MLD, and test objects according to Kconfig symbols.

## Important APIs, Types, and Build Targets
- Main target: `obj-$(CONFIG_IWLWIFI) += iwlwifi.o`.
- Shared objects: IO, driver core, debug, NVM utils/parse, PHY DB, transport, firmware debug/dump/regulatory/pnvm.
- PCI transport objects: context info, driver, utilities, Gen1/2 RX/TX/transport.
- Config tables: DVM-era combined MAC/RF configs for 1000/2000/5000/6000, MVM configs for 7000/8000/9000/22000/AX210/BZ/SC and RF files, MLD configs for BZ/SC/DR and RF files.
- Subdirectories: `dvm/`, `mvm/`, `mei/`, `mld/`, and `tests/`.
- Conditional additions: `iwl-devtrace.o`, ACPI/UEFI helpers, debugfs firmware helpers.

## Control Flow and Integration
Kbuild first builds the common `iwlwifi.o` module from shared objects and selected config table objects. Opmodes are built as subdirectory modules or built-ins based on `IWLDVM`, `IWLMVM`, and `IWLMLD`. `iwlwifi-objs += $(iwlwifi-m)` folds conditional object fragments into the common module.

## State and Persistence Behavior
No runtime state is stored here. The file determines the binary composition of the driver and which exported config structures are present for PCI ID matching and firmware selection.

## Dependencies and Integration Points
It consumes symbols from `Kconfig`, includes headers with `ccflags-y += -I$(src)`, suppresses override-init warnings for `pcie/drv.o`, and wires firmware, transport, config, and opmode subsystems together.

## Risks and Edge Cases
- Duplicate inclusion of shared config files across MVM and MLD must remain intentional and link-safe.
- Missing a new cfg object means PCI IDs may reference unavailable config symbols.
- Feature-specific objects must align with Kconfig dependencies, especially debugfs, ACPI, EFI, tracing, tests, and opmode modularity.

## Test Signals
Run kbuild matrix for all relevant `IWLWIFI`, `IWLDVM`, `IWLMVM`, `IWLMLD`, `IWLMEI`, `ACPI`, `EFI`, `DEBUGFS`, tracing, and KUnit combinations; check modpost for unresolved config symbols and duplicate definitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/cfg/1000.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/cfg/1000.c

## Purpose
`1000.c` defines DVM-era configuration data for Intel Centrino Wireless-N 1000 and 100 devices, including firmware names/API ranges, EEPROM parameters, base hardware parameters, MAC config, RF configs, HT support, antenna behavior, LED modes, and module firmware aliases.

## Important APIs, Types, and Data
- Firmware API ranges: 1000 supports API 1-5; 100 supports API 5 only.
- Firmware prefixes: `iwlwifi-1000` and `iwlwifi-100`.
- `iwl1000_base`: queues, TFD queue size, low 2K OTP EEPROM, PLL config, no shadow RAM, LED compensation, disabled watchdog, event log size, SCD chain extension workaround.
- `iwl1000_eeprom_params`: regulatory band offsets with no 5 GHz HT40 band.
- `iwl1000_mac_cfg`: `IWL_DEVICE_FAMILY_1000`.
- RF configs: `iwl1000_bgn_cfg`, `iwl1000_bg_cfg`, `iwl100_bgn_cfg`, `iwl100_bg_cfg`.
- Product names and `MODULE_FIRMWARE` declarations.

## Control Flow and Integration
PCI ID tables select the MAC/RF config objects. The driver combines `iwl1000_mac_cfg` with an RF config to choose firmware, validate NVM/calibration versions, size firmware images, set LED behavior, and advertise HT capabilities. BGN variants enable greenfield, RTS/CTS aggregation protection, and 2.4 GHz HT40.

## State and Persistence Behavior
The file defines immutable `const` configuration. Runtime state is created elsewhere from these tables; firmware files are requested using the configured prefixes and API limits.

## Dependencies and Integration Points
It depends on `iwl-config.h`, `iwl-agn-hw.h`, Linux module firmware macros, and stringification. The top-level Makefile includes this object for `CONFIG_IWLDVM`.

## Risks and Edge Cases
Firmware API min/max, EEPROM versions, and calibration versions must match the supported firmware/NVM images. The 100 variant has SISO diversity and RF-state LED behavior while 1000 uses blink mode, so sharing fields carelessly can regress hardware-specific behavior.

## Test Signals
Build DVM support, check module firmware aliases, probe matching 100/1000 hardware or simulated IDs, verify firmware selection, NVM validation, 2.4 GHz HT capability advertisement, LED mode, and watchdog behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/cfg/1000.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/cfg/2000.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/cfg/2000.c

## Purpose
`2000.c` defines DVM configuration tables for Intel 2000/2030 and 105/135 Wireless-N families, including firmware API ranges, EEPROM parameters, base families, MAC configs, RF configs, HT capabilities, LED behavior, and product names.

## Important APIs, Types, and Data
- Firmware API ranges: 2000, 2030, 105, and 135 use max 6 and min 5.
- Base params: `iwl2000_base` and `iwl2030_base`, differing mainly LED compensation and watchdog timeout.
- EEPROM params: enhanced TX power, 2.4/5 GHz regulatory bands with 6000-style 2.4 HT40 and no 5 GHz HT40 entry.
- MAC configs: `iwl2000_mac_cfg`, `iwl2030_mac_cfg`, `iwl105_mac_cfg`, `iwl135_mac_cfg`.
- RF configs: `iwl2000_2bgn_cfg`, `iwl2030_2bgn_cfg`, `iwl105_bgn_cfg`, `iwl135_bgn_cfg`.
- 105/135 configs enable `rx_with_siso_diversity`.

## Control Flow and Integration
The driver uses these tables after PCI matching to request firmware, configure DVM runtime limits, load EEPROM/NVM data, set HT capabilities, and expose product names. All RF configs in this file enable greenfield, RTS/CTS aggregation protection, and 2.4 GHz HT40.

## State and Persistence Behavior
Only immutable config is defined. Runtime persistence includes firmware/NVM loaded based on these values and driver state derived from the selected MAC/RF pair.

## Dependencies and Integration Points
It depends on `iwl-config.h`, `iwl-agn-hw.h`, and DVM command definitions for Bluetooth-related constants. The Makefile includes it under `CONFIG_IWLDVM`.

## Risks and Edge Cases
Enhanced TX power and EEPROM version requirements must match hardware images. 2030/135 use longer watchdog/LED compensation than 2000/105; wrong pairing can cause timeouts or user-visible LED changes. Since the file includes DVM command headers for BT, command API changes can affect build compatibility.

## Test Signals
Validate firmware aliases, DVM probe for each product class, EEPROM version rejection/acceptance, HT capability flags, SISO diversity behavior, watchdog timing, and Bluetooth coexistence code paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/cfg/2000.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/cfg/22000.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/cfg/22000.c

## Purpose
`22000.c` defines MAC/base configuration for the 22000/Qu/AX200 generation used by MVM, including firmware API 77, large queue counts, shared memory ranges, monitor registers, Gen2 transport properties, integrated CNVi latency variants, and AX200/AX201 product names.

## Important APIs, Types, and Data
- Firmware prefix/API: `iwlwifi-cc-a0`, API 77 only.
- `iwl_22000_base`: 512 queues, 256 max TFD queue size, shadow RAM, L1, checksum features, SMEM range, APMG unsupported, MAC address CSR offset, D3 debug region, monitor SMEM/DRAM register definitions, GP2 register address, and API range.
- MAC configs: `iwl_qu_mac_cfg`, `iwl_qu_medium_latency_mac_cfg`, `iwl_qu_long_latency_mac_cfg`, `iwl_ax200_mac_cfg`.
- CNVi latency and LTR delay variants: 500, 1820, and 12000 xtal latency with matching delay constants.
- Product names for Killer AX1650 and AX200/AX201 variants.

## Control Flow and Integration
PCI matching selects one of the MAC configs and an RF config from another file. The transport and firmware loader use base parameters to size queues, set shared memory windows, program monitor buffers, configure Gen2 behavior, and request the firmware image declared by `MODULE_FIRMWARE`.

## State and Persistence Behavior
The configuration is immutable. Runtime state is created in the transport, firmware monitor, queue allocator, and MVM opmode from these limits and register addresses.

## Dependencies and Integration Points
It depends on `iwl-config.h`, `iwl-prph.h`, and `fw/api/txq.h`. It integrates with MVM, PCIe Gen2 transport, firmware debug/monitor code, and checksum offload setup.

## Risks and Edge Cases
Incorrect xtal latency/LTR pairing can affect power management and wake latency. Monitor register masks and GP2 addresses are silicon-specific. The `iwl_ax200_mac_cfg` differs by not being integrated and by setting `bisr_workaround`; wrong matching can regress device initialization.

## Test Signals
Probe AX200/AX201/Qu devices, verify firmware API 77 loading, queue allocation up to configured limits, monitor dump collection, D3 debug region capture, checksum offload advertisement, latency/LTR programming, and suspend/resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/cfg/22000.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/cfg/5000.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/cfg/5000.c

## Purpose
`5000.c` defines DVM configuration for Intel WiFi Link 5100/5300 and WiMAX/WiFi 5150/5350 families, including firmware API ranges, EEPROM/calibration versions, base parameters, RF configs, antenna overrides, HT capabilities, WiMAX coexistence flags, and firmware aliases.

## Important APIs, Types, and Data
- Firmware API ranges: 5000 supports API 1-5; 5150 supports API 1-2.
- EEPROM versions: separate 5000 and 5050/5150 calibration/version constants.
- `iwl5000_base`: EEPROM image size, 16 queue model, 256 TFD queue size, PLL config, LED compensation, disabled watchdog, event log size, SCD chain extension workaround.
- `iwl5000_eeprom_params`: regulatory bands including both 2.4 and 5 GHz HT40.
- MAC configs: `iwl5000_mac_cfg`, `iwl5150_mac_cfg`.
- RF configs: `iwl5300_agn_cfg`, `iwl5100_n_cfg`, `iwl5100_abg_cfg`, `iwl5350_agn_cfg`, `iwl5150_agn_cfg`, `iwl5150_abg_cfg`.

## Control Flow and Integration
PCI tables pair a MAC config with an RF config. The driver requests `iwlwifi-5000-*` or `iwlwifi-5150-*` firmware, validates EEPROM/calibration versions, sets valid antenna masks, and advertises HT40 for N-capable variants. WiMAX coexistence is enabled for 5350/5150.

## State and Persistence Behavior
This file contains read-only config only. The selected values feed firmware loading, NVM/regulatory parsing, antenna setup, LED mode, and runtime coexistence behavior.

## Dependencies and Integration Points
It depends on `iwl-config.h`, `iwl-agn-hw.h`, and module firmware macros. The Makefile includes it for `CONFIG_IWLDVM`.

## Risks and Edge Cases
Some EEPROMs have wrong antenna information; this file intentionally overrides valid TX/RX antennas for 5300 and 5100. Removing or changing those overrides can break RF capability. WiMAX coexistence flags must stay matched to combo hardware.

## Test Signals
Validate firmware alias generation, NVM/calibration version handling, antenna mask application, 2.4/5 GHz HT40 advertisement, WiMAX coexistence paths, and probe behavior for ABG versus AGN variants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/cfg/5000.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/cfg/6000.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/cfg/6000.c

## Purpose
`6000.c` defines DVM configuration for the Intel 6000, 6005, 6030, 6035, 6050, 6150, 1030, and 130 families, including multiple base parameter sets, firmware prefixes/API ranges, EEPROM/calibration versions, MAC configs, RF configs, HT capabilities, antenna overrides, LED modes, watchdogs, enhanced TX power, and WiMAX coexistence.

## Important APIs, Types, and Data
- Firmware ranges: 6000 min 4 max 6, 6050 min 4 max 5, 6000G2 min 5 max 6, 6035 API 6 only.
- Bases: `iwl6000_base`, `iwl6050_base`, `iwl6000_g2_base` with different OTP limits, event log sizes, LED compensation, and watchdog timeout.
- EEPROM params: enhanced TX power and regulatory bands including 6000-style 2.4 HT40 and 5 GHz HT40.
- MAC configs: `iwl6005_mac_cfg`, `iwl6030_mac_cfg`, `iwl6000i_mac_cfg`, `iwl6050_mac_cfg`, `iwl6150_mac_cfg`, `iwl6000_mac_cfg`.
- RF configs cover N and non-N variants, internal PA 6000i, WiMAX 6050/6150, and 3-antenna 6300.
- Product names for numerous retail and derivative devices.

## Control Flow and Integration
PCI matching chooses the correct MAC and RF config. The selected config drives firmware request prefix (`6000`, `6050`, `6000g2a`, `6000g2b`), EEPROM validation, TX/RX antenna masks, HT feature advertisement, LED mode, watchdog timeout, and WiMAX coexistence. N-capable configs enable greenfield, RTS/CTS aggregation protection, and 2.4/5 GHz HT40.

## State and Persistence Behavior
The file is immutable configuration. It influences runtime firmware/NVM selection, regulatory data interpretation, queue/watchdog behavior, LED behavior, and coexistence flags but does not mutate state directly.

## Dependencies and Integration Points
It depends on `iwl-config.h`, `iwl-agn-hw.h`, and DVM commands for Bluetooth-related definitions. The top-level Makefile includes it for `CONFIG_IWLDVM`.

## Risks and Edge Cases
Many products share similar names but require different base parameters and firmware prefixes. Antenna overrides for internal PA and combo hardware are significant. API ranges and EEPROM version constants must match firmware packages and hardware revisions.

## Test Signals
Build DVM, verify module firmware aliases, exercise probe for each firmware prefix family, validate EEPROM/calibration version handling, antenna masks, N/non-N feature exposure, LED behavior, watchdog selection, and WiMAX coexistence behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/cfg/6000.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/cfg/7000.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/cfg/7000.c

## Purpose
`7000.c` defines MVM-era MAC/RF configuration for Intel 7260, 7265, 7265D, 3160, 3165, and 3168 devices. It introduces 31 queues, DCCM memory definitions, NVM versions, thermal throttling parameters, power TX backoff tables, and RF configs for AC/N variants.

## Important APIs, Types, and Data
- Firmware ranges: 7260/7265 API 17, 7265D and 3168 API 22-29.
- NVM versions for 7260, 3160, 3165, 3168, 7265, 7265D.
- `iwl7000_base`: 16K OTP, 31 queues, shadow RAM, LED compensation, long watchdog, shadow register enablement, PCIe L1, APMG wake workaround.
- `iwl7000_high_temp_tt_params`: CT kill, dynamic SMPS, TX protection, and TX backoff thermal thresholds.
- MAC config: `iwl7000_mac_cfg`.
- RF configs: `iwl7260_cfg`, `iwl7260_high_temp_cfg`, `iwl3160_cfg`, `iwl3165_2ac_cfg`, `iwl3168_2ac_cfg`, `iwl7265_cfg`, `iwl7265d_cfg`.
- `iwl7265_pwr_tx_backoffs` maps power levels to backoff values.

## Control Flow and Integration
PCI IDs select a product-specific RF config. MVM uses firmware prefix/API range, NVM version, DCCM length, HT parameters, LDPC/STBC support, power backoff, and thermal params during init, capability registration, and runtime thermal management. Firmware aliases cover all declared prefixes.

## State and Persistence Behavior
The file is immutable config. Thermal and backoff tables become runtime policy inputs; DCCM lengths guide firmware memory dump handling; NVM versions gate NVM parsing.

## Dependencies and Integration Points
It depends on `iwl-config.h` and Linux module/stringify macros. It is included for `CONFIG_IWLMVM`.

## Risks and Edge Cases
7265D/3165 use the 7265D firmware prefix and newer API range; confusing 7265 and 7265D can break firmware loading. High-temperature configs must only be matched to hardware needing those thresholds. NVM type `IWL_NVM_SDP` is specific to 3168.

## Test Signals
Probe each 7000-family ID, verify firmware filename/API bounds, NVM version acceptance, STBC/LDPC flags, thermal throttling thresholds, power TX backoff application, DCCM dump sizing, and suspend/resume with PCIe L1.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/cfg/7000.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/cfg/8000.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/cfg/8000.c

## Purpose
`8000.c` defines MVM configuration for Intel 8260/8265/8275/4165-class devices, including firmware API 22-36, extended NVM, DCCM/DCCM2/SMEM ranges, thermal throttling, checksum offload, and VHT MU-MIMO support for 8265.

## Important APIs, Types, and Data
- Firmware prefixes: `iwlwifi-8000C` and `iwlwifi-8265`.
- `iwl8000_base`: 32K OTP, 31 queues, shadow RAM/registers, PCIe L1, NVM hardware section 10, RX checksum feature, SMEM range, APMG unsupported.
- `iwl8000_tt_params`: CT kill, dynamic SMPS, TX protection, and TX backoff thresholds.
- `iwl8000_mac_cfg`: family base config.
- Common RF macro includes RF-state LED, non-shared antenna A, DCCM/DCCM2 offsets and lengths, thermal params, and extended NVM.
- RF configs: `iwl8260_cfg`, `iwl8265_cfg`; both enable STBC, LDPC, and 2.4/5 GHz HT40, with 8265 also enabling VHT MU-MIMO.

## Control Flow and Integration
MVM uses the MAC config and RF config to size firmware memory areas, request the correct firmware, parse extended NVM, expose checksum offload and HT/VHT capabilities, and apply thermal limits. Product name constants are consumed by PCI ID tables.

## State and Persistence Behavior
Immutable configuration only. Runtime state includes firmware memory windows, NVM-derived capabilities, and thermal policy derived from these tables.

## Dependencies and Integration Points
It depends on `iwl-config.h`, module firmware macros, and MVM build inclusion. Transport debug and firmware dump code consume DCCM/SMEM fields.

## Risks and Edge Cases
8000C and 8265 have identical API bounds but different firmware prefixes and capabilities. Extended NVM and SMEM/DCCM sizes must match firmware dump expectations. MU-MIMO support should remain restricted to supported RF configs.

## Test Signals
Probe 8260/8265 variants, confirm firmware aliases, extended NVM parsing, checksum offload flags, VHT MU-MIMO exposure, thermal throttling behavior, and firmware dump memory range correctness.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/cfg/8000.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/cfg/9000.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/cfg/9000.c

## Purpose
`9000.c` defines MAC/base configuration for 9000-family devices such as 9000 and 9560, including firmware API 30-46, shared memory, monitor register mappings, checksum offload, MAC-address CSR location, D3 debug region, MQ RX, integrated CNVi, and xtal latency variants.

## Important APIs, Types, and Data
- Firmware prefixes: `iwlwifi-9000-pu-b0-jf-b0` and `iwlwifi-9260-th-b0-jf-b0`.
- `iwl9000_base`: 32K OTP, 31 queues, shadow RAM/registers, L1, SMEM range, TX/RX checksum features, APMG unsupported, MAC address CSR offset, D3 debug data range, NVM hardware section, monitor SMEM/DRAM register definitions, API range.
- MAC configs: `iwl9000_mac_cfg`, `iwl9560_mac_cfg`, `iwl9560_long_latency_mac_cfg`, `iwl9560_shared_clk_mac_cfg`.
- Integrated configs set `integrated`, xtal latency, and optionally shared clock PHY flag.

## Control Flow and Integration
PCI matching combines these MAC configs with RF configs such as JF/HR files. The base config feeds transport queue setup, firmware monitor handling, checksum offload setup, NVM parsing, D3 debug collection, and firmware request aliases.

## State and Persistence Behavior
Only immutable tables are defined. Runtime transport and MVM state persist the effects of queue limits, monitor register addresses, and integrated latency/clock settings.

## Dependencies and Integration Points
It depends on `iwl-config.h`, `fw/file.h`, and `iwl-prph.h` for monitor register definitions. It integrates with MVM, PCIe transport, and RF config files.

## Risks and Edge Cases
Integrated 9560 variants differ only in latency/shared-clock values, which are easy to mis-match in PCI ID tables. Monitor register masks must track firmware/hardware versions. Firmware API range is lower than newer AX/BZ families and must not be cross-applied.

## Test Signals
Probe 9000/9260/9560 variants, verify firmware prefix selection, MQ RX setup, checksum offload, monitor dump pointers, D3 debug data capture, NVM section parsing, shared-clock PHY flag handling, and suspend/resume latency behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/cfg/9000.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/cfg/ax210.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/cfg/ax210.c

## Purpose
`ax210.c` defines MAC/base configuration for AX210-generation devices, including firmware API 89, 512 queues, large TFD queue size, HE block-ack queue sizing, SMEM and debug regions, DBGC monitor registers, Gen2 transport, UMAC PRPH offset, integrated/non-integrated variants, latency variants, and IMR enablement.

## Important APIs, Types, and Data
- API range: AX210 API 89 only.
- `iwl_ax210_base`: 512 queues, max TFD queue size 65536, min TXQ size 128, HE BA queue size, SMEM, checksum features, MAC address CSR offset, D3 debug data, GP2 register address, SMEM/DRAM monitor registers with current-fragment support.
- MAC configs: `iwl_ty_mac_cfg`, `iwl_so_mac_cfg`, `iwl_so_long_latency_mac_cfg`, `iwl_so_long_latency_imr_mac_cfg`, `iwl_ma_mac_cfg`.
- Integrated variants set `integrated`, `low_latency_xtal`, LTR delay, and optional `imr_enabled`.

## Control Flow and Integration
The transport and MVM opmode consume these values after PCI matching. RF capabilities come from companion RF config files. The base config drives queue allocation, firmware monitor handling, checksum offload, UMAC PRPH address translation, and debug data collection.

## State and Persistence Behavior
The file defines immutable config. Runtime state includes allocated queue sets and firmware debug/monitor regions sized and addressed according to these constants.

## Dependencies and Integration Points
It depends on `iwl-config.h`, `iwl-prph.h`, and `fw/api/txq.h`. It integrates with AX210/So/Ty/Ma PCI IDs and RF config files such as GF/HR.

## Risks and Edge Cases
Large queue sizes and DBGC monitor fields must match firmware expectations. Several latency values are marked TODO in comments, signaling silicon-specific uncertainty. IMR must only be enabled for matching hardware.

## Test Signals
Probe AX210/AX211/related devices, verify API 89 firmware loading, queue allocation at HE sizes, DBGC monitor dump collection, UMAC PRPH offset access, IMR path on the IMR variant, checksum offload, and suspend/resume on long-latency CNVi devices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/cfg/ax210.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/cfg/bz.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/cfg/bz.c

## Purpose
`bz.c` defines MAC/base configuration for BZ/GL Wi-Fi 7-era devices, using core-release-based firmware API encoding, 512 queues, EHT BA queue sizing, SMEM/debug regions, DBGC/DBGI monitor registers, Gen2 transport, integrated BZ and discrete GL variants, and exported KUnit-visible config.

## Important APIs, Types, and Data
- Firmware versioning: core max 102 encoded as API max, API min 100.
- `iwl_bz_base`: 512 queues, 65536 max TFD queue size, min TXQ 128, EHT BA queue size, SMEM, checksum features, MAC address CSR offset 0x30, D3 debug data, GP2 address, SMEM/DRAM/DBGI monitor registers.
- MAC configs: `iwl_bz_mac_cfg` and `iwl_gl_mac_cfg`.
- `iwl_bz_mac_cfg` is integrated with long/low-latency xtal and LTR delay; `iwl_gl_mac_cfg` is non-integrated but otherwise Gen2 with UMAC PRPH offset.

## Control Flow and Integration
PCI tables select BZ or GL MAC config, then pair with RF configs such as FM/GF/HR. Transport setup uses base queue and monitor definitions; firmware loading uses core-as-API versioning and RF file firmware declarations.

## State and Persistence Behavior
The file is immutable configuration. Runtime state derives queue sizes, firmware debug buffers, monitor pointers, and latency behavior from the selected config.

## Dependencies and Integration Points
It depends on `iwl-config.h`, `iwl-prph.h`, and `fw/api/txq.h`. It is built for both MVM and MLD in the Makefile and exports `iwl_bz_mac_cfg` for KUnit when enabled.

## Risks and Edge Cases
BZ and GL differ in integration and latency settings; wrong matching can affect power management. Core-release version encoding must match firmware declaration macros in RF files. EHT queue sizing and DBGI monitor registers are newer paths that need firmware compatibility.

## Test Signals
Build MVM and MLD configurations, run KUnit references to exported config, probe BZ/GL devices, verify core firmware selection, EHT queue sizing, DBGC/DBGI monitor dump capture, checksum offload, and long-latency suspend/resume behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/cfg/bz.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/cfg/dr.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/cfg/dr.c

## Purpose
`dr.c` defines MAC/base configuration and firmware declaration for DR-family devices introduced in 2024-2025, using core max 102/API min 100, EHT queue sizing, DBGC/DBGI monitor registers, Gen2 integrated transport, and the `iwlwifi-dr-a0-pe-a0` firmware prefix.

## Important APIs, Types, and Data
- Firmware prefix/core: `IWL_DR_A_PE_A_FW_PRE`, `IWL_DR_UCODE_CORE_MAX`, `IWL_DR_UCODE_API_MIN`.
- `iwl_dr_base`: 512 queues, 65536 max TFD queue size, min TXQ 128, EHT BA queue size, SMEM, checksum features, MAC address CSR offset 0x30, D3 debug data, GP2 address, SMEM/DRAM/DBGI monitor registers.
- `iwl_dr_mac_cfg`: device family DR, Gen2, integrated, MQ RX, UMAC PRPH offset, long low-latency xtal, LTR delay.
- `IWL_CORE_FW` declares the firmware image for the core release.

## Control Flow and Integration
MLD/PCI matching selects `iwl_dr_mac_cfg` with a PE RF config. Transport uses the base queue and monitor definitions, and firmware loader sees the `IWL_CORE_FW` alias.

## State and Persistence Behavior
Immutable config only. Runtime queue, debug, monitor, and latency state is derived from this data.

## Dependencies and Integration Points
It depends on `iwl-config.h`, `iwl-prph.h`, and `fw/api/txq.h`. The top-level Makefile includes it for `CONFIG_IWLMLD`.

## Risks and Edge Cases
DR is newer and tightly tied to EHT queue sizing and core firmware versioning. Misaligned firmware prefix/core, MAC family, or RF pairing can prevent probe or produce unsupported capability exposure.

## Test Signals
Build MLD, validate firmware alias generation, probe DR hardware or PCI ID simulation, verify EHT TXQ sizing, DBGC/DBGI monitor collection, checksum offload, UMAC PRPH access, and suspend/resume with long-latency settings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/cfg/dr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/cfg/rf-fm.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/cfg/rf-fm.c

## Purpose
`rf-fm.c` defines FM RF configuration for BZ/GL/SC-era Wi-Fi 7 devices, including EHT/UHB capability, NVM version/type, RBD count, bandwidth-limited variant, product names, and core firmware declarations for several MAC/RF revision prefixes.

## Important APIs, Types, and Data
- Firmware prefixes: BZ FM B/C/FM4 and GL FM B/C variants.
- `IWL_DEVICE_FM` macro: STBC, LDPC, HT40 on 2.4/5 GHz, RF-state LED, non-shared antenna B, VHT MU-MIMO, UHB, EHT, EHT RBD count, NVM version 0x0a1d, extended NVM.
- RF configs: `iwl_rf_fm` and `iwl_rf_fm_160mhz` with `bw_limit = 160`.
- Product name strings for Killer BE1750/BE1790 and Intel BE200/BE201/BE202/BE401.
- `IWL_CORE_FW` declarations tied to `IWL_BZ_UCODE_CORE_MAX`.

## Control Flow and Integration
PCI ID tables pair these RF configs with BZ/GL/SC MAC configs. The selected RF config controls advertised PHY features, RBD sizing, NVM parsing, LED behavior, bandwidth limit, and firmware image prefix.

## State and Persistence Behavior
Immutable RF configuration only. Runtime capability state is derived by MVM/MLD from these fields and NVM contents.

## Dependencies and Integration Points
It depends on `iwl-config.h` and core firmware macros from the broader cfg build. It is included under `CONFIG_IWLMLD`.

## Risks and Edge Cases
The 160 MHz variant intentionally caps bandwidth despite EHT-capable defaults. Firmware prefixes share BZ core max, so core-version macro availability and include ordering matter. UHB/EHT flags must match regulatory/NVM support.

## Test Signals
Probe FM devices, confirm firmware alias availability, validate EHT/UHB capability exposure, RBD count, extended NVM parsing, bandwidth cap behavior for 160 MHz variants, and product-name mappings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/cfg/rf-fm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/cfg/rf-gf.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/cfg/rf-gf.c

## Purpose
`rf-gf.c` defines GF RF configuration for Wi-Fi 6E-generation AX210/AX211/AX411 and related SO/TY/MA/BZ/SC combinations, including firmware API 100, PNVM firmware declarations for several prefixes, UHB capability, HE RBD count, extended NVM, and product names.

## Important APIs, Types, and Data
- Firmware API range: GF API 100 only.
- Firmware prefixes for SO, TY, MA, BZ, and SC GF/GF4 combinations.
- `iwl_rf_gf`: UHB, RF-state LED, non-shared antenna B, VHT MU-MIMO, STBC/LDPC, 2.4/5 GHz HT40, NVM 0x0a1d, extended NVM, HE RBD count, API min/max.
- Product names for AX210/AX211/AX411 and Killer AX1675/AX1690 variants.
- Firmware declarations: `IWL_FW_AND_PNVM` for SO/TY/MA and `MODULE_FIRMWARE` for BZ/SC GF images.

## Control Flow and Integration
MAC configs such as AX210, BZ, and SC pair with this RF config. Firmware loader uses the prefix declarations and PNVM declarations where applicable. Capability registration uses the RF fields to expose 6 GHz/UHB and HT/VHT/HE behavior.

## State and Persistence Behavior
Only immutable RF config and names are defined. Runtime state includes parsed NVM/PNVM and capability flags derived from this table.

## Dependencies and Integration Points
It depends on `iwl-config.h` and firmware declaration macros. It is built for MVM RF configs and also declares firmware images used by newer MAC families.

## Risks and Edge Cases
Some prefixes use PNVM while BZ/SC entries are declared as plain module firmware. API 100 must align with matching MAC base min/max. UHB support requires correct regulatory/NVM handling.

## Test Signals
Verify firmware and PNVM alias installation, probe AX210/AX211/AX411 and BZ/SC GF IDs, check 6 GHz capability exposure, HE RBD sizing, extended NVM parsing, and product-name mapping.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/cfg/rf-gf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/cfg/rf-hr.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/cfg/rf-hr.c

## Purpose
`rf-hr.c` defines HR RF configuration for Wi-Fi 6 devices such as AX101/AX200/AX201/AX203 and multiple QU/SO/MA/BZ/SC MAC combinations. It sets firmware API 100, HE RBD count, extended NVM, bandwidth variants, SISO-diversity variant, product names, and firmware aliases.

## Important APIs, Types, and Data
- Firmware API range: HR API 100 only.
- Firmware prefixes for QU, QUZ, SO, MA, BZ, and SC HR combinations.
- `IWL_DEVICE_HR` macro: RF-state LED, non-shared antenna B, VHT MU-MIMO, STBC/LDPC, 2.4/5 GHz HT40, HE RBD count, NVM 0x0a1d, extended NVM, API min/max.
- RF configs: `iwl_rf_hr1` with TX SISO diversity, `iwl_rf_hr`, and `iwl_rf_hr_80mhz` with bandwidth cap.
- Product names for AX101, AX200, AX201, and AX203.

## Control Flow and Integration
PCI IDs combine HR RF configs with MAC configs. The firmware loader uses the relevant `MODULE_FIRMWARE` alias, while capability code consumes bandwidth caps, diversity, and HE/VHT flags.

## State and Persistence Behavior
The file is immutable. Runtime state is derived from config fields and NVM content during probe and capability registration.

## Dependencies and Integration Points
It depends on `iwl-config.h` and module firmware macros. It is included as an MVM RF config and shares newer firmware prefixes with BZ/SC MAC families.

## Risks and Edge Cases
The file defines both `IWL_SC_A_HR_A_FW_PRE` and `IWL_SC_A_HR_B_FW_PRE` to the same string, which should be intentional but is easy to misread. Bandwidth and SISO-diversity variants must be matched to correct SKU IDs. Firmware API 100 must remain compatible with MAC base configs.

## Test Signals
Probe HR variants, verify firmware aliases for each prefix, confirm bandwidth caps, SISO diversity behavior, HE RBD count, VHT MU-MIMO flags, NVM parsing, and product-name strings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/cfg/rf-hr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/cfg/rf-jf.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/cfg/rf-jf.c

## Purpose
`rf-jf.c` defines JF RF configuration for Wireless-AC 9260/9461/9462/9560-class devices, including firmware API 77, DCCM memory ranges for Pu/Th firmware, thermal throttling, extended NVM, non-HE RBD count, bandwidth variants, and product names.

## Important APIs, Types, and Data
- Firmware API range: JF API 77 only.
- Firmware prefixes for QU/QUZ/SO JF combinations.
- DCCM/DCCM2 offsets and lengths for 9000-era firmware.
- `iwl_jf_tt_params`: CT kill, dynamic SMPS, TX protection, and TX backoff thresholds.
- `IWL_DEVICE_JF`: DCCM/thermal fields, RF-state LED, non-shared antenna B, non-HE RBD count, VHT MU-MIMO, STBC/LDPC, HT40, NVM 0x0a1d, extended NVM, API range.
- RF configs: `iwl_rf_jf`, `iwl_rf_jf_80mhz`.
- Product and Killer adapter names.

## Control Flow and Integration
9000/22000-era MAC configs pair with JF RF configs. MVM uses DCCM fields for firmware dump support, thermal params for runtime throttling, and RF fields for capability registration and firmware loading.

## State and Persistence Behavior
The file defines immutable RF/thermal config. Runtime thermal state, firmware memory dump state, and capabilities derive from these tables.

## Dependencies and Integration Points
It depends on `iwl-config.h`. It is included under `CONFIG_IWLMVM` as an RF config and pairs especially with 9000-family MAC configs.

## Risks and Edge Cases
Comments note DCCM values are ignored when not paired with Pu/Th MAC firmware due to offload; wrong MAC/RF pairing can produce confusing unused fields. Bandwidth-capped variants must be correctly selected.

## Test Signals
Probe JF devices, confirm API 77 firmware aliases, validate 80/160 MHz capability selection, thermal throttling, DCCM dump ranges, extended NVM parsing, non-HE RBD count, and product-name mappings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/cfg/rf-jf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/cfg/rf-pe.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/cfg/rf-pe.c

## Purpose
`rf-pe.c` currently provides product name strings for PE-related Intel/Killer Wi-Fi 8 and Wi-Fi 7 devices. It explicitly notes that `iwl_rf_wh` and `iwl_rf_wh_160mhz` are currently aliases/defines for FM RF configs elsewhere rather than local RF config objects.

## Important APIs, Types, and Data
- Product names: Killer BN1850w2, Killer BN1850i, Intel BN201, BN203, and BE223.
- No local `struct iwl_rf_cfg` definitions are present in this file.

## Control Flow and Integration
PCI ID tables can reference these product-name symbols and RF config aliases defined in headers or other translation units. The file contributes names to the build but does not alter firmware selection or capabilities directly.

## State and Persistence Behavior
Only immutable string constants are defined. No runtime state is created or mutated.

## Dependencies and Integration Points
It depends on `iwl-config.h` for shared declarations. The Makefile includes this RF file for `CONFIG_IWLMLD`.

## Risks and Edge Cases
Because RF configs are not locally defined, maintainers must check header-level aliases when changing PE/WH/FM relationships. Product-name-only files can still break builds if declarations in `iwl-config.h` diverge.

## Test Signals
Build MLD configs, run modpost for exported/declared name symbols, and verify PCI ID mappings display the expected product names while using the intended aliased RF config.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/cfg/rf-pe.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/cfg/rf-wh.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/cfg/rf-wh.c

## Purpose
`rf-wh.c` defines a WH RF configuration variant for Wi-Fi 7 devices where EHT support is disabled, plus product names for BE211/BE213/AX221 and Killer BE1775 variants. Comments note that regular `iwl_rf_wh` and `iwl_rf_wh_160mhz` are currently aliases for FM configs.

## Important APIs, Types, and Data
- `IWL_DEVICE_WH` macro: STBC, LDPC, 2.4/5 GHz HT40, RF-state LED, non-shared antenna B, VHT MU-MIMO, UHB, EHT RBD count, NVM 0x0a1d, extended NVM.
- `iwl_rf_wh_non_eht`: applies `IWL_DEVICE_WH` and explicitly sets `.eht_supported = false`.
- Product names: Killer BE1775s/i, Intel BE211, BE213, and AX221.

## Control Flow and Integration
PCI IDs can select `iwl_rf_wh_non_eht` for WH devices requiring UHB-capable but non-EHT behavior, while other WH variants may alias FM configs. Capability registration consumes the EHT-disabled flag and bandwidth/capability fields.

## State and Persistence Behavior
The file defines immutable config and strings only. Runtime capabilities derive from these fields and NVM contents.

## Dependencies and Integration Points
It depends on `iwl-config.h`. The Makefile includes it for `CONFIG_IWLMLD`.

## Risks and Edge Cases
The macro includes EHT-sized RBD count while `iwl_rf_wh_non_eht` disables EHT; this should be validated against transport expectations. Alias comments mean WH behavior is split across this file and FM definitions.

## Test Signals
Build MLD, probe WH non-EHT IDs, verify UHB without EHT capability exposure, RBD allocation behavior, extended NVM parsing, and product-name mapping. Also check alias-based WH variants still resolve correctly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/cfg/rf-wh.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/cfg/sc.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/cfg/sc.c

## Purpose
`sc.c` defines MAC/base configuration and firmware declarations for SC-family devices, using core max 102/API min 100, EHT queue sizing, SMEM/debug regions, DBGC/DBGI monitor registers, Gen2 integrated transport, long low-latency xtal settings, and multiple FM/WH firmware prefixes.

## Important APIs, Types, and Data
- Firmware prefixes: SC FM B/C, SC WH A, SC2 FM C, SC2 WH A.
- `iwl_sc_base`: 512 queues, 65536 max TFD queue size, min TXQ 128, EHT BA queue size, SMEM, checksum features, MAC address CSR offset 0x30, D3 debug data, GP2 register, SMEM/DRAM/DBGI monitor registers, API range.
- `iwl_sc_mac_cfg`: device family SC, integrated, Gen2, MQ RX, UMAC PRPH offset, xtal latency 12000, low latency xtal, LTR delay.
- `IWL_CORE_FW` declarations for all SC/SC2 prefixes.

## Control Flow and Integration
MLD or MVM paths pair SC MAC config with RF configs such as FM/GF/HR/WH. Transport setup uses the base queue and monitor definitions; firmware loader uses the core firmware aliases.

## State and Persistence Behavior
Immutable config only. Runtime queue allocation, monitor state, checksum offload, firmware debug, and latency programming derive from these constants.

## Dependencies and Integration Points
It depends on `iwl-config.h`, `iwl-prph.h`, and `fw/api/txq.h`. The Makefile includes it for both `CONFIG_IWLMVM` and `CONFIG_IWLMLD`.

## Risks and Edge Cases
SC and SC2 firmware prefixes must remain aligned with RF pairings and core release. EHT BA queue sizing and DBGI monitor registers require matching firmware support. Shared inclusion by MVM and MLD requires symbol uniqueness and config compatibility.

## Test Signals
Build MVM and MLD, verify firmware aliases, probe SC/SC2 IDs, validate EHT queue sizing, DBGC/DBGI monitor dump collection, checksum offload, UMAC PRPH access, and long-latency suspend/resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/cfg/sc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/dvm/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/dvm/Makefile

## Purpose
`dvm/Makefile` defines the object composition of the DVM firmware opmode module `iwldvm`, which supports older iwlwifi devices using DVM firmware.

## Important APIs, Types, and Build Targets
- Main target: `obj-$(CONFIG_IWLDVM) += iwldvm.o`.
- Core DVM objects: `main.o`, `rs.o`, `mac80211.o`, `ucode.o`, `tx.o`, `lib.o`, `calib.o`, `tt.o`, `sta.o`, `rx.o`, `eeprom.o`, `power.o`, `scan.o`, `rxon.o`, and `devices.o`.
- Optional objects: `led.o` under `CONFIG_IWLWIFI_LEDS`, `debugfs.o` under `CONFIG_IWLWIFI_DEBUGFS`.
- Include path: `ccflags-y += -I $(src)/../`.

## Control Flow and Integration
Kbuild links the listed objects into `iwldvm.o` when DVM support is enabled. The module integrates with the shared `iwlwifi` core and config files compiled by the parent Makefile. Optional LED/debugfs objects add runtime surfaces only when the corresponding Kconfig features are enabled.

## State and Persistence Behavior
No runtime state is stored in the Makefile. It determines which code contributes to the DVM module, affecting available runtime features and callbacks.

## Dependencies and Integration Points
It consumes `CONFIG_IWLDVM`, `CONFIG_IWLWIFI_LEDS`, and `CONFIG_IWLWIFI_DEBUGFS` from Kconfig and includes headers from the parent `iwlwifi` directory.

## Risks and Edge Cases
Missing objects can cause unresolved symbols or missing opmode functionality. Optional debugfs/LED objects must remain guarded by the same Kconfig symbols as their declarations and call sites. Include path spacing is accepted by kbuild but should remain consistent with local style if edited.

## Test Signals
Build `IWLDVM` built-in and modular, with LED/debugfs enabled and disabled; check modpost for unresolved symbols; boot/probe an older DVM-supported device; verify mac80211 registration, firmware load, scan, RXON, station, TX/RX, power, thermal, LED, and debugfs paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/dvm/Makefile -->
