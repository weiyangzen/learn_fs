# File Research: sources/cow-pools/openzfs/module/zfs/bplist.c

## Scope

Implements a simple mutex-protected in-memory list of block pointers.

## APIs And Behavior

- `bplist_create()` initializes the list and mutex.
- `bplist_destroy()` destroys the list and mutex; callers are expected to have drained or cleared entries.
- `bplist_append()` allocates a `bplist_entry_t`, copies the block pointer, and appends it under lock.
- `bplist_iterate()` removes entries from the head, drops the lock while invoking the caller callback, frees each entry, and records the most recently removed entry for debugging.
- `bplist_clear()` removes and frees all queued entries under lock.

## State And Dependencies

State is limited to `bplist_t`, `bplist_entry_t`, a mutex, and an SPL list. Callback signatures accept a `dmu_tx_t` so the list can be used by transactional block-pointer processing code.

## Risks And Invariants

Callbacks run without `bpl_lock`, so they can be slow or re-enter other subsystems without holding the list mutex. Entries are consumed by iteration; this is not a read-only walk. The global `bplist_iterate_last_removed` is only a debugging aid and not a synchronization mechanism.
