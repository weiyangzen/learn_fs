# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/team/team_lib.sh

## Purpose
Shared library for team driver traffic tests. It provides team setup, iperf3 traffic generation, tcpdump capture, packet counting, and “no traffic” checks used by failover and teamd active-backup tests.

## Important APIs, Types, And Functions
It sources `net/forwarding/lib.sh` with `NUM_NETIFS=0` and `REQUIRE_MZ=no`. Key helpers are `setup_team()`, `start_listening_and_sending()`, `stop_sending_and_listening()`, `save_tcpdump_outputs()`, `clear_tcpdump_outputs()`, `did_interface_receive()`, and `check_no_traffic()`. It relies on globals supplied by callers, especially `NS1`, `NS2`, `NS2_IP`, and `NODAD`.

## Control Flow
`setup_team()` detaches members, removes an existing address, brings the team down, sets the team mode via `teamnl`, enslaves members, brings the team up, and assigns the IP address. Traffic helpers start an iperf3 server in `NS2`, verify reachability, then run a long-lived sender in `NS1`. Capture helpers start/stop tcpdump per interface and grep for packets toward the configured destination port.

## State And Persistence
The only global mutable state is `sender_pid`, used to terminate the background iperf3 client. Temporary tcpdump files are managed by forwarding-library helpers.

## Dependencies And Integration Points
Requires `teamnl`, `iperf3`, `tcpdump`, network namespaces, and the forwarding test library. It is meant to be sourced, not executed standalone.

## Risks
The helpers assume a single concurrent sender and fixed TCP port `43434`. Packet counting is based on tcpdump text output and can be sensitive to timing, output format, and background process cleanup.

## Test Signals
Consumers use packet presence or absence on specific member interfaces to validate team mode behavior. `setup_team()` return codes and `slowwait` reachability checks are early failure signals.
