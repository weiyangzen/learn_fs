# sources/distributed-fs/ceph-client/arch/m68k/include/asm/sun3xflop.h

## Purpose

`sun3xflop.h` adapts the generic floppy driver to Sun3x FDC hardware. It belongs to the m68k architecture support inside the ceph-client Linux source snapshot, so its behavior is architecture/kernel plumbing rather than Ceph protocol logic. Source read size: 263 lines and 5757 bytes.

## Important APIs, Types, And Data

Primary surface: FDC IRQ/control bits, private DMA-ish state, inb/outb callbacks, request IRQ hook,
initialization and eject helpers. Representative preprocessor definitions seen in the file are
`__ASM_SUN3X_FLOPPY_H`, `SUN3X_FDC_IRQ`, `FCR_TC`, `FCR_EJECT`, `FCR_MTRON`, `FCR_DSEL1`,
`FCR_DSEL0`, `release_region(X, Y)`, `request_region(X, Y, Z)`, `NO_FLOPPY_ASSEMBLER`,
`fd_eject(drive)`. Representative callable or assembly entry symbols are `sun3x_82072_fd_inb`,
`sun3x_82072_fd_outb`, `sun3xflop_hardint`, `sun3xflop_request_irq`, `floppy_set_flags`,
`sun3xflop_init`, `sun3x_eject`. Representative structs/unions/enums are `sun3xflop_private`. Direct
includes are `asm/irq.h`, `asm/page.h`, `asm/sun3x.h`, `linux/pgtable.h`.

## Control Flow And Integration

included by the floppy driver for Sun3x builds. Most headers in this subset contribute through
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

uses global driver macros and direct register access; motor/select/eject bits are hardware-
sensitive. Additional cross-cutting risks are conditional compilation drift between MMU families,
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
