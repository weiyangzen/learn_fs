# sources/distributed-fs/ceph-client/include/linux/ceph/msgpool.h

## Purpose

`msgpool.h` defines a small wrapper around kernel mempools for preallocating Ceph messages that may be needed in receive or low-memory paths.

## Important APIs, Types, and Functions

`struct ceph_msgpool` records a pool name, backing `mempool_t`, preallocated message type, front length, and max data items. APIs are `ceph_msgpool_init()`, `ceph_msgpool_destroy()`, `ceph_msgpool_get()`, and `ceph_msgpool_put()`.

## Control Flow

Owners initialize a pool with message shape and size, get messages for matching incoming/outgoing paths, and return them when message processing is done. `ceph_msg` records its pool so put paths can return pooled allocations appropriately.

## State and Persistence Behavior

Runtime state is the mempool and its preallocated elements. There is no persistent state.

## Dependencies and Integration Points

It depends on `linux/mempool.h` and forward use of `struct ceph_msg`. It integrates with messenger allocation and OSD client `msgpool_op`/`msgpool_op_reply`.

## Risks and Edge Cases

Requested front length or data item count larger than the pool shape may require fallback allocation or fail depending on implementation. Pool destruction must happen after all borrowed messages are returned.

## Test Signals

Test init/destroy, get/put under allocation pressure, oversized request behavior, pool-backed `ceph_msg_put()` return paths, and OSD client shutdown with active pooled messages.
