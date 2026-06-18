# Research: sources/distributed-fs/eos/mgm/proc/admin/EvictCmd.cc

## Purpose

`EvictCmd.cc` implements the protobuf tape-eviction command. It removes disk replicas for files that have tape replicas, optionally respecting an eviction counter and optionally targeting a single filesystem id.

## Important APIs, Types, and Functions

- `EvictCmd::ProcessRequest()` is the complete command implementation.
- It consumes `EvictProto` fields including repeated `file`, `ignoreevictcounter`, `evictsinglereplica().fsid()`, and `ignoreremovalonfst`.
- It uses `_access`, `_exists`, `_stat`, `_dropstripe`, and `_dropallstripes` on `gOFS`.
- It reads/writes namespace metadata attributes `RETRIEVE_EVICT_COUNTER_NAME`, `RETRIEVE_REQID_ATTR_NAME`, and `RETRIEVE_REQTIME_ATTR_NAME`.
- `EosCtaReporterEvict` logs CTA/tape eviction audit parameters.

## Control Flow

The command validates option combinations: `fsid` requires `ignore-evict-counter`, and `ignore-removal-on-fst` requires `fsid`. It then iterates each file identifier, resolving path or fid to a path. For each file, it checks `p` ACL permission on the parent path, validates that the path exists and is a file, stats it, and requires tape mode (`EOS_TAPE_MODE_T`).

It counts disk replicas by reading file metadata and ignoring `TAPE_FS_ID`. If a target fsid is present, it verifies that replica exists. With single-fsid eviction, it calls `_dropstripe()` as root, optionally skipping FST removal. Without fsid, it optionally decrements the eviction counter under a metadata write lock and skips removal if the counter remains positive; otherwise it calls `_dropallstripes()`.

When all disk replicas are removed, it resets retrieve request id/time and eviction-counter attributes. It accumulates success/error counts and emits a summary.

## State and Persistence Behavior

The command mutates namespace metadata by decrementing/removing retrieve eviction counters and clearing retrieve request attributes. It removes disk replica locations through MGM drop operations. It uses root virtual identity for the actual drop calls after validating the caller has parent `p` ACL permission.

CTA reporter objects are per-file runtime audit records. Summary counters are per-request.

## Dependencies and Integration Points

Dependencies include path utilities, timing, `XrdMgmOfs`, `EosCtaReporter`, common constants/definitions, namespace `IView`, and optional. It integrates with CTA/tape workflows, retrieve/evict metadata conventions, EOS ACL checking, and low-level replica removal.

## Risks and Edge Cases

- `allReplicasRemoved` is declared outside the file loop and is not reset per file; after one file removes all replicas, later files can enter the cleanup block even if their own removal did not remove all replicas.
- Error messages accumulate in one stream across files, so later per-file errors can produce long combined stderr.
- `_exists` failure returns `errno`, but the actual `XrdOucErrInfo` code may be more precise.
- Direct `gOFS->eosView->getFile()` calls are not consistently protected by `eosViewRWMutex` in replica-count sections.
- Single-replica eviction uses root identity after only parent `p` ACL validation; ACL semantics must be correct for this destructive operation.

## Test Signals

Tests should cover invalid option combinations, path and fid resolution, empty paths, missing files, directory input, missing parent `p` permission, non-tape files, files with no disk replicas, fsid not present, single-replica drop success/failure, drop-all success/failure, eviction-counter decrement/skip/remove, retrieve attribute cleanup, multi-file mixed success/errors, and the `allReplicasRemoved` per-file behavior.
