# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath5k/desc.c

## Purpose
`desc.c` implements version-specific hardware descriptor setup and status parsing for ath5k DMA. It hides AR5210/AR5211 2-word TX descriptors and AR5212 4-word TX descriptors behind callback pointers in `struct ath5k_hw`, and provides common RX descriptor setup/status parsing.

## Important APIs and functions
- TX setup: `ath5k_hw_setup_2word_tx_desc`, `ath5k_hw_setup_4word_tx_desc`.
- MRR setup: `ath5k_hw_setup_mrr_tx_desc`.
- TX status parse: `ath5k_hw_proc_2word_tx_status`, `ath5k_hw_proc_4word_tx_status`.
- RX setup: `ath5k_hw_setup_rx_desc`.
- RX status parse: `ath5k_hw_proc_5210_rx_status`, `ath5k_hw_proc_5212_rx_status`.
- Attach hook: `ath5k_hw_init_desc_functions`.

## Control flow
Attach calls `ath5k_hw_init_desc_functions` after identifying the MAC generation. That assigns `ah_setup_tx_desc`, `ah_proc_tx_desc`, and `ah_proc_rx_desc`. TX enqueue in `base.c` calls the selected setup function after DMA mapping an skb. The setup functions validate nonzero retry count and nonzero rate to avoid dangerous hardware behavior, compute frame length excluding software padding and including FCS, round beacon buffer length, fill encryption key fields when present, encode frame type, antenna, no-ack, interrupt, VEOL, RTS/CTS, CTS-to-self, rate, retry, and txpower fields. AR5212 setup additionally writes four control words and supports CTSENA/MRR.

TX completion paths call the selected status parser. The parser checks the DONE bit, returns `-EINPROGRESS` if hardware still owns the descriptor, and fills `ath5k_tx_status` with timestamp, retry counts, sequence, ACK RSSI, antenna, final MRR index, and error flags for excessive retry, FIFO underrun, and filtered frames.

RX setup clears descriptor state and writes buffer length plus optional interrupt request. RX parsers check DONE, extract length, RSSI, rate, antenna, timestamp, key index, more-fragment flag, and map hardware error bits into `AR5K_RXERR_*`. AR5212 PHY errors optionally feed ANI when hardware PHY error counters are unavailable.

## State and persistence behavior
The file writes DMA descriptors in coherent memory shared with hardware and reads status words written by hardware. It does not allocate memory or persist state itself. `READ_ONCE` is used for AR5212 status words to avoid compiler reordering or duplicate loads from hardware-updated memory.

## Dependencies and integration points
It depends on descriptor layout definitions in `desc.h`, register bit helpers in `ath5k.h`, hardware version fields, ANI error reporting, and debug logging. It is used directly by `base.c` TX/RX paths through function pointers.

## Risks and edge cases
- Zero rate with nonzero retries can cause continuous noise transmission; the code explicitly warns and rejects this.
- Frame/buffer length field overflows return `-EINVAL`; callers must handle descriptor setup failure and unmap DMA.
- AR5210/AR5211 timestamp width comments note uncertainty around 13-bit versus 15-bit assumptions.
- Descriptor memory is hardware-shared, so status readiness and field ordering are race-sensitive.
- MRR only applies to AR5212; older devices silently ignore it.

## Test signals
Exercise TX with ACKed frames, excessive retries, FIFO underruns, filtered frames, RTS/CTS, no-ack, hardware encryption, beacons, and MRR rates. Exercise RX with CRC, PHY, decrypt, MIC, key-index, and restart PHY errors. Look for no WARNs on zero rates, no DMA leaks after setup failures, correct mac80211 status reporting, and valid debug descriptor dumps.
