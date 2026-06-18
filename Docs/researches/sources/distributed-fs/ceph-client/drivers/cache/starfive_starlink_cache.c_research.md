# sources/distributed-fs/ceph-client/drivers/cache/starfive_starlink_cache.c

## Purpose
`starfive_starlink_cache.c` registers StarFive StarLink cache controller operations for RISC-V noncoherent DMA cache maintenance.

## Important APIs, Types, And Functions
The file has a singleton `starlink_cache_base`. `starlink_cache_dma_cache_wback()`, `starlink_cache_dma_cache_invalidate()`, and `starlink_cache_dma_cache_wback_inv()` write controller range registers and command modes. `starlink_cache_flush_complete()` polls for completion. `starlink_cache_init()` performs OF discovery and registration.

## Control Flow
Arch init finds an available `starfive,jh8100-starlink-cache` node, reads and validates `cache-block-size`, maps the controller, sets `riscv_cbom_block_size`, marks noncoherent support, and registers nonstandard cache ops. Each operation writes start and end physical addresses masked to 40 bits, issues a memory barrier, writes the flush control mode, and polls until the enable bit clears.

## State And Persistence
State is global MMIO mapping plus registered RISC-V cache ops. Hardware state is transient per range flush/invalidate commands. There is no explicit unmap or unregister path for this arch init driver.

## Dependencies And Integration Points
The driver depends on OF, 64-bit RISC-V, noncoherent DMA infrastructure, 64-bit MMIO accesses, and a block size that is a multiple of 64 bytes. It integrates directly with the DMA cache maintenance callbacks used by noncoherent devices.

## Risks And Edge Cases
The code writes the mode field without explicitly setting an enable bit; this relies on hardware semantics where the mode write starts the operation. The end address is `paddr + size` rather than an explicitly inclusive endpoint, so it must match the controller contract. Completion timeout is long, five seconds, and only warns on failure. Address masking limits ranges to 40-bit physical addresses.

## Test Signals
Boot on JH8100 hardware, DMA correctness for clean, invalidate, and clean-invalidate paths, unaligned and zero-size ranges, high physical addresses near the 40-bit mask, timeout injection, and validation that the configured cache block size matches DMA expectations.
