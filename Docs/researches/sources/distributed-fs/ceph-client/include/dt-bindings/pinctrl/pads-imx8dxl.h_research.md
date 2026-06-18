<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/pinctrl/pads-imx8dxl.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/pinctrl/pads-imx8dxl.h

## Purpose

`pads-imx8dxl.h` is the NXP i.MX8DXL System Controller firmware pinctrl binding catalog. It assigns stable pad IDs and mux alternatives so DTS files can request pad ownership/function through the i.MX SCU pinctrl interface.

## Important APIs, Types, and Functions

The file exports 626 definitions: 136 numeric pad IDs and 489 pad/function/mux tuples, plus the include guard. The first section maps symbols such as `IMX8DXL_EMMC0_CLK`, `IMX8DXL_ENET0_RGMII_TXC`, `IMX8DXL_SPI3_SCK`, and `IMX8DXL_SCU_BOOT_MODE*` to pad IDs. The second section maps functions using `IMX8DXL_<pad>_<domain>_<signal>  IMX8DXL_<pad>  <mux>`. Domains include HSIO, ADMA, CONN, LSIO, SCU, MIPI, and audio/display-related blocks. A final set of `_PAD` definitions covers companion-control pads such as voltage/compensation controls.

## Control Flow

There is no executable control flow. DTS macros expand to pin ID and mux selector cells. The i.MX SCU pinctrl path passes those values to firmware/hardware to select pad routing, typically when a device's default pinctrl state is applied.

## State and Persistence Behavior

The header is stateless. Selected pin states are stored in device tree and become runtime pad ownership/mux state in the SCU-managed pin controller. The header does not describe drive strength, pull, or persistence policy by itself; those are additional binding cells or firmware-controlled pad settings.

## Dependencies and Integration Points

The header is standalone and is included by i.MX8DXL DTS/DTSI files. It integrates with the NXP SCU pinctrl binding, SCFW resource ownership, and peripheral nodes for eMMC/USDHC, Ethernet, USB, SPI, UART, I2C, MIPI, QSPI, audio clocks, and SCU boot/GPIO pins.

## Risks and Edge Cases

i.MX8DXL uses SCU-managed resources, so a valid macro may still fail if firmware ownership or power-domain setup does not permit the pad/function. Many pads have GPIO alternatives in multiple LSIO banks and mux values 4 or 5; selecting the wrong bank can compile but expose the wrong GPIO number. Companion-control pads ending in `_PAD` are not normal signal muxes and should not be treated like peripheral data pins. Board-level voltage compatibility is important for the `COMP_CTL_GPIO_1V8_3V3_*` pads.

## Test Signals

Good tests are DTS compilation for i.MX8DXL boards, pinctrl binding validation, SCU firmware boot logs for pad ownership errors, debugfs pinmux inspection, and hardware tests for eMMC, USDHC, RGMII, USB, QSPI, SPI, UART/I2C, MIPI, and GPIO fallback paths. Static checks should verify two-cell function macros reference an existing pad ID and use valid mux numbers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/pinctrl/pads-imx8dxl.h -->
