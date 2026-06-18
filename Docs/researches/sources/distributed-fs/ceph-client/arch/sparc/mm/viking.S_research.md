# sources/distributed-fs/ceph-client/arch/sparc/mm/viking.S

Purpose: implements TI Viking and Viking/MXCC cache/TLB operations for SPARC32 SRMMU systems, including sun4d SMP TLB-flush serialization.

Important APIs/functions: exports `viking_flush_cache_all()`, `viking_flush_cache_mm()`, `viking_flush_cache_range()`, `viking_flush_cache_page()`, `viking_flush_page()`, `viking_mxcc_flush_page()`, `viking_flush_page_for_dma()`, `viking_flush_page_to_ram()`, `viking_flush_sig_insns()`, `viking_flush_tlb_all()`, `viking_flush_tlb_mm()`, `viking_flush_tlb_range()`, `viking_flush_tlb_page()`, and SMP `sun4dsmp_flush_tlb_*()` variants.

Control flow: cache flushes mostly flush register windows and rely on broad behavior selected by `srmmu.c`. `viking_flush_page()` scans D-cache tags by set/block to evict a matching physical page; MXCC uses stream registers to flush cache streams. TLB functions switch to the target context, demap all/mm/range/page, then restore the previous context. sun4d SMP wrappers serialize the same operations with an `ldstub` spin byte to avoid XBUS broadcast FIFO overflow.

State and persistence: only hardware cache/TLB state and the SMP spin byte are mutated. No filesystem or long-lived allocation state exists.

Dependencies and integration points: selected by `init_viking()` and the sun4d SMP op table in `srmmu.c`; depends on MXCC ASIs, Viking register definitions, SRMMU context registers, and VMA/mm offset constants.

Risks: page cache flush tag comparisons must match physical tag encoding. Context restore after flush is mandatory. sun4d serialization is a hardware workaround; removing it risks lost broadcast invalidations and memory corruption.

Test signals: run Viking with and without MXCC, sun4d SMP TLB shootdown stress, DMA tests on old Viking, page-color alias workloads, mprotect/munmap range invalidations, and fork/exec with many active contexts.
