# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_devcoredump.c

## Purpose
This file implements Xe device coredumps using Linux `dev_coredump`. On the first GPU hang/error, it captures a stable snapshot of device, GT, GuC, exec queue, job, HW engine, and VM state and exposes it through sysfs for postmortem debugging.

## Important APIs, Types, and Functions
Public functions are `xe_devcoredump`, `xe_devcoredump_init`, and `xe_print_blob_ascii85`. Important internals include `devcoredump_snapshot`, `xe_devcoredump_deferred_snap_work`, `xe_devcoredump_read`, `__xe_devcoredump_read`, `xe_devcoredump_snapshot_free`, and `xe_devcoredump_free`.

## Control Flow
`xe_devcoredump` takes the device coredump lock, ignores later hangs while one dump is active, stores a formatted reason, captures immediate snapshots under forcewake/signaling constraints, and queues deferred work. The worker registers the devcoredump node, reacquires runtime PM and forcewake, captures delayed VM/exec queue details, computes formatted dump size, pre-renders either the whole dump or a 1.5 GB chunk window, and frees raw snapshots when possible. Reads flush deferred work, page through large dump chunks, copy data, and use runtime PM for large regenerated chunks.

## State and Persistence Behavior
State lives in `xe->devcoredump`: a mutex, `captured` flag, snapshot structures, delayed work, reason string, and optional formatted read buffer. Only the first failure is retained until userspace releases the devcoredump or the timeout expires. Freeing clears snapshot fields and resets `captured`.

## Dependencies and Integration Points
It depends on Linux devcoredump, DRM printers, runtime PM, forcewake, GuC CT/log/capture, GuC submit snapshots, scheduler job snapshots, HW engine snapshots, VM snapshots, and device snapshot printing. GuC submit timeout paths call `xe_devcoredump`.

## Risks
Capture runs near failure paths and must avoid sleeping/allocating in signaling-sensitive contexts; delayed work handles heavier allocations. Very large dumps require chunk regeneration and runtime PM. Locking must prevent stale reads while allowing release. If snapshot free misses a subobject, repeated hangs leak memory or expose stale data.

## Test Signals
GPU hang injection, multiple-hang suppression, devcoredump sysfs read/release, timeout cleanup, large-dump chunk reads, runtime PM during reads, forcewake failure handling, and ASCII85 blob output tests are important signals.
