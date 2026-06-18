## sources/distributed-fs/ceph-client/tools/testing/selftests/net/netfilter/conntrack_sctp_collision.sh

Purpose: reproduces an SCTP collision scenario where simultaneous INIT exchanges and delayed INIT ACKs can interact badly with nf_conntrack state handling.

Important APIs and tools: sources `lib.sh`, uses three namespaces, veth topology, IPv4 forwarding, `tc htb` and `netem delay`, iptables state match, SCTP module/sysctls, and compiled `./sctp_collision`.

Control flow: `setup()` creates SERVER, ROUTER, and CLIENT namespaces with routed veth links. It adds a `tc` filter on the server side matching SCTP INIT ACK-like traffic and delays it by 1200 ms, installs router iptables rules to drop INVALID/UNTRACKED forwarded packets and input SCTP, loads SCTP, and lowers client `net.sctp.association_max_retrans`. `do_test()` starts the helper server in the server namespace and runs the client helper from the client namespace. Cleanup kills helper processes and removes namespaces.

State and persistence: temporary namespaces, qdiscs, iptables rules, and SCTP sysctl changes inside namespaces. Dependencies include SCTP, `tc` netem, iptables state match, and helper binary. Risks include fragile byte-offset filter matching, timing dependence, and missing netem causing skip. Test signal is helper success followed by `PASS!` and exit status.
