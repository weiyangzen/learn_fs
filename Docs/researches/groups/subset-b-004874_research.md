# Research: subset-b-004874 rtl8xxxu chip subdrivers

This grouped report covers five Realtek rtl8xxxu chip-specific source files. Each section is delimited for reconciliation into the required source-tree-aligned per-file research document.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtl8xxxu/8192c.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtl8xxxu/8192c.c

## Purpose

`8192c.c` supplies the RTL8XXXU chip operations for the older generation RTL8188C/8188R/8191C/8192C USB WLAN family. The entire file is guarded by `CONFIG_RTL8XXXU_UNTESTED`, so the compiled driver only includes these callbacks when untested chip support is enabled. It is a hardware-programming shim: it binds static MAC/RF/power tables and chip-specific identify, EFUSE, firmware, power, RF-init, and LED callbacks into `rtl8192cu_fops` for the core USB/mac80211 driver.

## Important APIs, Types, and Functions

- `rtl8192cu_fops` is the exported `struct rtl8xxxu_fileops` instance consumed through USB ID table `driver_info` in `core.c`.
- `rtl8192cu_identify_chip()` reads `REG_SYS_CFG`, `REG_HPON_FSM`, and `REG_GPIO_OUTSTS` to distinguish 8188CU, 8188RU, 8191CU, and 8192CU characteristics, set path counts, vendor, ROM revision, USB interrupt use, and endpoint topology.
- `rtl8192cu_parse_efuse()` validates EFUSE ID `0x8129`, copies MAC address and gen1 TX-power arrays, assigns `priv->power_base`, and detects 8188RU high-power/no-PAPE mode from `rf_regulatory`.
- `rtl8192cu_load_firmware()` selects firmware by vendor/cut/chip: TMSC, UMC cut B/8192C, or UMC cut A.
- `rtl8192cu_init_phy_rf()` selects RF init tables for RTL8188R high-PA, 1T, or 2T and initializes RF_A and optionally RF_B through `rtl8xxxu_init_phy_rf()`.
- `rtl8192cu_power_on()` and `rtl8192cu_power_off()` implement the chip power state sequence using `REG_APS_FSMCO`, `REG_SYS_ISO_CTRL`, `REG_CR`, firmware/MCU registers, GPIO mux registers, and an 8188RU LNA-leakage workaround.
- `rtl8192cu_led_brightness_set()` maps `LED_OFF`, `LED_ON`, and `RTL8XXXU_HW_LED_CONTROL` to `REG_LEDCFG0`.

## Control Flow and Integration

Core probe assigns this fileops table, calls `identify_chip`, reads and parses EFUSE, loads firmware, then `rtl8xxxu_init_device()` calls the power, LLT, PHY, RF, calibration, aggregation, and descriptor callbacks. Most active runtime behavior is shared gen1 core code: channel setup, IQ calibration, TX power, rate mask, RX descriptor parsing, PHY stats, RF enable/disable, USB quirks, TX descriptor fill, connect/RSSI reports, and aggregation.

The chip-specific flow is front-loaded. Identification determines path counts and endpoint mapping, EFUSE parsing fills `priv` fields later used by gen1 TX-power code, firmware choice depends on vendor/cut state, and RF init table choice depends on the detected package/path count. Power-on polls hardware FSM bits before enabling MAC DMA/WMAC/scheduler/security blocks; power-off reverses this, pauses TX, powers down RF AFE/BB, handles firmware/8051 reset if firmware was running, disables GPIO/analog, and locks power-control registers.

## State and Persistence Behavior

The file persists hardware-derived state in `struct rtl8xxxu_priv`: `chip_name`, `rtl_chip`, `chip_cut`, path counts, `usb_interrupts`, `has_wifi`, vendor flags, `rom_rev`, `mac_addr`, TX-power arrays, high-PA/no-PAPE flags, and `power_base`. The driver does not persist state outside kernel memory; all durable device configuration comes from EFUSE and firmware files. Runtime state is embodied in device registers and restored by re-running init sequences after probe or reset.

## Dependencies

This file depends on `regs.h` register definitions, `rtl8xxxu.h` types and helper prototypes, gen1 core helpers, Linux USB/mac80211/LED infrastructure, firmware blobs under `rtlwifi/`, and EFUSE structure layout `rtl8192cu_efuse`. RF and MAC tables must match Realtek hardware programming expectations and are terminated by sentinel values.

## Risks and Edge Cases

- Build coverage is explicitly limited by `CONFIG_RTL8XXXU_UNTESTED`; normal builds may not compile this path.
- Wrong chip identification affects TX/RX path count, endpoint selection, firmware, and RF tables.
- EFUSE ID mismatch returns `-EINVAL`, preventing probe.
- Power sequencing depends on polling loops without sleeps in some loops; hardware that never clears bits returns `-ENODEV` or `-EBUSY`.
- 8188RU mode mutates the chip identity after EFUSE parse and applies high-PA/no-PAPE and LNA leakage workarounds; regression risk is concentrated there.
- RF init uses one table for multiple chip/package variants; bad table choice can silently degrade RF performance.

## Test Signals

Useful signals include successful module build with `CONFIG_RTL8XXXU_UNTESTED`, probe logs showing chip/vendor/ROM revision and no fatal identify/EFUSE/firmware errors, firmware request success for all selected firmware names, endpoint count fallback coverage, successful power-on/off suspend-remove cycles, RF path count matching hardware, LED mode transitions on `REG_LEDCFG0`, and TX/RX traffic on 1T and 2T devices. Hardware validation should include 8188RU because it has special power-base and leakage handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtl8xxxu/8192c.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtl8xxxu/8192e.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtl8xxxu/8192e.c

## Purpose

`8192e.c` implements RTL8191EU/RTL8192EU support for the rtl8xxxu USB mac80211 driver. It provides gen2 chip operations, register initialization tables, AGC variants, RF tables, EFUSE decoding, custom TX-power programming, PHY/LC/IQ calibration, power sequencing, RF enable behavior, CCK RSSI conversion, and LED control through `rtl8192eu_fops`.

## Important APIs, Types, and Functions

- `rtl8192eu_fops` exports the fileops table for the core driver, with 24-byte RX descriptors, 40-byte TX descriptors, gen2 rate/connect/RSSI callbacks, auto LLT, gen2 USB quirks, and AP support.
- `rtl8192eu_identify_chip()` reads `REG_SYS_CFG` and `REG_HPON_FSM` to distinguish 1T `8191EU` from 2T `8192EU`, rejects test chips, records vendor/ROM revision, and configures endpoints using SIE with fallback.
- `rtl8192eu_parse_efuse()` validates EFUSE ID `0x8129`, copies MAC address and A/B base power arrays, normalizes OFDM/HT20/HT40 power diffs into `priv`, and stores default crystal cap from `xtal_k`.
- `rtl8192e_set_tx_power()` computes channel group power for CCK, OFDM, and MCS rates and writes A/B TX AGC registers, respecting `tx_paths`.
- `rtl8192eu_init_phy_bb()` enables BB/RF blocks, loads `rtl8192eu_phy_init_table`, then selects standard or high-PA AGC table based on `priv->hi_pa`.
- `rtl8192eu_init_phy_rf()` loads RF_A and RF_B tables.
- IQK helpers (`rtl8192eu_iqk_path_a/b`, RX variants, `rtl8192eu_phy_iqcalibrate()`, `rtl8192eu_phy_iq_calibrate()`) perform multi-pass TX/RX IQ calibration, compare candidate results, fill IQK matrices, and save recovery BB registers.
- Power helpers (`rtl8192e_disabled_to_emu()`, `rtl8192e_emu_to_active()`, `rtl8192eu_active_to_lps()`, `rtl8192eu_active_to_emu()`, `rtl8192eu_emu_to_disabled()`) stage transitions used by `rtl8192eu_power_on()` and `rtl8192eu_power_off()`.
- `rtl8192e_enable_rf()` configures RX wait CCA, GPIO mux, PTA action, RFE buffers, antenna source, LED config, pad control, and clears TX pause.
- `rtl8192e_cck_rssi()` maps CCK AGC report fields through one of two LNA tables.

## Control Flow and Integration

Probe-time flow is identify, EFUSE read/parse, firmware load (`rtlwifi/rtl8192eu_nic.bin`), then full device init. `power_on()` adjusts LDO/SWR voltage based on `SYS_CFG_SPS_LDO_SEL`, tunes AFE crystal/PLL bits, enters active state by polling APS FSM readiness and MAC enable completion, clears `REG_CR`, and enables HCI/Tx/Rx/protocol/scheduler/security/calibration timer blocks.

PHY init enables BB/RF resets, loads large BB/AGC register scripts, then initializes both RF paths. IQ calibration saves ADDA, MAC, and BB registers on the first pass, runs path A and B TX/RX IQK up to two retries per pass, repeats for up to three result sets, chooses a similar candidate with `rtl8xxxu_gen2_simularity_compare()`, writes IQK correction matrices, restores saved state, and saves BB recovery registers for later resets.

Power-off flushes FIFO, disables TX reports and RF, moves active to low-power state, resets firmware if running from RAM, disables the MCU, resets firmware-ready state, calls generic 8051 reset, and moves active-to-emu-to-disabled.

## State and Persistence Behavior

Persistent runtime state is held in `rtl8xxxu_priv`: chip identity, path counts, vendor flags, endpoint counts, EFUSE-derived MAC/TX-power/crystal values, calibration backups (`adda_backup`, `mac_backup`, `bb_backup`, `bb_recovery_backup`), IQK result fields (`rege94`, `rege9c`, `regeb4`, `regebc`), and CFO crystal cap tracking. The file writes hardware registers extensively but has no disk persistence. Firmware is loaded externally from the kernel firmware path.

## Dependencies

The file depends on rtl8xxxu core register IO helpers, gen2 shared helpers, EFUSE layout `rtl8192eu_efuse`, `rtl8723a_phy_lc_calibrate()` and `rtl8723a_set_crystal_cap()` shared with 8723A, Linux LED class support, and the `rtlwifi/rtl8192eu_nic.bin` firmware. Optional compile-time `EXT_PA_8192EU` changes PHY/RF/AGC programming.

## Risks and Edge Cases

- `path_b_ok` in calibration is only meaningful when RF path B executes; path-count mistakes can corrupt calibration assumptions.
- EFUSE power-diff indexing assumes `RTL8723B_TX_COUNT` layout; malformed or all-`0xff` EFUSE data can produce unrealistic TX power.
- Poll loops in power transitions return `-EBUSY`; failure paths leave partial hardware state that relies on core cleanup.
- `rtl8192e_enable_rf()` includes board-specific RFE and transmission-failure fixes; changes risk RF switch or TX regressions.
- EXT_PA and `priv->hi_pa` variants need separate validation because they select different AGC/PHY constants.
- CCK RSSI depends on `cck_agc_report_type`; wrong type yields inaccurate signal reporting rather than obvious probe failure.

## Test Signals

Check build coverage, probe success for both 8191EU and 8192EU bonding, firmware load success, correct endpoint fallback behavior, `iw` scan/association and AP mode, TX power programming on HT20/HT40 and both TX paths, suspend/remove power-off without timeout warnings, IQK debug logs without persistent path failures, CCK RSSI sanity against expected signal strength, and LED behavior through software and hardware LED modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtl8xxxu/8192e.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtl8xxxu/8192f.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtl8xxxu/8192f.c

## Purpose

`8192f.c` implements RTL8192FU support. It is a newer gen2/Jaguar2-style two-stream USB WLAN subdriver with larger register scripts, 7-bit TX AGC writes, custom channel handling, RFE-type-sensitive IQ calibration, kfree EFUSE power trimming, chip-specific power sequencing, 8051 reset, crystal-cap control, CCK RSSI conversion, and dual LED GPIO support.

## Important APIs, Types, and Functions

- `rtl8192fu_fops` is the fileops export with tx report support, full init, init of RX filter/pkt lifetime/HMTFR, burst init, Jaguar2 PHY stats, 24-byte RX descriptors, 40-byte TX descriptors, 256-byte page buffers, and AP support.
- `rtl8192fu_identify_chip()` sets fixed 2x2 `RTL8192F` identity, reads multi-function WiFi/BT/GPS flags, rejects test chips, records vendor/ROM revision, and uses no-SIE endpoint config.
- `rtl8192fu_parse_efuse()` validates ID `0x8129`, copies A/B power bases and diffs, sets crystal cap and `rfe_type`, and warns for untested RFE types other than 1 and 5.
- `rtl8192f_set_tx_power()` writes masked 7-bit CCK/OFDM/MCS AGC values for RF_A/RF_B using `rtl8188f_channel_to_group()`.
- `rtl8192f_revise_cck_tx_psf()` adjusts CCK filter registers for channels 13 and 14 and must stay synchronized with the PHY init table.
- `rtl8192fu_config_kfree()` reads EFUSE offsets `0x1ee`, `0x1ec`, and `0x1ea` and writes per-channel-group BB gain trims into RF debug/power-trim registers.
- `rtl8192fu_config_channel()` handles HT20/HT40 channel/subchannel selection, CCK filter revision, RF channel/bandwidth, kfree trim, ADC/DAC clocking, sideband, CCK enable, and RX DFIR parameters.
- `rtl8192fu_init_phy_bb()` and `rtl8192fu_init_phy_rf()` load BB/AGC and RF_A/RF_B tables.
- `rtl8192f_phy_lc_calibrate()` wraps shared 8188F LC calibration while preserving Aries narrowband bits and resetting OFDM state.
- IQK helpers implement path A/B TX/RX IQK with report polling, RFE-specific PA/PAD settings, LUT reloads, multi-pass candidate selection, IQK matrix fill, and restoration of RF/RFE state.
- Power helpers implement disabled/emu/active/LPS transitions and `rtl8192f_reset_8051()`.
- `rtl8192f_usb_quirks()`, `rtl8192f_set_crystal_cap()`, `rtl8192f_cck_rssi()`, and `rtl8192fu_led_brightness_set()` provide post-generic USB enable, CFO crystal adjustment, Jaguar2 CCK RSSI conversion, and board-observed LED programming.

## Control Flow and Integration

The core driver uses the fileops table after matching RTL8192FU USB IDs. Probe establishes chip identity, EFUSE state, firmware `rtlwifi/rtl8192fufw.bin`, and device init. Runtime channel changes call `rtl8192fu_config_channel()`, not the generic gen2 channel routine, because 8192F needs channel 13/14 filter tweaks, kfree power trim, and custom DFIR/clock/RF bandwidth programming.

Power-on starts by setting USB access timeout, clearing disabled/suspend bits, enabling LDOA15 and RF/XTAL/GPIO support, polling APS FSM readiness and MAC enable, then enabling DMA/protocol/scheduler/security/calibration in `REG_CR`. Power-off flushes FIFO, disables TX report timer and RX, enters LPS, resets firmware/MCU state, and moves active-to-emu-to-disabled.

IQ calibration is extensive: it saves key analog/MAC/BB/RFE state, adjusts path/RFE switch controls for external PA variants, retries path A and B TX/RX IQK, compares up to three candidate result sets, writes correction matrices if valid, restores RF registers, and reapplies RFE-specific switch state for RFE 7/8/9/12.

## State and Persistence Behavior

The file stores chip identity, path counts, multifunction flags, EFUSE-derived MAC/TX power/crystal/RFE data, CFO crystal cap, calibration backups, and current IQK results in `rtl8xxxu_priv`. It also reads EFUSE kfree values at channel-change time rather than caching them. Register writes are volatile and replayed by initialization. No local disk persistence exists beyond firmware dependency.

## Dependencies

It depends on rtl8xxxu core helpers, 8188F shared helpers (`rtl8188f_channel_to_group`, `rtl8188f_phy_lc_calibrate`), Jaguar2 PHY stats parser, firmware `rtlwifi/rtl8192fufw.bin`, EFUSE structure `rtl8192fu_efuse`, and numerous register/mask definitions in `regs.h`/`rtl8xxxu.h`.

## Risks and Edge Cases

- RFE types beyond 1 and 5 are warned as untested, while IQK still has branches for 7/8/9/12; board diversity is a major risk.
- `rtl8192f_revise_cck_tx_psf()` is manually coupled to the PHY table; table updates can silently stale the restore values.
- kfree EFUSE reads may return undefined values; fallback behavior depends on the middle group being defined.
- Custom power sequencing touches GPIO/interrupt/XTAL/RF path registers and can regress suspend/resume or hardware RF-off behavior.
- IQK has many restore paths; early failures may leave RF_GAIN or RFE switch registers altered if not covered by restore logic.
- LED handling writes GPIO share registers observed from Windows traffic and supports boards using different LEDs; board-specific regressions are plausible.

## Test Signals

Validate compile, firmware load, probe chip/vendor/BT/GPS flags, channel changes across 1-14 including HT40 plus/minus and channels 13/14, TX power on both RF paths, kfree EFUSE fallback, RFE type warning coverage, scan/association/AP traffic, TX report operation, suspend/remove cycles, IQK warnings, CCK RSSI plausibility with Jaguar2 stats, and LED behavior on boards using LED0 and LED1.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtl8xxxu/8192f.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtl8xxxu/8710b.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtl8xxxu/8710b.c

## Purpose

`8710b.c` implements RTL8710BU, also identified in comments as 8188GU, support. It is a 1x1 gen2/Jaguar2-style USB WLAN subdriver with package-specific PHY/RF tables, indirect SYSON/EFUSE register access, vendor/package-driven firmware selection, custom EFUSE parser, channel and calibration handling, statistics setup, power sequencing, RF control, crystal-cap handling, and RSSI conversion.

## Important APIs, Types, and Functions

- `rtl8710bu_fops` exports the chip fileops with custom EFUSE read, package-specific PHY/RF init, Jaguar2 stats, NHM/statistics init, tx report support, 24-byte RX descriptors, 40-byte TX descriptors, 16 MAC IDs, and AP support.
- `rtl8710b_indirect_read32()` and `rtl8710b_indirect_write32()` access indirect registers via `REG_USB_HOST_INDIRECT_ADDR_8710B`, `REG_USB_HOST_INDIRECT_DATA_8710B`, and `REG_EFUSE_INDIRECT_CTRL_8710B`, serialized by `priv->syson_indirect_access_mutex`.
- `rtl8710b_read_syson_reg()` and `rtl8710b_write_syson_reg()` add the SYSON base address to indirect access.
- `rtl8710b_read_efuse8()` and `rtl8710b_read_efuse()` implement byte and logical EFUSE map reading using 8710B indirect controls and Realtek physical EFUSE packet headers.
- `rtl8710bu_identify_chip()` reads SYSON config, rejects test chips, maps vendor bits with an SMIC/TSMC swap relative to generic helper behavior, reads package type from EFUSE, infers default package if undefined, records ROM revision, and configures endpoints.
- `rtl8710bu_parse_efuse()` validates EFUSE ID `0x8195`, copies MAC and 1T power values, and sets default crystal cap.
- `rtl8710bu_load_firmware()` selects `rtl8710bufw_SMIC.bin` or `rtl8710bufw_UMC.bin`; unknown vendors fail.
- `rtl8710bu_init_phy_bb()` and `rtl8710bu_init_phy_rf()` select QFN48M_U or QFN48M_S PHY/RF tables based on `priv->package_type`.
- `rtl8710bu_config_channel()` handles 2.4 GHz channel/subchannel, CCK channel 13/14 filter fixes, WMAC bandwidth, FPGA RF mode, ADC/DAC clocking, OFDM RX DFIR, and RF bandwidth.
- `rtl8710bu_init_statistics()` programs NHM thresholds/timer and enables CCK/max-power behavior.
- IQK functions (`rtl8710bu_iqk_path_a`, RX path, `rtl8710bu_phy_iqcalibrate`, `rtl8710bu_phy_iq_calibrate`) implement one-path calibration with LOK result preservation and S0/S1 path switching.
- `rtl8710bu_power_on()` and `rtl8710bu_power_off()` handle USB timeout, isolation, WL status, hardware sequence number, CM4 suspend gating through SYSON register `0x138`, FIFO/interrupt cleanup, LPS, and MCU reset.

## Control Flow and Integration

Core probe calls the custom identify routine before normal EFUSE read/parse. Identification is unusual because it needs indirect SYSON reads and an EFUSE byte read before full EFUSE map parsing, so package and vendor are available for firmware and table selection. Full EFUSE reading then builds `priv->efuse_wifi.raw` from packetized EFUSE data, and parse fills MAC and power data.

During init, BB/RF tables are selected by package type. Channel changes use the custom 8710BU function, which is necessary because bandwidth, ADC/DAC clocking, RX DFIR, and CCK filters differ from generic gen2 routines. Power-on includes normal MAC enable plus extra CM4 suspend prevention, while power-off allows CM4 suspend and masks/clears 8710B host interrupts.

## State and Persistence Behavior

The file stores vendor flags, `package_type`, `chip_cut`, `rom_rev`, MAC address, 1T TX-power state, default crystal cap, and EFUSE raw map in `rtl8xxxu_priv`. Indirect access is protected by `syson_indirect_access_mutex`, preventing concurrent SYSON/EFUSE operations from racing. Hardware state is volatile; package/vendor decisions are derived from EFUSE/SYSON on each probe. No disk persistence exists.

## Dependencies

Dependencies include rtl8xxxu core IO helpers, shared gen2 helpers, 8188F TX power and LC calibration, Jaguar2 PHY stats, firmware files `rtlwifi/rtl8710bufw_SMIC.bin` and `rtlwifi/rtl8710bufw_UMC.bin`, 8710B-specific register definitions, EFUSE layout `rtl8710bu_efuse`, and core initialization of `syson_indirect_access_mutex`.

## Risks and Edge Cases

- Indirect reads/writes require 4-byte alignment and polling; timeout returns `0xffffffff` or logs warnings, which can cascade into wrong vendor/package/chip state.
- Unknown vendor has no firmware fallback and returns failure.
- Undefined or unexpected package type is inferred, with warnings; wrong inference selects wrong PHY/RF tables.
- EFUSE packet parsing checks map bounds but malformed EFUSE can still produce partial power/MAC state before returning.
- The file uses several literal registers (`0x20`, `0x5d`, `0xfef9`, SYSON `0x138`), making hardware revision regressions harder to spot.
- The `ustime_tsf_edca` comment documents that vendor value `0x50` caused slow upload/packet loss in rtl8xxxu, so throughput is sensitive to timing constants.

## Test Signals

Validate indirect access warnings absence, package/vendor identification logs, firmware load for SMIC and UMC parts, endpoint config, EFUSE parser success with ID `0x8195`, scan/association/AP traffic, channel 13/14 and HT40 behavior, NHM/statistics reads if available, IQK warnings, CM4 suspend bit handling across power cycles, upload throughput and packet loss around `ustime_tsf_edca`, CCK RSSI sanity, and suspend/remove cleanup with no active-to-LPS timeout.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtl8xxxu/8710b.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtl8xxxu/8723a.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtl8xxxu/8723a.c

## Purpose

`8723a.c` implements RTL8723AU support for the rtl8xxxu USB mac80211 driver. It is an older gen1 1x1 multifunction WiFi/BT/GPS chip subdriver that provides MAC/RF/power tables, chip identification, EFUSE parsing, chip-cut and Bluetooth-aware firmware selection, RF init spur reduction, power sequencing, crystal-cap control, CCK RSSI conversion, LED control, and the `rtl8723au_fops` operations table.

## Important APIs, Types, and Functions

- `rtl8723au_fops` exports gen1 fileops with 16-byte RX descriptors, v1 TX descriptors, gen1 channel/TX power/rate/report/aggregation/RF helpers, AP-related security CAM capacity, LED callback, and `rtl8723a_set_crystal_cap()`.
- `rtl8723au_identify_chip()` reads `REG_SYS_CFG`, rejects test chips, sets fixed `8723AU` identity/path counts, detects WiFi/BT/GPS multifunction flags from `REG_MULTI_FUNC_CTRL`, identifies vendor, records ROM revision, and configures endpoints with SIE fallback.
- `rtl8723au_parse_efuse()` validates EFUSE ID `0x8129`, copies MAC and gen1 power arrays, sets default crystal cap when EFUSE version supports it, disables the `set_crystal_cap` callback for older EFUSE versions, and assigns `rtl8723a_power_base`.
- `rtl8723au_load_firmware()` selects `rtl8723aufw_A.bin`, `rtl8723aufw_B.bin`, or `rtl8723aufw_B_NoBT.bin` according to chip cut and `priv->enable_bluetooth`.
- `rtl8723au_init_phy_rf()` loads the RF_A table and applies a three-write AFE PLL/XTAL sequence to reduce an 80 MHz spur.
- `rtl8723a_emu_to_active()`, `rtl8723au_power_on()`, `rtl8723au_active_to_emu()`, `rtl8723au_emu_to_disabled()`, and `rtl8723au_power_off()` implement the chip-specific power lifecycle.
- `rtl8723a_set_crystal_cap()` writes XTAL fields in `REG_MAC_PHY_CTRL` and updates CFO tracking.
- `rtl8723a_cck_rssi()` converts legacy CCK AGC reports into RSSI-like power.
- `rtl8723au_led_brightness_set()` controls LED software/hardware mode using `REG_LEDCFG2`.

## Control Flow and Integration

Probe binds `rtl8723au_fops`, identifies multifunction capabilities, parses EFUSE, selects firmware by cut/Bluetooth setting, then enters common rtl8xxxu init. The actual BB init, channel config, IQ calibration, LC calibration, aggregation, RF enable/disable, TX power, and descriptors use shared gen1 helpers. The file-specific path is mainly hardware state discovery, firmware selection, RF table setup, power transitions, LED/crystal/RSSI helpers, and power-base assignment for shared TX-power logic.

Power-on unlocks power registers, calls the generic disabled-to-emu step, runs the 8723A emu-to-active sequence with LDOA15, BT/GPS pin isolation, analog isolation release, APS FSM polling, WLON reset, hardware power-down/suspend clearing, MAC enable polling, and DPDT selection. It then resets 8051 through APS bits, enables DMA/protocol/scheduler/security/calibration in `REG_CR`, and sets EFUSE PG voltage bits. Power-off flushes FIFO, enters shared LPS, turns RF off, resets firmware/MCU state, moves active-to-emu-to-disabled, resets the MCU IO wrapper, and relocks power-control registers.

## State and Persistence Behavior

The file persists detected chip, path count, multifunction flags, endpoint config, vendor, ROM revision, MAC, power arrays, default crystal cap, and power base in `rtl8xxxu_priv`. It can mutate `priv->fops->set_crystal_cap` to `NULL` when older EFUSE data lacks crystal trim support, which changes later CFO behavior globally for that device's fileops instance. Hardware register state is volatile and reconstructed during init/power transitions. Firmware is external.

## Dependencies

Dependencies include `regs.h`, `rtl8xxxu.h`, shared gen1 rtl8xxxu helpers, EFUSE layout `rtl8723au_efuse`, firmware files under `rtlwifi/`, Linux LED class support, and core CFO tracking. It shares helper functions with other gen1 files: `rtl8723a_phy_lc_calibrate`, `rtl8xxxu_gen1_phy_iq_calibrate`, `rtl8xxxu_gen1_config_channel`, and gen1 TX power.

## Risks and Edge Cases

- Mutating `priv->fops->set_crystal_cap` is risky because fileops tables are global static objects; if multiple devices with different EFUSE versions coexist, callback state could leak across devices.
- Firmware selection only accepts chip cut 0 or 1; other cuts fail with `-EINVAL`.
- Bluetooth enable state changes firmware choice for cut B, so coexistence regressions can come from wrong `enable_bluetooth`.
- Power transitions depend on APS FSM polling and many literal hardware bits; timeout leaves partially initialized hardware.
- The DPDT code documents a mismatch between vendor documentation and observed behavior, suggesting fragility around antenna/RF switch control.
- Older gen1 shared helpers do most RF/channel/TX power behavior, so problems may surface outside this file.

## Test Signals

Validate probe on cut A and cut B devices, firmware selection with Bluetooth enabled and disabled, multifunction flags, EFUSE version paths including old-version crystal-cap disable, scan/association traffic, suspend/remove cycles without MAC disable timeouts, RF spur/noise behavior after init, LED software and hardware modes, CCK RSSI sanity, and multi-device testing focused on the global `fops->set_crystal_cap` mutation risk.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtl8xxxu/8723a.c -->
