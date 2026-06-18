# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/book3s/32/mmu-hash.h

Purpose: defines 32-bit Book3S hash MMU constants, BAT encoding helpers, segment register fields, hash PTE layout, context representation, and user segment update helpers.

Important APIs/types/functions: macros include BAT block sizes, `BPP_*`, `BAT_PHYS_ADDR`, `PHYS_BAT_ADDR`, `PP_*`, `SR_NX`, `SR_KP`, `SR_KS`, `CTX_TO_VSID`, `mmu_virtual_psize`, and `mmu_linear_psize`. Types include `struct ppc_bat`, `struct hash_pte`, and `mm_context_t`. Functions/macros include assembly `update_user_segments_by_4`, C `update_user_segment()`, `update_user_segments()`, `find_free_bat()`, `bat_block_size()`, and `update_bats()`.

Control flow: assembler macros conditionally program segment registers for configured user segments and optionally issue `isync` on hash-table cores. C helpers update each segment register up to `TASK_SIZE`, masking and skewing the VSID value.

State and persistence: state is hardware BATs, segment registers, hash table entries, and `mm_context_t` context IDs. Updates persist until context switch, MMU reprogramming, or reset.

Dependencies and integration points: depends on asm offsets, `reg.h`, task size definitions, MMU feature patching, and low-level hash fault/flush assembly.

Risks: `CTX_TO_VSID` must remain synchronized with hash functions. Segment-update ordering and `isync` are CPU-sensitive. BAT physical address bit packing differs for 64-bit physical address support.

Test signals: boot 6xx/7xx/604/603-style targets, switch processes over varied `TASK_SIZE`, exercise BAT mappings, and run TLB/hash fault tests with and without extended physical addresses.
