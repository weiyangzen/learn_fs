# sources/distributed-fs/ceph-client/include/net/nfc/hci.h

Purpose: defines the NFC HCI device abstraction, pipe/gate constants, command/event helpers, and driver callbacks for NFC controllers using the ETSI HCI protocol.

Important APIs and types: `struct nfc_hci_ops` covers device open/close, session load/readiness, complete-buffer transmit, polling, DEP link management, target discovery, initiator/target data exchange, secure element operations, firmware download, and vendor events/commands. `struct nfc_hci_dev` stores NFC core device, LLC instance, gate-to-pipe mappings, tx/rx queues, timers, pending command, callback context, general bytes, version fields, and quirks. Public helpers allocate/register devices, connect/disconnect gates, get/set parameters, send commands/events, reset pipes, receive frames, and convert results.

Control flow: lower LLC/driver receive paths call frame/response/command/event entry points; upper NFC operations issue HCI commands through pipe/gate routing and serialize pending command state with timers/work.

State and persistence: session identity, pipe table, gate map, queued messages, pending command, firmware/version metadata, and async callbacks are in-memory controller-session state. Persistence depends on controller session loading.

Dependencies and integration points: depends on NFC core and LLC, skbuff queues, timers, workqueues, and secure element APIs.

Risks and test signals: risks include pipe map corruption, command timer races, incomplete lower-layer transmit, shutdown with queued messages, and quirk-specific clear behavior. Test HCI open/session load, pipe creation/reset, parameter get/set, event dispatch, DEP up/down, SE IO, firmware download, and LLC failures.
