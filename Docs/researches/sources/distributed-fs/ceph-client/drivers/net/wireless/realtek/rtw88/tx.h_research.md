## sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/tx.h

Purpose: declares the rtw88 TX descriptor format, queue-select values, TX helper APIs, and descriptor checksum helper.

Important APIs/types: `struct rtw_tx_desc` is a packed ten-word hardware descriptor. `RTW_TX_DESC_W*` masks encode packet size, offset, BMC, MAC ID, QSEL, rate ID, security type, aggregation, report, RTS, fixed rate, data rate, BW, LDPC/STBC, checksum, hardware sequence, software sequence, and TIM offset. `enum rtw_tx_desc_queue_select` maps TIDs, beacon, high, management, and H2C queue selects.

Control flow: `fill_txdesc_checksum_common()` clears and recomputes the descriptor checksum over 16-bit words. `rtw_tx_fill_txdesc_checksum()` delegates to chip ops, allowing chip-specific checksum behavior while preserving the common call site.

State and persistence: no persistent state. The header defines on-wire/on-DMA descriptor state used by all HCI transmit paths.

Dependencies and integration: included by common TX plus USB/SDIO transports. It depends on `struct rtw_dev`, `struct rtw_tx_pkt_info`, mac80211 TX types, and chip ops.

Risks and test signals: descriptor ABI mistakes produce firmware drops, wrong queueing, bad rates, or checksum failures. Test with descriptor dumps, H2C/reserved pages, TX over each access category, and chip-specific checksum validation.
