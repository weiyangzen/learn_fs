# sources/distributed-fs/ceph-client/tools/testing/selftests/landlock/scoped_abstract_unix_test.c

## Purpose

`scoped_abstract_unix_test.c` validates `LANDLOCK_SCOPE_ABSTRACT_UNIX_SOCKET`. It tests abstract UNIX stream and datagram communication across parent, child, and grandchild domains, contrasts scoped domains with unrelated filesystem-only domains, verifies audit logging, and proves pathname and unnamed UNIX sockets are not incorrectly governed by abstract-socket scoping.

## Important APIs, Types, and Functions

The file uses `create_scoped_domain()` from `scoped_common.h`, `create_fs_domain()` for non-scope control domains, `set_unix_address()`, `send_fd()`/`recv_fd()`, AF_UNIX `socket()`, `bind()`, `listen()`, `connect()`, `accept()`, `send()`, `sendto()`, `socketpair()`, pipes, fork/wait, and audit helpers. It includes both `scoped_base_variants.h` and `scoped_multiple_domain_variants.h`.

## Control Flow and State

Tests build deterministic abstract addresses, create server sockets in parent or child domains, synchronize process ordering with pipes, and assert whether domain ancestry allows connection or datagram sends. Additional fixtures test sockets created in one domain and used in another via FD passing, pathname sockets under `TMP_DIR`, connected datagram sockets after later scoping, and inherited self-bound datagram sockets. State includes socket creator domain, process domain, connected datagram peer state, abstract socket names, and audit counters.

## Dependencies and Integration Points

It depends on Landlock's scoped-domain checks in UNIX socket connect/send paths, kselftest helpers, audit filtering, temporary directory cleanup, and common Landlock socket fixture helpers.

## Risks and Test Signals

Risks include confusing process domain with socket creation domain, over-blocking pathname or unnamed sockets, allowing unconnected datagram sends out of scope, and audit path encoding drift for abstract socket names. Success signals include `EPERM` only for out-of-scope abstract operations, data bytes arriving on allowed streams/datagrams, correct FD-passing behavior, and audit regex matches for `scope.abstract_unix_socket`.
