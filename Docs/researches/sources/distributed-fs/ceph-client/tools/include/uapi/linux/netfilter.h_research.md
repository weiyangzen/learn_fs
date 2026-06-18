# sources/distributed-fs/ceph-client/tools/include/uapi/linux/netfilter.h

Purpose: defines core netfilter verdicts, hook numbers, protocol-family identifiers, and address union used by userspace netfilter APIs and kernel-facing UAPI structures.

Important APIs/types: verdict constants include `NF_DROP`, `NF_ACCEPT`, `NF_STOLEN`, `NF_QUEUE`, `NF_REPEAT`, and deprecated `NF_STOP`. Macros encode queue numbers and drop errno values into verdict high bits (`NF_QUEUE_NR`, `NF_DROP_ERR`). Hook enums define IPv4/IPv6/inet pre-routing, local-in, forward, local-out, post-routing, ingress, and netdev ingress/egress. Protocol IDs include inet, IPv4, ARP, netdev, bridge, IPv6, and legacy DECnet for userspace. `union nf_inet_addr` stores IPv4/IPv6 addresses.

Control flow, state, and persistence: netfilter hooks return encoded verdicts that direct packet traversal, queueing, dropping, repeating, or accepting. Userspace APIs such as nfnetlink/nftables use these constants to define rules and verdict expressions. Rulesets persist in kernel tables until replaced/deleted; verdicts are per packet.

Dependencies and integration points: depends on types, compiler, IPv4, and IPv6 headers. Integrates nftables/iptables, nfqueue, conntrack/NAT, bridge and netdev packet paths.

Risks and test signals: risks include errno encoding mistakes, queue-number truncation to 16 bits, relying on deprecated `NF_STOP`, and hook-family mismatch. Tests should install nftables/iptables rules for accept/drop/queue/repeat-like behavior, verify NFQUEUE numbers and drop errors, and exercise inet/bridge/netdev hook families.
