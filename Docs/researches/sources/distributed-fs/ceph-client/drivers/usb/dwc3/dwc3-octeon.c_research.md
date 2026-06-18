# sources/distributed-fs/ceph-client/drivers/usb/dwc3/dwc3-octeon.c

Purpose: Cavium/Marvell Octeon III DWC3 UCTL wrapper driver. It parses board clock and power-control properties, programs 64-bit UCTL registers, sets endian mode, releases PHY reset, and populates the child DWC3 core in host mode.

Important APIs, types, and functions: `struct dwc3_octeon` stores the parent device and UCTL MMIO base. `dwc3_octeon_readq()` and `_writeq()` use Octeon CSR accessors when available. `dwc3_octeon_config_gpio()` wires Octeon GPIO outputs for port power. `dwc3_octeon_get_divider()` selects a controller clock divider from IO clock rate. `dwc3_octeon_setup()` implements the hardware init sequence. `dwc3_octeon_set_endian_mode()`, `_phy_reset()`, and `_probe()` finish setup.

Control flow: probe requires `refclk-frequency`, `refclk-type-ss`, and `refclk-type-hs`, converts those to reference-clock selector, fsel, and MPLL multiplier values, reads optional `power` GPIO tuple, maps UCTL registers, runs the ordered setup sequence, sets DMA/CSR endian bits, deasserts PHY reset, stores private data, and populates the OF child. Removal only depopulates children.

State and persistence: state is primarily hardware state in `USBDRD_UCTL_CTL`, `HOST_CFG`, and `SHIM_CFG`. The setup sequence asserts resets, sets dividers and reference clocks, powers HS/SS PHYs, deasserts UCTL and UAHC resets, enables clocks, configures port power polarity, and forces host mode. There is no PM restore path, so firmware or full reprobe is expected after reset-level loss.

Dependencies and integration: depends on Octeon SOC CSR helpers under `CONFIG_CAVIUM_OCTEON_SOC`, OF properties, MMIO, delays, and OF child population. It integrates with board GPIO routing for power control and with the DWC3 child through the standard `snps,dwc3` node.

Risks: invalid clock properties fall back or fail depending on field, so board DT accuracy is critical. The non-Octeon stubs return zero reads and no-op writes, making the driver only meaningful on Octeon builds. There is no runtime/system PM handling; suspend behavior depends on wider platform handling. Power GPIO tuple parsing is nonstandard and easy to mis-specify.

Test signals: verify UCTL clock divider selection across IO clock rates, refclk combinations at 50/100/125 MHz, host-only operation, endian correctness on big-endian kernels, GPIO power polarity, and child DWC3 probe after UCTL reset release.
