<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/fixmap.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/fixmap.h

## Purpose
Compile-time fixed virtual address layout for x86 early boot, APIC/MMIO, kmap-local, GHES, vsyscall, and early ioremap users. The header is 200 lines and is part of the Ceph client copy of the Linux x86 architecture tree.

## Important APIs, Types, and Functions
Key includes: `#include <asm/kmap_size.h>`; `#include <linux/kernel.h>`; `#include <asm/apicdef.h>`; `#include <asm/page.h>`; `#include <asm/pgtable_types.h>`; `#include <linux/threads.h>`; `#include <uapi/asm/vsyscall.h>`; `#include <asm-generic/fixmap.h>`

Notable constants/macros: `#define _ASM_X86_FIXMAP_H`; `#define FIXMAP_PMD_TOP 507`; `#define FIXADDR_TOP ((unsigned long)__FIXADDR_TOP)`; `#define FIXADDR_TOP (round_up(VSYSCALL_ADDR + PAGE_SIZE, 1<<PMD_SHIFT) - \`; `#define NR_FIX_BTMAPS 64`; `#define FIX_BTMAPS_SLOTS 8`; `#define TOTAL_FIX_BTMAPS (NR_FIX_BTMAPS * FIX_BTMAPS_SLOTS)`; `#define FIXADDR_SIZE (__end_of_permanent_fixed_addresses << PAGE_SHIFT)`; `#define FIXADDR_START (FIXADDR_TOP - FIXADDR_SIZE)`; `#define FIXADDR_TOT_SIZE (__end_of_fixed_addresses << PAGE_SHIFT)`; `#define FIXADDR_TOT_START (FIXADDR_TOP - FIXADDR_TOT_SIZE)`; `#define FIXMAP_PAGE_NOCACHE PAGE_KERNEL_IO_NOCACHE`; `#define __late_set_fixmap(idx, phys, flags) __set_fixmap(idx, phys, flags)`; `#define __late_clear_fixmap(idx) __set_fixmap(idx, 0, __pgprot(0))`

Notable declarations and inline helpers: `#define _ASM_X86_FIXMAP_H`; `# define FIXMAP_PMD_NUM 2`; `# define KM_PMDS (KM_MAX_IDX * ((CONFIG_NR_CPUS + 511) / 512))`; `# define FIXMAP_PMD_NUM (KM_PMDS + 2)`; `#define FIXMAP_PMD_TOP 507`; `extern unsigned long __FIXADDR_TOP;`; `#define FIXADDR_TOP ((unsigned long)__FIXADDR_TOP)`; `#define FIXADDR_TOP (round_up(VSYSCALL_ADDR + PAGE_SIZE, 1<<PMD_SHIFT) - \`; `enum fixed_addresses {`; `#define NR_FIX_BTMAPS 64`; `#define FIX_BTMAPS_SLOTS 8`; `#define TOTAL_FIX_BTMAPS (NR_FIX_BTMAPS * FIX_BTMAPS_SLOTS)`; `extern void reserve_top_address(unsigned long reserve);`; `#define FIXADDR_SIZE (__end_of_permanent_fixed_addresses << PAGE_SHIFT)`; `#define FIXADDR_START (FIXADDR_TOP - FIXADDR_SIZE)`; `#define FIXADDR_TOT_SIZE (__end_of_fixed_addresses << PAGE_SHIFT)`; `#define FIXADDR_TOT_START (FIXADDR_TOP - FIXADDR_TOT_SIZE)`; `extern int fixmaps_set;`; `extern pte_t *pkmap_page_table;`; `void __native_set_fixmap(enum fixed_addresses idx, pte_t pte);`; `void native_set_fixmap(unsigned /* enum fixed_addresses */ idx,`; `static inline void __set_fixmap(enum fixed_addresses idx,`; `#define FIXMAP_PAGE_NOCACHE PAGE_KERNEL_IO_NOCACHE`; `void __init *early_memremap_encrypted(resource_size_t phys_addr,`

## Control Flow
Callers convert fixed-address enum indices into top-down virtual addresses and bind/unbind physical pages with native_set_fixmap(), __set_fixmap(), or early/late wrappers.

## State and Persistence
State is global page-table state plus fixmaps_set and pkmap_page_table; mappings persist until explicitly cleared or superseded by boot/runtime phases.

## Dependencies and Integration Points
Depends on page-table types, APIC limits, kmap sizing, vsyscall layout, memory encryption attributes, and asm-generic fixmap helpers.

## Risks
Risks include enum ordering changes, PMD coverage errors, missing encryption/decryption attributes, and overlap with vmalloc or vsyscall space.

## Test Signals
Boot tests should exercise early_ioremap, APIC/IO-APIC mapping, kmap-local debug modes, encrypted/decrypted early memremap, and x86_32 FIXADDR_TOP reservation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/fixmap.h -->
