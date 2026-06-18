# sources/distributed-fs/ceph-client/arch/arm/include/uapi/asm/perf_regs.h

## Purpose
`sources/distributed-fs/ceph-client/arch/arm/include/uapi/asm/perf_regs.h` enumerates ARM register
IDs for perf sample register masks. It is part of the vendored Linux ARM code under the Ceph client
source tree and has 24 source lines in this checkout.

## Important APIs, Types, and Functions
Primary API or contract surface: enum perf_event_arm_regs from R0 through PC and PERF_REG_ARM_MAX.
Important macros/constants include: `_ASM_ARM_PERF_REGS_H`.

## Control Flow
perf_event_open users and perf tooling use these IDs to request and decode register samples.

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
Primary risk: changing enum order breaks perf data ABI and cross-tool decoding. Changes should
preserve register layouts, numeric constants, early-boot calling conventions, and userspace/module
ABI boundaries implied by this file.

## Test Signals
Run `make headers_check` or the architecture header export path, compile representative ARM
userspace programs against the exported headers, and exercise ABI-specific tools such as strace,
gdb, perf, or stat/syscall tests depending on the constants in this file.
