# sources/distributed-fs/ceph-client/kernel/entry/Makefile

## Purpose

This Makefile builds the generic kernel entry subsystem objects while disabling instrumentation that is unsafe for `noinstr` entry code. It controls sanitizer, coverage, branch profiling, and stack protector settings for files that run at interrupt, syscall, and user/guest transition boundaries.

## Important APIs, Types, And Functions

- `KASAN_SANITIZE := n`, `UBSAN_SANITIZE := n`, and `KCOV_INSTRUMENT := n` disable sanitizers and coverage for this directory.
- `ccflags-$(CONFIG_TRACE_BRANCH_PROFILING) += -DDISABLE_BRANCH_PROFILING` disables branch profiling when tracing branch profiling is enabled.
- `CFLAGS_REMOVE_common.o` removes stack protector flags for `common.o`, and `CFLAGS_common.o += -fno-stack-protector` enforces no stack protector.
- Object selection: `common.o` for `CONFIG_GENERIC_IRQ_ENTRY`, `syscall-common.o` and `syscall_user_dispatch.o` for `CONFIG_GENERIC_SYSCALL`, and `virt.o` for `CONFIG_VIRT_XFER_TO_GUEST_WORK`.

## Control Flow

Kbuild evaluates configuration symbols and includes only the matching objects. The build flags are applied before compiling the entry code so runtime behavior remains compatible with `noinstr` constraints.

## State And Persistence Behavior

There is no runtime state. The file affects build outputs and compiler instrumentation choices.

## Dependencies And Integration Points

The Makefile integrates with Kbuild, generic IRQ entry, generic syscall handling, syscall user dispatch, virtual guest-transfer work handling, sanitizer tooling, KCOV, branch profiling, and compiler stack-protector flags.

## Risks And Edge Cases

- Re-enabling sanitizers, coverage, branch profiling, or stack protector in `noinstr` entry paths can introduce instrumentation calls where tracing/RCU/lockdep state is not safe.
- Missing config guards can either omit required entry behavior or compile code on architectures that do not support it.

## Test Signals

Build kernels with combinations of `CONFIG_GENERIC_IRQ_ENTRY`, `CONFIG_GENERIC_SYSCALL`, `CONFIG_VIRT_XFER_TO_GUEST_WORK`, sanitizers, KCOV, branch profiling, and stack protector enabled. Runtime entry validation includes objtool/noinstr warnings, boot tests, interrupt/syscall smoke tests, and tracing sanity checks.
