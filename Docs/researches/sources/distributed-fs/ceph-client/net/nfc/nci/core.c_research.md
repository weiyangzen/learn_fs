# sources/distributed-fs/ceph-client/net/nfc/nci/core.c

Purpose: Implements the NCI core device, request serialization, command/data workqueues, NFC operation callbacks, RF discovery/activation/deactivation, NFCEE helpers, logical connection management, loopback, and driver-facing allocation/registration APIs.

Important APIs and functions: Exported APIs include `nci_allocate_device`, `nci_free_device`, `nci_register_device`, `nci_unregister_device`, `nci_recv_frame`, `nci_send_frame`, `nci_send_cmd`, `nci_request`, `nci_req_complete`, `nci_core_cmd`, `nci_prop_cmd`, `nci_core_reset`, `nci_core_init`, `nci_set_config`, `nci_nfcee_discover`, `nci_nfcee_mode_set`, `nci_core_conn_create`, `nci_core_conn_close`, and `nci_nfcc_loopback`.

Control flow: Requests are serialized by `req_lock`; `__nci_request` sends a request function and waits for `req_completion`. Open runs driver open/init, CORE_RESET, setup, CORE_INIT, post_setup, RF discovery map, then marks the device up. TX command work sends one command while `cmd_cnt` allows and arms a command timer. RX work validates inbound packet size and dispatches to response, notification, or data handlers. Data TX work sends queued data while connection credits allow.

State and persistence: `struct nci_dev` stores flags (`NCI_UP`, `NCI_INIT`, `NCI_UNREG`, data exchange flags), request status/result, workqueues, timers, command/rx/tx queues, connection list, RF connection pointer, HCI device, targets, current request parameters, active protocol, remote general bytes, ATS, and controller capabilities.

Dependencies and integration points: Hooks into `struct nfc_ops` for NFC core operations; calls lower driver `open`, `close`, `send`, and optional setup/security-element/firmware hooks; delegates packet bodies to `rsp.c`, `ntf.c`, and `data.c`; allocates an HCI-over-NCI helper through `hci.c`.

Risks: `nci_prop_cmd`, `nci_core_cmd`, `nci_core_reset`, and `nci_core_init` call `__nci_request` directly rather than `nci_request`, so callers must ensure serialization and device state. Close/unregister paths use workqueue flushes and timers with lock ordering that must avoid deadlocks with rx work and request completion. `nci_valid_size` rejects zero-length standard notifications/responses, so spec exceptions must be explicit.

Test signals: Exercise open success and each failure unwind point, command timeout and response completion, rx validation, proprietary/core op delegation, RF discovery state transitions, target activation/deactivation, data exchange busy handling, close during pending request/data exchange, logical connection create/close, and loopback connection reuse.
