# sources/distributed-fs/ceph-client/drivers/staging/nvec/nvec.h

## Purpose
Shared interface and core data structures for the NVEC MFD parent and child drivers.

## Important APIs, Types, And Functions
Defines `NVEC_POOL_SIZE`, `NVEC_MSG_SIZE`, `enum nvec_event_size`, `enum nvec_msg_type`, `struct nvec_msg`, and `struct nvec_chip`. Declares `nvec_write_async()`, `nvec_write_sync()`, `nvec_register_notifier()`, `nvec_unregister_notifier()`, and `nvec_msg_free()`.

## Control Flow
Child drivers include this header to send commands and register notifier callbacks. The parent uses the same types for queueing TX/RX messages and dispatching events.

## State And Persistence
The header describes runtime state but stores none itself. `struct nvec_chip` state is in-memory transport, queue, sync-write, and state-machine state.

## Dependencies And Integration Points
Pulls in kernel atomics, clk, completions, lists, mutexes, notifiers, reset controls, spinlocks, and workqueues. It is the contract between `nvec.c` and all NVEC children.

## Risks
The message size assumes SMBus block semantics: one command byte, one count byte, and up to 32 payload bytes. Event type and size encodings are protocol-specific; misuse by children can misparse EC messages.

## Test Signals
Compile all child modules against the header, validate event type values used by keyboard/mouse/power, and exercise sync/async API ownership rules including freeing returned sync messages.
