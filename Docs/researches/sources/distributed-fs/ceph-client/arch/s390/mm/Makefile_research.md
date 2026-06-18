# sources/distributed-fs/ceph-client/arch/s390/mm/Makefile

## Purpose
Build manifest for s390 architecture memory-management code.

## Important APIs, Types, And Functions
Core built-in objects include initialization, fault handling, extmem, mmap, vmem, maccess, page state, page attributes, page tables, page allocation, and exception tables. Optional objects are `cmm.o`, `physaddr.o`, `hugetlbpage.o`, `dump_pagetables.o`, and `pfault.o`. `gmap_helpers.o` is included when `CONFIG_KVM` is set to built-in or module by normalizing module state with `$(subst m,y,$(CONFIG_KVM))`.

## Control Flow And State
Control is entirely build-time and Kconfig-driven. The KVM gmap helper rule ensures architecture memory helpers are available even when KVM is modular.

## Dependencies And Integration
Integrates with the kernel build system, s390 MM subsystem, KVM gmap support, CMM, hugetlb, page-table dump, debug virtual address checking, and pfault.

## Risks And Test Signals
Risks include missing memory-management objects under uncommon configs, wrong KVM module/built-in dependency behavior, and feature objects omitted from s390 builds. Signals include s390 defconfig/allmodconfig builds, KVM module builds, and boot tests for CMM/PFAULT/HUGETLB/PTDUMP configurations.
