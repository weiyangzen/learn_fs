## sources/distributed-fs/ceph-client/mm/hugetlb_vmemmap.h

Purpose: declares the HugeTLB vmemmap optimization interface and computes how much vmemmap memory can be optimized for each HugeTLB hstate.

Important APIs and types: the header exposes restore and optimize entry points for single folios and folio lists, bootmem-specific optimize/init hooks, `HUGETLB_VMEMMAP_RESERVE_SIZE`, `HUGETLB_VMEMMAP_RESERVE_PAGES`, `hugetlb_vmemmap_size()`, `hugetlb_vmemmap_optimizable_size()`, and `hugetlb_vmemmap_optimizable()`. When `CONFIG_HUGETLB_PAGE_OPTIMIZE_VMEMMAP` is disabled, inline stubs preserve call-site simplicity.

Control flow: callers can use the functions unconditionally. Enabled builds route into `hugetlb_vmemmap.c`; disabled builds return success or no-op, with `hugetlb_vmemmap_restore_folios()` moving input folios to the non-HVO list through `list_splice_init()`.

State and persistence: the header owns no state. It defines policy constants: one vmemmap page is reserved and the rest may be deduplicated when `sizeof(struct page)` is power-of-two and the HugeTLB vmemmap footprint exceeds the reserve.

Dependencies and integration: includes HugeTLB, IO, and memblock headers because the implementation spans HugeTLB metadata, boot memory, and sparse vmemmap setup. Integration points are HugeTLB free/alloc paths and sparsemem preinit code.

Risks and test signals: the main risks are arithmetic assumptions around `sizeof(struct page)` and call sites incorrectly assuming optimization exists in disabled builds. Tests should cover configs with and without `CONFIG_HUGETLB_PAGE_OPTIMIZE_VMEMMAP`, tiny hstates whose vmemmap is not optimizable, and list-restore behavior when optimization is compiled out.
