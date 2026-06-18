# sources/distributed-fs/ceph-client/drivers/siox/Makefile

Purpose: Kbuild object selection for SIOX.

Important build rules: `CONFIG_SIOX` builds `siox-core.o`; `CONFIG_SIOX_BUS_GPIO` builds `siox-bus-gpio.o`.

Control flow and integration: client SIOX drivers link against symbols exported by `siox-core.o`, while the GPIO master registers a `siox_master` when its platform device probes.

State and dependencies: no runtime state. Dependencies are Kbuild and Kconfig symbols. Risks are symbol availability if a bus master is built without core support, normally handled by Kconfig menu nesting. Test signals are successful modular and built-in combinations, exported SIOX symbols resolving, and module aliases for the GPIO platform driver.
