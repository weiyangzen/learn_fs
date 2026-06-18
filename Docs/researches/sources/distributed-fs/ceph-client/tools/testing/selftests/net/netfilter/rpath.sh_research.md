<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/netfilter/rpath.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/netfilter/rpath.sh

## Purpose
This test validates reverse-path filtering matches in iptables/ip6tables and nftables. It checks that martian traffic fails rpfilter/fib reverse-path matches while regular traffic passes, both before and after putting an interface into a VRF.

## Important APIs, Types, And Functions
The script uses `lib.sh`, `iptables` or `iptables-legacy`, `ip6tables` or legacy, `nft`, `ip netns`, `ping`, veth/dummy/VRF devices, and helpers `die()`, `ipt_zero_rule()`, `ipt_zero_reverse_rule()`, `nft_zero_rule()`, `netns_ping()`, `clear_counters()`, and `testrun()`. nft coverage uses `fib saddr . iif oif exists`.

## Control Flow
It chooses available firewall tools, creates two namespaces, configures normal veth-connected addresses and martian addresses where ns2 routes return traffic via a dummy device, installs rpfilter/inverted rules, and adds static IPv6 neighbors. `testrun()` clears counters, sends martian pings that should fail, verifies only inverted rpfilter rules match, then sends regular pings and verifies normal rules match. It repeats after enslaving veth to a VRF in ns2.

## State, Persistence, And Dependencies
State includes namespaces, veth/dummy/VRF devices, IPv4/IPv6 addresses, static neighbors, raw-table iptables rules, and nft rules. Cleanup removes namespaces. The test can run with any of iptables, ip6tables, or nft present, but full coverage requires all.

## Integration Points
It bridges legacy xtables `rpfilter` behavior and nftables FIB expression behavior, including VRF routing semantics. It is a regression test for source validation in netfilter prerouting.

## Risks
Tool availability changes coverage. Counter parsing depends on iptables `-vS` and nft chain output formats. VRF support may be unavailable, and static neighbor setup assumes predictable veth MAC parsing.

## Test Signals
Success prints `PASS: netfilter reverse path match works as intended`. Failures identify whether martian or regular traffic matched incorrectly for iptables, ip6tables, or nft, and exit immediately.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/netfilter/rpath.sh -->
