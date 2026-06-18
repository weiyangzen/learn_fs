# sources/distributed-fs/ceph-client/arch/xtensa/lib/checksum.S

Purpose: Provides optimized IP/TCP/UDP checksum routines for Xtensa.

Important APIs, types, and functions: `csum_partial()`, `csum_partial_copy_generic()`, `ONES_ADD`, exception table `EX()` annotations, `.fixup` handler returning zero, and exported symbols.

Control flow: `csum_partial()` handles 4-byte aligned, 2-byte aligned, and odd-address buffers with chunked loops and one's-complement carry folding. `csum_partial_copy_generic()` copies while accumulating checksum, selecting fast 4-byte aligned path, 2-byte path, or byte path, and uses exception fixups for faulting loads/stores.

State and persistence: Reads source buffers, writes destination in copy variant, and returns accumulated checksum. On exception in copy variant, returns zero from fixup rather than partial state.

Dependencies and integration: Used by networking checksum paths and user/kernel copy checksum operations; depends on Xtensa alignment behavior, loop-option macros, endian-specific byte placement, and exception table machinery.

Risks: `csum_partial()` documents that 1-byte alignment is very slow and certain alignments are expected; checksum correctness is endian-sensitive; fault fixup behavior must match callers' error expectations.

Test signals: Network checksum self-tests, packet transmit/receive under TCP/UDP, odd/2/4-byte aligned buffers, fault injection for copy source/destination, and big-endian builds.
