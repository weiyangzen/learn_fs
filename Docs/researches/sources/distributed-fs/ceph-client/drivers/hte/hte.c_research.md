# sources/distributed-fs/ceph-client/drivers/hte/hte.c

## Purpose
Implements the generic Hardware Timestamping Engine core that connects provider chips with consumers requesting timestamped lines.

## Important APIs, Types, and Functions
- Core state: global `hte_devices` protected by `hte_lock`; per-provider `struct hte_device`; per-line `struct hte_ts_info`.
- Consumer APIs: `of_hte_req_count()`, `hte_init_line_attr()`, `hte_ts_get()`, `hte_request_ts_ns()`, `devm_hte_request_ts_ns()`, `hte_enable_ts()`, `hte_disable_ts()`, `hte_ts_put()`, and `hte_get_clk_src_info()`.
- Provider APIs: `devm_hte_register_chip()` and `hte_push_ts_ns()`.

## Control Flow
Providers register an `hte_chip`; the core allocates a flex-array `hte_device`, initializes one `hte_ts_info` per line, links it globally, and creates debugfs. Consumers initialize attributes, then `hte_ts_get()` finds a provider either through DT phandles or provider `match_from_linedata`, calls provider translation, module-pins the provider, and binds the descriptor to a free line. `hte_request_ts_ns()` calls provider request, stores callbacks, initializes optional work for sleeping callbacks, creates per-line debugfs, and marks the line registered. Providers push timestamp data with `hte_push_ts_ns()`, which sequences events, drops unregistered/disabled pushes, calls the primary callback under spinlock, and queues the secondary callback when requested. Release disables provider state, flushes queued work, clears flags, removes debugfs, and module_puts.

## State and Persistence
State is in memory: per-line flags (`REQ`, `REGISTERED`, `DISABLE`, `QUEUE_WK`), sequence counters, callback pointers, client data, line names, dropped timestamp counts, locks, and debugfs dentries. There is no persistent storage.

## Dependencies and Integration Points
Integrates with OF phandle parsing, module reference counts, debugfs, workqueues, mutexes/spinlocks, provider `hte_ops`, and public `<linux/hte.h>` descriptors.

## Risks and Test Signals
Risks include callback invocation under spinlock, release racing queued secondary work, provider unregister while descriptors are live, line-name ownership (`free_attr_name`), and duplicate requests for one line. Test signals include duplicate request returning `-EUSERS`, disable dropping timestamps, secondary callback work flushing on release, devm release on consumer remove, provider unregister cleanup, and debugfs counters.
