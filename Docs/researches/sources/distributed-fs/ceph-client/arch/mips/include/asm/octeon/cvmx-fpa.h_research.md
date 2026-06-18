# sources/distributed-fs/ceph-client/arch/mips/include/asm/octeon/cvmx-fpa.h

## Purpose
This header provides the runtime API for Octeon's hardware Free Pool Allocator. It exposes pool metadata, enables the FPA, allocates blocks synchronously or asynchronously, frees blocks with or without ordering, and declares pool setup/shutdown helpers.

## Important APIs, Types, and Functions
Constants define 8 pools, 128-byte minimum block size, and 128-byte alignment. `cvmx_fpa_iobdma_data_t` describes async allocation command data. `cvmx_fpa_pool_info_t` records a pool's name, block size, base pointer, and starting element count, with global `cvmx_fpa_pool_info[]`. Inline helpers return pool name/base, test membership, enable FPA, allocate (`cvmx_fpa_alloc`), async allocate (`cvmx_fpa_async_alloc`), free without ordering (`cvmx_fpa_free_nosync`), and free with ordering (`cvmx_fpa_free`). External APIs include pool setup/shutdown and block-size query.

## Control Flow
`cvmx_fpa_enable()` reads status, warns if already enabled, applies pass1 FIFO mark workarounds with a short delay, then writes enable. Allocation reads from an FPA DID address and converts a physical address to a pointer. Async allocation sends an IOBDMA command to write the result to scratchpad. Free converts a pointer to physical, encodes the FPA pool DID into the address, optionally issues `CVMX_SYNCWS`, and writes the cache-line invalidate count to the FPA I/O address.

## State and Persistence Behavior
Pool metadata is software global state. Hardware pool contents and counts live in FPA CSRs/FIFOs and persist until blocks are allocated/freed or the unit is reset. Freeing transfers ownership of a memory block to hardware; callers must not touch it afterward without reallocation.

## Dependencies and Integration Points
It depends on Linux delay, CVMX address conversion and CSR helpers, `cvmx-fpa-defs.h`, Octeon model/pass detection, debug printing, barriers, and IOBDMA send support. It integrates with packet buffers, work queue entries, command queues, DMA descriptors, and bootmem-backed pool creation.

## Risks
Memory ordering is critical: `cvmx_fpa_free_nosync()` is unsafe for buffers modified by the core unless the caller supplied ordering elsewhere. Pool membership has no bounds checking for invalid pool IDs. Passing a bad pointer or wrong pool corrupts hardware free lists. Async scratch addresses must be aligned. Pass1 workaround programming must remain before enabling FPA on affected chips.

## Test Signals
Test pool setup, enable, sync and async allocation, ordered and unordered frees, membership checks, shutdown returning expected block counts, pass1 hardware workaround paths, and packet I/O under FPA pressure with no use-after-free buffer corruption.
