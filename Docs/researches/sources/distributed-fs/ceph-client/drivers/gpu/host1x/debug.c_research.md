<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/host1x/debug.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/host1x/debug.c

## Purpose

`debug.c` implements host1x debugfs and printk dump support. It reports syncpoint state, waiters, mlocks, channel CDMA/FIFO state, and queued gathers, and exposes knobs for command-buffer tracing and timeout forcing.

## Important APIs, Types, And Functions

- `host1x_debug_output()` and `host1x_debug_cont()` format output through a generic `struct output`.
- `show_syncpts()` reads min/max values and counts fence waiters per syncpoint.
- `show_channel()` runtime-resumes the host, locks CDMA/debug locks, and delegates FIFO/CDMA decoding to hardware debug ops.
- `show_all()` prints mlocks, syncpoints, and all allocated channels.
- `host1x_debug_init()` / `host1x_debug_deinit()` create/remove debugfs files.
- `host1x_debug_dump()` writes the same full state to printk, used during timeout handling.

## Control Flow

Debugfs `status` and `status_all` call `show_all()` with FIFO disabled/enabled. Status collection resumes the device, locks enough state to avoid racing queue mutation, invokes hardware-specific decoders, and releases runtime PM. Timeout handling in `cdma_hw.c` calls `host1x_debug_dump()` before freezing a timed-out channel.

## State And Persistence Behavior

Persistent debug state includes the debugfs dentry, `host1x_debug_trace_cmdbuf`, and force-timeout variables. The output routines mostly observe hardware/software state but can load syncpoint registers into shadow values.

## Dependencies And Integration Points

Depends on debugfs, seq_file, runtime PM, channel/CDMA structures, syncpoint APIs, and hardware debug operation tables. Trace control integrates with `cdma.c` and `channel_hw.c`.

## Risks And Test Signals

Debug reads can fail if runtime resume fails. Hardware debug helpers must tolerate inactive channels and unmappable BOs. Tests should read debugfs during idle, active jobs, timeout, and suspend/resume, and verify no lockdep inversions among CDMA, debug, and syncpoint locks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/host1x/debug.c -->
