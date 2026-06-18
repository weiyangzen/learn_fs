<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/textsearch.c -->
# sources/distributed-fs/ceph-client/lib/textsearch.c

## Purpose
Core generic text-search framework for linear and non-linear data. It provides algorithm registration, algorithm lookup/autoload, configuration lifecycle, and a convenience wrapper for contiguous buffers.

## APIs, Types, and Functions
Exports `textsearch_register()`, `textsearch_unregister()`, `textsearch_prepare()`, `textsearch_destroy()`, and `textsearch_find_continuous()`. Internal state includes the RCU-protected `ts_ops` list and `ts_mod_lock`. `lookup_ts_algo()` resolves registered algorithms and takes a module reference. `struct ts_linear_state` and `get_linear_data()` adapt contiguous memory to the block-fetch callback model.

## Control Flow, State, and Persistence
Algorithms register a populated `struct ts_ops` with a unique name. Registration validates required callbacks, checks for duplicate names under a spinlock, and appends via `list_add_tail_rcu()`. Lookup walks the list under RCU and uses `try_module_get()` to pin the provider. `textsearch_prepare()` rejects zero-length patterns, optionally requests `ts_<algo>` modules under `TS_AUTOLOAD`, calls the algorithm `init()`, stores `ops` in the returned config, and drops the module reference on error. `textsearch_destroy()` calls an optional algorithm destructor, releases the module, and frees the config. Linear searches install `get_linear_data` into `conf->get_next_block` and stash buffer metadata in `state->cb`.

## Dependencies and Integration
Depends on module loading, RCU lists, spinlocks, error pointers, slab allocation, and `linux/textsearch.h`. Algorithms in `ts_bm.c`, `ts_kmp.c`, and `ts_fsm.c` integrate by registering `struct ts_ops`; users include networking, filtering, and other subsystems that need pattern search over fragmented data.

## Risks and Test Signals
Risks include unregister lifetime requiring RCU-safe users, mutation of `conf->get_next_block` by the linear helper making shared configs caller-sensitive, autoload deadlock avoidance when `TS_AUTOLOAD` is omitted, and algorithm-specific pattern compatibility. Test signals should include duplicate registration, missing callback validation, module autoload success/failure, concurrent search with separate `ts_state`, destroy reference release, and continuous versus block-backed searches.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/textsearch.c -->
