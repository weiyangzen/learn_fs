# sources/distributed-fs/ceph-client/drivers/pinctrl/mvebu/pinctrl-armada-375.c

## Purpose
This file supplies the Marvell Armada 375 / MV88F6720 MPP mode table and probe glue for the shared MVEBU pinctrl core.

## Important APIs, Types, and Data
- `mv88f6720_mpp_modes` covers MPP pins 0-66 with functions for GPIO, device bus, SPI0/1, NAND, PTP, LEDs, audio, PCIe reset/clock request, I2C, UART, TDM, GE0/GE1, SD, SATA presence, DRAM VTT/error, and reference clock output.
- `armada_375_pinctrl_info` is the per-SoC info structure populated at probe.
- `armada_375_pinctrl_of_match` binds `marvell,mv88f6720-pinctrl`.
- `mv88f6720_mpp_controls` declares one MMIO MPP control range.
- `mv88f6720_mpp_gpio_ranges` exposes GPIO ranges for pins 0-31, 32-63, and 64-66.
- `armada_375_pinctrl_probe()` fills the SoC info and calls `mvebu_pinctrl_simple_mmio_probe()`.

## Control Flow
The platform probe stores mode/control/range tables into `armada_375_pinctrl_info`, attaches it to `pdev->dev.platform_data`, and delegates registration and runtime behavior to the shared MVEBU core.

## State and Persistence
The file defines static tables and one static SoC info structure. MPP state persists in hardware. No local dynamic state or suspend/resume handling is present.

## Dependencies and Integration Points
It depends on `pinctrl-mvebu.h`, platform/OF support, and Kconfig/Makefile selection through `CONFIG_PINCTRL_ARMADA_375`.

## Risks
The control descriptor uses `MPP_FUNC_CTRL(0, 69, ...)` while the visible mode table covers modes through 66 and GPIO ranges cover 67 pins; this may reflect hardware reserved pins but is a table consistency point to verify against the shared core and datasheet. Incorrect alternate values could break storage, PCIe, Ethernet, or boot bus pin routing.

## Test Signals
Build with `CONFIG_PINCTRL_ARMADA_375`, boot with `marvell,mv88f6720-pinctrl`, inspect pinctrl debugfs, and test representative SD, SPI, NAND, UART/I2C, PCIe reset/clkreq, GE, LED, and GPIO paths. Check for warnings or missing modes around the high MPP numbers.
