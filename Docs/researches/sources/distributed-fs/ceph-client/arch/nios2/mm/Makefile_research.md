# sources/distributed-fs/ceph-client/arch/nios2/mm/Makefile

Purpose: selects the Nios II MM objects for cache, init, fault, ioremap, extable, TLB, DMA mapping, page
tables, user access, and MMU contexts.

Important APIs/types/functions: Build declarations: `obj-y=cacheflush.o`, `obj-y=dma-mapping.o`, `obj-y=extable.o`, `obj-y=fault.o`,
`obj-y=init.o`, `obj-y=ioremap.o`, `obj-y=mmu_context.o`, `obj-y=pgtable.o`, `obj-y=tlb.o`,
`obj-y=uaccess.o`.

Control flow: The build system reads this file during Kbuild traversal; object lists and targets determine which
architecture sources are compiled or packaged for the selected configuration.

State and persistence: Persistent effects are build artifacts only: selected objects, generated images, DTBs, or exported
headers. Runtime state is created by the compiled code, not by the make fragment itself.

Dependencies and integration points: Dependencies are mostly implicit architecture and generic kernel headers. Integration points include
generic Linux MM, irq, signal, ptrace, module, timekeeping, devicetree, syscall, and cache/TLB
subsystems plus Nios II control-register assembly. This source is part of the Nios II architecture
port under the vendored ceph-client kernel tree.

Risks: Risks are missing objects, stale generated-header dependencies, wrong boot target names, or
configuration drift that silently excludes required architecture code.

Test signals: Test signals are architecture defconfig builds, `make ARCH=... headers_install`, boot image
generation, DTB generation, and allmodconfig coverage for selected options.
