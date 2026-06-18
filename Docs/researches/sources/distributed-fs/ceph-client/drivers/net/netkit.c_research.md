# sources/distributed-fs/ceph-client/drivers/net/netkit.c

Purpose: implements the `netkit` rtnl link type, a BPF-programmable virtual network device that can run as a paired device or single device and supports BPF multi-program attachment, queue leasing, XSK delegation, and peer forwarding.

Important APIs/types/functions: `struct netkit` stores peer RCU pointer, active BPF multi-program entry, policy, scrub mode, bundle, mode, pairing, primary flag, and headroom. `netkit_xmit()` is the fast path. `netkit_new_link()`, `netkit_del_link()`, `netkit_change_link()`, and `netkit_fill_info()` implement rtnl behavior. `netkit_prog_attach()`, `netkit_prog_detach()`, `netkit_prog_query()`, and `netkit_link_attach()` expose BPF attach/link APIs.

Control flow: transmit validates peer/up state, prepares skb for cross-netns forwarding, sets peer packet type/device, runs attached BPF programs until PASS/DROP/REDIRECT/NEXT, then injects into peer with `__netif_rx()`, redirects, or drops with stats. Newlink parses mode, pairing, policies, scrub, peer info, headroom/tailroom, creates/registers a peer when paired, initializes bundles, sets carrier, and links peers by RCU. BPF attach/detach/update operates under RTNL, updates active entries with RCU synchronization, and commits multi-program changes. Uninit releases all programs/links and unleases queues.

State and persistence: all state is netdev private and volatile. BPF programs are refcounted or held through `bpf_link`; active entry pointers are RCU-protected. Queue leases are stored in netdev RX queue lease pointers.

Dependencies and integration: uses rtnl link ops, BPF mprog/link APIs, TCX action compatibility, netdev queue leasing, XDP socket delegation, netdevice notifier for physical-device unregister, netfilter egress skip, and standard netdev stats/features.

Risks: peer lifetime, unregister batching, and queue leases require careful RTNL/RCU ordering. Only primary paired devices can be management targets for BPF APIs. Single mode disallows peer-specific attributes and enables XSK support differently. BPF return codes must stay ABI-compatible with TCX.

Test signals: create paired and single devices, attach multiple BPF programs and links with replace/relative/revision flags, update/detach links, change policies, forward/drop/redirect traffic, lease queues to physical devices, test XSK setup/wakeup, unregister leased physical devices, and dump rtnl attributes.
