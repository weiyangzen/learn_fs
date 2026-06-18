# sources/distributed-fs/openafs/src/util/work_queue_types.h

Purpose: Defines public opaque work queue types, option structs, and callback signatures.

Important types: Forward declares `struct afs_work_queue_node` and `struct afs_work_queue`. `struct afs_work_queue_opts` configures pending low/high thresholds. `struct afs_work_queue_add_opts` configures add-time donation, blocking, and force behavior. `afs_wq_callback_func_t` is invoked as `callback(queue, node, queue_rock, node_rock, worker_rock)`. `afs_wq_callback_dtor_t` destroys node rock.

Control flow and state: Header-only type contract. The semantics of thresholds and add options are enforced in `work_queue.c`.

Dependencies and integration: Included by `work_queue.h` and private implementation headers. Public consumers need only this header and `work_queue.h` to create queues and nodes without seeing internals.

Risks and test signals: The callback can receive the node and mutate dependencies while running, so caller discipline is important. `donate` transfers a node reference to the queue when set; misuse can leak or prematurely free nodes. Tests should cover add options and callback return codes.
