# sources/distributed-fs/glusterfs/libglusterfs/src/Makefile.am

Purpose: Main Automake recipe for building `libglusterfs.la`, installing public GlusterFS headers, and generating parser/default/event headers for the core library.

Important build declarations: Builds `lib_LTLIBRARIES = libglusterfs.la` from a large source list covering dicts, xlators, logging, event loops, memory pools, graph parsing, syncops, monitoring, async threading, and I/O backends. Conditional sources include bundled `xxhash`, `libexecinfo`, `run.c` versus `run_fork.c`, events, and io_uring. Public headers install under `$(includedir)/glusterfs`; changelog header installs under a gfchangelog include dir. `nodist` sources include generated `y.tab.c`, `graph.lex.c`, and `defaults.c`.

Control flow: Build generates `eventtypes.h`, parser lexer/YACC outputs, and `defaults.c` before compiling. Link flags set libtool versioning and export symbols from `libglusterfs.sym`. Conditional sections adapt to platform/library availability and build options.

State and persistence: Produces the installed shared library and public headers. Generated files are cleaned via `CLEANFILES`; unit-test mode adds coverage and xunit cleanup patterns.

Dependencies and integration: Links zlib, math, UUID, dl, userspace-RCU, RCU CDS, resolver, and optional contrib libraries. Provides the core APIs consumed by `glusterfsd`, translators, RPC code, and helpers. Compile-time macros define xlator directories, sbindir, large-file behavior, and namespace selection for xxhash.

Risks: Source/header list drift can break installed API or omit objects from the library. Generated parser dependencies must be ordered correctly for parallel builds. Conditional bundled-library paths must match configure checks. Export-symbol mismatch can hide new APIs.

Test signals: `make -j`, `make distcheck`, install-header checks, ABI/export checks, and builds across feature combinations (`BUILD_EVENTS`, `BUILD_LINUX_IO_URING`, missing libxxhash/backtrace) are the primary validation.
