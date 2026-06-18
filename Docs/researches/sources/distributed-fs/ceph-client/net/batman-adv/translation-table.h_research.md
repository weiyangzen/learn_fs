# sources/distributed-fs/ceph-client/net/batman-adv/translation-table.h

## Purpose
Declares the translation-table API used across batman-adv for client learning, lookup, netlink dumps, route cleanup, AP isolation, roaming checks, MTU resizing, temporary entries, and module cache lifecycle.

## Important APIs And Types
Exports initialization/free functions (`batadv_tt_init`, `batadv_tt_free`, `batadv_tt_cache_init`, `batadv_tt_cache_destroy`), local table operations (`batadv_tt_local_add`, `batadv_tt_local_remove`, `batadv_tt_local_dump`, `batadv_tt_local_commit_changes`, `batadv_tt_local_resize_to_mtu`), global table operations (`batadv_tt_global_dump`, `batadv_tt_global_del_orig`, `batadv_tt_global_hash_find`, `batadv_tt_global_hash_count`, `batadv_tt_add_temporary_global_entry`, `batadv_tt_global_is_isolated`), lookup/policy helpers (`batadv_transtable_search`, `batadv_is_my_client`, `batadv_is_ap_isolated`, roaming checks), and the inline `batadv_tt_global_entry_put` kref release wrapper.

## Control Flow
The only executable code is `batadv_tt_global_entry_put`, which is null-safe and releases the embedded common kref through `batadv_tt_global_entry_release`. The rest of the header defines cross-module contracts for the implementation in `translation-table.c`.

## State And Persistence
The header owns no state. It exposes refcounted `batadv_tt_global_entry` pointers and functions that mutate `bat_priv->tt` in-memory state.

## Dependencies And Integration Points
Includes `main.h`, kref, netdevice, netlink, skb, and types headers. It is included by routing, send, mesh-interface, netlink, originator cleanup, and other modules that need client-to-originator mapping or TT policy decisions.

## Risks
Callers receiving `batadv_tt_global_entry *` from lookup APIs must eventually use `batadv_tt_global_entry_put`; leaking or double-putting these refcounted objects can corrupt global TT state. API users also need to respect VLAN-aware lookups and distinguish local, global, roaming, temporary, and isolated clients.

## Test Signals
Compilation catches declaration drift. Runtime/API tests should pair every global lookup with a put, exercise VLAN-specific lookups, and verify route deletion calls remove matching originator TT entries.
