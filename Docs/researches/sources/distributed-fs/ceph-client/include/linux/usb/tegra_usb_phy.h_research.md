# `sources/distributed-fs/ceph-client/include/linux/usb/tegra_usb_phy.h`

## Purpose

`tegra_usb_phy.h` defines SoC configuration, UTMI tuning, port-speed enums, and runtime state for NVIDIA Tegra USB PHY drivers. It describes the knobs needed to initialize Tegra UTMI/ULPI/HSIC PHY variants and integrate them with clocks, regulators, reset, PMC, and legacy USB PHY APIs.

## Important APIs, Types, and Constants

- `struct tegra_phy_soc_config` records SoC-specific behavior: whether CAR owns UTMI PLL setup, HOSTPC support, USBMODE setup requirement, extra tuning requirement, PMC AO power-up, HSIC register offset, HSIC tuning values, and PORTSC1 offset.
- `struct tegra_utmip_config` stores UTMI timing and signal-integrity tuning values such as sync start delay, elastic limit, idle wait, term range, fuse usage, XCVR setup, LS slew, HS slew, squelch, and disconnect levels.
- `enum tegra_usb_phy_port_speed` identifies full, low, and high speed.
- `struct tegra_usb_phy` stores IRQ, instance, crystal frequency, MMIO bases, clocks, regulator, PMC regmap, role mode, config pointer, SoC config, ULPI PHY, embedded `usb_phy`, legacy flag, interface type, reset GPIO, pad reset, wakeup and power flags.

## Control Flow and Lifetimes

The Tegra PHY driver allocates and fills `tegra_usb_phy`, maps registers, obtains clocks/regulators/resets/PMC regmap, applies SoC and UTMI tuning, initializes the embedded `usb_phy`, and manages power/wakeup through callbacks. Controllers use the embedded legacy PHY object for host/gadget operation.

## State and Persistence Behavior

`tegra_usb_phy` is persistent runtime state for a PHY instance. `powered_on`, `wakeup_enabled`, and `pad_wakeup` track mutable hardware power state. Register configuration persists while powered and may be lost on reset or deep power collapse.

## Dependencies and Integration Points

It depends on clocks, regmap, resets, regulators through forward declarations/includes, GPIO descriptors, OTG role mode, and legacy USB PHY. It integrates Tegra SoC USB controllers, PMC power management, pad controls, ULPI/UTMI/HSIC PHY modes, and board tuning data.

## Risks and Edge Cases

Tuning values are SoC- and board-specific; wrong values can cause marginal high-speed signaling. Clock/reset/regulator ordering is critical. Legacy and non-legacy PHY paths must not double-control pads. Wakeup and AO power flags affect suspend behavior. USBMODE/HOSTPC register offsets vary by SoC.

## Test Signals

Probe Tegra PHY instances across UTMI/ULPI/HSIC modes, run host and device traffic, validate high-speed signal tuning, suspend/resume and wakeup, regulator/clock/reset failure unwinds, PMC AO power behavior, and role-mode transitions.
