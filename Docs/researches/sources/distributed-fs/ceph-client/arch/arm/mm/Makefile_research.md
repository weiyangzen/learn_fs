# sources/distributed-fs/ceph-client/arch/arm/mm/Makefile

Purpose: builds the ARM-specific memory-management objects according to the Kconfig CPU, MMU, debug, sanitizer, and outer-cache selections. It ties generic ARM MM files to the exact abort, cache, copy-page, TLB, processor, and outer-cache implementations selected for the target kernel.

Important APIs/types/functions: key build groups include always-built core objects `extable.o`, `fault.o`, `init.o`, `iomap.o`, `dma-mapping$(MMUEXT).o`, `cache.o`, and `tlb.o`; MMU-only objects `fault-armv.o`, `flush.o`, `idmap.o`, `ioremap.o`, `mmap.o`, `pgd.o`, `mmu.o`, and `pageattr.o`; no-MMU objects `nommu.o`, `pmsa-v7.o`, and `pmsa-v8.o`; abort objects `abort-*.o`; cache objects `cache-*.o`; TLB objects `tlb-*.o`; CPU processor objects `proc-*.o`; and outer cache objects such as `l2c-common.o`, `cache-l2x0.o`, and vendor-specific controllers.

Control flow: kbuild evaluates `obj-y` and `obj-$(CONFIG_...)` assignments, compiling and linking exactly the objects enabled by the configuration. It also disables KASAN for `mmu.o` and `physaddr.o` where instrumentation would interfere with low-level address translation paths.

State and persistence: the Makefile has no runtime state. Its persistent effect is the link composition of `arch/arm/mm`, including which entry points are available for processor dispatch tables and which outer-cache hooks can be initialized at boot.

Dependencies and integration points: consumes Kconfig symbols from this directory and broader kernel configuration. It integrates with kbuild, ARM processor support, fault handling, DMA mapping, KASAN, CFI, debug virtual address checks, module symbol export, and device-tree-driven outer cache initialization.

Risks: object selection must match Kconfig `select` chains exactly. A missing object for a selected CPU model will fail the build; a wrong object can compile but leave exception vectors, cache maintenance, or TLB routines incompatible with the CPU. Sanitizer overrides are important because instrumentation in early MM code can recurse through unmapped or not-yet-valid memory paths.

Test signals: run build coverage for representative `multi_v7_defconfig`, no-MMU, ARMv4/v5 legacy, LPAE, KASAN, CFI, and outer-cache configurations. Link-map inspection should show only the selected abort/cache/TLB/copy/proc objects. Runtime boot tests should exercise page faults, DMA mapping, module loading, CPU hotplug, and suspend/resume when corresponding objects are included.
