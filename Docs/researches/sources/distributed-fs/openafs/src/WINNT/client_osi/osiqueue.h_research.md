<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_osi/osiqueue.h -->
## sources/distributed-fs/openafs/src/WINNT/client_osi/osiqueue.h

Purpose: Declares the intrusive queue node, one-pointer queue-data wrapper, queue APIs, allocator APIs, and small accessor macros.

Important APIs, types, and functions: `osi_queue_t` has `nextp` and `prevp`. `osi_queueData_t` embeds `osi_queue_t` plus `datap`. `OSI_NQDALLOC` sets bulk allocation size to 64. Exports cover add-head, add-tail, add-head-with-tail, remove, remove-with-tail, initialization, allocate, and free. Macros read/write data, next/prev pointers, and queue emptiness.

Control flow and state: Structures embedding `osi_queue_t` can be cast to queue nodes. The queue is null-terminated, not circular, making end checks simple.

Persistence and dependencies: No persistence and no external dependencies beyond C types. Implementations require OSI thread wrappers.

Integration points: Shared infrastructure across most OSI diagnostic and locking packages.

Risks: Intrusive queues require careful ownership; an element cannot safely belong to two lists using the same embedded node. Macros do no null checking.

Test signals: Unit-test list invariants after each operation and verify embedding/casting in representative OSI structs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_osi/osiqueue.h -->
