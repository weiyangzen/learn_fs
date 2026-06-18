<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/kaslr.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/kaslr.h

## Purpose
x86 KASLR declarations for random values, physical/virtual memory randomization, and trampoline randomization. The header is 15 lines and is part of the Ceph client copy of the Linux x86 architecture tree.

## Important APIs, Types, and Functions
Key includes: None visible in this header.

Notable constants/macros: `#define _ASM_KASLR_H_`

Notable declarations and inline helpers: `#define _ASM_KASLR_H_`; `unsigned long kaslr_get_random_long(const char *purpose);`; `void kernel_randomize_memory(void);`; `void init_trampoline_kaslr(void);`; `static inline void kernel_randomize_memory(void) { }`; `static inline void init_trampoline_kaslr(void) {}`

## Control Flow
Boot code obtains purpose-labeled random longs and applies kernel memory and trampoline layout randomization when RANDOMIZE_MEMORY is enabled.

## State and Persistence
State is boot-chosen randomized physical/virtual offsets and trampoline placement; fixed after boot.

## Dependencies and Integration Points
Depends on early entropy, boot parameters, memory map parsing, page-table setup, and CONFIG_RANDOMIZE_MEMORY.

## Risks
Risks include weak early entropy, collisions with reserved regions, and runtime code assuming fixed addresses.

## Test Signals
Tests should boot repeatedly and compare layout variance, validate no overlap with reserved memory, test nokaslr, and cover hibernation/kexec interactions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/kaslr.h -->
