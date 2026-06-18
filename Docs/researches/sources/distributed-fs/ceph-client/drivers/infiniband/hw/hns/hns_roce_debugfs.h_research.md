# sources/distributed-fs/ceph-client/drivers/infiniband/hw/hns/hns_roce_debugfs.h

Purpose: Declares debugfs wrapper structures and lifecycle functions for HNS RoCE diagnostics.

Important APIs/types/functions: `struct hns_debugfs_seqfile` stores a seq read callback and data pointer. `struct hns_sw_stat_debugfs` groups the software-stat root and seqfile. `struct hns_roce_dev_debugfs` is embedded in `hns_roce_dev` and stores the per-device root plus software-stat subtree. Public functions initialize/cleanup module debugfs and register/unregister a device.

Control flow: The header does not implement flow; it provides the device-embedded state consumed by `hns_roce_debugfs.c` and main device lifecycle code.

State and persistence: The structures model debugfs dentries that persist for device/module lifetime and are removed recursively on cleanup.

Dependencies and integration: Forward declares `struct hns_roce_dev` and relies on Linux debugfs/seq_file types through implementation includes. It is included by `hns_roce_device.h`.

Risks: Dentry lifetime must match device lifetime to avoid dangling private data in seqfile callbacks. Test signals include build coverage, open/read while device removal is serialized, and cleanup idempotence.
