# sources/distributed-fs/ceph-client/drivers/clk/eswin/Kconfig

Purpose: declares ESWIN clock-controller Kconfig options.

Important APIs/types/functions: `COMMON_CLK_ESWIN` is an internal boolean selected by SoC drivers. `COMMON_CLK_EIC7700` is a tristate user-visible driver option depending on `ARCH_ESWIN || COMPILE_TEST`, selecting `COMMON_CLK_ESWIN` and defaulting to `ARCH_ESWIN`.

Control flow: configuration controls whether shared ESWIN clock helpers and the EIC7700 provider are compiled.

State and persistence: no runtime state.

Dependencies and integration points: ties ESWIN architecture selection and compile-test coverage to `drivers/clk/eswin/Makefile`, which builds `clk.o` for common helpers and `clk-eic7700.o` for the SoC provider.

Risks: `COMMON_CLK_ESWIN` has no prompt, so helper code is only built when selected. The EIC7700 driver is tristate, while its helper selection is bool; module/built-in combinations need link coverage.

Test signals: run `allyesconfig`/`allmodconfig`/`COMPILE_TEST` builds and an `ARCH_ESWIN` default build to ensure helper/provider symbols link in both built-in and module configurations.
