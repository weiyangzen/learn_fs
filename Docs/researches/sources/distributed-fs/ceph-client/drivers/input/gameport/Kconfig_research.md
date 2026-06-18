# sources/distributed-fs/ceph-client/drivers/input/gameport/Kconfig

This Kconfig file defines the legacy PC gameport subsystem and hardware-specific gameport providers. `GAMEPORT` is a tristate root option disabled on UML, with help text explaining the 15-pin PC gameport and sound-card gameport use cases. Under `if GAMEPORT`, it offers `GAMEPORT_NS558`, `GAMEPORT_L4`, `GAMEPORT_EMU10K1`, and `GAMEPORT_FM801`.

The dependency graph is the important behavior. ISA-only drivers (`NS558`, `L4`) depend on `ISA`; PCI drivers depend on `PCI`, and `FM801` additionally requires `HAS_IOPORT`. These symbols drive the gameport Makefile and determine whether the generic `gameport.o` core and specific bridge drivers are built in or as modules. There is no runtime state here, but the file is a persistence point for kernel configuration and controls module names documented in the help text.

Integration points are joystick drivers that `select GAMEPORT`, platform bus availability, PCI/ISA probing, and distro kernel configuration. Risks are stale help text, dependencies that allow building a driver without required I/O primitives, or missing `select GAMEPORT` from consumers. Test signals are Kconfig resolution across `allyesconfig`, `allmodconfig`, `UML`, PCI-disabled, ISA-disabled, and no-IOPORT configurations, plus ensuring selected module names match Makefile objects.
