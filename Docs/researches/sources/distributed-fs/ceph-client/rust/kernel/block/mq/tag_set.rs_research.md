<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/kernel/block/mq/tag_set.rs -->
# sources/distributed-fs/ceph-client/rust/kernel/block/mq/tag_set.rs

## Purpose
This file wraps C `struct blk_mq_tag_set`, which owns blk-mq tag allocation and request private-data sizing for a Rust block driver.

## Important APIs, Types, and Functions
`TagSet<T: Operations>` is a pinned transparent wrapper over `Opaque<bindings::blk_mq_tag_set>`. `TagSet::new(nr_hw_queues, num_tags, num_maps)` returns a `PinInit<Self>`. `raw_tag_set` exposes the C pointer for disk allocation. Pinned `Drop` calls `blk_mq_free_tag_set`.

## Control Flow and State
Construction zeroes a C tag set, computes `cmd_size` from `RequestDataWrapper`, fills operations pointer from `OperationsVTable::<T>::build`, queue counts, default timeout, NUMA node, depth, flags, driver data, and map count, then calls `blk_mq_alloc_tag_set` in a pin chain. Drop frees the allocated tag-set resources.

## State and Persistence Behavior
The tag set persists pinned because the C struct includes linked-list state and is registered with blk-mq. It carries the request private-data size used by request init callbacks and the static operations vtable pointer. `GenDisk` holds an `Arc<TagSet<T>>` to keep it alive while queues use it.

## Dependencies and Integration Points
The file depends on blk-mq bindings, `OperationsVTable`, `RequestDataWrapper`, `PinInit`, `try_pin_init`, and `Opaque`. It integrates with `GenDiskBuilder::build` through `raw_tag_set`.

## Risks
Incorrect `cmd_size` would break `Request::wrapper_ptr`. Queue/depth/map parameters are passed through without higher-level policy validation. `blk_mq_free_tag_set` must run only after queues and disks no longer use the tag set, so user code should preserve the `Arc` lifetime pattern.

## Test Signals
No local tests. Useful coverage would allocate/drop tag sets with varied queue parameters and exercise request PDU init/exit through a minimal blk-mq driver.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/kernel/block/mq/tag_set.rs -->
