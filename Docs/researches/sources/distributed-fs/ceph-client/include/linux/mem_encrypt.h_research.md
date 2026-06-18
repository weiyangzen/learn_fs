<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mem_encrypt.h -->
# sources/distributed-fs/ceph-client/include/linux/mem_encrypt.h

## Purpose
This header provides common memory-encryption address conversion helpers, especially for AMD SME/SEV-style encryption masks.

## Important APIs, types, and functions
When architecture memory encryption is enabled it includes `<asm/mem_encrypt.h>`. With `CONFIG_AMD_MEM_ENCRYPT`, `__sme_set()` ORs `sme_me_mask` into an address-like value and `__sme_clr()` removes it. `dma_addr_encrypted`, `dma_addr_unencrypted`, and `dma_addr_canonical` normalize DMA address conversions, with identity fallbacks when unsupported.

## Control flow
Callers wrap physical/DMA/PTE-like values when they need encrypted, unencrypted, or canonical forms. Architecture headers can override the DMA helper macros before generic fallbacks are defined.

## State and persistence
The only external state is architecture-provided encryption mask state such as `sme_me_mask`. The header itself stores none.

## Dependencies and integration points
It depends on architecture Kconfig and arch memory-encryption declarations. It integrates page-table setup, DMA mapping, and platform code with encryption-aware address formats.

## Risks and test signals
Risks include double-applying or failing to clear encryption masks, using helpers on non-address bitfields, and inconsistent arch overrides. Test encrypted and unencrypted DMA mappings, canonicalization, disabled-config identity behavior, and PTE/address mask boundaries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mem_encrypt.h -->
