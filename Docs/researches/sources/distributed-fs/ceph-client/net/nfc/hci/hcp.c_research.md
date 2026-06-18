# sources/distributed-fs/ceph-client/net/nfc/hci/hcp.c

Purpose: Implements HCP message transmit fragmentation and top-level receive dispatch for the HCI stack.

Important APIs and functions: `nfc_hci_hcp_message_tx` allocates `struct hci_msg`, fragments payloads according to `hdev->max_data_link_payload`, stores callbacks and completion delay, and queues the message for `core.c` transmit work. `nfc_hci_hcp_message_rx` dispatches completed HCP messages to response, command, or event handlers.

Control flow: Transmit prepends the HCP message header only in the first fragment, copies payload across fragments, sets the final-fragment bit on the last packet header, then appends the message to `hdev->msg_tx_queue` under `msg_tx_mutex`. Receive is a small type switch that calls `nfc_hci_resp_received`, `nfc_hci_cmd_received`, or `nfc_hci_event_received`.

State and persistence: Queued `struct hci_msg` owns an skb fragment queue, callback metadata, wait-response flag, and completion delay until the core tx/response path frees it.

Dependencies and integration points: Depends on `hci.h` wire definitions, `struct nfc_hci_dev` queue/mutex fields initialized in `core.c`, and downstream LLC transmission through the core tx worker.

Risks: Fragment sizing relies on `max_data_link_payload` being larger than the packet header; invalid driver configuration could underflow payload room. The `ptr` handling interleaves message header and payload bytes and should be regression-tested for zero-length and exact-boundary payloads. Shutdown detection happens after all fragments are allocated.

Test signals: Exercise zero payload commands, single-fragment payloads, multi-fragment payloads, allocation failure cleanup, shutdown rejection, final-fragment bit placement, and receive dispatch for all HCP message types.
