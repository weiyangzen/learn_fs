<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/batman-adv/fragmentation.h -->
# sources/distributed-fs/ceph-client/net/batman-adv/fragmentation.h research

Purpose: declares the fragmentation subsystem API and provides the inline timeout predicate used by originator cleanup code.

Important APIs and types: `batadv_frag_purge_orig()` purges per-originator fragment buffers using an optional predicate; `batadv_frag_skb_fwd()` may forward a fragment without reassembly; `batadv_frag_skb_buffer()` buffers and possibly merges a received fragment; `batadv_frag_send_packet()` fragments and sends an oversized skb. `batadv_frag_check_entry()` tests whether a non-empty chain has exceeded `BATADV_FRAG_TIMEOUT`.

Control flow and state behavior: the header has no storage. Its inline predicate reads `fragment_list` and `timestamp` from `struct batadv_frag_table_entry`, tying the implementation to per-originator fragment state initialized elsewhere in `types.h` and originator setup.

Dependencies and integration: includes `main.h`, kernel list/skbuff types, and depends on `batadv_has_timed_out()` plus fragmentation constants in `main.h`. It is consumed by receive routing, originator purge, and send paths.

Risks: callers must hold the correct chain lock when using timeout checks in contexts where the list can mutate. The API uses pointer-to-pointer skb ownership for buffering, which is easy to misuse if a caller continues to reference a consumed skb.

Test signals: compile with receive/send users, verify timeout purge invokes `batadv_frag_check_entry()`, check caller behavior for merged, buffered, and failed outcomes, and run lockdep around fragment purge while traffic is active.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/batman-adv/fragmentation.h -->
