# sources/distributed-fs/ceph-client/fs/ocfs2/slot_map.h

## Purpose
`slot_map.h` declares the OCFS2 slot-map lifecycle and lookup API used by mount, unmount, recovery, and node coordination code.

## Important APIs, types, and functions
The header declares initialization and teardown (`ocfs2_init_slot_info`, `ocfs2_free_slot_info`), slot acquisition/release (`ocfs2_find_slot`, `ocfs2_put_slot`), refresh (`ocfs2_refresh_slot_info`), node/slot translation (`ocfs2_node_num_to_slot`, `ocfs2_slot_to_node_num_locked`), and explicit clearing (`ocfs2_clear_slot`).

## Control flow
Mount code initializes slot info, refreshes or finds a slot, then other subsystems query node-to-slot mappings. Unmount calls `ocfs2_put_slot` to invalidate the disk slot and free cached slot state. Recovery paths can refresh or clear slot records when a node leaves.

## State and persistence
The header owns no state. The implementation persists slot ownership in the slot-map system file and stores the active slot in `struct ocfs2_super`.

## Dependencies and integration points
It depends on `struct ocfs2_super` and is included by OCFS2 superblock, heartbeat, recovery, quota, and journal code that needs slot identity or mapping.

## Risks and test signals
Risks are API misuse around locking: `ocfs2_slot_to_node_num_locked` requires `osb_lock`, while lookup helpers manage locking internally. Test signals include lockdep on lookup paths, mount/unmount lifecycle tests, and recovery tests clearing slots for departed nodes.
