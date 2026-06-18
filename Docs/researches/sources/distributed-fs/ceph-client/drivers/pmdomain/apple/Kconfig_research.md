# sources/distributed-fs/ceph-client/drivers/pmdomain/apple/Kconfig

Purpose: Kconfig fragment for Apple SoC PMGR power-state control.

Important APIs/types/functions: defines `APPLE_PMGR_PWRSTATE` under `ARCH_APPLE || COMPILE_TEST`, depending on `PM` and selecting `REGMAP`, `MFD_SYSCON`, `PM_GENERIC_DOMAINS`, and `RESET_CONTROLLER`.

Control flow: no runtime flow; enables Apple PMGR genpd/reset provider.

State and persistence: `.config` controls build inclusion.

Dependencies/integration: consumed by `apple/Makefile` and matches `pmgr-pwrstate.c` use of syscon regmaps, genpd, and reset controller APIs.

Risks: missing reset or regmap selections would break build/link; bool-only configuration means no module build coverage here.

Test signals: compile-test and Apple architecture builds with `CONFIG_APPLE_PMGR_PWRSTATE=y`.
