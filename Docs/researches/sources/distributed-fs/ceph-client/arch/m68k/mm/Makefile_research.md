# sources/distributed-fs/ceph-client/arch/m68k/mm/Makefile

## Purpose
Selects m68k memory-management objects according to MMU family configuration.

## APIs, Flow, And State
Always builds `init.o`. With `CONFIG_MMU`, it adds `cache.o` and `fault.o`. Motorola MMU builds add `kmap.o`, `memory.o`, `motorola.o`, and `hwtest.o`; Sun3 builds add `sun3kmap.o`, `sun3mmu.o`, and `hwtest.o`; ColdFire MMU builds add `kmap.o`, `memory.o`, and `mcfmmu.o`. There is no runtime state in this file.

## Dependencies And Integration
Consumed by Kbuild for the m68k architecture. It connects the common page-fault/cache code in this work item to the broader MMU implementations and platform-specific memory setup.

## Risks And Test Signals
Incorrect object selection can either omit required MMU handlers or link incompatible implementations. Build-matrix coverage across `CONFIG_MMU_MOTOROLA`, `CONFIG_MMU_SUN3`, and `CONFIG_MMU_COLDFIRE` is the primary test signal, followed by boot-time paging and cache behavior.
