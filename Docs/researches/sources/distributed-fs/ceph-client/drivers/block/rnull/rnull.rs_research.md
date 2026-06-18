# sources/distributed-fs/ceph-client/drivers/block/rnull/rnull.rs

## Purpose
Implements a Rust null block driver module. It registers a configfs subsystem, creates in-memory block disks on demand, and completes every request successfully without storing data.

## Important APIs, types, and functions
- `module!` declares `rnull_mod`, author, description, and GPL license.
- `NullBlkModule` owns the pinned configfs subsystem.
- `NullBlkDevice::new()` creates a single-queue blk-mq tag set, queue data containing `IRQMode`, and a `GenDisk` with requested capacity, block sizes, and rotational flag.
- `impl Operations for NullBlkDevice` defines `queue_rq()`, `commit_rqs()`, and `complete()`.
- `QueueData` stores the configured completion mode.

## Control flow
Module init logs load and initializes configfs. Configfs calls `NullBlkDevice::new()` when a group is powered on. Requests enter `queue_rq()`: in `IRQMode::None`, they are ended synchronously with `Request::end_ok()`; in `IRQMode::Soft`, they are completed through blk-mq soft completion and later ended in `complete()`.

## State and persistence behavior
The module keeps only the configfs subsystem. Each disk's queue data stores IRQ mode. No request payloads are persisted or inspected; all I/O is discarded and reads complete without backing storage semantics beyond successful completion.

## Dependencies and integration points
Uses Rust-for-Linux block mq/gen_disk APIs, `Arc` tag sets, `KBox` queue data, and the local `configfs` module. It parallels the C `null_blk` driver concept but implements a smaller feature set.

## Risks and test signals
- `capacity_mib << (20 - SECTOR_SHIFT)` should be tested with large capacities.
- The code expects `end_ok()` not to fail because no extra request refs are held; request-lifetime API changes would matter.
- Test both IRQ modes, queue depth saturation, module unload with powered devices, and configfs power cycling under I/O.
