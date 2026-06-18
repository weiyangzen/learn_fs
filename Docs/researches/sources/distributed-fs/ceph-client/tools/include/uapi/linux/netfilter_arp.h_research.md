# sources/distributed-fs/ceph-client/tools/include/uapi/linux/netfilter_arp.h

Purpose: defines ARP-specific netfilter protocol and hook constants for userspace compatibility with ARP filtering.

Important APIs/types: `NF_ARP` is the pseudo protocol family value because there is no `PF_ARP`. Hook constants are `NF_ARP_IN`, `NF_ARP_OUT`, and `NF_ARP_FORWARD`; userspace also sees `NF_ARP_NUMHOOKS`.

Control flow, state, and persistence: ARP packets traverse the ARP netfilter hooks and rules return core netfilter verdicts from `netfilter.h`. Persistent state is the configured ARP filtering ruleset, not this header.

Dependencies and integration points: includes `netfilter.h`. Integrates arptables/nftables ARP-family rules, bridge/ARP filtering paths, and legacy tooling that expects these hook numbers.

Risks and test signals: risks are assuming ARP has a normal socket protocol family, mixing ARP hook numbers with IPv4/inet hooks, and relying on legacy arptables behavior without nftables compatibility testing. Tests should install ARP input/output/forward rules, verify ARP request/reply filtering, and compare legacy arptables and nftables ARP-family behavior.
