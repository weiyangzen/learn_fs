# sources/distributed-fs/ceph-client/drivers/net/bonding/bond_debugfs.c

## Purpose
`bond_debugfs.c` provides optional debugfs visibility for bonding, specifically the ALB receive-load-balancing hash table. When debugfs is enabled and network namespaces are not enabled, it creates `/sys/kernel/debug/bonding/<bond>/rlb_hash_table`; otherwise it compiles stub functions so the rest of bonding can call debug hooks unconditionally.

## Important APIs, Types, and Functions
- `bond_debug_rlb_hash_show()` is a seq_file show callback that prints source IP, destination IP, destination MAC, and assigned slave device for each used RLB hash entry.
- `DEFINE_SHOW_ATTRIBUTE(bond_debug_rlb_hash)` builds the file operations.
- `bond_debug_register()`, `bond_debug_unregister()`, and `bond_debug_reregister()` manage per-bond debugfs directories and files.
- `bond_create_debugfs()` and `bond_destroy_debugfs()` manage the top-level `bonding` debugfs directory.
- The `#else` branch defines no-op versions of all public functions when unsupported.

## Control Flow
At bonding module initialization, `bond_create_debugfs()` creates the root directory. Each bond calls register to create a directory named after the bond netdev and a read-only `rlb_hash_table` file. Reading that file checks the bond is in ALB mode, locks `bond->mode_lock`, walks `bond_info->rx_hashtbl_used_head` through `used_next`, and prints assigned client entries. Rename calls attempt `debugfs_change_name()` and fall back to unregistering the old directory on failure. Module cleanup recursively removes the root.

## State and Persistence
The file owns `bonding_debug_root` and each bond stores `bond->debug_dir`. The displayed RLB state is owned by `bond_alb.c`; debugfs only reads it under lock. There is no persistent storage, and debugfs entries disappear on unregister/module exit.

## Dependencies and Integration Points
It depends on `CONFIG_DEBUG_FS`, absence of `CONFIG_NET_NS` for real debugfs support, bonding internals, `bond_alb.h` RLB structures, `seq_file`, and debugfs APIs. It integrates with bonding lifecycle hooks in the main driver.

## Risks
Debugfs is unavailable when network namespaces are enabled, so tooling must tolerate stubs. `debugfs_create_*` failures are not fatal and are only partially reported. The file exposes IPv4 RLB state only; it does not summarize TLB or 802.3ad state. Readers hold `mode_lock` while formatting the table, so very large tables can extend lock hold time.

## Test Signals
Tests should verify root and per-bond directory creation, readable `rlb_hash_table` in ALB mode, empty output in non-ALB modes, correct formatting for assigned and `(none)` clients, safe unregister/reregister, cleanup on module exit, and successful builds with debugfs disabled or netns enabled using the stub functions.
