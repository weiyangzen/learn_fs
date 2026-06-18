# sources/distributed-fs/ceph-client/include/linux/signal_types.h

## Purpose

`signal_types.h` defines the core kernel signal data structures shared by signal handling code: kernel siginfo, queued realtime signal objects, pending signal sets, sigaction wrappers, delivered signal state, and valid userspace sigaction flags.

## Important APIs, Types, And Functions

Types are `kernel_siginfo_t`, `struct sigqueue`, `struct sigpending`, `struct sigaction`, `struct k_sigaction`, optional `struct old_sigaction`, and `struct ksignal`. `struct sigqueue` stores list linkage, flags, kernel siginfo, and `ucounts` charging. `struct sigpending` stores queued signal list and aggregate signal set. `struct sigaction` is architecture-sensitive around IRIX ordering and optional restorer fields. `struct ksignal` combines selected action, siginfo, and signal number for delivery.

Constants include `SIGQUEUE_PREALLOC`, `SA_IMMUTABLE`, `__ARCH_UAPI_SA_FLAGS`, and `UAPI_SA_FLAGS`.

## Control Flow

There is no executable flow. Signal code allocates and links `sigqueue` objects, accumulates pending masks in `sigpending`, stores user-visible actions in `sigaction`, wraps them as `k_sigaction`, and passes one selected signal as `ksignal` to architecture frame setup.

## State And Persistence

Queued realtime signals persist until delivered or flushed. `sigpending.signal` is the aggregate pending bitset, while `sigpending.list` stores queued detail. `sigaction` state persists in each process signal handler table. `SA_IMMUTABLE` protects forced signal action races.

## Dependencies And Integration Points

Dependencies include kernel types and UAPI signal definitions. Integration points are signal syscalls, realtime signal queues, ucounts resource accounting, architecture signal frame setup, old ABI compatibility, and userspace sigaction flag validation.

## Risks And Test Signals

Risks are ABI layout mismatches across architectures, missing restorer handling, realtime queue accounting leaks, and allowing invalid UAPI sigaction flags. Test signals include ABI build checks, old sigaction compatibility, realtime signal queue limits, forced-signal race tests, and architecture signal frame tests.
