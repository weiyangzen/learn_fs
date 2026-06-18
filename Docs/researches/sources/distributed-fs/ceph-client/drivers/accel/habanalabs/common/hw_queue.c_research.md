# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/common/hw_queue.c

## Purpose
This file manages HabanaLabs hardware queues: ring allocation, producer/consumer accounting, completion-queue reservation, BD submission, signal/wait stream setup, staged CS mirroring, and reset handling.

## Important APIs, Types, And Functions
Key APIs are `hl_hw_queue_submit_bd()`, `hl_hw_queue_schedule_cs()`, `hl_hw_queues_create()`, `hl_hw_queues_destroy()`, `hl_hw_queue_reset()`, `hl_hw_queue_update_ci()`, and `hl_hw_queue_send_cb_no_cmpl()`. Internal paths split by queue type into external, internal, CPU, and hardware queue initialization and scheduling. Signal/wait support uses SOB and monitor state through `init_signal_cs()`, `init_wait_cs()`, and encapsulated-signal helpers.

## Control Flow
Creation allocates the queue array, copies ASIC queue properties, allocates or retrieves queue memory by type, and initializes sync-stream resources. Scheduling locks hardware queues, rejects non-operational devices, checks queue and CQ capacity, initializes special CS types, runs ASIC pre-schedule hooks, mirrors the CS for completion/TDR, then emits each job to its target queue. Failures unwind CQ reservations.

## State And Persistence
Persistent state includes queue PI/CI, DMA ring memory, shadow queues, CQ free-slot reservations, sync-stream SOBs, monitor IDs, staged CS lists, collective monitor allocation, and CS mirror list entries. Reset zeros queue indices and sync-stream state.

## Dependencies And Integration Points
It depends on ASIC callbacks for locking, doorbells, PQE writes, end-of-CB packets, signal/wait CB generation, SOB addresses, collective wait setup, and pre-schedule behavior. It integrates with CS parsing, IRQ completion, fences, and device reset.

## Risks
CQ reservations must be perfectly unwound. PI/CI wrap depends on queue length conventions. Signal/wait refcounting races with completion and reset. Staged CS state depends on mirror-list consistency.

## Test Signals
Stress queue-full/CQ-full paths, non-completion CS CI updates, mixed queue types, signal/wait races, encapsulated signals, staged CS errors, TDR scheduling, reset behavior, and partial queue-init failure.
