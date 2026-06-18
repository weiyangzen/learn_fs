# sources/distributed-fs/ceph-client/drivers/clk/stm32/clk-stm32mp13.c

## Purpose

`clk-stm32mp13.c` is the STM32MP13 RCC clock driver built on the shared STM32 clock core. It declares MP13-specific gate, mux, divider, security, multi-mux, reset, and clock-binding tables, then registers them through `stm32_rcc_init()`.

## Important APIs, Types, And Functions

- `stm32mp13_gates[]`, `stm32mp13_muxes[]`, and `stm32mp13_dividers[]` describe MP13 RCC register fields.
- `stm32mp13_security[]` maps `SECF_*` IDs to RCC security-status registers and bits.
- Static `clk_stm32_gate`, `clk_stm32_mux`, `clk_stm32_div`, and `clk_stm32_composite` objects represent timer, bus, kernel, Ethernet, MCO, trace, and debug clocks.
- `stm32mp13_clock_cfg[]` maps exported binding IDs to those objects and to security IDs.
- `stm32mp13_clock_is_provided_by_secure()` skips clocks whose RCC security bit says they are secure-owned.
- `stm32mp13_is_multi_mux()` reports paired logical clocks sharing one hardware mux so the shared core can keep CCF parentage coherent.
- `stm32mp1_rcc_clocks_probe()` maps MMIO and delegates to the shared initializer.

## Control Flow

The platform driver binds `st,stm32mp13-rcc` at `core_initcall`. Probe maps the RCC resource with `devm_platform_ioremap_resource()` and calls `stm32_rcc_init()`. The shared core initializes resets with a 16-bit reset ID space and clear offset `0x4`, then registers clocks from `stm32mp13_clock_cfg[]`, skipping secure-provided entries.

The clock table covers APB/AHB peripheral gates, timers, GPIOs, DMA/DMAMUX, ADC, crypto, Ethernet 1/2, USB, SDMMC, FMC/QSPI, serial/audio kernel clocks, DCMIPP, SAES, MCOs, trace, and debug. Safe mux flags are used for FMC, QSPI, and SDMMC kernel muxes, and multi-mux groups cover shared SPI/I2C/LPTIM/UART/SAI selectors.

## State And Persistence Behavior

Runtime state is mostly the shared core's gate counters and registered CCF objects. Hardware state persists in RCC gate, mux, divider, security, and reset registers. Security status is read during registration; if firmware changes ownership later, the registered clock set will not be dynamically rebuilt.

## Dependencies And Integration Points

The driver depends on `clk-stm32-core`, `reset-stm32`, `stm32mp13_rcc.h`, and `dt-bindings/clock/stm32mp13-clks.h`. It exports clocks and resets to MP13 device-tree consumers. Secure-world integration is through RCC security-status bits rather than the STM32 firewall bus API used by MP21/MP25.

## Risks And Edge Cases

Security IDs must match the RCC security registers or Linux may touch secure-owned clocks. Multi-mux pairings must match shared hardware selectors or sibling clocks will show stale parents. Safe muxes assume parent index 0 is valid while disabled. Some entries intentionally use non-obvious parents such as `ck_mlahb`, `pclk6`, or Ethernet parent muxes; parent-name drift in DT or upstream clock names can break registration. Reset IDs use generic banking unless explicit reset lines are not supplied, so the ID mask and clear offset are critical.

## Test Signals

Boot an STM32MP13 board and check probe success plus clock-summary entries for MP13 timers, GPIOs, serial buses, SDMMC, FMC/QSPI, Ethernet 1/2, USB, ADC, DCMIPP, MCO, and trace. Test secure firmware configurations by verifying protected clocks are skipped. Exercise SDMMC/FMC/QSPI disable paths, UART/I2C/SPI shared selectors, reset consumers, and Ethernet PTP clocks.
