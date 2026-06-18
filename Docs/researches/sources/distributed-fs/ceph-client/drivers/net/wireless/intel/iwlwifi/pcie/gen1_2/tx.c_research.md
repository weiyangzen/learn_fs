# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/pcie/gen1_2/tx.c

## Purpose
This file implements the legacy/gen1 PCIe transmit path for iwlwifi transport, with some shared dispatch to gen2 helpers. It owns TX DMA queue allocation, TFD construction/unmapping, scheduler byte-count table updates, host command enqueue/completion, data-frame DMA mapping, reclaim, queue stop/start, and watchdog handling.

## Important APIs, Types, and Functions
- `iwl_pcie_alloc_dma_ptr()` and `iwl_pcie_free_dma_ptr()` allocate/free coherent DMA blocks used by keep-warm and scheduler byte-count tables.
- `iwl_pcie_txq_alloc()`, `iwl_txq_init()`, `iwl_pcie_tx_init()`, `iwl_pcie_tx_start()`, `iwl_pcie_tx_stop()`, and `iwl_pcie_tx_free()` form the TX lifecycle.
- `iwl_pcie_enqueue_hcmd()`, `iwl_pcie_hcmd_complete()`, and `iwl_trans_pcie_send_hcmd()` implement host command submission, synchronous wait, response ownership, and async command validation.
- `iwl_trans_pcie_tx()` maps mac80211 data SKBs and `iwl_device_tx_cmd` payloads into transfer buffer descriptors.
- `iwl_pcie_reclaim()` frees completed non-command TX entries, returns SKBs to the caller, drains overflow queues, and wakes stopped queues.
- `iwl_trans_pcie_txq_enable()`, `iwl_trans_pcie_txq_disable()`, `iwl_pcie_set_q_ptrs()`, and `iwl_pcie_freeze_txq_timer()` expose queue control to higher transport/op-mode layers.
- TSO/A-MSDU support is handled by `iwl_pcie_get_page_hdr()`, `iwl_pcie_prep_tso()`, `iwl_pcie_get_sgt_tb_phys()`, and `iwl_fill_data_tbs_amsdu()` when `CONFIG_INET` is enabled.

## Control Flow
Initialization allocates per-queue coherent TFD rings and first-TB buffers, coherent scheduler byte-count tables, command buffers, and a keep-warm buffer. `iwl_pcie_tx_init()` points FH registers at those rings, disables TX FIFOs during setup, and initializes queue locks, indexes, and watermarks. `iwl_pcie_tx_start()` clears SCD context memory, programs the SCD DRAM base, enables the command queue and FIFO channels, enables FH TX DMA channels, and applies device-family workarounds.

For host commands, `iwl_trans_pcie_send_hcmd()` rejects dead/RFKILL-incompatible commands, routes async commands directly to enqueue, and serializes sync commands with `STATUS_SYNC_HCMD_ACTIVE`. `iwl_pcie_enqueue_hcmd()` chooses narrow or wide headers, splits copy/NOCOPY/DUP buffers into TFD TBs, maps DMA, optionally blocks data TXQ write-pointer updates, updates the command queue write pointer, and wakes/holds the NIC when needed. Completion unmaps the TFD, steals response pages for `CMD_WANT_SKB`, unblocks data queues, reclaims the command slot, clears sync status, and wakes waiters.

For data TX, `iwl_trans_pcie_tx()` verifies queue use and ring space, stops low-space queues, optionally queues overflow SKBs, checks A-MPDU sequence-to-ring alignment, maps the first command/header TBs, maps SKB head/frags or builds TSO-derived A-MSDU subframes, copies the first TB after mutation, updates SCD byte-count entries, advances the write pointer, and optionally delays the hardware write pointer for fragmented 802.11 frames. Reclaim walks from software read pointer to the firmware SSN, frees TSO pages and DMA mappings, invalidates byte-count table entries, queues completed SKBs, drains overflow packets, and wakes mac80211 when free space recovers.

## State and Persistence Behavior
The file maintains only in-memory transport state: `trans_pcie->txqs`, queue bitmaps, per-queue read/write pointers, `need_update`, `block`, `ampdu`, `frozen`, watchdog timer fields, SKB overflow queues, command metadata, and DMA addresses. Hardware-visible persistent state lives in coherent DRAM rings/tables and device registers/SRAM until reset. Sync host command state is tracked with `STATUS_SYNC_HCMD_ACTIVE`; APMG workaround state uses `cmd_hold_nic_awake`.

## Dependencies and Integration Points
It depends on Linux DMA, SKB, timer, spinlock, scatter-gather, TCP segmentation, and mac80211 header helpers. It integrates with iwlwifi common transport structs from `internal.h`, register access from `iwl-io.h`, scheduler helpers from `iwl-scd.h`, firmware command formats from `fw/api/*`, op-mode callbacks such as `iwl_op_mode_free_skb()`, reset/error paths such as `iwl_trans_schedule_reset()` and `iwl_force_nmi()`, and gen2 functions for newer queue formats.

## Risks and Edge Cases
The highest-risk areas are DMA lifetime and ring-index correctness. Error paths must unmap partially built TFDs, clear duplicated buffers, and avoid stale command response pointers. Queue arithmetic assumes power-of-two sizes. Hardware quirks include SCD pointer step avoidance, 32-bit DMA address constraints, APMG wake workarounds, disabled chain extension, and frozen station timers. A stuck queue triggers SCD logging and NMI. `iwl_pcie_txq_unmap()` has a defensive path for missing SKBs but could spin if a malformed queue never advances past a bad entry; this depends on invariants from normal enqueue paths.

## Test Signals
Coverage is mostly indirect through iwlwifi runtime, firmware command exercise, suspend/reset/RFKILL flows, and mac80211 TX tests. Useful test signals include host command timeout behavior, DMA mapping failure injection, ring wrap/overflow traffic, A-MSDU/TSO traffic, A-MPDU sequence alignment, queue freeze/unfreeze, command response page ownership, and debug/NMI reports for stuck queues.
