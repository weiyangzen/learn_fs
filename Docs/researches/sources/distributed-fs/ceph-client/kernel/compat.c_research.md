# sources/distributed-fs/ceph-client/kernel/compat.c

## Purpose

`compat.c` provides 32-bit compatibility helpers and compat syscall implementations used by 64-bit kernels serving 32-bit userspace ABIs.

## Important APIs, Types, and Functions

Functions include optional `compat_sys_sigprocmask()`, `put_compat_rusage()`, `compat_sched_setaffinity()`, `compat_sched_getaffinity()`, `get_compat_sigevent()`, `compat_get_bitmap()`, `compat_put_bitmap()`, and exported `get_compat_sigset()`.

## Control Flow and State

`compat_sys_sigprocmask()` translates an old compat signal mask, rejects attempts to block `SIGKILL`/`SIGSTOP`, applies the requested operation to `current->blocked`, and optionally copies out the old mask. `put_compat_rusage()` narrows a native `rusage` into `compat_rusage` and copies it to userspace. Compat affinity syscalls allocate cpumasks, translate compat bitmaps, and call native scheduler affinity helpers. `get_compat_sigevent()` copies the fields the kernel needs from a compat sigevent. Bitmap helpers pack and unpack pairs of compat words into native words.

## Dependencies and Integration Points

It depends on compat ABI types, uaccess primitives, scheduler affinity APIs, signal APIs, rusage/timer structures, endian-specific signal-set layout, and architecture Kconfig such as `__ARCH_WANT_SYS_SIGPROCMASK`.

## Risks and Edge Cases

The main risks are userspace pointer faults, size/alignment validation, endian conversion for signal sets, truncation or layout mismatch between native and compat structures, and cpumask length handling. Affinity get rejects lengths too small for `nr_cpu_ids` and lengths not aligned to compat word size.

## Test Signals

Tests should run 32-bit programs on a compat kernel path for signal masks, affinity set/get with short, exact, long, and misaligned lengths, `getrusage()` field translation, sigevent creation, bitmap round trips on big- and little-endian builds, and fault injection for bad userspace pointers.
