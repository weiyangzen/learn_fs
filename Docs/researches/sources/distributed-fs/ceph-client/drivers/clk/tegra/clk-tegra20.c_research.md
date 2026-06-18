# sources/distributed-fs/ceph-client/drivers/clk/tegra/clk-tegra20.c

## Purpose
This file is the Tegra20 CAR clock driver. It maps the Tegra20 clock-and-reset controller registers, discovers oscillator and PLL reference rates, registers the Tegra20 PLLs, super clocks, audio clocks, EMC/MC clocks, and peripheral gates with the common clock framework, and publishes CPU clock/reset callbacks through `tegra_cpu_car_ops`. It is an early boot clock provider declared with `CLK_OF_DECLARE_DRIVER("nvidia,tegra20-car")`, with a second platform-driver probe phase for clocks that depend on driver-core/runtime-PM readiness.

## Important APIs, Types, And Functions
Key tables are `pll_*_freq_table`, `pll_*_params`, `devclks`, `tegra20_clks`, `init_table`, and `tegra_clk_duplicates`. The PLL parameter tables describe register offsets, lock bits, lock delays, fixed-rate constraints, post-dividers, and rate tables consumed by helpers from `clk.h`. The public integration path is `tegra20_clock_init()` plus `tegra20_car_probe()`.

Important local functions include `tegra20_clk_measure_input_freq()`, `tegra20_get_pll_ref_div()`, `tegra20_pll_init()`, `tegra20_super_clk_init()`, `tegra20_audio_clk_init()`, `tegra20_periph_clk_init()`, and `tegra20_osc_clk_init()`. CPU control is implemented by `tegra20_wait_cpu_in_reset()`, `tegra20_put_cpu_in_reset()`, `tegra20_cpu_out_of_reset()`, `tegra20_enable_cpu_clock()`, `tegra20_disable_cpu_clock()`, and optional suspend/resume helpers.

## Control Flow
`tegra20_clock_init()` maps the CAR node and matching PMC node, allocates the shared clock array with three peripheral banks, registers oscillator/fixed clocks, registers PLLs, CPU super clock, gen4 super clocks, peripheral clocks, and audio clocks, then installs duplicate clkdev aliases, the OF onecell provider, and Tegra CPU CAR ops. `tegra20_car_probe()` later registers `sclk`, creates clkdev lookups, applies `init_table`, and flips `tegra20_car_initialized` so normal clock lookups stop deferring.

Clock lookup is guarded by `tegra20_clk_src_onecell_get()`: RTC, TWD, and TIMER are available before full init; other clocks return `-EPROBE_DEFER` until probe finishes. CDEV1/CDEV2/CSUS also defer until their pinctrl-created parent exists, and EMC defers until the Tegra20 EMC clock driver is available.

## State And Persistence Behavior
Persistent runtime state is MMIO-backed: PLL programming, clock-source registers, peripheral enables, reset bits, and CPU-complex bits. In memory, the file stores `clk_base`, `pmc_base`, `clks`, `tegra20_car_initialized`, and optional CPU suspend context. During CPU clock suspend it saves Coresight source, CCLK burst policy, PLLX base/misc, and CCLK divider; resume restores PLLX if needed and then restores burst/divider/Coresight settings.

## Dependencies And Integration Points
The file depends heavily on Tegra common clock helpers in `clk.h`, dt-bindings from `tegra20-car.h`, OF address mapping, clkdev aliases for legacy drivers, and the shared reset/onecell infrastructure in `clk.c`. It integrates with the Tegra20 PMC, the Tegra EMC/MC clock helpers, audio clock helpers, gen4 super-clock helpers, and CPU hotplug/power code through `tegra_cpu_car_ops`.

## Risks
Oscillator detection uses `BUG()` for unexpected hardware state, which is acceptable for early platform bring-up but harsh if firmware provides unexpected values. Rate tables are hardware-contract data; incorrect entries can silently produce unstable peripheral, display, memory, USB, or CPU clocks. The split init model is sensitive to ordering: exposing clocks before `tegra20_car_initialized` could let consumers use half-registered clocks, while over-deferral can stall device probe. CPU reset/clock functions directly manipulate shared CPU-complex registers and rely on barriers and polling with no timeout in `wait_cpu_in_reset()`.

## Test Signals
Useful signals are boot logs without clock registration errors, successful OF clock lookup after platform probe, stable init-table rate setting, working RTC/timer/TWD access during early boot, EMC driver probe deferral/resolution, CPU hotplug/reset behavior, suspend/resume across LP2/system sleep, and functional display/audio/USB/SDMMC/UART peripherals at their programmed rates.
