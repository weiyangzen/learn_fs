# sources/distributed-fs/ceph-client/include/linux/bootmem_info.h

Purpose: Provides memory-hotplug bootmem metadata helpers for tracking memblock-allocated page structures and freeing them correctly when sections or node metadata are released. The header abstracts whether the architecture supports storing bootmem metadata in `page->private`.

Important APIs/types/functions: `enum bootmem_type` identifies `SECTION_INFO`, `MIX_SECTION_INFO`, and `NODE_INFO` metadata, with min/max bounds for hotplug users. With `CONFIG_HAVE_BOOTMEM_INFO_NODE`, APIs include `register_page_bootmem_info_node()`, `register_page_bootmem_memmap()`, `get_page_bootmem()`, and `put_page_bootmem()`. Inline helpers decode low bits of `page->private` with `bootmem_type()` and the shifted info payload with `bootmem_info()`. `free_bootmem_page()` validates a reference count of 2 and only releases section/mixed-section metadata via `put_page_bootmem()`.

Control flow: Memory initialization registers pgdat and memmap pages as bootmem-backed metadata. Hotplug/removal code later checks `page->private`, drops metadata references, and returns eligible reserved pages to the buddy allocator. Without config support, registration is a no-op and `free_bootmem_page()` directly tells kmemleak about the physical page and calls `free_reserved_page()`.

State/persistence: State is encoded in `struct page::private`; low 4 bits are the type and upper bits are the info value. This persists for reserved metadata pages until released. The fallback path carries no encoded metadata.

Dependencies/integration: Depends on core MM, memblock/buddy allocator behavior, kmemleak, `pglist_data`, `struct page`, PFN translation, and memory-hotplug section management.

Risks/test signals: Risks include corrupting `page->private`, freeing a page with the wrong refcount/type, leaking memmap pages, or double-freeing reserved memory when config variants diverge. Test signals include memory hotplug add/remove cycles, sparsemem section teardown, kmemleak scans, VM_BUG_ON coverage under debug kernels, and boot tests on architectures with and without `CONFIG_HAVE_BOOTMEM_INFO_NODE`.
