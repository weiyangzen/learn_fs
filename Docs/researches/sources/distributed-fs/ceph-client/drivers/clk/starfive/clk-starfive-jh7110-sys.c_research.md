# sources/distributed-fs/ceph-client/drivers/clk/starfive/clk-starfive-jh7110-sys.c

## Purpose
This built-in driver registers the main JH7110 system clock controller and reset auxiliary device. It covers CPU, bus, DDR, GPU, ISP top, audio, VOUT top, codec, QSPI, SDIO, USB/STG roots, GMAC, APB peripherals, and audio serial clocks.

## Important APIs, Types, And Functions
`jh7110_sysclk_data[]` is the main topology table. `jh7110_reset_controller_register()` creates an auxiliary reset device backed by the same register base and is exported for child clock domains. `jh7110_pll0_clk_notifier_cb()` temporarily switches `cpu_root` to `osc` during PLL0 rate changes. `jh7110_syscrg_probe()` registers clocks, optional fixed-factor PLL fallbacks, OF provider, and reset device `rst-sys`.

## Control Flow
Probe maps registers, tries to get real `pll*_out` clocks, and falls back to fixed factors if absent. If PLL0 exists it registers a notifier. It iterates through all SYS clock IDs, resolving parents to local clocks, external firmware names, real PLL names, or fallback PLL hardware. After registration it adds the OF provider and registers reset ID 0.

## State And Persistence
Clock state is in one register per clock index. Driver state tracks the register base, read-modify-write lock, fallback PLLs, original CPU-root parent during PLL0 transitions, and notifier block. Reset auxiliary devices share the same base.

## Dependencies And Integration Points
It depends on the shared JH71x0 core, the JH7110 PLL provider when enabled, auxiliary bus, reset framework, and board-provided external clocks. Child domains AON/STG/ISP/VOUT depend on its parent clocks and exported reset helper.

## Risks
PLL0 notifier obtains `osc` with `clk_get()` but does not check for an error before `clk_set_parent()`. A registered PLL0 notifier is not explicitly unregistered, relying on built-in lifetime. Parent mapping is large and table-driven, so binding ID drift is high impact. Fallback fixed-factor PLLs may hide missing PLL provider configuration.

## Test Signals
Boot with real PLL provider and fallback PLLs, CPU frequency changes involving PLL0, child-domain probes, reset auxiliary-device binding, GMAC modes, audio serial clocks, SDIO/QSPI, and critical interconnect clocks should be validated.
