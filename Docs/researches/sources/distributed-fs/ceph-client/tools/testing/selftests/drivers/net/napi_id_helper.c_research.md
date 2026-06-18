<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/napi_id_helper.c -->
## sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/napi_id_helper.c

Purpose: companion TCP server for `napi_id.py` that validates `SO_INCOMING_NAPI_ID` on an accepted socket.

Important functions/APIs: single `main` uses `getaddrinfo`, `socket`, `setsockopt(SO_REUSEADDR)`, `bind`, `listen`, `ksft_ready`, `accept`, `getsockopt(SO_INCOMING_NAPI_ID)`, `read`, `ksft_wait`, and cleanup closes.

Control flow: resolves bind address/port from argv, starts a listening socket, announces readiness to the Python harness, accepts one client, reads the incoming NAPI ID socket option, drains one read, waits for harness synchronization, and fails if NAPI ID is zero.

State/dependencies: only socket descriptors. Depends on kernel support for `SO_INCOMING_NAPI_ID` and ksft sync helpers. Risks include missing argc validation, returning `-1` for `EAFNOSUPPORT`, and not closing sockets on early errors. Test signals are process exit status and stderr diagnostics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/napi_id_helper.c -->
