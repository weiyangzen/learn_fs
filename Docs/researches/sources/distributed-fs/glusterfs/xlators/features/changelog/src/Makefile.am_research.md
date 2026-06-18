# sources/distributed-fs/glusterfs/xlators/features/changelog/src/Makefile.am

## Purpose
Builds the changelog feature xlator module and declares its source, private headers, dependencies, and compiler flags.

## APIs, Types, and Functions
Declares `changelog.la` under `xlator_LTLIBRARIES`, installs it in the GlusterFS feature xlator directory, and lists sources: `changelog.c`, `changelog-rt.c`, `changelog-helpers.c`, `changelog-encoders.c`, `changelog-rpc.c`, `changelog-barrier.c`, `changelog-rpc-common.c`, and `changelog-ev-handle.c`. `noinst_HEADERS` lists internal headers such as helpers, memory types, RPC, event handling, encoders, misc constants, and messages.

## Control Flow, State, and Persistence
There is no runtime control flow. Build-time state is the automake recipe: module LDFLAGS, libglusterfs/gfxdr/gfrpc link dependencies, include paths to libglusterfs, RPC XDR, RPC transport socket, and the changelog library source directory. It forces `-fPIC`, 64-bit file offsets, `_GNU_SOURCE`, and `DATADIR`.

## Dependencies and Integration
Integrates the xlator with libglusterfs, RPC XDR, and RPC library artifacts. The include path to `xlators/features/changelog/lib/src` allows the xlator and libgfchangelog to share constants and RPC common headers.

## Risks and Test Signals
Risks include duplicated `changelog-rpc-common.h` in `noinst_HEADERS`, missing source entries when new helpers are added, and include-path coupling to the library implementation tree. Test signals are successful automake/configure builds, module load tests, and link failures catching missing RPC/XDR dependencies.
