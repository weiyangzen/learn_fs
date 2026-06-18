# sources/distributed-fs/ceph-client/drivers/nvdimm/pmem.c

Purpose: Implements the NVDIMM persistent-memory block and DAX driver. It probes raw PMEM namespaces, PFN-backed namespaces, BTT claims, and DAX claims, then exposes a gendisk and optional DAX host for direct access.

Important APIs and flow: `pmem_submit_bio()` handles `REQ_PREFLUSH`, iterates bio segments, performs direct read/write via `copy_mc_to_kernel()` or `memcpy_flushcache()`, handles badblocks and poison clearing on writes, honors FUA with `nvdimm_flush()`, and ends the bio. DAX operations include `pmem_dax_direct_access()`, `pmem_dax_zero_page_range()`, and `pmem_recovery_write()` for poison recovery. `pmem_attach_disk()` enables the namespace, optionally parses PFN metadata, maps memory via `devm_memremap_pages()` or `devm_memremap()`, initializes badblocks, allocates DAX, adds the disk, and tracks `badblocks` sysfs. `nd_pmem_probe()` chooses BTT, PFN, DAX, or raw PMEM attach.

State and persistence behavior: Runtime `struct pmem_device` stores physical base, data offset, virtual mapping, namespace size, PFN padding, badblocks, DAX device, gendisk, and `dev_pagemap`. Persistent metadata is read through PFN/DAX info blocks and badblock/poison state from the NVDIMM subsystem. Writes use cache-flush copies and explicit region flushes when required.

Dependencies and integration points: Depends on libnvdimm namespace probing, BTT/PFN/DAX helpers, block layer, DAX core, badblocks, memory failure handling, `nvdimm_flush()`, and architecture PMEM flush/copy APIs.

Risks and test signals: Media poison paths must preserve data integrity and update badblocks only after successful recovery. DAX direct access must return accurate good ranges around badblocks. Tests should cover raw/PFN/BTT/DAX probe ordering, write-cache attribute visibility, FUA/prefetch flush failures, memory-failure notification, badblock revalidation, remove/shutdown flush, and fallback when DAX allocation is unsupported.
