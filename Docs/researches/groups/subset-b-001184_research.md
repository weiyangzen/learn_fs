# Research for subset-b-001184

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/tegra/clk-tegra20.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/tegra/clk-tegra20.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/tegra/clk-tegra210-emc.c -->
# sources/distributed-fs/ceph-client/drivers/clk/tegra/clk-tegra210-emc.c

## Purpose
This file implements the Tegra210 EMC clock as a common-clock-framework clock. The EMC clock is unusual because memory-controller timing changes are owned by an external EMC provider, not just by the CAR clock driver. This file exposes a clock named `emc`, validates provider timing tables, chooses supported EMC rates, coordinates parent rate changes, and calls the provider's `set_rate()` hook to perform the actual memory timing transition.

## Important APIs, Types, And Functions
The central type is `struct tegra210_clk_emc`, containing `clk_hw`, CAR register base, provider pointer, and parent clock slots. The public entry points are `tegra210_clk_register_emc()`, `tegra210_clk_emc_attach()`, and exported `tegra210_clk_emc_detach()`. Clock operations are `tegra210_clk_emc_get_parent()`, `tegra210_clk_emc_recalc_rate()`, `tegra210_clk_emc_determine_rate()`, and `tegra210_clk_emc_set_rate()`.

The file uses `struct tegra210_clk_emc_provider` and `struct tegra210_clk_emc_config` from shared Tegra clock headers. The parent list is fixed to `pll_m`, `pll_c`, `pll_p`, `clk_m`, `pll_m_ud`, `pll_mb_ud`, `pll_mb`, and `pll_p_ud`.

## Control Flow
Registration allocates `struct tegra210_clk_emc`, initializes a CCF clock named `emc` with `CLK_IS_CRITICAL | CLK_GET_RATE_NOCACHE`, and registers it with eight parents. Attachment takes a provider module reference, iterates every provider config, validates divider parity and MC/EMC ratio flags, decodes source parent index and divisor, and computes or verifies `config->parent_rate`. If validation fails, it drops the module reference and rejects the provider.

Rate requests first round to the nearest provider config at or above the requested rate, falling back to the maximum available config. `set_rate()` selects the same config, compares the current parent rate and configured source, switches to an alternate PLLM/PLLMB parent when the parent rate must change but the encoded parent would otherwise stay the same, sets the chosen parent clock rate, enables the new parent if reparenting, mutates `config->value` with the actual parent index, calls `provider->set_rate(dev, config)`, then reparents the CCF clock and disables the old parent.

## State And Persistence Behavior
The only persistent software state is the provider pointer and module reference. Hardware state lives in `CLK_SOURCE_EMC`; `get_parent()` decodes bits 31:29 and `recalc_rate()` decodes the 2x divisor in bits 7:0. `recalc_rate()` deliberately ignores the cached parent rate argument and reads the actual current parent because EMC transitions can change both parent and parent rate during `set_rate()`.

## Dependencies And Integration Points
This file integrates the CAR clock tree with the Tegra210 EMC/memory timing driver through the provider interface. It uses Linux CCF APIs for parent lookup, rate setting, parent enable/disable, and manual reparenting. It depends on bitfield helpers for decoding register fields and on Tegra210 CAR register definitions shared with `clk-tegra210.c`, which provides low-level EMC register update functions exported for the EMC provider.

## Risks
`tegra210_clk_emc_set_rate()` mutates the provider config's `value` in place when switching parent index, so provider config storage must be writable and callers must tolerate that updated state. `tegra210_clk_emc_find_parent()` converts from `clk_hw` to name and then uses `__clk_lookup()`, which is global-name dependent. Error handling after a successful provider rate switch but failed old-parent lookup returns an error after hardware has already changed. The rate-selection policy rounds upward and only falls back to max; users expecting exact-only matching need to check returned rates.

## Test Signals
Validation signals include provider attach failure for odd divisors or inconsistent MC/EMC ratio flags, correct `clk_round_rate()` behavior against the timing table, successful EMC frequency transitions across PLLM/PLLMB alternate parents, no parent clock leaks after failed transitions, correct `clk_get_rate(emc)` after parent changes, and suspend/resume or memory stress tests while changing EMC rates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/tegra/clk-tegra210-emc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/tegra/clk-tegra210.c -->
# sources/distributed-fs/ceph-client/drivers/clk/tegra/clk-tegra210.c

## Purpose
This file is the Tegra210 SoC CAR clock driver. It registers the Tegra210 oscillator, PLLs, PLL outputs, super clocks, peripheral clocks, EMC/MC clocks, special resets, CPU clock callbacks, syscore suspend/resume handling, and exported PLL hardware-sequencer controls used by XUSB, SATA, UTMIPLL, PLLE, and EMC code. Compared with Tegra20/Tegra30 it carries more hardware policy: PLL default repair, SDM/fractional rate calculation, dynamic ramping, MBIST workarounds, and special reset lines.

## Important APIs, Types, And Functions
Exported functions include `tegra210_plle_hw_sequence_is_enabled()`, `tegra210_plle_hw_sequence_start()`, XUSB/SATA hardware control and sequence helpers, `tegra210_set_sata_pll_seq_sw()`, EMC update helpers, `tegra210_clk_handle_mbist_war()`, and UTMIPLL IDDQ helpers. Core init is `tegra210_clock_init()` declared with `CLK_OF_DECLARE("nvidia,tegra210-car")`.

Important local mechanisms include many `struct tegra_clk_pll_params` definitions for PLLX, PLLC/C2/C3/C4, PLLM/PLLMB, PLLE, PLLRE, PLLP, PLLA/A1, PLLD/D2/DP, and PLLU; post-divider maps; SDM helper macros; `tegra210_pll_fixed_mdiv_cfg()`; `tegra210_pllx_dyn_ramp()`; PLL default setters; `tegra210_periph_clk_init()`; `tegra210_pll_init()`; `tegra210_init_pllu()`; syscore suspend/resume; and special reset assert/deassert hooks for DFLL DVCO and ADSP.

## Control Flow
`tegra210_clock_init()` maps CAR and PMC, maps AHUB/DISPA/VIC physical ranges needed for MBIST workarounds, allocates the shared clock array for seven peripheral banks, reads `SPARE_REG0` to determine the `clk_m` divisor, initializes oscillator and fixed clocks, registers PLLs, registers peripheral clocks, registers audio clocks, forces PLLD as DSIA/DSIB source, stores the init-table callback, initializes gen5 super clocks, installs special reset callbacks, publishes the OF onecell clock/reset provider, registers clkdev aliases, prepares MBIST clock bulk lists, installs CPU CAR ops, and registers syscore suspend/resume.

PLL init first ensures PLLU/UTMIPLL hardware sequencing is configured, then registers PLL families and their fixed/gated/divider outputs. Peripheral init handles SOR semantics, DPAUX, DSI, CSI test pattern, LA, CML, ACLK, SDMMC mux/div clocks, generated peripheral tables, Tegra common peripheral clocks, Tegra210 EMC clock, and MC divider. `tegra210_clock_apply_init_table()` runs later through `tegra_clk_apply_init_table` arch initcall from `clk.c`.

## State And Persistence Behavior
State is a mix of MMIO state, global pointers, PLL parameter objects, spinlocks, and suspend snapshots. MMIO writes configure PLL defaults, lock-detect bits, IDDQ, dividers, clock enable banks, resets, and hardware sequencer state. PM sleep support saves generic CCF clock context, selected bootloader-programmed CAR registers, CPU soft reset registers, and peripheral enable/reset state, then restores oscillator, PLLU/UTMIPLL, clock framework context, and peripheral context on resume.

MBIST workaround state is in `tegra210_pg_mbist_war[]`, which maps powergate IDs to clock bulk arrays and level-2 override handlers. `tegra210_mbist_clk_init()` resolves clock IDs to `clk_bulk_data`; `tegra210_clk_handle_mbist_war()` prepares/enables those clocks, serializes override writes with `lvl2_ovr_lock`, runs a domain-specific handler, and disables the clocks.

## Dependencies And Integration Points
The file is tightly coupled to Tegra common clock code in `clk.h`, common reset provider setup in `clk.c`, PM core syscore hooks, Tegra PMC powergate IDs, dt-bindings for Tegra210 clocks/resets, Linux CCF APIs, and SoC blocks outside CAR such as AHUB, DISPA, and VIC. It exports symbols consumed by USB/XUSB/SATA/EMC and powergate code. It also depends on firmware/bootloader initial clock state because many default setters inspect already-enabled PLLs and only apply safe in-flight defaults.

## Risks
This file has high hardware risk. It directly maps fixed physical addresses for AHUB/DISPA/VIC rather than discovering them from DT. Several flows use `BUG()` or warnings for unexpected oscillator/reference rates. PLL default setters intentionally postpone full programming when firmware left PLLs enabled; wrong assumptions can leave mixed boot/kernel PLL state. `tegra210_wait_for_mask()` can time out but some callers ignore dynamic-ramp errors. The suspend resume sequence temporarily enables all valid peripheral clocks before restoring rates, which is required for glitchless switching but can expose power or peripheral side effects. Special reset IDs are offset behind common reset banks, so `tegra_init_special_resets(2, ...)` must stay synchronized with dt-bindings.

## Test Signals
Strong signals include clean boot without PLL default warnings beyond expected firmware state, successful `of_clk_src_onecell_get()` for all dt-bindings, working XUSB/SATA/UTMI hardware sequencer transitions, EMC rate changes through the separate EMC provider, display SOR/DPAUX operation, audio PLL exact-rate behavior, CPU idle/suspend/resume, ADSP and DFLL reset behavior, powergate MBIST workaround calls for graphics/display/audio/XUSB/SATA domains, and stress tests around PLL rate changes and resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/tegra/clk-tegra210.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/tegra/clk-tegra30.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/tegra/clk-tegra30.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/tegra/clk-utils.c -->
# sources/distributed-fs/ceph-client/drivers/clk/tegra/clk-utils.c

## Purpose
This file provides a small shared helper, `div_frac_get()`, for computing Tegra divider register values from a requested child rate, parent rate, divider field width, fractional width, and Tegra divider flags. It is used by Tegra clock implementations that need consistent integer/fractional divider math.

## Important APIs, Types, And Functions
The only function is `int div_frac_get(unsigned long rate, unsigned parent_rate, u8 width, u8 frac_width, u8 flags)`. The local `div_mask(w)` macro computes the maximum register value for a divider field of width `w`. The function understands `TEGRA_DIVIDER_INT` and `TEGRA_DIVIDER_ROUND_UP` from `clk.h`.

## Control Flow
If `rate` is zero, the function returns zero. Otherwise it starts with `parent_rate`, scales by `1 << frac_width` for fractional dividers, optionally adds `rate - 1` to implement round-up division, divides by requested rate with `do_div()`, rescales integer-divider results into fractional units, clamps results below one unit to zero, subtracts one unit because Tegra dividers encode `divider - 1`, then clamps the encoded value to the bitfield mask.

## State And Persistence Behavior
The helper is pure computation. It has no static mutable state, performs no allocation, and touches no hardware. Its only persistence effect is the returned encoded divider value that callers later write into clock registers.

## Dependencies And Integration Points
The file depends on `<asm/div64.h>` for `do_div()` and on Tegra divider flag definitions in `clk.h`. It integrates with Tegra divider, peripheral, and mux/div clock registration code elsewhere in the Tegra clock driver set. Because it returns an encoded register field rather than a human divider, callers must pair it with the same flag/field semantics used by their hardware register definitions.

## Risks
`div_mask(w)` uses `1 << w`, so callers must provide widths that fit the integer expression and match hardware field sizes. A zero requested rate returns an encoded zero rather than an error, so callers must validate invalid rate requests if zero should be rejected. The function clamps over-large dividers to the maximum field value, which avoids overflow but can hide that a requested rate is below hardware capability unless the caller separately checks achieved rate.

## Test Signals
Test cases should cover zero rate, integer and fractional dividers, round-up versus truncating behavior, values below the minimum divider, values above the maximum field encoding, and known parent/rate pairs from Tegra peripheral clock tables. Cross-checking `recalc_rate` after programming a divider is the best integration signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/tegra/clk-utils.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/tegra/clk.c -->
# sources/distributed-fs/ceph-client/drivers/clk/tegra/clk.c

## Purpose
This file is the shared Tegra clock-provider core used by SoC-specific CAR drivers. It owns the global clock array, peripheral enable reference counts, reset-controller registration, common peripheral enable/reset suspend context, init-table application, clkdev alias registration, special reset dispatch, optional clock-device creation for runtime PM, and the global `tegra_cpu_car_ops` pointer used by CPU power/control code.

## Important APIs, Types, And Functions
Important exported/shared functions include `tegra_clk_init()`, `tegra_add_of_provider()`, `tegra_init_special_resets()`, `tegra_register_devclks()`, `tegra_lookup_dt_id()`, `tegra_clk_dev_register()`, `tegra_init_dup_clks()`, `tegra_init_from_table()`, `tegra_clk_periph_suspend()`, `tegra_clk_periph_resume()`, `tegra_clk_set_pllp_out_cpu()`, and `get_reg_bank()`. Reset-controller callbacks are `tegra_clk_rst_assert()`, `tegra_clk_rst_deassert()`, and `tegra_clk_rst_reset()`.

Key global state includes `tegra_car_np`, `tegra_cpu_car_ops`, `periph_clk_enb_refcnt`, `periph_banks`, `periph_state_ctx`, `clks`, `clk_num`, `clk_data`, `clk_base`, and special reset callback pointers. `periph_regs[]` describes each CAR peripheral bank's enable and reset register offsets.

## Control Flow
SoC drivers call `tegra_clk_init(regs, num, banks)` early to set the CAR base, allocate per-clock and per-enable reference arrays, record bank count, and allocate suspend context when PM sleep is enabled. They register clocks into the returned `clks` array and finally call `tegra_add_of_provider()`, which normalizes missing clocks to `ERR_PTR(-EINVAL)`, publishes an OF onecell provider, and registers a reset controller with reset count equal to common peripheral reset lines plus any SoC-specific special resets.

Reset assert/deassert first handle common banked reset IDs by writing set/clear registers. IDs after the banked range dispatch to SoC-specific special reset handlers installed by `tegra_init_special_resets()`. `tegra_init_from_table()` applies parent, rate, and enable state rows from SoC init tables. `arch_initcall(tegra_clocks_apply_init_table)` invokes a SoC-assigned callback late enough to apply table state after the SoC driver has assigned it.

## State And Persistence Behavior
The file persists clock pointers for OF and clkdev lookup, peripheral enable reference counts used by gate implementations, banked peripheral enable/reset snapshots for suspend/resume, reset-controller configuration, and special reset callbacks. Suspend saves each bank's enable registers followed by reset registers. Resume writes enables first, waits for reset propagation, restores reset registers, and fences again.

`tegra_clk_dev_register()` can create a platform device for a clock subnode under the CAR node, enable runtime PM on that device, and register the clock against that device. This makes some clock implementations runtime-PM aware while keeping early boot clocks device-less.

## Dependencies And Integration Points
The file integrates Linux CCF, clkdev, OF clock providers, reset-controller framework, platform devices, runtime PM, Tegra fuse/chipid APB flush behavior, and SoC-specific files such as Tegra20/30/210 CAR drivers. It is the shared contract behind the `clks[]` arrays populated from dt-binding IDs and the reset specifiers consumed by device tree clients.

## Risks
The module uses global singleton state, so only one Tegra CAR instance is expected. `tegra_clk_rst_assert()` always reads chip ID to flush APB before asserting reset; that is conservative but means reset behavior depends on fuse/chipid access being safe. Missing clocks are converted to `ERR_PTR(-EINVAL)`, and init-table rows warn but continue, so incomplete clock registration can appear as later consumer failures. `tegra_clk_dev_register()` relies on child node names derived by replacing underscores with hyphens in clock names, making DT naming part of the API. Special reset IDs must stay aligned between bank counts, `num_special_reset`, and SoC reset bindings.

## Test Signals
Signals include onecell provider registration with the expected `clk_num`, reset-controller registration with expected reset count, successful common and special reset operations, correct suspend/resume restoration of peripheral enable/reset state, correct clkdev lookup for legacy aliases, runtime-PM device creation for clocks with matching child DT nodes, and init-table warnings staying absent during boot.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/tegra/clk.c -->
