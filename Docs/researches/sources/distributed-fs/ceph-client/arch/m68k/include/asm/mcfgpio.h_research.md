# sources/distributed-fs/ceph-client/arch/m68k/include/asm/mcfgpio.h

## Purpose

`mcfgpio.h` provides ColdFire GPIO register addressing and generic GPIO glue. It belongs to the m68k architecture support inside the ceph-client Linux source snapshot, so its behavior is architecture/kernel plumbing rather than Ceph protocol logic. Source read size: 292 lines and 8144 bytes.

## Important APIs, Types, And Data

Primary surface: port read/write macros, `mcfgpio_bit()`, `mcfgpio_port()`, SETR/CLRR/PODR/PDDR/PPDR
helpers, and `__gpio_*` wrappers. Representative preprocessor definitions seen in the file are
`mcfgpio_h`, `MCFGPIO_PORTTYPE`, `MCFGPIO_PORTSIZE`, `mcfgpio_read(port)`, `mcfgpio_write(data,
port)`, `mcfgpio_bit(gpio)`, `mcfgpio_port(gpio)`, `MCFGPIO_SCR_START`, `MCFGPIO_SETR_PORT(gpio)`,
`MCFGPIO_CLRR_PORT(gpio)`. Representative callable or assembly entry symbols are
`__mcfgpio_get_value`, `__mcfgpio_set_value`, `__mcfgpio_direction_input`,
`__mcfgpio_direction_output`, `__mcfgpio_request`, `__mcfgpio_free`, `__gpio_get_value`,
`__gpio_set_value`, `__gpio_to_irq`, `gpio_direction_input`, `gpio_direction_output`,
`gpio_request`, `gpio_free`, `__mcfgpio_ppdr`. Representative structs/unions/enums are none. Direct
includes are `linux/gpio.h`.

## Control Flow And Integration

integrates ColdFire GPIO banks with Linux gpiolib and optional IRQ mapping. Most headers in this
subset contribute through compile-time selection and inline helpers; the C and assembly files add
runtime entry points. Control reaches these definitions from generic Linux subsystems such as memory
management, scheduler context switching, traps, syscall dispatch, DMA mapping, console setup,
procfs, module loading, or board-specific drivers.

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

SoC-family conditional port sizes and register layouts differ; GPIO numbers crossing a port boundary
are the main edge case. Additional cross-cutting risks are conditional compilation drift between MMU
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
