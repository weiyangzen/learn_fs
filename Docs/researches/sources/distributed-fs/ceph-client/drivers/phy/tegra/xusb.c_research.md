# `sources/distributed-fs/ceph-client/drivers/phy/tegra/xusb.c` Research

## Purpose

This file is the common NVIDIA Tegra XUSB pad controller platform driver. It abstracts SoC-specific padctl behavior behind ops tables from `xusb.h`, creates pad devices, generic PHY lane providers, and port devices from device tree, wires USB role-switch compatibility, manages regulators/resets, handles suspend/resume dispatch, and exports helper APIs used by Tegra USB/XHCI/PHY consumers.

## Important APIs, Types, and Functions

- `tegra_xusb_padctl_of_match[]` maps compatible strings to SoC descriptors for Tegra124/210/186/194/234.
- `tegra_xusb_lane_parse_dt()` validates each lane's `nvidia,function` against its SoC function list.
- `tegra_xusb_pad_init()`, `tegra_xusb_pad_register()`, and `tegra_xusb_pad_unregister()` create pad devices and lane PHY providers.
- `tegra_xusb_setup_pads()` creates pads and programs lane mux functions.
- `tegra_xusb_find_lane()`, `tegra_xusb_port_find_lane()`, `tegra_xusb_find_port()`, and typed USB2/USB3 find helpers connect ports to lanes.
- `tegra_xusb_setup_usb_role_switch()` registers a USB role switch and a legacy `usb_phy` notifier bridge for OTG/peripheral modes.
- `tegra_xusb_setup_ports()` creates USB2, ULPI, HSIC, and USB3 ports and optionally assigns fake USB3 ports.
- `tegra_xusb_padctl_probe()` / `_remove()` own platform lifecycle.
- Exported functions include padctl get/put, USB3 context save, HSIC idle, sleepwalk/wake enable/disable, remote wake detection, LFPS detect, VBUS override, UTMI reset/pad power, companion lookup, and port-number lookup.

## Control Flow

Platform probe first checks for modern `"pads"` child nodes. If missing, it delegates to legacy probe for old device trees. For modern DTs, it gets the SoC descriptor, asks the SoC-specific probe to allocate padctl state, maps MMIO, gets reset and regulators, deasserts reset, enables supplies, then sets up pads and ports.

Pad setup iterates the SoC pad list, finds each pad's DT node under `pads`, calls the pad's SoC-specific probe, registers enabled lane child nodes as PHYs, parses lane functions, and then writes mux bits for each lane through `tegra_xusb_lane_program()`. Port setup iterates SoC port counts for USB2, ULPI, HSIC, and USB3, creates each enabled port device from the `ports` node, maps it to a lane through SoC port ops, parses port-specific properties, and calls port enable callbacks. For SoCs that require fake USB3 ports, USB2 OTG/peripheral ports without a real companion are assigned an unused USB3 index.

For USB role switching, USB2 port parsing defaults to host when `mode` is absent. Peripheral or OTG modes require `usb-role-switch`; setup registers a `usb_role_switch`, creates a legacy `usb_phy` with OTG callbacks, schedules notifier work on role changes, and populates connector child devices. Removal unwinds ports, role-switch state, pads, supplies, reset, and SoC private state in reverse order.

## State and Persistence

The common `struct tegra_xusb_padctl` keeps lists of pads, lanes, and ports, mapped registers, reset, supplies, clock pointer, a mutex, and SoC descriptor. Pad/lane/port objects live as devices or PHY-private data and are freed by release/remove hooks. USB2 port state records mode, internal flag, VBUS regulator, and fake USB3 assignment. USB3 port state records companion USB2 port, internal flag, Gen2 limit, and saved tuning fields. Suspend/resume is delegated to SoC ops; the common layer itself preserves list/device topology but not hardware registers.

## Dependencies and Integration Points

This file depends on Linux platform driver, device tree, generic PHY, regulator, reset, USB role-switch, legacy USB PHY/OTG, workqueue, and Tegra fuse headers. It is the integration point between SoC-specific padctl files and external USB controller drivers. External consumers use the PHY provider under each pad, the exported `tegra_xusb_padctl_*` helpers, and DT phandle `nvidia,xusb-padctl`.

## Risks and Edge Cases

- Modern DT detection is binary: missing `pads` falls into legacy handling, so partial or malformed modern DTs may fail in less obvious ways.
- Peripheral/OTG USB2 modes fail probe without `usb-role-switch`, making DT correctness critical.
- `tegra_xusb_setup_ports()` logs port enable failures but continues after individual enable errors; later PHY consumers may see delayed failures.
- Fake USB3 port assignment depends on disabled/unavailable USB3 DT ports; a fully populated USB3 set leaves no fake port for OTG/peripheral-only USB2.
- Role-switch setup allocates a minimal `device_driver` to satisfy role-switch owner expectations and temporarily assigns driver pointers to PHY devices; changes in USB core assumptions could affect this bridge.
- Exported helpers often return `-ENOSYS`, `-ENOTSUPP`, or `-EOPNOTSUPP` depending on missing SoC ops, so callers must not assume uniform errors.

## Test Signals

Validation should include platform probe/remove on every matched compatible, legacy-DT fallback, pad/lane DT function validation including invalid functions, optional disabled pads/ports, PHY provider lookup, USB2 host/peripheral/OTG mode parsing, role-switch default mode, fake USB3 assignment, suspend/resume dispatch to SoC ops, exported helper behavior when SoC ops are absent, and leak/error-unwind checks around partial pad/port creation failures.
