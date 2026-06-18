# sources/distributed-fs/ceph-client/samples/pktgen/pktgen_sample01_simple.sh

## Purpose

This shell sample configures Linux pktgen for a single transmit thread and one network device. It demonstrates the smallest useful pktgen setup: parse common parameters, require a destination MAC, default the destination IP, randomize UDP source ports, and start `/proc/net/pktgen/pgctrl`.

## Important APIs, Types, and Functions

The script depends on `functions.sh` for `root_check_run_with_sudo`, `trap_exit`, `pg_ctrl`, `pg_thread`, `pg_set`, address parsing, and validation. `parameters.sh` supplies `DEV`, `DEST_IP`, `DST_MAC`, `COUNT`, `PKT_SIZE`, `DELAY`, `APPEND`, `IP6`, `DST_PORT`, and `UDP_CSUM`. The local `print_result()` reads `/proc/net/pktgen/$DEV`.

## Control Flow

After privilege escalation and parameter parsing, defaults are filled, destination address and optional UDP destination port are parsed, and pktgen state is reset unless `APPEND` is set. Thread 0 is cleared and given `$DEV`; the device receives count, clone, packet size, delay, no timestamping, destination MAC/IP range, optional destination-port randomization, UDP checksum, and random UDP source port range. If not appending, it starts pktgen and prints device results.

## State and Persistence Behavior

State is external to the script and lives under `/proc/net/pktgen`: thread device membership and device generator attributes persist until reset or rewritten. `APPEND` intentionally avoids reset so multiple scripts can compose a run.

## Dependencies and Integration Points

It requires root, pktgen support loaded in the running kernel, a usable transmit interface, a valid neighbor/receiver MAC, and the companion pktgen helper scripts.

## Risks and Edge Cases

Missing `DST_MAC` is fatal. `COUNT=0` can run forever. `clone_skb` can defeat per-packet randomness. Bad IP/port values should be caught by helper validators, but invalid interface names or unavailable pktgen files fail at write time.

## Test Signals

Run with a test interface and `-m` destination MAC, then inspect `/proc/net/pktgen/$DEV`, packet counters, and receiver captures. `APPEND=1` should configure without starting.
