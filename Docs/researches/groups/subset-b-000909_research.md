# Research: subset-b-000909

Grouped research for x86 memory-management files under `sources/distributed-fs/ceph-client/arch/x86/mm`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/mm/init_32.c -->
# sources/distributed-fs/ceph-client/arch/x86/mm/init_32.c

## Purpose
This file implements 32-bit x86 kernel memory initialization: early page-table construction, lowmem/highmem sizing, fixed-map/kmap setup, boot-time paging finalization, write-protect testing, and late kernel text/rodata hardening. It is the 32-bit counterpart to `init_64.c`, with extra handling for highmem and PAE/non-PAE page-table folding.

## Important APIs, Types, and Functions
- `populate_extra_pmd()` and `populate_extra_pte()` allocate or locate kernel page-table levels for early extra mappings, using `one_md_table_init()` and `one_page_table_init()`.
- `kernel_physical_mapping_init()` builds the direct mapping from physical RAM to `PAGE_OFFSET`, optionally using PSE 2 MiB pages and falling back to 4 KiB PTEs.
- `early_ioremap_page_table_range_init()` pre-creates fixmap page tables for early ioremap users, then calls `early_ioremap_reset()`.
- `find_low_pfn_range()`, `lowmem_pfn_init()`, `highmem_pfn_init()`, and `initmem_init()` decide the low/high memory split and initialize `high_memory`, `highstart_pfn`, `highend_pfn`, and memblock node ownership.
- `paging_init()`, `native_pagetable_init()`, `arch_mm_preinit()`, and `mem_init()` sequence boot memory and page-table readiness.
- `mark_rodata_ro()` and `mark_nxdata_nx()` apply final page attributes to kernel text, rodata, and data.

## Control Flow and State
Boot code starts with provisional mappings from assembly, then `kernel_physical_mapping_init()` runs in two passes: first preserving initial identity attributes while deciding page sizes, then flushing TLBs and rewriting the desired NX/global/executable attributes. `native_pagetable_init()` removes boot-time mappings above `max_low_pfn` and calls `paging_init()`. Highmem-aware paths allocate contiguous low pages for kmap PTEs and can relocate early fixmap PTE pages to maintain linearity. Memory sizing state is held in global PFN variables and in `high_memory`; `__vmalloc_start_set` marks vmalloc layout readiness.

## Dependencies and Integration Points
The file depends on x86 page-table helpers, memblock, e820-derived PFN bounds, highmem, fixmap, early ioremap, PCI IOMMU allocation, OLPC device tree setup, and CPA/set-memory APIs. Its exports of `__supported_pte_mask` and `__default_kernel_pte_mask` feed page-protection construction used across the architecture and by modules.

## Risks
The direct-map construction must obey Intel's rule against changing page size and attributes in one write; the two-pass algorithm is critical. Highmem/fixmap PTE relocation has BUG_ON checks because nonlinear early allocations would corrupt kmap/fixmap layout. Incorrect low/high PFN trimming can hide RAM, expose unmapped memory, or break vmalloc/highmem boundaries. `mark_rodata_ro()` and NX setup depend on precise section alignment.

## Test Signals
Boot logs report LOWMEM/HIGHMEM, mapped low RAM, WP-bit validation, and rodata write protection. CPA debug can temporarily revert and reapply rodata permissions. Useful validation includes 32-bit boot with PAE/non-PAE, `highmem=` variants, CONFIG_HIGHMEM on/off, early ioremap users, and page-table dumps confirming kernel text executable while data is NX/read-only as expected.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/mm/init_32.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/mm/init_64.c -->
# sources/distributed-fs/ceph-client/arch/x86/mm/init_64.c

## Purpose
This file implements 64-bit x86 kernel memory initialization, direct-map population, page-table synchronization, hotplug add/remove, sparse vmemmap backing, vmalloc preallocation, rodata hardening, and memory block sizing. It is central to 4-level/5-level paging support and to keeping kernel mappings consistent across process page tables.

## Important APIs, Types, and Functions
- `arch_sync_kernel_mappings()` synchronizes newly populated top-level kernel mappings into all process PGDs using `sync_global_pgds_l5()` or `sync_global_pgds_l4()`.
- `set_pte_vaddr*()`, `populate_extra_pmd()`, and `populate_extra_pte()` create or update kernel mappings for fixmap/early users.
- `init_extra_mapping_wb()` and `init_extra_mapping_uc()` create early PMD-sized direct-map additions with explicit cache modes.
- `kernel_physical_mapping_init()` and `kernel_physical_mapping_change()` build or split direct mappings through `phys_p4d_init()`, `phys_pud_init()`, `phys_pmd_init()`, and `phys_pte_init()`.
- Hotplug APIs include `arch_add_memory()`, `add_pages()`, `arch_remove_memory()`, `vmemmap_free()`, and page-table removal helpers.
- Vmemmap APIs include `vmemmap_set_pmd()`, `vmemmap_check_pmd()`, `vmemmap_populate()`, `register_page_bootmem_memmap()`, and `vmemmap_populate_print_last()`.
- `memory_block_size_bytes()` probes hotplug granularity; `mark_rodata_ro()` hardens kernel mappings.

## Control Flow and State
Early boot creates missing page-table pages via `spp_getpage()`, using memblock before `after_bootmem` and atomic page allocation afterward. Direct-map creation descends from PGD to PTE, preserving existing Xen or early mappings when possible and choosing 1 GiB, 2 MiB, or 4 KiB mappings based on `page_size_mask`. When new top-level entries are installed, `sync_global_pgds()` propagates them. Memory hotplug first maps the physical range, adds struct pages, updates `max_pfn`, `max_low_pfn`, and `high_memory`, and later can tear down direct-map and vmemmap page tables with TLB flushes. Vmemmap state tracks unused sub-PMD ranges with `unused_pmd_start` and debug span globals.

## Dependencies and Integration Points
The implementation integrates with memblock, sparsemem/vmemmap, memory hotplug, NUMA, e820, kcore, bootmem info, ftrace rodata protection, Xen/PV expectations, and generic memory section registration. `mm_internal.h` exposes the direct-map creation and change routines to encryption and setup code. KASLR affects virtual base addresses through `__va()` and page-table layout.

## Risks
Top-level synchronization differs between 4-level and 5-level paging; using the wrong level can leave process page tables missing kernel mappings. Hot-remove must not free low identity mappings below 1 GiB and must coordinate altmap-backed vmemmap memory. Large-page splitting must preserve physical frame and attributes before changing page size. `preallocate_vmalloc_pages()` panics if synchronization-critical page-table levels cannot be allocated.

## Test Signals
Boot and hotplug logs show memory block size, vmemmap PMD spans, kcore vsyscall registration, rodata protection, and page-count updates. Test scenarios include 4-level and 5-level paging, memory hotplug add/remove, device-private `memremap_pages()`, vmemmap hugepage/altmap paths, KASLR direct-map bases, Xen/PV boot, and CPA debug rodata toggling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/mm/init_64.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/mm/iomap_32.c -->
# sources/distributed-fs/ceph-client/arch/x86/mm/iomap_32.c

## Purpose
This 32-bit-only file supports temporary/local I/O mappings with correct cache attributes, especially write-combining mappings for devices. It bridges generic iomap callers to x86 PAT/memtype tracking and highmem local kmap primitives.

## Important APIs, Types, and Functions
- `iomap_create_wc()` reserves a write-combining memory type for a physical I/O range and returns a filtered `pgprot_t`.
- `iomap_free()` releases the corresponding memtype reservation.
- `__iomap_local_pfn_prot()` maps a PFN locally with a caller-supplied protection, adjusting non-PAT systems to UC-minus for non-WB requests.
- `is_io_mapping_possible()` rejects >4 GiB mappings on non-PAE kernels even when `phys_addr_t` is 64-bit.

## Control Flow and State
`iomap_create_wc()` first validates addressability, calls `memtype_reserve_io()`, and then synthesizes `__PAGE_KERNEL | cachemode2protval(pcm)`, masked by `__default_kernel_pte_mask`. `__iomap_local_pfn_prot()` checks PAT availability, normalizes cache mode when PAT is absent, masks unsupported bits, and delegates to `__kmap_local_pfn_prot()`. Persistent state lives in PAT memtype reservations, not in this file.

## Dependencies and Integration Points
The file depends on `asm/memtype.h`, PAT cache-mode translation, `__default_kernel_pte_mask` from x86 init code, and highmem local mapping. It is used by I/O mapping helpers that need temporary CPU access to device PFNs without a long-lived vmalloc mapping.

## Risks
Skipping the non-PAE addressability check would create impossible mappings above 4 GiB. Cache-mode mismatches can corrupt device interaction or conflict with existing PAT reservations. Callers must pair successful `iomap_create_wc()` with `iomap_free()`.

## Test Signals
Useful signals are successful WC mappings on PAT-enabled 32-bit kernels, UC-minus fallback on non-PAT kernels, rejection of high physical addresses without PAE, and PAT debug output showing reservations released after use.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/mm/iomap_32.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/mm/ioremap.c -->
# sources/distributed-fs/ceph-client/arch/x86/mm/ioremap.c

## Purpose
This file implements x86 physical-to-kernel virtual remapping for MMIO and special memory, including cache attribute negotiation, memory-encryption policy, early fixmap-backed remaps, `/dev/mem` translation, and `memremap()` architecture decisions.

## Important APIs, Types, and Functions
- `ioremap()`, `ioremap_uc()`, `ioremap_wc()`, `ioremap_wt()`, `ioremap_cache()`, `ioremap_encrypted()`, and `ioremap_prot()` are exported mapping entry points.
- `__ioremap_caller()` performs validation, memtype reservation, encryption attribute selection, vmalloc area allocation, direct-map cache synchronization, page-range mapping, and mmiotrace notification.
- `iounmap()` tears down ioremap areas, calls mmiotrace and KMSAN unmap hooks, frees memtype reservations, and removes the vm area.
- `arch_memremap_wb()`, `xlate_dev_mem_ptr()`, `unxlate_dev_mem_ptr()`, `arch_memremap_can_ram_remap()`, `early_memremap_pgprot_adjust()`, and `phys_mem_access_encrypted()` integrate with generic memremap and `/dev/mem`.
- `early_ioremap_init()`, `is_early_ioremap_ptep()`, and `__early_set_fixmap()` manage the early boot PTE table `bm_pte`.

## Control Flow and State
`__ioremap_caller()` rejects zero/wrapping/invalid ranges and normal RAM that is not reserved. It page-aligns the physical range, strips non-address bits, reserves a PAT memtype, verifies fallback compatibility, chooses encrypted or decrypted `PAGE_KERNEL_IO`, allocates a `VM_IOREMAP` area, synchronizes any direct-map cache mode, installs the page range, and records the mapping for mmiotrace. Unmap reverses this in a strict order. Encryption-aware memremap helpers classify persistent memory, EFI data, setup_data, reserved e820 ranges, SEV/TDX guest state, and Hyper-V/private MMIO.

## Dependencies and Integration Points
The implementation depends on memtype/PAT, vmalloc, fixmap/early_ioremap, e820, EFI, confidential-computing attributes, KMSAN, mmiotrace, `physaddr.h`, and set-memory CPA operations. Drivers see this through the public `ioremap*()` APIs; debug tracing sees it through `mmiotrace_ioremap()` and `mmiotrace_iounmap()`.

## Risks
Incorrect cache-mode reservation or direct-map synchronization can create aliasing with different memory types. Mapping normal RAM through ioremap is intentionally blocked because it can bypass kernel memory management. Encryption decisions are subtle: setup data, EFI data, persistent memory, reserved ranges, SEV, SNP, TDX, and host SME have different required C-bit states. Early fixmap code assumes the boot ioremap range fits within one PMD.

## Test Signals
Expected signals include WARN_ON for ioremap-on-RAM, PAT debug conflicts, iomem sanity warnings for multi-BAR mappings, KMSAN unmap coverage, mmiotrace mapping/unmapping records, and successful early encrypted/decrypted remaps under AMD memory encryption. Tests should cover each cache-mode API, unaligned addresses, EFI/setup_data memremap, confidential guest boot, and early fixmap teardown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/mm/ioremap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/mm/kasan_init_64.c -->
# sources/distributed-fs/ceph-client/arch/x86/mm/kasan_init_64.c

## Purpose
This file initializes KASAN shadow memory on x86_64, from the earliest shared shadow mappings through the final per-region shadow population used after paging is fully initialized. It handles both 4-level and 5-level paging and supports optional vmalloc shadow population on demand.

## Important APIs, Types, and Functions
- `kasan_early_init()` builds early shadow page-table chains and maps the shadow range in `early_top_pgt` and `init_top_pgt`.
- `kasan_init()` replaces temporary shadow coverage with real shadow mappings for direct map, CPU entry area shared portions, kernel image, vmalloc/modules gaps, and remaining KASAN shadow bounds.
- `kasan_populate_shadow_for_vaddr()` maps shadow for a caller-provided virtual range.
- Internal helpers `kasan_populate_pgd/p4d/pud/pmd()`, `kasan_populate_shadow()`, and `map_range()` allocate shadow backing, trying huge mappings at PUD/PMD levels when aligned.
- `clear_pgds()`, `kasan_map_early_shadow()`, and shallow-population helpers manage top-level entries safely around 5-level layout collisions.

## Control Flow and State
Early initialization fills all early shadow PTE/PMD/PUD/P4D entries with `kasan_early_shadow_page`, masking unsupported page bits and including encryption. Final initialization copies the top-level table, temporarily switches CR3 to `early_top_pgt`, clears the KASAN shadow range, maps early shadows for holes, maps real shadow for every `pfn_mapped[]` range, populates CPU entry area shared shadow, handles vmalloc either shallowly or with early shadow, maps kernel text/data shadow, then switches back to `init_top_pgt`. It finally zeroes and write-protects the shared early shadow page and calls generic KASAN init.

## Dependencies and Integration Points
The file depends on memblock allocation, `pfn_mapped[]` from e820/direct-map setup, CPU entry area layout, x86 page-table allocation, KASAN generic helpers, section symbols, and TLB/CR3 operations. It coordinates with KASLR because shadow bounds and virtual bases differ under 5-level paging.

## Risks
KASAN shadow overlaps with kernel, module, EFI, and CPU entry regions near `KASAN_SHADOW_END`; the 5-level temporary P4D copy avoids clobbering unrelated mappings. Missing shadow for CPU entry or direct-map ranges can cause early faults. Using huge shadow pages requires exact alignment and allocation success fallback. TLB flushes around CR3 switches and write-protecting early shadow are correctness-critical.

## Test Signals
Booting with KASAN should produce no shadow faults during early init, CPU entry area use, vmalloc allocation, module loading, or kernel image accesses. Useful scenarios include 4-level and 5-level paging, `CONFIG_KASAN_VMALLOC`, NUMA node allocation, large-memory direct maps, and memory encryption where `_PAGE_ENC` must be preserved.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/mm/kasan_init_64.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/mm/kaslr.c -->
# sources/distributed-fs/ceph-client/arch/x86/mm/kaslr.c

## Purpose
This file randomizes x86_64 kernel virtual memory regions at boot: direct map, vmalloc, and vmemmap. It also prepares the real-mode trampoline mapping needed when the direct map base is randomized.

## Important APIs, Types, and Functions
- `kernel_randomize_memory()` computes randomized bases for `page_offset_base`, `vmalloc_base`, and `vmemmap_base`, and sets `direct_map_physmem_end`.
- `init_trampoline_kaslr()` builds a low-memory PGD entry for the real-mode trampoline that mirrors the direct-map PUD/P4D path for physical address 0.
- `struct kaslr_memory_region` records each randomized region's base pointer, optional end pointer, and size in TiB.
- `get_padding()` converts TiB-sized region slots into bytes.

## Control Flow and State
The algorithm starts at the configured 4-level or 5-level page-offset base and ends before `CPU_ENTRY_AREA_BASE`. It initializes the direct-map maximum to `(1 << MAX_PHYSMEM_BITS) - 1`, exits if memory KASLR is disabled, sizes the direct map from physical RAM plus configured padding, optionally shrinks it when `ZONE_DEVICE` is disabled, derives vmemmap size from the direct-map size, and distributes remaining entropy between ordered regions. Random entropy is PUD-aligned and order is preserved. `direct_map_physmem_end` is updated when the direct map is trimmed.

## Dependencies and Integration Points
The code depends on `kaslr_get_random_long()`, `prandom`, `max_pfn`, paging mode selection, global virtual base variables from x86 layout code, CPU entry area bounds, and `alloc_low_page()` from `mm_internal.h`. Direct-map sizing feeds later page-table initialization and hotplug limit checks.

## Risks
Virtual layout constants must remain ordered; BUILD_BUG_ON checks catch only some layout drift. Shrinking `direct_map_physmem_end` conflicts with `ZONE_DEVICE`, which may need arbitrary physical addresses mapped. Entropy arithmetic must leave enough room for all regions and maintain PUD alignment. The trampoline mapping must match the randomized direct map or secondary CPU real-mode entry can fail.

## Test Signals
Boot logs and page-table dumps should show randomized bases when memory KASLR is enabled and fixed bases when disabled. Tests should include 4-level/5-level paging, large RAM, `CONFIG_RANDOMIZE_MEMORY_PHYSICAL_PADDING`, `ZONE_DEVICE`, CPU bring-up after KASLR, and hotplug ranges checked against `DIRECT_MAP_PHYSMEM_END`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/mm/kaslr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/mm/kmmio.c -->
# sources/distributed-fs/ceph-client/arch/x86/mm/kmmio.c

## Purpose
This file implements low-level MMIO probing for mmiotrace. It marks MMIO mapping pages non-present, handles the resulting page faults, single-steps the faulting instruction, and calls registered pre/post probe handlers.

## Important APIs, Types, and Functions
- `register_kmmio_probe()` and `unregister_kmmio_probe()` add/remove `struct kmmio_probe` ranges and arm/disarm affected pages.
- `kmmio_handler()` handles page faults from armed MMIO pages and sets trap flag state for single stepping.
- `post_kmmio_handler()` completes the single-step debug trap and rearms pages.
- `kmmio_init()` and `kmmio_cleanup()` register/unregister the die notifier.
- `struct kmmio_fault_page` tracks an armed page, saved presence bits, refcount, and delayed release state; `struct kmmio_context` is per-CPU in-flight state.

## Control Flow and State
Probe registration inserts the probe in an RCU-protected global list and arms each page by clearing PTE/PMD presence while saving the old entry. On page fault, the handler looks up the fault page and probe under scheduler RCU, records per-CPU context, invokes the pre-handler, enables TF, disables IF, restores page presence, and returns handled. The debug-trap notifier calls the post-handler, rearms the page if still referenced, restores flags, and releases RCU. Unregistration decrements page refcounts, disarms zero-count pages, removes probes, and uses a two-stage RCU delayed release before freeing fault-page records.

## Dependencies and Integration Points
The code integrates with x86 page-fault handling, debug trap die notifications, `lookup_address()`, TLB flush helpers, debug registers, RCU, local interrupt control, and `linux/mmiotrace.h`. `mmio-mod.c` registers the actual mmiotrace probes and supplies pre/post callbacks.

## Risks
This code runs in fault/debug trap context with interrupts disabled and cannot sleep. Recursive faults, multiple CPUs accessing the same page during single-step, or premature RCU freeing can lose events or crash. Large PMD mappings are handled, but unexpected page levels are rejected. Locking uses an arch spinlock hidden from lockdep because it is used in NMI-like contexts.

## Test Signals
Expected signals include successful mmiotrace enable/disable, probe callbacks around MMIO instructions, no leaked fault pages at cleanup, warnings on recursive probes or unexpected debug traps, and stable behavior under concurrent CPU access. Testing usually pairs this with `testmmiotrace` or mmiotrace debugfs workflows.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/mm/kmmio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/mm/kmsan_shadow.c -->
# sources/distributed-fs/ceph-client/arch/x86/mm/kmsan_shadow.c

## Purpose
This small file provides x86-specific KMSAN metadata storage for the CPU entry area, which lacks normal `struct page` backing.

## Important APIs, Types, and Functions
- `DEFINE_PER_CPU(char[CPU_ENTRY_AREA_SIZE], cpu_entry_area_shadow)` allocates per-CPU KMSAN shadow bytes for CPU entry area addresses.
- `DEFINE_PER_CPU(char[CPU_ENTRY_AREA_SIZE], cpu_entry_area_origin)` allocates per-CPU KMSAN origin bytes for the same region.

## Control Flow and State
There is no executable control flow in this file. It defines persistent per-CPU arrays. KMSAN's architecture helpers map addresses in each CPU's entry area to these arrays when normal page-backed metadata lookup cannot apply.

## Dependencies and Integration Points
The file depends on `asm/cpu_entry_area.h` for `CPU_ENTRY_AREA_SIZE` and on percpu definitions. It integrates with `arch_kmsan_get_meta_or_null()` declared elsewhere and with exception/entry-stack instrumentation.

## Risks
The arrays must stay exactly sized to the CPU entry area. If CPU entry area layout changes without matching metadata mapping logic, KMSAN can miss uninitialized accesses or compute invalid metadata addresses.

## Test Signals
KMSAN-enabled boot should handle exceptions, entry stacks, and CPU entry area accesses without metadata faults. Instrumentation tests that exercise interrupts, exceptions, and context switches are relevant.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/mm/kmsan_shadow.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/mm/maccess.c -->
# sources/distributed-fs/ceph-client/arch/x86/mm/maccess.c

## Purpose
This file supplies the x86 policy for `copy_from_kernel_nofault_allowed()`, deciding whether a kernel no-fault read source address is permissible.

## Important APIs, Types, and Functions
- `copy_from_kernel_nofault_allowed(const void *unsafe_src, size_t size)` returns whether no-fault kernel copying may try the address.
- On x86_64 it rejects userspace plus the guard page, rejects vsyscall addresses, permits early boot before virtual-address width is initialized, and checks canonicality.
- On 32-bit it permits addresses at or above `TASK_SIZE_MAX`.

## Control Flow and State
The function is a pure policy check. x86_64 first compares the address against `TASK_SIZE_MAX + PAGE_SIZE`, then calls `is_vsyscall_vaddr()`, then handles early boot by checking `boot_cpu_data.x86_virt_bits`, and finally validates canonical address form. It does not persist state.

## Dependencies and Integration Points
It depends on uaccess, task-size constants, vsyscall address classification, and CPU virtual-address-width discovery. It is consumed by generic no-fault memory access helpers used by debugging, probing, and fault-tolerant kernel reads.

## Risks
Allowing userspace or vsyscall addresses can turn kernel no-fault reads into unsafe user access or unhandled faults. Rejecting too much during early boot can break early exception decoding before CPU address-width state is initialized. The `size` parameter is not used here, so callers must handle range overflow elsewhere.

## Test Signals
Tests should confirm rejection of userspace, guard-page, and vsyscall addresses; acceptance of canonical kernel addresses; and early-boot functionality in fault handlers. Fault-injection around no-fault copy helpers is useful.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/mm/maccess.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/mm/mem_encrypt.c -->
# sources/distributed-fs/ceph-client/arch/x86/mm/mem_encrypt.c

## Purpose
This file contains common x86 memory-encryption setup shared by AMD SME/SEV and Intel TDX paths. It adjusts DMA policy, SWIOTLB sizing, virtio restricted-memory behavior, and boot-time feature reporting.

## Important APIs, Types, and Functions
- `force_dma_unencrypted()` implements `ARCH_HAS_FORCE_DMA_UNENCRYPTED` policy for encrypted guests and host SME devices that cannot address the encryption bit.
- `mem_encrypt_init()` updates SWIOTLB memory attributes, prepares SNP secure TSC state, and prints active encryption features.
- `mem_encrypt_setup_arch()` performs early architecture setup, including SNP e820 fixups and encrypted-guest SWIOTLB sizing.
- `print_mem_encrypt_feature_info()` formats active Intel TDX, AMD SME, SEV, SEV-ES, and SEV-SNP state.

## Control Flow and State
DMA policy is queried per device: encrypted guests always require shared/unencrypted DMA; SME hosts compare device DMA masks against the encryption mask. Architecture setup fixes SNP e820 tables for hosts, then encrypted guests size SWIOTLB to roughly 6 percent of RAM clamped between the default and 1 GiB, and install the virtio restricted-memory callback. Runtime initialization exits unless memory encryption is active, then updates bounce-buffer attributes and reports features.

## Dependencies and Integration Points
The file depends on confidential-computing attributes, `sme_me_mask`, DMA direct mapping, SWIOTLB, memblock, virtio anchor callbacks, and SEV/SNP helpers. It affects all DMA-capable drivers indirectly through DMA mapping and bounce-buffer policy.

## Risks
Under-sizing SWIOTLB in encrypted guests causes DMA failures or severe performance loss. Overly broad unencrypted DMA policy can reduce protection, while overly narrow policy breaks devices that cannot address encrypted memory. Feature reporting depends on `cc_vendor` and attribute state being initialized correctly.

## Test Signals
Boot logs should show memory encryption features and adjusted SWIOTLB size under SEV/TDX. DMA-heavy workloads in encrypted guests, virtio devices, and devices with limited DMA masks validate the policy. SNP host boots should show successful e820 fixups.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/mm/mem_encrypt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/mm/mem_encrypt_amd.c -->
# sources/distributed-fs/ceph-client/arch/x86/mm/mem_encrypt_amd.c

## Purpose
This file implements AMD-specific memory encryption mechanics for SME, SEV, SEV-ES, and SEV-SNP: early encrypt/decrypt operations, page-table C-bit transitions, SNP RMP state changes, hypervisor notifications, boot-data mapping, and decrypted memory cleanup.

## Important APIs, Types, and Functions
- Globals `sme_me_mask`, `sev_status`, and `sev_check_data` live in `.data` for very early boot and are exported or PIC-aliased.
- `sme_early_encrypt()` and `sme_early_decrypt()` call `__sme_early_enc_dec()` for early in-place content conversion.
- `early_set_memory_decrypted()` and `early_set_memory_encrypted()` alter early direct-map page encryption attributes.
- `prepare_pte_enc()` and `set_pte_enc_mask()` support later encryption attribute changes by computing PFN/protection state and updating PTEs.
- `sme_early_init()` installs encryption masks, protection-map changes, SNP/SEV hooks, and feature-specific boot workarounds.
- `sme_map_bootdata()` and `sme_unmap_bootdata()` map or unmap boot params and command line under SME.
- `mem_encrypt_free_decrypted_mem()` re-encrypts and frees unused decrypted BSS pages.

## Control Flow and State
Early encryption maps source and destination aliases with encrypted/decrypted protections, copies through a cache-line-safe temporary buffer, and for SNP transitions pages shared/private around copies. Large page attribute changes may split mappings through `kernel_physical_mapping_change()` before updating PTE/PMD/PUD entries and flushing TLBs. `sme_early_init()` propagates the C-bit into early PMD flags and supported PTE masks, registers guest encryption hooks, disables parallel bring-up for SEV-ES, disables IA32 emulation for SEV, and suppresses unsafe ROM/table scans for SNP.

## Dependencies and Integration Points
The file depends on early memremap encrypted/decrypted variants, SNP RMP helpers, set-memory/CPA, TLB/cache flushes, boot parameters, x86 platform hooks, SEV GHCB/SNP helpers, and `mm_internal.h` direct-map splitting. It feeds generic `set_memory_encrypted/decrypted()` through platform hooks and affects kexec, AP bring-up, DMI/MP parsing, and device DMA.

## Risks
Encryption attribute transitions require cache flushes, TLB flushes, RMP state ordering, and sometimes hypervisor notifications. Wrong ordering can corrupt memory, trigger SNP validation faults, or expose private data as shared. Early boot code runs before normal allocators and must use limited fixmap slots. SEV-ES and SNP workarounds are security-sensitive and platform-specific.

## Test Signals
Relevant tests include SME bare-metal boot, SEV/SEV-ES/SEV-SNP guest boot, encrypted/decrypted `set_memory_*()` transitions, kexec, AP bring-up, IA32 syscall attempts in SEV guests, ROM/DMI probing under SNP, and freeing unused decrypted ranges without warnings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/mm/mem_encrypt_amd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/mm/mem_encrypt_boot.S -->
# sources/distributed-fs/ceph-client/arch/x86/mm/mem_encrypt_boot.S

## Purpose
This assembly file provides the position-independent AMD SME routine that encrypts kernel memory in place during early boot, while running from a decrypted work area outside the kernel image being transformed.

## Important APIs, Types, and Functions
- `__pi_sme_encrypt_execute` is the external entry point. It receives encrypted and decrypted virtual aliases, length, workarea virtual address, and encryption page-table physical address.
- Local routine `__enc_copy` is copied into the workarea and performs the actual CR3 switch and chunked copy.

## Control Flow and State
The entry point saves the original stack, switches to a one-page workarea stack, copies `__enc_copy` into the workarea, prepares arguments, and calls the copied routine. `__enc_copy` loads the encryption page tables into CR3, toggles CR4.PGE to flush global TLBs, changes PAT PA5 to write-protected, executes `wbinvd`, then copies up to 2 MiB at a time from the decrypted alias to an intermediate buffer and back through the encrypted alias. It restores PAT state and returns with unret annotations.

## Dependencies and Integration Points
It depends on x86 control registers, PAT MSR encoding, page size constants, retpoline/unret annotations, and the C-side SME early boot setup that prepares aliases, workarea, and page tables. It is part of the SME encrypt-in-place path used before normal kernel execution can assume encrypted contents.

## Risks
This code runs while the kernel image may be in transition between decrypted and encrypted states, so it cannot rely on normal kernel text or stack. Incorrect CR3, PAT, or cache ordering can corrupt the kernel image. The copied routine must remain position-independent and avoid return-thunk offsets that are invalid from the workarea.

## Test Signals
SME-enabled boot is the main validation. Failures usually appear as immediate boot hangs or corrupted kernel execution after encryption. Review signals include objdump checks for position independence, correct workarea sizing, and preservation/restoration of PAT and stack state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/mm/mem_encrypt_boot.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/mm/mm_internal.h -->
# sources/distributed-fs/ceph-client/arch/x86/mm/mm_internal.h

## Purpose
This private x86 mm header shares internal helpers and state between x86 memory-management implementation files without exposing them as public architecture APIs.

## Important APIs, Types, and Functions
- `alloc_low_pages()` and inline `alloc_low_page()` provide early low-memory page allocation for page tables and trampoline/KASLR code.
- `early_ioremap_page_table_range_init()` initializes early fixmap page-table coverage.
- `kernel_physical_mapping_init()` and `kernel_physical_mapping_change()` create or change direct-map page tables.
- `after_bootmem`, `update_cache_mode_entry()`, and `tlb_single_page_flush_ceiling` expose shared state or helpers.
- `x86_numa_init()` is declared when NUMA is enabled.

## Control Flow and State
The header has no runtime control flow. It defines cross-file contracts used during boot and memory hotplug. `after_bootmem` gates whether early or normal allocation paths may be used.

## Dependencies and Integration Points
Consumers include `init_32.c`, `init_64.c`, `kaslr.c`, `mem_encrypt_amd.c`, `ioremap.c`, `numa.c`, and PAT code. The direct-map APIs connect boot memory setup, encryption page-attribute changes, and hotplug.

## Risks
Because these are internal interfaces, signature or semantic changes can break boot ordering across several files. `kernel_physical_mapping_change()` in particular requires callers to understand TLB flush responsibilities.

## Test Signals
Build coverage across 32-bit, 64-bit, NUMA/non-NUMA, PAT, memory encryption, and hotplug configurations validates the header contract. Runtime validation comes from successful boot and direct-map changes without stale TLB faults.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/mm/mm_internal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/mm/mmap.c -->
# sources/distributed-fs/ceph-client/arch/x86/mm/mmap.c

## Purpose
This file implements x86 virtual-memory layout decisions for user processes, mmap randomization, address hint validation, `/dev/mem` physical range validation, and L1TF-sensitive PFN permission checks.

## Important APIs, Types, and Functions
- `task_size_32bit()` and `task_size_64bit()` return process address-space limits.
- `arch_mmap_rnd()`, `arch_pick_mmap_layout()`, and `get_mmap_base()` choose randomized top-down or legacy mmap bases.
- `mmap_address_hint_valid()` rejects hints crossing the default 47-bit map window on 5-level systems.
- `valid_phys_addr_range()` and `valid_mmap_phys_addr_range()` validate direct and mmap physical access.
- `pfn_modify_allowed()` restricts high MMIO `PROT_NONE` inversion on L1TF-vulnerable CPUs.

## Control Flow and State
Layout selection checks `ADDR_COMPAT_LAYOUT` and `sysctl_legacy_va_layout`; otherwise it uses a top-down base below the stack. Randomization derives from `PF_RANDOMIZE` and 32/64-bit mmap random bit settings. Compat builds maintain separate 32-bit and 64-bit bases in `mm_struct`. Address hints must fit within task size and stay on one side of `DEFAULT_MAP_WINDOW`.

## Dependencies and Integration Points
The file depends on process personality, rlimits, randomization sysctls, compat syscall detection, ELF randomization settings, `high_memory`, `phys_addr_valid()`, `range_is_allowed()` through related code, and L1TF mitigation helpers. It is used by generic mmap, proc/devmem, and PFN-mapped VMA paths.

## Risks
Incorrect mmap base calculations can collide with stack growth or reduce ASLR. The 5-level hint rule protects applications that cannot handle >47-bit addresses. `pfn_modify_allowed()` is security-sensitive for L1TF because inverted PROT_NONE PTEs can otherwise point speculation at valid memory.

## Test Signals
Tests should cover legacy vs top-down layout, 32-bit compat bases, ASLR on/off, 5-level paging hints around `DEFAULT_MAP_WINDOW`, `/dev/mem` range validation, and L1TF PFN modification with and without `CAP_SYS_ADMIN`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/mm/mmap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/mm/mmio-mod.c -->
# sources/distributed-fs/ceph-client/arch/x86/mm/mmio-mod.c

## Purpose
This file implements the higher-level mmiotrace module logic around KMMIO: tracking ioremap/iounmap events, decoding MMIO instructions, emitting trace records, and optionally reducing the system to one CPU to avoid missed events.

## Important APIs, Types, and Functions
- `mmiotrace_ioremap()` and `mmiotrace_iounmap()` are called from ioremap/iounmap paths.
- `enable_mmiotrace()` and `disable_mmiotrace()` control tracing lifetime.
- `mmiotrace_printk()` emits formatted trace messages while tracing is enabled.
- `pre()` and `post()` are KMMIO probe callbacks that decode instruction type, width, value, PC, and physical address.
- `struct trap_reason` stores per-CPU active instruction context; `struct remap_trace` couples a KMMIO probe to physical mapping metadata.

## Control Flow and State
When tracing is enabled, each ioremap call can allocate a `remap_trace`, emit an `MMIO_PROBE` mapping record, add it to `trace_list`, and register a KMMIO probe unless `nommiotrace` is set. Fault pre-handling decodes reads/writes/immediate writes and fills per-CPU trace state. Post-handling captures read results and emits `mmio_trace_rw()`. Iounmap unregisters the probe, emits `MMIO_UNPROBE`, waits for RCU, and frees the trace. Enable/disable is serialized by `mmiotrace_mutex`; trace list and enabled state are protected by `trace_lock`.

## Dependencies and Integration Points
The module depends on kmmio, ioremap hooks, instruction decoder helpers in `pf_in.h`, debugfs/trace mmiotrace core APIs, CPU hotplug, percpu storage, and page-table lookup for diagnostics. Module parameters `filter_offset`, `nommiotrace`, and `trace_pc` tune behavior.

## Risks
Tracing can miss events on other CPUs during KMMIO single-step windows; CPU hotplug downshifting mitigates this when available. Pre/post nesting must match exactly or the code BUGs. Recording PCs can taint clean-room reverse engineering, so it is optional. Failing to unregister probes on disable would leave non-present mappings armed.

## Test Signals
Enable/disable logs, mapping/unmapping records, read/write trace records, CPU offline/online logs, and cleanup purges for leaked mappings are primary signals. Tests include `nommiotrace`, `filter_offset`, `trace_pc`, hotplug enabled/disabled builds, and MMIO reads/writes through traced ioremaps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/mm/mmio-mod.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/mm/numa.c -->
# sources/distributed-fs/ceph-client/arch/x86/mm/numa.c

## Purpose
This file contains common 32/64-bit x86 NUMA initialization and CPU-to-node mapping. It parses NUMA command-line options, initializes node memory blocks from ACPI/AMD/OF or a dummy fallback, registers nodes, and maintains CPU masks.

## Important APIs, Types, and Functions
- `numa_setup()` handles `numa=off`, `numa=fake=`, `numa=noacpi`, and `numa=nohmat`.
- `x86_numa_init()` tries ACPI, AMD, OF, then dummy NUMA initialization.
- `numa_set_node()`, `numa_clear_node()`, `early_cpu_to_node()`, and `__cpu_to_node()` maintain CPU-node mappings.
- `setup_node_to_cpumask_map()`, `numa_add_cpu()`, `numa_remove_cpu()`, and `cpumask_of_node()` maintain node CPU masks.
- `init_gi_nodes()` onlines Generic Initiator-only nodes; `init_cpu_to_node()` seeds early CPU mappings.
- NUMA emulation helpers update APIC-to-node mapping and DMA boundary behavior.

## Control Flow and State
Early parameter parsing can disable NUMA, request emulation, or disable ACPI/HMAT paths. Initialization clears APIC mappings, lets `numa_memblks_init()` parse memory blocks, registers nodes with valid PFN ranges, clears CPU mappings to offline nodes, and round-robins unknown CPUs across online nodes. Dummy mode creates node 0 covering all memory and cannot fail. CPU-node state starts in early percpu storage and later moves to normal percpu data; node masks are bootmem-allocated after possible node IDs are known.

## Dependencies and Integration Points
The file depends on ACPI SRAT/HMAT, AMD northbridge NUMA, OF NUMA, memblock NUMA metadata, topology/percpu APIs, APIC ID mapping, node registration, and NUMA emulation. `init_64.c` calls `x86_numa_init()` through `initmem_init()` when NUMA is configured.

## Risks
Missing or inconsistent firmware tables can leave CPUs mapped to offline nodes; the code clears or fakes mappings to avoid that. `cpumask_of_node()` is invalid before `setup_node_to_cpumask_map()`. Generic Initiator-only nodes need special early online handling before node subsystem registration. NUMA emulation must remap physical node IDs consistently.

## Test Signals
Boot logs show NUMA disabled/fallback/faked nodes and memblock dumps. Tests should cover ACPI NUMA, AMD NUMA, OF fallback, `numa=off`, `numa=fake=`, memoryless CPU nodes, Generic Initiators, CPU hotplug mask updates, and `CONFIG_DEBUG_PER_CPU_MAPS` warnings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/mm/numa.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/mm/pat/Makefile -->
# sources/distributed-fs/ceph-client/arch/x86/mm/pat/Makefile

## Purpose
This Makefile selects the x86 PAT/page-attribute implementation objects for the `arch/x86/mm/pat` subdirectory.

## Important APIs, Types, and Functions
- `obj-y := set_memory.o memtype.o` always builds the core set-memory and memtype logic.
- `obj-$(CONFIG_X86_PAT) += memtype_interval.o` adds the interval-tree reservation backend when PAT is enabled.

## Control Flow and State
There is no runtime control flow. Build-time Kconfig decides whether the interval tracking implementation is compiled. When PAT is disabled, inline stubs from `memtype.h` replace the interval backend.

## Dependencies and Integration Points
The objects are consumed by x86 page-attribute changes, ioremap, pfnmap tracking, and cache-mode conversion. `memtype.c` is always present because it also handles disabled-PAT and MTRR-compatible behavior.

## Risks
Omitting `memtype_interval.o` when `CONFIG_X86_PAT=y` would leave non-stub symbols unresolved. Building it when PAT is disabled would be unnecessary and could conflict with stub expectations.

## Test Signals
Builds should pass with `CONFIG_X86_PAT=y` and `CONFIG_X86_PAT=n`. Runtime PAT debugfs availability depends on the enabled configuration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/mm/pat/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/mm/pat/cpa-test.c -->
# sources/distributed-fs/ceph-client/arch/x86/mm/pat/cpa-test.c

## Purpose
This file implements a boot-time/kernel-thread self-test for change-page-attribute (CPA) operations. It randomly changes a software PTE bit over direct-map pages, verifies page-table splitting and attributes, then reverts the changes.

## Important APIs, Types, and Functions
- `pageattr_test()` performs one test pass over random direct-map ranges.
- `print_split()` counts 4 KiB, large, 1 GiB, executable, and missed mappings and validates coverage against `max_pfn_mapped`.
- `do_pageattr_test()` runs the test repeatedly every 30 seconds until failure or stop.
- `start_pageattr_test()` starts the kernel thread via `device_initcall()`.
- The test exercises `change_page_attr_set()`, `change_page_attr_clear()`, and `cpa_set_pages_array()`.

## Control Flow and State
The test allocates a bitmap covering `max_pfn_mapped`, samples `NTEST` random PFNs, limits each range to uniform page protections and unused bitmap entries, then sets `_PAGE_CPA_TEST` through three CPA call styles. It verifies the first PTE has the test bit and was split to 4 KiB level. After all mutations, it clears the bit and verifies reversion. `print` limits detailed split output to the first pass.

## Dependencies and Integration Points
The file depends on direct-map page tables, CPA/cacheflush internals, random number generation, vmalloc, kthreads, and `lookup_address()`. It is only meaningful in debug/test configurations where `_PAGE_CPA_TEST` exists.

## Risks
Because it mutates direct-map attributes, failures indicate serious CPA bugs and trigger warnings. Random selection must avoid overlapping ranges and mixed protections to keep expected results meaningful. The repeated thread can add boot/runtime noise if enabled unintentionally.

## Test Signals
Expected logs start with `CPA self-test:` and eventually `ok.` on the first pass. Failures print bad PTEs, unexpected page levels, coverage mismatches, or reverting errors, followed by `NOT PASSED`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/mm/pat/cpa-test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/mm/pat/memtype.c -->
# sources/distributed-fs/ceph-client/arch/x86/mm/pat/memtype.c

## Purpose
This file implements x86 PAT cache-type policy: PAT MSR initialization, cache-mode translation, reservation/freeing of memory types for RAM and I/O ranges, direct-map cache synchronization, `/dev/mem` protections, PFN map tracking, and debugfs reporting.

## Important APIs, Types, and Functions
- `pat_bp_init()` selects the boot CPU PAT MSR value and initializes cache-mode translation; `pat_cpu_init()` programs secondary CPUs.
- `pat_enabled()`, `nopat`, and `debugpat` control feature availability and diagnostics.
- `memtype_reserve()`, `memtype_free()`, `memtype_reserve_io()`, and `memtype_free_io()` manage cache-type reservations.
- `reserve_ram_pages_type()` stores RAM cache type in page flags; non-RAM ranges use the interval tree through `memtype_check_insert()`.
- `memtype_kernel_map_sync()` updates direct-map attributes to avoid cache alias conflicts.
- `pfnmap_track()`, `pfnmap_untrack()`, `pfnmap_setup_cachemode()`, `phys_mem_access_prot_allowed()`, `phys_mem_access_prot()`, `pgprot_writecombine()`, and `pgprot_writethrough()` provide external policy hooks.

## Control Flow and State
PAT boot initialization disables PAT for missing CPU/firmware support, emulates legacy PWT/PCD modes when needed, handles old Intel errata by using only lower entries, or programs the full PAT layout with WC/WP/WT support. Reservations sanitize physical addresses, skip platform-untracked ranges, intersect WB requests with MTRR state, classify RAM vs non-RAM, and either update page flags or insert an interval-tree entry under `memtype_lock`. Freeing reverses page flags or exact interval entries. Direct-map synchronization changes kernel identity mapping cache attributes for RAM aliases.

## Dependencies and Integration Points
The file depends on MTRR lookup, page flags, memblock/system RAM walking, `x86_platform.is_untracked_pat_range`, set-memory CPA, ioremap, `/dev/mem`, KVM export for UC-MTRR immunity, debugfs, and `memtype_interval.c`. It is a core dependency of `ioremap.c` and 32-bit iomap.

## Risks
Conflicting cache aliases can corrupt memory, so reservation correctness is critical. RAM supports only WB/WC/UC-/WT in page flags; WP fails and UC redirects. MTRR can force WB requests to UC-minus. Non-RAM reservations require exact freeing; invalid frees are logged. Direct-map sync failures must unwind reservations.

## Test Signals
Boot logs print `x86/PAT: Configuration [0-7]`. `debugpat` logs reservations and frees. Debugfs `pat_memtype_list` exposes non-RAM reservations. Tests should cover PAT disabled, legacy CPUs, old Intel errata paths, ioremap WC/UC/WT, `/dev/mem` O_DSYNC, PFNMAP VMAs, RAM page-flag conflicts, and KVM `pat_pfn_immune_to_uc_mtrr()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/mm/pat/memtype.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/mm/pat/memtype.h -->
# sources/distributed-fs/ceph-client/arch/x86/mm/pat/memtype.h

## Purpose
This private PAT header defines the memory-type reservation record, debug printing, cache-mode names, and interval-tree backend prototypes or stubs.

## Important APIs, Types, and Functions
- `struct memtype` stores `[start,end)`, `subtree_max_end`, cache `type`, and rb-tree node.
- `cattr_name()` maps `enum page_cache_mode` values to human-readable strings.
- `dprintk()` emits PAT debug output only when `pat_debug_enable` is set.
- Prototypes include `memtype_check_insert()`, `memtype_erase()`, `memtype_lookup()`, and `memtype_copy_nth_element()`.
- When `CONFIG_X86_PAT` is disabled, static inline stubs provide no-op behavior.

## Control Flow and State
The header has no runtime state beyond declarations. It standardizes interval endpoint representation as exclusive `end` in `struct memtype`, while the interval backend converts to inclusive ends for the generic interval tree.

## Dependencies and Integration Points
`memtype.c` and `memtype_interval.c` include this header. Debugfs printing and conflict diagnostics rely on `cattr_name()`. The stubs allow `memtype.c` to compile when PAT tracking is disabled.

## Risks
The exclusive-end convention must remain consistent between reservation, lookup, and erase. Stubs returning success/null are correct only when higher-level PAT-disabled paths avoid relying on actual tracking.

## Test Signals
Compile both PAT-enabled and disabled configurations. Runtime debug messages should use consistent cache names, and interval-tree operations should preserve exact range endpoints.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/mm/pat/memtype.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/mm/pat/memtype_interval.c -->
# sources/distributed-fs/ceph-client/arch/x86/mm/pat/memtype_interval.c

## Purpose
This file provides the interval-tree backend for non-RAM PAT memory-type reservations. It stores physical ranges, detects cache-type conflicts among overlapping aliases, supports exact removal, lookup, and debugfs iteration.

## Important APIs, Types, and Functions
- `INTERVAL_TREE_DEFINE()` creates the augmented rb-tree operations for `struct memtype`.
- `memtype_check_insert()` validates overlap compatibility and inserts a new reservation.
- `memtype_erase()` removes an exact `[start,end)` reservation.
- `memtype_lookup()` finds a reservation overlapping a page-sized address range.
- `memtype_copy_nth_element()` copies the nth reservation for debugfs iteration.

## Control Flow and State
The static `memtype_rbroot` stores all interval entries. Conflict checking finds the first overlap, allows success with no overlap, fails when `newtype == NULL` and a different type overlaps, or adopts the first overlapping type and requires all other overlaps to match it. Insert updates `entry_new->type` to the compatible type when requested. Erase scans overlaps until it finds an exact start/end match.

## Dependencies and Integration Points
The tree is protected externally by `memtype_lock` in `memtype.c`. It depends on Linux's generic interval tree macros and the `struct memtype` layout from `memtype.h`. Debugfs list printing uses `memtype_copy_nth_element()`.

## Risks
Overlaps with inconsistent cache types must fail to prevent CPU cache corruption. Exact-endpoint removal means callers must free the same range they reserved. The debugfs nth-element scan is O(n) and safe only because callers copy while holding the lock briefly.

## Test Signals
PAT debug logs should show overlap handling. Tests should include non-overlapping insert, overlapping same-type insert, overlapping type adoption through `newtype`, conflicting insert failure, exact erase, invalid erase, lookup hits/misses, and debugfs iteration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/mm/pat/memtype_interval.c -->
