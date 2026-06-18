# sources/distributed-fs/ceph-client/fs/ext2/trace.h

## Purpose

`fs/ext2/trace.h` declares ext2 tracepoints for direct-I/O read and write paths. It uses the Linux trace event macro language to record inode, device, file size, IO position, request length, kiocb flags, async/sync mode, and return status around direct-I/O operations.

## Important APIs, types, and functions

- `TRACE_SYSTEM ext2` names the trace subsystem.
- `DECLARE_EVENT_CLASS(ext2_dio_class, ...)` defines the common payload for most direct-I/O events using `struct kiocb`, `struct iov_iter`, and an `ssize_t ret`.
- `DEFINE_DIO_RW_EVENT()` instantiates `ext2_dio_write_begin`, `ext2_dio_write_end`, `ext2_dio_write_buff_end`, `ext2_dio_read_begin`, and `ext2_dio_read_end`.
- `TRACE_EVENT(ext2_dio_write_endio, ...)` adds an end-IO-specific event with completed size and integer return value.
- `TP_fast_assign` derives `dev`, `ino`, `isize`, `pos`, `count` or `size`, `ki_flags`, `aio`, and `ret`.
- `TP_printk` formats device major/minor, inode, size, position, length, IOCB flag strings, async status, and return value.

## Control flow

The header is normally included by trace callers in declaration mode and once by `trace.c` in definition mode. At runtime, ext2 direct-I/O paths call generated `trace_ext2_*` helpers. When disabled, tracepoints are low-overhead static keys; when enabled, the fast assignment code snapshots the current IO state and emits formatted records.

## State and persistence behavior

Trace payloads are transient diagnostic records. They do not persist to ext2 media and do not mutate ext2 state. They do expose live inode size and kiocb state at the time the tracepoint is hit, which is useful for debugging races and partial IO behavior.

## Dependencies and integration points

The header depends on `<linux/tracepoint.h>`, `TRACE_IOCB_STRINGS` from kernel tracing helpers, VFS `file_inode()`, kiocb state, and `iov_iter_count()`. `TRACE_INCLUDE_PATH .` and `TRACE_INCLUDE_FILE trace` make generated trace code locate this file from the ext2 build directory.

## Risks and edge cases

Tracepoint ABI names are externally visible to tracing scripts. Renaming events or fields can break diagnostics even though filesystem behavior is unchanged. Values such as `i_size` and `ki_pos` are sampled without locking beyond caller context, so consumers should treat them as observational data rather than synchronization. The class assumes `iocb->ki_filp` is valid.

## Test signals

Compile-test with tracing, enable each ext2 direct-I/O tracepoint, perform direct reads/writes including async and sync kiocb paths, verify IOCB flags print correctly, and check that error/short-IO return values appear in begin/end/endio event streams.
