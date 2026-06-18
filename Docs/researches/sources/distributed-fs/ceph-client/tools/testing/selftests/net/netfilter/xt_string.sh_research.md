<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/netfilter/xt_string.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/netfilter/xt_string.sh

## Purpose
This test validates the xtables `string` match offset semantics for Boyer-Moore and KMP algorithms, including payload before/inside/outside `--from` and `--to` bounds and patterns spanning fragmentation boundaries.

## Important APIs, Types, And Functions
It uses `lib.sh`, `iptables`, `socat`, `ip netns`, dummy devices, and helpers `add_rule()`, `showrules()`, `zerorules()`, `countrule()`, and `send()`. The tested API is `iptables -m string --string ... --algo bm|kmp --from --to`.

## Control Flow
The script creates a namespace with a dummy interface and four OUTPUT rules: bm/kmp over ranges 1000-1500 and 1400-1600. `send()` creates UDP payloads with the pattern at specified absolute packet offsets. Each phase zeroes counters, sends one or more packets, counts rules with expected packet counters, and decrements `rc` on mismatch.

## State, Persistence, And Dependencies
State includes one namespace, dummy link, iptables OUTPUT rules/counters, and a temporary payload file. Cleanup deletes the namespace and temp file. It depends on iptables string match support and `socat`.

## Integration Points
This is legacy xtables coverage rather than nftables coverage. It is useful for regression testing text-search behavior in netfilter, especially boundary handling when payload spans fragments.

## Risks
The test assumes IPv4+UDP header length of 28 bytes and depends on generated packet sizes creating the intended offsets/fragments. Counter parsing relies on iptables `-v -S` including `-c` counters. It uses negative return count values for failures, which are shell-exit-code wrapped.

## Test Signals
Success prints `PASS: string match tests`. Failures name the offset/range scenario and dump matching rules with counters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/netfilter/xt_string.sh -->
