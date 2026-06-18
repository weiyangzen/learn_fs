# sources/distributed-fs/ceph-client/arch/m68k/include/asm/zorro.h

## Purpose

`zorro.h` maps Amiga Zorro bus I/O helpers onto raw I/O and kmap helpers. It belongs to the m68k architecture support inside the ceph-client Linux source snapshot, so its behavior is architecture/kernel plumbing rather than Ceph protocol logic. Source read size: 47 lines and 1222 bytes.

## Important APIs, Types, And Data

Primary surface: `z_read*`, `z_write*`, memset/memcpy I/O aliases, and `z_ioremap()`/unmap wrappers.
Representative preprocessor definitions seen in the file are `_ASM_M68K_ZORRO_H`, `z_readb`,
`z_readw`, `z_readl`, `z_writeb`, `z_writew`, `z_writel`, `z_memset_io(a,b,c)`,
`z_memcpy_fromio(a,b,c)`, `z_memcpy_toio(a,b,c)`, `z_unmap`, `z_iounmap`, `z_ioremap`.
Representative callable or assembly entry symbols are `z_remap_nocache_ser`,
`z_remap_nocache_nonser`, `z_remap_writethrough`, `z_remap_fullcache`. Representative
structs/unions/enums are none. Direct includes are `asm/kmap.h`, `asm/raw_io.h`.

## Control Flow And Integration

used by Amiga Zorro bus drivers. Most headers in this subset contribute through compile-time
selection and inline helpers; the C and assembly files add runtime entry points. Control reaches
these definitions from generic Linux subsystems such as memory management, scheduler context
switching, traps, syscall dispatch, DMA mapping, console setup, procfs, module loading, or board-
specific drivers.

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

Zorro bus byte ordering and memory window mapping need hardware or emulator validation. Additional
cross-cutting risks are conditional compilation drift between MMU families, inline assembly
constraints that differ between 68000/020/030/040/060/ColdFire, register-endianness mistakes on
memory-mapped buses, and ABI changes to exported bootinfo, ptrace, signal, stat, or syscall
structures.

## Test Signals

Useful signals are m68k `defconfig`, allmodconfig where practical, and targeted builds for ColdFire
MMU, no-MMU, Sun3, Motorola MMU, Q40, Macintosh, Amiga, MVME, HP300 and virt configurations. Runtime
validation should cover boot to userspace, syscall tracing/seccomp, signal delivery and return,
fork/clone/vfork, module loading, DMA cache coherency tests, serial/early console output, interrupt
delivery, TLB flush stress, and userspace ABI checks for ptrace, stat, signal, cacheflush, and
bootinfo records.
