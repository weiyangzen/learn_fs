# sources/distributed-fs/ceph-client/sound/core/seq/seq_queue.c

## Purpose
`seq_queue.c` manages ALSA sequencer timing queues. A timing queue owns separate tick and real-time priority queues plus a sequencer timer, accepts scheduled events, dispatches ready events, and handles queue-control events such as start, stop, tempo, position, and skew.

## Important APIs, Types, and Functions
- `snd_seq_queue_alloc()`, `snd_seq_queue_delete()`, and `snd_seq_queues_delete()` manage queue lifecycle.
- `queueptr()` returns a referenced queue pointer; `queuefree()` releases it via use lock.
- `snd_seq_enqueue_event()` schedules an event cell onto the destination queue.
- `snd_seq_check_queue()` dispatches ready tick/time events in bounded batches.
- `snd_seq_queue_use()`, `snd_seq_queue_is_used()`, and `snd_seq_queue_client_leave()` track clients using queues and cleanup on client exit.
- `snd_seq_queue_timer_open()`, `snd_seq_queue_timer_close()`, `snd_seq_queue_timer_set_tempo()`, and `snd_seq_queue_set_owner()` expose queue control.
- `snd_seq_control_queue()` receives system timer-port events and applies queue operations.

## Control Flow
Queue allocation creates a `snd_seq_queue`, two priority queues, and a timer, marks the creating client as a user, takes one use lock reference for the caller, and inserts the queue into a global array. Enqueue converts relative timestamps to absolute using the queue timer state, inserts into tick or real-time prioq, and immediately checks for ready events.

`snd_seq_check_queue()` prevents reentrant queue scans with `check_lock`, dispatches ready tick events then real-time events, and stops after `MAX_CELL_PROCESSES_IN_QUEUE` to avoid monopolizing CPU. If another thread requested a check while blocked, it loops again before releasing the block.

Queue-control events are permission-checked by owner/lock state. Start clears timestamped events from the controlling client, starts the timer, and broadcasts; continue/stop/tempo/position/skew update the timer and broadcast successful changes from the system timer port.

## State and Persistence
Global runtime state is `queue_list[]` and `num_queues`. Per-queue state includes owner/lock bits, client-use bitmap/count, timer, priority queues, name, info flags, and use locks. State is in-memory only and destroyed when queues are deleted or the sequencer exits.

## Dependencies and Integration Points
Uses event cells from `seq_memory.c`, priority queues from `seq_prioq.c`, timer operations from `seq_timer.c`, client dispatch from `seq_clientmgr`, system broadcast semantics, and proc reporting. Queue ids are referenced by sequencer events and user ioctls.

## Risks
Concurrency risk is high: global list locking, queue owner locking, timer mutex, check reentrancy, and use-lock lifetime must agree. `snd_seq_queues_delete()` deletes queues still present in `queue_list[]` without clearing the array in this file, so it is intended for final teardown. Client-leave paths must remove both owned queues and remaining events in non-owned queues.

## Test Signals
Test queue allocation limits, owner permission checks, relative timestamp conversion, timer control event effects, bounded dispatch under large ready queues, client leave cleanup, remove-events filters across both prioqs, and proc queue reporting.
