# sources/distributed-fs/ceph-client/arch/m68k/include/asm/seccomp.h

## Purpose

`seccomp.h` declares m68k seccomp audit architecture identifiers. It belongs to the m68k architecture support inside the ceph-client Linux source snapshot, so its behavior is architecture/kernel plumbing rather than Ceph protocol logic. Source read size: 11 lines and 283 bytes.

## Important APIs, Types, And Data

Primary surface: `SECCOMP_ARCH_NATIVE`, native syscall table number, and native architecture name.
Representative preprocessor definitions seen in the file are `_ASM_SECCOMP_H`,
`SECCOMP_ARCH_NATIVE`, `SECCOMP_ARCH_NATIVE_NR`, `SECCOMP_ARCH_NATIVE_NAME`. Representative callable
or assembly entry symbols are none. Representative structs/unions/enums are none. Direct includes
are `asm-generic/seccomp.h`.

## Control Flow And Integration

used by generic seccomp filter validation and audit. Most headers in this subset contribute through
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

must match the syscall ABI exposed by UAPI `unistd.h`. Additional cross-cutting risks are
conditional compilation drift between MMU families, inline assembly constraints that differ between
68000/020/030/040/060/ColdFire, register-endianness mistakes on memory-mapped buses, and ABI changes
to exported bootinfo, ptrace, signal, stat, or syscall structures.

## Test Signals

Useful signals are m68k `defconfig`, allmodconfig where practical, and targeted builds for ColdFire
MMU, no-MMU, Sun3, Motorola MMU, Q40, Macintosh, Amiga, MVME, HP300 and virt configurations. Runtime
validation should cover boot to userspace, syscall tracing/seccomp, signal delivery and return,
fork/clone/vfork, module loading, DMA cache coherency tests, serial/early console output, interrupt
delivery, TLB flush stress, and userspace ABI checks for ptrace, stat, signal, cacheflush, and
bootinfo records.
