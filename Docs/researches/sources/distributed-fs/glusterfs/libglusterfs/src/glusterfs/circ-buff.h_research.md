# sources/distributed-fs/glusterfs/libglusterfs/src/glusterfs/circ-buff.h

## Purpose
`circ-buff.h` declares a mutex-protected circular buffer abstraction that stores timestamped opaque pointers, usually for bounded history/debug/event tracking.

## Important APIs, Types, and Functions
- `circular_buffer_t`: one entry with `struct timeval tv` and `void *data`.
- `buffer_t`: ring metadata (`w_index`, `used_len`, `size_buffer`), entry pointer array, data destructor, mutex, and `use_once` policy.
- `cb_buffer_new()`, `cb_buffer_destroy()`: allocate and free a buffer.
- `cb_add_entry_buffer()`: append an item, overwriting or stopping based on policy.
- `cb_buffer_show()`, `cb_buffer_dump()`: display/dump stored entries via a callback.

## Control Flow
The header defines the object model. Implementations allocate an array of entry pointers, write entries at `w_index`, track used length up to capacity, and use `destroy_buffer_data` when replacing or destroying item data.

## State and Persistence
All state is in memory and protected by `buffer->lock`. Stored payload ownership is defined by the destroy callback. No persistence exists beyond optional dump output.

## Dependencies and Integration Points
Depends on `common-utils.h` for Gluster types and pthread support. It is used by subsystems needing a fixed-size rolling event history.

## Risks and Edge Cases
- `BUFFER_SIZE`/`TOTAL_SIZE` are small defaults but `cb_buffer_new()` accepts a size, so implementation must avoid assumptions.
- Payload lifetime depends on the destroy callback being correct.
- Dump/show callbacks must not mutate buffer state without respecting locks.

## Test Signals
Test allocation/destruction, wraparound, use-once behavior, timestamp population, destructor invocation on overwrite/destroy, and concurrent add/dump locking.
