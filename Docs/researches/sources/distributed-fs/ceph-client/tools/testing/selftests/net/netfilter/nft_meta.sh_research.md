<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/netfilter/nft_meta.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/netfilter/nft_meta.sh

## Purpose
This kselftest validates nftables `meta` matches on loopback traffic in an isolated network namespace. It checks ingress and egress interface identity, interface names, interface groups, interface types, protocol family, L4 protocol, packet mark, socket UID/GID, CPU, and time-window matches.

## Important APIs, Types, And Functions
The script uses `nft`, `ip netns`, `ping -m`, `taskset`, `date`, and shell helpers `cleanup()`, `check_one_counter()`, and `check_lo_counters()`. The central nftables API surface is `meta iif`, `iifname`, `iifgroup`, `iiftype`, `oif`, `oifname`, `oifgroup`, `oiftype`, `nfproto`, `l4proto`, `mark`, `skuid`, `skgid`, `cpu`, and `time`.

## Control Flow
It creates one namespace, brings up loopback, loads an `inet filter` table with named counters, verifies zero counters, sends a marked loopback ping, and checks expected packet counts. It then pins the shell to CPU 0, resets nft counters, sends another ping, and confirms the CPU meta counter increments.

## State, Persistence, And Dependencies
State is limited to a temporary netns, loopback address, nftables ruleset, process CPU affinity, and counters. The cleanup trap deletes the namespace. The test depends on nftables meta expression support, `iproute2`, `ping`, `taskset`, and root privileges.

## Integration Points
This is a focused nftables meta-expression regression test in the netfilter selftest suite. It exercises both input and output hook paths and validates that loopback packets produce the expected two hook observations.

## Risks
The CPU test assumes `taskset -p 01 $$` causes the packet-processing path to see CPU 0, which may be sensitive to scheduler and namespace behavior. Time matching depends on system date and nftables time parser support. The cleanup path assumes namespace creation succeeded.

## Test Signals
PASS output reports expected meta counters and CPU counter behavior. Failure signals are mismatched named counters, nft ruleset load failures, missing `nft`, and nonzero exit status.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/netfilter/nft_meta.sh -->
