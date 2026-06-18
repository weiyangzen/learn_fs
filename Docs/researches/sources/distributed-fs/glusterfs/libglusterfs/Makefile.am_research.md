# sources/distributed-fs/glusterfs/libglusterfs/Makefile.am

Purpose: Automake dispatcher for the core `libglusterfs` subtree.

Important build declarations: `SUBDIRS = src` delegates all library compilation, generated sources, and header installation to `libglusterfs/src`. `CLEANFILES =` is empty at this directory level.

Control flow: Recursive Automake targets enter `src`. This file has no conditionals or local targets.

State and persistence: No runtime state and no installed files directly from this level.

Dependencies and integration: Integrates the core library source directory into the top-level GlusterFS build. All substantive dependencies are defined in `src/Makefile.am`.

Risks: Low. New files placed directly under `libglusterfs/` would be invisible to the build unless rules are added.

Test signals: Build traversal through `src` during `make`, `make clean`, and distribution targets.
