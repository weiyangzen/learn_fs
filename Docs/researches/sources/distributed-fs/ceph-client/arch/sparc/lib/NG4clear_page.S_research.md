# sources/distributed-fs/ceph-client/arch/sparc/lib/NG4clear_page.S

Purpose: Niagara4 optimized page clear implementation.

Important APIs/functions: Defines `NG4clear_page` and `NG4clear_user_page`.

Control flow: Iterates over `PAGE_SIZE`, using `stxa` with `ASI_ST_BLKINIT_MRU_P` to zero cacheline-sized/page chunks efficiently. `clear_user_page` aliases the same implementation while accepting an unused virtual-address argument.

State and persistence: No persistent state; writes zeros to the destination page.

Dependencies/integration: Includes `asm/asi.h` and `asm/page.h`; patched into `_clear_page` and `clear_user_page` by `NG4patch.S`.

Risks/test signals: Store ASI choice and page loop count are critical. Test full-page zeroing, page alignment, cache coherency, and patch activation on NG4 hardware.
