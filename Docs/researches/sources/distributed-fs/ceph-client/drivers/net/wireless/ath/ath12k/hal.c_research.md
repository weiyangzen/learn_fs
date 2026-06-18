# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/hal.c

## Purpose

`hal.c` implements generic ath12k hardware abstraction helpers around SRNG rings, CE descriptors, REO/WBM setup hooks, buffer address encoding, shadow register configuration, and TLV header encode/decode. Hardware-specific behavior is delegated through `ab->hal.ops`; this file provides common state management and ring pointer mechanics.

## Important APIs, Types, and Functions

Thin ops wrappers cover CE descriptor size/setup, DSCP/TID maps, TCL bank configuration, REO queue LUT programming, REO hardware setup, idle link list setup, RX buffer address set/get, RX MSDU list extraction, REO entry buffer address extraction, current-channel config, and idle link RBM selection.

SRNG APIs include `ath12k_hal_srng_get_entrysize()`, `ath12k_hal_srng_get_max_entries()`, `ath12k_hal_srng_get_params()`, `ath12k_hal_srng_get_hp_addr()`, `ath12k_hal_srng_get_tp_addr()`, peek/get/reap helpers for source and destination rings, `ath12k_hal_srng_src_num_free()`, `ath12k_hal_srng_dst_num_free()`, `ath12k_hal_srng_access_begin()`, `ath12k_hal_srng_access_end()`, `ath12k_hal_srng_setup()`, `ath12k_hal_srng_init()`, and `ath12k_hal_srng_deinit()`.

Debug/config helpers include `ath12k_hal_srng_shadow_config()`, `ath12k_hal_srng_get_shadow_config()`, `ath12k_hal_srng_shadow_update_hp_tp()`, `ath12k_hal_dump_srng_stats()`, and TLV helpers `ath12k_hal_encode_tlv64_hdr()`, `ath12k_hal_encode_tlv32_hdr()`, `ath12k_hal_decode_tlv64_hdr()`, and `ath12k_hal_decode_tlv32_hdr()`.

## Control Flow

HAL initialization calls the hardware op to create the SRNG config table, stores the device pointer, allocates coherent remote-data-pointer (`rdp`) and write-pointer (`wrp`) arrays, and registers lockdep classes for every SRNG. Deinit unregisters lock keys, frees coherent pointer memory, and frees the config table.

SRNG setup resolves a ring ID from type/ring/mac ID, fills `hal->srng_list[ring_id]`, clears ring memory, initializes source or destination software pointers, assigns pointer addresses in `rdp`/`wrp` memory, flags LMAC rings when pointer updates go through firmware-shared memory, initializes UMAC hardware rings through ops, and applies CE destination setup for CE DST rings.

Ring access is bracketed. `ath12k_hal_srng_access_begin()` syncs cached tail/head pointers from hardware/shared memory and uses `dma_rmb()` before reading new destination descriptors. Callers then use src/dst get/peek helpers, which mutate software HP/TP offsets modulo `ring_size`. `ath12k_hal_srng_access_end()` writes updated HP/TP either to shared memory for LMAC rings or through `ath12k_hif_write32()` for UMAC/MMIO rings, with memory barriers before publishing descriptor ownership.

Shadow config walks non-CE, non-DMAC/PMAC ring types and asks hardware ops to configure shadow registers. Stats dump prints CE interrupt ages, external IRQ group ages, and current/cached/last ring pointers for initialized rings.

## State and Persistence Behavior

Persistent HAL state lives in `struct ath12k_hal`: SRNG list entries, SRNG config table, coherent RDP/WRP memory, device pointer, hardware ops, register table, HAL params, shadow register config, descriptor sizes, and TCL-to-WBM maps. Each `hal_srng` tracks ring identity, physical/virtual base, entry sizes, interrupt settings, MSI data, pointer addresses, cached pointers, last pointers, timestamp, and spinlock.

Ring pointer updates are shared state with hardware/firmware. The memory barriers in access begin/end are part of the ownership protocol and must be preserved when optimizing.

## Dependencies and Integration Points

The file depends on `hif.h` for MMIO writes, hardware-specific `hal_ops`, Linux DMA coherent allocation, lockdep, jiffies, ath12k CE state, external IRQ groups, and all datapath users that post/reap SRNG descriptors (`dp_rx.c`, TX datapath, CE transport, HTT/REO command paths).

## Risks and Edge Cases

- Source ring helpers keep one entry empty to distinguish full from empty; callers must use `ath12k_hal_srng_src_num_free()` rather than raw entry counts.
- Many helpers assume `srng->lock` is held and rely on lockdep assertions. Missing locks can corrupt HP/TP state.
- Modulo arithmetic is used for all rings because some descriptor sizes make ring size non-power-of-two; attempts to optimize must preserve non-power-of-two correctness.
- `ath12k_hal_srng_setup()` indexes LMAC pointer arrays by subtracting `HAL_SRNG_RING_ID_DMAC_CMN_ID_START`; invalid hardware ring IDs would corrupt pointer setup.
- `ath12k_hal_srng_shadow_update_hp_tp()` only updates source rings when non-empty; callers relying on shadow state for empty rings need to understand that behavior.
- TLV encode helpers use `HAL_TLV_HDR_*` masks for both 32-bit and 64-bit paths in `hal.c`; definitions exist separately in the header, so mask consistency matters.

## Test Signals

Useful validation includes ring setup for every `hal_ring_type`, CE send/receive, RX/TX data traffic, monitor rings, shadow register configuration, ring full/empty wraparound tests with non-power-of-two sizes, DMA barrier stress on weakly ordered architectures, lockdep coverage, and SRNG stats dumps during simulated interrupt stalls.
