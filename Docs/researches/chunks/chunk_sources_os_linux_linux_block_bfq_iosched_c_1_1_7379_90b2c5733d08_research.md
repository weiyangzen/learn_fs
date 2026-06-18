# Chunk Research: sources/os/linux/linux/block/bfq-iosched.c lines 1-7379

## Scope

This chunk covers almost all of Linux's BFQ multi-queue I/O scheduler implementation except the sysfs attribute table and module registration tail after line 7379. It defines BFQ's per-request and per-queue lifecycle, low-latency heuristics, cooperative/stable queue merging, dispatch/idling/injection policy, request completion handling, per-IO-context queue management, and queue initialization/teardown.

## Core APIs and Entry Points

- Elevator/block-mq hooks implemented in this chunk:
  - `bfq_limit_depth()` limits allocation depth for async I/O and sync writes, and clamps depth to 1 when a queue/cgroup is over its weighted request allocation.
  - `bfq_bio_merge()`, `bfq_request_merge()`, `bfq_request_merged()`, `bfq_requests_merged()`, and `bfq_allow_bio_merge()` integrate BFQ queues with block-layer bio/request merge paths.
  - `bfq_prepare_request()` attaches an `io_cq` to a request and clears stale elevator-private pointers.
  - `bfq_insert_request()` and `bfq_insert_requests()` route new requests into BFQ queues or the direct dispatch list.
  - `bfq_dispatch_request()` is the externally visible dispatch hook; it locks `bfqd->lock`, delegates to `__bfq_dispatch_request()`, and updates debug stats after unlocking.
  - `bfq_finish_request()` and `bfq_finish_requeue_request()` release scheduler-private request state on normal completion or requeue.
  - `bfq_exit_icq()`, `bfq_init_queue()`, and `bfq_exit_queue()` handle per-context and per-device lifecycle.

## Major State

- `struct bfq_data` is the per-device scheduler state: dispatch queues, active/idle queues, in-service queue, burst tracking, device-rate estimation, injection state, hardware queueing detection, multi-actuator ranges, root group, and the OOM fallback queue.
- `struct bfq_queue` is the per-flow/per-actuator queue: rb-tree/FIFO request state, budget/service accounting, low-latency weight raising, seek/think-time heuristics, merge/split state, waker state, and injection limits.
- `struct bfq_io_cq` binds an `io_context` to BFQ queues with `bfqq[2][BFQ_MAX_ACTUATORS]`, saved merge/split state, stable-merge candidates, and request counts.
- BFQ group/entity scheduling is consumed through `bfq-cgroup.c` and `bfq-wf2q.c`; this file handles leaf queues and request lifecycle.

## Control Flow

### Request Lifecycle

1. `bfq_prepare_request()` attaches `rq->elv.icq` and clears private pointers.
2. `bfq_init_rq()` performs delayed association with a `bfq_queue`, after the request can no longer become a non-BFQ/pass-through request.
3. `bfq_insert_request()` attempts block-layer merging, then either inserts directly into `bfqd->dispatch` or calls `__bfq_insert_request()`.
4. `__bfq_insert_request()` may merge cooperating queues, updates think-time/seek-time state, adds the request to `sort_list` and FIFO, updates `next_rq`, and handles idling/timer effects.
5. `bfq_dispatch_request()` selects work through `bfq_select_queue()` and dispatches via `bfq_dispatch_rq_from_bfqq()`.
6. `bfq_finish_requeue_request()` and `bfq_completed_request()` update stats, injection feedback, in-driver counters, expiration/idling decisions, refs, and private request state.

### Scheduling, Idling, and Budgets

- Requests are ordered by sync before async, metadata before non-metadata, then seek distance with limited backward seek support.
- BFQ budgets are sector-based. Async requests may be charged by `bfq_async_charge_factor` unless sync, weight-raised, or in an asymmetric scenario.
- `bfq_bfqq_update_budg_for_activation()` preserves remaining budget for queues that return quickly after idling, enabling service-hole recovery.
- `__bfq_bfqq_recalc_budget()` adapts queue budgets on expiration based on timeout, exhaustion, too-idle, or no-more-requests.
- `bfq_update_peak_rate()` estimates device peak rate from dispatch/completion timing and sequentiality, then updates dynamic max budget.
- `bfq_better_to_idle()` permits idling only when it boosts throughput or is required for service guarantees.

### Low-Latency Heuristics

- `bfq_bfqq_handle_idle_busy_switch()` detects interactive/soft-RT candidates, large bursts, and preemption opportunities.
- `bfq_update_bfqq_wr_on_rq_arrival()` starts or updates weight raising.
- `bfq_update_wr_data()` ends weight raising after max duration, large-burst suppression, or excessive service from weight raising.
- Soft real-time detection uses `soft_rt_next_start`, isochronous request patterns, bandwidth caps, and seekiness filters.

### Merge, Split, and Burst Handling

- `bfq_handle_burst()` detects rapid queue creation under the same parent and suppresses latency heuristics for large bursts to favor throughput.
- Cooperative merging uses request-position trees and close-sector detection, filtered by device type, ioprio class, parent entity, sync status, creation age, OOM queue, and seekiness.
- Stable merge uses the last-created queue per group/entity to combine flows likely belonging to the same application/task.
- Seeky cooperative queues can be marked for split and later detached through `bfq_split_bfqq()`, with saved queue state restored.

### Injection and Waker Handling

- When the in-service queue is empty but should idle, BFQ may inject:
  - async I/O from the same bic,
  - I/O from a detected waker queue,
  - I/O from a queue woken by the current queue,
  - budget-compatible work from active queues.
- `bfq_check_waker()` detects queues whose completions unblock another queue.
- `bfq_update_inject_limit()` adapts per-queue injection limits by comparing total service time with and without injected requests.

## Dependencies

- Linux block/elevator APIs: `blk_mq_*`, `blk_queue_*`, `blk_stat_*`, `wbt_*`, `elv_*`, `request_queue`, `request`, `bio`, `io_cq`, and request merge/hash helpers.
- Kernel infrastructure: hrtimers, ktime/jiffies, rb-trees, lists/hlists, slab caches, spinlocks, cgroups, `READ_ONCE`/`WRITE_ONCE`, and warning macros.
- BFQ WF2Q helpers from `bfq-wf2q.c`: queue activation/deactivation, requeue, service charging, next-queue selection, and in-service reset.
- BFQ cgroup helpers from `bfq-cgroup.c`: group lookup, queue migration, hierarchy creation, async queue cleanup, stats, and blkg/group refs.
- `bfq-iosched.h` provides queue/data/entity definitions, constants, flags, logging, and expiration enums.

## Risks and Invariants

- Most state is protected by `bfqd->lock`; `bfqd->queued` is intentionally read locklessly in `bfq_has_work()`.
- Queue refcounting is delicate: process refs, request allocation refs, weight-counter refs, stable-merge refs, async group pins, and merge-chain refs must balance.
- `bfqq_process_refs()` is central to avoiding unsafe merges/splits on queues that may be freed.
- Timer/idling paths must avoid expiring an idling queue in ways that break BFQ timestamp guarantees.
- Cooperative merging may impair fairness, so the code uses conservative filters and disables much merging on non-rotational queueing devices.
- Hardware queueing detection is sampled and approximate, but it drives major merge/idling decisions.
- Multi-actuator support depends on `disk->ia_ranges`; out-of-range bio sectors warn and fall back to actuator 0.
- This chunk initializes only `active_list[0]` and `active_list[1]` while later loops use `num_actuators`; verify against the full file/header context for supported actuator list initialization.

## Cross-Chunk References

- Lines after 7379 should bind these functions into the elevator via sysfs attributes, `elevator_type`, module init, and module exit.
- `bfq_init_queue()` depends on `ref_wr_duration[]` being initialized before queue creation; the module-init tail likely performs that conversion and calls `bfq_slab_setup()`.
- `bfq_slab_setup()` and `bfq_slab_kill()` are defined at the end of this chunk but likely called after line 7379.
- The final merged per-file report should add the exact elevator hook table, sysfs tunable bounds, and module registration/unregistration flow.