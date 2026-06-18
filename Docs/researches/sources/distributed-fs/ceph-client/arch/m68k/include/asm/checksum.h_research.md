<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/checksum.h -->
# sources/distributed-fs/ceph-client/arch/m68k/include/asm/checksum.h

## Purpose
This header provides m68k-optimized Internet checksum helpers unless `CONFIG_GENERIC_CSUM` selects generic code.

## Important APIs, Types, And Functions
- External helpers: `csum_partial()`, `csum_and_copy_from_user()`, and `csum_partial_copy_nocheck()`.
- `ip_fast_csum()` computes IPv4 header checksums using m68k add-with-extend loops.
- `csum_fold()` folds a 32-bit partial checksum to complemented 16-bit form.
- `csum_tcpudp_nofold()` and `csum_tcpudp_magic()` handle IPv4 pseudo-header checksums.
- `ip_compute_csum()` wraps `csum_partial()` and `csum_fold()`.
- `csum_ipv6_magic()` computes IPv6 pseudo-header checksums.

## Control Flow
Checksum functions run inline assembly loops over input words, preserving carry with `addx`/`addxl`. Copy-and-checksum helpers are implemented externally. Generic checksum code is included instead when configured.

## State And Persistence Behavior
The helpers are stateless except for reading buffers and writing destination buffers in copy variants. User-copy variants interact with user memory fault handling in their implementation.

## Dependencies And Integration Points
It depends on Linux checksum types, IPv6 address definitions, user pointer annotations, and networking stack checksum contracts.

## Risks And Edge Cases
Alignment and even-length assumptions matter for `csum_partial()`. Carry handling in inline assembly is architecture-sensitive. User-copy checksum paths must handle faults correctly and not leak partial state.

## Test Signals
Networking checksum selftests, IPv4/IPv6 TCP/UDP traffic, odd final fragment lengths, unaligned buffers, user-copy checksum fault tests, and generic-vs-arch checksum comparison validate behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/checksum.h -->
