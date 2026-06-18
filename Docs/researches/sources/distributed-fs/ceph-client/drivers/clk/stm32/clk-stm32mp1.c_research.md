# sources/distributed-fs/ceph-client/drivers/clk/stm32/clk-stm32mp1.c

## Purpose

`clk-stm32mp1.c` is the original STM32MP1 RCC clock driver. Unlike later STM32MP13/21/25 drivers, it contains its own local clock framework wrappers for gates, muxes, dividers, composites, PLLs, timer kernel clocks, multi-gates, multi-muxes, reset setup, OF provider registration, and platform-driver probe.

## Important APIs, Types, And Functions

- Local `clock_config` entries describe each clock name, binding ID, parents, flags, config blob, and registration callback.
- `_clk_hw_register_gate()`, `_clk_hw_register_fixed_factor()`, `_clk_hw_register_divider_table()`, and `_clk_hw_register_mux()` wrap standard CCF helpers.
- `mp1_gate_clk_ops` supports STM32MP1 set/clear gate registers by writing the clear offset on disable.
- `mp1_mgate_clk_ops` tracks several logical clocks sharing one hardware gate through `struct stm32_mgate`.
- `clk_mmux_ops` reparents sibling mux users when a shared hardware mux changes.
- `pll_ops` models PLL enable/disable, ready polling, parent readback, and rate recalculation from DIVM/DIVN/fractional registers.
- `timer_ker_ops` handles timer kernel clocks whose rates depend on APB prescalers and TIMPRE bits.
- `rtc_div_clk_ops` applies the RTC divider only when HSE is the selected RTC parent.
- `stm32_rcc_clock_init()`, `stm32_rcc_init()`, and `stm32mp1_rcc_clocks_probe()` perform provider setup.

## Control Flow

`core_initcall(stm32mp1_clocks_init)` registers a platform driver for `st,stm32mp1-rcc` and `st,stm32mp1-rcc-secure`. Probe first keeps references to external oscillator dependencies (`hsi`, `hse`, `csi`, `lsi`, `lse`) so they remain available, maps RCC with `of_iomap()`, initializes reset control through `stm32_rcc_reset_init()`, and registers all clocks from `stm32mp1_clock_cfg`.

The clock table builds oscillator gates, PLLs and PLL outputs, system muxes/dividers, APB peripheral clocks, timer clocks, kernel clocks for SDMMC/FMC/QSPI/RNG/USB/SPI/I2C/LPTIM/UART/SAI/ADC/DSI/Ethernet, RTC/MCO/debug clocks, and fixed factors. Secure-compatible instances skip IDs listed in `stm32mp1_clock_secured`.

## State And Persistence Behavior

Persistent state lives in the RCC MMIO registers: mux selections, PLL enable and fractional configuration, dividers, gate bits, reset bits, TIMPRE settings, and RTC/MCO state. Software state includes CCF objects allocated with `devm_kzalloc`, `mp1_mgate[].flag` bitmasks, `ker_mux[].hws`, and external oscillator references. The driver does not implement suspend/resume; CCF and hardware register retention determine behavior across power states.

## Dependencies And Integration Points

The driver integrates Linux CCF, platform-driver and OF matching, reset-controller APIs via `reset-stm32`, and `dt-bindings/clock/stm32mp1-clks.h`. It exports a one-cell clock provider for consumers such as timers, UART/I2C/SPI, SDMMC, USB, Ethernet, display, crypto, watchdog, and RTC drivers.

## Risks And Edge Cases

PLL enable polling uses a bounded udelay loop inside a spinlocked enable path because jiffies polling is unavailable there; timeout behavior can affect early boot. Multi-gate and multi-mux arrays must remain consistent with the clock table or shared hardware bits will be mishandled. Secure mode skips clocks rather than registering stubs, so consumers must not request secure-only IDs from the non-secure RCC. `of_iomap()` cleanup only occurs on failure, matching old provider lifetime assumptions. Parent-name strings and binding IDs are ABI-sensitive.

## Test Signals

Build with STM32MP1 clock support and boot both secure and non-secure RCC compatibles. Validate clock-summary entries for PLLs, MPU/AXI/MCU, APB pclk, timer kernel clocks, RTC, MCO, SDMMC, USB, Ethernet, SPI/I2C/UART, SAI, and display clocks. Exercise PLL-dependent peripherals, `clk_disable_unused`, reset controls, and secure firmware configurations where protected clocks should be absent from Linux.
