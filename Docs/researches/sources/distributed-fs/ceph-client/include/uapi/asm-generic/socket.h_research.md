# sources/distributed-fs/ceph-client/include/uapi/asm-generic/socket.h

## Purpose
Defines generic `SOL_SOCKET` option numbers and related `SCM_*` control-message aliases for socket syscalls.

## Important APIs, Types, And Functions
Exports `SO_*` constants for buffer sizing, credentials, timestamps, BPF filters, reuseport BPF, busy polling, zerocopy, txtime, netns cookies, device memory, priority, pass-rights, and `SO_INQ`. It also maps old/new time64-sensitive options through `SO_TIMESTAMP`, `SO_RCVTIMEO`, and `SO_SNDTIMEO`.

## Control Flow
Preprocessor logic preserves powerpc-specific credential option overrides and chooses old versus new timestamp/timeval option numbers based on `__BITS_PER_LONG`, x32, and `sizeof(time_t)` in user space.

## State, Persistence, And Dependencies
No local state. The constants select per-socket kernel state via `setsockopt`, `getsockopt`, and ancillary data. It depends on `<linux/posix_types.h>` and `<asm/sockios.h>`.

## Integration Points
Consumed by networking stacks, libc socket headers, applications, BPF socket filters, timestamping APIs, ioctls from `sockios.h`, and protocol families that honor socket-level options.

## Risks
Numeric option values are stable ABI. Time option remapping is subtle for 32-bit time64 transitions. `SCM_*` aliases must track their matching `SO_*` options. Privileged options such as force buffers, marks, and priority need kernel-side permission checks.

## Test Signals
Build header tests across 32-bit, 64-bit, and x32; `setsockopt`/`getsockopt` round trips for each option family; timestamp ABI tests with 32-bit time64; ancillary data decoding tests; BPF attach/detach and reuseport tests.
