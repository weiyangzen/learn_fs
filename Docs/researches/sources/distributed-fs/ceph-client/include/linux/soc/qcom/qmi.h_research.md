# sources/distributed-fs/ceph-client/include/linux/soc/qcom/qmi.h

Purpose: This header defines the in-kernel Qualcomm QMI helper framework for encoding/decoding TLV messages, service lookup, handles, transactions, and callbacks.

Important APIs/types/functions: It defines QMI element descriptors, array/string/struct encodings, transaction state, service info, handle operations, and APIs for handle init/release, adding/removing lookup, sending requests/responses/indications, transaction init/wait/cancel, encoding, decoding, and message handler dispatch.

Control flow: A QMI service/client initializes a handle with ops, registers lookups or server state, creates transactions for requests, sends encoded messages, waits for responses, and dispatches incoming messages to handlers based on type and message ID.

State and persistence: `qmi_handle` and transactions maintain socket/transport bindings, pending responses, service lookup state, locks/lists, and private callbacks. Remote services persist across subsystem restarts.

Dependencies and integration: Integrates with Qualcomm QRTR sockets, workqueues, mutexes/completions, service registry, PDR, remoteproc clients, and subsystem-specific protocols.

Risks and test signals: TLV descriptor mismatches can corrupt decode, leak memory, or reject valid messages. Transaction timeout/cancel paths are race-prone. Test encode/decode vectors, lookup add/remove, concurrent transactions, SSR, malformed messages, and handler coverage.
