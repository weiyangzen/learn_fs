# sources/distributed-fs/ceph-client/sound/core/seq/seq_prioq.c

## Purpose
`seq_prioq.c` implements the sequencer priority queue used by timing queues. It orders event cells by tick or real-time timestamp, preserves FIFO order for equal timestamps unless priority is requested, and removes queued cells by client or flush criteria.

## Important APIs, Types, and Functions
- `snd_seq_prioq_new()` and `snd_seq_prioq_delete()` manage queue lifecycle.
- `snd_seq_prioq_cell_in()` inserts an event cell in timestamp order.
- `snd_seq_prioq_cell_out()` pops the head only when no current time is provided or the head timestamp is ready.
- `snd_seq_prioq_avail()` reports number of queued cells.
- `snd_seq_prioq_leave()` removes events related to a client, optionally including all timestamped events.
- `snd_seq_prioq_remove_events()` removes events matching `snd_seq_remove_events` filters.

## Control Flow
Insertion first tries a fast tail append when the new cell is non-priority and timestamp is >= current tail. Otherwise it walks the linked list until it finds an earlier timestamp position or an equal timestamp with priority. Dequeue compares the head event timestamp against the current tick/time pointer. Removal walks the queue under lock, unlinks matching nodes into a temporary free list, then frees cells outside the queue lock.

## State and Persistence
The queue stores `head`, `tail`, `cells`, and a spinlock. It is purely in-memory and owns references to cells until dequeue/removal/free.

## Dependencies and Integration Points
Uses `seq_timer.h` timestamp comparison helpers and `seq_memory.h` cell ownership/freeing. `seq_queue.c` maintains separate tick and real-time priority queues per sequencer queue.

## Risks
The queue is an O(n) linked list; large scheduled-event workloads can make insertion expensive. The insertion loop contains a fixed count guard against list corruption. Tail update in removal must be correct when deleting the last node. Timestamp comparison assumes event flag type matches the queue it is in.

## Test Signals
Test sorted insertion, equal timestamp FIFO, priority insertion before equal timestamp events, dequeue readiness for tick and real time, client-leave removal, all remove-mode filters, and corruption-resistant behavior under heavy queue sizes.
