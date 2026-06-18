<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/kernel/block/mq.rs -->
# sources/distributed-fs/ceph-client/rust/kernel/block/mq.rs

## Purpose
This module documents and assembles the Rust blk-mq abstraction layer for implementing block device drivers.

## Important APIs, Types, and Functions
It exposes `gen_disk`, private `operations`, private `request`, private `tag_set`, and publicly re-exports `Operations`, `Request`, and `TagSet`. The module-level documentation describes the required sequence: implement `Operations`, create a `TagSet<T>`, build a `GenDisk<T>` through `GenDiskBuilder`, and ensure requests are ended.

## Control Flow and State
There is no executable control flow in this file. It defines the public composition of the blk-mq API and the conceptual request lifecycle: blk-mq queues a `Request`, Rust driver code receives `ARef<Request<T>>`, and driver completion must call `Request::end_ok` or equivalent completion flow.

## State and Persistence Behavior
The documentation highlights that Rust drivers hold refcounts on in-flight C requests, and that `TagSet` maintains tag-to-request mapping and blk-mq queue resources. Actual state is implemented in sibling modules.

## Dependencies and Integration Points
It integrates the Rust block module with C blk-mq concepts: `struct blk_mq_tag_set`, `struct gendisk`, `struct request`, queue depth, queue maps, and request completion. The example uses `Arc<TagSet<_>>`, `GenDiskBuilder`, and `ARef<Request<_>>`.

## Risks
The main risk described here is liveness: drivers must end every request, and the Rust reference-count model must align with blk-mq ownership. Holding requests too long, ending with extra references, or losing the tag-set/disk lifetime ordering can deadlock or timeout I/O.

## Test Signals
No local tests are present. The embedded example is a compile-time/API smoke signal for creating a tag set, disk, and request callback.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/kernel/block/mq.rs -->
