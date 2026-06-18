# sources/distributed-fs/ceph-client/drivers/nvdimm/pfn_devs.c

Purpose: Implements libnvdimm PFN device creation, sysfs configuration, persistent PFN/DAX info-block validation, and `dev_pagemap` setup for fsdax/devdax namespaces.

Important APIs and flow: Sysfs attributes configure `mode`, `align`, `uuid`, and claimed `namespace`, and expose resource, size, and supported alignments. `nd_pfn_create()` creates seed PFN devices for memory regions. `nd_pfn_probe()` detects existing PFN info blocks on namespaces and registers PFN devices. `nd_pfn_validate()` reads the info block, checks signature, checksum, parent UUID, mode, page/struct-page compatibility, alignment, padding, and bounds. `nvdimm_setup_pfn()` initializes or validates the info block, clears metadata badblocks, and fills `struct dev_pagemap`.

State and persistence behavior: The key persistent state is `struct nd_pfn_sb` stored at namespace offset `SZ_4K`. New initialization computes `dataoff`, `npfns`, `end_trunc`, `align`, page-size metadata, and checksum before `nvdimm_write_bytes()`. Runtime state includes `nd_pfn->mode`, `align`, `uuid`, `ndns`, `pfn_sb`, `npfns`, and the region PFN ida.

Dependencies and integration points: Depends on namespace claim helpers, libnvdimm bus locking, `nvdimm_read_bytes()`/`nvdimm_write_bytes()`, badblocks, `memremap_compat_align()`, hugepage alignment availability, devdax detection, `dev_pagemap`, vmem altmap, and KMSAN page-struct override behavior.

Risks and test signals: This file gates DAX correctness. High-risk cases include legacy `start_pad`, namespace alignment changes, struct page size mismatch, insufficient namespace capacity, badblock clearing in metadata space, and partial device allocation failure. Tests should cover PFN_MODE_RAM versus PFN_MODE_PMEM, existing valid and corrupt info blocks, read-only regions, small namespaces, DAX alignment rejection, and page-struct override configurations.
