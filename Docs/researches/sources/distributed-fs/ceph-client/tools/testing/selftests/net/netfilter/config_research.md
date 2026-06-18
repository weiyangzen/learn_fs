## sources/distributed-fs/ceph-client/tools/testing/selftests/net/netfilter/config

Purpose: kernel configuration fragment documenting/enabling the modules and built-ins required for the netfilter selftest suite.

Important entries: covers audit, BPF syscall, namespaces, bridge/netfilter/ebtables legacy modules, IPv4/IPv6 iptables and raw/filter/nat modules, conntrack zones/events/protocol support, nfnetlink queue, nftables families and expressions (`NFT_CT`, `NFT_FIB`, `NFT_FLOW_OFFLOAD`, `NFT_QUEUE`, NAT/masq/redir/synproxy/tproxy), IPVS, VRF, veth, dummy, macvlan, VLAN, VXLAN, TUN, IPIP, XFRM, SCTP, and traffic control qdiscs/classes used by the tests.

Control flow: no executable logic; it integrates with kselftest/kernel build config tooling. The fragment intentionally mixes built-in and module settings to allow tests to modprobe functionality while keeping core dependencies available.

State and persistence: affects kernel build configuration, not runtime state. Dependencies are Kconfig symbols existing for the target kernel. Risks are configuration drift when tests add features without updating this fragment, and false skips/failures when optional modules are absent. Test signal is indirect: tests should avoid feature-missing skips when run on a kernel built with this config.
