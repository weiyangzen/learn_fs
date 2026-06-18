# sources/distributed-fs/ceph-client/net/nfc/nci/ntf.c

Purpose: Parses and handles NCI notification packets, including reset notifications, connection credits, generic/interface errors, RF discovery, RF activation/deactivation, and NFCEE discovery.

Important APIs and functions: `nci_ntf_packet` is the dispatcher. Supporting functions include `nci_core_reset_ntf_packet`, `nci_core_conn_credits_ntf_packet`, `nci_core_generic_error_ntf_packet`, `nci_core_conn_intf_error_ntf_packet`, RF parameter extractors, `nci_add_new_protocol`, `nci_add_new_target`, `nci_clear_target_list`, `nci_rf_discover_ntf_packet`, `nci_rf_intf_activated_ntf_packet`, `nci_rf_deactivate_ntf_packet`, and `nci_nfcee_discover_ntf_packet`.

Control flow: The dispatcher strips the NCI control header, offers proprietary notifications to driver ops, then handles core opcodes. Discovery notifications parse RF technology parameters, aggregate protocols on existing logical targets, and report targets when the final discovery notification arrives. Activation notifications update RF connection payload size/credits, store NFC-DEP general bytes or ISO-DEP ATS, and transition to poll-active or listen-active. Credit notifications add to connection credits and restart TX work.

State and persistence: Mutates `ndev->nci_ver`, manufacturer fields, target array/count, state atomics, RF connection credits and payload size, remote general bytes, target ATS, HCI NFCEE id/current params, tx queue, rx reassembly, and data-exchange flags.

Dependencies and integration points: Works with `core.c` request completion and state machine, `data.c` data exchange completion, NFC core target reporting and target-mode activation, driver proprietary/core notification hooks, and NCI HCI setup.

Risks: Parsing is length-aware in many places, but some activation parameter copies clamp length without always verifying enough remaining bytes for copied data. Protocol filtering depends on `ndev->poll_prots` and may drop proprietary mappings unless the driver implements `get_rfprotocol`. Deactivation purges data queues and completes exchanges with `-EIO`, so upper layers must tolerate abrupt cancellation.

Test signals: Fuzz all notification parsers, exercise multi-notification discovery, duplicate logical targets with multiple protocols, activation for ISO-DEP/NFC-DEP/frame/listen modes, credit replenishment, interface errors during exchange, deactivation modes, NFCEE discovery for HCI, and proprietary notification delegation.
