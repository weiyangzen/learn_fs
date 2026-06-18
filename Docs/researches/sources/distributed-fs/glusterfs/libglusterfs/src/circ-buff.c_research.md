# sources/distributed-fs/glusterfs/libglusterfs/src/circ-buff.c

## Purpose
`circ-buff.c` implements a small thread-safe circular buffer abstraction for storing timestamped opaque pointers. It supports either overwrite-on-full ring behavior or `use_once` behavior where additions fail after capacity is reached.

## Important APIs, Types, And Functions
The public type `buffer_t` owns `w_index`, `used_len`, `size_buffer`, an array of `circular_buffer_t *`, a data destructor callback, a mutex, and the `use_once` policy. Each `circular_buffer_t` stores a `struct timeval tv` and `void *data`.

`cb_buffer_new()` allocates and initializes a buffer and mutex. `cb_add_entry_buffer()` locks and delegates to `__cb_add_entry_buffer()`. `__cb_add_entry_buffer()` inserts a new item, optionally destroys an overwritten entry, timestamps it with `gettimeofday`, advances `w_index`, and returns the next write index. `cb_buffer_dump()` iterates entries in chronological ring order for reusable buffers and index order for use-once buffers. `cb_buffer_show()` logs basic state. `cb_buffer_destroy()` frees entries, their data, the pointer array, the mutex, and the buffer.

## Control Flow
Creation allocates the owner and the entry pointer array. Adding an item acquires the mutex, checks capacity policy, destroys the current write slot if overwriting, allocates a new entry, stores the item and timestamp, advances modulo capacity, and updates `used_len`. Dumping acquires the mutex and invokes a caller-provided dumper for each entry. Destruction iterates the used entries and invokes the optional data destructor before freeing memory.

## State And Persistence Behavior
State is entirely in memory. The buffer owns the `circular_buffer_t` wrappers and, by convention, owns entry data enough to pass it to `destroy_buffer_data` and then `GF_FREE(cb->data)`. Each entry records insertion wall-clock time. No contents are persisted.

## Dependencies And Integration Points
It depends on `glusterfs/circ-buff.h`, GlusterFS allocation/logging macros, `pthread_mutex_t`, `gettimeofday`, and the caller-supplied destroy/dump callbacks. Integration points are diagnostic buffers, recent-event tracking, and translator-local telemetry that needs bounded memory.

## Risks And Edge Cases
`cb_buffer_new()` accepts `buffer_size == 0`; later modulo operations in add/dump would divide by zero. `cb_buffer_destroy()` iterates only `i < used_len`, which is not the same as all occupied slots after ring wrap; entries above `used_len - 1` can be missed when `w_index` has wrapped. `cb_buffer_dump()` copies `used_len`, `w_index`, and `size_buffer` before acquiring the lock, so it can observe inconsistent state under concurrent mutation. `cb_destroy_data()` calls a caller destructor and then always `GF_FREE(cb->data)`, which is only correct if all stored data is GlusterFS-allocated and the destructor does not already free it. Add paths do not validate `buffer`.

## Test Signals
Tests should cover normal insertion order, overwrite behavior, use-once full behavior, destroy callback ownership, wrap-around destroy correctness, dump under concurrent add, zero-capacity rejection, and timestamp population when `gettimeofday` succeeds or fails.
