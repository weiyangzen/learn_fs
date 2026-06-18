# File Research: sources/cow-pools/openzfs/module/os/linux/spl/spl-tsd.c

## Purpose

Implements Solaris-style thread-specific data for Linux without modifying `task_struct`. It uses a global hash table keyed by `(tsd key, pid)` and supports per-key destructors, per-thread cleanup, and lookup by current or specified thread.

## Main Structures

- `tsd_hash_table_t`: global table with table lock, key allocator, hash size, and bins.
- `tsd_hash_bin_t`: per-bin spinlock plus hlist.
- `tsd_hash_entry_t`: one hash object, used for actual TSD values and for anchor entries.
- Key anchor: entry with `he_pid == DTOR_PID`, holding destructor and list of values for that key.
- PID anchor: entry with `he_key == PID_KEY`, holding list of values for that thread.

## Important Functions

- `tsd_hash_search()`: lookup by key and pid, locking only the computed bin.
- `tsd_hash_add_key()`: allocates a new nonzero TSD key and creates its destructor anchor.
- `tsd_hash_add_pid()`: creates a PID anchor on first use by a thread.
- `tsd_hash_add()`: creates a real TSD entry, linking it into the hash bin, key-anchor list, and pid-anchor list.
- `tsd_remove_entry()`: removes one value entry and prunes the PID anchor when empty.
- `tsd_hash_table_init()` / `tsd_hash_table_fini()`: allocate/free the fixed-size table and run destructors on remaining entries.
- `tsd_set()`: update, add, or remove current-thread value for a key.
- `tsd_get()`: get current-thread value.
- `tsd_get_by_thread()`: get value for a specific `kthread_t`.
- `tsd_create()`: create a key with optional destructor.
- `tsd_destroy()`: remove a key and all values using it.
- `tsd_exit()`: remove all TSD for the current thread.
- `spl_tsd_init()` / `spl_tsd_fini()`: module lifecycle.

## Concurrency Notes

Fast lookup locks only one hash bin. Operations that need to connect or tear down key/pid anchor relationships take the table lock and then bin locks. Destructors run after entries are removed from shared structures by moving removed entries to a local work list.
