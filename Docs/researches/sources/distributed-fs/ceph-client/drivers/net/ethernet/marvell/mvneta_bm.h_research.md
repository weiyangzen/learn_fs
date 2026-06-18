# sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/mvneta_bm.h

## Purpose
`mvneta_bm.h` is the public and private contract for the Marvell NETA Buffer Manager driver. It defines BM register offsets and bitfields, pool sizing constants, packet-buffer size macros, core BM data structures, exported function declarations, and no-op stubs for builds without `CONFIG_MVNETA_BM`.

## Important APIs, Types, and Definitions
- Register groups cover BM configuration/activation, XBAR target attributes, pool base/read/write/size registers, and interrupt cause/mask registers.
- Constants define four pools, capacity minimum/default/maximum/alignment, 32-byte pool pointer alignment, BPPI SRAM size, and `MVNETA_RX_BUF_SIZE()`.
- `enum mvneta_bm_type` tracks whether a pool is free, long-buffer, or short-buffer.
- `struct mvneta_bm` stores global mapped register/SRAM/clock/platform state and the pool array.
- `struct mvneta_bm_pool` stores HWBM pool metadata, packet and buffer sizes, coherent BPPE allocation, port-use bitmap, and backpointer to the controller.
- Inline accessors `mvneta_bm_pool_put_bp()` and `mvneta_bm_pool_get_bp()` write/read pool-specific BPPI slots.
- The conditional API block exposes real declarations when enabled and stubbed functions otherwise.

## Control Flow
This header does not execute control flow directly, but it shapes how `mvneta_bm.c` and the main NETA driver interact. Consumers call `mvneta_bm_get()` to resolve a BM controller, `mvneta_bm_pool_use()` to attach a port to a pool, `mvneta_bm_pool_put_bp()` to return buffer physical addresses to hardware, `mvneta_bm_pool_get_bp()` to drain them, and destroy/free helpers during teardown. If BM support is disabled, callers can still compile against the same names and receive inert or failure-returning stubs.

## State and Persistence
The structures model all mutable software state for the BM controller and pools. Hardware state is represented by macros rather than stored values, with register persistence limited to device lifetime. The inline BPPI accessors encode the pool ID into an SRAM offset via `pool->id << MVNETA_BM_POOL_ACCESS_OFFS`, so the pool ID must remain stable after initialization.

## Dependencies and Integration Points
The header assumes Linux kernel types including `struct clk`, `struct platform_device`, `struct gen_pool`, `dma_addr_t`, `struct hwbm_pool`, `struct device_node`, and MMIO helpers. It is included by `mvneta_bm.c` and by NETA Ethernet code that optionally uses BM acceleration. It also encodes device-tree-facing sizing behavior indirectly through constants consumed during pool initialization.

## Risks and Edge Cases
The inline BPPI helpers take and return 32-bit values even though `dma_addr_t` may be wider on some architectures, reflecting the original Armada NETA constraints. Stub functions hide disabled-BM behavior at compile time, so call sites must treat `mvneta_bm_pool_use()` returning `NULL` as a normal unsupported path. The header declares `mvneta_bm_pool_refill()`, but this source subset does not contain its implementation, so users must verify the main NETA driver supplies it under the same config assumptions.

## Test Signals
Compile coverage should include both `CONFIG_MVNETA_BM=y/m` and disabled builds to validate real declarations and stubs. Runtime tests should confirm pool IDs map to correct BPPI offsets, register macros match hardware documentation, and pool capacity/alignment constants align with the controller limits used by `mvneta_bm.c`.
