# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_guc_log_types.h

## Purpose
Defines persistent and snapshot state structures for GuC logging.

## Important APIs, Types, And Functions
`struct xe_guc_log_snapshot` stores copied chunks, total size, timestamps, log level, firmware versions, and firmware path. `struct xe_guc_log` stores live log level, the mapped GuC log BO, and overflow/flush stats indexed by GuC log buffer type.

## Control Flow
The implementation fills `xe_guc_log` during init and populates snapshots during capture. Snapshot users print or dump the captured data and then free it.

## State And Persistence
`xe_guc_log` persists with the GuC object. Snapshots persist independently from live GuC memory until freed, which makes them suitable for later coredump/debug output.

## Dependencies And Integration Points
Includes GuC log ABI and firmware version types, and forward-declares `struct xe_bo`.

## Risks And Test Signals
`copy` is an array of chunk pointers rather than a flat allocation, so all users must iterate by `num_chunks` and honor `size`. Test signals include snapshot capture/free under fault injection and coredump output with large buffers.
