# sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeon_ep/octep_tx.c

## Purpose
This file implements PF transmit queue allocation, descriptor and scatter/gather list management, completion processing, pending-buffer cleanup, and queue teardown for OCTEON Input Queues.

## Important APIs, Types, And Functions
- Setup/cleanup: `octep_setup_iqs()`, `octep_setup_iq()`, `octep_free_iqs()`, `octep_free_iq()`, and `octep_clean_iqs()`.
- Completion: `octep_iq_process_completions()` reads the hardware read index via `hw_ops.update_iq_read_idx()`, unmaps DMA buffers, frees skbs, updates stats, completes BQL accounting, and wakes stopped subqueues.
- Shutdown cleanup: `octep_iq_free_pending()` unmaps and frees all packets between `flush_index` and `host_write_index` and resets BQL state.
- Index management: `octep_iq_reset_indices()` zeros fill, write, read, flush, and hardware completion accounting fields.

## Control Flow
Queue setup allocates a `struct octep_iq`, coherent descriptor ring, coherent per-packet SGL memory, and a software buffer-info array. It precomputes each tx buffer's SGL virtual and DMA address, resets queue indices, and calls chip-specific `setup_iq_regs()`. During NAPI, completion processing updates the device read index, walks descriptors from `flush_index` until the hardware read index or budget, unmaps either single-buffer or gather DMA mappings, frees skbs, advances `flush_index`, updates stats and BQL, and wakes subqueues when descriptor space recovers.

On stop, `octep_clean_iqs()` frees any submitted but not completed buffers and resets indices before hardware queues are disabled/reset and queue structures are freed.

## State And Persistence
Tx state is per-open runtime state: descriptor ring DMA memory, SGL DMA memory, `buff_info`, ring indices, `fill_cnt`, `fill_threshold`, `pkt_in_done`, `pkts_processed`, BQL state, and per-queue stats. No persistent state exists. Hardware-visible state includes the IQ descriptor ring, SGL memory, doorbell writes, and instruction count register acknowledgements.

## Dependencies And Integration Points
The file depends on `octep_tx.h` for formats and stats, `octep_config.h` for queue sizes and thresholds, `octep_main.h` for hardware ops and device context, Linux DMA APIs, skb APIs, and netdev queue/BQL APIs. It is used by `octep_main.c` open/stop and NAPI paths; descriptor contents are prepared by `octep_start_xmit()`.

## Risks And Edge Cases
- DMA unmap logic must mirror mapping logic in `octep_start_xmit()`, including SGL index layout.
- `octep_free_iqs()` assumes queue pointers exist for active ring count; callers must only call it after partial setup cleanup has handled NULLs or active counts are consistent.
- Completion budget returns `!budget`, which signals pending work when budget is exhausted rather than when hardware still has completions.
- Ring size masks require descriptor counts to be powers of two.
- BQL accounting must remain balanced between `netdev_tx_sent_queue()`/`__netdev_tx_sent_queue()` in transmit and `netdev_tx_completed_queue()`/reset in completion/cleanup.

## Test Signals
Exercise Tx under single-buffer and fragmented skb loads, TSO/checksum-enabled traffic, queue-full and wake paths, BQL behavior, open/stop with pending Tx, DMA debug unmap balance, netdev watchdog timeout recovery, and partial allocation failure unwinding.
