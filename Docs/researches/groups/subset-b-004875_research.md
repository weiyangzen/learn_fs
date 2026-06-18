# subset-b-004875 research

Work item: `subset-b-004875`

This grouped report covers the rtl8xxxu RTL8723BU chip support files in source-tree order. Each file section is wrapped for reconciliation into the required per-file research document.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtl8xxxu/8723b.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtl8xxxu/8723b.c

## Purpose

`8723b.c` is the RTL8723BU-specific implementation for the shared `rtl8xxxu` mac80211 USB wireless driver. It supplies chip identification, efuse parsing, firmware selection, PHY/RF initialization tables, calibration routines, power sequencing, RF/BT coexistence setup, RSSI interpretation, LED control, and a populated `struct rtl8xxxu_fileops rtl8723bu_fops` vtable consumed by the common driver core.

The file is not a standalone driver. Device matching and mac80211/USB plumbing live in `core.c`; this file provides the hardware personality for Realtek RTL8723B USB parts, especially one-transmit/one-receive-path 8723BU devices with Bluetooth coexistence hardware.

## Important APIs, Types, and Data

- `struct rtl8xxxu_fileops rtl8723bu_fops` is the exported integration point. `core.c` installs a pointer to this table from USB device IDs and calls its callbacks throughout probe, start, stop, channel configuration, RX/TX, LED, and calibration paths.
- `struct rtl8xxxu_priv` is the persistent device state carrier. This file writes chip identity fields, path counts, feature flags, efuse-derived power tables, calibration backups/results, firmware capability state, MAC address, and LED container state through it.
- `struct rtl8723bu_efuse` and `struct rtl8723bu_efuse_tx_power` describe the 8723BU efuse layout used by `rtl8723bu_parse_efuse()`.
- `struct h2c_cmd` is used to send host-to-controller firmware commands for Bluetooth MP register writes, BT grant, antenna selection reservation, BT info, and ignore-WLAN-action control.
- Static hardware tables drive most bring-up: `rtl8723b_mac_init_table`, `rtl8723b_phy_1t_init_table`, `rtl8xxx_agc_8723bu_table`, and `rtl8723bu_radioa_1t_init_table`.
- Register and bit definitions come from `regs.h`; shared rtl8xxxu helpers and type definitions come from `rtl8xxxu.h`.

Key local functions:

- `rtl8723bu_identify_chip()` reads `REG_SYS_CFG`, rejects test chips, records chip name/type/path counts/multifunction flags/vendor/ROM revision, and configures USB endpoints from SIE data or fallback probing.
- `rtl8723bu_parse_efuse()` validates efuse `rtl_id == 0x8129`, copies the MAC address, fills CCK/HT40 power base arrays and OFDM/HT20/HT40 power diffs, and records the default crystal capacitor.
- `rtl8723bu_load_firmware()` selects `rtlwifi/rtl8723bu_bt.bin` when Bluetooth firmware is enabled and `rtlwifi/rtl8723bu_nic.bin` otherwise.
- `rtl8723bu_init_phy_bb()` and `rtl8723bu_init_phy_rf()` bring baseband/RF blocks out of reset, apply PHY/AGC/RF tables, and perform an RF local calibration sequence.
- `rtl8723bu_phy_iq_calibrate()` orchestrates repeated IQ calibration attempts and calls lower-level TX/RX path-A calibration helpers.
- `rtl8723bu_power_on()`, `rtl8723bu_power_off()`, `rtl8723b_emu_to_active()`, and `rtl8723bu_active_to_emu()` implement the chip power state transitions used by the common lifecycle.
- `rtl8723b_enable_rf()` performs RF enablement, antenna switch setup, and initial BT coexistence firmware/register programming.
- `rtl8723b_set_tx_power()` programs per-rate TX AGC registers from efuse-derived channel-group power indexes.
- `rtl8723b_cck_rssi()` maps the 8723B CCK AGC report format into an RSSI-like receive power estimate.
- `rtl8723bu_led_brightness_set()` implements Linux LED class brightness operations by programming `REG_LEDCFG2`.

## Control Flow

Probe and initialization flow is driven from the common rtl8xxxu core:

1. USB device matching selects `rtl8723bu_fops`.
2. The core calls `.identify_chip`, which reads system configuration, sets `RTL8723B`, declares one RF/RX/TX path, records WiFi/BT/GPS multifunction capabilities, identifies the vendor, reads ROM revision, and configures endpoints.
3. The core reads efuse via shared `.read_efuse = rtl8xxxu_read_efuse`, then invokes `.parse_efuse` to load MAC address, TX power indexes, power diffs, and crystal trim into `priv`.
4. `.load_firmware` selects the NIC or BT-capable 8723BU firmware image according to `priv->enable_bluetooth`.
5. `.power_on` moves hardware from disabled/EMU to active, enables DMA/WMAC/scheduler/security/calibration timer bits, and applies early BT coexistence and antenna-switch register values.
6. `.init_phy_bb`, `.init_phy_rf`, `.phy_lc_calibrate`, `.phy_iq_calibrate`, `.init_aggregation`, `.init_statistics`, `.init_burst`, and `.enable_rf` prepare radio operation.
7. Runtime channel changes and association reporting mostly use shared gen2 callbacks; this file contributes TX power programming, CCK RSSI decoding, LED brightness control, and 8723BU-specific RF/coexistence setup.
8. Shutdown calls `.power_off`, which flushes FIFOs, disables TX report timing and MAC blocks, enters LPS, resets firmware/MCU state, transitions active-to-EMU, and enables GPIO9 wake behavior.

Calibration has an internal retry/candidate flow:

- `rtl8723bu_phy_iq_calibrate()` prepares calibration, saves the original BT control register, clears a 4x8 result matrix, and runs up to three rounds of `rtl8723bu_phy_iqcalibrate()`.
- `rtl8723bu_phy_iqcalibrate()` saves ADDA/MAC/BB state on the first pass, turns ADDA on, adjusts MAC/BB/RF IQK settings, retries TX path-A IQK and RX path-A IQK twice, stores successful register results, and restores backed-up state on the final pass.
- `rtl8723bu_phy_iq_calibrate()` chooses a candidate by comparing result similarity across attempts, fills IQK correction matrices for path A and conditionally path B, backs up recovery BB registers, restores BT control, programs final RF tuning values, and exits calibration mode.
- Path B code is present only in a disabled `#if 0` block; active code warns that path B is not supported if multi-path hardware is reported.

## State and Persistence Behavior

This file persists device-specific state only in memory and hardware/firmware registers; it does not write files or durable storage.

- Efuse state is read from device nonvolatile storage by the shared reader and parsed here into `priv->mac_addr`, `cck_tx_power_index_*`, `ht40_1s_tx_power_index_*`, `ofdm_tx_power_diff`, `ht20_tx_power_diff`, `ht40_tx_power_diff`, and `default_crystal_cap`.
- Identification persists in `priv->chip_name`, `priv->rtl_chip`, `priv->chip_cut`, `priv->rf_paths`, `priv->rx_paths`, `priv->tx_paths`, multifunction flags, vendor info, `rom_rev`, and endpoint fields.
- Calibration writes transient hardware state, saves/restores register snapshots in `priv->adda_backup`, `priv->mac_backup`, `priv->bb_backup`, and stores selected IQK results in `priv->rege94`, `priv->rege9c`, `priv->regeb4`, and `priv->regebc`.
- Power-state functions mutate MAC, RF, analog isolation, LDO, GPIO interrupt, firmware download, and wake registers. Those changes persist in hardware until subsequent driver actions or device reset.
- Firmware choice depends on `priv->enable_bluetooth`; H2C commands program firmware runtime behavior for BT coexistence and antenna control.

## Dependencies and Integration Points

- Depends on the Linux USB, mac80211, firmware loader, LED class, bitfield, delay, and networking support included by the surrounding driver.
- Depends on shared rtl8xxxu helpers for MMIO/USB register reads and writes, RF register access, efuse reading, firmware loading, H2C command transport, endpoint discovery, LLT initialization, gen2 rate/report/channel/RX/TX descriptor logic, calibration helpers, and RF disable/USB quirks.
- Integrates with `core.c` through `rtl8723bu_fops`; the common core advertises the required firmware names, maps RTL8723BU USB IDs to this fops table, and handles C2H BT coexistence messages that complement the setup in this file.
- `rtl8723bu_phy_init_antenna_selection()` is non-static and reused by another chip implementation (`8188f.c`), so changes to it can affect more than RTL8723BU.
- BT coexistence setup interacts with shared functions such as `rtl8723bu_set_ps_tdma()` and core-side BT info/inquiry handlers.
- Build integration is through the local Makefile, which always includes `8723b.o` in `rtl8xxxu-y` when `CONFIG_RTL8XXXU` is enabled.

## Risks and Edge Cases

- Hardware sequencing is register-literal heavy. Small changes can break bring-up, RF switching, power transitions, or coexistence without compile-time signals.
- `rtl8723bu_identify_chip()` rejects test chips via `SYS_CFG_TRP_VAUX_EN`; endpoint fallback is necessary for devices lacking normal SIE endpoint data.
- `rtl8723bu_parse_efuse()` requires efuse ID `0x8129`; bad or unexpected efuse data aborts initialization with `-EINVAL`.
- TX power programming uses path B efuse arrays and `.b` diffs despite this chip being configured as one path. This matches existing layout/use, but it is a sensitive area for regulatory and RF performance behavior.
- IQ calibration has many magic thresholds and temporarily disables/restores IQK/BT-control-related state. Failures are mostly debug logged and fall back to default matrix values, which may reduce RF quality rather than fail probe.
- Path B support is incomplete/disabled, so a future 2T variant reporting more than one path would warn and likely be under-supported.
- `rtl8723b_emu_to_active()` reads `REG_APS_FSMCO` with an 8-bit accessor into a 32-bit variable before clearing `APS_FSMCO_SW_LPS`; this mirrors existing code but is worth care if modifying the power sequence.
- Several comments explicitly note unknown vendor-register behavior (`0x0790`, `0x0778`, bits in `0x0974`, package-type conditions). These should be treated as hardware compatibility constraints.
- LED control preserves only `LEDCFG2_DPDT_SELECT` from the existing register and rewrites software/hardware LED mode bits; board-specific LED behavior can regress if assumptions differ.
- Bluetooth coexistence uses H2C commands and direct registers. Reordering can affect PTA behavior, antenna ownership, or BT/WiFi mutual interference.

## Test Signals

- Compile coverage: build the kernel module with `CONFIG_RTL8XXXU=m` and ensure `8723b.o` is linked into `rtl8xxxu.o` without warnings.
- Firmware coverage: boot/probe with RTL8723BU hardware and verify the requested firmware path is available (`rtlwifi/rtl8723bu_nic.bin` or `rtlwifi/rtl8723bu_bt.bin`).
- Probe signals: dmesg should show successful chip identification, endpoint configuration, efuse parsing, firmware load, and no "Unsupported test chip", efuse `-EINVAL`, or MAC disable/power-ready timeout warnings.
- Runtime RF signals: scan, associate, ping, throughput, RSSI reporting, LED behavior, suspend/resume or unplug/replug, and AP mode if supported.
- BT coexistence signals: with combo devices, test WiFi traffic during Bluetooth inquiry/audio/input activity and watch for C2H BT info handling, link stability, and antenna switching regressions.
- Calibration signals: enable dynamic debug around rtl8xxxu and inspect IQK candidate/failure debug output; compare RSSI/throughput before and after calibration-sensitive changes.
- Static review signals: changes to register tables, power sequencing, H2C command layout, or efuse parsing should be reviewed against vendor programming sequences and neighboring chip implementations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtl8xxxu/8723b.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtl8xxxu/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtl8xxxu/Kconfig

## Purpose

This Kconfig file exposes build-time configuration for the `rtl8xxxu` Realtek 802.11n USB wireless driver. It defines the main `RTL8XXXU` tristate option and a subordinate `RTL8XXXU_UNTESTED` boolean that expands device detection to untested Realtek USB IDs.

## Important Symbols

- `config RTL8XXXU`: enables built-in or module compilation of the mac80211-based Realtek RTL8XXX USB driver. The resulting module name is `rtl8xxxu`.
- `depends on MAC80211 && USB`: requires the mac80211 stack and USB support.
- `depends on LEDS_CLASS`: requires LED class support because the driver exposes LED class device behavior through fileops such as the RTL8723BU brightness setter.
- `config RTL8XXXU_UNTESTED`: optional experimental detection path for untested 8723/8188/8191/8192 WiFi USB devices.
- `depends on RTL8XXXU`: the untested-device switch is only visible when the base driver is enabled.

## Control Flow and Build Behavior

Kconfig does not execute runtime logic. Its control effect is at kernel configuration time:

1. If `RTL8XXXU=n`, the driver objects listed in the Makefile are not built and no rtl8xxxu USB IDs are registered.
2. If `RTL8XXXU=m`, the objects are linked into `rtl8xxxu.ko`.
3. If `RTL8XXXU=y`, the same driver is built into the kernel image.
4. If `RTL8XXXU_UNTESTED=y`, `core.c` compiles additional USB ID table entries guarded by `CONFIG_RTL8XXXU_UNTESTED`, increasing hardware match coverage.

## State and Persistence Behavior

The selected values are stored in the generated kernel `.config` and propagated as preprocessor/build variables. They do not create runtime persistence by themselves, but they determine whether the driver is present and whether experimental IDs are compiled in.

## Dependencies and Integration Points

- Integrates with the kernel Kconfig system under the wireless Realtek driver tree.
- Feeds `CONFIG_RTL8XXXU` into the local Makefile so `rtl8xxxu.o` is produced.
- Feeds `CONFIG_RTL8XXXU_UNTESTED` into source conditionals, notably the USB device ID list in `core.c` and chip files with untested-specific ID guards.
- The help text documents coexistence with the older `rtlwifi` driver; operational module binding may still need user control if multiple drivers can match related hardware.

## Risks and Edge Cases

- `LEDS_CLASS` is a hard dependency. Minimal configurations without LED class support cannot build this driver even if LED functionality is not operationally important for a target board.
- Enabling `RTL8XXXU_UNTESTED` can make the driver bind to hardware whose register sequences, efuse layout, or RF frontend have not been validated, increasing probe or runtime regression risk.
- The help text says the driver lacks 40 MHz channel and power-management support. Users enabling it should not infer feature parity with vendor drivers.
- Coexistence with `rtlwifi` is possible but not automatic policy. Module alias ordering, blacklists, or manual binding may be needed to choose one driver.
- The help text has historical chip-list wording and should be kept aligned with actual USB IDs and fileops support when chips are added or removed.

## Test Signals

- Run Kconfig dependency checks through a kernel build configuration with `RTL8XXXU=m` and verify `rtl8xxxu.ko` is produced.
- Verify that disabling `MAC80211`, `USB`, or `LEDS_CLASS` hides or prevents the base option as expected.
- Compare USB device alias output with `RTL8XXXU_UNTESTED=n` and `y` to confirm experimental IDs are gated.
- Smoke-test module loading on systems where `rtlwifi` could also bind and confirm the expected module owns the USB interface.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtl8xxxu/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtl8xxxu/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtl8xxxu/Makefile

## Purpose

This Makefile wires the rtl8xxxu driver objects into the Linux kernel build. When `CONFIG_RTL8XXXU` is enabled, it builds one composite object, `rtl8xxxu.o`, from the common core and all listed chip-specific implementation files.

## Important Build Rules

- `obj-$(CONFIG_RTL8XXXU) += rtl8xxxu.o` includes the composite object when the Kconfig symbol is built-in or modular.
- `rtl8xxxu-y := core.o 8192e.o 8723b.o 8723a.o 8192c.o 8188f.o 8188e.o 8710b.o 8192f.o` defines the members of the composite driver object.
- `8723b.o` is therefore always compiled into the driver whenever `RTL8XXXU` is enabled; there is no separate chip-level Kconfig switch for RTL8723BU support.

## Control Flow and Build Behavior

Kbuild expands `obj-$(CONFIG_RTL8XXXU)` according to the selected Kconfig value:

1. `CONFIG_RTL8XXXU=n`: no object is emitted from this directory for rtl8xxxu.
2. `CONFIG_RTL8XXXU=m`: Kbuild compiles all `rtl8xxxu-y` members and links them into `rtl8xxxu.ko`.
3. `CONFIG_RTL8XXXU=y`: Kbuild compiles the same members into a built-in driver object.

Runtime chip dispatch is not controlled by this Makefile. All listed chip implementations are present in the compiled driver, and USB device matching in `core.c` chooses the appropriate `struct rtl8xxxu_fileops` table.

## State and Persistence Behavior

The Makefile has no runtime state. Its persistent effect is in build artifacts: object files, the linked module or built-in object, generated module metadata, and any module aliases derived from the compiled source.

## Dependencies and Integration Points

- Consumes `CONFIG_RTL8XXXU` from the adjacent Kconfig file.
- Integrates with Linux Kbuild composite-object semantics through the `rtl8xxxu-y` variable.
- Requires every listed object to compile and resolve symbols together. For example, `8723b.o` exports `rtl8723bu_fops`, while `core.o` references it through extern declarations and USB ID `driver_info`.
- Chip files share helper symbols from `core.o` and declarations in `rtl8xxxu.h`; ordering in `rtl8xxxu-y` does not express runtime order, only link membership.

## Risks and Edge Cases

- Adding a new chip file requires both adding its object here and connecting its fops/USB IDs in source. Updating only one side causes either missing support or unresolved/unused code.
- Removing or renaming an object listed in `rtl8xxxu-y` breaks builds whenever `RTL8XXXU` is enabled.
- Because all chip implementations are compiled together, a compile error in any chip file disables the entire rtl8xxxu driver build.
- There is no fine-grained way to reduce module size by selecting only one chip family; any such split would require Kconfig and source-level restructuring.

## Test Signals

- Build with `CONFIG_RTL8XXXU=m` and confirm `rtl8xxxu.ko` contains symbols from `core.o` and chip objects including `rtl8723bu_fops`.
- Build with `CONFIG_RTL8XXXU=y` to catch built-in link differences.
- Run `modinfo rtl8xxxu` in a module build to confirm module metadata and aliases are still generated from the compiled source.
- Use incremental build tests after modifying the object list to ensure dependencies and symbol references remain valid.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtl8xxxu/Makefile -->
