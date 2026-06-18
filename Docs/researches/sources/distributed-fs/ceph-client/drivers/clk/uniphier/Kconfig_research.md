# sources/distributed-fs/ceph-client/drivers/clk/uniphier/Kconfig

Purpose: Kconfig option for the UniPhier clock controller driver.

Important APIs/types/functions: defines `CONFIG_CLK_UNIPHIER` as a boolean prompt "Clock driver for UniPhier SoCs". It depends on `ARCH_UNIPHIER || COMPILE_TEST`, and also on `OF && MFD_SYSCON`; it defaults to `ARCH_UNIPHIER`.

Control flow: build-time only. Enabling the option compiles the UniPhier clock driver objects listed by the local Makefile.

State and persistence: no runtime state. The config gates whether built-in platform clock drivers are present.

Dependencies/integration: captures required OF and syscon/regmap infrastructure for the table-driven clock provider.

Risks: disabling the option on UniPhier prevents system, media I/O, peripheral, and SoC-glue clocks from registering. The option is bool rather than tristate, matching builtin platform driver usage.

Test signals: Kconfig dependency resolution for UniPhier and COMPILE_TEST builds, and build coverage with OF/syscon disabled to confirm the option is hidden.
