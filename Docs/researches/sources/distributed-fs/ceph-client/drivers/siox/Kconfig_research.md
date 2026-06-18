# sources/distributed-fs/ceph-client/drivers/siox/Kconfig

Purpose: configuration menu for Eckelmann SIOX bus support and its GPIO master.

Important symbols: `SIOX` is a tristate menuconfig for the SIOX bus core. `SIOX_BUS_GPIO` is a tristate child option for bit-banging a SIOX bus over four GPIO lines.

Control flow: enabling `SIOX` builds the core, and enabling `SIOX_BUS_GPIO` builds the platform GPIO master driver. The help text documents that SIOX is a synchronous I/O extension bus used in industrial refrigeration systems.

State and dependencies: no runtime state. Dependencies are Kconfig and the matching Makefile. The GPIO driver implicitly depends on GPIOLIB through its source includes but no explicit Kconfig dependency is declared here. Risks include users selecting GPIO support without the needed GPIO provider in unusual builds. Test signals are Kconfig visibility, module selection for core and GPIO driver, and allmodconfig build coverage.
