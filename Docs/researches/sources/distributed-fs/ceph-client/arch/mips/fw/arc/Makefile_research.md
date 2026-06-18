# sources/distributed-fs/ceph-client/arch/mips/fw/arc/Makefile

Purpose: selects ARC PROM monitor library routines for MIPS firmware support.

Important build behavior: with `CONFIG_ARC_CMDLINE_ONLY`, only `cmdline.o` is built. Otherwise the core library includes command line, environment, file, identify, init, and misc helpers. Optional objects are selected by `CONFIG_ARC_MEMORY`, `CONFIG_ARC_CONSOLE`, and `CONFIG_ARC_PROMLIB`.

Dependencies and integration: this Makefile supports platforms using ARC firmware services for early command line, memory discovery, console, file access, and PROM library calls.

Risks and test signals: selecting command-line-only mode intentionally omits memory and console helpers, so platform code must not call them. Build test ARC configurations with each optional feature combination.
