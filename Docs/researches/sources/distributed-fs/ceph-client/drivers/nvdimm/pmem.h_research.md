# sources/distributed-fs/ceph-client/drivers/nvdimm/pmem.h

Purpose: Defines the shared persistent-memory device structure consumed by the PMEM driver and NVDIMM test overrides.

Important APIs and types: `struct pmem_device` records physical address, PFN/DAX data offset, kernel mapping, immutable namespace size, PFN padding, badblocks sysfs node, badblocks state, DAX device, gendisk, and `dev_pagemap`. It declares weak-overridable `__pmem_direct_access()` and wraps `TestClearPageHWPoison()` behind `test_and_clear_pmem_poison()` when memory failure support is enabled.

State and persistence behavior: The structure is runtime state only; it points to persistent media and persistent poison/badblock information managed elsewhere. The `data_offset` and `pfn_pad` fields reflect on-media PFN metadata decisions.

Dependencies and integration points: Depends on page flags, badblocks, memremap, fs types, DAX access mode, and memory failure configuration. `tools/testing/nvdimm` can consume this header and override direct access behavior.

Risks and test signals: Consumers must initialize `bb.dev` before helpers use it indirectly. Build tests should cover `CONFIG_MEMORY_FAILURE` enabled/disabled and NVDIMM test override linkage.
