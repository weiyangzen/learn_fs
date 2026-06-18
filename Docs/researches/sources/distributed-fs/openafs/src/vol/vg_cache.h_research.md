# sources/distributed-fs/openafs/src/vol/vg_cache.h

## Purpose

`vg_cache.h` is the public interface for the demand-attach volume-group cache. It exposes operations for adding/removing parent-child volume id relationships, querying a volume group by member id, launching/waiting for partition scans, checking partition state, and initializing/shutting down the package.

## Important APIs and Types

The header includes `vg_cache_types.h` for `VVGCache_query_t` and `partition.h` for `struct DiskPartition64`. For every mutating and query operation it generally exports both a normal wrapper and an `_r` variant: `VVGCache_entry_add`/`VVGCache_entry_add_r`, `VVGCache_entry_del`/`VVGCache_entry_del_r`, `VVGCache_query`/`VVGCache_query_r`, and scan start/wait pairs. In OpenAFS naming, the `_r` suffix means the caller is expected to hold the volume package global lock.

`VVGCache_checkPartition_r` is declared here but not implemented in the inspected source set; this is either a stale declaration or implemented conditionally elsewhere in builds not present in this tree.

## Control Flow and State Contract

Callers initialize with `VVGCache_PkgInit`, then use add/delete to keep the cache synchronized with volume header lifecycle events. A query may return `EAGAIN` when a partition cache is invalid or currently being rebuilt; callers should wait with `VVGCache_scanWait` or retry after the async scanner completes. Passing `NULL` to `VVGCache_scanStart` asks the implementation to scan all partitions.

## Dependencies and Integration Points

This header sits between volume attach/volser code and the private implementation in `vg_cache.c`/`vg_scan.c`. It intentionally hides hash table entries, scan tables, and partition delete-lists. Consumers only see partition pointers, volume ids, and exported query results.

## Risks and Test Signals

The most important contract risk is lock discipline: mixing `_r` and non-`_r` calls incorrectly can deadlock or race with scanner updates. Header-level tests are compile/link oriented: ensure all declared functions have definitions for the target build configuration, ensure callers include the public header instead of `vg_cache_impl.h`, and verify DAFS-only consumers guard use with `AFS_DEMAND_ATTACH_FS`.
