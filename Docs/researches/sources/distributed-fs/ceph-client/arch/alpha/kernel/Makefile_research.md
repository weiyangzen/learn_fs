<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/kernel/Makefile -->
## sources/distributed-fs/ceph-client/arch/alpha/kernel/Makefile

**Purpose:** Builds the Alpha kernel architecture objects. It selects common entry/trap/process/time/syscall/error/I/O objects, optional subsystem objects, and platform-specific core logic, board, IRQ, and machine-check files.

**Important APIs/types/functions:** `obj-y`, `obj-$(CONFIG_*)`, `always-$(KBUILD_BUILTIN)`, `asflags-y`, and `ccflags-y` assignments.

**Control flow:** Kbuild evaluates Alpha configuration symbols to decide whether to build a generic multi-platform kernel or a specific machine family. Generic builds include multiple core logic and board files; non-generic builds include only selected platform support.

**State and persistence behavior:** No runtime state; it determines linked kernel contents and therefore the available platform initialization paths.

**Dependencies and integration points:** Depends on Kbuild, Alpha Kconfig symbols, linker script generation, and source files in `arch/alpha/kernel`.

**Risks:** Missing object selections can produce kernels that boot but lack IRQ/core-logic/error support for a board. Generic versus non-generic conditional differences are easy to regress.

**Test signals:** Build Alpha generic and representative non-generic configs, verify `vmlinux.lds` generation, and boot platform-specific images.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/kernel/Makefile -->
