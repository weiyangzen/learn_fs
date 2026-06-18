<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/pinctrl/pads-imx8qxp.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/pinctrl/pads-imx8qxp.h

## Purpose

`pads-imx8qxp.h` provides i.MX8QXP pad ID and mux constants for device-tree pinctrl states. It maps physical pads to SCU pin identifiers and names each legal alternate function.

## Important APIs, Types, and Functions

The header exports 736 definitions: 174 numeric pad IDs and 561 function tuples. Pad IDs cover PCIe, USB SS3, eMMC/USDHC, ENET, ESAI/SPDIF, SPI, UART, MIPI DSI/CSI, SCU pins, QSPI, ADC, JTAG, and companion-control pads. Function macros use the form `IMX8QXP_<pad>_<domain>_<signal>  IMX8QXP_<pad>  <mux>`, with domains including HSIO, ADMA, CONN, LSIO, SCU, MIPI, DMA-like audio/display blocks, and QSPI/KPP alternatives.

## Control Flow

There is no executable flow. The header provides constants that are resolved during DTS preprocessing. At runtime, the i.MX SCU pinctrl implementation applies the pad/mux pairs when a device selects a pinctrl state.

## State and Persistence Behavior

The header is stateless. Persistence is limited to compiled DTBs and source DTS files. Runtime pad state is held by the SCU pinctrl/firmware path and hardware registers, not by this file.

## Dependencies and Integration Points

The file is standalone. It integrates with i.MX8QXP DTS files, SCFW-managed pinctrl, and drivers for storage, Ethernet, display/camera, serial buses, USB, QSPI, audio, keypad, and GPIO. It shares many concepts and names with `pads-imx8dxl.h`, but the pad numbering and available functions are not identical.

## Risks and Edge Cases

Porting between QXP, DXL, and QM by name alone can misroute pins because numeric IDs and mux alternatives differ. Some QSPI0B pads expose QSPI1A and keypad alternatives in addition to GPIO, making instance confusion easy. GPIO fallback generally uses LSIO mux 4 in this file, unlike i.MX8QM's common mux 3. Valid macros still depend on firmware resource ownership and board-level voltage/pad constraints.

## Test Signals

Checks include DTS compilation for i.MX8QXP boards, `dtbs_check`, boot-log review for SCU pinctrl failures, pinctrl debugfs inspection, and hardware validation for eMMC/USDHC, ENET, USB, QSPI, MIPI, audio, UART/SPI/I2C, keypad, and GPIO modes. Static tests should ensure every function tuple references a defined pad ID and no board DTS uses a DXL/QM-only macro.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/pinctrl/pads-imx8qxp.h -->
