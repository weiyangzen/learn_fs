# sources/distributed-fs/ceph-client/arch/arm/include/uapi/asm/hwcap.h

## Purpose
`sources/distributed-fs/ceph-client/arch/arm/include/uapi/asm/hwcap.h` defines ARM AT_HWCAP and
AT_HWCAP2 feature bits. It is part of the vendored Linux ARM code under the Ceph client source tree
and has 49 source lines in this checkout.

## Important APIs, Types, and Functions
Primary API or contract surface: HWCAP_* CPU feature bits and HWCAP2_* crypto/speculation feature
bits.
Important macros/constants include: `_UAPI__ASMARM_HWCAP_H`, `HWCAP_SWP`, `HWCAP_HALF`,
`HWCAP_THUMB`, `HWCAP_26BIT`, `HWCAP_FAST_MULT`, `HWCAP_FPA`, `HWCAP_VFP`, `HWCAP_EDSP`,
`HWCAP_JAVA`, `HWCAP_IWMMXT`, `HWCAP_CRUNCH`, `HWCAP_THUMBEE`, `HWCAP_NEON`, `HWCAP_VFPv3`,
`HWCAP_VFPv3D16`, `HWCAP_TLS`, `HWCAP_VFPv4`, ... (37 total).

## Control Flow
kernel ELF setup fills auxv feature masks and libc/JITs dispatch on these values.

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
Primary risk: feature bit reuse or inaccurate exposure can crash optimized userspace code paths.
Changes should preserve register layouts, numeric constants, early-boot calling conventions, and
userspace/module ABI boundaries implied by this file.

## Test Signals
Run `make headers_check` or the architecture header export path, compile representative ARM
userspace programs against the exported headers, and exercise ABI-specific tools such as strace,
gdb, perf, or stat/syscall tests depending on the constants in this file.
