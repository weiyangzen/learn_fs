# sources/distributed-fs/ceph-client/net/nfc/nci/hci.c

Purpose: Implements HCI over NCI logical connections, allowing HCP command/event/response traffic to run over the NCI data path as specified by NCI 1.1.

Important APIs and functions: Exported APIs include `nci_hci_send_event`, `nci_hci_send_cmd`, `nci_hci_clear_all_pipes`, `nci_hci_open_pipe`, `nci_hci_set_param`, `nci_hci_get_param`, `nci_hci_connect_gate`, `nci_hci_dev_session_init`, `nci_hci_allocate`, and `nci_hci_deallocate`. Core helpers include `nci_hci_send_data`, `nci_hci_data_received_cb`, `nci_hci_cmd_received`, and `nci_hci_msg_rx_work`.

Control flow: HCI send paths resolve gate to pipe, build HCP headers, and call `nci_send_data` over `hci_dev->conn_info`. Synchronous commands use `nci_request` and receive their response through `nci_hci_data_received_cb`, which reassembles HCP fragments and completes the request. Non-response commands/events are queued to `msg_rx_work`; admin notifications update the pipe table and send a response.

State and persistence: `struct nci_hci_dev` holds pipe/gate tables, HCI init data, NFCEE id, HCI connection info, receive fragment queue, message receive queue, and rx work. Session init resets pipes, opens the admin pipe, reads session identity, optionally restores a driver session, or clears/reconnects configured gates and stores a session id.

Dependencies and integration points: Depends on NCI connection records from CORE_CONN_CREATE and NFCEE discovery notifications. Uses `nci_request`, `nci_send_data`, and driver callbacks such as `hci_event_received`, `hci_cmd_received`, and `hci_load_session`.

Risks: `nci_hci_send_cmd`, `set_param`, and `get_param` assume `conn_info->rx_skb` is present after a successful request. `nci_hci_hcp_message_rx` calls `nci_req_complete` after dispatch even though response handling also completes, which should be verified for harmless duplicate completion. Fragment reassembly needs malformed and allocation-failure coverage. Pipe table updates rely on controller-provided lengths and pipe IDs.

Test signals: Exercise HCI logical connection setup, session restore versus clear/reconnect, command response conversion, parameter get/set, event/cmd driver callbacks, HCP fragmentation/reassembly, admin pipe notifications, invalid pipe/gate handling, and missing `conn_info` errors.
