# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath11k/ce.c

## Purpose
`ce.c` implements ath11k Copy Engine host-side rings. Copy Engines move HTC, WMI, HTT, pktlog, and raw/control traffic between host and firmware. The file provides hardware-family CE attribute tables, DMA-coherent ring allocation, HAL SRNG setup, TX submission/completion, RX buffer posting/completion, shadow-register handling, and cleanup.

## Important APIs, Types, And Functions
Exported entry points include `ath11k_ce_alloc_pipes()`, `ath11k_ce_init_pipes()`, `ath11k_ce_free_pipes()`, `ath11k_ce_send()`, `ath11k_ce_per_engine_service()`, `ath11k_ce_rx_post_buf()`, `ath11k_ce_cleanup_pipes()`, `ath11k_ce_get_shadow_config()`, `ath11k_ce_stop_shadow_timers()`, and `ath11k_ce_get_attr_flags()`. The main configuration tables are `ath11k_host_ce_config_ipq8074`, `ath11k_host_ce_config_qca6390`, and `ath11k_host_ce_config_qcn9074`, each defining source/destination ring sizes, max buffer sizes, callbacks, and interrupt-disabling flags.

## Control Flow
Allocation initializes `ab->ce.ce_lock`, creates per-pipe source, destination, and status rings according to hardware params, and uses DMA-coherent descriptor memory aligned to `CE_DESC_RING_ALIGN`. Initialization turns those rings into HAL SRNGs and sets MSI interrupt parameters when interrupts are enabled. TX via `ath11k_ce_send()` optionally polls disabled-interrupt rings, rejects crash flush, obtains a HAL source descriptor, writes the DMA address/length/transfer ID, stores the skb at the write index, and starts the CE4 shadow timer workaround when needed. RX posting allocates skbs, DMA-maps them, queues destination descriptors, and later `ath11k_ce_recv_process_cb()` unmaps, validates lengths, passes skb lists to receive callbacks, and replenishes buffers. Interrupt handlers in bus layers call `ath11k_ce_per_engine_service()` to reap both TX and RX.

## State And Persistence
Per-ring state includes host and CE DMA addresses, software/write indices, HAL ring ID, and skb slots. Per-pipe state includes callbacks, buffer size, interrupt tasklet, and `rx_buf_needed`. State is volatile; descriptor memory and skb DMA mappings are created and destroyed per device lifecycle. The RX replenish retry timer in `ath11k_base` persists across temporary allocation failures until cleanup.

## Dependencies And Integration Points
CE sits between HIF interrupt code, HAL SRNG operations, HTC callbacks, DP HTT handlers, DMA APIs, and hardware params from `core.c`. Shadow-register workarounds integrate with DP shadow timer helpers. HIF start/stop and QMI firmware startup expect CE rings and QMI CE config to be ready.

## Risks And Test Signals
Risk areas include ring index correctness, DMA map/unmap pairing, buffer exhaustion, crash-flush races, disabled-interrupt CE polling, and partial initialization cleanup. Comments explicitly note incomplete cleanup questions for TX buffers and partial ring init. Test signals include WMI/HTC boot traffic, high-throughput HTT TX/RX, repeated firmware restart, RX replenish failure injection, big-endian byte-swap coverage, and KASAN/KMSAN/lockdep checks around `ce_lock` and SRNG locks.
