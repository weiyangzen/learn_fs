## sources/distributed-fs/ceph-client/arch/arm64/include/asm/fixmap.h

Purpose: defines arm64 fixed virtual address slots used during early boot and runtime special mappings.

Important APIs/types/functions: defines fixmap address bounds, slot enums for early console, FDT, PCI IO, fixmap page tables, and permanent/temporary mappings; exposes fixmap helpers through generic fixmap infrastructure.

Control flow: early boot maps physical resources into predetermined virtual slots, then later code uses fixed slots for special-purpose mappings.

State and persistence: page table entries for fixmap slots persist while mappings are active; early temporary mappings are overwritten.

Dependencies and integration: depends on memory layout, page-table levels, EFI/early ioremap, PCI IO, FDT setup, and generic fixmap.

Risks: slot overlap or wrong address calculation corrupts early mappings and can break boot before normal VM is available. Test signals are earlycon, DTB parsing, EFI boot, KASAN/VMAP configurations, and page-table debug.
