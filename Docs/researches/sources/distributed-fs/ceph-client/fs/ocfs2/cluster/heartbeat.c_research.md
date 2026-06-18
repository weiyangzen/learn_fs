# sources/distributed-fs/ceph-client/fs/ocfs2/cluster/heartbeat.c

## Purpose
`heartbeat.c` implements O2CB disk heartbeat. It exposes heartbeat regions through configfs, starts one kernel thread per region, writes this node’s slot to a shared block device, reads peer slots, derives live-node membership, fires ordered callbacks, tracks global-heartbeat quorum regions, and fences via quorum on heartbeat write timeouts.

## Important APIs, types, and functions
Main structures are `struct o2hb_region`, `struct o2hb_disk_slot`, `struct o2hb_node_event`, `struct o2hb_callback_func`, and `struct o2hb_bio_wait_ctxt`. Public APIs include `o2hb_init`, `o2hb_exit`, `o2hb_alloc_hb_set`, `o2hb_free_hb_set`, `o2hb_setup_callback`, `o2hb_register_callback`, `o2hb_unregister_callback`, `o2hb_fill_node_map`, `o2hb_check_node_heartbeating_no_sem`, `o2hb_check_node_heartbeating_from_callback`, `o2hb_stop_all_regions`, `o2hb_get_all_regions`, and `o2hb_global_heartbeat_active`.

## Control flow
Userspace creates a heartbeat configfs item, sets `block_bytes`, `start_block`, and `blocks`, then writes a block-device fd to `dev`. That commit path opens the block device, verifies sector size, allocates slot pages, reads baseline slot data, registers timeout work, starts `o2hb_thread`, and waits for steady iterations. Each heartbeat loop reads configured/live slots, validates peer CRCs, checks this node’s previous slot for overwrite/generation mismatch, prepares and writes this node’s slot, updates membership through `o2hb_check_slot`, and arms write/negotiation timeouts after steady state. Drop-item stops the thread, clears global-region bitmaps, wakes startup waiters, and releases the config item.

## State and persistence behavior
Persistent state lives on shared disk in `struct o2hb_disk_heartbeat_block` slots: sequence time, node number, CRC, generation, and dead timeout. Runtime global state includes live-node lists/bitmap, all-region list, live/quorum/failed region bitmaps, callback lists, debugfs buffers, heartbeat mode, dead threshold, and dependent-user pin counts. Region state includes block device file, task pointer, slot buffers, generation, timeout work, negotiation bitmap/key, and debugfs entries.

## Dependencies and integration points
It depends on configfs, block bio I/O, kthreads, delayed work, debugfs, CRC32, random generation values, O2CB networking for timeout negotiation messages, nodemanager for node identity/config dependencies, and quorum for self-fencing. O2NET and DLM register callbacks for node up/down events.

## Risks and test signals
Risks include false fencing on slow I/O, missed node transitions due to CRC/generation edge cases, configfs lifetime races while startup waits, mismatched dead thresholds across nodes, global-heartbeat region pin leaks, bio allocation under GFP_ATOMIC, and unsafe unclean stops. Test signals include local and global heartbeat modes, region creation/removal during startup, slow or failed heartbeat writes, all-nodes-hung negotiation, duplicate node slot detection, generation rollover/restart, callback priority ordering, debugfs bitmap reads, dependent-user pin/unpin, and quorum-region cut-off behavior.
