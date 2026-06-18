# sources/distributed-fs/openafs/src/afs/afs_prototypes.h

## Purpose

`afs_prototypes.h` is the main internal prototype aggregation header for the non-Windows OpenAFS cache manager. It does not implement behavior; it publishes cross-file globals, function declarations, platform-specific syscall/vnode signatures, helper macros, and a few small type/flag definitions so the cache-manager modules can call each other consistently across Unix kernels and UKERNEL builds.

## Important APIs, types, and functions

The header is organized by source module. Major groups include request/error handling (`afs_Analyze`, `afs_CheckCode`), initialization/shutdown, cell/volume/server/connection management, dcache and fetch/store interfaces, pioctl entry points, credential/PAG/token support, vcache/vnode operations, OSI allocation/sleep/file/VM abstractions, generated UUID helpers, and platform VFS roots.

For this subset, the key declarations are `afs_syscall_pioctl`, platform-specific `afs_xioctl`, `HandleIoctl`, and the segment APIs `afs_StoreAllSegments`, `afs_InvalidateAllSegments`, `afs_InvalidateAllSegments_once`, `afs_ExtendSegments`, and `afs_TruncateAllSegments`. It also defines `enum afs_shutdown_type` and `afs_stalevc_flags_t` with `AFS_STALEVC_*` flags used by vcache invalidation.

## Control flow

Runtime control flow is indirect. The file's main role is compile-time wiring: modules include it through the OpenAFS include stack, and conditional blocks select signatures for Solaris, Linux, Darwin/BSD, AIX, SGI, UKERNEL, and other environments. The declarations mirror cache-manager execution: syscalls/vnode ops create requests, pioctls and vnode ops validate vcaches, dcache/fetchstore code moves file data, RX connection/server/volume code contacts fileservers, callbacks and DNLC maintain coherency, and shutdown paths unwind initialized modules.

## State and persistence behavior

The header exposes many kernel-lifetime globals, including cache sizing and dcache tables, cell/server/volume tables and locks, callback counters/interface state, user/token tables, vcache LRU/hash lists, system-name state, PAG counters, mariner monitor state, stats structures, and global VFS/root vnode pointers. It does not itself persist data, but declarations refer to cache metadata files/inodes and functions that mutate local cache files or server-side state.

## Dependencies and integration points

`afs_prototypes.h` depends on prior definitions for OpenAFS core structs, vnode/credential types, locks, RX types, and AFS RPC structures. It ends by including `osi_prototypes.h` for supported environments. It is the integration map tying `afs_pioctl.c` and `afs_segments.c` to vcache, dcache, fetchstore, VM, server, volume, token, request, and OSI implementations.

## Risks and edge cases

- A small signature mismatch can break multiple platforms or silently select the wrong ABI.
- Platform-specific declarations use old kernel ABI types and require broad build coverage.
- The `afs_xioctl` declaration block contains a likely typo, `AFS_DAWRIN_ENV`, where surrounding code uses `AFS_DARWIN_ENV`.
- Writable globals are exposed widely, making invariants hard to enforce.
- Duplicate declarations and include-order dependencies increase maintenance risk.

## Test signals

The strongest signals are cross-platform compile/static-analysis runs for all conditional branches, prototype-vs-definition checks for pioctl and segment functions, ABI review for syscall/vnode declarations, and header hygiene checks for duplicate prototypes, misspelled platform macros, and globals without a single owning definition.
