<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/gcov/Makefile -->
# sources/distributed-fs/ceph-client/kernel/gcov/Makefile

Purpose: builds the kernel gcov support objects and passes source/object tree paths to the implementation for debugfs path generation and coverage data export.

Important APIs/types/functions: `ccflags-y` defines `SRCTREE` and `OBJTREE`. `obj-y` always includes `base.o` and `fs.o` when the directory is built. GCC builds add `gcc_base.o` and `gcc_4_7.o`; Clang builds add `clang.o`. Compiler-specific objects suppress missing-prototype and missing-declaration warnings because they expose compiler-runtime callback shapes.

Control flow: this is build-time only. Kbuild selects compiler-specific backend objects through `CONFIG_CC_IS_GCC` or `CONFIG_CC_IS_CLANG`, while shared gcov list/event and filesystem support are always compiled for the gcov directory.

State and persistence behavior: no Makefile runtime state exists. The emitted macros persist into compiled objects, letting runtime code know the original source and object tree roots for exported coverage paths.

Dependencies and integration points: depends on compiler selection Kconfig symbols, the gcov base/fs implementation, and compiler-format-specific backends. It integrates with the Kconfig options that decide whether this directory is reachable and with debugfs consumers that expect stable source/object path metadata.

Risks: wrong compiler backend selection would break coverage data format parsing. Incorrect `SRCTREE`/`OBJTREE` quoting would produce unusable debugfs paths. Warning suppressions should stay limited to backend files that intentionally match compiler-generated interfaces.

Test signals: GCC and Clang gcov builds, debugfs path inspection, coverage extraction with source/object tree relocation, W=1 builds verifying warning scope, and build tests with per-file `GCOV_PROFILE` flags.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/gcov/Makefile -->
