<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/apps/devel/lmdb/module.mk.in -->
## sources/distributed-fs/orangefs/src/apps/devel/lmdb/module.mk.in

**Purpose:** This make fragment conditionally adds internal LMDB development tools to the OrangeFS development-source build list.

**Important APIs, types, and functions:** It sets `DIR := src/apps/devel/lmdb` and, when `WANT_INTERNAL_LMDB` is `yes`, appends `mdb_copy.c`, `mdb_dump.c`, `mdb_load.c`, and `mdb_stat.c` to `DEVELSRC`.

**Control flow:** Build inclusion is entirely controlled by the make conditional. There are no generated targets or per-tool flags in this fragment.

**State and persistence:** It affects build graph state, not runtime state. Enabling internal LMDB causes these utilities to compile as part of development sources.

**Dependencies and integration points:** It integrates with the top-level make system via `DEVELSRC` and `WANT_INTERNAL_LMDB`, and assumes the LMDB headers/library are available through the internal LMDB configuration.

**Risks and edge cases:** If `WANT_INTERNAL_LMDB` is mis-set, tools may be omitted despite source presence or included without needed LMDB build products. Tests should inspect configured make output for both yes/no values and verify each listed source compiles when enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/apps/devel/lmdb/module.mk.in -->
