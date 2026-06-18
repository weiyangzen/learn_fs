# sources/distributed-fs/ceph-client/include/linux/blktrace_api.h

## Purpose
`blktrace_api.h` declares the kernel side of block I/O tracing. It connects request queues, relay channels, trace setup ioctls, cgroup-aware trace messages, driver-private trace payloads, and request-to-sector formatting helpers.

## Important APIs, Types, And Functions
With `CONFIG_BLK_DEV_IO_TRACE`, `struct blk_trace` stores version, trace state, relay channel, per-cpu sequence and message buffers, action mask, LBA filter range, pid, device, debugfs directory, running list, and dropped count. Exported functions include `blk_trace_ioctl()`, `blk_trace_shutdown()`, `__blk_trace_note_message()`, `blk_add_driver_data()`, `blk_trace_setup()`, `blk_trace_startstop()`, and `blk_trace_remove()`.

Macros `blk_add_cgroup_trace_msg()` and `blk_add_trace_msg()` RCU-read `q->blk_trace` and emit formatted messages when tracing is active. `blk_trace_note_message_enabled()` checks whether notification tracing is enabled. `BLK_TN_MAX_MSG` caps message size. Without tracing config, the API compiles to `-ENOTTY`, no-op, or false stubs. Under `CONFIG_COMPAT`, `struct compat_blk_user_trace_setup` and `BLKTRACESETUP32` define the 32-bit setup ioctl layout.

Always-available helpers are `blk_fill_rwbs()`, `blk_rq_trace_sector()`, and `blk_rq_trace_nr_sectors()`. The sector helpers suppress sector counts for passthrough requests and unset sectors.

## Control Flow And State
Trace message emission is lockless from the caller perspective: enter RCU read-side section, dereference `q->blk_trace`, conditionally emit, then unlock. Setup/start/stop/remove manage relay and debugfs state in implementation code. Runtime trace state persists in `struct blk_trace`, referenced from `request_queue` under `CONFIG_BLK_DEV_IO_TRACE`.

## Dependencies And Integration Points
The header includes `blk-mq.h`, relay, compat, UAPI blktrace definitions, list, and blk types. It integrates with request queues, debugfs/relayfs, cgroup CSS for tagged messages, request tracing, and userspace blktrace tooling.

## Risks And Test Signals
Risks include RCU lifetime bugs, dropped trace accounting, message truncation, compat ioctl layout issues, tracing passthrough requests with bogus sectors, and missing stubs in non-trace builds. Tests should cover trace setup/start/stop/remove, concurrent queue teardown, cgroup trace messages, driver data payloads, compat setup ioctl, LBA/pid/action filters, and non-configured `-ENOTTY` behavior.
