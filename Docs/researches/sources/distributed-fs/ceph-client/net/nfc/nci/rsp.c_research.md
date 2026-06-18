# sources/distributed-fs/ceph-client/net/nfc/nci/rsp.c

Purpose: Parses and handles NCI response packets, updating controller capability state, RF/request state, logical connection records, and request completion.

Important APIs and functions: `nci_rsp_packet` is the dispatcher. Response handlers include `nci_core_reset_rsp_packet`, `nci_core_init_rsp_packet_v1`, `nci_core_init_rsp_packet_v2`, `nci_core_init_rsp_packet`, `nci_core_set_config_rsp_packet`, `nci_rf_disc_map_rsp_packet`, `nci_rf_disc_rsp_packet`, `nci_rf_disc_select_rsp_packet`, `nci_rf_deactivate_rsp_packet`, `nci_nfcee_discover_rsp_packet`, `nci_nfcee_mode_set_rsp_packet`, `nci_core_conn_create_rsp_packet`, and `nci_core_conn_close_rsp_packet`.

Control flow: The dispatcher stops the command timer, logs opcode fields, strips the control header, dispatches proprietary responses to driver ops or core opcodes to local handlers, calls optional core response hooks, frees the skb, resets `cmd_cnt`, and queues the next command if one is pending. Some requests complete only after a later notification, such as RF_DISCOVER_SELECT success or active-target RF_DEACTIVATE success.

State and persistence: Mutates controller version/capability fields, supported RF interfaces, routing/control limits, manufacturer fields, NCI state, RF connection info, connection list, current HCI connection pointer, connection payload sizes, and credits. Connection records are devm-allocated and linked in `ndev->conn_info_list`.

Dependencies and integration points: Completes `core.c` synchronous requests via `nci_req_complete`, creates connection metadata consumed by `data.c` and `hci.c`, and delegates driver-specific response handling via proprietary/core ops tables.

Risks: Core init v1/v2 parsing relies on response lengths matching spec after the generic NCI size check; malformed but minimally sized packets can still cause offset issues. `nci_core_conn_create_rsp_packet` cleanup uses devm allocation/free patterns and must keep `hci_dev->conn_info` consistent. Some response handlers intentionally defer completion, so request timeout coverage is important.

Test signals: Validate reset/init parsing for NCI 1.x and 2.x, RF discovery success creating static RF connection, deferred completion paths, logical connection create/close including HCI connection selection, command queue restart after each response, proprietary response delegation, and malformed lengths.
