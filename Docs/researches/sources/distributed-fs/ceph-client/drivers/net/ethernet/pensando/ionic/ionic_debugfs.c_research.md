# sources/distributed-fs/ceph-client/drivers/net/ethernet/pensando/ionic/ionic_debugfs.c

Purpose: Creates debugfs inspection trees for Ionic devices, LIFs, queues, completions, interrupts, notify blocks, and RX filters when `CONFIG_DEBUG_FS` is enabled.

Important APIs and flow: `ionic_debugfs_create()` creates the global `ionic` directory; `ionic_debugfs_add_dev()` creates a per-PCI-device directory; `ionic_debugfs_add_ident()` and `ionic_debugfs_add_sizes()` expose identity and queue/interrupt sizing. `ionic_debugfs_add_lif()` adds LIF netdev and filter views. `ionic_debugfs_add_qcq()` builds per-queue directories with queue/CQ physical addresses, sizes, head/tail show files, descriptor blobs, SG blobs, interrupt register sets, and notify block status. Delete helpers remove device, LIF, and QCQ subtrees.

State and persistence: Stores debugfs dentries in `ionic->dentry`, `lif->dentry`, and `qcq->dentry`. Blob and regset wrappers are devm allocations tied to the device lifetime, while files point directly at live queue/CQ/register memory.

Dependencies and integration: Depends on debugfs, seq_file, PCI/netdev naming through `ionic_bus_info()`, LIF queue/filter structures, and register definitions. Called throughout PCI and LIF allocation/reconfiguration paths.

Risks and test signals: Debugfs files expose live structures without strong lifetime pinning beyond subtree removal, so teardown/reconfiguration ordering matters. `ionic_debugfs_add_qcq()` can return after partial creation on allocation failure. Test with debugfs enabled/disabled, queue reconfiguration, reset recovery, concurrent reads during remove, filter list locking, and descriptor blob sizes for SG and non-SG queues.
