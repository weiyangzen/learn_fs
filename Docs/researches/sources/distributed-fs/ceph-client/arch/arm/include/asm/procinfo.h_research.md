# sources/distributed-fs/ceph-client/arch/arm/include/asm/procinfo.h

## Purpose
Defines ARM CPU/procinfo records used during boot-time CPU matching and processor-function table selection.

## Important APIs, Types, And Functions
Key declarations include struct cpu_tlb_fns;; struct cpu_user_fns;; struct cpu_cache_fns;; struct processor;; struct proc_info_list {; unsigned int cpu_val;. Important macros/constants include __ASM_PROCINFO_H. It depends directly on #include <asm/elf.h>.

## Control Flow
Early assembly and C setup compare CPU IDs against proc_info_list entries, then install MMU/cache/proc function pointers for the matched core.

## State And Persistence
The file mostly defines compile-time constants, type layouts, inline helpers, or extern declarations; persistent state lives in the subsystem implementation that includes it.

## Dependencies And Integration Points
Integrated by ARM architecture code and generic kernel subsystems that include this header. Direct dependencies include #include <asm/elf.h>.

## Risks And Edge Cases
Most risk is configuration and ABI drift: these headers are consumed by assembly, linker scripts, generic kernel code, or userspace-visible ABIs, so field layout and constants must remain synchronized with their callers.

## Test Signals
Primary signals are compile coverage for the relevant ARM Kconfig combinations plus boot/runtime tests of the subsystem that includes the header.
