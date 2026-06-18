<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/uapi/asm/swab.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/uapi/asm/swab.h

Purpose: Provides x86 optimized byte-swap helpers for 32-bit and 64-bit values using `bswap` assembly.

Important APIs/types/functions: `__arch_swab32()` and `__arch_swab64()`.

Control flow: Inline helpers emit `bswapl`; 64-bit swaps use either two 32-bit swaps plus exchange on i386 or `bswapq` on x86_64.

State and persistence behavior: No state; helpers are pure value transformations.

Dependencies and integration points: Depends on Linux UAPI types and compiler attributes. Integrates with generic byte-swap code, endian conversions, networking/filesystem parsers, and userspace builds including kernel UAPI.

Risks and test signals: Risks include inline assembly constraint errors or wrong i386 half-ordering. Test compile under i386 and x86_64, constant-folding behavior, and known byte-swap vectors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/uapi/asm/swab.h -->
