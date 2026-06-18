# sources/distributed-fs/openafs/src/afs/afs_segments.c

## Purpose

`afs_segments.c` manages the cache manager's per-file data segments: storing dirty dcaches back to fileservers, issuing minimal truncation/extension stores, invalidating cached chunks, extending local cache chunks with zeroes, and truncating local cached chunks. It bridges vnode-level file size changes, VM page flushing, local dcache metadata, and RXAFS store RPCs.

## Important APIs, types, and functions

- `afs_StoreMini` sends a minimal `StoreData`/`StoreData64` request when only length/truncation metadata must reach the fileserver.
- `afs_StoreAllSegments` stores all dirty chunks for a vcache, updates data versions, clears dirty state when safe, and handles post-error invalidation.
- `afs_InvalidateAllSegments_once` performs one invalidation pass over all matching dcaches.
- `afs_InvalidateAllSegments` retries invalidation through background daemon requests until it succeeds after fatal store failures.
- `afs_ExtendSegments` extends local cached chunks by writing zero pages.
- `afs_TruncateAllSegments` truncates local cache/VM state or marks a pure extension for later store.
- Globals include `afs_stampValue`, `NCHUNKSATONCE`, and `afs_dvhack`.

## Control flow

`afs_StoreAllSegments` starts with the vcache write-locked, flushes VM pages unless sync flags suppress it, rejects disconnected non-sync stores, snapshots the starting data version/callback count, downgrades the vcache lock, and repeatedly scans the dcache DV hash for `IFDataMod` chunks matching the FID. It batches up to `NCHUNKSATONCE` chunk slots and calls `afs_CacheStoreVCache` to store them. After dirty data stores, it upgrades the vcache lock, calls `afs_StoreMini` if truncation/extension still needs a server-side length update, then relabels eligible dcaches and clears `DWriting`.

`afs_StoreMini` computes the target length from current length and `truncPos`, clears extension/truncation markers, obtains a fileserver connection, prefers `StoreData64`, falls back to 32-bit `StoreData` on `RXGEN_OPCODE`, and processes returned fetch status on success.

Invalidation clears vcache truncation/extension/dirty state, gathers matching dcaches under `afs_xdcache`, clears dirty/page index flags, then zaps each dcache. If the one-shot invalidator fails, `afs_InvalidateAllSegments` warns and retries every ten seconds via `BOP_INVALIDATE_SEGMENTS`.

Extension writes zero-filled pages to local cache files until `validPos` and `avc->f.m.Length` reach the requested length. Truncation performs VM truncation, updates `truncPos`, gathers dcaches for the file, and truncates local cache files and validity metadata beyond the new EOF.

## State and persistence behavior

Server persistence happens through `RXAFS_StoreData`/`StoreData64` in `afs_StoreMini` and through `afs_CacheStoreVCache` in the full-store path. Local persistent cache state includes dcache file sizes, `chunkBytes`, `validPos`, dirty flags, `DWriting`, `DFEntryMod`, dcache data versions, and index flags. Vcache state changed here includes file length/date, `truncPos`, `CExtendedFile`, `CDirty`, `mapDV`, and stale/dirty markers.

The invalidation retry loop is deliberately blocking from a correctness perspective: after failed stores, bad local chunks must be removed before the client can safely continue serving data.

## Dependencies and integration points

This file depends on dcache hash/index state, fetchstore (`afs_CacheStoreVCache`), vcache status processing, RXAFS RPC stubs, connection retry analysis, VM hooks, local cache file operations, background daemon queues, tracing/statistics, and disconnected-mode globals. Its public functions are declared in `afs_prototypes.h` and are used by vnode write, setattr/truncate, close/fsync/inactive, error-recovery, and background daemon paths.

## Risks and edge cases

- Lock ordering across `avc->lock`, `afs_xdcache`, and `tdc->lock` is delicate.
- Dirty chunk batching depends on repeated sorted/contiguous scans; mistakes can skip or double-store chunks.
- Data-version relabeling must avoid marking stale chunks as fresh.
- `afs_StoreMini` clears truncation/extension markers before the RPC completes.
- 32-bit store fallback returns `EFBIG` for large lengths old servers cannot represent.
- Invalidation can wait indefinitely when local cache I/O keeps failing.
- `afs_ExtendSegments` advances `validPos` after writes and deserves write-error scrutiny.
- `afs_TruncateAllSegments` asserts cache-file open success in the truncation loop.

## Test signals

Cover dirty multi-chunk stores, sparse extension plus StoreMini, truncate-without-dirty-data, truncation across chunk boundaries, 64-bit and 32-bit StoreData paths, temporary vs permanent write errors, disconnected `ENETDOWN`, ccore invalidation, version relabeling after callback changes, VM sync flags, directory invalidation, cache I/O failure injection, and large-file edges near 2 GiB. Watch `IFDataMod`, `DWriting`, `DFEntryMod`, `CDirty`, `CExtendedFile`, `truncPos`, `mapDV`, and `validPos`.
