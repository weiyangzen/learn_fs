# sources/distributed-fs/ceph-client/fs/afs/cell.c

## Purpose
`cell.c` manages AFS cell records within a network namespace: lookup/allocation, root-cell setup, DNS/VL server refresh, procfs activation, reference and active-use lifetimes, garbage collection, timers, and purge.

## Important APIs, types, and functions
Key public functions are `afs_find_cell()`, `afs_lookup_cell()`, `afs_cell_init()`, `afs_get_cell()`, `afs_put_cell()`, `afs_use_cell()`, `afs_unuse_cell()`, `afs_see_cell()`, `afs_queue_cell()`, `afs_set_cell_timer()`, and `afs_cell_purge()`. Internal helpers include `afs_alloc_cell()`, `afs_update_cell()`, `afs_manage_cell()`, `afs_activate_cell()`, `afs_deactivate_cell()`, and `afs_has_cell_expired()`.

## Control flow
Lookups search the netns rb-tree under `cells_lock`, preallocate a candidate if absent, insert it with RCU rb-linking, optionally queue DNS lookup, and wait for setup unless the caller requested preload/dynroot behavior. The manager work item activates proc entries, refreshes VL server lists from DNS with TTL clamping, transitions cell states, schedules future management, or removes inactive cells by purging servers and root volume references. Purge unpins the workstation cell and waits for outstanding cells to be destroyed.

## State and persistence
Runtime state includes cell rb-tree/proc links, name/key descriptor, VL server list RCU pointer, DNS source/status/expiry/count, state/error, active/ref counts, timers, volumes and file-server trees, alias/root-volume links, anonymous key, and dynroot inode ID.

## Dependencies and integration points
It depends on DNS resolver, address parsing, VL server lists, procfs cell setup, server/volume management, keyring/security, net namespace lifetime, workqueues, timers, RCU, rbtrees, and IDR.

## Risks and test signals
Risks include state-machine races, DNS error classification, TTL clamping, candidate insertion races, use/ref imbalance, root-cell pinning leaks, purge hangs, and procfs list ordering. Test signals include rootcell strings with/without VL addresses, invalid names, concurrent lookups, DNS success/temp/fail/notfound, GC after inactivity, netns teardown purge, and cell reactivation during removal.
