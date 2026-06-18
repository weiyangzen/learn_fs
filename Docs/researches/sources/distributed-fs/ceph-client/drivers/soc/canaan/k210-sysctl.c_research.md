# sources/distributed-fs/ceph-client/drivers/soc/canaan/k210-sysctl.c

Purpose: Canaan Kendryte K210 system controller driver and early SoC clock initializer. It enables the sysctl bus clock during platform probe and populates child devices, while very early init maps the sysctl block to initialize PLL1/SRAM-capable clocks.

Important APIs and functions: `k210_sysctl_probe()` gets and enables the bus clock with devm clock APIs and calls `devm_of_platform_populate()`. `builtin_platform_driver(k210_sysctl_driver)` registers the OF platform driver for `canaan,k210-sysctl`. `k210_soc_early_init()` is registered via `SOC_EARLY_INIT_DECLARE()` for `canaan,kendryte-k210` and calls `k210_clk_early_init()` on a temporary mapping of fixed physical sysctl registers.

Control flow: the early init path uses the hard-coded K210 sysctl base before normal device model probing because PLL1 must be enabled before all SRAM can be used. Later, normal probe logs the controller, enables the clock, and creates child platform devices.

State and persistence: no private persistent struct is stored. Persistent side effects are clock controller state and child device creation. The early MMIO mapping is unmapped before return.

Dependencies and integration: depends on RISC-V SoC early init, OF platform population, common clock K210 support, and `soc/canaan/k210-sysctl.h`. It integrates parent sysctl with child clock/reset/syscon-like devices.

Risks and test signals: risks include hard-coded physical address mismatch, missing bus clock, and child population failure after the bus clock is enabled. Test signals are boot on K210 with full SRAM usable, `K210 system controller` probe log, child devices appearing, and no clock enable or ioremap panic failures.
