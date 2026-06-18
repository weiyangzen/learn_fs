# sources/distributed-fs/ceph-client/arch/arm/include/uapi/asm/sigcontext.h

## Purpose
`sources/distributed-fs/ceph-client/arch/arm/include/uapi/asm/sigcontext.h` defines the signal frame
machine context saved for ARM signal delivery. It is part of the vendored Linux ARM code under the
Ceph client source tree and has 35 source lines in this checkout.

## Important APIs, Types, and Functions
Primary API or contract surface: struct sigcontext with trap/error, register, CPSR, and
fault_address fields.
Important macros/constants include: `_ASMARM_SIGCONTEXT_H`.

## Control Flow
signal setup stores interrupted register state and sigreturn restores it through this stable layout.

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
Primary risk: inserting fields before the end would break userspace signal handlers and unwinders.
Changes should preserve register layouts, numeric constants, early-boot calling conventions, and
userspace/module ABI boundaries implied by this file.

## Test Signals
Run `make headers_check` or the architecture header export path, compile representative ARM
userspace programs against the exported headers, and exercise ABI-specific tools such as strace,
gdb, perf, or stat/syscall tests depending on the constants in this file.
