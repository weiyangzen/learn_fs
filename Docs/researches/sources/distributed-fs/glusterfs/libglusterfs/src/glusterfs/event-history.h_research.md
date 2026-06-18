# sources/distributed-fs/glusterfs/libglusterfs/src/glusterfs/event-history.h

## Purpose
Declares a small event-history ring buffer abstraction for recording recent diagnostic events and dumping them through caller-provided formatting callbacks.

## APIs, Types, and Functions
`struct event_hist` contains a `buffer_t *` circular buffer and a `pthread_mutex_t` lock, with `eh_t` as the typedef. APIs are `eh_new()`, `eh_save_history()`, `eh_dump()`, and `eh_destroy()`. Creation takes buffer size, one-shot-buffer policy, and a data destructor callback.

## Control Flow, State, and Persistence
The event history is process-local volatile state. Callers allocate a history buffer, save entries under lock, dump the circular buffer through a callback, and destroy it with optional item cleanup.

## Dependencies and Integration
Depends on `circ-buff.h`, `glusterfs.h` for `gf_boolean_t`, pthreads, and diagnostic consumers selected by command-line or config options such as event history support.

## Risks and Test Signals
Risks include storing pointers whose lifetime is shorter than the history, destructor mismatches, dump/save races if locking is bypassed, and buffer-size choices that hide important events. Test signals include wraparound tests, one-shot mode tests, destructor invocation checks, concurrent save/dump stress, and statedump/log dump validation.
