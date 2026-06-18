# sources/distributed-fs/ceph-client/security/landlock/errata/abi-4.h

## Purpose

This ABI errata header documents and registers erratum 1 for Landlock ABI 4: TCP socket identification for network access rights.

## Important APIs, Types, and Functions

The file expands `LANDLOCK_ERRATUM(1)` and documents that non-TCP stream protocols should not be restricted by TCP-specific access rights.

## Control Flow

Included by `errata.h` with ABI 4, it contributes an entry consumed by `setup.c` during `compute_errata()`.

## State and Persistence Behavior

No local runtime state exists; the global errata bitmask records the fix.

## Dependencies and Integration Points

This relates directly to `net.c`, where `hook_socket_bind()` and `hook_socket_connect()` call `sk_is_tcp()` before enforcing `LANDLOCK_ACCESS_NET_BIND_TCP` and `LANDLOCK_ACCESS_NET_CONNECT_TCP`.

## Risks and Test Signals

Without the fix, SMC, MPTCP, SCTP, or other stream protocols could be denied by TCP rules. Test non-TCP stream bind/connect under network rules and verify ABI errata reporting.
