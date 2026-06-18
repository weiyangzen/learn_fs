# sources/distributed-fs/ceph-client/drivers/pinctrl/mvebu/pinctrl-armada-370.c

## Purpose
This file provides the Marvell Armada 370 / MV88F6710 MPP mode table and probe glue for the shared MVEBU pinctrl core.

## Important APIs, Types, and Data
- `mv88f6710_mpp_modes` describes MPP pins 0-65 with alternate functions including GPIO/GPO, UARTs, I2C, GE0/GE1, SATA presence, TDM, audio, SD0, SPI0/1, PCIe clock request/reset, device bus, and TCLK.
- `armada_370_pinctrl_info` is populated at probe.
- `armada_370_pinctrl_of_match` binds `marvell,mv88f6710-pinctrl`.
- `mv88f6710_mpp_controls` declares a single MMIO function control over pins 0-65.
- `mv88f6710_mpp_gpio_ranges` exposes three GPIO ranges: 0-31, 32-63, and 64-65.
- `armada_370_pinctrl_probe()` fills SoC info and delegates to `mvebu_pinctrl_simple_mmio_probe()`.

## Control Flow
Probe writes the static mode/control/range data into `armada_370_pinctrl_info`, assigns it to platform data, and invokes the shared simple MMIO probe. The shared core handles pinctrl registration and runtime register writes.

## State and Persistence
Static mode data lives for the built-in driver lifetime. Hardware MPP selections persist in MMIO registers controlled by the shared core. No local software state beyond the SoC info structure is maintained.

## Dependencies and Integration Points
It depends on `pinctrl-mvebu.h`, OF platform matching, and the shared MVEBU MMIO controller implementation. Kbuild includes it through `CONFIG_PINCTRL_ARMADA_370`.

## Risks
The mode table is large and hardware-specific; wrong mode values can reroute boot-critical device bus, SPI, SD, SATA, or Ethernet pins. Some pins are GPO rather than GPIO-capable; consumers must not assume all ranges support input semantics beyond what the shared core/gpio ranges expose.

## Test Signals
Build and boot Armada 370 hardware/DT, verify debugfs MPP function lists, and exercise UART, I2C, SPI, SD, Ethernet, SATA presence, device bus, and GPIO operations. Cross-check GPIO range counts against DT GPIO controller expectations.
