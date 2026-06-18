# sources/distributed-fs/ceph-client/drivers/pmdomain/actions/Kconfig

Purpose: Kconfig fragment for Actions Semiconductor Owl Smart Power System power-domain support.

Important APIs/types/functions: under `ARCH_ACTIONS || COMPILE_TEST`, defines hidden bool `OWL_PM_DOMAINS_HELPER` and user-visible bool `OWL_PM_DOMAINS`. The main symbol depends on `PM`, selects the helper and `PM_GENERIC_DOMAINS`, and describes S500/S700/S900 SPS power gating.

Control flow: no runtime flow. Configuration enables helper and platform provider objects.

State and persistence: symbol choices persist in `.config`.

Dependencies/integration: consumed by `drivers/pmdomain/actions/Makefile`, which builds `owl-sps-helper.o` for the helper and `owl-sps.o` for the provider.

Risks: the helper is exported for reuse, so it must be selected whenever the main driver builds. Missing `PM_GENERIC_DOMAINS` would cause unresolved genpd dependencies.

Test signals: compile with `ARCH_ACTIONS`, compile-test builds, and verifying `CONFIG_OWL_PM_DOMAINS=y` also sets `CONFIG_OWL_PM_DOMAINS_HELPER=y`.
