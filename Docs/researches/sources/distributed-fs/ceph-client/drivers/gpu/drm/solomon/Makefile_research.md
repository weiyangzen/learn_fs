# sources/distributed-fs/ceph-client/drivers/gpu/drm/solomon/Makefile

Purpose: maps Solomon SSD130x Kconfig symbols to build objects.

Important APIs/types/functions: no runtime API. Builds `ssd130x.o`, `ssd130x-i2c.o`, and `ssd130x-spi.o` from their matching config symbols.

Control flow: Kbuild includes the shared core and selected transports.

State and persistence: no state.

Dependencies and integration: must align with namespace exports/imports in the core and transport modules.

Risks: transport modules require core symbols; incorrect symbol selection would fail module linking or probing.

Test signals: module and built-in builds for each symbol combination.
