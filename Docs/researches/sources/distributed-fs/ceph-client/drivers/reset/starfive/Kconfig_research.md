# sources/distributed-fs/ceph-client/drivers/reset/starfive/Kconfig

Purpose: Kconfig definitions for StarFive JH71x0 common reset support and JH7100/JH7110 SoC drivers.

Important APIs/types/functions: `RESET_STARFIVE_JH71X0` is hidden common code. `RESET_STARFIVE_JH7100` depends on `ARCH_STARFIVE || COMPILE_TEST`; `RESET_STARFIVE_JH7110` depends on `CLK_STARFIVE_JH7110_SYS`, selects `AUXILIARY_BUS`, and both select common JH71x0 support.

Control flow: build-time only. Defaults follow `ARCH_STARFIVE`, producing built-in bool drivers.

State and persistence: generated kernel config selects which reset providers are compiled.

Dependencies and integration: ties reset support to StarFive architecture or clock-controller providers.

Risks and test signals: JH7110 reset devices require the clock driver to publish auxiliary devices. Test dependency-disabled configs, COMPILE_TEST, and JH7100/JH7110 independent selection.
