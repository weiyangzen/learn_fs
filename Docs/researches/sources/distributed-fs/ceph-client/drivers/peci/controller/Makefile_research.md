# sources/distributed-fs/ceph-client/drivers/peci/controller/Makefile

Purpose: Builds selected PECI hardware controller drivers.

Important APIs and types: Adds `peci-aspeed.o` when `CONFIG_PECI_ASPEED` is enabled and `peci-npcm.o` when `CONFIG_PECI_NPCM` is enabled.

Control flow: Build-system only.

State and persistence: Determines which platform-driver modules are linked for PECI controller support.

Dependencies and integration points: Consumed from the top-level PECI Makefile's `controller/` descent and tied to controller Kconfig symbols.

Risks: Object names must match source files and module aliases; adding a controller requires both Kconfig and Makefile updates.

Test signals: Selected objects appear in build output and can link against the PECI core when built as modules or built-in.
