# sources/distributed-fs/ceph-client/arch/x86/include/asm/page_64.h

Purpose: supplies x86-64 page helpers that require C code rather than pure constants: virtual-to-physical conversion for kernel mappings, page clearing/copying declarations, and dynamic user task-size calculation for 4-level versus 5-level paging.

Important APIs, types, and functions: exports `max_pfn`, `phys_base`, `page_offset_base`, `vmalloc_base`, `vmemmap_base`, and `direct_map_physmem_end`. Key inline helpers are `__phys_addr_nodebug()`, `__phys_addr_symbol()`, `clear_pages()`, `clear_page()`, and `task_size_max()`. It declares `__phys_addr()` when `CONFIG_DEBUG_VIRTUAL` is active, `__clear_pages_unrolled()`, and `copy_page()`.

Control flow: `__phys_addr_nodebug()` distinguishes kernel image addresses from direct-map addresses by subtracting `__START_KERNEL_map` and using carry behavior to choose `phys_base` or the direct-map delta. `clear_pages()` unpoisons KMSAN metadata, then uses alternative patching to select unrolled stores, `rep stosq`, or ERMS `rep stosb`. `task_size_max()` uses `alternative_io()` to return the highest user address for LA57 or non-LA57 CPUs.

State and persistence: this header reads boot/runtime layout globals but does not own them. Page clearing mutates memory only in caller-supplied kernel mappings.

Dependencies and integration points: depends on `page_64_types.h`, CPU feature alternatives, KMSAN, debug virtual checks, KCFI references, and x86 boot memory layout. It integrates with generic page clear/copy code, `virt_to_phys()` paths, and `TASK_SIZE_MAX`.

Risks: physical address conversion is security- and crash-sensitive; wrong range logic corrupts DMA, page tables, or symbol fixups. `clear_pages()` inline assembly must accurately declare clobbers despite embedding a call. `task_size_max()` protects against highest-canonical-page CPU errata and SYSRET hazards.

Test signals: boot 4-level and 5-level paging systems, run `CONFIG_DEBUG_VIRTUAL`, KMSAN, and alternatives tests, validate `virt_to_phys()` for direct map and kernel text, clear/copy page selftests, and mmap tests near `DEFAULT_MAP_WINDOW` and `TASK_SIZE_MAX`.
