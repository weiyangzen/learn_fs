# sources/distributed-fs/ceph-client/include/uapi/asm-generic/signal.h

## Purpose
Defines generic signal numbers, signal set layout, `struct sigaction`, and alternate signal stack structure for new Linux architectures.

## Important APIs, Types, And Functions
Exports `_NSIG`, `_NSIG_BPW`, `_NSIG_WORDS`, standard signal numbers 1-31, realtime range `SIGRTMIN` to `SIGRTMAX`, `MINSIGSTKSZ`, `SIGSTKSZ`, `sigset_t`, `old_sigset_t`, `struct sigaction`, and `stack_t`.

## Control Flow
Compile-time logic sizes `sigset_t` from `__BITS_PER_LONG`, imports `asm-generic/signal-defs.h`, marks `__ARCH_HAS_SA_RESTORER` if an architecture defines `SA_RESTORER`, and hides user-visible `struct sigaction` inside kernel builds.

## State, Persistence, And Dependencies
No runtime state. The bitset and structure layouts persist in process signal masks, syscall arguments, and signal frames. It depends on `<linux/types.h>` and generic signal definitions.

## Integration Points
Used by `rt_sigaction`, `rt_sigprocmask`, `sigaltstack`, signal frame construction, libc signal APIs, and `ucontext.h` through `stack_t` and `sigset_t`.

## Risks
Signal numbers and `sigset_t` word layout are ABI. Architecture overrides must avoid conflicting with the generic realtime range and stack constants. `sa_mask` being last is an extensibility contract.

## Test Signals
Run signal number ABI checks, `sigset_t` size tests across 32/64-bit builds, `sigaltstack` delivery tests, `SA_RESTORER` architecture smoke tests, and libc header compatibility builds.
