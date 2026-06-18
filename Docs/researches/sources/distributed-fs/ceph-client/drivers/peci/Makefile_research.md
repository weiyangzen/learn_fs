# sources/distributed-fs/ceph-client/drivers/peci/Makefile

Purpose: Builds the PECI core, optional PECI CPU driver, and controller subdirectory.

Important APIs and types: `peci-y` links `core.o`, `request.o`, `device.o`, and `sysfs.o` into `peci.o`. `obj-$(CONFIG_PECI)` includes the core. `peci-cpu-y` builds `cpu.o` into `peci-cpu.o`. `obj-y += controller/` descends into hardware controller builds.

Control flow: Build-system only; no runtime flow.

State and persistence: Object composition determines module boundaries and exported symbols available to controller drivers.

Dependencies and integration points: Driven by Kconfig symbols `CONFIG_PECI` and `CONFIG_PECI_CPU`; delegates controller selection to `drivers/peci/controller/Makefile`.

Risks: The controller directory is always visited, but its objects are gated internally. Core object list must stay in sync with PECI subsystem source files and exported namespace expectations.

Test signals: `make drivers/peci/` with PECI built-in and modular configurations, expected module names, and successful controller linkage against core symbols.
