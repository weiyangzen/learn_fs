# sources/distributed-fs/ceph-client/drivers/clk/tegra/clk-tegra30.c

## Purpose
This file is the Tegra30 CAR clock driver. It initializes Tegra30 oscillator-derived clocks, PLLs, CPU super clocks, audio sync clocks, EMC/MC clocks, peripheral clocks, clkdev aliases, and CPU reset/clock callbacks. It is structurally close to the Tegra20 driver but expands the hardware model for Tegra30: more peripheral banks, more oscillator rates, PLLD2/CML support, low-power and G CPU clock domains, additional audio clocks, SATA/PCIe/HDA clocks, and postcore registration ordering for the memory controller.

## Important APIs, Types, And Functions
The main entry points are `tegra30_clock_init()` via `CLK_OF_DECLARE_DRIVER("nvidia,tegra30-car")`, `tegra30_car_probe()` via a platform driver, and `tegra30_car_init()` via `postcore_initcall()`. Important setup functions are `tegra30_pll_init()`, `tegra30_super_clk_init()`, and `tegra30_periph_clk_init()`.

Static data drives most behavior: PLL frequency tables and `tegra_clk_pll_params`, `tegra30_input_freq`, `devclks`, `tegra30_clks`, `tegra_periph_clk_list`, `tegra_periph_nodiv_clk_list`, `init_table`, duplicate clkdev entries, and `tegra30_audio_plls`. CPU control callbacks are collected in `tegra30_cpu_car_ops`.

## Control Flow
`tegra30_clock_init()` maps CAR and PMC, allocates the shared clock array for five peripheral banks, initializes oscillator clocks with `tegra_osc_clk_init()`, registers fixed clocks, initializes most PLL outputs and CPU super clocks, registers peripheral clocks, initializes audio clocks, adds duplicate lookup aliases, publishes the OF provider, and installs CPU CAR ops. The platform-driver probe later registers PLLC, PLLE, PLLM, and SCLK, then registers clkdev lookups, applies the init table, and sets `tegra30_car_initialized`.

`tegra30_clk_src_onecell_get()` mirrors the Tegra20 deferral strategy: only RTC/TWD/TIMER are usable before full CAR probe, and EMC lookup defers until the EMC driver is available. `tegra30_car_init()` registers the platform driver at postcore init because the memory controller is arch-init-level and currently cannot rely on deferred probing.

## State And Persistence Behavior
Persistent state is held in hardware registers plus static globals for `clk_base`, `pmc_base`, `input_freq`, `clks`, and `tegra30_car_initialized`. Optional CPU suspend context saves Coresight source, CPU burst policy, PLLX base/misc, and CCLK divider. Resume checks whether CPU complex is already running from PLLX and restores PLLX settings only if the CPU is not on PLLX, then restores divider/burst/Coresight state. CPU rail-off readiness checks reset state plus PMC power state for secondary CPUs.

## Dependencies And Integration Points
The driver depends on Tegra common PLL/peripheral/super-clock helpers, the shared `clk.c` OF provider and reset controller, Tegra PMC APIs for CPU power status, `tegra30-car.h` dt-bindings, audio clock helpers, EMC/MC helpers, and clkdev aliases for legacy device names. Peripheral integrations include display, CSI pads, PCIe/AFI, SATA, HDA, AHUB/audio, SDMMC, SPI, I2C, UART, graphics, video, and memory controller clocks.

## Risks
The two-phase init has ordering risk similar to Tegra20: PLLC/PLLE/PLLM/SCLK are not available until platform probe, and consumers must handle `-EPROBE_DEFER`. The `devclks` table has many legacy string bindings, so typos or ID mismatches can break non-DT consumers. CPU reset waiting loops have no timeout. PLL and oscillator tables are dense hardware data; rate-table mistakes can destabilize CPU, memory, display, or USB/SATA paths. The memory-controller ordering comment indicates a known integration fragility if initcall levels change.

## Test Signals
Useful signals include boot without CAR/PMC mapping errors, memory-controller probe after postcore CAR registration, successful late probe applying `init_table`, working EMC probe deferral/resolution, CPU hotplug and rail-off readiness, suspend/resume through CPU LP2/system sleep, display through PLLD/PLLD2 paths, SATA/PCIe CML clocks, HDA/AHUB audio clocks, and SDMMC/UART/I2C/SPI rates matching init-table expectations.
