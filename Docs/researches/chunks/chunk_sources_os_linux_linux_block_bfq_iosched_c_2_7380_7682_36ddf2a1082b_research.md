# Chunk Research: sources/os/linux/linux/block/bfq-iosched.c lines 7380-7682

## Scope

This chunk is the BFQ multi-queue elevator's sysfs tuning surface, elevator registration record, module initialization, and module teardown. It wires earlier BFQ request scheduling, queue lifecycle, cgroup, and weight-raising logic into the Linux block elevator framework.

Primary lines covered: `sources/os/linux/linux/block/bfq-iosched.c:7380-7682`.

## APIs and Entry Points

- `bfq_var_show()` formats an unsigned tunable as a newline-terminated decimal string for sysfs.
- `bfq_var_store()` parses a base-10 unsigned long from a sysfs write using `kstrtoul()`.
- Macro-generated `*_show()` / `*_store()` handlers expose and update BFQ per-device fields from `struct bfq_data`, with conversions between raw values, jiffies, milliseconds, nanoseconds, and microseconds.
- Custom stores update coupled state:
  - `bfq_max_budget_store()` handles auto mode when user value is `0`.
  - `bfq_timeout_sync_store()` updates timeout and recomputes auto budget when needed.
  - `bfq_strict_guarantees_store()` can raise `bfq_slice_idle` to at least `8 ms`.
  - `bfq_low_latency_store()` calls `bfq_end_wr()` before disabling low-latency heuristics.
- `bfq_attrs[]` publishes the elevator sysfs knobs: `fifo_expire_sync`, `fifo_expire_async`, `back_seek_max`, `back_seek_penalty`, `slice_idle`, `slice_idle_us`, `max_budget`, `timeout_sync`, `strict_guarantees`, and `low_latency`.
- `iosched_bfq_mq` registers BFQ as elevator name `"bfq"`.
- `bfq_init()` and `bfq_exit()` define module lifetime setup and teardown.

## Control Flow

Sysfs reads go through the elevator sysfs layer into BFQ show handlers, fetch `e->elevator_data` as `struct bfq_data`, convert the selected field if needed, and format it through `bfq_var_show()`.

Sysfs writes parse the input, clamp ranges, convert user units to internal units, then update scheduler state. Budget and timeout writes can recompute `bfq_max_budget`; disabling low latency clears active weight raising.

`iosched_bfq_mq` binds earlier functions into the block-mq scheduler ABI: request depth limiting, request prepare/finish/requeue, insertion, dispatch, merge handling, work detection, depth updates, and queue init/exit.

`bfq_init()` registers the BFQ blkcg policy when configured, creates the BFQ queue slab cache, initializes `ref_wr_duration[]`, then calls `elv_register()`. Failure paths unwind in reverse order. `bfq_exit()` unregisters the elevator, unregisters blkcg policy when present, and destroys the slab cache.

## State and Dependencies

Touched `struct bfq_data` fields include `bfq_fifo_expire[]`, `bfq_back_max`, `bfq_back_penalty`, `bfq_slice_idle`, `bfq_max_budget`, `bfq_user_max_budget`, `bfq_timeout`, `strict_guarantees`, and `low_latency`.

Important dependencies:

- `bfq_calc_max_budget()` depends on `peak_rate` and `bfq_timeout`.
- `bfq_end_wr()` clears weight-raising state across active, idle, and async queues.
- `ref_wr_duration[]` is initialized here and consumed by earlier weight-raising/throughput code.
- `bfq_pool` is managed through adjacent slab setup/kill helpers.
- `blkcg_policy_bfq` comes from `bfq-cgroup.c` under `CONFIG_BFQ_GROUP_IOSCHED`.

## Risks and Edge Cases

- Generated show handlers use a `u64` temporary but pass through `bfq_var_show(unsigned int)`, so very large displayed values can truncate.
- Store handlers silently clamp out-of-range inputs instead of rejecting them.
- `bfq_slice_idle` is a `u32`; large millisecond or microsecond inputs are converted to nanoseconds and can overflow/truncate on assignment.
- Enabling `strict_guarantees` mutates `bfq_slice_idle`; disabling it does not restore the old value.
- Disabling `low_latency` has a side effect beyond flag assignment: it tears down weight raising via `bfq_end_wr()`.
- Module init cleanup ordering must stay aligned with setup ordering: blkcg policy, slab cache, then elevator registration.

## Cross-Chunk References

- Earlier `bfq_init_queue()` seeds the tunables exposed here.
- Earlier `bfq_limit_depth()` and `bfq_depth_updated()` are installed into the elevator ops table here.
- Earlier merge, dispatch, insert, request lifecycle, and I/O context functions become externally reachable through `iosched_bfq_mq`.
- Earlier weight-raising logic is controlled by this chunk’s `low_latency` sysfs knob.
- `bfq-cgroup.c` provides `blkcg_policy_bfq`, registered and unregistered at module boundaries here.