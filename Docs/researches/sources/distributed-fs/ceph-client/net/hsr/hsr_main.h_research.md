## sources/distributed-fs/ceph-client/net/hsr/hsr_main.h

Purpose: private shared definitions for the HSR/PRP driver. It defines IEC 62439-3 timing constants, HSR/PRP wire structures, core private state, port iteration helpers, protocol-operation hooks, and inline helpers used by frame forwarding, supervision, node registration, netlink, and slave setup code.

Important APIs/types/functions: `struct hsr_priv` is the central per-master object, carrying the RCU-protected port list, node databases, proxy node database, self-node pointer, announce/prune timers, HSR/PRP version, sequence counters, locks, protocol operations, PRP net id, offload and RedBox state, supervision multicast address, and optional debugfs root. `struct hsr_port` links a netdev into an HSR master as master/slave/interlink and stores the original MAC for restoration. `struct hsr_proto_ops` abstracts HSRv0, HSRv1, and PRPv1 differences for supervision, duplicate-drop, tagging, ingress validation, and frame registration. Wire helpers include `set_hsr_tag_path`, `set_hsr_tag_LSDU_size`, `set_hsr_stag_path`, `set_hsr_stag_HSR_ver`, `set_prp_lan_id`, `set_prp_LSDU_size`, `hsr_get_skb_sequence_nr`, `skb_get_PRP_rct`, `prp_get_skb_sequence_nr`, and `prp_check_lsdu_size`.

Control flow and state: this header does not execute large flows itself, but it establishes the data passed between RX handlers, forwarding, frame registration, timers, and netlink. Sequence number state is protected by `seqnr_lock`; node and port lists are RCU/list based with `list_lock` for node mutations. PRP frame validation relies on the trailer at `skb_tail_pointer(skb) - HSR_HLEN` and checks the suffix against `ETH_P_PRP`.

Dependencies and integration points: depends on Linux netdevice, VLAN, list, if_hsr UAPI, skb, RCU, timers, debugfs, and endian helpers. Its structs are consumed by `hsr_slave.c`, `hsr_netlink.c`, device setup, forwarding, frame registry, and debugfs modules.

Risks: most inline wire helpers assume callers have already validated skb layout and protocol. Miscomputed LSDU size or path bits can break duplicate detection or interop. `skb_get_PRP_rct()` trusts tailroom size; callers must ensure PRP-suffixed skbs are long enough. RCU callers must use the matching port iteration/read-side locking pattern.

Test signals: KUnit PRP duplicate-discard tests exercise sequence-related state derived from these definitions. Runtime validation comes from HSR/PRP link creation, supervision frames, duplicate handling, RedBox/proxy handling, and debugfs/node netlink visibility.
