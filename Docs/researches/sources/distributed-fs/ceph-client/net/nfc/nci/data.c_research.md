# sources/distributed-fs/ceph-client/net/nfc/nci/data.c

Purpose: Handles NCI data packet transmission, fragmentation, receive reassembly, status-byte handling for frame interfaces, and completion of NFC data exchanges.

Important APIs and functions: `nci_data_exchange_complete` completes pending exchanges and calls the stored callback. `nci_conn_max_data_pkt_payload_size` reports connection payload size. `nci_send_data` queues data to the NCI tx worker, fragmenting via `nci_queue_tx_data_frags` when needed. `nci_rx_data_packet` parses inbound data headers and calls `nci_add_rx_data_frag`.

Control flow: TX pushes an NCI data header with connection id, payload length, message type, and PBF. Large skbs are split into fragments sized by `conn_info->max_pkt_payload_len`, queued atomically, and the original skb is freed. RX strips the data header, optionally removes a trailing status byte for frame interfaces, reassembles continuation fragments in `ndev->rx_data_reassembly`, and either forwards target-mode data to NFC TM or completes the active exchange.

State and persistence: Uses per-connection `max_pkt_payload_len` and callbacks from `conn_info`, `ndev->tx_q`, `ndev->cur_conn_id`, `ndev->rx_data_reassembly`, `NCI_DATA_EXCHANGE`, and the data timer maintained by core.

Dependencies and integration points: Works with `nci_tx_work` in `core.c`, connection metadata created by `rsp.c`, RF mode from the NFC core device, and NFC target-mode delivery via `nfc_tm_data_received`.

Risks: RX reassembly stores only one partial packet for the whole device, so interleaved fragmented data on different connections would corrupt state. Status-byte removal assumes skb length is nonzero. `nci_data_exchange_complete` clears the data-exchange bit before invoking callbacks, intentionally allowing immediate reentry but requiring callback-safe state.

Test signals: Fragment at exact max size, one byte over max, multi-fragment payloads, allocation failure cleanup, credit-limited tx progression through core tx work, RX continuation/last reassembly, malformed empty frame-interface data, target-mode forwarding, and callback reentry.
