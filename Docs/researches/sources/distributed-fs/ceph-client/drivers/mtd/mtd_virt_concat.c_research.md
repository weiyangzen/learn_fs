# sources/distributed-fs/ceph-client/drivers/mtd/mtd_virt_concat.c

Purpose: device-tree-driven virtual concatenation layer. It discovers partitions linked by the `part-concat-next` phandle property, withholds component partitions from normal registration, creates a concatenated MTD once all components are available, and restores individual partitions when a concat is destroyed.

Important APIs/types/functions: `struct mtd_virt_concat_node`, `mtd_virt_concat_node_create()`, `mtd_virt_concat_add()`, `mtd_virt_concat_create_join()`, `mtd_virt_concat_destroy()`, `mtd_virt_concat_destroy_joins()`, `mtd_virt_concat_destroy_items()`. It depends on OF node iteration/phandle refs, global `concat_node_list`, `mtd_concat_create()`, `add_mtd_device()`, `del_mtd_device()`, and partition locking from `mtdcore`.

Control flow: node discovery finds available nodes with `part-concat-next`, skips nodes already part of another concat, counts linked phandles plus the defining node, allocates an item and concat container, and stores node references. As partitions are allocated, `mtd_virt_concat_add()` captures matching MTD pointers instead of registering them individually. Join creation waits until all subdevices are present, builds a hyphenated name with `"concat"` suffix, creates an `mtd_concat`, copies parent device identity from the first subdevice, and registers the concat. Destroy unregisters concat, releases subdevice refs, re-adds remaining child MTDs when needed, and drops OF refs.

State and persistence: global list entries hold OF node refs, subdevice pointers, counts, and concat metadata. Persistent data is unchanged; only the visible MTD topology changes.

Risks and test signals: name allocation and duplicate detection are delicate. `mtd_virt_concat_destroy_joins()` dereferences `item->concat` before its null check. Tests should cover phandle chains, duplicate membership, missing component devices, re-creation with same name, destroy-on-component removal, OF ref balancing, and restoration of individual partitions.
