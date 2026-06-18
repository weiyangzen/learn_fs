## sources/distributed-fs/ceph-client/tools/testing/selftests/net/netfilter/br_netfilter.sh

Purpose: regression stress for legacy `br_netfilter` plus connection tracking when broadcast/multicast packets are cloned through bridge and IP netfilter paths. It also checks that the kernel taint flag remains unchanged.

Important APIs and tools: sources netfilter `lib.sh`, requires `nft`, uses `/proc/sys/kernel/tainted`, `modprobe br_netfilter`, `ip` bridge/veth/macvlan setup, bridge sysctl `net.bridge.bridge-nf-call-iptables`, nftables bridge and IP rules, and broadcast pings.

Control flow: skips if the kernel is already tainted. It creates five namespaces with one bridge namespace, four veth peers, a bridge, a macvlan on the bridge, and a macvlan on a non-bridge veth enslaved to the bridge. It enables bridge netfilter and conntrack, loads rules that accept new conntrack state in IP input and drop broadcast ICMP in bridge forward, then verifies unicast connectivity and repeated broadcast pings from multiple ingress paths. It ends by re-reading taint state and dumping dmesg on taint.

State and persistence: all namespace/link/ruleset state is temporary and cleaned by `cleanup_all_ns`. Dependencies include bridge, macvlan, br_netfilter, nftables bridge family, and root. Risks include flood-ping timing, slow-machine packet count reduction still being load-sensitive, and false skips on pre-tainted kernels. Test signals are PASS/ERROR lines and final `ret`.
