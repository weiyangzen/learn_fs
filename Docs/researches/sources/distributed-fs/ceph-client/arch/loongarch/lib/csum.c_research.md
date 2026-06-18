# sources/distributed-fs/ceph-client/arch/loongarch/lib/csum.c

Purpose: provides optimized Internet checksum routines for LoongArch, including generic buffer checksum and IPv6 pseudo-header checksum.

Important APIs, types, and functions: `do_csum(const unsigned char *buff, int len)` is marked `__no_sanitize_address`; `csum_ipv6_magic()` is exported. `accumulate()` performs 64-bit one's-complement accumulation with carry.

Control flow: `do_csum()` performs an explicit KASAN read check, rounds the pointer down to an aligned 64-bit boundary, masks leading bytes, accumulates 64-byte chunks using `__uint128_t`, processes remaining 16/8-byte chunks, masks the tail over-read, folds to 16 bits, and swaps for odd alignment. `csum_ipv6_magic()` sums source/destination IPv6 addresses, length, protocol, and input checksum before folding.

State and persistence: no persistent state; pure computations over input buffers.

Dependencies and integration points: used by networking stack checksum paths; depends on KASAN explicit checks, endian helpers, `csum_fold()`, and int128 compiler support.

Risks: intentional over-read is safe only within same cache line/page assumptions and explicit KASAN coverage. Odd-alignment byte order and carry folding are subtle. Compiler codegen for int128 affects performance.

Test signals: networking checksum selftests, IPv4/IPv6 packet checksum validation, KASAN runs, odd/even alignment tests, and fuzzing against generic checksum implementation.
