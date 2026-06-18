# sources/distributed-fs/ceph-client/arch/arm/include/uapi/asm/Kbuild

## Purpose
`sources/distributed-fs/ceph-client/arch/arm/include/uapi/asm/Kbuild` declares generated and generic
UAPI headers for ARM. It is part of the vendored Linux ARM code under the Ceph client source tree
and has 5 source lines in this checkout.

## Important APIs, Types, and Functions
Primary API or contract surface: generated-y entries for unistd-oabi.h and unistd-eabi.h plus
generic-y kvm_para.h.
No standalone symbols are declared beyond build-system or include-level directives.

## Control Flow
Kbuild expands generated syscall headers into the exported UAPI include tree.

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
Primary risk: generated syscall header mismatches break userspace ABI and libc/kernel header
synchronization. Changes should preserve register layouts, numeric constants, early-boot calling
conventions, and userspace/module ABI boundaries implied by this file.

## Test Signals
Run `make headers_check` or the architecture header export path, compile representative ARM
userspace programs against the exported headers, and exercise ABI-specific tools such as strace,
gdb, perf, or stat/syscall tests depending on the constants in this file.
