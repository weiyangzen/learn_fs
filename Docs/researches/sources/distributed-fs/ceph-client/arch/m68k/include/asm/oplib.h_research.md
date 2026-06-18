# sources/distributed-fs/ceph-client/arch/m68k/include/asm/oplib.h

## Purpose

`oplib.h` declares Sun PROM library functions and device enums. It belongs to the m68k architecture support inside the ceph-client Linux source snapshot, so its behavior is architecture/kernel plumbing rather than Ceph protocol logic. Source read size: 294 lines and 9812 bytes.

## Important APIs, Types, And Data

Primary surface: PROM init, I/O, reboot/halt, node/property walking, memory allocation, console, CPU
control, range adjustment, and boot argument helpers. Representative preprocessor definitions seen
in the file are `__SPARC_OPLIB_H`. Representative callable or assembly entry symbols are
`prom_init`, `prom_getbootargs`, `prom_mapio`, `prom_unmapio`, `prom_devopen`, `prom_devclose`,
`prom_seek`, `prom_meminfo`, `prom_reboot`, `prom_feval`, `prom_cmdline`, `prom_halt`,
`prom_setsync`, `prom_get_idprom`. Representative structs/unions/enums are `prom_major_version`,
`prom_input_device`, `prom_output_device`. Direct includes are `asm/openprom.h`, `linux/compiler.h`.

## Control Flow And Integration

implemented by Sun PROM support and consumed by Sun platform setup, console, and device discovery.
Most headers in this subset contribute through compile-time selection and inline helpers; the C and
assembly files add runtime entry points. Control reaches these definitions from generic Linux
subsystems such as memory management, scheduler context switching, traps, syscall dispatch, DMA
mapping, console setup, procfs, module loading, or board-specific drivers.

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

PROM calls run before normal kernel services; callers must treat return values and firmware strings
as unreliable. Additional cross-cutting risks are conditional compilation drift between MMU
families, inline assembly constraints that differ between 68000/020/030/040/060/ColdFire, register-
endianness mistakes on memory-mapped buses, and ABI changes to exported bootinfo, ptrace, signal,
stat, or syscall structures.

## Test Signals

Useful signals are m68k `defconfig`, allmodconfig where practical, and targeted builds for ColdFire
MMU, no-MMU, Sun3, Motorola MMU, Q40, Macintosh, Amiga, MVME, HP300 and virt configurations. Runtime
validation should cover boot to userspace, syscall tracing/seccomp, signal delivery and return,
fork/clone/vfork, module loading, DMA cache coherency tests, serial/early console output, interrupt
delivery, TLB flush stress, and userspace ABI checks for ptrace, stat, signal, cacheflush, and
bootinfo records.
