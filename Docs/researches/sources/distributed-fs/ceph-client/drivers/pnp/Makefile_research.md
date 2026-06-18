<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pnp/Makefile -->
# sources/distributed-fs/ceph-client/drivers/pnp/Makefile

Purpose: Kbuild composition for the PnP subsystem.

Important APIs/types/functions: always builds aggregate `pnp.o` from `core.o card.o driver.o resource.o manager.o support.o interface.o quirks.o system.o`. Adds `pnpacpi/`, `pnpbios/`, and `isapnp/` subdirectories based on config.

Control flow/state: build-time only. Comment notes `system.o` is appended after protocol init ordering concerns.

Dependencies/integration: ties the PnP bus core to resource management, sysfs interface, quirks, and protocol backends.

Risks: object order may matter for initcall behavior and symbol availability.

Test signals: compile each protocol combination and ensure `pnp_system_init` ordering remains valid.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pnp/Makefile -->
