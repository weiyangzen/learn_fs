<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/asm/initialize_mmu.h -->
# sources/distributed-fs/ceph-client/arch/xtensa/include/asm/initialize_mmu.h

## Purpose
Provides assembly macros to initialize Xtensa MMU/cache attributes before or during early kernel startup, including MMUv3 spanning-way remapping and noMMU cache-attribute setup.

## Important APIs, Types, And Functions
Defines `CA_BYPASS`, `CA_WRITEBACK`, `initialize_mmu`, and `initialize_cacheattr`.

## Control Flow
`initialize_mmu` optionally initializes `atomctl` for S32C1I/cache behavior, then for MMUv3 with PTP MMU and spanning way creates a temporary mapping, jumps through it, invalidates old TLB mappings, programs ITLB/DTLB configuration, installs cached and bypass KSEG mappings, optional 512M second mappings, KIO mappings, jumps to final mapping, removes the temporary mapping, and clears `ptevaddr`. `initialize_cacheattr` programs MPU or TLB cache attributes for noMMU/TLB systems from `CONFIG_MEMMAP_CACHEATTR`.

## State And Persistence
It mutates hardware TLB, MPU/cache attribute, AtomCtl, and processor state. These mappings persist into early kernel execution.

## Dependencies And Integration Points
Depends on Kconfig memory layout, page attribute bits, variant MMU features, vector relocation support, and boot/head assembly.

## Risks And Edge Cases
MMUv3 requires relocatable vectors. Temporary mapping address must not collide with the kernel load address. KSEG physical address alignment is critical. Wrong cache attributes can break atomics, instruction fetch, or device access.

## Test Signals
Boot MMUv2/MMUv3, 128M/256M/512M KSEG, noMMU MPU/TLB cacheattr configurations, S32C1I atomics, and XIP/non-XIP layouts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/asm/initialize_mmu.h -->
