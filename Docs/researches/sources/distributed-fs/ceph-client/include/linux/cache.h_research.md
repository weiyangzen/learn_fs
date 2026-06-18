## sources/distributed-fs/ceph-client/include/linux/cache.h

**Purpose:** This header defines cacheline alignment, placement, and structure-layout helpers used for performance and false-sharing control.

**Important APIs/types/functions:** It provides `L1_CACHE_ALIGN`, `SMP_CACHE_ALIGN`, `LARGEST_ALIGN`, `__read_mostly`, `__ro_after_init`, `__cacheline_aligned`, `__cacheline_aligned_in_smp`, internode alignment helpers, `cache_line_size()`, cacheline group markers, `CACHELINE_ASSERT_GROUP_MEMBER`, `CACHELINE_ASSERT_GROUP_SIZE`, `CACHELINE_PADDING`, and `ARCH_DMA_MINALIGN` fallback.

**Control flow, state, persistence:** No runtime control flow except optional `cache_line_size()` macro/function. The helpers affect linker sections, alignment, and struct padding, which changes object placement and memory layout.

**Dependencies/integration:** Includes UAPI alignment helpers, VDSO cache data, and architecture cache definitions. Used broadly by hot-path networking, scheduler, MM, block, and driver data structures.

**Risks and test signals:** Risks are ABI/layout changes, excessive padding, false sharing from missing alignment, and misuse of `__read_mostly` without performance justification. Test signals include pahole/layout checks, cacheline group build assertions, perf false-sharing traces, and DMA alignment tests.
