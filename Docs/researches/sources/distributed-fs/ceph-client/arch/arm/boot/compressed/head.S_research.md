<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/boot/compressed/head.S -->
# sources/distributed-fs/ceph-client/arch/arm/boot/compressed/head.S

## Purpose
This is the ARM zImage decompressor entry and relocation assembly. It handles legacy boot headers, ARM/Thumb state, optional EFI header data, AUTO_ZRELADDR memory-base calculation, appended DTB and ATAG-to-FDT handling, self-relocation, GOT/BSS fixups, cache/MMU/MPU setup and teardown, decompressor invocation, HYP-mode handoff, and final branch into the decompressed kernel.

## Important APIs, Types, and Functions
Assembly-visible symbols include `efi_enter_kernel`, `start`, `not_angel`, `restart`, `dtb_check_done`, `wont_overwrite`, `not_relocated`, `LC0`, `LC1`, `params`, `cache_on`, `__armv4_mpu_cache_on`, `__armv3_mpu_cache_on`, `__setup_mmu`, `__armv6_mmu_cache_on`, `__arm926ejs_mmu_cache_on`, `__armv4_mmu_cache_on`, `__armv7_mmu_cache_on`, `__fa526_cache_on`, `__common_mmu_cache_on`, `call_cache_fn`, `proc_types`, `cache_off`, `__armv4_mpu_cache_off`, and 24 more. Included source files are `<linux/linkage.h>`, `<asm/assembler.h>`, `<asm/v7m.h>`, `"efi-header.S"`. Embedded binary inputs are none.

## Control Flow
Execution enters at `start`, preserves boot registers, normalizes CPU mode, computes the final kernel load address, optionally validates it through FDT memory data, decides whether a temporary page table/cache setup is safe, relocates the decompressor if it would overlap the inflated kernel, fixes GOT and BSS pointers, clears BSS, calls `decompress_kernel`, flushes caches, disables cache/MMU state, and then jumps to the kernel entry or HYP re-entry path. Processor tables near the end dispatch CPU-specific cache on/off/flush routines.

## State and Persistence Behavior
State is register, cache/MMU, copied-memory, or linked-binary state during the boot wrapper/decompressor phase. It is not persistent storage, but it determines the exact payload bytes, CPU mode, early memory layout, and handoff arguments observed by the decompressed kernel.

## Dependencies and Integration Points
Dependencies include ARM assembler macros, `arch/arm/boot/compressed/Makefile`, linker scripts, binary payload generation, bootloader register ABI, CPU control registers, optional EFI/HYP paths, and shared ARM library assembly where included.

## Risks
Risks are severe: wrong relocation bounds can overwrite the decompressor or inflated kernel, bad GOT/BSS fixups break C code, incorrect cache maintenance can execute stale instructions, appended DTB growth can collide with BSS, and boot-mode/HYP handling mistakes can strand the CPU before the kernel entry point.

## Test Signals
Boot zImage on ARMv4/v5/v6/v7, Thumb2, BE8, AUTO_ZRELADDR, appended-DTB, ATAG compatibility, EFI stub, and HYP-mode configurations. Use `DEBUG_UNCOMPRESS` to inspect relocation and DTB diagnostics, and verify cache flush/off paths on real hardware or accurate emulators.

Source read size: 1531 lines, 39017 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/boot/compressed/head.S -->
