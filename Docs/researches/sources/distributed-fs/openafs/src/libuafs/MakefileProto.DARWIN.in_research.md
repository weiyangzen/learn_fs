## sources/distributed-fs/openafs/src/libuafs/MakefileProto.DARWIN.in

Purpose: Defines Darwin/macOS flags for the common libuafs build.

Important variables: `DEFINES=-D_REENTRANT -DKERNEL -DUKERNEL`, empty `KOPTS`, `UAFS_CFLAGS=$(ARCHFLAGS)`, `TEST_CFLAGS` with pthread environment and architecture flags, `TEST_LDFLAGS=$(XLDFLAGS) $(ARCHFLAGS)`, and empty `TEST_LIBS`.

Control flow: Includes config and install substitutions, sets platform flags, then includes `Makefile.common` for the actual build graph.

State and persistence: Build artifacts are those produced by common rules. Architecture flags propagate to library objects, `linktest`, and optional SWIG binding compilation.

Dependencies and integration: Integrates with Darwin multi-architecture support in `lwp/Makefile.in` and libtool configuration. `ARCHFLAGS` is the key platform-specific input.

Risks: Missing or inconsistent `ARCHFLAGS` can produce linktest or binding architecture mismatches. Empty `TEST_LIBS` assumes system libraries satisfy pthread and runtime needs via compiler/linker defaults.

Test signals: Single-arch and multi-arch Darwin builds, linktest execution/link success, optional Perl binding architecture compatibility, and install packaging.
