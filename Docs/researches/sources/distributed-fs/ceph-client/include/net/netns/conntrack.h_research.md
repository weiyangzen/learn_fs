# sources/distributed-fs/ceph-client/include/net/netns/conntrack.h

Purpose: Defines per-network-namespace conntrack protocol timeout/configuration state and conntrack subsystem controls.

Important APIs/types/functions: Protocol structs include `nf_generic_net`, `nf_tcp_net`, `nf_udp_net`, `nf_icmp_net`, optional `nf_sctp_net`, and optional `nf_gre_net`. `nf_ip_net` groups per-protocol settings. `struct netns_ct` stores event/work flags, sysctl booleans, per-cpu stats, event notifier RCU pointer, protocol config, and optional label usage count.

Control flow: Conntrack initialization fills timeouts and sysctls per namespace; packet tracking consults protocol-specific arrays; sysctl writes update behavior; event delivery reads `nf_conntrack_event_cb`; flowtable uses offload timeouts when enabled.

State and persistence: Runtime per-net state, including per-cpu stats and RCU notifier pointer. No durable persistence.

Dependencies/integration: Depends on nf_conntrack protocol definitions, TCP/SCTP/GRE config options, seqlocks/list_nulls/workqueues, labels, events, sysctl, and flowtable.

Risks/test signals: Test timeout sysctls per namespace, notifier RCU teardown, label counter, event work pending flag, flowtable offload timeout config, and protocol config option combinations.
