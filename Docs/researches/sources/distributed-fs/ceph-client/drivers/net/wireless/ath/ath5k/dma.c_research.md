# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath5k/dma.c

## Purpose
`dma.c` owns ath5k hardware DMA control and interrupt-mask/status handling. It starts and stops RX DMA, programs RX/TX descriptor pointers, starts and drains TX queues, adjusts the TX FIFO trigger level, translates hardware interrupt status into `enum ath5k_int`, and initializes/stops DMA during reset or device shutdown. It hides major register differences between AR5210, which lacks QCU/DCU and PISR/SISR registers, and AR5211/AR5212+ hardware.

## Important APIs and Control Flow
The RX path is small: `ath5k_hw_start_rx_dma()` writes `AR5K_CR_RXE`; `ath5k_hw_stop_rx_dma()` writes `AR5K_CR_RXD` and polls for `AR5K_CR_RXE` to clear; `ath5k_hw_set_rxdp()` refuses to change `AR5K_RXDP` while RX is active.

TX queue flow runs through `ath5k_hw_start_tx_dma()` and private `ath5k_hw_stop_tx_dma()`. AR5210 maps logical ath5k queues onto two legacy control bits and `AR5K_BSR`; newer chips use `AR5K_QCU_TXE`, `AR5K_QCU_TXD`, `AR5K_QUEUE_TXDP()`, `AR5K_QUEUE_STATUS()`, and `AR5K_QUEUE_MISC()`. Stop logic enables DCU early termination, waits for QCU disable, polls pending frame counts, and on AR2414+ tries a QUIET-period packet-drop workaround before declaring `-EBUSY`.

Interrupt flow is centered on `ath5k_hw_get_isr()`. AR5210 reads `AR5K_ISR`; newer chips read PISR plus SISR0..4, clear SISRs before selected PISR bits, build `ah->ah_txq_isr_txok_all`, and map beacon, fatal, queue overrun/underrun, and trigger conditions into abstract ath5k bits. `ath5k_hw_set_imr()` disables global interrupts while rewriting masks, preserves per-queue TXURN mask bits, writes IMR/PIMR/SIMR2, updates `ah->ah_imr`, and re-enables `AR5K_IER` if requested.

## State, Dependencies, and Integration
Persistent driver state includes `ah->ah_imr`, `ah->ah_txq[]`, `ah->ah_txq_isr_txok_all`, hardware descriptor pointers, FIFO trigger registers, and pending interrupt registers. Dependencies are register helpers/macros from `reg.h`, debug macros, queue capability state, and timing delays (`udelay`). Integration points include the IRQ handler, reset/stop sequencing, qcu queue setup, beacon queue shutdown, and TX underrun recovery.

## Risks and Test Signals
Risks are hardware hangs during DMA drain, lost interrupts if PISR/SISR clear ordering changes, descriptor-pointer writes while engines are active, and version-specific AR5210 behavior. Test signals include successful suspend/reset without `-EBUSY`, no repeated "queue didn't stop" or "failed to stop RX DMA" debug messages, TX underrun recovery through trigger-level increase, stable beacon queues, and correct per-queue TX completion tasklet scheduling after simultaneous TXOK/TXERR/TXEOL interrupts.
