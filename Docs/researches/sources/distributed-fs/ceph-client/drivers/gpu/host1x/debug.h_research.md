<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/host1x/debug.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/host1x/debug.h

## Purpose

`debug.h` declares the generic host1x debug output abstraction and debug lifecycle APIs.

## Important APIs, Types, And Functions

- `struct output`: callback context plus a 256-byte formatting buffer.
- `write_to_seqfile()` and `write_to_printk()` adapt output to debugfs or printk.
- `host1x_debug_output()` / `host1x_debug_cont()` are printf-style helpers.
- `host1x_debug_trace_cmdbuf` controls command-buffer trace emission.
- Init/deinit/dump prototypes are consumed by `dev.c` and timeout code.

## Control Flow

The inline writers either call `seq_write()` or `pr_info()`/`pr_cont()`. Higher-level flow is in `debug.c`.

## State And Persistence Behavior

The header stores no state except declaring the external trace flag. Output buffers are stack/local in callers.

## Dependencies And Integration Points

It depends on debugfs/seq_file/printk and is included by generic and hardware debug implementations plus CDMA tracing code.

## Risks And Test Signals

Format strings must fit the buffer or be intentionally truncated by `vsnprintf()`. Build coverage and debugfs reads during active hardware are the main signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/host1x/debug.h -->
