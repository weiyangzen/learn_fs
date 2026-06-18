# sources/distributed-fs/ceph-client/net/netlink/genetlink.h

## Purpose

`genetlink.h` is a small private synchronization header shared between Generic Netlink and the core netlink release path. It declares state used to wait for generic netlink socket destruction during family unregistration.

## Important APIs, Types, and Functions

The header declares `atomic_t genl_sk_destructing_cnt` and `wait_queue_head_t genl_sk_destructing_waitq`. `af_netlink.c` increments and decrements the counter around `NETLINK_GENERIC` socket removal/release, and `genetlink.c` waits on the queue during `genl_unregister_family()`.

## Control Flow

There is no executable code. The control flow is cross-file: `netlink_remove()` increments the counter for generic netlink sockets, `netlink_release()` decrements it and wakes the queue when it reaches zero, and `genl_unregister_family()` waits after removing a family from the IDR before freeing family-private socket storage.

## State and Persistence Behavior

The counter is global process state and persists for the life of the generic netlink subsystem. It represents in-flight generic netlink socket destruction, not registered family count.

## Dependencies and Integration Points

The header depends on `linux/wait.h`. Its only integration point is synchronization between `af_netlink.c` and `genetlink.c`.

## Risks and Edge Cases

If the counter is not balanced, family unregistration can hang forever or free per-socket private storage while release still needs it. The wake queue must be signaled only after the last in-flight generic netlink socket release completes.

## Test Signals

Stress generic netlink family unregister while user sockets are closing, with lockdep and refcount debugging enabled. Module unload tests for families using `sock_priv_size` exercise this path.
