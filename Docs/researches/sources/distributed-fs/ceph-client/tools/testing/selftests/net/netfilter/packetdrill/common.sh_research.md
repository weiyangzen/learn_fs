<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/netfilter/packetdrill/common.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/netfilter/packetdrill/common.sh

## Purpose
This common shell fragment normalizes network stack settings for netfilter packetdrill tests. It reduces timing variance, enables conntrack, and configures TCP defaults expected by packetdrill scenarios.

## Important APIs, Types, And Functions
It directly invokes `modprobe nf_conntrack`, `sysctl`, `ip tcp_metrics flush`, `tc qdisc`, and `$xtables`. It expects the caller to define `xtables` as the iptables command to use.

## Control Flow
The file runs commands at source time: loads conntrack, enables invalid logging, flushes TCP metrics, adjusts TCP rmem/wmem, sets cubic congestion control, disables slow start after idle and ECN, sets `tcp_notsent_lowat`, replaces the `tun0` qdisc with `pfifo`, and appends an INPUT conntrack match rule for TCP SYNs.

## State, Persistence, And Dependencies
This fragment mutates global or namespace sysctls, qdisc state on `tun0`, TCP metrics, module state, and iptables rules. There is no cleanup in this file; callers must run it in disposable namespaces or restore state.

## Integration Points
It is shared setup for packetdrill-based netfilter tests and links packetdrill traffic to conntrack/iptables visibility. The `$xtables` hook allows callers to choose legacy or nft-backed iptables tooling.

## Risks
Because it executes immediately and has no guards around all commands, missing `tun0`, missing `$xtables`, or permission problems can break callers. Sysctl changes may leak when not run inside a test namespace. The qdisc replacement is intentionally chosen to avoid FQ pacing but assumes packetdrill timing needs.

## Test Signals
The file itself emits no PASS/FAIL output. Downstream signals are reduced packetdrill timing flakes and conntrack-enabled packet traces; setup errors surface as command failures in the caller.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/netfilter/packetdrill/common.sh -->
