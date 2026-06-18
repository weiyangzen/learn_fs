<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/hsr/hsr_debugfs.c -->
# sources/distributed-fs/ceph-client/net/hsr/hsr_debugfs.c

## Purpose
Adds debugfs visibility for HSR/PRP node tables, including node MAC pairs, ingress timestamps, AddrB port, and PRP SAN/DANP classification.

## APIs, Types, and Functions
Defines root dentry `hsr_debugfs_root_dir`, show function `hsr_node_table_show()`, `DEFINE_SHOW_ATTRIBUTE(hsr_node_table)`, and public helpers `hsr_debugfs_rename()`, `hsr_debugfs_init()`, `hsr_debugfs_term()`, `hsr_debugfs_create_root()`, and `hsr_debugfs_remove_root()`.

## Control Flow, State, and Persistence
Root creation makes `/sys/kernel/debug/hsr`. Per HSR device, `hsr_debugfs_init()` creates a directory named after the netdev and a read-only `node_table` file. Reads take RCU, walk `priv->node_db`, skip the self node, and print MAC A, MAC B, last-seen times for slave A/B, AddrB port, and either PRP SAN flags or HSR DAN-H marker. Rename follows netdev name changes by changing the debugfs directory name. Termination removes the per-device subtree, and module exit removes the root. State is debugfs dentries stored in `hsr_priv`.

## Dependencies and Integration
Depends on debugfs, seq_file show helpers, HSR node database structures, RCU list traversal, and self-node detection from `hsr_framereg.c`. It is compiled only when `CONFIG_DEBUG_FS` is enabled.

## Risks and Test Signals
Risks include raw jiffies output being hard to interpret, stale RCU entries during concurrent removal, debugfs creation failures being nonfatal, and rename failure leaving stale directory names. Test signals include debugfs root creation/removal, per-device file creation, node table output for HSR and PRP modes, self-node suppression, and rename on `NETDEV_CHANGENAME`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/hsr/hsr_debugfs.c -->
