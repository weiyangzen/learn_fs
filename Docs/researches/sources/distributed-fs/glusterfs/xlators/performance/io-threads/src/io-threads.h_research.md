# sources/distributed-fs/glusterfs/xlators/performance/io-threads/src/io-threads.h

## Purpose
Declares io-threads configuration constants and runtime state structures used by `io-threads.c`.

## Important APIs, types, and functions
`IOT_MIN_THREADS`, `IOT_DEFAULT_THREADS`, `IOT_MAX_THREADS`, `IOT_DEFAULT_IDLE`, and `IOT_THREAD_STACK_SIZE` define defaults and bounds. `iot_client_ctx_t` stores one request list and client-list node per priority. `iot_fop_data_t` stores per-priority active limits/counts, client queues, no-client queue, queue sizes, and watchdog markers. `iot_conf_t` stores global worker-pool, queue, watchdog, option, and synchronization state.

## Control flow
The header has no executable flow, but `io-threads.c` relies on these structures for queue scheduling, worker scaling, statedump, reconfigure, and shutdown.

## State and persistence behavior
All declared state is process memory. It determines how queued operations survive while the graph is active and how they are drained on shutdown, but it has no persistent format.

## Dependencies and integration points
Includes Gluster dict/list/compat errno, iot memory types, pthread/semaphore-related platform headers, and priority constants from Gluster core.

## Risks and test signals
Risks include counters not protected by the mutex, queue-list node misuse because `iot_client_ctx_t` embeds both request and client links, and option defaults drifting from volume option definitions. Tests should inspect statedump values under load and validate queue cleanup across client lifecycle events.
