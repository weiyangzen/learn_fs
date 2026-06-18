# sources/distributed-fs/ceph-client/tools/include/uapi/asm-generic/socket.h

## Purpose
Defines generic Linux `SOL_SOCKET` option numbers and control-message aliases for user-space socket consumers.

## Important APIs, Types, and Functions
Includes `<linux/posix_types.h>` and `<asm/sockios.h>`. Exports `SO_*` options from legacy options through newer BPF, zerocopy, timestamp, busy-poll, netns-cookie, pidfd, devmem, and rights-passing options. Defines timestamp/timeo old/new selector macros based on `__BITS_PER_LONG`, x32, `time_t`, and `__kernel_long_t`, then maps `SCM_TIMESTAMP*`.

## Control Flow, State, and Persistence
No runtime code. Conditional macro selection handles ABI differences for 32-bit time64 transitions and keeps powerpc overrides for credential/low-water options.

## Dependencies and Integration
Depends on socket ioctl and kernel type headers plus `__BITS_PER_LONG`. It integrates with networking tools, BPF socket options, timestamping users, and code that sends or receives ancillary data.

## Risks and Test Signals
Risks include selecting wrong old/new timestamp option on unusual ABIs, arch overrides hidden by include order, and using option numbers unsupported by the running kernel. Test signals include compile probes for 32-bit, 64-bit, and x32 and runtime `getsockopt()`/`setsockopt()` checks for representative options.
