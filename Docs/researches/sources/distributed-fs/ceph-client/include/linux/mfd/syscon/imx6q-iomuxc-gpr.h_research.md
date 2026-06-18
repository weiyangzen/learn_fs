# sources/distributed-fs/ceph-client/include/linux/mfd/syscon/imx6q-iomuxc-gpr.h

## Purpose

This 472-line header defines i.MX6 IOMUXC general-purpose register offsets and bitfields for clocks, DMA request muxing, PCIe, USB, MIPI/LVDS/HDMI display routing, cache/QoS controls, SATA PHY, Ethernet clocks, MQS, CSI muxes, and related SoC glue.

## Important APIs, Types, and Functions

It exports `IOMUXC_GPR0` through `GPR13` offsets and many `IMX6Q_*`, `IMX6SL_*`, `IMX6SX_*`, `IMX6UL_*`, and `IMX6SLL_*` masks/values. Notable groups cover audio clock muxes, DMA request muxes, PCIe reset/refclk/power, USB ID, IPU/VPU/display muxing, LVDS format/width, cache controls, stop request/ack bits, SATA equalization/boost/level/speed settings, FEC clock direction, MQS control, CSI mux, and `MCLK_DIR(x)`.

## Control Flow

No code executes. Drivers obtain the IOMUXC GPR syscon regmap and perform masked updates when configuring PHYs, display pipelines, audio clocks, Ethernet clock direction, PCIe, SATA, and low-power stop controls.

## State and Persistence Behavior

The GPR fields persist in SoC system registers and directly affect pin mux glue, peripheral routing, clocking, resets, power states, cache policy, and PHY tuning.

## Dependencies and Integration Points

It includes bitops and integrates syscon consumers in PCIe, SATA, USB, DRM/display, Ethernet, audio, VPU/IPU, CSI, MQS, and low-power management drivers.

## Risks and Edge Cases

Many SoC variants share the header but not all fields. Some constants duplicate values or use raw shifts instead of `FIELD_PREP`; consumers must use the correct mask/value pair and avoid applying i.MX6Q fields to i.MX6SX/UL/SLL variants.

## Test Signals

Build tests for all i.MX6 variant drivers, syscon masked-update tests, board boot/display/network/PCIe/SATA smoke tests, and static checks for mask/value compatibility.
