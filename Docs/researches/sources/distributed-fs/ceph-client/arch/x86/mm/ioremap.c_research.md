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
