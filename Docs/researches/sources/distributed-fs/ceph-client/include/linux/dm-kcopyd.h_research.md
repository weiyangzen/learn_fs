<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/dm-kcopyd.h -->
# sources/distributed-fs/ceph-client/include/linux/dm-kcopyd.h

## Purpose
Declares kcopyd, a Device Mapper service for copying or zeroing block-device regions synchronously with optional asynchronous completion.

## Important APIs, Types, And Functions
Defines `DM_KCOPYD_MAX_REGIONS`, `DM_KCOPYD_IGNORE_ERROR`, `DM_KCOPYD_WRITE_SEQ`, `struct dm_kcopyd_throttle`, `DECLARE_DM_KCOPYD_THROTTLE_WITH_MODULE_PARM()`, `struct dm_kcopyd_client`, `dm_kcopyd_client_create()`, `dm_kcopyd_client_destroy()`, `dm_kcopyd_client_flush()`, `dm_kcopyd_copy()`, `dm_kcopyd_prepare_callback()`, `dm_kcopyd_do_callback()`, and `dm_kcopyd_zero()`.

## Control Flow
Targets create a client, submit copy jobs from one source region to up to eight destination regions, and receive read/write error status through a callback. Zero jobs write zeroes to destination regions. Callback preparation can allocate in sleepable context and later complete from interrupt context through the kcopyd thread.

## State And Persistence
Runtime state includes job queues, client pools, optional shared throttle counters, and submitted block I/O. Persistent effects are copied or zeroed sectors after completion and flushes requested by higher layers.

## Dependencies And Integration Points
Builds on `dm-io`, block devices, module parameters for throttling, and DM targets such as snapshots, mirrors, and thin provisioning.

## Risks And Edge Cases
Destination count is bounded by `DM_KCOPYD_MAX_REGIONS`. `write_err` is a bitset indexed by destination. Throttle structs may be shared across clients and must be initialized. `dm_kcopyd_prepare_callback()` must not be called in interrupt context, while `dm_kcopyd_do_callback()` may be.

## Test Signals
Tests should cover single and multiple destination copies, read errors, per-destination write errors, ignore-error behavior, sequential write flag behavior, zeroing, throttling, client flush/destroy ordering, and interrupt-context callback submission.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/dm-kcopyd.h -->
