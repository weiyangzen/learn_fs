# sources/distributed-fs/glusterfs/libglusterfs/src/event-history.c

## Purpose
This file wraps circular-buffer history storage for translator or subsystem events. It provides a small `eh_t` object with a buffer, lock, save, dump, and destroy operations.

## Important APIs, types, and functions
The exported APIs are `eh_new`, `eh_dump`, `eh_save_history`, and `eh_destroy`. `eh_t` owns a `buffer_t *` created by `cb_buffer_new()`, and callers supply an optional `destroy_buffer_data` callback for buffered entries.

## Control flow
`eh_new()` allocates an `eh_t`, creates the circular buffer with configured size and use-once behavior, initializes a mutex, and returns the history object. `eh_save_history()` appends data through `cb_add_entry_buffer()`. `eh_dump()` calls `cb_buffer_dump()` with a caller-supplied dumper. `eh_destroy()` destroys the buffer, destroys the mutex, and frees the history.

## State and persistence behavior
History is in-memory only. The circular buffer determines retention and overwrite/use-once behavior. The lock is initialized but this file does not acquire it around save or dump, so synchronization is either inside the circular-buffer implementation or expected from callers.

## Dependencies and integration points
It depends on `glusterfs/event-history.h`, circular-buffer helpers, GlusterFS allocation and logging, pthread mutexes, and translator/subsystem code that records diagnostic histories.

## Risks and edge cases
`eh_save_history()` does not check for NULL `history` before dereferencing. `eh_dump()` tolerates NULL history, but save does not. The local mutex is unused here, which can be misleading if callers assume `eh_t` itself serializes access. Destroy during concurrent save/dump would be unsafe without external coordination.

## Test signals
Tests should cover allocation failure, buffer creation failure cleanup, save/dump order, use-once behavior, destroy callback invocation, NULL destroy handling, NULL history behavior for dump and save, and concurrent access if circular-buffer internals claim thread safety.
