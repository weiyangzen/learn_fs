# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/team/teamd_activebackup.sh

## Purpose
End-to-end teamd active-backup runner test. It verifies that teamd can create two two-port teams in separate namespaces, carry traffic, select an active port, and move active traffic between ports.

## Important APIs, Types, And Functions
The script uses `teamd`, `teamdctl`, `teamnl` indirectly through `team_lib.sh`, `iperf3`, `tcpdump`, `ip netns`, and kselftest net helpers. Local helpers include `teamd_config_create()`, `environment_create()`, `environment_destroy()`, `set_active_port()`, `wait_to_stop_receiving()`, and `teamd_test_active_backup()`.

## Control Flow
It optionally switches to IPv4 with `-4`, otherwise using IPv6. Setup creates two namespaces, two veth pairs, JSON configs for `test_team1` and `test_team2`, starts daemonized teamd instances, brings teams up, assigns addresses, and checks ping. The test starts iperf3 traffic, verifies baseline delivery, forces `eth1` active on both teams, confirms only `eth1` receives, then forces `eth0` active and confirms only `eth0` receives.

## State And Persistence
Temporary config files and teamd PIDs are tracked in globals and removed by `environment_destroy()`. Namespace, veth, and team state is transient. `/var/run/teamd` pid/socket files may be force-removed if graceful shutdown fails.

## Dependencies And Integration Points
Requires root, namespace support, teamd/teamdctl, team driver, veth, iperf3, tcpdump, and shared `team_lib.sh`.

## Risks
Traffic assertions are timing-sensitive and depend on iperf3/tcpdump readiness. `pgrep -f` on config path must identify the right teamd process. Force-kill cleanup must not collide with unrelated same-named teamd instances.

## Test Signals
Pass is a `log_test` for active backup runner behavior. Failures are missing traffic on the active interface, traffic on inactive interface, teamd startup errors, or inability to change `runner.active_port`.
