<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/Kconfig -->
# sources/distributed-fs/ceph-client/arch/xtensa/Kconfig

## Purpose
Defines the Xtensa architecture feature matrix and user-visible configuration: processor variant, MMU support, ABI choices, SMP, platform selection, boot parameters, semihosting, simulated disks, XIP, memory layout, vectors, highmem, and hibernation.

## Important APIs, Types, And Functions
Important symbols include `XTENSA`, `MMU`, `XTENSA_VARIANT_*`, `XTENSA_VARIANT_NAME`, `XTENSA_VARIANT_MMU`, `XTENSA_VARIANT_HAVE_PERF_EVENTS`, `XTENSA_FAKE_NMI`, `PFAULT`, `HAVE_SMP`, `SMP`, `NR_CPUS`, `KERNEL_ABI_*`, `USER_ABI_*`, `XTENSA_PLATFORM_*`, `USE_OF`, `PARSE_BOOTPARAM`, `INITIALIZE_XTENSA_MMU_INSIDE_VMLINUX`, `XIP_KERNEL`, `MEMMAP_CACHEATTR`, `KSEG_PADDR`, `KERNEL_LOAD_ADDRESS`, `XTENSA_VECTORS_*`, `HIGHMEM`, and `ARCH_FORCE_MAX_ORDER`.

## Control Flow
Kconfig selects generic kernel capabilities, chooses endianness from the compiler, selects a core variant directory, optionally enables MMU and perf features, controls ABI compiler flags through the Makefile, chooses one board platform, and derives memory layout constants consumed by headers and linker scripts.

## State And Persistence
The persistent output is `.config`, generated autoconf headers, and build-time feature selection. Runtime state is indirect through compiled code paths and memory layout constants.

## Dependencies And Integration Points
Feeds `arch/xtensa/Makefile`, `kmem_layout.h`, `initialize_mmu.h`, `page.h`, boot linker scripts, platform code, OF DTB builds, and generic kernel feature gates.

## Risks And Edge Cases
Incorrect variant names break include paths. ABI mismatches can make user signal delivery or kernel assembly invalid. KSEG and load-address misalignment can prevent boot. `MEMMAP_CACHEATTR` values are MMU-type specific. `XTENSA_FAKE_NMI` is safe only under strict interrupt-level constraints.

## Test Signals
Run `allyesconfig`/defconfig-style compile coverage for FSF, DC232B, DC233C, custom MMU/noMMU, ISS/XTFPGA/XT2000, call0/windowed ABI, SMP, highmem, OF, and XIP combinations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/Kconfig -->
