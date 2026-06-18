# sources/distributed-fs/ceph-client/sound/core/seq/seq_prioq.h

## Purpose
`seq_prioq.h` declares the ALSA sequencer priority queue structure and operations. It is the internal interface between timer queues and event-cell storage.

## Important APIs, Types, and Functions
- `struct snd_seq_prioq` contains linked-list head/tail pointers, cell count, and a spinlock.
- Declares constructor/destructor, enqueue/dequeue, availability, client-leave cleanup, and remove-events APIs.

## Control Flow
Consumers create a priority queue, enqueue `snd_seq_event_cell` objects, periodically dequeue ready cells based on the current timer value, and remove cells on client departure or explicit flush.

## State and Persistence
State is transient and cell-backed. The priority queue does not allocate events itself; it only owns cell links while queued.

## Dependencies and Integration Points
Includes `seq_memory.h`. Used directly by `seq_queue.c` for separate tick and real-time queues.

## Risks
The API gives direct cell pointers, so ownership transfer must be clear: enqueue transfers ownership to the prioq; dequeue transfers ownership to the caller; removal frees internally.

## Test Signals
Compile-time include coverage plus queue lifecycle tests that ensure all queued cells are freed by `snd_seq_prioq_delete()` and no cells leak across remove paths.
