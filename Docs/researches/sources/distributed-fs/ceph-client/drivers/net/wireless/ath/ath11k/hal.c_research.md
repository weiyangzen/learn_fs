# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath11k/hal.c

## Purpose

`hal.c` implements ath11k hardware abstraction for SRNG ring configuration, ring pointer access, CE descriptor helpers, WBM idle link setup, shadow register configuration, and SRNG lifecycle diagnostics. It is the low-level layer that maps datapath ring types to hardware ring ids/registers and provides safe producer/consumer operations for source and destination rings.

## Important APIs, Types, and Functions

- `hw_srng_config_template[]` describes all supported ring classes: REO destination/exception/reinject/cmd/status, TCL data/cmd/status, CE source/destination/status, WBM idle/release, RXDMA buffer/destination/monitor rings, and direct RXDMA buffer rings. Each entry defines start ring id, maximum ring count, descriptor entry size in dwords, LMAC ownership, direction, and max register size.
- `ath11k_hal_srng_init()` allocates per-ring configuration, coherent read/write pointer memory (`rdp` and `wrp`), and lockdep classes.
- `ath11k_hal_srng_deinit()` unregisters lock classes, frees coherent pointer memory, and frees copied SRNG config.
- `ath11k_hal_srng_setup()` initializes one `hal_srng`, maps ring type/number/mac id to a ring id, assigns ring memory, pointer addresses, flags, thresholds, and hardware registers, then programs hardware for non-LMAC rings.
- `ath11k_hal_srng_access_begin()` and `ath11k_hal_srng_access_end()` synchronize cached HP/TP state with hardware/FW-visible pointers and enforce DMA barriers.
- Ring entry APIs include `ath11k_hal_srng_src_get_next_entry()`, `ath11k_hal_srng_dst_get_next_entry()`, `ath11k_hal_srng_src_num_free()`, `ath11k_hal_srng_dst_num_free()`, source reap helpers, and peek helpers.
- CE helpers `ath11k_hal_ce_src_set_desc()`, `ath11k_hal_ce_dst_set_desc()`, `ath11k_hal_ce_dst_status_get_length()`, and `ath11k_hal_ce_get_desc_size()` encode/copy CE descriptors.
- `ath11k_hal_set_link_desc_addr()` writes link descriptor address/cookie fields.
- `ath11k_hal_setup_link_idle_list()` programs the WBM idle link scatter list and ring pointers.
- Shadow register APIs configure and expose shadow HP/TP registers when supported.
- `ath11k_hal_dump_srng_stats()` emits CE, IRQ group, and per-SRNG pointer/timestamp diagnostics.

## Control Flow

Initialization starts with `ath11k_hal_srng_init()`, which clears the HAL object, copies the static ring template, fills hardware-specific register base/stride values in `ath11k_hal_srng_create_config()`, allocates coherent pointer arrays for read pointers and write pointers, and registers one lockdep key per possible ring id. Higher-level datapath code then allocates ring memory and calls `ath11k_hal_srng_setup()` for each ring it needs.

`ath11k_hal_srng_setup()` validates the ring number, computes ring id with LMAC offset if needed, initializes the `hal_srng` object, zeros ring memory, applies endian swap flags on big-endian builds, and assigns source or destination pointer fields. Source rings track software head pointer and hardware/FW tail pointer; destination rings track software tail pointer and hardware/FW head pointer. LMAC rings use coherent shared pointer arrays and set `HAL_SRNG_FLAGS_LMAC_RING`; non-LMAC rings use MMIO or shadow-register addresses and are immediately programmed by `ath11k_hal_srng_hw_init()`.

Hardware programming is split by direction. Destination rings write MSI config if enabled, base address, size, ring id/entry size, interrupt thresholds, HP address, initial HP/TP, swap flags, and enable bit. Source rings similarly program MSI, base address/size, entry size, consumer interrupt thresholds, low threshold, TP address, initial HP/TP, loop-count-disable, swap flags, and enable bit.

Runtime users must hold `srng->lock`, call `ath11k_hal_srng_access_begin()`, consume or produce entries, then call `ath11k_hal_srng_access_end()`. Begin refreshes cached hardware pointers and prefetches cached destination descriptors. End publishes software pointer updates either through shared LMAC memory or MMIO writes and records `srng->timestamp` for diagnostics.

Shadow-register flow is optional. `ath11k_hal_srng_shadow_config()` iterates non-CE, non-LMAC rings and assigns target HP/TP registers to limited shadow slots. `ath11k_hal_srng_update_shadow_config()` records target register addresses and rewires the SRNG HP/TP pointer address to the shadow register memory window.

## State and Persistence Behavior

State is entirely runtime memory and hardware register state. `ab->hal.srng_config` is a kmemdup of the template with hardware-specific register addresses. `ab->hal.srng_list[]` stores each live ring's pointer offsets, ring memory, direction, flags, cached HP/TP values, thresholds, MSI data, and last access timestamp. `hal->rdp` and `hal->wrp` are coherent DMA allocations used for FW/HW-visible ring pointers. Shadow register configuration is held in `hal->shadow_reg_addr[]` and `hal->num_shadow_reg_configured`.

No on-disk persistence exists. Hardware-visible state persists only until device reset/deinit. `ath11k_hal_srng_clear()` clears SRNG and shadow bookkeeping without freeing the coherent pointer arrays.

## Dependencies and Integration Points

This file depends on Linux DMA coherent allocation, hif MMIO read/write accessors, HAL descriptor definitions, hardware parameter macros, lockdep, and CE/IRQ state from ath11k core. It is used by datapath TX/RX (`dp_tx.c`, `dp_rx.c`), CE transport, WBM link descriptor setup, HTT ring setup, interrupt diagnostics, and reset/recovery paths.

## Risks and Edge Cases

- Ring pointer barriers are correctness-critical. Source descriptors must be visible before HP updates; destination descriptors must be read before TP updates. Barrier regressions can cause hardware to read stale descriptors or software to process stale DMA data.
- LMAC, non-LMAC MMIO, and shadow-register pointer paths differ. A wrong `supports_shadow_regs` or LMAC flag can publish HP/TP updates to the wrong address.
- Ring sizes are tracked in dwords, while several external APIs use bytes. Entry-size conversion mistakes can corrupt ring strides or HTT setup values.
- `ath11k_hal_srng_src_get_next_entry()` uses modulo because not all ring sizes are powers of two; changing this casually can break non-power-of-two descriptor rings.
- Shadow configuration has a fixed `HAL_SHADOW_NUM_REGS` limit; exceeding it returns `-EINVAL`, and callers must tolerate unavailable shadow slots.
- CE destination setup writes max-buffer length after generic SRNG setup; ring type ordering matters.
- `ath11k_hal_setup_link_idle_list()` programs several WBM scatter registers and assumes valid scatter buffers/counts supplied by caller.

## Test Signals

Strong signals include boot-time SRNG setup across all supported hardware variants, TX/RX traffic through TCL/REO/RXDMA rings, CE transport activity, monitor ring operation, big-endian build coverage, shadow-register capable and non-shadow hardware tests, lockdep runs ensuring SRNG locks are held, ring full/empty boundary tests, reset/deinit/reinit cycles, and `ath11k_hal_dump_srng_stats()` output that shows moving HP/TP timestamps under traffic.
