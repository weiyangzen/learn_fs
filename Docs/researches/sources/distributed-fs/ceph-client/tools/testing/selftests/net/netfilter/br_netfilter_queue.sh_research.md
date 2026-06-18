## sources/distributed-fs/ceph-client/tools/testing/selftests/net/netfilter/br_netfilter_queue.sh

Purpose: tests bridge netfilter interaction with nft queue verdicting and conntrack flushing under broadcast ICMP load, again using kernel taint as a crash/BUG signal.

Important APIs and tools: uses `unshare -n`, namespace helpers, bridge and veth setup, `modprobe br_netfilter`, bridge netfilter sysctl, nft queue rule with `queue num 0 bypass`, compiled `./nf_queue`, `conntrack -F`, `ping -f -b`, and `/proc/self/net/netfilter/nfnetlink_queue`.

Control flow: top-level re-execs itself in a fresh network namespace. It creates a root bridge plus four port namespaces, verifies unicast pings, installs an nft forward-chain rule that queues ICMP and counts new conntrack states, starts `nf_queue -t 5`, waits until queue 0 appears, then concurrently flushes conntrack while sending flood broadcast pings. Finally it checks that the global kernel taint value remains zero.

State and persistence: namespace and queue state are temporary; cleanup deletes all named netns. Dependencies include nfnetlink_queue support, nft, conntrack, bridge netfilter, and the helper binary. Risks include races around queue readiness, flood sensitivity, and reliance on host taint being clean before start. Test signal is PASS/ERROR plus exit status.
