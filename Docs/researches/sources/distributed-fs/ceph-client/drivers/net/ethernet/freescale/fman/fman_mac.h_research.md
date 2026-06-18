# sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/fman/fman_mac.h

## Purpose

`fman_mac.h` defines the shared MAC-layer contract for FMan MAC implementations. It provides Ethernet address helpers, pause/PFC constants, MAC exception enums, hash-list support, callback typedefs, and the initialization parameter structure used by dTSEC and mEMAC backends.

## Important APIs, Types, And Functions

Important types are `enet_addr_t`, `enum fman_mac_exceptions`, `struct fman_mac_params`, `struct eth_hash_entry`, and `struct eth_hash_t`. The address conversion macros `ENET_ADDR_TO_UINT64()` and `MAKE_ENET_ADDR_FROM_UINT64()` normalize 48-bit MAC addresses into the representation used by the backends. Inline helpers `dequeue_addr_from_hash_entry()`, `free_hash_table()`, and `alloc_hash_table()` implement the software hash table backing multicast/unicast filter programming.

## Control Flow

MAC implementations allocate hash tables with `alloc_hash_table()`, add/remove `eth_hash_entry` nodes as hardware hash bits are changed, and call `free_hash_table()` from their cleanup paths. Exception callbacks point back to the generic MAC device layer, allowing backend interrupt handlers to report MAC-specific events.

## State And Persistence Behavior

The hash table stores lists of dynamically allocated entries per hardware bucket so drivers can leave a hardware hash bit enabled while multiple addresses collide in the same bucket. The header itself does not persist state, but its inline cleanup owns freeing all list entries and bucket arrays.

## Dependencies And Integration Points

The header includes `fman.h`, Linux slab, PHY, and Ethernet headers. It is shared by `fman_dtsec.c`, `fman_memac.c`, and their small public headers. It also depends on local allocation helper macros such as `kmalloc_obj()` and `kmalloc_objs()` being available from the wider tree.

## Risks And Edge Cases

`ETH_HASH_ENTRY_OBJ` uses `hlist_entry_safe` even though `struct eth_hash_entry::node` is a `struct list_head`; this is suspicious and should be validated against local macro definitions or compilation. Hash helper functions are inline in the header, so bugs replicate into every MAC backend. The exception enum merges 1G, 10G, mEMAC, and timestamp events, requiring each backend to reject unsupported values cleanly.

## Test Signals

Build all MAC backends to catch list helper type mismatches. Exercise hash allocation failure, freeing partially populated tables, bucket collision removal, and unsupported exception mappings in dTSEC and mEMAC.
