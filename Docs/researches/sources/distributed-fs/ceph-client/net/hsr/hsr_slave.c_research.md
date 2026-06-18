## sources/distributed-fs/ceph-client/net/hsr/hsr_slave.c

Purpose: manages HSR/PRP slave/interlink ports and the RX handler installed on lower devices. It validates candidate netdevices, registers/unregisters the receive hook, links slaves under the HSR master, updates MTU/features, and forwards accepted frames into the HSR forwarding engine.

Important APIs/types/functions: `hsr_handle_frame()` is the registered `rx_handler`. It drops loopback/self-originated frames, rejects invalid DAN ingress protocols through `proto_ops->invalid_dan_ingress_frame`, prepares MAC/network headers for HSR/PRP, then calls `hsr_forward_skb()`, with `seqnr_lock` held for interlink ingress. `hsr_invalid_dan_ingress_frame()` accepts only HSR/PRP protocols for DAN ingress. `hsr_port_exists()`, `hsr_add_port()`, and `hsr_del_port()` are the external port-management API. Internals include `hsr_check_dev_ok()` and `hsr_portdev_setup()`.

Control flow and state: add-port allocates `struct hsr_port`, records original MAC, appends to the RCU port list, then for non-master ports sets promiscuity when forwarding is not offloaded, links the lower device as an upper/lower relationship, installs the RX handler, disables LRO, and updates master features/MTU. Deletion removes the RCU list entry, unregisters RX handler, reverses promiscuity and upper links, restores PRP slave B MAC when needed, and frees by `kfree_rcu()`.

Dependencies and integration points: depends on netdevice RX handlers, RTNL upper-device links, LAG upper info, VLAN checks, `hsr_device`, `hsr_forward`, and frame registry helpers. Offload is signaled by `NETIF_F_HW_HSR_TAG_RM` and `hsr->fwd_offloaded`.

Risks: skb manipulation assumes MAC header validity after explicit checks; malformed or short packets must be rejected before HSR tag access. Promiscuity and upper-device rollback must stay balanced across setup failures. Interlink forwarding serializes sequence allocation with a spinlock, making deadlock and lock ordering important around forwarding paths.

Test signals: enslave rejection tests for loopback, VLAN, existing HSR slaves, HSR masters, and non-bridgeable devices; RX tests for self-frame drop, invalid protocol pass-through, hardware tag removal, PRP SAN frames, and interlink sequence handling; teardown tests for promiscuity and MAC restoration.
