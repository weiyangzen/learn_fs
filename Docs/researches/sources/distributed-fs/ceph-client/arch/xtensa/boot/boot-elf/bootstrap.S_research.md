<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/boot/boot-elf/bootstrap.S -->
# sources/distributed-fs/ceph-client/arch/xtensa/boot/boot-elf/bootstrap.S

## Purpose
Reset-vector bootstrap for uncompressed Xtensa ELF images. It establishes a known processor state, optionally initializes the MMU before `vmlinux`, prepares a bootparam block, and jumps into the kernel image.

## Important APIs, Types, And Functions
Key labels are `_ResetVector`, `_bootparam`, `_SetupMMU`, and `reset`. It uses `initialize_mmu` from `asm/initialize_mmu.h` and constants from `asm/bootparam.h` and `asm/vectors.h`.

## Control Flow
The reset vector jumps to `_SetupMMU`, clears windowbase/windowstart for windowed cores, sets processor status, optionally invokes `initialize_mmu` when MMU initialization is not inside `vmlinux`, lowers interrupt level below debug, loads the kernel entry address (`CONFIG_KERNEL_LOAD_ADDRESS` for selected MMUv3 inside-vmlinux cases or `KERNELOFFSET` otherwise), sets bootparam pointer in `a2` when enabled, clears `a3/a4`, and jumps to the kernel.

## State And Persistence
State changes are CPU special registers and optional bootparam data embedded in the image. No durable persistence.

## Dependencies And Integration Points
Depends on Xtensa reset-vector semantics, ABI registers, MMU initialization macros, boot parameter parser, and kernel startup entry expectations.

## Risks And Edge Cases
Windowed register state, PS value, interrupt level, and MMU mapping must be correct before the jump. Wrong entry address selection breaks MMUv3 and U-Boot/KEXEC layouts.

## Test Signals
Boot uncompressed `Image.elf` with and without `CONFIG_PARSE_BOOTPARAM`, with inside-vmlinux and bootstrap MMU initialization, and verify early kernel entry.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/boot/boot-elf/bootstrap.S -->
