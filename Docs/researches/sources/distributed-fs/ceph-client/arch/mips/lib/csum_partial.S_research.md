# sources/distributed-fs/ceph-client/arch/mips/lib/csum_partial.S

Purpose: implements optimized MIPS IP checksum and checksum-copy routines, including user/kernel copy variants.

Important APIs/functions: exports `csum_partial`, `__csum_partial_copy_nocheck`, `__csum_partial_copy_to_user`, and `__csum_partial_copy_from_user`. Core macros include `ADDC`, `ADDC32`, `CSUM_BIGCHUNK`, and `__BUILD_CSUM_PARTIAL_COPY_USER`.

Control flow: `csum_partial` aligns the source, processes large 128/64/32-byte chunks with carry accumulation, handles tail bytes with endian-aware shifts, folds 64-bit sums when needed, handles odd starting alignment, then adds the incoming partial checksum. Copy variants combine aligned/unaligned copy loops with checksum accumulation and exception-table fixups for user/EVA accesses.

State and persistence: stateless except writes to destination buffers and exception fixup return values.

Dependencies and integration: used by networking checksums and copy/checksum helpers; depends on MIPS ABI register conventions, EVA support, exception tables, endian macros, and exported kernel checksum ABI.

Risks: assembly is sensitive to alignment, endianness, 32/64-bit mode, CPU errata workarounds, exception fixups, and carry propagation. Any incorrect tail handling corrupts network checksums.

Test signals: network stack checksum tests, ping/TCP/UDP data integrity, usercopy fault injection, EVA build/run coverage, and big/little endian builds.
