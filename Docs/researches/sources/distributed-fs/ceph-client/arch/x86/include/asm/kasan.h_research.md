<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/kasan.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/kasan.h

## Purpose
x86 KASAN shadow memory layout and init declarations. The header is 41 lines and is part of the Ceph client copy of the Linux x86 architecture tree.

## Important APIs, Types, and Functions
Key includes: `#include <linux/const.h>`

Notable constants/macros: `#define _ASM_X86_KASAN_H`; `#define KASAN_SHADOW_OFFSET _AC(CONFIG_KASAN_SHADOW_OFFSET, UL)`; `#define KASAN_SHADOW_SCALE_SHIFT 3`; `#define KASAN_SHADOW_START (KASAN_SHADOW_OFFSET + \`; `#define KASAN_SHADOW_END (KASAN_SHADOW_START + \`

Notable declarations and inline helpers: `#define _ASM_X86_KASAN_H`; `#define KASAN_SHADOW_OFFSET _AC(CONFIG_KASAN_SHADOW_OFFSET, UL)`; `#define KASAN_SHADOW_SCALE_SHIFT 3`; `#define KASAN_SHADOW_START (KASAN_SHADOW_OFFSET + \`; `#define KASAN_SHADOW_END (KASAN_SHADOW_START + \`; `void __init kasan_early_init(void);`; `void __init kasan_init(void);`; `void __init kasan_populate_shadow_for_vaddr(void *va, size_t size, int nid);`; `static inline void kasan_early_init(void) { }`; `static inline void kasan_init(void) { }`; `static inline void kasan_populate_shadow_for_vaddr(void *va, size_t size,`; `int nid) { }`

## Control Flow
Boot KASAN code computes shadow start/end from CONFIG_KASAN_SHADOW_OFFSET, populates early shadow mappings, and later initializes full shadow coverage.

## State and Persistence
State is KASAN shadow memory mappings and per-address shadow bytes maintained by sanitizer runtime.

## Dependencies and Integration Points
Depends on virtual address layout, page tables, memory initialization, NUMA node population, and generic KASAN.

## Risks
Risks include wrong shadow range for 5-level paging or KASLR, missing early mappings, and false positives/negatives from unpopulated shadow.

## Test Signals
Tests should boot KASAN configs, run kasan tests, exercise vmalloc/module/direct-map shadow, NUMA population, and KASLR/LA57 combinations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/kasan.h -->
