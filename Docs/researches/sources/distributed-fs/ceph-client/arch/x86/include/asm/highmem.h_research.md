<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/highmem.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/highmem.h

## Purpose
32-bit highmem mapping constants and helpers for permanent kmap and temporary kmap-local support. The header is 73 lines and is part of the Ceph client copy of the Linux x86 architecture tree.

## Important APIs, Types, and Functions
Key includes: `#include <linux/interrupt.h>`; `#include <linux/threads.h>`; `#include <asm/tlbflush.h>`; `#include <asm/fixmap.h>`; `#include <asm/pgtable_areas.h>`

Notable constants/macros: `#define _ASM_X86_HIGHMEM_H`; `#define LAST_PKMAP_MASK (LAST_PKMAP-1)`; `#define PKMAP_NR(virt) ((virt-PKMAP_BASE) >> PAGE_SHIFT)`; `#define PKMAP_ADDR(nr) (PKMAP_BASE + ((nr) << PAGE_SHIFT))`; `#define flush_cache_kmaps() do { } while (0)`; `#define arch_kmap_local_post_map(vaddr, pteval) \`; `#define arch_kmap_local_post_unmap(vaddr) \`

Notable declarations and inline helpers: `#define _ASM_X86_HIGHMEM_H`; `extern unsigned long highstart_pfn, highend_pfn;`; `#define LAST_PKMAP_MASK (LAST_PKMAP-1)`; `#define PKMAP_NR(virt) ((virt-PKMAP_BASE) >> PAGE_SHIFT)`; `#define PKMAP_ADDR(nr) (PKMAP_BASE + ((nr) << PAGE_SHIFT))`; `#define flush_cache_kmaps() do { } while (0)`; `#define arch_kmap_local_post_map(vaddr, pteval) \`; `#define arch_kmap_local_post_unmap(vaddr) \`

## Control Flow
Highmem users map pages through pkmap/fixmap slots and convert kmap virtual addresses back to pages; on non-highmem paths most behavior is absent.

## State and Persistence
State is pkmap_page_table and kmap-local fixmap slots, with mappings managed by highmem core.

## Dependencies and Integration Points
Depends on fixmap, pgtable, kmap_size, page flags, and x86_32 memory layout.

## Risks
Risks include stale temporary mappings, wrong page-table attributes, and 32-bit-only assumptions leaking into generic code.

## Test Signals
Tests should cover HIGHMEM32 configs, kmap/kunmap, kmap_local nesting, debug forced-map mode, and highmem I/O paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/highmem.h -->
