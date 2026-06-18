# Research: subset-b-004768

Grouped source research for ath9k QCA/AR9003-family initialization tables, core driver state declarations, and the Owl external EEPROM loader. Each section is source-tree aligned and intended for deterministic splitting into `Docs/researches/<source>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/ar953x_initvals.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/ar953x_initvals.h

Purpose: Provides QCA953x AR9003-family hardware initialization arrays for MAC, baseband, radio, RX gain, TX gain, and modal/postamble programming. These tables are selected by `ar9003_hw.c` for `AR_SREV_9531()` hardware during reset and channel bring-up.

Important APIs and data: The file exports static `u32` init arrays such as `qca953x_1p0_mac_core`, `qca953x_1p0_baseband_core`, `qca953x_1p0_baseband_postamble`, `qca953x_1p0_radio_core`, `qca953x_1p0_radio_postamble`, revision-specific TX gain tables for 1.0, 1.1, and 2.0 silicon, and 2.0-specific baseband/RX gain tables. Macro aliases reuse shared AR9300/AR955x tables for MAC postamble, SOC pre/postamble, common RX gain, no-XLNA gain, fast clock, and RX gain bounds.

Control flow: The header has no executable flow. Its arrays are consumed through `INIT_INI_ARRAY()` in `ar9003_hw_attach_ops()` and the AR9003 TX/RX gain selection helpers. The main hardware initialization branch chooses 1.0/1.1 versus 2.0 baseband and RX tables using `AR_SREV_9531_20()`, and chooses TX gain tables according to `AR_SREV_9531_10()`, `AR_SREV_9531_11()`, or `AR_SREV_9531_20()`. Later gain-mode overrides can replace `ah->iniModesTxGain` and `ah->iniModesRxGain` when EEPROM/configured gain indices request alternate tables.

State and persistence: The file owns immutable compile-time register data only. Runtime state is the `struct ath_hw` INI array pointers populated from these tables; hardware register state persists until the next reset, channel reprogramming, or power transition.

Dependencies and integration points: Depends on the common ath9k initval convention: two-column arrays for register/value programming and five-column arrays for modal values across operating modes. It integrates with `ar9003_hw.c`, `hw.c` reset/programming paths, EEPROM-derived TX/RX gain selection, regulatory/channel setup, and shared tables from `ar9003_2p2_initvals.h` and `ar955x_1p0_initvals.h`.

Risks: Register values are silicon-revision and board-design sensitive. Incorrect table selection for QCA9531 1.0, 1.1, or 2.0 can break RF bring-up, calibration, sensitivity, or TX power. Macro aliases hide dependencies on AR9300/AR955x data, so changing a shared table affects QCA953x. Column-count mismatches would corrupt modal programming. TX gain table selection is especially risky because XPA/no-XPA and low-power variants must match board front-end hardware.

Test signals: Boot QCA9531 1.0/1.1/2.0 boards, verify hardware reset completes, scan/associate on 2.4 GHz, exercise EEPROM TX gain indices, compare RSSI/noise floor with and without external LNA, run throughput and power measurements, test regulatory channel changes, and watch ath9k debug output for calibration, PLL, or stuck beacon/reset loops.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/ar953x_initvals.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/ar955x_1p0_initvals.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/ar955x_1p0_initvals.h

Purpose: Supplies AR955x 1.0 SoC WLAN initialization tables for AR9003-family MAC, baseband, radio, SOC, RX gain bounds, TX gain, and fast-clock programming. `ar9003_hw.c` installs these tables for `AR_SREV_9550()` devices.

Important APIs and data: Defines `ar955x_1p0_radio_postamble`, `ar955x_1p0_baseband_postamble`, `ar955x_1p0_radio_core`, `ar955x_1p0_modes_xpa_tx_gain_table`, `ar955x_1p0_mac_core`, `ar955x_1p0_baseband_core`, `ar955x_1p0_soc_preamble`, `ar955x_1p0_common_wo_xlna_rx_gain_bounds`, `ar955x_1p0_mac_postamble`, `ar955x_1p0_common_rx_gain_bounds`, `ar955x_1p0_modes_no_xpa_tx_gain_table`, and `ar955x_1p0_modes_fast_clock`. Macro aliases reuse AR9300 2.2 SOC postamble, common RX gain tables, no-XLNA RX gain tables, and Japan 2484 MHz CCK FIR coefficients.

Control flow: The file is declarative. The AR9550 initialization branch assigns these arrays into `ah->iniMac`, `ah->iniBB`, `ah->iniRadio`, `ah->iniSOC`, `ah->iniModesRxGain`, `ah->ini_modes_rx_gain_bounds`, `ah->iniModesTxGain`, and `ah->iniModesFastClock`. Gain override helpers later switch between XPA and no-XPA TX tables and between common and no-XLNA RX tables based on hardware configuration.

State and persistence: The arrays are read-only driver data. They become active by being referenced from `struct ath_hw` and then written into device registers during hardware reset/channel setup. No filesystem or NVRAM persistence is handled here.

Dependencies and integration points: Integrated with AR9003 init sequencing, EEPROM/board data that determines XPA and XLNA behavior, fast-clock mode programming, and shared AR9300 tables. AR955x tables are also reused by QCA953x/QCA956x headers through macro aliases for SOC and gain-bound data.

Risks: AR955x is an SoC target, so bad init values can affect integrated radio/MAC operation before higher-level mac80211 symptoms are obvious. The TX gain arrays use nine columns, unlike narrower QCA953x/QCA956x tables, so consumers must use the correct array metadata. Shared aliases mean edits may affect descendant chip headers. RX gain bounds must remain synchronized with the selected RX gain table.

Test signals: Validate AR9550 reset, scan, association, 20/40 MHz operation, fast-clock behavior, XPA/no-XPA boards, external-LNA and no-XLNA receive paths, throughput under calibration load, and no regressions in QCA953x/QCA956x table selection that aliases AR955x definitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/ar955x_1p0_initvals.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/ar9565_1p0_initvals.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/ar9565_1p0_initvals.h

Purpose: Defines AR9565 1.0 PCIe WLAN init tables for MAC, baseband, radio, SOC, RX gain, PCIe SERDES power-save, fast clock, and multiple TX gain modes. These are used by ath9k when `AR_SREV_9565()` hardware is older than 1.1.

Important APIs and data: Exports `ar9565_1p0_mac_core`, `ar9565_1p0_baseband_core`, `ar9565_1p0_baseband_postamble`, `ar9565_1p0_radio_core`, `ar9565_1p0_radio_postamble`, `ar9565_1p0_soc_preamble`, `ar9565_1p0_soc_postamble`, `ar9565_1p0_Common_rx_gain_table`, `ar9565_1p0_pciephy_clkreq_disable_L1`, `ar9565_1p0_modes_fast_clock`, `ar9565_1p0_common_wo_xlna_rx_gain_table`, and low/high/high-power TX gain tables. Aliases map the default lowest-OB/DB TX gain table and the Japan 2484 MHz CCK FIR coefficients.

Control flow: `ar9003_hw.c` installs these arrays in the AR9565 1.0 branch. PCIe SERDES arrays are assigned only when `ah->config.pll_pwrsave` requests D3 or D0 PLL power-save handling. TX and RX gain helper functions can later swap `ah->iniModesTxGain` and `ah->iniModesRxGain` among low, high, high-power, and no-XLNA variants based on EEPROM/configuration gain indices.

State and persistence: The file holds immutable register tables. Active runtime state is stored in `struct ath_hw` INI descriptors and in the programmed PCIe/radio/baseband registers. PCIe power-save behavior persists in the device until the next SERDES reprogramming or reset.

Dependencies and integration points: Consumed by AR9003 hardware attach/reset code and PCIe power-management paths. It depends on AR9331 MAC postamble and AR9300 2.2 CCK FIR data through aliases. It interacts with EEPROM calibration, PLL power-save config, mac80211 suspend/resume, and ath9k reset/recovery paths.

Risks: PCIe SERDES values can cause link instability or resume failures if applied to the wrong revision or power state. AR9565 has PCIe-specific behavior unlike SoC-only QCA95xx parts, so table mixups can show as device disappearance rather than only RF degradation. The 1.1 header aliases most 1.0 tables, so changes here affect later revisions unless overridden. TX power and receive sensitivity depend on EEPROM gain-mode selection matching these arrays.

Test signals: Probe AR9565 1.0 PCIe devices, suspend/resume with D0 and D3 PLL power-save flags, verify scan/association and throughput, exercise TX gain modes 0/1/2/3, test no-XLNA RX mode, monitor PCIe link errors, and run reset recovery after beacon miss or hardware check failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/ar9565_1p0_initvals.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/ar9565_1p1_initvals.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/ar9565_1p1_initvals.h

Purpose: Provides the AR9565 1.1 initval layer. It mostly reuses AR9565 1.0 tables and overrides only the radio postamble values needed for 1.1-or-later silicon.

Important APIs and data: Macro aliases map `ar9565_1p1_mac_core`, MAC postamble, baseband core/postamble, radio core, SOC pre/postamble, RX gain, TX gain, PCIe SERDES, fast-clock, no-XLNA RX gain, and Japan CCK FIR names to their 1.0 equivalents. The only local array is `ar9565_1p1_radio_postamble`, a five-column modal table with 1.1-specific radio postamble entries.

Control flow: `ar9003_hw.c` selects these symbols for `AR_SREV_9565_11_OR_LATER()`. Because most symbols are aliases, initialization flows exactly like the 1.0 branch except that `ah->iniRadio[ATH_INI_POST]` points at the 1.1 radio postamble. TX/RX gain override helpers use the 1.1 names, which resolve to 1.0 data except where separately overridden.

State and persistence: No runtime state is owned by the header. It controls which read-only tables are referenced by `struct ath_hw` and later written to device registers during reset/channel setup.

Dependencies and integration points: Depends directly on `ar9565_1p0_initvals.h` being included before use in `ar9003_hw.c`. It integrates with AR9565 revision detection, PCIe power-save setup, TX/RX gain selection, and shared AR9003 init sequencing.

Risks: The alias-heavy design makes the single override easy to miss. Any future 1.1-specific change must define a real table before the alias is used or it will silently keep 1.0 behavior. Include ordering is material because the alias targets must already exist. Misclassifying 1.0 versus 1.1 hardware affects radio postamble programming.

Test signals: Confirm AR9565 1.1-or-later devices choose this branch, compare radio register writes against the 1.1 postamble, run association/throughput tests across 2.4 GHz channels, exercise PCIe suspend/resume, and ensure AR9565 1.0 behavior is unchanged.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/ar9565_1p1_initvals.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/ar956x_initvals.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/ar956x_initvals.h

Purpose: Defines QCA956x/QCA9561 SoC init tables for AR9003-family baseband, radio, RX gain, TX gain, XLNA, DFS, Japan-channel, and fast-clock support. `ar9003_hw.c` installs these for `AR_SREV_9561()`.

Important APIs and data: Local arrays include `qca956x_1p0_baseband_core`, `qca956x_1p0_baseband_postamble`, `qca956x_1p0_radio_core`, `qca956x_1p0_radio_postamble`, `qca956x_1p0_baseband_core_txfir_coeff_japan_2484`, `qca956x_1p0_modes_no_xpa_tx_gain_table`, `qca956x_1p0_modes_xpa_tx_gain_table`, `qca956x_1p0_modes_no_xpa_low_ob_db_tx_gain_table`, `qca956x_1p0_modes_no_xpa_green_tx_gain_table`, `qca956x_1p0_common_rx_gain_table`, and `qca956x_1p0_xlna_only`. Macro aliases reuse AR955x MAC/SOC/gain-bound definitions, AR9331 MAC postamble, AR9300 no-XLNA RX gain and DFS tables, and AR9462 fast-clock tables.

Control flow: The AR9561 init branch assigns MAC, baseband, radio, SOC, no-XLNA RX gain, RX gain bounds, default no-XPA TX gain, DFS, Japan CCK FIR, and fast-clock tables. TX gain helper modes can replace the default with XPA, low-OB/DB, or green TX gain tables. RX gain mode 0 can select `qca956x_1p0_common_rx_gain_table` plus `qca956x_1p0_xlna_only`, while mode 1 uses the no-XLNA alias.

State and persistence: The header contributes immutable register tables only. Runtime effects are hardware register programming and `struct ath_hw` INI pointer selection during resets and channel changes.

Dependencies and integration points: Integrated with AR9003 reset, DFS-channel setup, Japan 2484 MHz channel support, EEPROM gain decisions, QCA9561 SoC revision detection, and shared AR9300/AR9331/AR9462/AR955x tables. The XLNA-only table is an integration point for boards with external LNA-specific receive-chain behavior.

Risks: Many definitions are cross-chip aliases, so validating QCA956x changes requires checking AR955x, AR9331, AR9300, and AR9462 assumptions. TX gain tables use three columns rather than the wider AR955x/AR9580 format, so incorrect table metadata can program wrong modal values. DFS and Japan-channel table mistakes can cause regulatory or interoperability failures. XLNA selection is board-specific and can degrade sensitivity if applied incorrectly.

Test signals: Boot QCA9561 boards with no-XPA and XPA front ends, test scan/association/throughput, verify DFS-channel register programming, test channel 14/Japan CCK behavior when supported, exercise RX gain mode switching including XLNA-only path, and check calibration/noise-floor stability after reset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/ar956x_initvals.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/ar9580_1p0_initvals.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/ar9580_1p0_initvals.h

Purpose: Supplies AR9580 1.0 initialization data for radio, baseband, MAC, RX gain, DFS/Japan channel support, and a broad set of TX gain modes. These tables are selected for `AR_SREV_9580()` hardware in AR9003 setup.

Important APIs and data: Defines `ar9580_1p0_radio_core`, `ar9580_1p0_radio_postamble`, `ar9580_1p0_baseband_core`, `ar9580_1p0_low_ob_db_tx_gain_table`, `ar9580_1p0_high_power_tx_gain_table`, `ar9580_1p0_lowest_ob_db_tx_gain_table`, `ar9580_1p0_mac_core`, `ar9580_1p0_mixed_ob_db_tx_gain_table`, `ar9580_1p0_type6_tx_gain_table`, `ar9580_1p0_rx_gain_table`, `ar9580_1p0_baseband_postamble`, and `ar9580_1p0_baseband_postamble_dfs_channel`. Macro aliases reuse AR9300 2.2 SOC, MAC postamble, no-XLNA RX gain, type5/high-OB/DB TX gain, fast-clock, and Japan CCK FIR data.

Control flow: The AR9580 branch installs the local MAC/baseband/radio/SOC/RX/TX tables, then assigns fast-clock, Japan CCK FIR, and DFS tables. TX gain helper modes select among lowest, high-OB/DB, low-OB/DB, high-power, mixed, type5, and type6 tables according to the EEPROM/configured gain index. RX gain mode 1 switches to the aliased no-XLNA table.

State and persistence: The arrays are static read-only data. They affect runtime through `struct ath_hw` INI descriptors and the resulting device register writes. No persistent storage is modified.

Dependencies and integration points: Integrated with AR9003 hardware attach, EEPROM gain-index interpretation, DFS channel handling, fast-clock programming, Japan channel support, and common AR9300 tables. AR9580 has more TX gain variants than several neighboring chips, making it a key consumer of the gain-mode dispatch table.

Risks: Gain-mode dispatch must remain aligned with available AR9580 tables; selecting the wrong table can violate power limits or reduce performance. DFS postamble values are regulatory-sensitive. Shared aliases mean AR9300 table changes can affect AR9580 behavior. Modal array widths must match the INI programming helper expectations.

Test signals: Validate AR9580 reset and association, run TX power/EVM checks for all supported gain modes, test DFS channels and radar-capable channel changes, verify Japan 2484 MHz behavior where applicable, exercise no-XLNA RX mode, and watch for calibration, ANI, or stuck beacon regressions under traffic.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/ar9580_1p0_initvals.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/ath9k.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/ath9k.h

Purpose: Central ath9k soft-MAC driver header. It declares driver-wide module variables, descriptor/DMA helpers, TX/RX data structures, aggregation state, channel-context/P2P/offchannel state, beaconing state, calibration/workqueue entry points, Bluetooth coexistence, LEDs, WoWLAN, antenna diversity, PCI/AHB glue, and the main `struct ath_softc`.

Important APIs and types: Key types include `struct ath_descdma`, `struct ath_txq`, `struct ath_frame_info`, `struct ath_rxbuf`, `struct ath_buf_state`, `struct ath_buf`, `struct ath_atx_tid`, `struct ath_node`, `struct ath_tx_control`, `struct ath_tx`, `struct ath_rx_edma`, `struct ath_rx`, `struct ath_chanctx`, `struct ath_chanctx_sched`, `struct ath_offchannel`, `struct ath_vif`, `struct ath9k_vif_iter_data`, `struct ath_beacon`, `struct ath_btcoex`, `struct ath_ant_comb`, and `struct ath_softc`. Important helpers/macros include `ATH_TXBUF_RESET`, `DS2PHYS`, descriptor 4 KiB boundary checks, `INCR`, `TID_TO_WME_AC`, block-ack window macros, aggregation delimiter calculation, `ath_node_to_tid()`, channel-context iteration, TX queue locking wrappers, and `ath_read_cachesize()`. It declares major entry points for RX/TX, aggregation, beacons, ANI/calibration, reset, power save, device init/deinit, RF kill, bus registration, TX99, and HWRNG.

Control flow: The header defines the shared state and call surface used by implementation files. mac80211 operations enter ath9k through `ath9k_ops`; TX paths use `ath_tx_start()`, queue/TID scheduling, aggregation start/stop, and completion tasklets; RX paths use `ath_startrecv()`, `ath_rx_tasklet()`, and RX filter calculation; interrupt handling reaches `ath_isr()` and `ath9k_tasklet()`. Reset and calibration flow through work items and timers declared here. Optional channel-context code routes events through `ath_chanctx_event()` and offchannel/P2P helpers, while compile-time stubs collapse the flow when the feature is disabled.

State and persistence: `struct ath_softc` is the persistent runtime driver object for one device. It stores mac80211 hardware pointers, device/MMIO/IRQ data, spinlocks and mutexes, hardware state, interrupt status, power-save flags/reference count, RX/TX queues and DMA descriptors, beacon slots, current channel definition, up to two channel contexts, work items, timers, debug/LED/BTCOEX/WoW/HWRNG/TX99/DFS state, antenna-combining state, and completion objects. State is runtime-only but spans interrupts, tasklets, timers, workqueues, suspend/resume, reset, and device removal.

Dependencies and integration points: Includes Linux networking/device/interrupt/LED/completion/time/HWRNG headers plus ath9k `common.h`, `debug.h`, `mci.h`, and `dfs.h`. It is included across ath9k implementation files and binds the driver to mac80211, cfg80211 channel contexts, DMA mapping, PCI/AHB bus glue, Bluetooth coexistence, DFS pattern detection, WoWLAN, debugfs, and LED class integration.

Risks: This is a high-fanout header; structure layout or prototype changes can ripple through the whole driver. Locking boundaries are distributed across TX queue locks, power-management locks, channel locks, serial register access, and the main mutex. Compile-time feature stubs must match real function signatures or callers will diverge between configurations. `ath_node_to_tid()` assumes a valid vif and txq private storage. Aggregation/block-ack arithmetic must preserve 12-bit sequence wrap behavior. `struct ath_softc` lifetime crosses asynchronous tasklets, timers, workqueues, completions, and device removal, so teardown ordering is critical.

Test signals: Build with combinations of `CONFIG_ATH9K_PCI`, `CONFIG_ATH9K_AHB`, `CONFIG_ATH9K_CHANNEL_CONTEXT`, `CONFIG_ATH9K_BTCOEX_SUPPORT`, `CONFIG_MAC80211_LEDS`, `CONFIG_ATH9K_WOW`, `CONFIG_ATH9K_HWRNG`, and `CONFIG_ATH9K_TX99`. Exercise TX/RX traffic, AMPDU start/stop, queue drain/flush, beacon slot changes, channel-context switching, scan/remain-on-channel, suspend/resume/WoW, BT coexistence, antenna diversity, DFS, RF kill polling, hardware reset, and module unload with pending work.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/ath9k.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/ath9k_pci_owl_loader.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/ath9k_pci_owl_loader.c

Purpose: Implements a helper PCI driver for Atheros Owl emulation devices whose calibration/EEPROM init data is not available during early PCI quirks. It loads calibration data from nvmem or firmware after userspace is available, writes the register/value script into the device, removes the temporary PCI device, and rescans so the real ath9k device can appear with the correct product ID.

Important APIs and functions: `struct owl_ctx` stores the `pci_dev`, completion, work item, and optional nvmem cell. `ath9k_pci_fixup()` validates EEPROM data, handles byte-swapped calibration blobs, maps BAR0, temporarily enables memory/master PCI command bits, writes register/value pairs until a `0xffff` terminator, restores BAR0/command state, unmaps, and disables the device. `owl_rescan()` stops/removes the temporary device and rescans the bus. `owl_fw_cb()` handles asynchronous firmware completion. `owl_get_eeprom_name()` builds the `ath9k-eeprom-pci-%s.bin` firmware name. `owl_nvmem_work()` reads the `calibration` nvmem cell and applies it. `owl_nvmem_probe()` chooses nvmem or firmware fallback. `owl_probe()` initializes the context and starts loading. `owl_remove()` waits for the load completion. The PCI ID table matches Atheros `0xff1c` and `0xff1d` emulation IDs.

Control flow: Probe first enables the PCI device and allocates a devm context. It tries `devm_nvmem_cell_get("calibration")`; if present, it schedules work that completes the load marker, reads the cell, applies the fixup, frees the buffer, and rescans. If nvmem is absent or unsupported, probe builds the firmware filename and calls `request_firmware_nowait()`. The firmware callback completes the marker, applies the same fixup when data exists, rescans, reports missing data otherwise, and releases the firmware. Remove waits for the completion before clearing drvdata so asynchronous work/callbacks do not outlive the device context.

State and persistence: Runtime state is per-device `owl_ctx`, the completion used as a removal barrier, and the nvmem work item. `ath9k_pci_fixup()` temporarily mutates PCI BAR0 and command register state and writes device registers from calibration data; it restores BAR0 and disables memory/master before disabling the device. The durable calibration source remains firmware storage or nvmem; this module does not write persistent storage.

Dependencies and integration points: Uses Linux PCI core, firmware loader, nvmem consumer API, workqueues, completions, delays, and I/O mapping. It integrates with ath9k's firmware naming convention from `init.c`, platform nvmem descriptions for calibration cells, PCI rescan/remove locking, and later binding by the normal ath9k PCI driver once the device reports the proper ID.

Risks: `ath9k_pci_fixup()` trusts the calibration blob format after size/magic checks; malformed register scripts could write unintended BAR offsets until the terminator is reached. The loop compares against `cal_end` while reading a packed record, so boundary correctness depends on the earlier even-size and max-size validation. Endianness handling uses both 16-bit and halfword-swapped 32-bit conversion. The completion is signaled before fixup/rescan work, so remove can wait only until the callback/work has started past the completion point, not necessarily until every side effect is finished. PCI config restoration and bus rescan ordering are critical because the device is intentionally removed during probe-time recovery.

Test signals: Test nvmem calibration path, firmware fallback path, missing firmware, invalid size, invalid magic, byte-swapped magic, register-script terminator handling, PCI BAR/command restoration, device disable, remove while firmware request or nvmem work is pending, and final rescan/bind of the normal ath9k PCI driver on devices such as Meraki Z1-style platforms.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/ath9k_pci_owl_loader.c -->
