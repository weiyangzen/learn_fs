# sources/distributed-fs/ceph-client/drivers/connector/cn_queue.c

## Purpose
This file implements callback registration storage and lifetime management for the connector subsystem. It maintains a spinlock-protected list of connector callback entries keyed by connector IDs.

## Important APIs, Types, And Functions
`cn_queue_alloc_callback_entry()` allocates and initializes `struct cn_callback_entry`, sets its refcount, increments the parent queue device refcount, copies the callback name and ID, and stores the function pointer. `cn_queue_release_callback()` decrements the entry refcount, decrements the parent device refcount, and frees the entry on last reference. `cn_cb_equal()` compares connector IDs. Public queue operations are `cn_queue_add_callback()`, `cn_queue_del_callback()`, `cn_queue_alloc_dev()`, and `cn_queue_free_dev()`.

## Control Flow
Adding a callback allocates an entry first, then locks `queue_lock`, scans for duplicate IDs, and either appends to the list or releases the unused entry and returns `-EINVAL`. Deleting locks the list, removes the first matching entry, unlocks, then releases it. Freeing the queue removes all list entries under lock and then waits, sleeping one second at a time, until the queue device refcount reaches zero before freeing the device.

## State And Persistence
State lives in `struct cn_queue_dev`: callback list, queue lock, netlink socket pointer, name, and atomic refcount. Each callback entry has its own refcount and parent queue reference. Callback entries persist until explicitly deleted and until in-flight dispatch references are released.

## Dependencies And Integration Points
The file depends on connector data structures from `linux/connector.h`, kernel list/spinlock/refcount APIs, allocation helpers, and work with dispatch in `connector.c`, which takes temporary references before invoking callbacks.

## Risks And Edge Cases
`cn_queue_free_dev()` waits unboundedly for references to drain, which can delay module unload if callbacks are stuck. Duplicate detection is linear. Deletion removes the entry from the list before dropping the refcount, so in-flight callbacks can finish safely if dispatch took a ref. The `dev = NULL` assignment after `kfree()` is local only.

## Test Signals
Useful tests include duplicate ID rejection, callback add/delete races with dispatch, refcount drain on queue free, callback name truncation behavior, and correct parent refcount increments/decrements.
