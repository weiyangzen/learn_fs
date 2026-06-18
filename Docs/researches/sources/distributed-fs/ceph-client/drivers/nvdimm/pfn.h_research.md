# sources/distributed-fs/ceph-client/drivers/nvdimm/pfn.h

Purpose: Defines the on-media PFN/DAX info-block format used to describe fsdax/devdax namespace metadata, alignment, data offset, and vmemmap placement.

Important APIs and types: `PFN_SIG` and `DAX_SIG` identify PFN and DAX superblocks. `struct nd_pfn_sb` stores signature, UUID, parent namespace UUID, version fields, `dataoff`, `npfns`, mode, legacy `start_pad`, `end_trunc`, alignment, page size, struct page size, padding, and checksum.

State and persistence behavior: This structure is written to the namespace info-block area at offset `SZ_4K` by `pfn_devs.c` and later validated on probe. Fields are little-endian and constitute persistent ABI; version-minor handling in implementation supplies defaults for older records.

Dependencies and integration points: Included by PFN, DAX, and PMEM code plus testing code that needs the exact layout. It depends on kernel integer and memory zone definitions.

Risks and test signals: Layout compatibility is critical because the structure is on-media metadata. Tests should validate checksums, older minor versions, endianness, signature matching, parent UUID matching, and that `sizeof(struct nd_pfn_sb)` remains compatible with the expected info-block area.
