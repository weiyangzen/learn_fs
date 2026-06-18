# `sources/distributed-fs/ceph-client/drivers/phy/tegra/xusb-tegra124.c` Research

## Purpose

This file implements the NVIDIA Tegra124/Tegra132 XUSB pad controller SoC backend. It supplies the SoC-specific pad, lane, port, PHY, fuse-calibration, PLL, and ELPG register operations consumed by the common Tegra XUSB padctl core in `xusb.c`/`xusb.h`. It covers USB2 UTMI lanes, one ULPI lane, HSIC lanes, PCIe UPHY lanes that may be muxed to USB3 SuperSpeed, and a SATA lane that may also serve USB3.

## Important APIs, Types, and Functions

- `struct tegra124_xusb_fuse_calibration` stores HS current, IREF, termination, and squelch fuse-derived calibration for USB2 pads.
- `struct tegra124_xusb_padctl` embeds the common `struct tegra_xusb_padctl` and the Tegra124 fuse data.
- `tegra124_xusb_padctl_probe()` allocates SoC private state and calls `tegra124_xusb_read_fuse_calibration()`.
- `tegra124_xusb_padctl_enable()` / `tegra124_xusb_padctl_disable()` reference-count and sequence AUX mux LP0 clamp/vcore bits.
- `tegra124_usb3_save_context()` samples USB3 DFE/CTLE tuning from IOPHY misc output registers and stores it in the common USB3 port structure.
- `tegra124_hsic_set_idle()` toggles HSIC pull-down/pull-up state for idle.
- Per-pad probe/remove and `struct phy_ops` sets exist for USB2, ULPI, HSIC, PCIe, and SATA.
- `tegra124_usb3_port_enable()` programs SuperSpeed port mapping, EQ/CDR/DFE tuning, RX eye enable, SATA-specific PLL details when applicable, and ELPG unclamp sequencing.
- `tegra124_xusb_padctl_soc` is the exported SoC descriptor consumed by the common platform driver.

## Control Flow

The common driver matches `"nvidia,tegra124-xusb-padctl"` or Tegra132-compatible data to `tegra124_xusb_padctl_soc`. Probe allocates the private padctl and reads fuses. Common pad setup then creates enabled pads from the SoC pad list, registers lanes as generic PHYs, parses each lane's `nvidia,function`, and programs the mux field at each lane's register offset. Common port setup creates optional USB2/ULPI/HSIC/USB3 ports, maps each port to a lane, parses port properties, and calls each port's enable callback.

PHY users drive the main runtime behavior through `phy_ops`. USB2 and HSIC init/exit take/release the padctl AUX clamp reference. USB2 power-on programs fuse-calibrated bias and OTG pad registers, sets the port capability to host in this older implementation, enables VBUS, and powers up the shared USB2 bias pad under a pad-local reference count. HSIC power-on enables its regulator, writes trim and tuning values from lane state, and clears HSIC power-down bits. PCIe and SATA power-on manually initialize PLLs, poll lock bits with 50 ms timeouts, and clear IDDQ for the lane group. USB3 port enable maps the port to its USB2 companion, configures equalization/tuning, optionally restores saved context, and performs ELPG vcore/clamp deassertion.

## State and Persistence

Persistent hardware-facing state is mostly register state plus fuse-derived calibration cached in memory. The padctl has a shared `enable` reference count guarding AUX LP0 clamp sequencing; USB2 pads have their own `enable` count for the shared bias pad. USB3 context (`tap1`, `amp`, `ctle_g`, `ctle_z`, `context_saved`) is stored in the common USB3 port object after `tegra124_usb3_save_context()`. There is no suspend/resume hook in this file's padctl ops, so durable low-power context restoration is narrower than Tegra210/186.

## Dependencies and Integration Points

The file depends on common Tegra XUSB data structures from `xusb.h`, generic PHY APIs, device tree lane/port child nodes, regulators for VBUS/HSIC supplies, Tegra fuse reads, reset/clock primitives, and low-level MMIO access through `padctl_readl()`/`padctl_writel()`. It integrates with the common driver through pad, lane, port, and padctl ops tables. External USB/XHCI/PCIe/SATA consumers see the result as generic PHYs and exported padctl services through the common layer.

## Risks and Edge Cases

- PLL lock paths rely on fixed 50 ms polling windows and return `-ETIMEDOUT`; marginal hardware or clock setup issues can fail PHY bring-up.
- USB2 power-on unconditionally writes the USB2 port capability as host, which is less role-flexible than newer SoCs.
- The SATA power-off path sets `value |= ~XUSB_PADCTL_IOPHY_MISC_PAD_S0_CTL1_IDDQ_OVRD` and `value |= ~XUSB_PADCTL_IOPHY_MISC_PAD_S0_CTL1_IDDQ`, which appears suspicious because it sets nearly all bits rather than setting/clearing the named bits only.
- USB3 port enable contains a TODO noting that some PCIe/SATA PHY setup may belong in PHY power-on callbacks, so ordering may be hardware-sensitive.
- Error unwinding around regulator enable and pad counts should be tested carefully because shared pad state spans multiple lane users.

## Test Signals

Useful validation signals include `CONFIG_ARCH_TEGRA_124_SOC` builds, device-tree lane mux combinations for USB2/ULPI/HSIC/PCIe/SATA, probe logs for fuse reads and optional pad creation, PHY power-on/off cycles, USB2 VBUS behavior, HSIC idle transitions, USB3 companion mapping, PLL timeout absence, and suspend/resume or controller reset tests that exercise `tegra124_usb3_save_context()`.
