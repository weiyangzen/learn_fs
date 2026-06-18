<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/netlink-dumps.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/netlink-dumps.c

## Purpose
This kselftest harness validates robustness of netlink dump error handling, extended ACK parsing, and socket close behavior while generic-netlink dumps are in progress or referenced by mqueue notification state.

## Important APIs, Types, And Functions
Key pieces are `struct ext_ack`, `enum get_ea_ret`, `nl_get_extack()`, static malformed request blobs `dump_neigh_bad` and `dump_policies`, and tests `dump_extack`, `test_sanity`, `close_in_progress`, and `close_with_ref`. It uses `NETLINK_ROUTE`, `NETLINK_GENERIC`, `SOL_NETLINK` options `NETLINK_CAP_ACK`, `NETLINK_EXT_ACK`, `NETLINK_GET_STRICT_CHK`, generic netlink control commands, POSIX mqueue syscalls, and `kselftest_harness.h`.

## Control Flow
`dump_extack` opens a route netlink socket with strict/extack options, sends many invalid neighbor dump requests to overflow receive buffers, observes `ENOBUFS`, then parses subsequent messages to ensure extack data reports `EINVAL` and the expected bad attribute offset. `test_sanity` proves the policy dump spans more than one message. `close_in_progress` closes a socket after starting a generic-netlink policy dump. `close_with_ref` adds a message-queue notification reference to the netlink socket before closing it.

## State, Persistence, And Dependencies
State is limited to sockets, receive buffers, and a POSIX message queue named `sed` created via syscall. There is no explicit unlink in this file. The test depends on netlink strict validation, generic netlink controller policy dumps, YNL attribute helpers, and mqueue support.

## Integration Points
It exercises kernel netlink dump lifecycle and extack reporting from userspace selftests. It integrates low-level raw netlink messages with the kselftest C harness and YNL parsing helpers.

## Risks
The exact extack offset and error sequence are tied to kernel validation behavior. The mqueue object name may persist outside the process if not cleaned by system policy. Buffer-overflow timing around ENOBUFS/EBUSY can vary, though the test tolerates early receive exhaustion after at least 10 replies.

## Test Signals
Assertions validate socket creation, send sizes, ENOBUFS observation, extack presence, `EINVAL`, bad attribute offset, multi-message dumps, and no crash on close paths. Any assertion failure is a kselftest failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/netlink-dumps.c -->
