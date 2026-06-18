# sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb4/l2t.h

Purpose: declares the Layer-2 table state machine, entry structure, skb ARP error callback storage, and exported L2T APIs for cxgb4 offload paths.

Important APIs/types: `VLAN_NONE`, `L2T_SIZE`, L2T state enum, `struct l2t_entry`, `arp_err_handler_t`, `struct l2t_skb_cb`, `L2T_SKB_CB`, `t4_set_arp_err_handler`, and prototypes for L2T lookup/send/release/update/switching allocation/init/debugfs support.

Control flow/state: the enum defines runtime states from valid/stale/resolving/sync-write to switching and unused. `struct l2t_entry` combines hash-chain node, bucket head, neighbor pointer, ARP queue, refcount, VLAN, lport, MAC address, and lock.

Dependencies/integration: includes spinlock, Ethernet, atomic, skb, neighbor, and net_device types. ULDs use the API to hold L2 entries and send queued offload packets.

Risks: `skb->cb` is reused for ARP error handling, so callers must not conflict with other skb control-block users. State values below `L2T_STATE_SWITCHING` are treated as hashed entries by implementation logic.

Test signals: compile coverage for ULD callers, skb control-block handler invocation, state transition tests, and debugfs file operation registration.
