# sources/distributed-fs/ceph-client/drivers/pmdomain/amlogic/Makefile

Purpose: Kbuild mapping for Amlogic PM-domain drivers.

Important APIs/types/functions: builds `meson-ee-pwrc.o` for `CONFIG_MESON_EE_PM_DOMAINS` and `meson-secure-pwrc.o` for `CONFIG_MESON_SECURE_PM_DOMAINS`.

Control flow: no runtime flow.

State and persistence: build output follows `.config`.

Dependencies/integration: synchronized with `amlogic/Kconfig`.

Risks: stale object names cause Kconfig-visible drivers not to build.

Test signals: targeted `make drivers/pmdomain/amlogic/` with each symbol enabled.
