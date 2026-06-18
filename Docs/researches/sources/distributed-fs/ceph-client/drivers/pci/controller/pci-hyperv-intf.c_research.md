## sources/distributed-fs/ceph-client/drivers/pci/controller/pci-hyperv-intf.c

Purpose: Small exported interface layer between generic PCI users and the Hyper-V PCI frontend. It provides callback indirection for block configuration reads, writes, and invalidation registration.

Important APIs, types, and functions: global `struct hyperv_pci_block_ops hvpci_block_ops` is exported GPL so the Hyper-V PCI frontend can populate operations. `hyperv_read_cfg_blk()` calls `hvpci_block_ops.read_block` if present. `hyperv_write_cfg_blk()` calls `write_block`. `hyperv_reg_block_invalidate()` calls `reg_blk_invalidate`. All wrappers return `-EOPNOTSUPP` when the relevant callback is absent. All wrapper functions are exported GPL.

Control flow: clients call the exported helpers; helpers dispatch through the global ops table. There is no probe path.

State and persistence: state is the global function-pointer table only, populated by another module/driver at runtime. No persistent storage exists.

Dependencies and integration points: Hyper-V headers, PCI device pointers, module export infrastructure, and whichever Hyper-V PCI frontend owns `hvpci_block_ops` initialization.

Risks: The global ops table has no explicit locking here, so writers and callers must rely on module load/unload ordering or external synchronization. A missing callback produces feature-not-supported behavior. The helper layer does not validate buffer lengths beyond forwarding them.

Test signals: symbol export resolution, calls before frontend registration returning `-EOPNOTSUPP`, successful read/write/invalidate callback dispatch after registration, and module unload ordering safety.
