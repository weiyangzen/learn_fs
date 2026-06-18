# File Research: sources/block-storage/util-linux/sys-utils/swapoff.c

This file implements `swapoff(8)`, disabling swap devices or files by path, `LABEL=`, `UUID=`, `-L`, `-U`, or `--all`. It uses the `swapoff(2)` syscall or a syscall fallback, libmount tables for `/proc/swaps` and fstab, blkid probing helpers, and the shared `swapon-common` infrastructure.

`do_swapoff()` resolves non-canonical specs through the global libmount cache and, for swap files, can resolve labels/UUIDs by scanning active swap files from `/proc/swaps` and probing them directly. It maps failures into bitwise exit codes distinguishing success, ENOMEM, generic swapoff failure, system errors, usage errors, all-failed, and mixed `--all` results.

`swapoff_all()` first disables active swaps from `/proc/swaps` in reverse order, counting success/failure, then scans fstab swap entries and quietly attempts inactive entries not already present. Main lowers its OOM killer score via `/proc/oom_adj`, initializes the libmount cache, processes labels, UUIDs, positional specs, and `--all`, then frees shared tables and returns the combined status.
