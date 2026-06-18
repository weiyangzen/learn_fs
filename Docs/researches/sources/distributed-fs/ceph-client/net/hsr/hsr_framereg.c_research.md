<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/hsr/hsr_framereg.c -->
# sources/distributed-fs/ceph-client/net/hsr/hsr_framereg.c

## Purpose
Maintains HSR/PRP node databases, self-node recognition, proxy node state, duplicate-discard sequence tracking, supervision-frame node merging, address substitution, node pruning, and node data export.

## APIs, Types, and Functions
Implements `hsr_addr_is_redbox()`, `hsr_addr_is_self()`, `hsr_is_node_in_db()`, `hsr_create_self_node()`, `hsr_del_self_node()`, `hsr_del_nodes()`, `prp_handle_san_frame()`, `hsr_get_node()`, `prp_update_san_info()`, `hsr_get_seq_block()`, `hsr_handle_sup_frame()`, `hsr_addr_subst_source()`, `hsr_addr_subst_dest()`, `hsr_register_frame_in()`, `hsr_register_frame_out()`, `prp_register_frame_out()`, `hsr_prune_nodes()`, `hsr_prune_proxy_nodes()`, `hsr_get_next_node()`, and `hsr_get_node_data()`.

## Control Flow, State, and Persistence
Nodes are looked up by MAC A or B in RCU lists and created on first valid traffic. Each node records MAC A/B, AddrB port, ingress timestamps per port, stale flags, SAN flags, removed state, an XArray of sequence blocks, and a fixed backing buffer of sparse sequence bitmaps. Duplicate discard maps sequence numbers into 128-entry blocks, expires old blocks, reuses a bounded ring of blocks, and sets bits per outgoing port or PRP master path; failure to allocate or validate errs toward accepting frames. Supervision handling can merge a node first seen by MAC B into the real MAC A node, copy newer timestamps, OR sequence bitmaps, set AddrB port, and remove the duplicate node with RCU freeing. Prune timers detect ring errors from slave timing skew, emit netlink ring/nodedown events, remove old node/proxy entries, and restart themselves. State persists in `hsr_priv->self_node`, `node_db`, `proxy_node_db`, and each `hsr_node` until pruned or device teardown.

## Dependencies and Integration
Depends on HSR/PRP header parsing helpers, RCU lists, spinlocks, XArray, timers, netlink notification helpers, skb MAC headers, and protocol callbacks from `hsr_device.c`. KUnit visibility exposes sequence block lookup and PRP registration behavior.

## Risks and Test Signals
Risks include RCU/list removal races, bounded sequence block reuse accepting duplicates, sequence port count mismatch, jiffies wrap/stale handling, supervision skb pull/push correctness, node merge races, and ring-error false positives. Test signals include self-node replacement/removal, node creation from HSR/PRP/SAN traffic, duplicate discard across block boundaries and expiry, PRP master duplicate discard, supervision merge with RedBox TLV, address substitution, prune nodedown/ringerror events, proxy pruning, and node data export.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/hsr/hsr_framereg.c -->
