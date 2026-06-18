# sources/distributed-fs/ceph-client/drivers/cache/ax45mp_cache.c

## Purpose
`ax45mp_cache.c` registers software cache-management operations for Andes AX45MP systems that need nonstandard cache maintenance for noncoherent DMA.

## Important APIs, Types, And Functions
`struct ax45mp_priv` stores the L2 controller MMIO base and cache line size. `ax45mp_cpu_cache_operation()` performs per-line L1 CSR and L2 MMIO operations. `ax45mp_dma_cache_inv()`, `ax45mp_dma_cache_wback()`, and `ax45mp_dma_cache_wback_inv()` implement `struct riscv_nonstd_cache_ops`. `ax45mp_cache_init()` is an `early_initcall`.

## Control Flow
Early init finds an `andestech,ax45mp-cache` node, skips unavailable hardware, maps the L2 controller resource, validates `cache-line-size`, and registers nonstandard RISC-V cache ops if `riscv_cbom_block_size` indicates software handling is needed. Each DMA op converts the physical address to a virtual address, aligns the range to the line size, disables local interrupts, walks cache lines, issues L1 CCTL CSRs, writes physical line addresses and commands to per-hart L2 registers, and busy-waits for the per-hart status bits to become idle.

## State And Persistence
State is global and singleton: the mapped L2 base, expected 64-byte line size, and registered RISC-V cache ops. There is no unregistration path because this is early platform setup.

## Dependencies And Integration Points
The driver depends on OF address translation, Andes-specific CCTL CSRs, L2 controller register layout, `phys_to_virt()` reachability, `smp_processor_id()`, and `riscv_noncoherent_register_cache_ops()`.

## Risks And Edge Cases
The busy-wait loop has no timeout. Operations assume hart IDs map directly to L2 per-core register slots. Interrupts are disabled during potentially large range walks, which can affect latency. `wback_inv` is implemented as writeback then invalidate, doubling walk cost. If `cache-line-size` differs from 64 bytes, init fails rather than adapting.

## Test Signals
Boot on AX45MP with and without IOCP/CBOM support, DMA correctness tests for unaligned buffers, stress large DMA ranges, CPU hotplug or SMP hart-id coverage, and instrumentation for stuck L2 status bits.
