<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_osi/osiqueue.c -->
## sources/distributed-fs/openafs/src/WINNT/client_osi/osiqueue.c

Purpose: Implements a simple non-circular intrusive doubly linked queue and a pooled `osi_queueData_t` allocator.

Important APIs, types, and functions: `osi_QAdd` pushes to head with only a head pointer. `osi_QAddH` pushes to head and maintains a tail pointer. `osi_QAddT` appends to tail with head/tail maintenance. `osi_QRemove` removes from a head-only list. `osi_QRemoveHT` removes from a list with head and tail pointers. `osi_InitQueue` initializes allocator locking. `osi_QDAlloc` allocates one `osi_queueData_t`, bulk-allocating `OSI_NQDALLOC` entries when needed. `osi_QDFree` returns an entry to the free list.

Control flow and state: Queue operations manipulate caller-owned intrusive `nextp`/`prevp` fields and do not perform locking. The queue-data allocator is protected by `osi_qdcrit`; it bulk-allocates blocks and threads all but the returned entry onto `osi_QDFreeListp`.

Persistence and dependencies: No persistence. Allocated blocks are never globally freed, forming a process-lifetime pool. Dependencies include `malloc`, thread critical-section wrappers, and `osi_assertx`.

Integration points: Used heavily by fd registries, sleep hash buckets and turnstiles, stats lock lists, active-info lists, and lock-order references.

Risks: Queue operations assume the element is currently in the list on remove and not in another list on add. `osi_InitQueue` uses a plain static int without interlocked protection, so concurrent first calls could race. The allocator's pooled blocks are intentionally retained and not individually freed to the OS.

Test signals: Add/remove head, tail, single-element, middle-element cases; allocator/free-list reuse; assertion on stale `datap`; and concurrent allocator stress after explicit initialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_osi/osiqueue.c -->
