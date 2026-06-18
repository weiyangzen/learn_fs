<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/rxrpc/rxperf.c -->
# sources/distributed-fs/ceph-client/net/rxrpc/rxperf.c

## Purpose
`rxperf.c` implements an in-kernel AF_RXRPC performance test server. It listens on service 147/port 7009, accepts encrypted calls, unmarshals rxperf request parameters, discards or replies with configured byte counts, and supplies test security keys.

## Important APIs, Types, And Functions
Important functions include `rxperf_init()`, `rxperf_exit()`, `rxperf_open_socket()`, `rxperf_close_socket()`, `rxperf_charge_preallocation()`, `rxperf_deliver_to_call()`, `rxperf_extract_data()`, `rxperf_deliver_param_block()`, `rxperf_deliver_request()`, `rxperf_process_call()`, `rxperf_add_rxkad_key()`, and optional `rxperf_add_yfs_rxgk_key()`. It defines `struct rxperf_call`, protocol constants, and rxrpc kernel callbacks.

## Control Flow
Late init creates a workqueue, allocates a server keyring, adds an RxKAD key and optional RxGK enctype keys, opens an AF_RXRPC IPv6 datagram socket, sets minimum security to encrypt, attaches the keyring and notification ops, binds/listens, and precharges accepts. New call notifications replenish preallocation. Per-call work receives a fixed parameter block, validates version and operation, reads size parameters and request data/magic cookie, sets reply length, sends zero-page reply chunks plus terminal magic cookie, waits for final ACK/life check, then shuts down and releases the call. Errors are mapped to rxgen aborts.

## State And Persistence
Global state includes `rxperf_socket`, `rxperf_sec_keyring`, and `rxperf_workqueue`. Each `rxperf_call` tracks rxrpc call pointer, iterator/kvecs, operation, request/reply lengths, state, abort/error fields, service ID, and work item.

## Dependencies And Integration Points
The server uses AF_RXRPC kernel APIs for accept precharge, notifications, receive, send, TX length, abort, shutdown, and put-call. It depends on kernel keyrings, RxKAD/RxGK security modules, Kerberos enctype lookup, workqueues, zero pages, and trace enum definitions.

## Risks And Edge Cases
The module is test-oriented but binds a real service port in `init_net`. Preallocation must free unattached call records on discard/failure. Large requested replies stream zero pages but still exercise socket/call flow control. Shutdown must stop listening before releasing socket and flush the workqueue to avoid call use-after-free.

## Test Signals
Run rxperf send/recv/rpc operations with RxKAD and each configured RxGK enctype, version/opcode mismatch aborts, large request/reply sizes, client aborts, final ACK wait behavior, module unload during active calls, keyring setup failures, and workqueue/preallocation leak checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/rxrpc/rxperf.c -->
