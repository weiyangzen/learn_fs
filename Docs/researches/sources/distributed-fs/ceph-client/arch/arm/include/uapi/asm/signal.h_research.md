# sources/distributed-fs/ceph-client/arch/arm/include/uapi/asm/signal.h

## Purpose
`sources/distributed-fs/ceph-client/arch/arm/include/uapi/asm/signal.h` defines ARM signal numbers,
sigaction layout, altstack type, and ARM-specific flags. It is part of the vendored Linux ARM code
under the Ceph client source tree and has 100 source lines in this checkout.

## Important APIs, Types, and Functions
Primary API or contract surface: NSIG, SIG* values, SIGRTMIN/MAX, SIGSWI, SA_THIRTYTWO, SA_RESTORER,
struct sigaction, and stack_t.
Visible dependencies include: `linux/types.h`, `asm-generic/signal-defs.h`.
Important macros/constants include: `_UAPI_ASMARM_SIGNAL_H`, `NSIG`, `SIGHUP`, `SIGINT`, `SIGQUIT`,
`SIGILL`, `SIGTRAP`, `SIGABRT`, `SIGIOT`, `SIGBUS`, `SIGFPE`, `SIGKILL`, `SIGUSR1`, `SIGSEGV`,
`SIGUSR2`, `SIGPIPE`, `SIGALRM`, `SIGTERM`, ... (46 total).

## Control Flow
libc and applications compile these constants into signal setup and handler dispatch.

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
Primary risk: signal number or struct layout changes are direct ABI breaks. Changes should preserve
register layouts, numeric constants, early-boot calling conventions, and userspace/module ABI
boundaries implied by this file.

## Test Signals
Run `make headers_check` or the architecture header export path, compile representative ARM
userspace programs against the exported headers, and exercise ABI-specific tools such as strace,
gdb, perf, or stat/syscall tests depending on the constants in this file.
