<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/ppp/pppoe.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/ppp/pppoe.sh

## Purpose

`pppoe.sh` verifies PPP over Ethernet operation across a veth pair connecting server and client namespaces. It exercises kernel PPPoE support, userspace `pppoe-server`, the `pppd` PPPoE plugin, and the same IP connectivity path as the async PPP test.

## Important APIs, Types, and Functions

The script sources `ppp_common.sh`, uses `require_command pppoe-server`, `ppp_common_init`, `ppp_test_connectivity`, `modprobe -q pppoe`, and `find /usr/{lib,lib64,lib32}/pppd/ -name pppoe.so`. It creates `veth-server`/`veth-client`, runs `socat` as a `/dev/log` UNIX receiver for PPPoE logs, starts `pppoe-server` with `-I`, `-L`, `-R`, `-N`, `-q`, `-k`, `-O`, and `-g`, and starts client `pppd` with the PPPoE plugin and `nic-<ifname>`.

## Control Flow

After cleanup trap installation, the script checks for `pppoe-server`, initializes namespaces, loads the PPPoE module, and locates the `pppoe.so` plugin. Missing plugin is treated as a kselftest skip. It then creates and moves veth endpoints to the two namespaces, starts a syslog listener, starts the server, starts the client, runs shared connectivity, logs `PPPoE`, and dumps collected syslog payloads if the test failed.

## State and Persistence Behavior

Runtime state includes two namespaces, a veth pair, PPPoE discovery/session state, `pppd` and `pppoe-server` processes, a temporary syslog capture file, and `ppp0` addresses. Cleanup removes namespaces, kills `socat`, and deletes the temporary log file.

## Dependencies, Integration Points, Risks, and Test Signals

Dependencies include root, veth, PPPoE kernel support, `pppoe-server`, `pppd`, a usable `pppoe.so`, `socat`, `iperf3`, and the support file `pppoe-server-options`. Integration points are PPPoE discovery over Ethernet, PPP negotiation, and kselftest logging. Risks include distribution-specific PPP plugin paths, older `pppoe-server` versions ignoring `-g`, missing syslog socket behavior in namespaces, and timing around daemon startup. Signals are PPP address assignment, successful ping and `iperf3`, `log_test "PPPoE"`, and failure diagnostics from the captured PPPoE log.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/ppp/pppoe.sh -->
