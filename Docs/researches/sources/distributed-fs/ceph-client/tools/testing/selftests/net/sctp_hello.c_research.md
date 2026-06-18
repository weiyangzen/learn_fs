<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/sctp_hello.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/sctp_hello.c

## Purpose

`sctp_hello.c` is a small SCTP client/server helper used by `sctp_vrf.sh` to test SCTP listener lookup, VRF binding, and `l3mdev_accept` behavior.

## Important APIs, Types, and Functions

`set_addr` fills `sockaddr_in` or `sockaddr_in6` based on the selected family. `do_client` creates an `SOCK_STREAM` SCTP socket, optionally binds a local source address and port, connects to the server, performs a zero-length receive, and closes. `main` dispatches between server and client modes; server mode optionally sets `SO_BINDTODEVICE`, binds, listens, accepts one client, and exits.

## Control Flow

CLI mode determines execution: `client -4|-6 IP PORT [IP PORT]` or `server -4|-6 IP PORT [IFACE]`. Server setup is blocking at `accept`; client returns success only when `connect` succeeds. The helper is intentionally single-connection and short-lived.

## State and Persistence Behavior

All state is per-process socket state. Optional `SO_BINDTODEVICE` pins the listening SCTP socket to a device or VRF name. No files or kernel configuration are persisted.

## Dependencies and Integration Points

It depends on SCTP kernel support, `IPPROTO_SCTP`, and the `sctp_vrf.sh` topology. It integrates with `ss` polling in the shell script, which waits for the listening socket bound to the expected interface.

## Risks and Edge Cases

Error handling prints simple messages and often returns `-1` without closing already-open sockets on early failures. The zero-length `recv` is a synchronization placeholder rather than data validation. Invalid IPv6 text is not deeply diagnosed.

## Test Signals

The main signal is process exit status under `timeout` in `sctp_vrf.sh`: successful connect/accept is pass for allowed cases, and timeout or connect failure is pass for denied cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/sctp_hello.c -->
