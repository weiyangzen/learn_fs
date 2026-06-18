# sources/distributed-fs/glusterfs/xlators/features/metadisp/src/Makefile.am

## Purpose

This Automake file builds the `metadisp.la` xlator module and generates `fops.c` from `fops-tmpl.c` plus `gen-fops.py`.

## Important APIs, Types, and Functions

Key build variables are `xlator_LTLIBRARIES = metadisp.la`, `xlatordir`, `nodist_metadisp_la_SOURCES = fops.c`, `BUILT_SOURCES = fops.c`, `metadisp_la_SOURCES`, `metadisp_la_LIBADD`, `noinst_HEADERS`, `AM_CPPFLAGS`, and `AM_CFLAGS`. The generation rule runs `$(PYTHON) $(srcdir)/gen-fops.py $(srcdir)/fops-tmpl.c > $@` with `PYTHONPATH` pointed at libglusterfs generator helpers.

## Control Flow

Build flow first generates `fops.c`, then compiles it together with the hand-written metadisp fop files and links the translator module against `libglusterfs.la`.

## State and Persistence Behavior

`fops.c` is generated build state, listed in `CLEANFILES` through `$(nodist_metadisp_la_SOURCES)`. It is not distributed as source.

## Dependencies and Integration Points

The file integrates with GlusterFS xlator install layout under `$(libdir)/glusterfs/$(PACKAGE_VERSION)/xlator/features`, libglusterfs headers, XDR headers, and the shared Python generator in `libglusterfs/src/generator.py`.

## Risks and Edge Cases

Generated and hand-written fop coverage must stay synchronized. Missing `generator.py`, a Python interpreter mismatch, or a broken `#pragma generate` template prevents the xlator from compiling. Because `fops.c` is nodist, source tarball consumers must be able to regenerate it.

## Test Signals

Run the autotools build from a clean tree, verify `fops.c` is generated, compile `metadisp.la`, run `make clean` to ensure generated files are removed, and check that installed xlator path matches other feature translators.
