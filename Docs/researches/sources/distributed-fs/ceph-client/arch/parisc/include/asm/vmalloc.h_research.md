<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/asm/vmalloc.h -->
# sources/distributed-fs/ceph-client/arch/parisc/include/asm/vmalloc.h

Source read size: 4 lines, 96 bytes.

Purpose: placeholder architecture vmalloc header for PA-RISC. Important APIs: none defined directly. Control flow: none. State and persistence: none. Dependencies and integration points: satisfies generic includes that expect `asm/vmalloc.h`; actual vmap/vmalloc cache coherency lives in `kernel/cache.c`. Risks: future additions must coordinate with PA-RISC cache/TLB flushing semantics. Test signals: build coverage and vmalloc/vmap/ioremap cache flush tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/asm/vmalloc.h -->
