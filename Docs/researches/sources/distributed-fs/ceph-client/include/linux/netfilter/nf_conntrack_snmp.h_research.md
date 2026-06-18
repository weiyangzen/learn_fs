# sources/distributed-fs/ceph-client/include/linux/netfilter/nf_conntrack_snmp.h

Purpose: Declares the optional SNMP NAT helper hook used to translate embedded addresses in SNMP payloads.

Important APIs, types, and functions: Exports `nf_nat_snmp_hook_fn` and the RCU pointer `nf_nat_snmp_hook`. Detected source surface: 16 lines; includes `linux/netfilter.h`, `linux/skbuff.h`; macros `_NF_CONNTRACK_SNMP_H`; structs `nf_conn`; enums `ip_conntrack_info`; typedefs none; function-like declarations/helpers `nf_nat_snmp_hook_fn`.

Control flow: Conntrack/NAT code checks the hook under RCU and calls it with skb, hook state, direction, and manipulation type when SNMP payload rewriting is needed.

State and persistence behavior: The only state in this header is the global RCU hook pointer; module load/unload controls whether NAT support is active.

Dependencies and integration points: Depends on netfilter hook state and sk_buff. Integrates with the SNMP conntrack/NAT helper implementation.

Risks and test signals: Risks are RCU lifetime bugs and payload rewriting that changes packet checksums incorrectly. Test with NATed SNMP queries/traps and module unload while traffic is active.
