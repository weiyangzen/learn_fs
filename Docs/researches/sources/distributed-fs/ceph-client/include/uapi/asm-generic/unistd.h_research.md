# sources/distributed-fs/ceph-client/include/uapi/asm-generic/unistd.h

## Purpose
Defines the generic Linux syscall number table and maps numbers to kernel syscall entry symbols for architectures that use the generic ABI.

## Important APIs, Types, And Functions
Exports `__NR_*` numbers from `io_setup` through `rseq_slice_yield`, `__NR_syscalls 472`, helper macros `__SC_3264`, `__SC_COMP`, `__SC_COMP_3264`, architecture-reserved range `__NR_arch_specific_syscall`, and aliases such as `__NR_fcntl`/`__NR_fcntl64` depending on word size.

## Control Flow
Preprocessor logic selects 32-bit versus 64-bit entry points, compat handlers, time32/time64 syscall exposure, optional legacy syscalls requested by `__ARCH_WANT_*`, and MMU-only calls skipped under `__ARCH_NOMMU`.

## State, Persistence, And Dependencies
No runtime state. The table is persistent ABI: numbers are embedded in libc, seccomp filters, tracers, audit, and applications. It depends on `<asm/bitsperlong.h>`.

## Integration Points
Used by architecture syscall tables, generated syscall wrappers, libc, seccomp BPF policies, audit, ptrace, strace, and all kernel syscall dispatch paths. Filesystem-relevant entries include xattrs, open, statfs, syncfs, statx, mount APIs, file attribute syscalls, and namespace listing.

## Risks
Numbers cannot be reused or reordered. Time32/time64 and compat mappings are subtle. Optional holes and architecture ranges must be preserved. `__NR_syscalls` must track the highest assigned generic number plus one.

## Test Signals
Generated syscall table comparison, libc syscall-number tests, seccomp allowlist tests, 32-bit compat and time64 syscall tests, `__NR_syscalls` bounds checks, and smoke tests for newly added numbers.
