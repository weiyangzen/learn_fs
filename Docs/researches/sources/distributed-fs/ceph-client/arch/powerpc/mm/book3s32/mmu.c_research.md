<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/mm/book3s32/mmu.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/mm/book3s32/mmu.c

## Purpose
This file initializes and manages Book3S32 block address translations and hash table setup.

## Important APIs, types, and functions
Key APIs include `v_block_mapped`, `p_block_mapped`, `find_free_bat`, `bat_block_size`, `mmu_mapin_ram`, `mmu_mark_initmem_nx`, `mmu_mark_rodata_ro`, `setbat`, `__update_mmu_cache`, `MMU_init_hw`, `MMU_init_hw_patch`, `setup_initial_memory_limit`, and `print_system_hash_info`. Important state includes `early_hash`, `Hash`, `Hash_size`, `Hash_mask`, `_SDR1`, `BATS`, `bat_addrs`, and `mmu_hash_lock`.

## Control flow
Boot starts with an early hash table, maps kernel RAM with BATs where possible, later allocates a suitably sized hash table from memblock, computes SDR1/hash masks, and patches low-level assembly hash helpers with actual table base/mask values. Runtime page-fault completion calls `__update_mmu_cache`, which preloads HPTEs only for young user PTEs following instruction/data storage faults.

## State and persistence behavior
It persists BAT register images, BAT range metadata, SDR1/hash metadata, and assembly patch constants. It also changes segment NX bits and BAT permissions for strict RWX/RODATA transitions.

## Dependencies and integration points
Integrated with memblock, machine progress callbacks, text patching, `hash_low.S`, TLB/cache behavior, strict kernel RWX, debug pagealloc/KFENCE, and execmem module ranges.

## Risks and edge cases
BAT block sizing must honor alignment and 128 KiB minimum. Strict RWX mapping can leave some RW data executable if BAT granularity is too coarse. Hash table patching must happen after no KASAN instrumentation can be triggered.

## Test signals
Boot logs for hash size, stable early boot mapping, successful page faults/hash preloads, strict RWX behavior, and correct block mapping lookups.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/mm/book3s32/mmu.c -->
