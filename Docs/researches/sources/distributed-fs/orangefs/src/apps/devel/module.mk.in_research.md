<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/apps/devel/module.mk.in -->
## sources/distributed-fs/orangefs/src/apps/devel/module.mk.in

**Purpose:** This make fragment adds development utility sources and defines the generated-source set for the memory analysis tool.

**Important APIs, types, and functions:** It sets `DIR := src/apps/devel`, appends `pvfs2-db-display.c` and `pvfs2-remove-prealloc.c` to `DEVELSRC`, defines `MEMANALYSIS := $(DIR)/mem_analysis`, lists `MEMANALYSISSRC` as `mem_analysis.c`, generated parser C, and generated scanner C, and lists `MEMANALYSISGEN` as scanner/parser generated outputs. `.SECONDARY` preserves generated files.

**Control flow:** The fragment contributes variables to the broader automake/make include system; it does not itself define commands in the visible lines.

**State and persistence:** It affects build products and generated parser/scanner artifacts. `.SECONDARY` prevents automatic deletion of generated files that may be useful for debugging or incremental builds.

**Dependencies and integration points:** It integrates the mem-analysis flex/yacc pipeline with the repository build and adds devel utilities to `DEVELSRC`.

**Risks and edge cases:** If generation rules are elsewhere and out of sync with `MEMANALYSISGEN`, builds may use stale generated parser/scanner files. Tests should run clean-tree generation, incremental rebuilds after `.y`/`.l` edits, and builds with generated files absent.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/apps/devel/module.mk.in -->
