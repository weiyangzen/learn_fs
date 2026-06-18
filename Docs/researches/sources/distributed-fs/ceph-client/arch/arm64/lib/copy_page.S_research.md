# sources/distributed-fs/ceph-client/arch/arm64/lib/copy_page.S

Purpose: provides `copy_page`, copying one page from a page-aligned source to a page-aligned destination.

Important APIs/types/functions: `__pi_copy_page`, alias `copy_page`, MOPS `cpypwn/cpymwn/cpyewn`, and the 128-byte pipelined ldp/stnp fallback.

Control flow: the MOPS path copies exactly `PAGE_SIZE` bytes. The fallback preloads 128 bytes, advances source/destination, then loops storing the previous cache-line-sized block while loading the next until the page boundary, finishing with the final preloaded block.

State and persistence: mutates only the destination page contents. No persistent state.

Dependencies/integration: exported to core MM page copy paths; depends on `PAGE_SIZE`, alternatives, CPU MOPS support, and normal cacheable kernel mappings.

Risks: assumes source and destination are page aligned and non-overlapping. Any loop-boundary error corrupts pages. Non-temporal stores (`stnp`) may have microarchitectural performance sensitivity.

Test signals: page-copy selftests, migration/COW page copy validation, multiple page sizes, MOPS vs non-MOPS paths, and KASAN checks for exact page bounds.
