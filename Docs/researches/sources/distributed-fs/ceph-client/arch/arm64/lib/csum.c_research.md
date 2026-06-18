# sources/distributed-fs/ceph-client/arch/arm64/lib/csum.c

Purpose: implements optimized ARM64 Internet checksum helpers, including raw buffer checksum accumulation and IPv6 pseudo-header checksum.

Important APIs/types/functions: `accumulate`, `do_csum`, `csum_ipv6_magic`, explicit `kasan_check_read`, 64/128-bit accumulation, endian-specific folding, and exported `csum_ipv6_magic`.

Control flow: `do_csum` validates length, performs a manual KASAN read check, aligns down to an 8-byte boundary, masks leading overread bytes, accumulates 64-byte and 16-byte body chunks using 128-bit carry folding, masks tail overread bytes, folds to 16 bits, and compensates odd initial alignment. `csum_ipv6_magic` loads source/destination IPv6 addresses as 128-bit values, adds length/protocol/checksum, folds each address half, and returns `csum_fold`.

State and persistence: reads packet buffers and returns checksum values. No persistent state.

Dependencies/integration: used by network checksum paths; depends on `<net/checksum.h>`, KASAN APIs, compiler support for `__uint128_t`, and endian configuration.

Risks: deliberate head/tail overreads require the explicit KASAN check and assumptions that the rounded reads stay within safe cache/page context. Endian and odd-byte alignment handling are easy to regress. Miscompiled 128-bit arithmetic would affect packet integrity.

Test signals: checksum selftests for all lengths and alignments, odd/even start address cases, IPv6 pseudo-header known vectors, KASAN-enabled tests, big-endian build coverage, and randomized comparison with a simple reference implementation.
