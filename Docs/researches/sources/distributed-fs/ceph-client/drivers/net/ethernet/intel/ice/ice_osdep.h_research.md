# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_osdep.h

## Purpose
`ice_osdep.h` provides the Linux OS adaptation layer used by the ICE shared code. It centralizes kernel includes, MMIO register access macros, polling, flush behavior, DMA memory representation, and debug/hex-dump wrappers.

## Important APIs, Types, and Functions
- MMIO macros: `wr32()`, `rd32()`, `wr64()`, and `rd64()` access registers relative to `struct ice_hw::hw_addr`.
- Polling and flush: `rd32_poll_timeout()` wraps `read_poll_timeout()`, and `ice_flush()` reads `GLGEN_STAT`.
- `ICE_M()` builds shifted unsigned masks from a mask and shift.
- `struct ice_dma_mem` stores virtual address, DMA address, and allocation size.
- `ice_hw_to_dev()` maps ICE hardware state to a Linux `struct device`.
- Debug macros: `ice_debug()`, `_ice_debug_array()`, `ice_debug_array()`, and `ice_debug_array_w_prefix()`.

## Control Flow
Shared ICE code uses these macros directly rather than calling Linux APIs everywhere. Register reads/writes inline to `readl`/`writel` and `readq`/`writeq`. Debug output either maps to `dev_dbg()` under dynamic debug, to `dev_info()` gated by `hw->debug_mask`, or to hex dump helpers depending on `CONFIG_DYNAMIC_DEBUG` and `DEBUG`.

## State and Persistence
The file itself has no storage. Its MMIO macros read and write persistent hardware register state, while debug behavior depends on `hw->debug_mask` and kernel config. `ice_flush()` causes an MMIO read used to flush posted writes.

## Dependencies and Integration Points
It depends on Linux kernel headers for types, IO, bitops, ethtool, ethernet, polling, PCI IDs, and UDP tunnel support. It is pulled into ICE common code and underpins nearly every hardware-facing source file in the driver.

## Risks
Register macros assume a valid mapped `hw_addr`; misuse before mapping or after teardown can fault. `wr64()`/`rd64()` require the non-atomic lo-hi compatibility include on non-64-bit configs. Debug array formatting in the non-DEBUG fallback manually loops over lengths and depends on `u16 len_l`, so callers should avoid unexpectedly large debug buffers.

## Test Signals
Build coverage across `CONFIG_DYNAMIC_DEBUG`, `DEBUG`, 32-bit, and 64-bit configurations is important. Runtime smoke tests should include register reads/writes through common initialization paths and debug-mask toggling to ensure logs remain bounded and readable.
