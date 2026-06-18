## sources/distributed-fs/ceph-client/arch/arm64/include/asm/checksum.h

Purpose: implements fast arm64 IP checksum helpers and declares the generic checksum backend.

Important APIs/types/functions: exports `_HAVE_ARCH_IPV6_CSUM`, `csum_fold`, `ip_fast_csum`, `do_csum`, and includes generic checksum support. The IPv6 csum declaration is present through the generic interface.

Control flow: `csum_fold` folds a 32-bit partial checksum with carry handling. `ip_fast_csum` loops over IPv4 header words using inline assembly adds/adcs and returns a folded complement. `do_csum` is implemented elsewhere.

State and persistence: stateless computations over caller buffers.

Dependencies and integration: depends on network checksum types and generic checksum code. Used by IPv4/IPv6/TCP/UDP packet paths.

Risks: carry or endian mistakes cause packet drops or silent corruption. Test signals are networking checksum selftests, packet generators, IPv4 options coverage, IPv6 traffic, and cross-checking with software checksum fallback.
