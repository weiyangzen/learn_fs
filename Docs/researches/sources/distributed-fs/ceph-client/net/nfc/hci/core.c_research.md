# sources/distributed-fs/ceph-client/net/nfc/hci/core.c

Purpose: Provides the NFC HCI core: NFC device allocation/registration, LLC integration, HCP transmit and receive workers, command timeout handling, HCI session initialization, target discovery, NFC operation callbacks, and driver failure propagation.

Important APIs and functions: Exported functions include `nfc_hci_result_to_errno`, `nfc_hci_reset_pipes`, `nfc_hci_reset_pipes_per_host`, `nfc_hci_sak_to_protocol`, `nfc_hci_target_discovered`, `nfc_hci_allocate_device`, `nfc_hci_free_device`, `nfc_hci_register_device`, `nfc_hci_unregister_device`, `nfc_hci_driver_failure`, and `nfc_hci_recv_frame`. Core workers are `nfc_hci_msg_tx_work`, `nfc_hci_msg_rx_work`, and `nfc_hci_cmd_timeout`.

Control flow: Transmit work serializes queued `struct hci_msg` items, sends fragments through `nfc_llc_xmit_from_hci`, and holds one pending command until response or timeout. Receive flow enters from `nfc_hci_recv_frame`, passes through the selected LLC, reassembles HCP fragments in `nfc_hci_recv_from_llc`, dispatches responses immediately, and queues commands/events to `msg_rx_work`. NFC operations call driver hooks where available, with generic fallbacks for polling and transceive.

State and persistence: `struct nfc_hci_dev` stores pipe mappings, pending command, tx/rx queues, timers, work items, version fields, async callback state, quirks, init data, and shutdown state. Session initialization reads the admin session identity and either asks the driver to `load_session` or clears/reconnects all configured gates and stores a fresh identity.

Dependencies and integration points: Integrates with `net/nfc` device registration via `struct nfc_ops`, the HCI command helpers in `command.c`, HCP dispatch in `hcp.c`, LLC engines from `llc.c`, and optional driver callbacks in `struct nfc_hci_ops`. Reports discovered targets via `nfc_targets_found` and failures via `nfc_driver_failure`.

Risks: The command serialization path must avoid races among shutdown, timeout, response completion, and worker rescheduling. HCP fragment reassembly assumes fragment queue consistency and only reports allocation failure through driver failure. Target discovery uses controller-provided parameter lengths and can fail with `-EPROTO`; edge cases around multi-target status are still TODO.

Test signals: Use a fake LLC engine and fake NFC core device to validate command queue progression, response-before-timeout, timeout callback, shutdown cleanup, receive reassembly, event dispatch to driver hooks, session identity restore versus reset, and failure propagation.
