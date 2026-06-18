# sources/distributed-fs/ceph-client/arch/mips/include/asm/octeon/cvmx-bootmem.h

## Purpose
This header declares Octeon's simple boot-time physical memory allocator and named-block ABI. It is used before normal kernel allocators or by CVMX applications to allocate shared, bootloader-described memory regions.

## Important APIs, Types, and Functions
Constants define the ABI-sized name length, named-block count, minimum alignment, descriptor version, and allocation flags (`END_ALLOC`, `NO_LOCKING`). `struct cvmx_bootmem_block_header` stores free-list links in physical memory. `struct cvmx_bootmem_named_block_desc` describes named allocations. `struct cvmx_bootmem_desc` is the global allocator descriptor with endian-specific field order, lock, free-list head, app-data fields, and named-block array metadata.

Declared APIs include `cvmx_bootmem_init`, address-specific and named allocators (`cvmx_bootmem_alloc_address`, `cvmx_bootmem_alloc_named`, `cvmx_bootmem_alloc_named_range`, `cvmx_bootmem_alloc_named_range_once`), named-block free/find helpers, physical allocation helpers (`cvmx_bootmem_phy_alloc`, `cvmx_bootmem_phy_named_block_alloc`, `__cvmx_bootmem_phy_free`), explicit lock/unlock, and `cvmx_bootmem_get_desc`.

## Control Flow
Initialization receives the bootloader-provided descriptor. Allocation scans the free-list for a range satisfying size, address bounds, alignment, and optional end-allocation behavior, then updates the descriptor and free block headers. Named allocation reserves a descriptor entry, prevents duplicate names, and optionally initializes a once-created block. Free is restricted mainly to named-block and initial free-list manipulation.

## State and Persistence Behavior
State is shared in physical memory: the descriptor, free-list headers embedded in free blocks, and named-block descriptors. Named blocks can persist across cooperating applications or kernel subsystems that know their names. The spinlock field protects concurrent access unless callers deliberately use `NO_LOCKING` under external locking.

## Dependencies and Integration Points
It integrates with `cvmx_bootinfo.phy_mem_desc_addr`, early Octeon memory setup, FPA pool allocation, command queue shared state, and other CVMX facilities that allocate named bootmem blocks. The ABI is shared with bootloader code and possibly 32-bit and 64-bit consumers.

## Risks
The structures are ABI-sensitive and referenced by bootloader assembly; changing layout or `CVMX_BOOTMEM_NAME_LEN` breaks compatibility. Freeing with the wrong physical address or size corrupts the free list. Misusing `NO_LOCKING` can race shared allocations. Alignment and address-bound handling must be precise because callers often need DMA-visible or hardware-constrained memory.

## Test Signals
Boot tests should verify descriptor version parsing, early allocations, named block reuse, range-restricted allocations, and lock behavior. Stress signals include repeated named alloc/free, allocation at exact addresses, high-address/end allocations, and no free-list corruption after failed allocations.
