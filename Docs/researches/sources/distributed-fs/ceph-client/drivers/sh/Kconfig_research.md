# sources/distributed-fs/ceph-client/drivers/sh/Kconfig

Purpose: top-level Kconfig menu for SuperH and SH-Mobile specific drivers. It creates the "SuperH / SH-Mobile Driver Options" menu and includes the interrupt-controller Kconfig.

Important symbols: it sources `drivers/sh/intc/Kconfig`; no local config symbols are defined here. Control flow is Kconfig inclusion only: architecture Kconfig files include this menu, and this file delegates feature selection to subdirectories.

State and dependencies: no runtime state or persistence. Dependency is the Kconfig parser and the referenced `drivers/sh/intc/Kconfig` path. Integration point is the kernel configuration UI/build system, which exposes SH interrupt-controller options. Risks are mainly menu placement and stale source paths if the directory layout changes. Test signals are `make menuconfig` visibility and successful configuration parsing with SH/COMPILE_TEST combinations.
