# sources/distributed-fs/ceph-client/drivers/soc/qcom/qmi_interface.c

## Purpose

`qmi_interface.c` provides the kernel-side Qualcomm QMI transport over QRTR sockets. It manages service lookup/advertisement, transactions, message dispatch, QRTR control packets, socket reset handling, workqueue-driven receive processing, and send helpers for requests, responses, and indications.

## Important APIs, Types, and Functions

Exported APIs include `qmi_add_lookup()`, `qmi_add_server()`, `qmi_txn_init()`, `qmi_txn_wait()`, `qmi_txn_cancel()`, `qmi_handle_init()`, `qmi_handle_release()`, `qmi_send_request()`, `qmi_send_response()`, and `qmi_send_indication()`. Internal paths handle QRTR `NEW_SERVER`, `DEL_SERVER`, `BYE`, `DEL_CLIENT`, net reset, message dispatch, and socket creation. Runtime state lives in `struct qmi_handle`: socket, locks, IDR of transactions, workqueue, receive buffer, service lists, lookup results, callbacks, and handlers.

## Control Flow

`qmi_handle_init()` initializes locks, IDR, service lists, work item, handlers, receive buffer, ordered workqueue, and QRTR socket. Socket data-ready callbacks queue work. `qmi_data_ready_work()` drains datagrams; control packets update callbacks/service lists, ENETRESET recreates the socket and reannounces lookups/services, and normal packets either use a raw `msg_handler` callback or the QMI transaction/handler dispatcher. Responses match `txn_id` in the IDR; requests and indications use a temporary transaction object carrying the incoming id. Send helpers encode messages with `qmi_encode_message()` and send over the QRTR socket under `sock_lock`.

## State and Persistence Behavior

State is volatile per QMI handle. Lookups and advertised services remain in lists and are replayed after QRTR net reset. Lookup results are dynamically allocated and freed on `DEL_SERVER`, `BYE`, net reset, or release. Transactions live from `qmi_txn_init()` until wait/cancel. There is no file persistence.

## Dependencies and Integration Points

The file depends on QRTR sockets, kernel networking, IDR, mutexes, completions, ordered workqueues, QMI codec functions, and `qmi_ops`/`qmi_msg_handler` definitions. It is used by QMI clients/servers such as the protection-domain mapper and remote service consumers.

## Risks and Edge Cases

`qmi_handle_release()` assumes `qmi->sock` is valid and dereferences it before locking. Transaction wait/cancel removes the IDR entry while receive dispatch may already hold the transaction lock; the locking is intentional but requires callers not to free transaction storage before wait/cancel returns. `qmi_add_lookup()` and `qmi_add_server()` do not deduplicate registrations. Receive buffer size is caller-controlled plus header, so undersized values can still decode-fail. On ENETRESET, callbacks are invoked while service lists are being rebuilt; client callbacks must tolerate reorder and loss.

## Test Signals

Tests should cover socket creation failure and `-EAFNOSUPPORT`, lookup/server registration replay after net reset, transaction success, timeout and cancel, unexpected response ids, malformed short packets, raw `msg_handler` override, all QRTR control packet types, concurrent send and release, QMI handler decode failures, and service callback allocation failures.
