# `sources/distributed-fs/ceph-client/drivers/phy/tegra/xusb-tegra186.c` Research

## Purpose

This file implements the Tegra186-family XUSB padctl backend, with shared support for Tegra186, Tegra194, and Tegra234 SoC descriptors. Compared with Tegra124/210 it focuses on USB2 UTMI and USB3 SuperSpeed pads and implements AO-register sleepwalk/wake handling for low-power USB wake. It also handles UTMI bias tracking, VBUS/ID override for role switching, fuse calibration, and minimal suspend context save/restore.

## Important APIs, Types, and Functions

- `struct tegra_xusb_fuse_calibration` stores per-USB2 HS current levels plus squelch, termination, and RPD control values.
- `struct tegra186_xusb_padctl_context` stores `vbus_id`, USB2 mux/capability, and SS capability registers across noirq suspend.
- `struct tegra186_xusb_padctl` embeds the common padctl, AO MMIO base, calibration data, USB2 tracking clock, UTMI enabled bitmap, and context.
- `tegra186_utmi_enable_phy_sleepwalk()` / `tegra186_utmi_disable_phy_sleepwalk()` program XUSB AO UTMI sleepwalk phases and wake detection.
- `tegra186_utmi_enable_phy_wake()` / `tegra186_usb3_enable_phy_wake()` set ELPG wake interrupt bits; matching disable and remote-wake-detected helpers clear/check those bits.
- `tegra186_utmi_bias_pad_power_on()` / `_off()` handle shared UTMI bias and tracking clock state.
- `tegra186_utmi_phy_set_mode()` implements OTG host/device/none transitions through ID and VBUS override helpers.
- `tegra186_usb3_phy_power_on()` programs SS port capability, optional Gen1-only speed support, and ELPG unclamp.
- Exported SoC descriptors include `tegra186_xusb_padctl_soc`, `tegra194_xusb_padctl_soc`, and `tegra234_xusb_padctl_soc`.

## Control Flow

The common padctl driver selects the SoC descriptor based on compatible strings. `tegra186_xusb_padctl_probe()` allocates the private structure, maps the `"ao"` MMIO resource, and reads fuse calibration. USB2 pad probe obtains the `trk` clock and registers UTMI PHY ops. USB3 pad probe registers SS PHY ops. Common port setup creates USB2 and USB3 ports according to the selected SoC port counts.

On UTMI power-on, the code maps the USB2 port to XUSB, sets port capability from `mode`, applies fuse-calibrated HS current/term/RPD values, and powers on the UTMI pad plus shared bias. Host-mode init enables the VBUS regulator; peripheral/OTG init resets VBUS/ID override to floating. Runtime mode changes use `PHY_MODE_USB_OTG` submodes to assert grounded ID for host, assert VBUS override for device, or clear both for none. USB3 power-on looks up its companion USB2 port, mirrors the companion role into SS port capability, optionally limits speed to Gen1 if `maximum-speed = super-speed`, and releases ELPG clamps.

For low-power wake, UTMI sleepwalk is programmed in AO registers: disable master, select low-power config, debounce lines, clear fake/wake state, save current speed, configure phased J/K/high-Z drive behavior, capture pad config, switch electrical control to XUSB_AO, program wake match, then enable line wake. USB3 sleepwalk is simpler and mainly asserts/deasserts ELPG clamps. Wake enable/disable functions manipulate ELPG wake event and interrupt bits.

## State and Persistence

The driver keeps fuse calibration in memory, tracks enabled UTMI pads in a bitmap, and uses a shared tracking clock for bias pad calibration. Noirq suspend saves the VBUS/ID override, USB2 pad mux, USB2 port cap, and SS port cap registers; resume restores them. Remote wake state is represented by sticky ELPG wake event bits combined with interrupt-enable bits. The AO sleepwalk configuration persists in AO registers while the main XUSB domain sleeps.

## Dependencies and Integration Points

Dependencies include device-tree MMIO resources (`"ao"`), generic PHY, regulator, clock, fuse, platform, and common XUSB padctl APIs. The common driver provides lane/port creation and external exported helpers, while this file supplies the SoC-specific lane ops and padctl ops. Tegra194 and Tegra234 reuse the same code with different port counts, supply names, and capability flags (`supports_gen2`, tracking polling, tracking update behavior, and low-power config enable).

## Risks and Edge Cases

- `tegra186_usb3_pad_remove()` casts the USB3 pad with `to_usb2_pad()`, which is likely a copy/paste bug; layout compatibility masks it only while the embedded base is first and no USB2-specific members are touched.
- Sleepwalk programming has many ordered register writes and short delays; missing AO resources or wrong SoC capability flags can break wake from suspend.
- UTMI bias tracking warns but continues on tracking-complete poll failure; systems may still work but signal-quality margin can degrade.
- Role switching mixes regulator state with VBUS/ID override. Failed regulator enable/disable paths can leave override state partially changed.
- HSIC support is disabled behind `#if 0` for Tegra186 in this file, so device trees expecting HSIC on this backend will not get a pad/port.

## Test Signals

Test with `CONFIG_ARCH_TEGRA_186_SOC`, `CONFIG_ARCH_TEGRA_194_SOC`, and `CONFIG_ARCH_TEGRA_234_SOC` compile coverage, DT resources named `"ao"`, USB2/USB3 port role combinations, `maximum-speed` limiting, runtime role switching through usb-role-switch, suspend/resume with remote wake from UTMI and SS devices, UTMI tracking-clock availability, and dmesg warnings for tracking poll or fuse read failures.
