# sources/distributed-fs/ceph-client/arch/x86/coco/core.c

Purpose: centralizes x86 confidential-computing vendor state, platform attribute queries, page-table encryption-bit transformations, attribute flags, and early RNG seeding for encrypted guests.

Important APIs and state: defines `cc_vendor`, `cc_mask`, static `cc_flags`, and exports `cc_platform_has()` and `cc_mkdec()`. Also provides `cc_mkenc()`, `cc_platform_clear()`, `cc_platform_set()`, and `cc_random_init()`. PIC aliases expose `cc_vendor` and `cc_mask` to position-independent startup code.

Control flow: `cc_platform_has()` dispatches to AMD or Intel implementations. Intel reports memory encryption and string-I/O unroll needs. AMD handles vTOM separately, SME host encryption, SEV guest memory/state encryption, string-I/O unroll without SEV-ES, SNP, secure TSC, host SNP flag, and secure AVIC. `cc_mkenc()`/`cc_mkdec()` set or clear `cc_mask` according to AMD C-bit, AMD vTOM, or Intel semantics. `cc_random_init()` seeds kernel randomness with RDRAND for encrypted guests and panics if no random longs are available.

Dependencies and integration: used across x86 memory management, SEV/TDX setup, page-table creation, and random initialization. Depends on `sev_status`, `sme_me_mask`, arch random, and cc_platform attribute enums.

Risks and test signals: encryption-bit polarity differs by vendor and vTOM, so wrong mask logic exposes or corrupts memory. RDRAND failure is fatal in encrypted guests by design. Test AMD SME, SEV, SEV-ES, SNP C-bit, SNP vTOM, Intel TDX, host SNP flag set/clear, `cc_mkenc/cc_mkdec` page-table values, and RDRAND failure handling.
