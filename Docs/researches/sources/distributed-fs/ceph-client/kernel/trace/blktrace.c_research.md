# sources/distributed-fs/ceph-client/kernel/trace/blktrace.c

## Purpose

`blktrace.c` implements block I/O tracing. With `CONFIG_BLK_DEV_IO_TRACE`, it provides the legacy debugfs/relayfs blktrace ioctl/sysfs interface, registers block tracepoint probes, records request/bio/remap/plug/unplug/zone/message events, and exposes a `blk` ftrace tracer. With `CONFIG_EVENT_TRACING`, it also provides `blk_fill_rwbs()` for block trace event formatting.

## Important APIs, types, and functions

- Public exported APIs: `blk_trace_setup()`, `blk_trace_startstop()`, `blk_trace_remove()`, `blk_trace_ioctl()`, `blk_trace_shutdown()`, `__blk_trace_note_message()`, `blk_add_driver_data()`, and `blk_fill_rwbs()`.
- Event recorders: `record_blktrace_event()` for v1 `struct blk_io_trace`, `record_blktrace_event2()` for v2 `struct blk_io_trace2`, and `relay_blktrace_event*()` for relayfs output.
- Core logging path: `__blk_add_trace()` maps request operation/flags to blktrace actions, filters by action mask/LBA/pid, writes to either ftrace ring buffer or relay channel, and handles cgroup IDs.
- Setup/teardown: `blk_trace_setup_prepare()`, `blk_trace_setup_finalize()`, `blk_trace_setup()`, `blk_trace_setup2()`, optional `compat_blk_trace_setup()`, `blk_trace_start()`, `blk_trace_stop()`, `blk_trace_cleanup()`, and `blk_trace_free()`.
- User interfaces: ioctl handler `blk_trace_ioctl()`, debugfs files `dropped` and `msg`, relay callbacks, and sysfs attributes `trace/enable`, `act_mask`, `pid`, `start_lba`, and `end_lba`.
- Tracepoint probes: request events (`insert`, `issue`, `merge`, `requeue`, `complete`), bio events (`queue`, `complete`, merges, getrq), plug/unplug, split, remap, zone write plug/unplug, zone append update, and driver data.
- Ftrace output: `fill_rwbs()`, `blk_log_*()` helpers, `what2act`, `print_one_line()`, `blk_trace_event_print()`, `blk_trace_event_print_binary()`, tracer callbacks, `trace_blk_event`, and `blk_tracer`.

## Control flow

For ioctl-based tracing, users call `BLKTRACESETUP` or `BLKTRACESETUP2`. `blk_trace_ioctl()` resolves the request queue and dispatches to setup helpers. `blk_trace_setup_prepare()` rejects concurrent traces on the same queue, allocates `struct blk_trace`, per-CPU sequence counters and message buffers, creates/reuses debugfs directories, creates `dropped` and `msg`, opens a relay channel, and initializes the LBA range. `blk_trace_setup_finalize()` copies the user-visible name, records version/action mask/range/pid, stores `Blktrace_setup`, publishes `q->blk_trace` with RCU, and increments the global probe reference count. The first reference registers block tracepoint callbacks.

`BLKTRACESTART` moves a trace from setup/stopped to running, increments `blktrace_seq`, links the trace on `running_trace_list`, and emits a timestamp note. `BLKTRACESTOP` marks it stopped, removes it from the running list, and flushes relay buffers. Teardown removes `q->blk_trace`, stops tracing, waits for RCU readers, closes relay/debugfs/percpu resources, and unregisters tracepoints when the global reference count drops to zero.

The sysfs path under `/sys/block/.../trace` can lazily create `struct blk_trace` with `blk_trace_setup_queue()` and remove it with `blk_trace_remove_queue()`. This path does not allocate a relay channel and is used with the ftrace `blk` tracer. The implementation explicitly normalizes uninitialized `bt->version == 0` to v2 in the ftrace recording path to avoid zero-length allocation/format mismatches.

Tracepoint callbacks run under RCU, load `q->blk_trace`, derive sector/bytes/op flags/cgroup ID, and call `__blk_add_trace()`. That function adds read/write/sync/readahead/meta/flush/FUA/zone/discard/write-zeroes classification bits, drops v2-only zone operations for v1 traces, filters by action mask, LBA range, and pid, and then writes either to the ftrace ring buffer (`TRACE_BLK`) or relay per-CPU buffer. Relay writes disable local IRQs while reserving per-CPU buffer space and incrementing the per-CPU sequence number.

The ftrace `blk` tracer registers a trace event and tracer during `device_initcall(init_blk_tracer)`, sometimes deferred to `trace_init_wq`. When enabled, `blk_tracer_enabled` diverts events into the tracing ring buffer. Printing uses `what2act` and `blk_log_*()` helpers to render classic or non-classic lines, optional cgroup IDs/names, binary v1-compatible output, and message/remap/PDU data.

## State and persistence behavior

Per-queue state lives in `struct blk_trace` referenced by `request_queue::blk_trace` under RCU. It includes version, trace state, relay channel, percpu sequence counters, percpu message buffers, action mask, LBA range, pid filter, device, debugfs directory, and running-list node. Global state includes `blktrace_seq`, `blk_tr`, `blk_tracer_enabled`, `running_trace_list`, `running_trace_lock`, `blk_probe_mutex`, and `blk_probes_ref`.

`q->blk_trace` publication/removal uses RCU so tracepoint callbacks can run locklessly. Debugfs setup/removal is serialized by the queue debugfs mutex. The running trace list is raw-spinlock protected because notes may be emitted with interrupts disabled. Probe registration is reference-counted so tracepoints are registered only while at least one trace is active/configured.

## Dependencies and integration points

The file depends on block-layer request/bio APIs, `linux/blktrace_api.h`, UAPI blktrace formats, relayfs, debugfs, sysfs device attributes, tracepoints from `trace/events/block.h`, ftrace ring buffer/tracer APIs, cgroup IDs under `CONFIG_BLK_CGROUP`, RCU, per-CPU allocation, compat ioctl support on x86_64, and `../../block/blk.h` queue debugfs helpers.

It is built in two modes: full blktrace under `CONFIG_BLK_DEV_IO_TRACE`, and event-format helper support under `CONFIG_EVENT_TRACING`. Its outputs are consumed by legacy `blktrace` tooling, tracefs `current_tracer=blk`, `trace_pipe`, perf/ftrace event consumers, and block trace event formatters.

## Risks and edge cases

- ABI compatibility is delicate. v1 and v2 trace records differ, and the ftrace path always prefers v2 while binary output can synthesize v1. Incorrect lengths or layouts corrupt trace buffers or user tooling.
- The sysfs path creates a `blk_trace` without relay channel or initialized version; the code contains explicit handling for version zero in `__blk_add_trace()`.
- Concurrent setup is rejected per queue, but callbacks may race teardown; RCU grace periods and probe reference counting are required for safety.
- Relay reservation failures silently drop events; `dropped` reports full-buffer drops but not every possible filtering/drop reason.
- LBA and pid filters can hide expected events; action masks are shifted into action bits and easy to misconfigure.
- Cgroup output changes PDU layout by prepending an ID, so all formatting and binary consumers must agree on `__BLK_TA_CGROUP`/`__BLK_TN_CGROUP`.
- Local IRQ disabling around relay writes protects per-CPU buffers but increases latency on hot block paths.

## Test signals

Useful signals include ioctl setup/start/stop/teardown with legacy blktrace tools, sysfs `trace/enable` toggling, ftrace `blk` tracer output, action-mask string parsing, pid/LBA filtering, cgroup ID/name formatting, request and bio tracepoint coverage, zone operation tracing with v2 and rejection with v1, remap/split/plug/unplug formatting, relay `dropped` accounting, teardown under active I/O, and KASAN/KCSAN/lockdep runs for buffer length and RCU lifetime issues.
