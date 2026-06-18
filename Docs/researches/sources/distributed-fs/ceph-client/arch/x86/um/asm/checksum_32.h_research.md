<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/um/asm/checksum_32.h -->
# sources/distributed-fs/ceph-client/arch/x86/um/asm/checksum_32.h

## Purpose
`checksum_32.h` adds 32-bit UML checksum helpers, including IPv6 pseudo-header checksum assembly.

## Important APIs, types, and functions
APIs are `ip_compute_csum()` and `_HAVE_ARCH_IPV6_CSUM` `csum_ipv6_magic()`.

## Control flow
`ip_compute_csum()` folds `csum_partial()`. `csum_ipv6_magic()` adds source/destination IPv6 words, length, protocol, and incoming sum with carry propagation before folding.

## State and persistence behavior
No persistent state exists.

## Dependencies and integration points
It depends on `csum_partial()`, `csum_fold()`, and network byte-order helpers.

## Risks and edge cases
Carry handling and htonl inputs must match Linux checksum ABI; 32-bit register constraints are architecture-specific.

## Test signals
Signals are IPv4/IPv6 networking tests and checksum validation against generic implementations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/um/asm/checksum_32.h -->
