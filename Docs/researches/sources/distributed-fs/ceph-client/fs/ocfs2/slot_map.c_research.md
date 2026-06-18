# sources/distributed-fs/ceph-client/fs/ocfs2/slot_map.c

## Purpose
`slot_map.c` manages the OCFS2 slot map, which assigns mounted cluster nodes to filesystem slots. Slots select per-node system files such as journals and local quota files, so the slot map is a core mount/unmount and recovery coordination structure.

## Important APIs, types, and functions
The file defines private `struct ocfs2_slot` and flexible `struct ocfs2_slot_info`. Public functions are `ocfs2_init_slot_info`, `ocfs2_free_slot_info`, `ocfs2_find_slot`, `ocfs2_put_slot`, `ocfs2_refresh_slot_info`, `ocfs2_node_num_to_slot`, `ocfs2_slot_to_node_num_locked`, and `ocfs2_clear_slot`. Internal helpers update old and extended on-disk formats, validate slot-map blocks, map slot-map buffers through the extent map, and write slot changes back to disk.

## Control flow
Mount initialization allocates slot info sized to `max_slots`, opens the slot-map system inode, computes the required physical size for old or extended format, maps and reads each backing block, then stores the structure on the superblock. `ocfs2_find_slot` refreshes in-memory state from disk, reuses an existing slot for the node if present or chooses the preferred/first free slot, updates `osb->slot_num`, and writes the corresponding disk block. `ocfs2_put_slot` refreshes the map, invalidates the node's slot on disk, resets `slot_num`, and frees slot info. `ocfs2_refresh_slot_info` rereads all mapped blocks, relying on super-lock callers to have serialized disk updates.

## State and persistence
Persistent state is the slot-map system file, either an old array of 16-bit node numbers or an extended array with valid bits and 32-bit node numbers. Runtime state is `osb->slot_info`, cached buffer heads, `si_slots[]`, `si_blocks`, format flag, and `osb->slot_num`. Updates are protected by `osb_lock` locally and written through `ocfs2_write_block`.

## Dependencies and integration points
It depends on system-file lookup, extent mapping, buffer-head I/O, heartbeat/mount coordination, superblock locking, and OCFS2 disk format helpers. Slot numbers feed journal selection, local quota file selection, recovery, and node-to-slot lookups elsewhere in OCFS2.

## Risks and test signals
Risks include stale slot data if refresh is skipped, lost slot invalidation on write failure, old-format truncation of large node numbers, insufficient slot-map file size, and mount races when a node finds its previous slot still allocated. Test signals include mount/unmount across multiple nodes, preferred slot reuse, no-free-slot behavior, extended slot-map files, slot clear during recovery, write failure rollback of `osb->slot_num`, and validation of bad slot-map block numbers.
