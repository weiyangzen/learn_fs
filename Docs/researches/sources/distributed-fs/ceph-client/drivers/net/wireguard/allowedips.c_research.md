# sources/distributed-fs/ceph-client/drivers/net/wireguard/allowedips.c

## Purpose
`allowedips.c` implements WireGuard's allowed-IPs routing table. It stores IPv4 and IPv6 CIDR prefixes in compressed binary tries, maps prefixes to peers, supports longest-prefix lookup for source/destination packet validation/routing, and maintains peer-owned lists for efficient removal.

## Important APIs, Types, And Functions
The public functions are `wg_allowedips_init()`, `wg_allowedips_free()`, `wg_allowedips_insert_v4()`, `wg_allowedips_insert_v6()`, `wg_allowedips_remove_v4()`, `wg_allowedips_remove_v6()`, `wg_allowedips_remove_by_peer()`, `wg_allowedips_read_node()`, `wg_allowedips_lookup_dst()`, `wg_allowedips_lookup_src()`, `wg_allowedips_slab_init()`, and `wg_allowedips_slab_uninit()`. Core internals include `swap_endian()`, `copy_and_assign_cidr()`, `choose()`, `common_bits()`, `prefix_matches()`, `find_node()`, `lookup()`, `node_placement()`, `add()`, `remove_node()`, and `remove()`.

## Control Flow
Insert operations increment the table sequence, convert network-order addresses into trie-order aligned keys, then call `add()` under the caller-provided mutex. `add()` handles empty trie creation, exact prefix replacement/list move, direct child insertion, or intermediate parent creation based on common prefix length. Lookup converts the packet address, enters RCU read-side critical section, finds the best matching node, and returns a strong peer reference with retry if the peer is being torn down. Removal finds the exact node for a peer, clears its peer pointer/list entry, collapses nodes with zero or one child where possible, and defers freeing via RCU. Full table free detaches roots, removes all peer-list entries, and schedules RCU traversal/free of the old roots.

## State And Persistence
The table contains two RCU roots (`root4`, `root6`) and a sequence counter. Each node stores peer pointer, two child pointers, prefix metadata, packed parent pointer/bit, and either peer-list membership or RCU head. Nodes come from a module slab cache. No durable persistence exists; WireGuard netlink configuration repopulates this state at runtime.

## Dependencies And Integration Points
This file integrates with `struct wg_peer` reference counting and `allowedips_list`, skb IP/IPv6 headers, RCU BH read-side locking, caller-held mutexes for mutation, kernel slab caches, and the optional included `selftest/allowedips.c` under debug.

## Risks
Pointer-bit packing depends on alignment; the header explicitly aligns `struct allowedips` for m68k. Mutations require the correct mutex; misuse can corrupt parent links or peer lists. Prefix comparison uses endian-swapped aligned buffers and casts to u32/u64, so alignment assumptions are important. `MAX_ALLOWEDIPS_DEPTH` bounds stack traversal; debug warns on overflow, but trie invariants should keep depth within IPv6 prefix length plus root.

## Test Signals
Use the built-in allowedips selftest under DEBUG, plus tests for overlapping prefixes, exact replacement, peer removal, IPv4/IPv6 longest-prefix lookup, source and destination lookup reference handling, RCU free after table reset, and sequence-number changes on every mutation.
