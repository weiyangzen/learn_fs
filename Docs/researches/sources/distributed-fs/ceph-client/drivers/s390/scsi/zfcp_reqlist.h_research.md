# sources/distributed-fs/ceph-client/drivers/s390/scsi/zfcp_reqlist.h

Purpose: provides the zfcp driver's in-memory hash table for tracking outstanding FSF requests by request ID. It is a small lock-protected helper used by the FCP/SCSI error and completion paths to find, remove, move, or iterate pending `struct zfcp_fsf_req` objects.

Important APIs/types/functions: `struct zfcp_reqlist` contains a spinlock and 128 list buckets. `zfcp_reqlist_alloc()` initializes the table, `zfcp_reqlist_free()` asserts the table is empty before freeing it, `_zfcp_reqlist_find()` does unlocked bucket lookup, and public helpers `zfcp_reqlist_find()`, `zfcp_reqlist_find_rm()`, `zfcp_reqlist_add()`, `zfcp_reqlist_move()`, and `zfcp_reqlist_apply_for_all()` wrap lookup, removal, insertion, bulk movement, and locked iteration.

Control flow: callers allocate one request list per adapter, add each FSF request after it receives a monotonically increasing `req_id`, look it up on completions or aborts, and remove it atomically when a completion owns the request. Bulk shutdown paths can splice all bucket contents into a plain list, while task-management code can apply a callback to every pending request under the request-list lock.

State and persistence: all state is volatile kernel memory: bucket membership through each request's `list` node plus the `req_id` hash. The helper does not reference hardware, sysfs, or persistent storage. Locking uses `spin_lock_irqsave()` because callers can run in interrupt-sensitive completion/error paths.

Dependencies and integration: depends on Linux list and spinlock primitives, zfcp's `struct zfcp_fsf_req`, and allocation helpers such as `kzalloc_obj()`. It is included by zfcp SCSI/FSF code and is particularly visible in abort and task-management cleanup paths.

Risks and test signals: `zfcp_reqlist_free()` uses `BUG_ON()` if any request remains, so teardown ordering must guarantee prior drain/removal. `zfcp_reqlist_apply_for_all()` explicitly is not safe against list mutation by the callback. The simple modulo hash relies on request IDs being distributed enough across 128 buckets. Test duplicate add/remove ordering, abort racing normal completion, adapter shutdown moving all requests, callback iteration that only mutates request payloads, and teardown after all FSF requests complete.
