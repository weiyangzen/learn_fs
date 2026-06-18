
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_oa_types.h

## Purpose

`xe_oa_types.h` defines the shared OA data structures embedded in Xe device, GT, unit, stream, and buffer state, plus the internal OA format enumeration.

## Important APIs, Types, and Functions

- `enum xe_oa_format_name` and `struct xe_oa_format` describe supported report encodings, report sizes, UAPI types, header width, counter size, and BC report fields.
- `struct xe_oa_regs` groups the OA register set for one unit.
- `struct xe_oa_unit` represents one hardware OA unit with type, GT, regs, engine count, id, and exclusive stream.
- `struct xe_oa_gt` stores per-GT OA lock and unit array.
- `struct xe_oa` stores device-level OA state, metrics sysfs/IDR, format table/mask, and id allocator.
- `struct xe_oa_buffer` stores the OA BO, vaddr, head/tail/circular size, format, and pointer lock.
- `struct xe_oa_stream` stores all per-FD state for OA stream operation.

## Control Flow

Implementation code initializes `xe_oa`, then each `xe_oa_gt` and `xe_oa_unit`. Stream open allocates and fills `xe_oa_stream`, while read/poll/ioctl paths mutate stream and buffer fields under their locks.

## State and Persistence Behavior

The structures define persistent lifetime boundaries: device OA state for device lifetime, GT OA units for GT lifetime, dynamic stream state for anon FD lifetime, and OA buffer state while a stream is active.

## Dependencies and Integration Points

The header depends on Linux IDR/mutex/bitops, UAPI OA definitions, register descriptors, hardware engine types, and DRM syncobj forward declarations.

## Risks and Edge Cases

- `exclusive_stream` must be protected by GT locking and cleared reliably.
- `oa_buffer.circ_size` may differ from BO size on Xe2+ overrun mode, so users must not assume full BO size is consumable reports.
- `wait_num_reports` and report size affect poll readiness and buffer sizing.
- Stream fields combine PM, forcewake, fences, syncs, and queues, making teardown ordering important.

## Test Signals

Structure-size/build coverage, stream lifecycle tests, lockdep on `gt_lock`/`stream_lock`/`ptr_lock`, and query tests for OA unit ids are useful signals.
