<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/mac.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/mac.c

Purpose: Implements exported low-level MAC helper APIs for ath9k queue control, TX/RX descriptor processing, DMA stop/abort, beacon queue setup, interrupt programming, and TX filtering. It bridges driver logic to Atheros AR register programming.

Important APIs and functions: Exports `ath9k_hw_gettxbuf()`, `ath9k_hw_puttxbuf()`, `ath9k_hw_txstart()`, `ath9k_hw_numtxpending()`, `ath9k_hw_updatetxtriglevel()`, `ath9k_hw_abort_tx_dma()`, `ath9k_hw_stop_dma_queue()`, `ath9k_hw_set_txq_props()`, `ath9k_hw_get_txq_props()`, `ath9k_hw_setuptxqueue()`, `ath9k_hw_releasetxqueue()`, `ath9k_hw_resettxqueue()`, `ath9k_hw_rxprocdesc()`, `ath9k_hw_setrxabort()`, `ath9k_hw_putrxbuf()`, `ath9k_hw_startpcureceive()`, `ath9k_hw_abortpcurecv()`, `ath9k_hw_stopdmarecv()`, `ath9k_hw_beaconq_setup()`, `ath9k_hw_intrpend()`, interrupt enable/disable helpers, and `ath9k_hw_set_tx_filter()`.

Control flow: TX queue setup maps abstract queue types to QCU IDs, stores properties, and resets queues by programming contention windows, AIFS, retry limits, CBR/ready time, burst time, beacon/CAB/UAPSD-specific flags, descriptor CRC checks, and interrupt masks. TX abort/stop assert queue disable or forced channel-idle bits and poll pending counters. RX descriptor processing converts hardware status words into `ath_rx_status`, handling RSSI, rate, aggregation, key index, delimiter CRC, PHY/CRC/decrypt/MIC/keymiss errors, STBC/GI/bandwidth flags, and corrupt descriptor detection. Interrupt setup derives AR_IMR/S2/S5 and MSI masks from `ah->imask`, queue interrupt masks, mitigation settings, autosleep, MCI, and BB watchdog config.

State and persistence: Mutates `ah->txq[]`, queue interrupt masks, `ah->imrs2_reg`, `ah->msi_mask`, `ah->msi_reg`, `ah->intr_ref_cnt`, `ah->tx_trig_level`, and hardware registers. No durable persistence exists, but register state persists until reset or reprogramming and must match in-memory masks.

Dependencies and integration points: Depends on `hw.h`, `hw-ops.h`, AR register macros, revision predicates, atomic interrupt reference counting, and exported symbols used by TX, RX, main interrupt/reset code, beaconing, and station power-save filtering.

Risks: Register bitfield mistakes directly corrupt queue timing, interrupt delivery, or descriptor interpretation. Interrupt reference count imbalance can leave interrupts disabled or spuriously enabled. RX status error precedence intentionally treats errors as mutually exclusive; changes can alter drop/stat behavior. DMA stop polling has hardware-specific stuck-state handling. MSI enable loops and masks are revision-sensitive.

Test signals: Configure all queue types, WMM AC parameter changes, beacon/CAB behavior, TX underrun trigger-level increases, TX DMA stop timeout, RX descriptor parsing for OK/PHY/CRC/decrypt/MIC/keymiss/corrupt cases, RX abort idle timeout, interrupt mask transitions with MSI and legacy INTx, MCI interrupt enabling, and sleeping-station TX filter programming.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/mac.c -->
