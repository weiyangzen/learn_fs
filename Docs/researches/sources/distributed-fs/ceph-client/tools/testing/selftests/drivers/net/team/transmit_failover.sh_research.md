# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/team/transmit_failover.sh

## Purpose
Tests basic transmit failover controlled by the per-port `enabled` team option without teamd. It covers broadcast, roundrobin, and random modes over two veth links between namespaces.

## Important APIs, Types, And Functions
Uses `teamnl setoption/getoption`, `setup_team()` and traffic helpers from `team_lib.sh`, namespace helpers from `net/lib.sh`, plus `iperf3` and `tcpdump`. Main functions are `environment_create()`, `team_test_mode_failover()`, and `team_test_failover()`.

## Control Flow
Setup creates namespaces, two veth pairs, two team devices, and configures the receiving team in roundrobin. For each sender mode, it configures sender team mode/address, starts traffic, verifies both links receive when enabled, disables `eth1` through `teamnl`, verifies only `eth0` receives, re-enables `eth1`, and verifies both links receive again.

## State And Persistence
All network state is namespace-local and cleaned by `cleanup_all_ns`. The sender process is tracked by `team_lib.sh`.

## Dependencies And Integration Points
Requires team driver modes broadcast/roundrobin/random, `teamnl`, veth, namespace support, iperf3, tcpdump, and the net forwarding library.

## Risks
The test intentionally excludes activebackup and loadbalance because `enabled` alone is insufficient. Packet distribution checks assume enough traffic over a one-second capture to observe both links.

## Test Signals
Per-mode `log_test` success means disabled links stop receiving and enabled links resume. `slowwait` confirmation of the option value is a key synchronization signal.
