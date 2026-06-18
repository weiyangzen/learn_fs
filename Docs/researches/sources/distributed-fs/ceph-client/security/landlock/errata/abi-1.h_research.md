# sources/distributed-fs/ceph-client/security/landlock/errata/abi-1.h

## Purpose

This ABI errata header documents and registers erratum 3 for Landlock ABI 1: disconnected directory handling in rename/link scenarios.

## Important APIs, Types, and Functions

The file expands `LANDLOCK_ERRATUM(3)` under the ABI value supplied by `errata.h`. Its comment documents the issue, fix, and impact.

## Control Flow

When included by `errata.h` with `LANDLOCK_ERRATA_ABI` set to 1, it contributes an entry to `landlock_errata_init[]`. `setup.c` later turns this into the corresponding runtime bit.

## State and Persistence Behavior

No local state exists. Runtime persistence is the global errata bitmask.

## Dependencies and Integration Points

This ties to filesystem refer checks in `fs.c`, especially disconnected directory walks that combine mount-root and filesystem-root restrictions.

## Risks and Test Signals

The behavioral risk is access widening through reparenting disconnected directories on kernels without the fix. Test bind mounts, disconnected dentries, rename/link with `LANDLOCK_ACCESS_FS_REFER`, and ABI errata reporting.
