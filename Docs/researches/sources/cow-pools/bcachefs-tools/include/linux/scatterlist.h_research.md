# File Research: sources/cow-pools/bcachefs-tools/include/linux/scatterlist.h

Defines the minimal scatter-gather list structure and helpers used by kernel-origin code. `page_link` stores page pointers plus low-bit chain/end flags; helpers set pages/buffers, walk chained lists, mark list ends, initialize tables, and return virtual addresses.

The implementation assumes `struct page` is a userspace pointer abstraction from the page/slab compatibility layer and checks low-bit page alignment before tagging.
