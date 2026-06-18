# sources/distributed-fs/ceph-client/tools/testing/selftests/net/test_neigh.sh

## Purpose
`test_neigh.sh` validates the neighbor table `extern_valid` flag for IPv4 ARP and IPv6 NDISC entries. It checks allowed and rejected flag combinations, state transitions, interface events, and garbage collection survival.

## Important APIs, Types, And Functions
Functions include `run_cmd()`, `setup()`, `exit_cleanup_all()`, `extern_valid_common()`, `extern_valid_ipv4()`, and `extern_valid_ipv6()`. It uses shared `lib.sh` helpers such as `setup_ns`, `cleanup_all_ns`, `check_err`, `check_fail`, and `log_test`. It relies on `ip neigh`, `ip ntable`, `tc`, and `jq`.

## Control Flow
For each address family, the script creates two namespaces connected by a veth, assigns IPv4 and IPv6 addresses, and runs the same `extern_valid_common()` sequence. It adds valid entries, rejects invalid states and incompatible `use` combinations, toggles the flag via replace, combines an existing extern-valid entry with `managed`, tests removal on administrative down and survival across carrier down, forces reachable and stale transitions, then manipulates global neighbor table thresholds to verify survival through forced and periodic garbage collection.

## State, Persistence, And Dependencies
State is temporary namespaces, neighbor entries, tc drop filter on the peer, and global neighbor table threshold/base-reachable settings in the initial namespace. The script saves and restores the modified ntable values. It depends on root, `ip` support for `extern_valid`, `jq`, and tc.

## Integration Points
The test exercises neighbor UAPI validation, neighbor state machine transitions, probing counters, interface event cleanup, and GC protection semantics for externally validated entries.

## Risks
The forced and periodic GC tests modify global thresholds, so interruption before restoration can affect the host. Timing depends on `delay_probe`, retransmit, and GC intervals. The script must run in isolation from other tests using neighbor table thresholds. The final file as read ends after the loop without an explicit summary `exit`, relying on lib status behavior and trap cleanup.

## Test Signals
Passing signals are logged success for add, invalid add/replace rejection, flag replace behavior, managed coexistence, interface-down flush, carrier-down retention, reachable/stale transitions retaining `extern_valid`, nonzero probe count during failed resolution, and survival of extern-valid entries while ordinary stale entries are collected.
