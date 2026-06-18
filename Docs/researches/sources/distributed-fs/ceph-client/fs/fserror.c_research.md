# sources/distributed-fs/ceph-client/fs/fserror.c

## Purpose
`fserror.c` provides asynchronous filesystem error reporting. It lets filesystem and iomap code report metadata, shutdown, and I/O errors to a superblock callback and fsnotify without running arbitrary notification code in atomic or locked contexts.

## Important APIs, Types, and Functions
- `fserror_mount()` initializes `sb->s_pending_errors` with a bias.
- `fserror_unmount()` drops the bias and waits for pending reports to drain.
- `fserror_report()` allocates an event, records type/range/error/inode, and schedules work.
- `fserror_worker()` invokes `sb->s_op->report_error()` when present and emits `fsnotify(FS_ERROR, ...)`.
- `fserror_init()` initializes a mempool of `struct fserror_event`.

## Control Flow
Callers invoke `fserror_report()` with a negative errno and optional inode/range. The allocator increments `s_pending_errors` only if nonzero and `SB_ACTIVE` is still set. If allocation and optional `igrab()` succeed, work is queued. The worker builds a positive error number for userspace-facing `fs_error_report`, calls the filesystem callback, sends fsnotify, drops the inode, decrements the pending counter, and returns the event to the mempool. Unmount waits until the biased pending counter goes below one.

## State and Persistence
State is volatile: a global mempool and per-superblock pending counter. Events hold a superblock pointer, optional active inode ref, error metadata, and a work item. There is no persistent error journal in this file; delivery can be lost under allocation or inode ref failure and is logged rate-limited.

## Dependencies and Integration Points
It integrates with `fs/super.c` mount/unmount lifecycle, `super_operations::report_error`, fsnotify, iomap error reporters, ext4/btrfs callers, inode refcounting, and workqueues.

## Risks
The file is sensitive to teardown ordering: `SB_ACTIVE` and `s_pending_errors` checks must prevent reports from racing past unmount. Since the mempool is finite, extreme bursts can still lose reports. Callers must pass negative errors and matching inode/superblock pairs; violations only warn. `report_error` implementations must tolerate process-context asynchronous delivery.

## Test Signals
Tests should trigger file I/O errors, metadata errors, shutdown errors, unmount with queued reports, memory pressure allocation fallback, and fsnotify consumers. Signals include no use-after-free during unmount, rate-limited lost-report logs only under induced failure, and callback delivery ordering.
