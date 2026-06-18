# sources/distributed-fs/ceph-client/drivers/clk/nuvoton/Kconfig

Purpose: Defines Kconfig selection for Nuvoton common clock support and the MA35D1 clock controller.

Important APIs, types, and functions: `COMMON_CLK_NUVOTON` is a bool gated by `ARCH_MA35 || COMPILE_TEST` and defaults to `ARCH_MA35`. Inside it, `CLK_MA35D1` enables the MA35D1 clock controller and also defaults to `ARCH_MA35`.

Control flow: Kconfig controls whether the Nuvoton clock directory builds the MA35D1 objects. The nested `if COMMON_CLK_NUVOTON` prevents selecting the SoC driver without the common family gate.

State and persistence: No runtime state; this file affects kernel configuration and object inclusion.

Dependencies and integration points: Integrates with architecture selection for MA35 and compile-test coverage for broader build validation.

Risks: Since both symbols are bool, the MA35D1 clock driver is built-in when enabled, matching its `postcore_initcall()` registration. Configurations that need modular clock support are not supported by this file.

Test signals: `ARCH_MA35=y` should default-enable both symbols. `COMPILE_TEST=y` should allow build coverage on other architectures. Disabling `CLK_MA35D1` should omit all MA35D1 clock objects.
