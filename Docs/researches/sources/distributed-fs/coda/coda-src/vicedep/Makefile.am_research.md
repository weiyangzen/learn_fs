# sources/distributed-fs/coda/coda-src/vicedep/Makefile.am

## Purpose

`sources/distributed-fs/coda/coda-src/vicedep/Makefile.am` defines the automake build for generated RPC2 dependency libraries shared by Venus, the file server, and volume utilities.

## Important APIs, Types, and Functions

It declares `libvenusdep.la` unconditionally and `libvicedep.la`/`libvolutildep.la` under `BUILD_SERVER`. It publishes `operations.h`, `recov_vollog.h`, `srv.h`, `venusioctl.h`, and `voltypes.h` as local headers. `RPC2_FILES` lists `callback.rpc2`, `cml.rpc2`, `mond.rpc2`, `res.rpc2`, `vcrcommon.rpc2`, `vice.rpc2`, `voldump.rpc2`, and `volutil.rpc2`, with generated client/server/multi/helper C sources assigned to the noinst libraries.

## Control Flow

There is no runtime control flow. At build time it includes `configs/rpc2_rules.mk`, which generates RPC2 stubs and helpers; automake then compiles the appropriate generated sources into private libraries for the selected build configuration.

## State and Persistence Behavior

No runtime state is owned here. The file controls generated build artifacts in the build tree and determines which generated protocol interfaces are linked into clients/server utilities.

## Dependencies and Integration Points

It depends on automake/libtool, the repository RPC2 generation rules, `$(RPC2_CFLAGS)`, and build-conditional `BUILD_SERVER`. It is the build integration point for the headers and generated stubs consumed by `vice`, `vol`, Venus, and volutil code.

## Risks and Edge Cases

Generated `nodist_*` sources must match the `.rpc2` files and include paths; missing regeneration can cause stale protocol stubs. Server-only libraries disappear when `BUILD_SERVER` is false, so consumers must be correctly guarded. Long source lists are easy to drift when adding an RPC interface.

## Test Signals

Run autoreconf/configure and both server-enabled and client-only builds; verify generated RPC2 files exist, the noinst libraries contain expected stubs, and incremental rebuilds happen when `.rpc2` files change.
