<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/set_memory.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/set_memory.h

Purpose: declares x86 page attribute and memory encryption transition APIs. Important APIs include `set_memory_uc/wc/wb/wp/ro/rw/x/nx()`, array variants, encrypted/decrypted/private/shared transitions, direct-map invalidation/restoration, cache flushing helpers, and CPA initialization functions.

Control flow: callers request attribute changes over page ranges; implementation updates page tables, flushes caches/TLBs as needed, and may alter direct-map aliases. Confidential computing paths call private/shared helpers for SEV-SNP or TDX state transitions.

State and persistence: mutates kernel page tables, direct-map aliases, and encryption/share state; changes persist until reversed or memory is freed. Dependencies include page tables, cache/TLB flushing, CPA code, AMD/Intel confidential-computing backends, and module/text permission management.

Risks: attribute aliasing, missing TLB/cache flushes, W+X exposure, incorrect shared/private conversion, and direct-map inconsistencies. Test signals include rodata/text permission tests, module load/unload, ioremap/cache attribute tests, SEV/TDX shared memory transitions, and debug page-table checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/set_memory.h -->
