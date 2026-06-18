<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/iomap.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/iomap.h

## Purpose
x86-specific iomap resource helper declarations for write-combining mappings. The header is 22 lines and is part of the Ceph client copy of the Linux x86 architecture tree.

## Important APIs, Types, and Functions
Key includes: `#include <linux/fs.h>`; `#include <linux/mm.h>`; `#include <linux/uaccess.h>`; `#include <linux/highmem.h>`; `#include <asm/cacheflush.h>`; `#include <asm/tlbflush.h>`

Notable constants/macros: `#define _ASM_X86_IOMAP_H`

Notable declarations and inline helpers: `#define _ASM_X86_IOMAP_H`; `void __iomem *__iomap_local_pfn_prot(unsigned long pfn, pgprot_t prot);`; `int iomap_create_wc(resource_size_t base, unsigned long size, pgprot_t *prot);`; `void iomap_free(resource_size_t base, unsigned long size);`

## Control Flow
iomap_create_wc() creates or adjusts WC pgprot mappings for a physical resource range; iomap_free() tears them down.

## State and Persistence
State is resource mapping/memtype state managed by PAT/ioremap internals.

## Dependencies and Integration Points
Depends on resource_size_t, pgprot_t, PAT memtype tracking, and generic iomap users.

## Risks
Risks include WC alias conflicts, leaking memtype reservations, and wrong resource size alignment.

## Test Signals
Tests should exercise framebuffer or PCI BAR WC mappings, overlapping aliases, unmap/free paths, and PAT-disabled fallback.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/iomap.h -->
