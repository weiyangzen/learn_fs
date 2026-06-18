# sources/distributed-fs/ceph-client/drivers/net/wireless/ralink/rt2x00/rt2800mmio.c

## Purpose
Implements the shared MMIO/DMA transport layer for RT2800 PCI and platform SoC devices. It owns MMIO TX/RX descriptor construction, RX descriptor interpretation, interrupt masking/dispatch, DMA queue register initialization, queue start/stop/kick/flush behavior, and the MMIO tx status timeout recovery loop.

## Important APIs, Types, And Functions
Exported functions include `rt2800mmio_get_dma_done()`, `rt2800mmio_get_txwi()`, `rt2800mmio_write_tx_desc()`, `rt2800mmio_fill_rxdone()`, tasklets for tx status/pre-TBTT/TBTT/RX/autowake, `rt2800mmio_interrupt()`, `rt2800mmio_toggle_irq()`, queue handlers, descriptor state helpers, `rt2800mmio_init_queues()`, `rt2800mmio_init_registers()`, `rt2800mmio_enable_radio()`, and `rt2800mmio_probe_hw()`. Descriptor fields come from `rt2800mmio.h`, while hardware access is via `rt2x00mmio_register_*()`.

## Control Flow
MMIO TX writes a DMA descriptor with SD_PTR0 pointing to TXWI, SD_PTR1 pointing to frame data, WIV/QSEL bits, burst/fragment flags, and records descriptor metadata in `skb_frame_desc`. TX kick updates `TX_CTX_IDX*` and starts the txstatus timer for EDCA queues. IRQ handling reads and acknowledges `INT_SOURCE_CSR`, masks active interrupt bits, pulls TX FIFO status into `txstatus_fifo`, and schedules tasklets. Tasklets process beacons, RX, autowake, or txdone and then re-enable their interrupt bit if the radio is still enabled. RX done reads descriptor word 3, flags CRC/cipher/L2PAD/MY_BSS/decryption status, then delegates RXWI parsing to shared RT2800 code.

## State And Persistence
Queue state is split between `data_queue` software indexes and hardware ring registers (`TX_BASE_PTR*`, `TX_MAX_CNT*`, `TX_CTX_IDX*`, `TX_DTX_IDX*`, `RX_BASE_PTR`, `RX_CRX_IDX`, `RX_DRX_IDX`). `txstatus_fifo` buffers ISR-collected status words, and `txstatus_timer` plus `txdone_work` recover missing or delayed status. `rt2800_drv_data.tbtt_tick` persists beacon interval skew compensation across TBTT interrupts while the radio is enabled.

## Dependencies And Integration Points
Used by both `rt2800pci.c` and `rt2800soc.c` through their `rt2x00lib_ops` and `rt2800_ops`. It depends on rt2x00 queue allocation/clear/index routines, RT2800 shared `rt2800_txdone*()` and `rt2800_process_rxwi()`, mac80211 beacon callbacks through `rt2x00lib_beacondone()`/`pretbtt()`, and kernel tasklets, hrtimers, workqueues, and kfifo.

## Risks
Interrupt masking is delicate: a missed re-enable can stall TX/RX/beacons, while a missed mask can race tasklet processing. TX status FIFO overflow or delayed hardware status can cause fallback `txdone_nostatus()` paths and misleading rate control. Descriptor DMA addresses and lengths must match the queue headroom/TXWI layout. Beacon skew compensation changes `BCN_TIME_CFG` every 64 beacons and can regress AP powersave clients if applied to the wrong mode. Flush waits are bounded and may leave hardware-owned entries on severe DMA hangs.

## Test Signals
Exercise TX/RX under high interrupt load, AP beaconing with powersave clients, tx status timeout recovery, suspend/remove during active tasklets, queue flush/drop, DMA ring wraparound, MMIC/ICV error reporting, and `ieee80211_restart_hw()` after watchdog. Useful diagnostics include interrupt counters, queue debugfs indexes, kfifo overflow warnings, and lockdep around `irqmask_lock`.
