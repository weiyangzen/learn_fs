# sources/distributed-fs/ceph-client/drivers/dax/fsdev.c

Purpose: FS-DAX-compatible dev_dax driver. It exposes dev_dax memory through DAX operations for filesystems rather than device-DAX mmap, using `MEMORY_DEVICE_FS_DAX` and order-0 folios.

Important APIs/types/functions: `fsdev_dax_direct_access()`, `fsdev_dax_zero_page_range()`, `fsdev_dax_recovery_write()`, `fsdev_pagemap_memory_failure()`, `fsdev_clear_folio_state()`, `fsdev_dax_probe()`, and `fsdev_dax_driver`.

Control flow and state: probe builds/validates pgmap, reserves ranges, caches total size, sets FS-DAX pgmap type/ops/owner, maps pages, clears stale compound folio state from previous drivers, computes data offset between pgmap and dev_dax range, adds a minimal cdev, installs DAX operations with `dax_set_ops()`, marks the device alive, and clears ops/folio state on cleanup. Direct-access translates pgoff to phys/kaddr/pfn and returns contiguous page availability clipped by cached size.

Dependencies and integration: depends on DAX core ops/holder failure notification, memremap_pages, fs-dax/iomap users, cdev, page/folio helpers, and DAX bus.

Risks and test signals: stale compound folio state, cached size correctness, range offset calculation, holder failure notification, and no-mmap semantics matter. Test binding after `device_dax`, filesystem `fs_dax_get()`, direct_access bounds, zero-page and recovery-write paths, memory failure notification, dynamic resize rejection while bound, and unbind cleanup.
