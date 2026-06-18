# sources/distributed-fs/ceph-client/arch/csky/mm/Makefile

Purpose: selects C-SKY memory-management objects according to cache, highmem, and TCM configuration.

Important APIs/types/functions: build rules: `ifeq ($(CONFIG_CPU_HAS_CACHEV2),y)`; `obj-y += cachev2.o`; `CFLAGS_REMOVE_cachev2.o = $(CC_FLAGS_FTRACE)`; `else`; `obj-y += cachev1.o`; `CFLAGS_REMOVE_cachev1.o = $(CC_FLAGS_FTRACE)`; `endif`; `obj-y += dma-mapping.o`

Control flow: Kbuild evaluates these object lists and conditionals at build time; runtime flow comes from the selected objects.

State and persistence: No runtime persistence in this file; it contributes compile-time symbols, declarations, constants, or object selection.

Dependencies and integration: Depends on Linux Kbuild/Kconfig evaluation and the configuration symbols or objects named by the rules.

Risks: Configuration drift can silently omit required objects or expose unsupported option combinations in cross-builds.

Test signals: C-SKY cross-build; defconfig, allyesconfig, and allmodconfig build checks; boot, mmap, page-fault, futex/locking, DMA, and usercopy stress tests.
