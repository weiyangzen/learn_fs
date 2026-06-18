# sources/distributed-fs/ceph-client/drivers/pinctrl/stm32/pinctrl-stm32f429.c

## Purpose

`pinctrl-stm32f429.c` is the SoC-specific pin description table and platform-driver registration unit for the STM32F429 pin controller. It does not implement pinctrl algorithms itself; instead it supplies static metadata to the shared STM32 pinctrl core in `pinctrl-stm32.c` through `struct stm32_pinctrl_match_data`.

The file declares 168 pins, numbered 0 through 167, covering GPIO ports PA through PJ with 16 pins each and PK with 8 pins. Each pin entry maps a Linux pinctrl pin descriptor such as `PINCTRL_PIN(0, "PA0")` to the STM32 alternate-function selector slots used by the generic STM32 pinctrl driver. Function slot 0 is always the GPIO function, slot 16 is `EVENTOUT`, and slot 17 is `ANALOG`; intermediate slots describe hardware alternate functions such as timers, USART/UART, I2C, SPI/I2S, Ethernet MII/RMII, SDIO, DCMI, FMC, LCD, OTG FS/HS, SAI1, JTAG/SWD/trace, CAN, and RTC outputs.

## Important APIs, Types, and Data

- `static const struct stm32_desc_pin stm32f429_pins[]`: the authoritative static pin/function table for this compatible.
- `STM32_PIN(...)`, `PINCTRL_PIN(...)`, and `STM32_FUNCTION(...)`: descriptor macros from the pinctrl and STM32 local headers. Each `STM32_FUNCTION(n, name)` stores the alternate-function selector number and user-visible function name in the fixed `functions[STM32_CONFIG_NUM]` array.
- `static struct stm32_pinctrl_match_data stm32f429_match_data`: binds `.pins` to `stm32f429_pins` and `.npins` to `ARRAY_SIZE(stm32f429_pins)`. No secure-control, I/O-sync, RIF, or package flags are set in this SoC table.
- `static const struct of_device_id stm32f429_pctrl_match[]`: matches device-tree nodes with `.compatible = "st,stm32f429-pinctrl"` and exposes `stm32f429_match_data` via `.data`.
- `static struct platform_driver stm32f429_pinctrl_driver`: registers the shared `stm32_pctl_probe` callback with driver name `stm32f429-pinctrl`.
- `arch_initcall(stm32f429_pinctrl_init)`: registers the platform driver early during kernel boot.

The table is data-heavy. Representative patterns include PA0-PA15 for low-numbered GPIOs and common peripheral pins, PB/PC/PD/PE/PF/PG for dense timer, serial, SDIO, Ethernet, FMC, and DCMI routing, PH/PI/PJ/PK for oscillator, trace, LCD, camera, FMC, and high pin-count package functions. Pins retain numeric holes only where the SoC itself has package/function constraints; the F429 table covers the full 0-167 range.

## Control Flow

1. The built-in initcall invokes `stm32f429_pinctrl_init()`.
2. `stm32f429_pinctrl_init()` calls `platform_driver_register(&stm32f429_pinctrl_driver)`.
3. When the platform bus finds a device-tree node compatible with `st,stm32f429-pinctrl`, the kernel binds it to this driver.
4. The shared `stm32_pctl_probe()` receives the `platform_device`, obtains the match data from the OF match table, and uses this file's pin table to register pins, groups, functions, GPIO ranges, and pin configuration support.
5. Later pinmux requests from device-tree states are resolved by the common driver against the `stm32_desc_pin` entries provided here.

There is no per-pin executable logic in this file after registration. The behavior comes from the data table and the shared STM32 core.

## State and Persistence

The pin table and OF match data are static kernel data. They are effectively immutable after boot. This file keeps no runtime state, owns no locks, allocates no memory directly, and persists nothing across boots. Hardware register programming, suspend/resume state, and pin configuration caching are delegated to the common STM32 pinctrl implementation.

Because this is built in via `arch_initcall`, the driver is intended to be present before dependent platform devices request their pin states. The absence of a module exit path is normal for this built-in pinctrl driver.

## Dependencies and Integration Points

- Linux headers: `<linux/init.h>`, `<linux/of.h>`, and `<linux/platform_device.h>`.
- Local integration: `pinctrl-stm32.h` defines descriptor structures, function-slot constants, and the shared `stm32_pctl_probe()` prototype.
- Device tree: board DTS files must use `compatible = "st,stm32f429-pinctrl"` and pinmux/function names that match this table.
- Generic pinctrl and gpiolib: the shared STM32 core converts this descriptor table into Linux pinctrl pins, functions, groups, and GPIO ranges.
- Peripheral drivers: Ethernet, LCD, DCMI, SDIO, USART/UART, SPI/I2S, I2C, timers, USB OTG, FMC, CAN, and debug/trace peripherals depend on these names and AF numbers when applying pinctrl states.

## Risks and Edge Cases

- A wrong alternate-function number silently programs incorrect hardware muxing even though the kernel data structures remain valid.
- Function-name drift between this table and device-tree bindings can break board pinctrl states at probe time.
- Multi-name function strings such as `TIM2_CH1 TIM2_ETR` or `ETH_MII_RX_CLK ETH_RMII_REF_CLK` intentionally represent shared AF selectors; consumers and reviewers must preserve those combined names rather than splitting them as independent selector slots.
- Debug pins (`JTMS SWDIO`, `JTCK SWCLK`, `JTDO TRACESWO`, `NJTRST`, trace data pins) can conflict with board debug access if selected by an alternate state.
- High-density peripheral groups such as FMC, LCD, DCMI, Ethernet, and SDIO require many pins to be consistent. A single descriptor typo can produce hard-to-diagnose board-level failures.
- This table has no package filtering (`pkg` remains unset), so package-specific absence of pins must be handled by board design and device-tree usage rather than this match data.

## Test Signals

- Build coverage: compile the STM32 pinctrl driver with this file enabled and check for descriptor macro or type regressions.
- Boot/probe coverage: a DTS node with `st,stm32f429-pinctrl` should bind to `stm32f429-pinctrl` and call the shared probe successfully.
- Device-tree validation: board pinctrl states should only reference pin/function names present in `stm32f429_pins`.
- Hardware smoke tests: exercise GPIO, USART, I2C, SPI/I2S, Ethernet MII/RMII, SDIO, LCD, DCMI, USB OTG, and FMC configurations on representative F429 boards.
- Regression checks: compare AF numbers against the STM32F429 datasheet/reference manual when adding or changing descriptors.
