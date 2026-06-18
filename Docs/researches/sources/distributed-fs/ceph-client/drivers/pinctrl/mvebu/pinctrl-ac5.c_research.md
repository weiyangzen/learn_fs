# sources/distributed-fs/ceph-client/drivers/pinctrl/mvebu/pinctrl-ac5.c

## Purpose
This file is the Marvell AC5 pinctrl SoC table driver. It describes AC5 multi-purpose pin (MPP) modes and passes them to the shared MVEBU pinctrl core.

## Important APIs, Types, and Data
- `ac5_mpp_modes` lists MPP pins 0 through 45 and their alternate functions, including GPIO, SDIO, NAND, SPI0/1, UARTs, I2C, MDIO, PTP, watchdog/interrupt lines, PCIe reset, syncE, and LED signals.
- `ac5_pinctrl_info` is the shared `mvebu_pinctrl_soc_info` filled at probe.
- `ac5_pinctrl_of_match` binds `marvell,ac5-pinctrl`.
- `ac5_mpp_controls` declares one MMIO MPP control covering pins 0-45 via `mvebu_mmio_mpp_ctrl`.
- `ac5_mpp_gpio_ranges` exposes all 46 pins as a GPIO range.
- `ac5_pinctrl_probe()` fills the SoC info and delegates to `mvebu_pinctrl_simple_mmio_probe()`.

## Control Flow
On platform probe, the driver initializes `ac5_pinctrl_info` with variant zero, control descriptors, GPIO ranges, mode table, and mode count, stores it in `pdev->dev.platform_data`, and calls the shared simple MMIO probe. Runtime muxing is implemented by the shared MVEBU core using these tables.

## State and Persistence
This file contains static mode/control data plus one static SoC info structure populated during probe. MPP state persists in hardware registers managed by the shared core. No local suspend/resume or dynamic state is implemented.

## Dependencies and Integration Points
It depends on `pinctrl-mvebu.h`, platform devices, OF matching, and the shared MVEBU MMIO control helpers. It is built when `CONFIG_PINCTRL_AC5` is selected.

## Risks
The driver assumes a single contiguous control range for all 46 pins. Incorrect MPP mode values or GPIO range length would cause wrong peripheral routing. `soc->nmodes` is derived from `ac5_mpp_controls[0].npins`, so it must match the populated `ac5_mpp_modes` entries.

## Test Signals
Build with `CONFIG_PINCTRL_AC5`, boot an AC5 DT using `marvell,ac5-pinctrl`, inspect pinctrl debugfs for MPP functions, and test representative muxes such as SDIO, NAND, SPI, UART, I2C, MDIO/PTP, LED, and GPIO.
