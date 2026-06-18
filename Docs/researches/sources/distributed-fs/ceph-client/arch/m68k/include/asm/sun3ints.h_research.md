# sources/distributed-fs/ceph-client/arch/m68k/include/asm/sun3ints.h

## Purpose

`sun3ints.h` declares Sun3 interrupt vector constants and control functions. It belongs to the m68k architecture support inside the ceph-client Linux source snapshot, so its behavior is architecture/kernel plumbing rather than Ceph protocol logic. Source read size: 37 lines and 989 bytes.

## Important APIs, Types, And Data

Primary surface: Sun3 vector counts, floppy/VME SCSI/CG vectors, IRQ enable/disable/init functions,
and interrupt master enable/disable. Representative preprocessor definitions seen in the file are
`SUN3INTS_H`, `SUN3_INT_VECS`, `SUN3_VEC_FLOPPY`, `SUN3_VEC_VMESCSI0`, `SUN3_VEC_VMESCSI1`,
`SUN3_VEC_CG`. Representative callable or assembly entry symbols are `sun3_enable_irq`,
`sun3_disable_irq`, `sun3_init_IRQ`, `sun3_enable_interrupts`, `sun3_disable_interrupts`.
Representative structs/unions/enums are none. Direct includes are `asm/intersil.h`, `asm/irq.h`,
`asm/oplib.h`, `asm/traps.h`, `linux/interrupt.h`, `linux/types.h`.

## Control Flow And Integration

used by Sun3 interrupt setup and device drivers. Most headers in this subset contribute through
compile-time selection and inline helpers; the C and assembly files add runtime entry points.
Control reaches these definitions from generic Linux subsystems such as memory management, scheduler
context switching, traps, syscall dispatch, DMA mapping, console setup, procfs, module loading, or
board-specific drivers.

## State And Persistence Behavior

The file itself does not persist external data unless it defines C storage or build/linker output,
but its interfaces describe persistent kernel state: page tables, PTE bits, ASIDs/contexts, saved
exception frames, thread flags, bootinfo records, hardware register state, DMA cache state, or UAPI
structures. Hardware-facing headers persist state by programming memory-mapped registers; UAPI
headers persist through ABI compatibility with bootloaders, libc, debuggers, and old binaries.

## Dependencies

Dependencies are primarily the direct include list above, the active m68k Kconfig family
(`CONFIG_MMU`, `CONFIG_COLDFIRE`, `CONFIG_SUN3`, machine selections, modules, PCI, DMA and early
console options), and matching C/assembly implementations elsewhere under `arch/m68k`. UAPI files
also depend on bootloader and userspace agreement about numeric constants and struct layouts.

## Risks And Edge Cases

PROM and Intersil timer dependencies mean early IRQ tests require real or accurate emulated Sun3
hardware. Additional cross-cutting risks are conditional compilation drift between MMU families,
inline assembly constraints that differ between 68000/020/030/040/060/ColdFire, register-endianness
mistakes on memory-mapped buses, and ABI changes to exported bootinfo, ptrace, signal, stat, or
syscall structures.

## Test Signals

Useful signals are m68k `defconfig`, allmodconfig where practical, and targeted builds for ColdFire
MMU, no-MMU, Sun3, Motorola MMU, Q40, Macintosh, Amiga, MVME, HP300 and virt configurations. Runtime
validation should cover boot to userspace, syscall tracing/seccomp, signal delivery and return,
fork/clone/vfork, module loading, DMA cache coherency tests, serial/early console output, interrupt
delivery, TLB flush stress, and userspace ABI checks for ptrace, stat, signal, cacheflush, and
bootinfo records.
