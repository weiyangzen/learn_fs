## sources/distributed-fs/ceph-client/lib/ref_tracker.c

Purpose: debug helper for tracking reference allocations/frees, aggregating allocation stack traces, detecting leaks/double frees, and optionally exposing live reference users through debugfs.

Important APIs/types: private `struct ref_tracker` stores list node, dead flag, allocation stack handle, and free stack handle. Public APIs include `ref_tracker_alloc()`, `ref_tracker_free()`, `ref_tracker_dir_print[_locked]()`, `ref_tracker_dir_snprint()`, `ref_tracker_dir_exit()`, and debugfs helpers when enabled.

Control flow: allocation records a stack trace in stackdepot, allocates a tracker, and links it into `dir->list`; NULL tracker pointers increment `no_tracker`, and allocation failures increment `untracked`. Freeing records a free stack, detects double free via `tracker->dead`, moves the tracker into a quarantine list, and frees the oldest quarantined tracker when the quota is exhausted. Directory exit marks debugfs entries dead, frees quarantine, reports remaining live references, and warns on leaks/counter imbalance.

State and persistence: state lives in caller-owned `ref_tracker_dir` lists, spinlock, counters, quarantine availability, and debugfs xarrays. Stack traces are persisted in stackdepot.

Dependencies/integration: uses list sorting/stat aggregation, stacktrace/stackdepot, seq_file, slab, refcount, xarray, workqueue, and debugfs.

Risks/test signals: debugfs teardown is asynchronous to avoid blocking in arbitrary free contexts. Incorrect tracker ownership can cause false double-free/leak reports. Warnings and stack dumps are the main diagnostic signal.
