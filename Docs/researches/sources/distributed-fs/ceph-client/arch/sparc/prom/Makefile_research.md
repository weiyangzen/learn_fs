# sources/distributed-fs/ceph-client/arch/sparc/prom/Makefile

Purpose: defines the SPARC PROM library object set for 32-bit and 64-bit builds.

Important APIs/targets: always includes bitness-specific `bootstr`, `init`, `misc`, `console`, `printf`, and `tree` objects. SPARC32 adds `memory.o`, `mp.o`, and `ranges.o`; SPARC64 adds IEEE-1275 `p1275.o` and `cif.o`.

Control flow: kbuild selects implementation variants through `$(BITS)` and `CONFIG_SPARC32`/`CONFIG_SPARC64`.

State and persistence: no runtime state; controls which PROM library symbols are linked.

Dependencies and integration points: integrates early boot, device-tree access, console, PROM calls, and architecture setup code.

Risks: wrong bitness object selection breaks boot-time PROM access. Missing 64-bit CIF or 32-bit ROM vector support prevents early console and device-tree discovery.

Test signals: build sparc32 and sparc64 defconfigs, check PROM symbol resolution, early boot console output, and device-tree probing.
