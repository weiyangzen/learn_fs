# sources/distributed-fs/ceph-client/include/linux/io.h

Purpose: This header is a generic kernel I/O mapping and memory-remap facade layered over architecture `asm/io.h`.

Important APIs, types, and functions: It declares copy helpers `__iowrite32_copy`, `__ioread32_copy`, `__iowrite64_copy`, `ioremap_page_range`, `vmap_page_range`, devres-managed `devm_ioremap*`, `devm_iounmap`, `devm_memremap`, `memremap`, `memunmap`, `pci_remap_cfgspace`, write-combining reservation helpers, and strict devmem `range_is_allowed`.

Control flow: MMU builds call real range mappers; non-MMU builds return success stubs. PCI config remap prefers non-posted `ioremap_np` and falls back to `ioremap`. `range_is_allowed` walks each PFN through `devmem_is_allowed` when strict devmem is enabled.

State and persistence: Devres-managed mappings are tied to a `struct device`; unmanaged `memremap`/`memunmap` and WC reservation handles require explicit release. Architecture WC handles may represent MTRR/PAT-like state.

Dependencies and integration points: Includes `asm/io.h`, `asm/page.h`, device resource management, PCI, devmem policy, memory encryption flags, and cacheability attributes.

Risks: Incorrect cacheability or posted/non-posted mapping selection can break device ordering. Missing unmap or WC release leaks virtual address or arch tracking resources. Strict devmem checks can reject userspace mappings that worked on permissive configs.

Test signals: Compile across MMU/non-MMU, PCI/non-PCI, strict devmem, and architecture override configurations. Runtime tests should cover devres cleanup, WC reserve/free pairing, `pci_remap_cfgspace` fallback, and user mapping policy for exclusive or restricted ranges.
