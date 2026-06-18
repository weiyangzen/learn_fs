# sources/distributed-fs/ceph-client/drivers/pmdomain/amlogic/Kconfig

Purpose: Kconfig menu for Amlogic PM-domain providers.

Important APIs/types/functions: defines `MESON_EE_PM_DOMAINS` for AO/HHI register-controlled Meson Everything-Else domains and `MESON_SECURE_PM_DOMAINS` for secure-monitor controlled A1/C1-family domains. Both select generic PM-domain support and OF provider support; the secure driver depends on `MESON_SM` and `HAVE_ARM_SMCCC`.

Control flow: no runtime flow; selects which Amlogic provider implementation is built.

State and persistence: `.config` controls built-in/module state and defaults to enabled on `ARCH_MESON`.

Dependencies/integration: consumed by `amlogic/Makefile`; dependencies match use of regmap/syscon for EE domains and secure monitor firmware calls for secure domains.

Risks: missing secure monitor dependency would build an unusable secure driver; missing OF/genpd selections would break providers for DT consumers.

Test signals: randconfig with `ARCH_MESON`, compile-test builds, and module names `meson-ee-pwrc`/`meson-secure-pwrc`.
