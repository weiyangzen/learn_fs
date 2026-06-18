# sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/mvneta_bm.c

## Purpose
`mvneta_bm.c` implements the platform driver for the Marvell NETA Buffer Manager used by Armada 380-class NETA Ethernet controllers. It owns the BM device lifetime, maps BM registers, enables the clock, allocates the BPPI SRAM window, initializes four hardware buffer-pointer pools, and exposes pool operations to the main `mvneta` network driver through exported GPL symbols. Its role is hardware resource management rather than packet processing: it prepares DMA-backed arrays of buffer pointers and feeds/empties those pools through the BM indirect SRAM access window.

## Important APIs, Types, and Functions
- `mvneta_bm_probe()` / `mvneta_bm_remove()` are the platform-driver entry points for `marvell,armada-380-neta-bm`.
- `mvneta_bm_get()` and `mvneta_bm_put()` let a consumer driver obtain and release the BM controller from a device-tree node-backed platform device.
- `mvneta_bm_pool_use()` validates pool sharing rules, initializes a free pool, creates the hardware pool, and pre-fills it via `hwbm_pool_add()`.
- `mvneta_bm_construct()` is the HWBM allocator callback; it writes the buffer virtual address into the first word, DMA maps the buffer, then releases the physical address to hardware with `mvneta_bm_pool_put_bp()`.
- `mvneta_bm_bufs_free()` drains hardware buffer pointers, unmaps DMA buffers, and returns them to HWBM.
- `mvneta_bm_pool_destroy()` tears down one pool when its port map reaches zero.
- Local register helpers `mvneta_bm_read()`, `mvneta_bm_write()`, `mvneta_bm_config_set()`, and `mvneta_bm_config_clear()` centralize MMIO accesses.

## Control Flow
Probe allocates `struct mvneta_bm`, maps the register resource, enables the clock, allocates BPPI SRAM using the `internal-mem` genpool, then calls `mvneta_bm_init()`. Initialization masks/clears interrupts, tunes the BM burst size, allocates the `bm_pools` array, starts the BM unit, resets read/write pointers, and reads optional per-pool `poolN,capacity` and `poolN,pkt-size` properties. When the Ethernet port later calls `mvneta_bm_pool_use()`, a free pool is configured with packet and fragment sizing, bound to the HWBM pool abstraction, given a coherent BPPE array, assigned MBUS target/attribute metadata, enabled in hardware, and filled with DMA-mapped receive buffers. Removal iterates all pools with an all-ports mask, frees SRAM, stops the BM unit, and disables the clock.

## State and Persistence
Runtime state is held in `struct mvneta_bm` and `struct mvneta_bm_pool`: register base, clock, platform device, genpool allocation, per-pool type, packet size, DMA buffer size, BPPE virtual/DMA addresses, port use map, and HWBM counters. Hardware state persists only while the device is bound: pool base/size/read/write registers, XBAR target attributes, interrupt masks/causes, command state, and config bits. Device-tree properties provide boot-time persistent configuration for pool capacity and optional packet size.

## Dependencies and Integration Points
The file depends on Linux platform-driver, OF, DMA, clock, genalloc, MBUS, netdevice, SKB, and `net/hwbm.h` APIs. It integrates with `mvneta_bm.h` for register definitions and inline BPPI accessors, with the main NETA Ethernet driver through exported BM symbols, with device-tree `internal-mem`, and with `mvebu_mbus_get_dram_win_info()` to program crossbar target attributes for coherent pool memory.

## Risks and Edge Cases
`mvneta_bm_construct()` stores a virtual address in the first four bytes using a `u32` cast, which matches the intended 32-bit platform assumptions but is not portable to arbitrary 64-bit virtual addresses. `mvneta_bm_bufs_free()` works around zero BPPI reads and uses `phys_to_virt()` on DMA addresses, so correctness depends on the platform memory mapping model. Partial `hwbm_pool_add()` failure in `mvneta_bm_pool_use()` returns `NULL` after warning but does not fully unwind the newly created pool. Pool sharing rules are strict: long pools cannot be shared by ports and short pools cannot be mixed with other types. Capacity values are clamped or aligned, but invalid `pool_id` values are not guarded inside `mvneta_bm_pool_use()` and must be validated by callers.

## Test Signals
Useful signals are successful BM probe logs, DT-driven capacity warnings, absence of DMA mapping errors, stable receive traffic using BM-backed pools, clean module/device removal without `cannot free all buffers` warnings, and register-level evidence that BM command/config/pool base/size/read/write registers are programmed. Fault tests should exercise missing `internal-mem`, clock enable failure, illegal pool capacities, DMA mapping failure, pool sharing conflicts, and repeated port open/close cycles.
