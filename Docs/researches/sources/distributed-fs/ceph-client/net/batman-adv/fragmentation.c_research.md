<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/batman-adv/fragmentation.c -->
# sources/distributed-fs/ceph-client/net/batman-adv/fragmentation.c research

Purpose: implements batman-adv layer-2 fragmentation and reassembly for unicast payloads that exceed next-hop MTU. It fragments outbound skbs, buffers inbound fragments per originator and sequence number, merges complete chains, forwards fragments without merging when the next hop cannot carry the merged payload, and purges stale fragment chains.

Important APIs and functions: public functions are `batadv_frag_purge_orig()`, `batadv_frag_skb_buffer()`, `batadv_frag_skb_fwd()`, and `batadv_frag_send_packet()`. Internal helpers include `batadv_frag_clear_chain()`, `batadv_frag_size_limit()`, `batadv_frag_init_chain()`, `batadv_frag_insert_packet()`, `batadv_frag_merge_packets()`, and `batadv_frag_create()`.

Control flow: outgoing fragmentation computes a max fragment size from the outgoing hard-interface MTU capped by `BATADV_FRAG_MAX_FRAG_SIZE`, refuses packets requiring more than `BATADV_FRAG_MAX_FRAGMENTS`, grabs the primary interface to fill originator address, then splits from the skb tail into numbered `BATADV_UNICAST_FRAG` packets. Incoming buffering linearizes fragments, selects a per-originator bucket by sequence number modulo `BATADV_FRAG_BUFFER_COUNT`, clears any chain with a different sequence number, inserts fragments in descending number order, validates aggregate size and total size consistency, and hands a complete chain to merge. Merge expands the first skb, strips the fragment header, restores the Ethernet header, then appends payloads from remaining fragments.

State and persistence: fragment state lives under each `batadv_orig_node->fragments[]` entry, with a spinlock, hlist, sequence number, timestamp, size, and total size. Stale entries are purged via `batadv_frag_purge_orig()` and `batadv_frag_check_entry()` from the header. State is bounded by buffer count, max fragments, and max total size, and it is purely in memory.

Dependencies and integration: uses `originator` router lookup, `send` helpers, hard-interface primary selection, batman packet UAPI, per-mesh counters, skb allocation/manipulation, jiffies timeouts, and MTU values from the next-hop hard interface. `hard-interface.c` accounts for fragment headers in headroom and MTU calculations.

Risks: skb ownership is strict: failed insert frees the fragment skb, successful buffer sets caller skb to NULL unless merged, and send consumes fragments. Fragment order and `total_size` validation prevent malformed reassembly but duplicate fragment numbers drop the new fragment. GRO frag_list linearization on send can be costly. Forward-without-merge depends on correct next-hop MTU and decrements TTL directly.

Test signals: packets around MTU boundaries, exactly 1 and 16 fragments, over-16 fragment refusal, duplicate and out-of-order fragments, mismatched total sizes, timeout purge, forwarding fragments when merged size exceeds next-hop MTU, skb with frag_list, priority propagation, and stats counters for TX/FWD bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/batman-adv/fragmentation.c -->
