<!-- Source: sources/distributed-fs/ceph-client/fs/netfs/fscache_internal.h -->
# sources/distributed-fs/ceph-client/fs/netfs/fscache_internal.h

## Purpose
Tiny compatibility header that includes netfs `internal.h` and changes `pr_fmt()` to report `FS-Cache:` rather than `netfs:`. It exists so FS-Cache-specific implementation files can share the central internal declarations while using cache-specific printk prefixes.

## Important APIs, Types, And Functions
No functions or types are declared here beyond the inherited contents of `internal.h`. Its only local behavior is undefining any existing `pr_fmt` and redefining it as `#define pr_fmt(fmt) "FS-Cache: " fmt`.

## Control Flow
There is no runtime control flow. The file participates at preprocessing time: include `internal.h`, reset the logging prefix, and let FS-Cache source files compile with the shared internal API surface.

## State And Persistence
No state is owned. It indirectly exposes all state declared in `internal.h`, including netfs pools, request lists, FS-Cache stats, cache state helpers, cookie/volume declarations, and debug macros.

## Dependencies And Integration Points
Depends directly on sibling `internal.h`. It integrates with FS-Cache implementation files that want netfs internals plus a cache-specific log prefix.

## Risks
The main risk is include-order confusion. Because it includes `internal.h` before redefining `pr_fmt`, any logging macros expanded inside included headers keep their own definitions, while later source logging uses `FS-Cache:`. It should stay minimal to avoid divergent declarations from `internal.h`.

## Test Signals
Build coverage is the useful signal. Compile FS-Cache files with and without debug enabled and verify messages from files including this header use the expected prefix.
