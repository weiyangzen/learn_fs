# sources/distributed-fs/ceph-client/drivers/net/wan/framer/Makefile

Purpose: build rules for the framer subsystem directory.

Important APIs, types, and functions: maps `CONFIG_GENERIC_FRAMER` to `framer-core.o` and `CONFIG_FRAMER_PEF2256` to the `pef2256/` subdirectory.

Control flow: during kbuild, object inclusion follows the selected Kconfig symbols. The PEF2256 directory is entered only when its driver is enabled.

State and persistence: build-only file with no runtime state.

Dependencies and integration points: depends on symbols defined in the adjacent Kconfig. It is the bridge from subsystem selection to the core framework and provider driver.

Risks: if additional framer drivers are added, they must be placed under the correct symbol and should select or depend on `GENERIC_FRAMER` consistently. Misalignment with Kconfig would produce missing symbols or unused objects.

Test signals: build matrix with generic core only and with PEF2256 enabled as built-in/module.
