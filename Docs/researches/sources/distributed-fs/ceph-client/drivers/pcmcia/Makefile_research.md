# sources/distributed-fs/ceph-client/drivers/pcmcia/Makefile

Purpose: Describes how the PCMCIA subsystem objects are assembled into kernel modules and built-in objects. It groups core socket services, 16-bit driver services, resource managers, and board/socket controller drivers.

Important APIs and targets: `pcmcia_core-y` includes `cs.o` and `socket_sysfs.o`; `pcmcia_core-$(CONFIG_CARDBUS)` adds `cardbus.o`. The `pcmcia` module includes `ds.o`, `pcmcia_resource.o`, `cistpl.o`, and `pcmcia_cis.o`. `pcmcia_rsrc` combines `rsrc_mgr.o` and optional `rsrc_nonstatic.o`. Driver objects are selected by symbols such as `CONFIG_YENTA`, `CONFIG_PCMCIA_BCM63XX`, `CONFIG_OMAP_CF`, `CONFIG_ELECTRA_CF`, and `CONFIG_PCMCIA_MAX1600`.

Control flow: Build-time only. Kconfig selects symbols, kbuild links matching objects into modules or built-ins, and composite `*-y` variables define internal module composition.

State and persistence: The Makefile persists the binary/module boundaries. These boundaries affect exported symbols and load order: `pcmcia_core`, `pcmcia`, and `pcmcia_rsrc` are separate logical units.

Dependencies and integration points: Integrates with Kbuild and with the Kconfig symbols in this folder. The split mirrors runtime layering: socket core, driver services, resource manager, and host socket drivers.

Risks: Missing an object from a composite module can cause unresolved symbols only under specific configs. Moving files between modules must account for exported symbols between `pcmcia_core` and `pcmcia`.

Test signals: Build all major configurations as modules and built-in, verify `modpost` has no unresolved symbols or section mismatch warnings, and confirm selected socket drivers produce expected `.ko` names.
