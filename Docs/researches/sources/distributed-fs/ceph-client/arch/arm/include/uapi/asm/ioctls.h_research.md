# sources/distributed-fs/ceph-client/arch/arm/include/uapi/asm/ioctls.h

## Purpose
`sources/distributed-fs/ceph-client/arch/arm/include/uapi/asm/ioctls.h` adds ARM-specific ioctl
numbers before importing generic ioctl definitions. It is part of the vendored Linux ARM code under
the Ceph client source tree and has 9 source lines in this checkout.

## Important APIs, Types, and Functions
Primary API or contract surface: FIOQSIZE and asm-generic/ioctls.h.
Visible dependencies include: `asm-generic/ioctls.h`.
Important macros/constants include: `__ASM_ARM_IOCTLS_H`, `FIOQSIZE`.

## Control Flow
terminal and file descriptor ioctl callers share these constants with the kernel.

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
Primary risk: ioctl number collisions or changes break userspace command decoding. Changes should
preserve register layouts, numeric constants, early-boot calling conventions, and userspace/module
ABI boundaries implied by this file.

## Test Signals
Run `make headers_check` or the architecture header export path, compile representative ARM
userspace programs against the exported headers, and exercise ABI-specific tools such as strace,
gdb, perf, or stat/syscall tests depending on the constants in this file.
