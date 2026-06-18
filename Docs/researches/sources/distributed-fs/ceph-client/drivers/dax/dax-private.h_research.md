# sources/distributed-fs/ceph-client/drivers/dax/dax-private.h

Purpose: private DAX core header defining in-memory region, mapping, and device objects shared by bus, super, and DAX drivers.

Important APIs/types/functions: `struct dax_region`, `struct dax_mapping`, `struct dev_dax_range`, `struct dev_dax`, `run_dax()`, `to_dev_dax()`, `to_dax_mapping()`, `dax_pgoff_to_phys()`, `inode_dax()`, `dax_inode()`, `dax_bus_init()/exit()`, and `dax_align_valid()`.

Control flow and state: `dax_region` tracks parent range, target node, alignment, IDs, resource tree, seed, and youngest device. `dev_dax` tracks a DAX core object, optional kernel mapping for fsdev, cached size, alignment, target node, pgmap, memmap-on-memory preference, and one or more physical ranges with mapping children. `dax_align_valid()` gates allowed page/PMD/PUD mapping sizes by THP architecture config.

Dependencies and integration: depends on device, cdev, IDR/IDA, THP config, and DAX pseudo-filesystem functions implemented in `super.c`.

Risks and test signals: this is a shared private ABI; field semantics affect sysfs, mmap faults, fs-dax, kmem, and producers. Test alignment validation across PAGE/PMD/PUD configs, dynamic multi-range devices, pgmap lifetime, and conversions between inode/device/dax types.
