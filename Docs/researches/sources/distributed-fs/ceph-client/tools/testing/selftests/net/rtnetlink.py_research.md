<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/rtnetlink.py -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/rtnetlink.py

## Purpose

`rtnetlink.py` is a focused Python kselftest for rtnetlink multicast-address dumping. It verifies that at least one interface reports the IPv4 all-hosts multicast address.

## Important APIs, Types, and Functions

The file imports `ksft_exit`, `ksft_run`, `ksft_ge`, and `RtnlAddrFamily` from `lib.py`, plus `socket`. `IPV4_ALL_HOSTS_MULTICAST` is the byte string `224.0.0.1`. `dump_mcaddr_check` calls `rtnl.getmulticast({"ifa-family": socket.AF_INET}, dump=True)`, filters returned entries whose `multicast` field equals the all-hosts address, and asserts the count is at least one. `main` constructs `RtnlAddrFamily`, runs the check, and exits through kselftest helpers.

## Control Flow

Execution is linear: create rtnetlink family wrapper, run one check under `ksft_run`, then report via `ksft_exit`. Failures are represented through kselftest assertion helpers rather than manual exceptions.

## State and Persistence Behavior

The test does not mutate system state. It opens netlink state through the helper object and inspects the current namespace's multicast address table.

## Dependencies, Integration Points, Risks, and Test Signals

Dependencies include the selftests Python rtnetlink library, rtnetlink multicast dump support, IPv4, and at least loopback or another interface with all-hosts multicast membership. Integration is with the netlink address-family dump ABI and the Python kselftest runner. Risks are minimal but include running in an unusual namespace with no IPv4 multicast membership or helper API schema changes. The signal is a passing `ksft_ge(len(all_host_multicasts), 1, ...)` assertion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/rtnetlink.py -->
