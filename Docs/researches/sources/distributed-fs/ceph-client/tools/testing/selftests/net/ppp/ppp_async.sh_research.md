<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/ppp/ppp_async.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/ppp/ppp_async.sh

## Purpose

`ppp_async.sh` verifies PPP async operation over a virtual serial link. It starts a PPP server and client in separate network namespaces connected by two PTYs created by `socat`, then checks IP-level connectivity and throughput.

## Important APIs, Types, and Functions

The script sources `ppp_common.sh`, uses its `ppp_common_init` and `ppp_test_connectivity` helpers, creates `TTY_SERVER` and `TTY_CLIENT` under a temporary directory, loads `ppp_async`, starts `socat -d PTY,... PTY,...`, and runs `pppd` in `NS_SERVER` and `NS_CLIENT`. Cleanup calls `cleanup_all_ns`, kills `SOCAT_PID`, and removes the temporary PTY directory.

## Control Flow

Startup creates PTY symlink paths, installs an EXIT trap, initializes namespaces and tool checks, loads the PPP async module, starts `socat`, waits up to five seconds for the server PTY link, starts the server-side `pppd` with fixed local/remote IPv4 addresses, starts client-side `pppd` with `updetach`, then invokes the shared connectivity test. On success or failure it logs `PPP async` and exits with the shared kselftest status.

## State and Persistence Behavior

Runtime state is temporary network namespaces, PTY symlinks, the `socat` process, `pppd` processes, and kernel PPP devices such as `ppp0`. The EXIT trap removes namespaces and local temporary files.

## Dependencies, Integration Points, Risks, and Test Signals

Dependencies include root privileges, `socat`, `pppd`, `iperf3`, `ip`, `ping`, PPP async kernel support, and namespace support. It integrates with PPP line discipline setup through `pppd` and with kselftest status helpers from `lib.sh`. Risks are PTY creation timing, missing `pppd` plugins, module load failures, and hanging `pppd` sessions. Test signals are client namespace acquiring `192.168.200.2` on `ppp0`, successful pings to `192.168.200.1`, an `iperf3` client/server transfer, and `log_test "PPP async"`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/ppp/ppp_async.sh -->
