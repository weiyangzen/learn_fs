# sources/distributed-fs/ceph-client/net/nfc/hci/command.c

Purpose: Implements public HCI command/event helper APIs on top of the local HCP transmit path. It converts gate-oriented operations into pipe-oriented HCP messages, provides synchronous command execution with wait queues, and manages administrative pipe operations such as create, open, close, delete, and clear-all.

Important APIs and functions: `nfc_hci_send_event`, `nfc_hci_send_cmd`, `nfc_hci_send_cmd_async`, `nfc_hci_set_param`, `nfc_hci_get_param`, `nfc_hci_disconnect_gate`, `nfc_hci_disconnect_all_gates`, and `nfc_hci_connect_gate` are exported entry points for HCI clients and drivers. Internally, `nfc_hci_execute_cmd` wraps `nfc_hci_hcp_message_tx` with an on-stack waiter, while `nfc_hci_execute_cb` stores the result skb or frees it on error.

Control flow: Callers address a gate; the file resolves `hdev->gate2pipe[gate]`, returns `-EADDRNOTAVAIL` for unmapped gates, and sends an HCP command/event through `nfc_hci_hcp_message_tx`. Synchronous commands enqueue a message and wait until the HCI core response path invokes the callback. Pipe connection first handles fixed admin/link-management pipes, otherwise creates a pipe on the admin pipe, opens it, and updates `hdev->pipes` plus `gate2pipe`.

State and persistence: The main persistent state is the in-memory gate-to-pipe table and pipe metadata on `struct nfc_hci_dev`. Session identity persistence is not implemented here, but this file is used by `core.c` session initialization to create or reset the active pipe topology.

Dependencies and integration points: Depends on `hci.h` HCP definitions, exported NFC HCI constants from `<net/nfc/hci.h>`, skb ownership rules, and the asynchronous completion machinery in `hcp.c`/`core.c`. Driver-specific gates are reached through the HCI device's configured gate table.

Risks: `nfc_hci_execute_cmd` waits without an explicit timeout in this function; timeout behavior depends on HCI core command timers firing the callback. `nfc_hci_create_pipe` trusts response layout after command success and should be exercised with malformed controller responses. `nfc_hci_clear_all_pipes` has a TODO for identity reference bytes, with a quirk for short clear commands.

Test signals: Mock an HCI device with a fake `nfc_hci_hcp_message_tx`/response path to verify sync completion, async callback forwarding, gate lookup failures, cleanup after open failure, and pipe table updates for fixed and dynamically created gates. Include controller error-code translation and short-clear quirk coverage.
