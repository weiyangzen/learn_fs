<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/kmsan.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/kmsan.h

## Purpose
x86 KMSAN metadata mapping helpers for shadow/origin lookup and address validity. The header is 102 lines and is part of the Ceph client copy of the Linux x86 architecture tree.

## Important APIs, Types, and Functions
Key includes: `#include <asm/cpu_entry_area.h>`; `#include <asm/processor.h>`; `#include <linux/mmzone.h>`

Notable constants/macros: `#define _ASM_X86_KMSAN_H`

Notable declarations and inline helpers: `#define _ASM_X86_KMSAN_H`; `static inline void *arch_kmsan_get_meta_or_null(void *addr, bool is_origin)`; `unsigned long addr64 = (unsigned long)addr;`; `unsigned long off;`; `int cpu;`; `static inline bool kmsan_phys_addr_valid(unsigned long addr)`; `static inline bool kmsan_virt_addr_valid(void *addr)`; `unsigned long x = (unsigned long)addr;`; `unsigned long y = x - __START_KERNEL_map;`; `bool ret;`

## Control Flow
arch_kmsan_get_meta_or_null() maps CPU entry area and other supported virtual addresses to shadow/origin metadata; validity helpers gate physical/virtual regions.

## State and Persistence
State is per-CPU CPU-entry-area shadow/origin arrays and KMSAN metadata mappings maintained by sanitizer runtime.

## Dependencies and Integration Points
Depends on cpu_entry_area layout, processor address classification, mmzone/phys validation, and generic KMSAN.

## Risks
Risks include missing metadata for entry stacks, wrong physical validity boundaries, and sanitizer false reports in low-level entry code.

## Test Signals
Tests should boot KMSAN configs, run KMSAN tests, exercise interrupts/syscalls using CPU entry area, vmalloc/direct-map accesses, and invalid physical addresses.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/kmsan.h -->
