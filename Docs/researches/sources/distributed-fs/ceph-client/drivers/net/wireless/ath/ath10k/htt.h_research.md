# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath10k/htt.h

Purpose: defines the ath10k HTT firmware ABI and host-side HTT state. It covers H2T commands, T2H indications, TX/RX descriptors, RX rings, debug stats, security and block-ack events, TX completions, high-latency fetch/push scheduling, DMA state, ops tables, and public HTT functions.

Important APIs/types/functions: key definitions include `enum htt_h2t_msg_type`, `struct htt_cmd`, TX descriptors, RX ring setup structs, stats/OOB/aggr/mgmt TX commands, firmware-specific and common T2H enums, RX indications, peer map/unmap, security, ADDBA/DELBA, TX completion formats, TX fetch/mode switch, peer stats, RX descriptor v1/v2 layouts, `struct ath10k_htt`, `struct ath10k_htt_tx_ops`, and `struct ath10k_htt_rx_ops`.

Control flow: setup sends version, fragment-bank, RX-ring, and aggregation commands. TX fills descriptors and receives target completions. RX maintains DMA buffer rings, receives indications, handles peer/security/reorder metadata, and delivers frames to mac80211. HL firmware can pull queued traffic through fetch indications and shared queue state.

State and persistence: all state is runtime memory and DMA allocations: RX paddr rings, skb rings/hash table, alloc-index shadow, timers, pending TX IDR, TX done FIFO, completion queues, fragment descriptor bank, TX buffer bank, optional queue-state memory, and ops pointers. No on-disk persistence exists.

Dependencies/integration: depends on Linux DMA/hash/kfifo/mac80211, `htc.h`, `hw.h`, `rx_desc.h`, and implementation files `htt.c`, `htt_tx.c`, and `htt_rx.c`. Packed little-endian structs must match firmware exactly.

Risks: ABI layout or enum changes can silently break firmware; variable-length messages require strict bounds checks; RX refill/ring accounting errors can starve or mis-associate buffers; default v1 RX descriptor access can hide wrong hardware selection; queue-state comments indicate firmware quirks around configured fields.

Test signals: 32/64-bit DMA, HL/LL, all firmware op versions, version negotiation, RX refill pressure, in-order RX, peer map/unmap, security, ADDBA/DELBA, TX completions with appended metadata, management TX status, fetch/mode switch, peer stats, pktlog/test messages, malformed variable-length indications, and descriptor size/offset assertions.
