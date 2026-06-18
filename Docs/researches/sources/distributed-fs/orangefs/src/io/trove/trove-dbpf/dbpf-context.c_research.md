# sources/distributed-fs/orangefs/src/io/trove/trove-dbpf/dbpf-context.c

## Purpose
`dbpf-context.c` implements Trove context lifecycle for DBPF. Contexts own completion queues used by DBPF operation testing and threaded completion paths.

## Important APIs, types, and functions
`dbpf_open_context()` allocates a free slot in `dbpf_completion_queue_array`, creates a queue, initializes its mutex, returns the context index, and initializes sync coalescing state with `dbpf_sync_context_init()`. `dbpf_close_context()` destroys the mutex, cleans up the queue, clears the slot, and calls `dbpf_sync_context_destroy()`. `dbpf_context_ops` exposes these functions to the Trove method table.

## Control flow and state
Global state includes `dbpf_completion_queue_array[TROVE_MAX_CONTEXTS]`, `dbpf_completion_queue_array_mutex[TROVE_MAX_CONTEXTS]`, and `dbpf_context_mutex` protecting allocation/free. Context ids are array indexes, selected by the first `NULL` queue slot.

## Persistence and integration
Contexts are runtime-only. They integrate directly with `dbpf-dspace.c` test/testsome/testcontext and with threaded DBPF completions that push completed operations into context-specific queues.

## Dependencies
It depends on DBPF op queues, sync coalescing, Trove context ops, and `gen_mutex`.

## Risks and test signals
If `dbpf_sync_context_init()` fails after a queue is allocated, the function returns the error without tearing down the queue slot, leaving a leaked/occupied context. `dbpf_close_context()` does not bounds-check `context_id`. Tests should cover maximum context exhaustion, sync init failure cleanup, close of unopened contexts, queue cleanup with pending operations, and repeated open/close cycles.
