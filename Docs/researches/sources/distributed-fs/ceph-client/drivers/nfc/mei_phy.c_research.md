# sources/distributed-fs/ceph-client/drivers/nfc/mei_phy.c

Purpose: Provides a reusable NFC HCI physical layer over Intel MEI client devices. It wraps HCI payloads in MEI NFC headers, performs maintenance version/connect handshakes, waits for send acknowledgements, dispatches inbound HCI frames, and exports `mei_phy_ops` plus allocation/free helpers.

Important APIs, types, and functions: Internal packed structs define MEI NFC headers, maintenance commands, replies, interface version, and connect response. `nfc_mei_phy_enable()` enables the MEI client, reads interface version, connects, and registers RX callback; `nfc_mei_phy_write()` sends an HCI SKB through `mei_nfc_send()`; `nfc_mei_rx_cb()` receives MEI frames and calls `nfc_hci_recv_frame()`; `nfc_mei_phy_alloc()` and `nfc_mei_phy_free()` manage `struct nfc_mei_phy`.

Control flow: A MEI-backed driver allocates the PHY and passes `mei_phy_ops` to an HCI core driver. Enable sends maintenance IF_VERSION and CONNECT commands synchronously through `mei_cldev_send/recv`, then registers a receive callback. Outbound HCI frames are prefixed with `MEI_NFC_CMD_HCI_SEND`, current request id, and payload length; the sender waits up to one second for an acknowledgement frame with matching request id. Inbound non-ack frames become HCI SKBs after the header is stripped.

State and persistence behavior: `nfc_mei_phy` tracks MEI client pointer, HCI device, send wait queue, firmware/vendor/radio identifiers, request and received ids, powered flag, and hard fault. State is volatile and reset by disable/free.

Dependencies and integration points: Uses the MEI client bus, NFC HCI core, wait queues, SKBs, and UUID published in `mei_phy.h`. `microread/mei.c` is a direct consumer.

Risks: Header length and packed layout must match ME firmware. Send acknowledgement is serialized only by request ids and wait queue state; concurrent writes could race. `hard_fault` is checked on RX but not broadly set in this file. Receive size validation is minimal beyond header-size checks.

Test signals: MEI probe/remove, enable handshake failures at send/recv/version/connect stages, send timeout, request id wrap, inbound HCI frame delivery, ack-only frame handling, disable while send waits, and module unload with registered callbacks.
