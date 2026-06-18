# sources/distributed-fs/ceph-client/arch/m68k/kernel/relocate_kernel.S

## Purpose

`relocate_kernel.S` is the no-return physical-mode kexec relocation stub copied into the kexec control page by `machine_kexec.c`. It disables the current MMU mapping, copies destination pages according to the kimage indirection list, flushes caches, and jumps to the new kernel entry.

## Important APIs, Types, and Functions

The exported symbols are `relocate_new_kernel` and `relocate_new_kernel_size`. Inputs are stack arguments: relocation list pointer, new kernel start address, and packed `cpu_mmu_flags`. The file emits `.m68k_fixup` records to patch virtual-to-physical offsets for internal branch targets.

## Control Flow

The stub tests MMU flags for 68851/68030, 68040, or 68060 support. For 030-class MMUs it clears the enable bit in TC and jumps to the physical copy routine. For 040/060 it sets a temporary transparent mapping for its physical code, disables TC and transparent registers, then falls into copy. The copy loop follows kexec entries: indirection entries replace the pointer, destination entries set `a2`, source entries copy one page from `a3` to `a2`, and done entries break to cache flush. Cache flushing then uses CACR for 020/030 or `cpusha/cinva` for 040/060 before jumping to `start`.

## State and Persistence Behavior

The stub mutates CPU MMU/cache registers and destination physical memory pages. It consumes the kexec relocation list but does not return or preserve old kernel state.

## Dependencies and Integration Points

It depends on kexec indirection entry bit definitions, `PAGE_MASK`, `PAGE_SIZE`, m68k CPU/MMU boot flags, and module/fixup processing for `.m68k_fixup`. `machine_kexec.c` copies it into executable control memory and passes flags.

## Risks and Edge Cases

Wrong CPU/MMU flags can leave the old MMU enabled or disable it through the wrong instruction sequence. The copy loop assumes page-aligned source and destination entries and one-page copies. Cache flushing is essential before executing the new kernel; missing a CPU path can boot stale code.

## Test Signals

Successful kexec handoff on 030 and 040/060 builds, inspection of `relocate_new_kernel_size`, and trace or emulator checks that TC and transparent registers are cleared before jumping to the new entry.
