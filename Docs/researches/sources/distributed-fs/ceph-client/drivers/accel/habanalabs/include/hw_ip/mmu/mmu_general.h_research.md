## sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/hw_ip/mmu/mmu_general.h

### Purpose
`mmu_general.h` defines shared HabanaLabs MMU page sizes, PTE flag masks, hop counts, hop table geometry, and common hop-number identifiers.

### Important APIs, Types, And Functions
It exports page shift/size macros from 4 KiB through 1 GiB, PTE flag masks (`PAGE_PRESENT_MASK`, `SWAP_OUT_MASK`, `LAST_MASK`, `FLAGS_MASK`), hop architecture constants from 3 to 6 hops, `HOP_PHYS_ADDR_MASK`, `HL_PTE_SIZE`, 512-entry hop table sizing, HOP0 physical-address register shifts, `MMU_CONFIG_TIMEOUT_USEC`, and `enum mmu_hop_num`.

### Control Flow
No executable flow exists. MMU code uses these constants to allocate page tables, encode/decode PTEs, walk address hops, program HOP0 roots, and poll MMU configuration completion.

### State, Persistence, And Dependencies
Persistent state is hardware page table memory and MMU configuration registers built using these masks. The header assumes `u64`, `_BITUL`, and `MAX_ASID` are available from surrounding driver headers.

### Integration Points
The file is shared by MMU implementations for multiple HabanaLabs ASIC generations and underpins virtual-memory mapping, ASID setup, page-table allocation, and PTE flag handling.

### Risks
Mask and size errors corrupt address translation. `HOP0_512_PTE_TABLES_TOTAL_SIZE` depends on `MAX_ASID`; mismatches can underallocate root tables. Flag masking must stay consistent with hardware-defined low PTE bits.

### Test Signals
Tests should cover PTE encoding/decoding, hop table allocation sizes, ASID root programming, page sizes at each supported granularity, and timeout behavior when MMU config busy bits do not clear.
