# sources/distributed-fs/glusterfs/xlators/features/upcall/src/Makefile.am

## Purpose
Builds the server-side `upcall.la` translator.

## Important APIs, Types, and Functions
- `if WITH_SERVER` gates module build.
- `upcall_la_SOURCES = upcall.c upcall-internal.c`.
- Links libglusterfs, gfrpc, and gfxdr.
- Installs under `xlator/features`.
- Headers include `upcall.h`, memory/message headers, and cache-invalidation constants.
- Uses `-fno-strict-aliasing`.

## Control Flow
Automake compiles upcall implementation and internal cache-invalidation support into one module.

## State and Persistence
No runtime state. Build artifacts are module and object files.

## Dependencies and Integration Points
Depends on server builds, libglusterfs, RPC libraries, and generated XDR headers because upcall notifications cross RPC/server boundaries.

## Risks
Missing RPC/XDR links break notification support. `-fno-strict-aliasing` suggests pointer-cast-sensitive code in the translator.

## Test Signals
Build `upcall.la`, package headers, and run server-side cache-invalidation tests.
