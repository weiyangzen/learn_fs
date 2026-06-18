# sources/distributed-fs/ceph-client/arch/x86/boot/pmjump.S

Purpose: performs the final architectural switch from 16-bit real mode into 32-bit protected mode and jumps to the kernel entry point.

Important APIs and state: defines `protected_mode_jump(u32 entrypoint, u32 bootparams)`. No persistent data.

Control flow: saves boot_params pointer in `%esi`, computes real-mode segment base, sets PE in CR0, far-jumps to 32-bit code segment, loads flat data segments, adjusts stack to linear address, loads TR and LDTR, clears extension registers, and jumps to the entrypoint in `%eax`.

Dependencies and integration: called by `pm.c` after GDT/IDT setup. Uses boot segment selectors from asm headers and assumes the GDT entries loaded by `setup_gdt()`.

Risks and test signals: incorrect segment base or selector values hang immediately. Test by BIOS booting bzImage, debug tracing around protected-mode entry, and QEMU CPU models including old 386/486 serialization behavior.
