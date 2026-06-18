<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/ppp/ppp_common.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/ppp/ppp_common.sh

## Purpose

`ppp_common.sh` provides shared setup and connectivity checks for PPP selftests. It avoids duplicating namespace creation, package checks, address checks, ping, and throughput validation between async PPP and PPPoE tests.

## Important APIs, Types, and Functions

The shared constants are `IP_SERVER=192.168.200.1` and `IP_CLIENT=192.168.200.2`. `ppp_common_init` requires `socat`, `pppd`, and `iperf3`, enforces root, and creates `NS_SERVER` and `NS_CLIENT` via `setup_ns`. `ppp_check_addr` queries IPv4 addresses on a device inside a namespace. `ppp_test_connectivity` waits for `ppp0` to receive the client address, pings the server address, starts an `iperf3` server in server namespace, waits for TCP port 5201, and runs a zero-copy-ish `iperf3 -Z` client transfer.

## Control Flow

Callers source this file, call `ppp_common_init`, create the PPP transport, start their server/client PPP daemons, then call `ppp_test_connectivity`. The helpers use `check_err` to aggregate failures into the common `RET`/`EXIT_STATUS` model from `lib.sh`.

## State and Persistence Behavior

The file stores only shell variables. Runtime state is created by callers and `setup_ns`: namespaces, PPP devices, an `iperf3` daemon, and network addresses. Namespace cleanup is caller-owned through an EXIT trap.

## Dependencies, Integration Points, Risks, and Test Signals

It depends on `../lib.sh`, root privileges, userspace PPP tools, and common network utilities. Integration is with PPP scripts and kselftest status handling. Risks are assuming the PPP interface is named `ppp0`, hard-coded `iperf3` port 5201, and transient failures before `pppd` finishes address negotiation. Signals are successful `slowwait`, zero `ping` exit status, listening `iperf3` server, and successful client throughput.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/ppp/ppp_common.sh -->
