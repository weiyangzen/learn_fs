# sources/distributed-fs/ceph-client/arch/arm/include/uapi/asm/stat.h

## Purpose
`sources/distributed-fs/ceph-client/arch/arm/include/uapi/asm/stat.h` defines ARM old stat, stat,
and stat64 UAPI layouts. It is part of the vendored Linux ARM code under the Ceph client source tree
and has 88 source lines in this checkout.

## Important APIs, Types, and Functions
Primary API or contract surface: struct __old_kernel_stat, STAT_HAVE_NSEC, struct stat, struct
stat64, STAT64_HAS_BROKEN_ST_INO.
Important macros/constants include: `_ASMARM_STAT_H`, `STAT_HAVE_NSEC`, `STAT64_HAS_BROKEN_ST_INO`.

## Control Flow
sys_stat family calls copy these exact layouts to userspace, including endian and padding rules.

## State and Persistence Behavior
The file stores no runtime state. It persists as exported kernel header text, and the values become
compiled into userspace programs, libc headers, debugging tools, or boot-loader interfaces. That
makes the definitions effectively persistent ABI even when the kernel source changes later.

## Dependencies and Integration Points
This exported header integrates with libc, tracing/debugging tools, the ELF loader, syscall
wrappers, and kernel implementation files that include the same UAPI definitions. Its numeric
constants and structure layouts are part of the ARM userspace ABI and must remain compatible across
kernel releases.

## Risks
Primary risk: padding or field width changes corrupt filesystem metadata observed by old binaries.
Changes should preserve register layouts, numeric constants, early-boot calling conventions, and
userspace/module ABI boundaries implied by this file.

## Test Signals
Run `make headers_check` or the architecture header export path, compile representative ARM
userspace programs against the exported headers, and exercise ABI-specific tools such as strace,
gdb, perf, or stat/syscall tests depending on the constants in this file.
