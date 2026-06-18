<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/handshake/handshake-test.c -->
# sources/distributed-fs/ceph-client/net/handshake/handshake-test.c

## Purpose
KUnit coverage for the generic handshake request API, focused on allocation validation, submission error handling, request lookup, duplicate submission, cancellation races, and destroy callbacks.

## APIs, Types, and Functions
Defines test callbacks `test_accept_func()`, `test_done_func()`, and `test_destroy_func()`, several test `struct handshake_proto` variants, parameterized allocation cases, and individual KUnit tests for `handshake_req_alloc()`, `handshake_req_submit()`, `handshake_req_hash_lookup()`, `handshake_req_next()`, `handshake_req_cancel()`, `handshake_complete()`, and request destruction.

## Control Flow, State, and Persistence
Allocation tests fuzz invalid protocol descriptors and excessive private size. Submit tests create TCP sockets in `init_net`, sometimes attach files with `sock_alloc_file()`, and assert behavior for NULL request, NULL socket, missing `sock->file`, max pending overflow, successful hash lookup, and duplicate submission returning `-EBUSY`. Cancel tests cover cancellation before accept, after simulated accept via `handshake_req_next()`, and after completion. The destroy test installs a protocol destroy callback, cancels a request, forces file teardown with `__fput_sync()`, and checks that socket destruction released the request. Static `handshake_req_destroy_test` records the destroyed request.

## Dependencies and Integration
Depends on KUnit, exported-for-KUnit handshake internals, kernel socket creation, file-backed sockets, init net namespace, generic-netlink definitions, and `MODULE_IMPORT_NS("EXPORTED_FOR_KUNIT_TESTING")`.

## Risks and Test Signals
Risks include tests mutating `hn_pending` directly, relying on socket/file lifetime details, and not exercising actual generic-netlink ACCEPT/DONE messages. Strong test signals are coverage of invalid proto inputs, one-request-per-socket enforcement, pending cap enforcement, hash lookup, pre/post-accept cancellation, completion-versus-cancel behavior, and destructor callback execution.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/handshake/handshake-test.c -->
