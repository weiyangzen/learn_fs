# Research: subset-b-000716

Grouped research for `subset-b-000716`. Each section is delimited for deterministic splitting into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/mcf_pgtable.h -->
# sources/distributed-fs/ceph-client/arch/m68k/include/asm/mcf_pgtable.h

## Purpose

`mcf_pgtable.h` defines ColdFire MMU page-table encodings and PTE helper operations. It belongs to the m68k architecture support inside the ceph-client Linux source snapshot, so its behavior is architecture/kernel plumbing rather than Ceph protocol logic. Source read size: 296 lines and 7194 bytes.

## Important APIs, Types, And Data

Primary surface: ColdFire page flag macros such as `CF_PAGE_VALID`, protection presets `PAGE_NONE`,
`PAGE_SHARED`, `PAGE_KERNEL`, PTE state helpers, swap-entry encoders, `kernel_pg_dir`, and PFN/PTE
conversion helpers. Representative preprocessor definitions seen in the file are `_MCF_PGTABLE_H`,
`CF_PAGE_LOCKED`, `CF_PAGE_EXEC`, `CF_PAGE_WRITABLE`, `CF_PAGE_READABLE`, `CF_PAGE_SYSTEM`,
`CF_PAGE_COPYBACK`, `CF_PAGE_NOCACHE`, `CF_CACHEMASK`, `CF_PAGE_MMUDR_MASK`, `_PAGE_NOCACHE030`,
`CF_PAGE_MMUTR_MASK`, `CF_PAGE_MMUTR_SHIFT`, `CF_PAGE_VALID`. Representative callable or assembly
entry symbols are `pte_modify`, `pgd_set`, `pte_none`, `pte_present`, `pte_clear`, `pmd_none2`,
`pmd_bad2`, `pmd_clear`, `pte_read`, `pte_write`, `pte_exec`, `pte_dirty`, `pte_young`,
`pte_wrprotect`. Representative structs/unions/enums are none. Direct includes are `asm/mcfmmu.h`,
`asm/page.h`.

## Control Flow And Integration

selected from the generic m68k pgtable wrappers when `CONFIG_COLDFIRE` and `CONFIG_MMU` are active;
consumed by fault handling, TLB miss code, memory setup, and context switch code. Most headers in
this subset contribute through compile-time selection and inline helpers; the C and assembly files
add runtime entry points. Control reaches these definitions from generic Linux subsystems such as
memory management, scheduler context switching, traps, syscall dispatch, DMA mapping, console setup,
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

hardware and fake software bits share the PTE word, so mask mistakes can write dirty/accessed or
swap-exclusive metadata into MMUDR/MMUTR fields. Additional cross-cutting risks are conditional
compilation drift between MMU families, inline assembly constraints that differ between
68000/020/030/040/060/ColdFire, register-endianness mistakes on memory-mapped buses, and ABI changes
to exported bootinfo, ptrace, signal, stat, or syscall structures.

## Test Signals

Useful signals are m68k `defconfig`, allmodconfig where practical, and targeted builds for ColdFire
MMU, no-MMU, Sun3, Motorola MMU, Q40, Macintosh, Amiga, MVME, HP300 and virt configurations. Runtime
validation should cover boot to userspace, syscall tracing/seccomp, signal delivery and return,
fork/clone/vfork, module loading, DMA cache coherency tests, serial/early console output, interrupt
delivery, TLB flush stress, and userspace ABI checks for ptrace, stat, signal, cacheflush, and
bootinfo records.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/mcf_pgtable.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/mcfclk.h -->
# sources/distributed-fs/ceph-client/arch/m68k/include/asm/mcfclk.h

## Purpose

`mcfclk.h` declares small ColdFire clock-provider data structures. It belongs to the m68k architecture support inside the ceph-client Linux source snapshot, so its behavior is architecture/kernel plumbing rather than Ceph protocol logic. Source read size: 48 lines and 961 bytes.

## Important APIs, Types, And Data

Primary surface: `struct clk`, `struct clk_ops`, `DEFINE_CLK()` variants, and init state helpers for
enabled or disabled clocks. Representative preprocessor definitions seen in the file are `mcfclk_h`,
`DEFINE_CLK(clk_bank, clk_name, clk_slot, clk_rate)`, `DEFINE_CLK(clk_ref, clk_name, clk_rate)`.
Representative callable or assembly entry symbols are `__clk_init_enabled`, `__clk_init_disabled`.
Representative structs/unions/enums are `clk`, `clk_ops`. Direct includes are none.

## Control Flow And Integration

feeds ColdFire platform clock registration and platform devices that need fixed-rate or banked clock
handles. Most headers in this subset contribute through compile-time selection and inline helpers;
the C and assembly files add runtime entry points. Control reaches these definitions from generic
Linux subsystems such as memory management, scheduler context switching, traps, syscall dispatch,
DMA mapping, console setup, procfs, module loading, or board-specific drivers.

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

macro signatures differ with clock-bank support, so board files must match the configured SoC clock
model. Additional cross-cutting risks are conditional compilation drift between MMU families, inline
assembly constraints that differ between 68000/020/030/040/060/ColdFire, register-endianness
mistakes on memory-mapped buses, and ABI changes to exported bootinfo, ptrace, signal, stat, or
syscall structures.

## Test Signals

Useful signals are m68k `defconfig`, allmodconfig where practical, and targeted builds for ColdFire
MMU, no-MMU, Sun3, Motorola MMU, Q40, Macintosh, Amiga, MVME, HP300 and virt configurations. Runtime
validation should cover boot to userspace, syscall tracing/seccomp, signal delivery and return,
fork/clone/vfork, module loading, DMA cache coherency tests, serial/early console output, interrupt
delivery, TLB flush stress, and userspace ABI checks for ptrace, stat, signal, cacheflush, and
bootinfo records.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/mcfclk.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/mcfdma.h -->
# sources/distributed-fs/ceph-client/arch/m68k/include/asm/mcfdma.h

## Purpose

`mcfdma.h` names ColdFire DMA controller register offsets and command/status bits. It belongs to the m68k architecture support inside the ceph-client Linux source snapshot, so its behavior is architecture/kernel plumbing rather than Ceph protocol logic. Source read size: 122 lines and 6662 bytes.

## Important APIs, Types, And Data

Primary surface: register offsets `MCFDMA_SAR`, `DAR`, `DCR`, `BCR`, `DSR`, `DIVR` plus transfer-
size, address increment, bandwidth, interrupt and done/error bits. Representative preprocessor
definitions seen in the file are `mcfdma_h`, `MCFDMA_SAR`, `MCFDMA_DAR`, `MCFDMA_DCR`, `MCFDMA_BCR`,
`MCFDMA_DSR`, `MCFDMA_DIVR`, `MCFDMA_DCR_INT`, `MCFDMA_DCR_EEXT`, `MCFDMA_DCR_CS`, `MCFDMA_DCR_AA`,
`MCFDMA_DCR_BWC_MASK`, `MCFDMA_DCR_BWC_512`, `MCFDMA_DCR_BWC_1024`. Representative callable or
assembly entry symbols are none. Representative structs/unions/enums are none. Direct includes are
none.

## Control Flow And Integration

used by ColdFire DMA drivers and platform code for memory-mapped DMA programming. Most headers in
this subset contribute through compile-time selection and inline helpers; the C and assembly files
add runtime entry points. Control reaches these definitions from generic Linux subsystems such as
memory management, scheduler context switching, traps, syscall dispatch, DMA mapping, console setup,
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

wrong width/stride or status-bit clearing can acknowledge the wrong DMA condition or corrupt device
memory. Additional cross-cutting risks are conditional compilation drift between MMU families,
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/mcfdma.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/mcfgpio.h -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/mcfgpio.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/mcfintc.h -->
# sources/distributed-fs/ceph-client/arch/m68k/include/asm/mcfintc.h

## Purpose

`mcfintc.h` defines ColdFire interrupt-controller priority/vector registers and mask helpers. It belongs to the m68k architecture support inside the ceph-client Linux source snapshot, so its behavior is architecture/kernel plumbing rather than Ceph protocol logic. Source read size: 90 lines and 3161 bytes.

## Important APIs, Types, And Data

Primary surface: `MCFSIM_ICR_*` priority values, external interrupt numbers, `mcf_mapirq2imr()`,
`mcf_autovector()`, `mcf_setimr()`, and `mcf_clrimr()`. Representative preprocessor definitions seen
in the file are `mcfintc_h`, `MCFSIM_ICR_AUTOVEC`, `MCFSIM_ICR_LEVEL0`, `MCFSIM_ICR_LEVEL1`,
`MCFSIM_ICR_LEVEL2`, `MCFSIM_ICR_LEVEL3`, `MCFSIM_ICR_LEVEL4`, `MCFSIM_ICR_LEVEL5`,
`MCFSIM_ICR_LEVEL6`, `MCFSIM_ICR_LEVEL7`, `MCFSIM_ICR_PRI0`, `MCFSIM_ICR_PRI1`, `MCFSIM_ICR_PRI2`,
`MCFSIM_ICR_PRI3`. Representative callable or assembly entry symbols are `mcf_mapirq2imr`,
`mcf_autovector`, `mcf_setimr`, `mcf_clrimr`. Representative structs/unions/enums are none. Direct
includes are none.

## Control Flow And Integration

used by ColdFire board and IRQ setup code to translate Linux IRQs into SIM interrupt-mask bits. Most
headers in this subset contribute through compile-time selection and inline helpers; the C and
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

autovector and IMR mapping are SoC-specific; bad mapping can leave lines masked or acknowledge the
wrong vector. Additional cross-cutting risks are conditional compilation drift between MMU families,
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/mcfintc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/mcfmmu.h -->
# sources/distributed-fs/ceph-client/arch/m68k/include/asm/mcfmmu.h

## Purpose

`mcfmmu.h` describes the ColdFire MMU register block and low-level accessors. It belongs to the m68k architecture support inside the ceph-client Linux source snapshot, so its behavior is architecture/kernel plumbing rather than Ceph protocol logic. Source read size: 114 lines and 3762 bytes.

## Important APIs, Types, And Data

Primary surface: MMU register offsets, `MMUCR`, `MMUOR`, `MMUSR`, `MMUTR`, `MMUDR` bitfields,
`mmu_read()`, `mmu_write()`, `cf_bootmem_alloc()`, `cf_mmu_context_init()`, and `cf_tlb_miss()`.
Representative preprocessor definitions seen in the file are `MCFMMU_H`, `MMUBASE`, `MMUCR`,
`MMUOR`, `MMUSR`, `MMUAR`, `MMUTR`, `MMUDR`, `MMUCR_EN`, `MMUCR_ASM`, `MMUOR_UAA`, `MMUOR_ACC`,
`MMUOR_RD`, `MMUOR_WR`. Representative callable or assembly entry symbols are `mmu_read`,
`mmu_write`, `cf_bootmem_alloc`, `cf_mmu_context_init`, `cf_tlb_miss`. Representative
structs/unions/enums are none. Direct includes are none.

## Control Flow And Integration

used by ColdFire TLB miss, boot memory setup, and context-switch code. Most headers in this subset
contribute through compile-time selection and inline helpers; the C and assembly files add runtime
entry points. Control reaches these definitions from generic Linux subsystems such as memory
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

inline register access assumes the memory-mapped MMU base and register semantics are correct for the
selected ColdFire core. Additional cross-cutting risks are conditional compilation drift between MMU
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/mcfmmu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/mcfpit.h -->
# sources/distributed-fs/ceph-client/arch/m68k/include/asm/mcfpit.h

## Purpose

`mcfpit.h` defines ColdFire periodic interrupt timer registers. It belongs to the m68k architecture support inside the ceph-client Linux source snapshot, so its behavior is architecture/kernel plumbing rather than Ceph protocol logic. Source read size: 51 lines and 2278 bytes.

## Important APIs, Types, And Data

Primary surface: `MCFPIT_PCSR`, `PMR`, `PCNTR`, prescaler constants, enable/interrupt/reload flags,
and output/control bits. Representative preprocessor definitions seen in the file are `mcfpit_h`,
`MCFPIT_PCSR`, `MCFPIT_PMR`, `MCFPIT_PCNTR`, `MCFPIT_PCSR_CLK1`, `MCFPIT_PCSR_CLK2`,
`MCFPIT_PCSR_CLK4`, `MCFPIT_PCSR_CLK8`, `MCFPIT_PCSR_CLK16`, `MCFPIT_PCSR_CLK32`,
`MCFPIT_PCSR_CLK64`, `MCFPIT_PCSR_CLK128`, `MCFPIT_PCSR_CLK256`, `MCFPIT_PCSR_CLK512`.
Representative callable or assembly entry symbols are none. Representative structs/unions/enums are
none. Direct includes are none.

## Control Flow And Integration

used by ColdFire clockevent/clocksource setup and board timer code. Most headers in this subset
contribute through compile-time selection and inline helpers; the C and assembly files add runtime
entry points. Control reaches these definitions from generic Linux subsystems such as memory
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

timer frequency depends on prescaler and bus-clock assumptions; incorrect `PCSR` programming loses
scheduler ticks. Additional cross-cutting risks are conditional compilation drift between MMU
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/mcfpit.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/mcfqspi.h -->
# sources/distributed-fs/ceph-client/arch/m68k/include/asm/mcfqspi.h

## Purpose

`mcfqspi.h` declares platform data for ColdFire queued SPI. It belongs to the m68k architecture support inside the ceph-client Linux source snapshot, so its behavior is architecture/kernel plumbing rather than Ceph protocol logic. Source read size: 42 lines and 1466 bytes.

## Important APIs, Types, And Data

Primary surface: `struct mcfqspi_cs_control` and `struct mcfqspi_platform_data` with chip-select
callbacks, bus count, and chip-select count. Representative preprocessor definitions seen in the
file are `mcfqspi_h`. Representative callable or assembly entry symbols are none. Representative
structs/unions/enums are `mcfqspi_cs_control`, `mcfqspi_platform_data`. Direct includes are none.

## Control Flow And Integration

consumed by the ColdFire QSPI platform driver and board files. Most headers in this subset
contribute through compile-time selection and inline helpers; the C and assembly files add runtime
entry points. Control reaches these definitions from generic Linux subsystems such as memory
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

callback ownership and CS polarity must match attached devices or transfers will talk to the wrong
SPI slave. Additional cross-cutting risks are conditional compilation drift between MMU families,
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/mcfqspi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/mcfsim.h -->
# sources/distributed-fs/ceph-client/arch/m68k/include/asm/mcfsim.h

## Purpose

`mcfsim.h` selects the correct ColdFire SIM header for the configured SoC family. It belongs to the m68k architecture support inside the ceph-client Linux source snapshot, so its behavior is architecture/kernel plumbing rather than Ceph protocol logic. Source read size: 52 lines and 1531 bytes.

## Important APIs, Types, And Data

Primary surface: conditional includes for `m5206sim.h`, `m520xsim.h`, `m523xsim.h`, `m525xsim.h`,
`m527xsim.h`, and related interrupt controller definitions. Representative preprocessor definitions
seen in the file are `mcfsim_h`. Representative callable or assembly entry symbols are none.
Representative structs/unions/enums are none. Direct includes are `asm/m5206sim.h`,
`asm/m520xsim.h`, `asm/m523xsim.h`, `asm/m525xsim.h`, `asm/m5272sim.h`, `asm/m527xsim.h`,
`asm/m528xsim.h`, `asm/m5307sim.h`.

## Control Flow And Integration

central include used by board code needing SIM, interrupt, GPIO, timer, and peripheral register
constants. Most headers in this subset contribute through compile-time selection and inline helpers;
the C and assembly files add runtime entry points. Control reaches these definitions from generic
Linux subsystems such as memory management, scheduler context switching, traps, syscall dispatch,
DMA mapping, console setup, procfs, module loading, or board-specific drivers.

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

incorrect Kconfig SoC selection silently exposes the wrong register map to many drivers. Additional
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/mcfsim.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/mcfslt.h -->
# sources/distributed-fs/ceph-client/arch/m68k/include/asm/mcfslt.h

## Purpose

`mcfslt.h` defines ColdFire slice timer registers. It belongs to the m68k architecture support inside the ceph-client Linux source snapshot, so its behavior is architecture/kernel plumbing rather than Ceph protocol logic. Source read size: 38 lines and 1240 bytes.

## Important APIs, Types, And Data

Primary surface: `MCFSLT_STCNT`, `SCR`, `SCNT`, `SSR`, plus run, interrupt-enable, timer-enable,
bus-error and timeout bits. Representative preprocessor definitions seen in the file are `mcfslt_h`,
`MCFSLT_STCNT`, `MCFSLT_SCR`, `MCFSLT_SCNT`, `MCFSLT_SSR`, `MCFSLT_SCR_RUN`, `MCFSLT_SCR_IEN`,
`MCFSLT_SCR_TEN`, `MCFSLT_SSR_BE`, `MCFSLT_SSR_TE`. Representative callable or assembly entry
symbols are none. Representative structs/unions/enums are none. Direct includes are none.

## Control Flow And Integration

used by ColdFire timer/clockevent implementations for slice timer hardware. Most headers in this
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

status bits are write/clear hardware state; tests need interrupt delivery and rollover behavior.
Additional cross-cutting risks are conditional compilation drift between MMU families, inline
assembly constraints that differ between 68000/020/030/040/060/ColdFire, register-endianness
mistakes on memory-mapped buses, and ABI changes to exported bootinfo, ptrace, signal, stat, or
syscall structures.

## Test Signals

Useful signals are m68k `defconfig`, allmodconfig where practical, and targeted builds for ColdFire
MMU, no-MMU, Sun3, Motorola MMU, Q40, Macintosh, Amiga, MVME, HP300 and virt configurations. Runtime
validation should cover boot to userspace, syscall tracing/seccomp, signal delivery and return,
fork/clone/vfork, module loading, DMA cache coherency tests, serial/early console output, interrupt
delivery, TLB flush stress, and userspace ABI checks for ptrace, stat, signal, cacheflush, and
bootinfo records.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/mcfslt.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/mcftimer.h -->
# sources/distributed-fs/ceph-client/arch/m68k/include/asm/mcftimer.h

## Purpose

`mcftimer.h` defines the legacy ColdFire timer register block. It belongs to the m68k architecture support inside the ceph-client Linux source snapshot, so its behavior is architecture/kernel plumbing rather than Ceph protocol logic. Source read size: 58 lines and 2357 bytes.

## Important APIs, Types, And Data

Primary surface: `MCFTIMER_TMR`, `TRR`, `TCR`, `TCN`, `TER`, clock-source, restart/free-run and
event flags. Representative preprocessor definitions seen in the file are `mcftimer_h`,
`MCFTIMER_TMR`, `MCFTIMER_TRR`, `MCFTIMER_TCR`, `MCFTIMER_TCN`, `MCFTIMER_TER`,
`MCFTIMER_TMR_PREMASK`, `MCFTIMER_TMR_DISCE`, `MCFTIMER_TMR_ANYCE`, `MCFTIMER_TMR_FALLCE`,
`MCFTIMER_TMR_RISECE`, `MCFTIMER_TMR_ENOM`, `MCFTIMER_TMR_DISOM`, `MCFTIMER_TMR_ENORI`.
Representative callable or assembly entry symbols are none. Representative structs/unions/enums are
none. Direct includes are none.

## Control Flow And Integration

used by ColdFire timer drivers and early board setup. Most headers in this subset contribute through
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

duplicated `TER` definition and mode-bit combinations require build coverage across SoC variants.
Additional cross-cutting risks are conditional compilation drift between MMU families, inline
assembly constraints that differ between 68000/020/030/040/060/ColdFire, register-endianness
mistakes on memory-mapped buses, and ABI changes to exported bootinfo, ptrace, signal, stat, or
syscall structures.

## Test Signals

Useful signals are m68k `defconfig`, allmodconfig where practical, and targeted builds for ColdFire
MMU, no-MMU, Sun3, Motorola MMU, Q40, Macintosh, Amiga, MVME, HP300 and virt configurations. Runtime
validation should cover boot to userspace, syscall tracing/seccomp, signal delivery and return,
fork/clone/vfork, module loading, DMA cache coherency tests, serial/early console output, interrupt
delivery, TLB flush stress, and userspace ABI checks for ptrace, stat, signal, cacheflush, and
bootinfo records.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/mcftimer.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/mcfuart.h -->
# sources/distributed-fs/ceph-client/arch/m68k/include/asm/mcfuart.h

## Purpose

`mcfuart.h` defines ColdFire UART registers, bitfields, and platform UART description. It belongs to the m68k architecture support inside the ceph-client Linux source snapshot, so its behavior is architecture/kernel plumbing rather than Ceph protocol logic. Source read size: 189 lines and 7076 bytes.

## Important APIs, Types, And Data

Primary surface: register offsets, mode/status/command bits, baud generator masks, FIFO bits, modem
controls, and `struct mcf_platform_uart`. Representative preprocessor definitions seen in the file
are `mcfuart_h`, `MCFUART_UMR`, `MCFUART_USR`, `MCFUART_UCSR`, `MCFUART_UCR`, `MCFUART_URB`,
`MCFUART_UTB`, `MCFUART_UIPCR`, `MCFUART_UACR`, `MCFUART_UISR`, `MCFUART_UIMR`, `MCFUART_UBG1`,
`MCFUART_UBG2`, `MCFUART_UTF`. Representative callable or assembly entry symbols are none.
Representative structs/unions/enums are `mcf_platform_uart`. Direct includes are
`linux/platform_device.h`, `linux/serial_core.h`.

## Control Flow And Integration

used by the ColdFire serial driver and platform-device registration. Most headers in this subset
contribute through compile-time selection and inline helpers; the C and assembly files add runtime
entry points. Control reaches these definitions from generic Linux subsystems such as memory
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

FIFO status and interrupt-mask bits are hardware-facing; baud, reset and flow-control regressions
show up as early console or tty failures. Additional cross-cutting risks are conditional compilation
drift between MMU families, inline assembly constraints that differ between
68000/020/030/040/060/ColdFire, register-endianness mistakes on memory-mapped buses, and ABI changes
to exported bootinfo, ptrace, signal, stat, or syscall structures.

## Test Signals

Useful signals are m68k `defconfig`, allmodconfig where practical, and targeted builds for ColdFire
MMU, no-MMU, Sun3, Motorola MMU, Q40, Macintosh, Amiga, MVME, HP300 and virt configurations. Runtime
validation should cover boot to userspace, syscall tracing/seccomp, signal delivery and return,
fork/clone/vfork, module loading, DMA cache coherency tests, serial/early console output, interrupt
delivery, TLB flush stress, and userspace ABI checks for ptrace, stat, signal, cacheflush, and
bootinfo records.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/mcfuart.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/mcfwdebug.h -->
# sources/distributed-fs/ceph-client/arch/m68k/include/asm/mcfwdebug.h

## Purpose

`mcfwdebug.h` names ColdFire hardware debug registers and exposes a low-level write helper. It belongs to the m68k architecture support inside the ceph-client Linux source snapshot, so its behavior is architecture/kernel plumbing rather than Ceph protocol logic. Source read size: 119 lines and 5106 bytes.

## Important APIs, Types, And Data

Primary surface: debug register numbers, TDR/CSR/PBR/ABHR/ABLR/DBR/DBMR bitfields, and `wdebug()`
inline assembly. Representative preprocessor definitions seen in the file are `mcfdebug_h`,
`MCFDEBUG_CSR`, `MCFDEBUG_BAAR`, `MCFDEBUG_AATR`, `MCFDEBUG_TDR`, `MCFDEBUG_PBR`, `MCFDEBUG_PBMR`,
`MCFDEBUG_ABHR`, `MCFDEBUG_ABLR`, `MCFDEBUG_DBR`, `MCFDEBUG_DBMR`, `MCFDEBUG_TDR_TRC_DISP`,
`MCFDEBUG_TDR_TRC_HALT`, `MCFDEBUG_TDR_TRC_INTR`. Representative callable or assembly entry symbols
are `wdebug`. Representative structs/unions/enums are none. Direct includes are none.

## Control Flow And Integration

used by ColdFire debug, breakpoint, and board bring-up code. Most headers in this subset contribute
through compile-time selection and inline helpers; the C and assembly files add runtime entry
points. Control reaches these definitions from generic Linux subsystems such as memory management,
scheduler context switching, traps, syscall dispatch, DMA mapping, console setup, procfs, module
loading, or board-specific drivers.

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

writes enter processor debug state directly; bad masks can halt or single-step unexpectedly.
Additional cross-cutting risks are conditional compilation drift between MMU families, inline
assembly constraints that differ between 68000/020/030/040/060/ColdFire, register-endianness
mistakes on memory-mapped buses, and ABI changes to exported bootinfo, ptrace, signal, stat, or
syscall structures.

## Test Signals

Useful signals are m68k `defconfig`, allmodconfig where practical, and targeted builds for ColdFire
MMU, no-MMU, Sun3, Motorola MMU, Q40, Macintosh, Amiga, MVME, HP300 and virt configurations. Runtime
validation should cover boot to userspace, syscall tracing/seccomp, signal delivery and return,
fork/clone/vfork, module loading, DMA cache coherency tests, serial/early console output, interrupt
delivery, TLB flush stress, and userspace ABI checks for ptrace, stat, signal, cacheflush, and
bootinfo records.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/mcfwdebug.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/mmu.h -->
# sources/distributed-fs/ceph-client/arch/m68k/include/asm/mmu.h

## Purpose

`mmu.h` selects the generic m68k `mm_context_t` definition. It belongs to the m68k architecture support inside the ceph-client Linux source snapshot, so its behavior is architecture/kernel plumbing rather than Ceph protocol logic. Source read size: 12 lines and 214 bytes.

## Important APIs, Types, And Data

Primary surface: include guard plus `asm-generic/mmu.h`. Representative preprocessor definitions
seen in the file are `__MMU_H`. Representative callable or assembly entry symbols are none.
Representative structs/unions/enums are none. Direct includes are `asm-generic/mmu.h`.

## Control Flow And Integration

included by MMU context, process, and memory-management headers. Most headers in this subset
contribute through compile-time selection and inline helpers; the C and assembly files add runtime
entry points. Control reaches these definitions from generic Linux subsystems such as memory
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

minimal wrapper; the main risk is include-order compatibility with architecture-specific context
users. Additional cross-cutting risks are conditional compilation drift between MMU families, inline
assembly constraints that differ between 68000/020/030/040/060/ColdFire, register-endianness
mistakes on memory-mapped buses, and ABI changes to exported bootinfo, ptrace, signal, stat, or
syscall structures.

## Test Signals

Useful signals are m68k `defconfig`, allmodconfig where practical, and targeted builds for ColdFire
MMU, no-MMU, Sun3, Motorola MMU, Q40, Macintosh, Amiga, MVME, HP300 and virt configurations. Runtime
validation should cover boot to userspace, syscall tracing/seccomp, signal delivery and return,
fork/clone/vfork, module loading, DMA cache coherency tests, serial/early console output, interrupt
delivery, TLB flush stress, and userspace ABI checks for ptrace, stat, signal, cacheflush, and
bootinfo records.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/mmu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/mmu_context.h -->
# sources/distributed-fs/ceph-client/arch/m68k/include/asm/mmu_context.h

## Purpose

`mmu_context.h` implements m68k address-space context allocation and MMU switching. It belongs to the m68k architecture support inside the ceph-client Linux source snapshot, so its behavior is architecture/kernel plumbing rather than Ceph protocol logic. Source read size: 322 lines and 7273 bytes.

## Important APIs, Types, And Data

Primary surface: ColdFire ASID allocation, Sun3 context activation, Motorola 020/030 CRP and 040/060
URP switching, `switch_mm()`, `activate_mm()`, and `load_ksp_mmu()`. Representative preprocessor
definitions seen in the file are `__M68K_MMU_CONTEXT_H`, `NO_CONTEXT`, `LAST_CONTEXT`,
`FIRST_CONTEXT`, `init_new_context(tsk, mm)`, `destroy_context`, `activate_mm`,
`prepare_arch_switch(next)`, `init_new_context`. Representative callable or assembly entry symbols
are `steal_context`, `get_mmu_context`, `destroy_context`, `set_context`, `switch_mm`,
`activate_mm`, `load_ksp_mmu`, `get_free_context`, `clear_context`, `init_new_context`,
`activate_context`, `switch_mm_0230`, `switch_mm_0460`. Representative structs/unions/enums are
none. Direct includes are `asm-generic/mm_hooks.h`, `asm-generic/mmu_context.h`, `asm-
generic/nommu_context.h`, `asm/atomic.h`, `asm/bitops.h`, `asm/cacheflush.h`, `asm/mcfmmu.h`,
`asm/mmu.h`.

## Control Flow And Integration

called from scheduler context-switch and `activate_mm()` paths; branches by `CONFIG_COLDFIRE`,
`CONFIG_SUN3`, generic MMU, or no-MMU. Most headers in this subset contribute through compile-time
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

TLB/cache flush ordering and context reuse are critical; ColdFire kernel-stack TLB preloading must
find valid PTEs with interrupts disabled. Additional cross-cutting risks are conditional compilation
drift between MMU families, inline assembly constraints that differ between
68000/020/030/040/060/ColdFire, register-endianness mistakes on memory-mapped buses, and ABI changes
to exported bootinfo, ptrace, signal, stat, or syscall structures.

## Test Signals

Useful signals are m68k `defconfig`, allmodconfig where practical, and targeted builds for ColdFire
MMU, no-MMU, Sun3, Motorola MMU, Q40, Macintosh, Amiga, MVME, HP300 and virt configurations. Runtime
validation should cover boot to userspace, syscall tracing/seccomp, signal delivery and return,
fork/clone/vfork, module loading, DMA cache coherency tests, serial/early console output, interrupt
delivery, TLB flush stress, and userspace ABI checks for ptrace, stat, signal, cacheflush, and
bootinfo records.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/mmu_context.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/module.h -->
# sources/distributed-fs/ceph-client/arch/m68k/include/asm/module.h

## Purpose

`module.h` defines m68k module relocation fixup metadata. It belongs to the m68k architecture support inside the ceph-client Linux source snapshot, so its behavior is architecture/kernel plumbing rather than Ceph protocol logic. Source read size: 42 lines and 847 bytes.

## Important APIs, Types, And Data

Primary surface: `enum m68k_fixup_type`, `struct m68k_fixup_info`, `mod_arch_specific`,
`m68k_fixup()`, and `module_fixup()`. Representative preprocessor definitions seen in the file are
`_ASM_M68K_MODULE_H`, `MODULE_ARCH_INIT`, `m68k_fixup(type, addr)`. Representative callable or
assembly entry symbols are `module_fixup`. Representative structs/unions/enums are
`m68k_fixup_type`, `m68k_fixup_info`, `mod_arch_specific`, `module`. Direct includes are `asm-
generic/module.h`.

## Control Flow And Integration

used by the module loader and architecture module relocation code. Most headers in this subset
contribute through compile-time selection and inline helpers; the C and assembly files add runtime
entry points. Control reaches these definitions from generic Linux subsystems such as memory
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

fixup section data is generated into module init data; wrong address/type pairs break runtime module
relocation. Additional cross-cutting risks are conditional compilation drift between MMU families,
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/module.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/module.lds.h -->
# sources/distributed-fs/ceph-client/arch/m68k/include/asm/module.lds.h

## Purpose

`module.lds.h` adds the m68k module linker-script section for fixups. It belongs to the m68k architecture support inside the ceph-client Linux source snapshot, so its behavior is architecture/kernel plumbing rather than Ceph protocol logic. Source read size: 7 lines and 91 bytes.

## Important APIs, Types, And Data

Primary surface: `SECTIONS { .m68k_fixup : { *(.m68k_fixup) } }`. Representative preprocessor
definitions seen in the file are none. Representative callable or assembly entry symbols are none.
Representative structs/unions/enums are none. Direct includes are none.

## Control Flow And Integration

included by the generic module linker script for m68k modules. Most headers in this subset
contribute through compile-time selection and inline helpers; the C and assembly files add runtime
entry points. Control reaches these definitions from generic Linux subsystems such as memory
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

the section name must match `m68k_fixup()` or module fixup metadata disappears at link time.
Additional cross-cutting risks are conditional compilation drift between MMU families, inline
assembly constraints that differ between 68000/020/030/040/060/ColdFire, register-endianness
mistakes on memory-mapped buses, and ABI changes to exported bootinfo, ptrace, signal, stat, or
syscall structures.

## Test Signals

Useful signals are m68k `defconfig`, allmodconfig where practical, and targeted builds for ColdFire
MMU, no-MMU, Sun3, Motorola MMU, Q40, Macintosh, Amiga, MVME, HP300 and virt configurations. Runtime
validation should cover boot to userspace, syscall tracing/seccomp, signal delivery and return,
fork/clone/vfork, module loading, DMA cache coherency tests, serial/early console output, interrupt
delivery, TLB flush stress, and userspace ABI checks for ptrace, stat, signal, cacheflush, and
bootinfo records.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/module.lds.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/motorola_pgalloc.h -->
# sources/distributed-fs/ceph-client/arch/m68k/include/asm/motorola_pgalloc.h

## Purpose

`motorola_pgalloc.h` defines page-table allocation helpers for Motorola MMU m68k. It belongs to the m68k architecture support inside the ceph-client Linux source snapshot, so its behavior is architecture/kernel plumbing rather than Ceph protocol logic. Source read size: 97 lines and 2149 bytes.

## Important APIs, Types, And Data

Primary surface: `mmu_page_ctor/dtor()`, pointer-table allocation/free helpers, PTE/PMD/PGD
allocation and TLB-free hooks, and populate helpers. Representative preprocessor definitions seen in
the file are `_MOTOROLA_PGALLOC_H`. Representative callable or assembly entry symbols are
`mmu_page_ctor`, `mmu_page_dtor`, `init_pointer_table`, `get_pointer_table`, `free_pointer_table`,
`pte_alloc_one_kernel`, `pte_free_kernel`, `pte_alloc_one`, `pte_free`, `__pte_free_tlb`,
`pmd_alloc_one`, `pmd_free`, `__pmd_free_tlb`, `pgd_free`. Representative structs/unions/enums are
`m68k_table_types`. Direct includes are `asm/tlb.h`, `asm/tlbflush.h`.

## Control Flow And Integration

used when `CONFIG_MMU` builds the non-ColdFire, non-Sun3 Motorola page-table implementation. Most
headers in this subset contribute through compile-time selection and inline helpers; the C and
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

table descriptors may be allocated from special pointer-table pools; freeing through the wrong path
leaks or corrupts MMU tables. Additional cross-cutting risks are conditional compilation drift
between MMU families, inline assembly constraints that differ between
68000/020/030/040/060/ColdFire, register-endianness mistakes on memory-mapped buses, and ABI changes
to exported bootinfo, ptrace, signal, stat, or syscall structures.

## Test Signals

Useful signals are m68k `defconfig`, allmodconfig where practical, and targeted builds for ColdFire
MMU, no-MMU, Sun3, Motorola MMU, Q40, Macintosh, Amiga, MVME, HP300 and virt configurations. Runtime
validation should cover boot to userspace, syscall tracing/seccomp, signal delivery and return,
fork/clone/vfork, module loading, DMA cache coherency tests, serial/early console output, interrupt
delivery, TLB flush stress, and userspace ABI checks for ptrace, stat, signal, cacheflush, and
bootinfo records.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/motorola_pgalloc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/motorola_pgtable.h -->
# sources/distributed-fs/ceph-client/arch/m68k/include/asm/motorola_pgtable.h

## Purpose

`motorola_pgtable.h` defines page-table encodings for 68020/030/040/060-style Motorola MMUs. It belongs to the m68k architecture support inside the ceph-client Linux source snapshot, so its behavior is architecture/kernel plumbing rather than Ceph protocol logic. Source read size: 206 lines and 7220 bytes.

## Important APIs, Types, And Data

Primary surface: hardware descriptor flags, cache/protection presets, `pte_modify()`, `pmd_set()`,
`pud_set()`, PTE state predicates/mutators, and swap-exclusive helpers. Representative preprocessor
definitions seen in the file are `_MOTOROLA_PGTABLE_H`, `_PAGE_PRESENT`, `_PAGE_SHORT`,
`_PAGE_RONLY`, `_PAGE_READWRITE`, `_PAGE_ACCESSED`, `_PAGE_DIRTY`, `_PAGE_SUPER`, `_PAGE_GLOBAL040`,
`_PAGE_NOCACHE030`, `_PAGE_NOCACHE`, `_PAGE_NOCACHE_S`, `_PAGE_CACHE040`, `_PAGE_CACHE040W`.
Representative callable or assembly entry symbols are `pte_modify`, `pmd_set`, `pud_set`,
`pte_write`, `pte_dirty`, `pte_young`, `pte_wrprotect`, `pte_mkclean`, `pte_mkold`,
`pte_mkwrite_novma`, `pte_mkdirty`, `pte_mkyoung`, `pte_mknocache`, `pte_mkcache`. Representative
structs/unions/enums are none. Direct includes are none.

## Control Flow And Integration

included through `pgtable_mm.h` for standard MMU builds outside Sun3/ColdFire. Most headers in this
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

short/long descriptor format differences and cache bits are CPU-generation sensitive. Additional
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/motorola_pgtable.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/movs.h -->
# sources/distributed-fs/ceph-client/arch/m68k/include/asm/movs.h

## Purpose

`movs.h` wraps privileged m68k control-space access instructions. It belongs to the m68k architecture support inside the ceph-client Linux source snapshot, so its behavior is architecture/kernel plumbing rather than Ceph protocol logic. Source read size: 56 lines and 1472 bytes.

## Important APIs, Types, And Data

Primary surface: `SET_DFC`, `GET_DFC`, `SET_SFC`, `GET_SFC`, `SET_VBR`, and control byte/word
`moves` access macros. Representative preprocessor definitions seen in the file are `__MOVS_H__`,
`SET_DFC(x)`, `GET_DFC(x)`, `SET_SFC(x)`, `GET_SFC(x)`, `SET_VBR(x)`, `GET_VBR(x)`,
`SET_CONTROL_BYTE(addr,value)`, `GET_CONTROL_BYTE(addr,value)`, `SET_CONTROL_WORD(addr,value)`,
`GET_CONTROL_WORD(addr,value)`. Representative callable or assembly entry symbols are none.
Representative structs/unions/enums are none. Direct includes are none.

## Control Flow And Integration

used by Sun3 MMU/control-space code and low-level exception/vector setup. Most headers in this
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

requires CPUs with address-space control registers; using on unsupported cores is illegal.
Additional cross-cutting risks are conditional compilation drift between MMU families, inline
assembly constraints that differ between 68000/020/030/040/060/ColdFire, register-endianness
mistakes on memory-mapped buses, and ABI changes to exported bootinfo, ptrace, signal, stat, or
syscall structures.

## Test Signals

Useful signals are m68k `defconfig`, allmodconfig where practical, and targeted builds for ColdFire
MMU, no-MMU, Sun3, Motorola MMU, Q40, Macintosh, Amiga, MVME, HP300 and virt configurations. Runtime
validation should cover boot to userspace, syscall tracing/seccomp, signal delivery and return,
fork/clone/vfork, module loading, DMA cache coherency tests, serial/early console output, interrupt
delivery, TLB flush stress, and userspace ABI checks for ptrace, stat, signal, cacheflush, and
bootinfo records.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/movs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/mvme147hw.h -->
# sources/distributed-fs/ceph-client/arch/m68k/include/asm/mvme147hw.h

## Purpose

`mvme147hw.h` describes MVME147 board hardware registers and IRQ routing. It belongs to the m68k architecture support inside the ceph-client Linux source snapshot, so its behavior is architecture/kernel plumbing rather than Ceph protocol logic. Source read size: 100 lines and 2726 bytes.

## Important APIs, Types, And Data

Primary surface: `struct pcc_regs`, PCC interrupt masks, timer, serial, Ethernet, SCSI, printer, and
RTC register locations. Representative preprocessor definitions seen in the file are
`_MVME147HW_H_`, `MVME147_RTC_BASE`, `m147_pcc`, `PCC_INT_ENAB`, `PCC_TIMER_INT_CLR`,
`PCC_TIMER_TIC_EN`, `PCC_TIMER_COC_EN`, `PCC_TIMER_CLR_OVF`, `PCC_LEVEL_ABORT`, `PCC_LEVEL_SERIAL`,
`PCC_LEVEL_ETH`, `PCC_LEVEL_TIMER1`, `PCC_LEVEL_SCSI_PORT`, `PCC_LEVEL_SCSI_DMA`. Representative
callable or assembly entry symbols are none. Representative structs/unions/enums are `pcc_regs`.
Direct includes are `asm/irq.h`.

## Control Flow And Integration

consumed by MVME147 platform, interrupt, timer, and device code. Most headers in this subset
contribute through compile-time selection and inline helpers; the C and assembly files add runtime
entry points. Control reaches these definitions from generic Linux subsystems such as memory
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

hard-coded board addresses and bit levels must match VME hardware, especially abort, AC-fail, and
DMA interrupt lines. Additional cross-cutting risks are conditional compilation drift between MMU
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/mvme147hw.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/mvme16xhw.h -->
# sources/distributed-fs/ceph-client/arch/m68k/include/asm/mvme16xhw.h

## Purpose

`mvme16xhw.h` describes MVME16x/MVME167 board hardware addresses and interrupt vectors. It belongs to the m68k architecture support inside the ceph-client Linux source snapshot, so its behavior is architecture/kernel plumbing rather than Ceph protocol logic. Source read size: 79 lines and 2002 bytes.

## Important APIs, Types, And Data

Primary surface: LPR/RTC/I596/SCC base addresses, SCC clock, IRQ numbers, and board-control register
layout. Representative preprocessor definitions seen in the file are `_M68K_MVME16xHW_H_`,
`MVME_LPR_BASE`, `mvmelp`, `MVME_RTC_BASE`, `MVME_I596_BASE`, `MVME_SCC_A_ADDR`, `MVME_SCC_B_ADDR`,
`MVME_SCC_PCLK`, `MVME162_IRQ_TYPE_PRIO`, `MVME167_IRQ_PRN`, `MVME16x_IRQ_I596`, `MVME16x_IRQ_SCSI`,
`MVME16x_IRQ_FLY`, `MVME167_IRQ_SER_ERR`. Representative callable or assembly entry symbols are
none. Representative structs/unions/enums are none. Direct includes are `asm/irq.h`.

## Control Flow And Integration

used by MVME16x platform initialization and drivers. Most headers in this subset contribute through
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

MVME162 and MVME167 IRQ layouts differ; selecting the wrong constants breaks device interrupt
delivery. Additional cross-cutting risks are conditional compilation drift between MMU families,
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/mvme16xhw.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/natfeat.h -->
# sources/distributed-fs/ceph-client/arch/m68k/include/asm/natfeat.h

## Purpose

`natfeat.h` declares ARAnyM/Atari native feature calls. It belongs to the m68k architecture support inside the ceph-client Linux source snapshot, so its behavior is architecture/kernel plumbing rather than Ceph protocol logic. Source read size: 23 lines and 533 bytes.

## Important APIs, Types, And Data

Primary surface: `nf_get_id()`, `nf_call()`, `nf_init()`, `nf_shutdown()`, and `nfprint()`.
Representative preprocessor definitions seen in the file are `_NATFEAT_H`. Representative callable
or assembly entry symbols are `nf_get_id`, `nf_call`, `nf_init`, `nf_shutdown`, `nfprint`.
Representative structs/unions/enums are none. Direct includes are `linux/compiler.h`.

## Control Flow And Integration

integrates m68k virtualized/native-feature services with early platform and console paths. Most
headers in this subset contribute through compile-time selection and inline helpers; the C and
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

feature IDs are provided by the emulator/firmware; calls must handle absent features gracefully.
Additional cross-cutting risks are conditional compilation drift between MMU families, inline
assembly constraints that differ between 68000/020/030/040/060/ColdFire, register-endianness
mistakes on memory-mapped buses, and ABI changes to exported bootinfo, ptrace, signal, stat, or
syscall structures.

## Test Signals

Useful signals are m68k `defconfig`, allmodconfig where practical, and targeted builds for ColdFire
MMU, no-MMU, Sun3, Motorola MMU, Q40, Macintosh, Amiga, MVME, HP300 and virt configurations. Runtime
validation should cover boot to userspace, syscall tracing/seccomp, signal delivery and return,
fork/clone/vfork, module loading, DMA cache coherency tests, serial/early console output, interrupt
delivery, TLB flush stress, and userspace ABI checks for ptrace, stat, signal, cacheflush, and
bootinfo records.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/natfeat.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/nettel.h -->
# sources/distributed-fs/ceph-client/arch/m68k/include/asm/nettel.h

## Purpose

`nettel.h` provides NETtel ColdFire board parallel-port and LED helpers. It belongs to the m68k architecture support inside the ceph-client Linux source snapshot, so its behavior is architecture/kernel plumbing rather than Ceph protocol logic. Source read size: 105 lines and 3084 bytes.

## Important APIs, Types, And Data

Primary surface: DCD/DTR bit masks, LED address definitions, and `mcf_getppdata()`/`mcf_setppdata()`
variants. Representative preprocessor definitions seen in the file are `nettel_h`, `MCFPP_DCD1`,
`MCFPP_DCD0`, `MCFPP_DTR1`, `MCFPP_DTR0`, `NETtel_LEDADDR`. Representative callable or assembly
entry symbols are `mcf_getppdata`, `mcf_setppdata`. Representative structs/unions/enums are none.
Direct includes are `asm/coldfire.h`, `asm/io.h`, `asm/mcfsim.h`.

## Control Flow And Integration

used by NETtel board support for modem control and LEDs. Most headers in this subset contribute
through compile-time selection and inline helpers; the C and assembly files add runtime entry
points. Control reaches these definitions from generic Linux subsystems such as memory management,
scheduler context switching, traps, syscall dispatch, DMA mapping, console setup, procfs, module
loading, or board-specific drivers.

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

conditional address definitions depend on exact board model; wrong bits affect serial handshaking.
Additional cross-cutting risks are conditional compilation drift between MMU families, inline
assembly constraints that differ between 68000/020/030/040/060/ColdFire, register-endianness
mistakes on memory-mapped buses, and ABI changes to exported bootinfo, ptrace, signal, stat, or
syscall structures.

## Test Signals

Useful signals are m68k `defconfig`, allmodconfig where practical, and targeted builds for ColdFire
MMU, no-MMU, Sun3, Motorola MMU, Q40, Macintosh, Amiga, MVME, HP300 and virt configurations. Runtime
validation should cover boot to userspace, syscall tracing/seccomp, signal delivery and return,
fork/clone/vfork, module loading, DMA cache coherency tests, serial/early console output, interrupt
delivery, TLB flush stress, and userspace ABI checks for ptrace, stat, signal, cacheflush, and
bootinfo records.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/nettel.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/nubus.h -->
# sources/distributed-fs/ceph-client/arch/m68k/include/asm/nubus.h

## Purpose

`nubus.h` maps NuBus I/O accessors onto raw I/O and kmap helpers. It belongs to the m68k architecture support inside the ceph-client Linux source snapshot, so its behavior is architecture/kernel plumbing rather than Ceph protocol logic. Source read size: 48 lines and 1262 bytes.

## Important APIs, Types, And Data

Primary surface: `nubus_read*`, `nubus_write*`, memset/memcpy I/O aliases, `nubus_ioremap()`, and
unmap wrappers. Representative preprocessor definitions seen in the file are `_ASM_M68K_NUBUS_H`,
`nubus_readb`, `nubus_readw`, `nubus_readl`, `nubus_writeb`, `nubus_writew`, `nubus_writel`,
`nubus_memset_io(a,b,c)`, `nubus_memcpy_fromio(a,b,c)`, `nubus_memcpy_toio(a,b,c)`, `nubus_unmap`,
`nubus_iounmap`, `nubus_ioremap`. Representative callable or assembly entry symbols are
`nubus_remap_nocache_ser`, `nubus_remap_nocache_nonser`, `nbus_remap_writethrough`,
`nubus_remap_fullcache`. Representative structs/unions/enums are none. Direct includes are
`asm/kmap.h`, `asm/raw_io.h`.

## Control Flow And Integration

used by Macintosh NuBus drivers. Most headers in this subset contribute through compile-time
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

endianness and bus address translation are implicit through raw I/O; drivers need real hardware
tests. Additional cross-cutting risks are conditional compilation drift between MMU families, inline
assembly constraints that differ between 68000/020/030/040/060/ColdFire, register-endianness
mistakes on memory-mapped buses, and ABI changes to exported bootinfo, ptrace, signal, stat, or
syscall structures.

## Test Signals

Useful signals are m68k `defconfig`, allmodconfig where practical, and targeted builds for ColdFire
MMU, no-MMU, Sun3, Motorola MMU, Q40, Macintosh, Amiga, MVME, HP300 and virt configurations. Runtime
validation should cover boot to userspace, syscall tracing/seccomp, signal delivery and return,
fork/clone/vfork, module loading, DMA cache coherency tests, serial/early console output, interrupt
delivery, TLB flush stress, and userspace ABI checks for ptrace, stat, signal, cacheflush, and
bootinfo records.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/nubus.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/openprom.h -->
# sources/distributed-fs/ceph-client/arch/m68k/include/asm/openprom.h

## Purpose

`openprom.h` defines Sun OpenPROM ROM vector structures and constants. It belongs to the m68k architecture support inside the ceph-client Linux source snapshot, so its behavior is architecture/kernel plumbing rather than Ceph protocol logic. Source read size: 313 lines and 8175 bytes.

## Important APIs, Types, And Data

Primary surface: PROM device constants, `struct linux_romvec`, node operation vectors,
memory/register/IRQ/range records, and boot argument layouts. Representative preprocessor
definitions seen in the file are `__SPARC_OPENPROM_H`, `KADB_DEBUGGER_BEGVM`, `LINUX_OPPROM_BEGVM`,
`LINUX_OPPROM_ENDVM`, `LINUX_OPPROM_MAGIC`, `PROMDEV_KBD`, `PROMDEV_SCREEN`, `PROMDEV_TTYA`,
`PROMDEV_TTYB`, `PROMREG_MAX`, `PROMVADDR_MAX`, `PROMINTR_MAX`. Representative callable or assembly
entry symbols are none. Representative structs/unions/enums are `linux_dev_v0_funcs`,
`linux_dev_v2_funcs`, `linux_mlist_v0`, `linux_mem_v0`, `linux_arguments_v0`, `linux_bootargs_v2`,
`linux_romvec`, `linux_nodeops`, `linux_prom_registers`, `linux_prom_irqs`. Direct includes are
none.

## Control Flow And Integration

used by Sun3/Sun3x PROM probing and boot-time firmware calls. Most headers in this subset contribute
through compile-time selection and inline helpers; the C and assembly files add runtime entry
points. Control reaches these definitions from generic Linux subsystems such as memory management,
scheduler context switching, traps, syscall dispatch, DMA mapping, console setup, procfs, module
loading, or board-specific drivers.

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

structure layout is firmware ABI; padding or pointer-size drift breaks PROM callbacks. Additional
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/openprom.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/oplib.h -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/oplib.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/page.h -->
# sources/distributed-fs/ceph-client/arch/m68k/include/asm/page.h

## Purpose

`page.h` selects m68k page size/types and MMU/no-MMU page helpers. It belongs to the m68k architecture support inside the ceph-client Linux source snapshot, so its behavior is architecture/kernel plumbing rather than Ceph protocol logic. Source read size: 62 lines and 1422 bytes.

## Important APIs, Types, And Data

Primary surface: `PAGE_OFFSET`, scalar `pte_t/pmd_t/pgd_t/pgprot_t` wrappers, `__pte()`, `__pgd()`,
`__pgprot()`, and included MMU or no-MMU page conversion helpers. Representative preprocessor
definitions seen in the file are `_M68K_PAGE_H`, `PAGE_OFFSET`, `pmd_val(x)`, `__pmd(x)`,
`pte_val(x)`, `pgd_val(x)`, `pgprot_val(x)`, `__pte(x)`, `__pgd(x)`, `__pgprot(x)`. Representative
callable or assembly entry symbols are none. Representative structs/unions/enums are `page`. Direct
includes are `asm-generic/getorder.h`, `asm-generic/memory_model.h`, `asm/page_mm.h`,
`asm/page_no.h`, `asm/page_offset.h`, `asm/setup.h`, `linux/const.h`, `vdso/page.h`.

## Control Flow And Integration

included across all m68k memory-management and driver code. Most headers in this subset contribute
through compile-time selection and inline helpers; the C and assembly files add runtime entry
points. Control reaches these definitions from generic Linux subsystems such as memory management,
scheduler context switching, traps, syscall dispatch, DMA mapping, console setup, procfs, module
loading, or board-specific drivers.

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

conditional inclusion by `CONFIG_MMU` means helper semantics differ sharply between paged and flat-
memory kernels. Additional cross-cutting risks are conditional compilation drift between MMU
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/page.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/page_mm.h -->
# sources/distributed-fs/ceph-client/arch/m68k/include/asm/page_mm.h

## Purpose

`page_mm.h` implements page clearing/copying and virtual/physical conversion for MMU kernels. It belongs to the m68k architecture support inside the ceph-client Linux source snapshot, so its behavior is architecture/kernel plumbing rather than Ceph protocol logic. Source read size: 149 lines and 3386 bytes.

## Important APIs, Types, And Data

Primary surface: `clear_page()`, `copy_page()`, user-page wrappers, `___pa()`, `__pa()`,
`virt_to_page()`, `page_to_virt()`, `virt_to_pfn()`, `pfn_valid()`, and `ARCH_PFN_OFFSET`.
Representative preprocessor definitions seen in the file are `_M68K_PAGE_MM_H`, `clear_page(page)`,
`copy_page(to,from)`, `clear_user_page(addr, vaddr, page)`, `copy_user_page(to, from, vaddr, page)`,
`WANT_PAGE_VIRTUAL`, `__pa(vaddr)`, `__pa(x)`, `virt_to_page(addr)`, `page_to_virt(page)`,
`ARCH_PFN_OFFSET`, `virt_addr_valid(kaddr)`, `pfn_valid(pfn)`. Representative callable or assembly
entry symbols are `copy_page`, `clear_page`, `___pa`, `__va`, `virt_to_pfn`, `pfn_to_virt`.
Representative structs/unions/enums are none. Direct includes are `asm/module.h`,
`linux/compiler.h`.

## Control Flow And Integration

used by allocators, fault handling, highmem, module memory, and DMA conversion paths. Most headers
in this subset contribute through compile-time selection and inline helpers; the C and assembly
files add runtime entry points. Control reaches these definitions from generic Linux subsystems such
as memory management, scheduler context switching, traps, syscall dispatch, DMA mapping, console
setup, procfs, module loading, or board-specific drivers.

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

m68k has discontiguous memory chunks; `virt_to_pfn()` and validity checks must account for
`m68k_memory[]`. Additional cross-cutting risks are conditional compilation drift between MMU
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/page_mm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/page_no.h -->
# sources/distributed-fs/ceph-client/arch/m68k/include/asm/page_no.h

## Purpose

`page_no.h` implements page and address helpers for no-MMU m68k. It belongs to the m68k architecture support inside the ceph-client Linux source snapshot, so its behavior is architecture/kernel plumbing rather than Ceph protocol logic. Source read size: 41 lines and 1177 bytes.

## Important APIs, Types, And Data

Primary surface: simple `clear_page`, `copy_page`, `__pa`, `__va`, `virt_to_page`, `page_to_virt`,
`virt_addr_valid`, and `virt_to_pfn` helpers. Representative preprocessor definitions seen in the
file are `_M68K_PAGE_NO_H`, `clear_page(page)`, `copy_page(to,from)`, `copy_user_page(to, from,
vaddr, pg)`, `vma_alloc_zeroed_movable_folio(vma, vaddr)`, `__pa(vaddr)`, `__va(paddr)`,
`virt_to_page(addr)`, `page_to_virt(page)`, `virt_addr_valid(kaddr)`, `ARCH_PFN_OFFSET`.
Representative callable or assembly entry symbols are `virt_to_pfn`, `pfn_to_virt`. Representative
structs/unions/enums are none. Direct includes are none.

## Control Flow And Integration

used by flat-memory ColdFire/68000 no-MMU builds. Most headers in this subset contribute through
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

identity-style conversions assume linear memory; no-MMU drivers must not expect page-table
protection. Additional cross-cutting risks are conditional compilation drift between MMU families,
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/page_no.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/page_offset.h -->
# sources/distributed-fs/ceph-client/arch/m68k/include/asm/page_offset.h

## Purpose

`page_offset.h` defines the raw kernel virtual base for page helpers. It belongs to the m68k architecture support inside the ceph-client Linux source snapshot, so its behavior is architecture/kernel plumbing rather than Ceph protocol logic. Source read size: 10 lines and 256 bytes.

## Important APIs, Types, And Data

Primary surface: `PAGE_OFFSET_RAW` selected by Sun3, MMU, or no-MMU configuration. Representative
preprocessor definitions seen in the file are `PAGE_OFFSET_RAW`. Representative callable or assembly
entry symbols are none. Representative structs/unions/enums are none. Direct includes are none.

## Control Flow And Integration

included by `page.h` before MMU/no-MMU helper selection. Most headers in this subset contribute
through compile-time selection and inline helpers; the C and assembly files add runtime entry
points. Control reaches these definitions from generic Linux subsystems such as memory management,
scheduler context switching, traps, syscall dispatch, DMA mapping, console setup, procfs, module
loading, or board-specific drivers.

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

a wrong offset invalidates every physical/virtual conversion in the architecture. Additional cross-
cutting risks are conditional compilation drift between MMU families, inline assembly constraints
that differ between 68000/020/030/040/060/ColdFire, register-endianness mistakes on memory-mapped
buses, and ABI changes to exported bootinfo, ptrace, signal, stat, or syscall structures.

## Test Signals

Useful signals are m68k `defconfig`, allmodconfig where practical, and targeted builds for ColdFire
MMU, no-MMU, Sun3, Motorola MMU, Q40, Macintosh, Amiga, MVME, HP300 and virt configurations. Runtime
validation should cover boot to userspace, syscall tracing/seccomp, signal delivery and return,
fork/clone/vfork, module loading, DMA cache coherency tests, serial/early console output, interrupt
delivery, TLB flush stress, and userspace ABI checks for ptrace, stat, signal, cacheflush, and
bootinfo records.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/page_offset.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/parport.h -->
# sources/distributed-fs/ceph-client/arch/m68k/include/asm/parport.h

## Purpose

`parport.h` declares m68k parport discovery hooks and aliases string I/O helpers. It belongs to the m68k architecture support inside the ceph-client Linux source snapshot, so its behavior is architecture/kernel plumbing rather than Ceph protocol logic. Source read size: 29 lines and 837 bytes.

## Important APIs, Types, And Data

Primary surface: `insl`, `outsl`, `parport_pc_find_isa_ports()`, and
`parport_pc_find_nonpci_ports()`. Representative preprocessor definitions seen in the file are
`_ASM_M68K_PARPORT_H`, `insl(port,buf,len)`, `outsl(port,buf,len)`. Representative callable or
assembly entry symbols are `parport_pc_find_isa_ports`, `parport_pc_find_nonpci_ports`.
Representative structs/unions/enums are none. Direct includes are none.

## Control Flow And Integration

used by the PC-style parallel-port driver on m68k systems with ISA-like ports. Most headers in this
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

stub discovery must match platform availability or drivers may probe nonexistent I/O. Additional
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/parport.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/pci.h -->
# sources/distributed-fs/ceph-client/arch/m68k/include/asm/pci.h

## Purpose

`pci.h` sets basic m68k PCI resource minima. It belongs to the m68k architecture support inside the ceph-client Linux source snapshot, so its behavior is architecture/kernel plumbing rather than Ceph protocol logic. Source read size: 10 lines and 228 bytes.

## Important APIs, Types, And Data

Primary surface: `PCIBIOS_MIN_IO` and `PCIBIOS_MIN_MEM`. Representative preprocessor definitions
seen in the file are `_ASM_M68K_PCI_H`, `pcibios_assign_all_busses()`, `PCIBIOS_MIN_IO`,
`PCIBIOS_MIN_MEM`. Representative callable or assembly entry symbols are none. Representative
structs/unions/enums are none. Direct includes are none.

## Control Flow And Integration

used by generic PCI resource allocation on m68k platforms with PCI. Most headers in this subset
contribute through compile-time selection and inline helpers; the C and assembly files add runtime
entry points. Control reaches these definitions from generic Linux subsystems such as memory
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

minimal constants still shape bridge/window assignment; bad minima can overlap legacy devices.
Additional cross-cutting risks are conditional compilation drift between MMU families, inline
assembly constraints that differ between 68000/020/030/040/060/ColdFire, register-endianness
mistakes on memory-mapped buses, and ABI changes to exported bootinfo, ptrace, signal, stat, or
syscall structures.

## Test Signals

Useful signals are m68k `defconfig`, allmodconfig where practical, and targeted builds for ColdFire
MMU, no-MMU, Sun3, Motorola MMU, Q40, Macintosh, Amiga, MVME, HP300 and virt configurations. Runtime
validation should cover boot to userspace, syscall tracing/seccomp, signal delivery and return,
fork/clone/vfork, module loading, DMA cache coherency tests, serial/early console output, interrupt
delivery, TLB flush stress, and userspace ABI checks for ptrace, stat, signal, cacheflush, and
bootinfo records.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/pci.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/pgalloc.h -->
# sources/distributed-fs/ceph-client/arch/m68k/include/asm/pgalloc.h

## Purpose

`pgalloc.h` selects the correct m68k page-table allocation backend. It belongs to the m68k architecture support inside the ceph-client Linux source snapshot, so its behavior is architecture/kernel plumbing rather than Ceph protocol logic. Source read size: 22 lines and 444 bytes.

## Important APIs, Types, And Data

Primary surface: conditional includes for ColdFire, Sun3, or Motorola pgalloc plus
`m68k_setup_node()`. Representative preprocessor definitions seen in the file are `M68K_PGALLOC_H`.
Representative callable or assembly entry symbols are `m68k_setup_node`. Representative
structs/unions/enums are none. Direct includes are `asm/mcf_pgalloc.h`, `asm/motorola_pgalloc.h`,
`asm/setup.h`, `asm/sun3_pgalloc.h`, `asm/virtconvert.h`, `linux/highmem.h`, `linux/mm.h`.

## Control Flow And Integration

included by generic mm page-table allocation code. Most headers in this subset contribute through
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

backend selection must match the selected pgtable format exactly. Additional cross-cutting risks are
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/pgalloc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/pgtable.h -->
# sources/distributed-fs/ceph-client/arch/m68k/include/asm/pgtable.h

## Purpose

`pgtable.h` selects m68k page-table definitions for MMU or no-MMU builds. It belongs to the m68k architecture support inside the ceph-client Linux source snapshot, so its behavior is architecture/kernel plumbing rather than Ceph protocol logic. Source read size: 17 lines and 293 bytes.

## Important APIs, Types, And Data

Primary surface: wrapper includes `page.h`, `pgtable_no.h`, or `pgtable_mm.h`, and declares
`paging_init()`. Representative preprocessor definitions seen in the file are `__M68K_PGTABLE_H`.
Representative callable or assembly entry symbols are `paging_init`. Representative
structs/unions/enums are none. Direct includes are `asm/page.h`, `asm/pgtable_mm.h`,
`asm/pgtable_no.h`.

## Control Flow And Integration

central include for Linux mm on m68k. Most headers in this subset contribute through compile-time
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

small wrapper, but an include-order regression can expose MMU symbols to no-MMU builds or vice
versa. Additional cross-cutting risks are conditional compilation drift between MMU families, inline
assembly constraints that differ between 68000/020/030/040/060/ColdFire, register-endianness
mistakes on memory-mapped buses, and ABI changes to exported bootinfo, ptrace, signal, stat, or
syscall structures.

## Test Signals

Useful signals are m68k `defconfig`, allmodconfig where practical, and targeted builds for ColdFire
MMU, no-MMU, Sun3, Motorola MMU, Q40, Macintosh, Amiga, MVME, HP300 and virt configurations. Runtime
validation should cover boot to userspace, syscall tracing/seccomp, signal delivery and return,
fork/clone/vfork, module loading, DMA cache coherency tests, serial/early console output, interrupt
delivery, TLB flush stress, and userspace ABI checks for ptrace, stat, signal, cacheflush, and
bootinfo records.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/pgtable.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/pgtable_mm.h -->
# sources/distributed-fs/ceph-client/arch/m68k/include/asm/pgtable_mm.h

## Purpose

`pgtable_mm.h` defines shared m68k MMU page-table geometry and selects CPU-specific encodings. It belongs to the m68k architecture support inside the ceph-client Linux source snapshot, so its behavior is architecture/kernel plumbing rather than Ceph protocol logic. Source read size: 168 lines and 4701 bytes.

## Important APIs, Types, And Data

Primary surface: page-table shifts/sizes, `PTRS_PER_*`, `VMALLOC/KMAP` ranges, `set_pte()`,
`swapper_pg_dir`, `kernel_set_cachemode()`, and `update_mmu_cache_range()`. Representative
preprocessor definitions seen in the file are `_M68K_PGTABLE_H`, `set_pte(pteptr, pteval)`,
`PMD_SHIFT`, `PMD_SIZE`, `PMD_MASK`, `PGDIR_SHIFT`, `PGDIR_SIZE`, `PGDIR_MASK`, `PTRS_PER_PTE`,
`__PAGETABLE_PMD_FOLDED`, `PTRS_PER_PMD`, `PTRS_PER_PGD`, `USER_PTRS_PER_PGD`, `KMAP_START`.
Representative callable or assembly entry symbols are `kernel_set_cachemode`,
`update_mmu_cache_range`. Representative structs/unions/enums are none. Direct includes are `asm-
generic/pgtable-nopmd.h`, `asm-generic/pgtable-nopud.h`, `asm/mcf_pgtable.h`,
`asm/motorola_pgtable.h`, `asm/processor.h`, `asm/setup.h`, `asm/sun3_pgtable.h`,
`asm/virtconvert.h`.

## Control Flow And Integration

included by `pgtable.h` for MMU builds and delegates final PTE flags to Sun3/ColdFire/Motorola
headers. Most headers in this subset contribute through compile-time selection and inline helpers;
the C and assembly files add runtime entry points. Control reaches these definitions from generic
Linux subsystems such as memory management, scheduler context switching, traps, syscall dispatch,
DMA mapping, console setup, procfs, module loading, or board-specific drivers.

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

layout constants vary by MMU family; wrong fold/level sizing corrupts page-table walks. Additional
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/pgtable_mm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/pgtable_no.h -->
# sources/distributed-fs/ceph-client/arch/m68k/include/asm/pgtable_no.h

## Purpose

`pgtable_no.h` provides stub page-table definitions for no-MMU kernels. It belongs to the m68k architecture support inside the ceph-client Linux source snapshot, so its behavior is architecture/kernel plumbing rather than Ceph protocol logic. Source read size: 42 lines and 931 bytes.

## Important APIs, Types, And Data

Primary surface: constant pgd predicates, protection presets, `swapper_pg_dir`, and VMALLOC/KMAP
range stubs. Representative preprocessor definitions seen in the file are `_M68KNOMMU_PGTABLE_H`,
`pgd_present(pgd)`, `pgd_none(pgd)`, `pgd_bad(pgd)`, `pgd_clear(pgdp)`, `pmd_offset(a, b)`,
`PAGE_NONE`, `PAGE_SHARED`, `PAGE_COPY`, `PAGE_READONLY`, `PAGE_KERNEL`, `swapper_pg_dir`,
`VMALLOC_START`, `VMALLOC_END`. Representative callable or assembly entry symbols are none.
Representative structs/unions/enums are none. Direct includes are `asm-generic/pgtable-nopud.h`,
`asm/io.h`, `asm/page.h`, `asm/processor.h`, `linux/slab.h`.

## Control Flow And Integration

lets generic mm code compile for flat-memory m68k. Most headers in this subset contribute through
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

many operations are compile-time no-ops; code must not infer real memory protection in no-MMU
builds. Additional cross-cutting risks are conditional compilation drift between MMU families,
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/pgtable_no.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/processor.h -->
# sources/distributed-fs/ceph-client/arch/m68k/include/asm/processor.h

## Purpose

`processor.h` defines m68k task CPU state, address-space limits, and control-register helpers. It belongs to the m68k architecture support inside the ceph-client Linux source snapshot, so its behavior is architecture/kernel plumbing rather than Ceph protocol logic. Source read size: 179 lines and 4306 bytes.

## Important APIs, Types, And Data

Primary surface: `thread_struct`, `INIT_THREAD`, task size macros, user/supervisor function codes,
USP and FC accessors, `start_thread()`, `__get_wchan()`, and `show_registers()`. Representative
preprocessor definitions seen in the file are `__ASM_M68K_PROCESSOR_H`, `TASK_SIZE`, `STACK_TOP`,
`STACK_TOP_MAX`, `TASK_UNMAPPED_BASE`, `TASK_UNMAPPED_ALIGN(addr, off)`, `USER_DATA`,
`USER_PROGRAM`, `SUPER_DATA`, `SUPER_PROGRAM`, `CPU_SPACE`, `INIT_THREAD`, `setframeformat(_regs)`,
`KSTK_EIP(tsk)`. Representative callable or assembly entry symbols are `rdusp`, `wrusp`, `set_fc`,
`get_fc`, `start_thread`, `__get_wchan`, `show_registers`. Representative structs/unions/enums are
`thread_struct`, `task_struct`. Direct includes are `asm/fpu.h`, `asm/ptrace.h`, `linux/preempt.h`,
`linux/thread_info.h`.

## Control Flow And Integration

used by process creation, context switch, ptrace, signal, and scheduler code. Most headers in this
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

task-size and function-code choices differ by CPU/MMU model; incorrect values expose kernel memory
or break user entry. Additional cross-cutting risks are conditional compilation drift between MMU
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/processor.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/ptrace.h -->
# sources/distributed-fs/ceph-client/arch/m68k/include/asm/ptrace.h

## Purpose

`ptrace.h` wraps uapi ptrace registers with kernel-mode helper predicates. It belongs to the m68k architecture support inside the ceph-client Linux source snapshot, so its behavior is architecture/kernel plumbing rather than Ceph protocol logic. Source read size: 28 lines and 645 bytes.

## Important APIs, Types, And Data

Primary surface: `user_mode()`, `instruction_pointer()`, `profile_pc()`, current pt_regs/USP
helpers, and single-step capability macros. Representative preprocessor definitions seen in the file
are `_M68K_PTRACE_H`, `PS_S`, `PS_M`, `user_mode(regs)`, `instruction_pointer(regs)`,
`profile_pc(regs)`, `current_pt_regs()`, `current_user_stack_pointer()`, `arch_has_single_step()`,
`arch_has_block_step()`. Representative callable or assembly entry symbols are none. Representative
structs/unions/enums are none. Direct includes are `uapi/asm/ptrace.h`.

## Control Flow And Integration

used by tracing, perf, signal, syscall, and exception code. Most headers in this subset contribute
through compile-time selection and inline helpers; the C and assembly files add runtime entry
points. Control reaches these definitions from generic Linux subsystems such as memory management,
scheduler context switching, traps, syscall dispatch, DMA mapping, console setup, procfs, module
loading, or board-specific drivers.

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

register layout comes from UAPI; helper offsets must match assembly save frames. Additional cross-
cutting risks are conditional compilation drift between MMU families, inline assembly constraints
that differ between 68000/020/030/040/060/ColdFire, register-endianness mistakes on memory-mapped
buses, and ABI changes to exported bootinfo, ptrace, signal, stat, or syscall structures.

## Test Signals

Useful signals are m68k `defconfig`, allmodconfig where practical, and targeted builds for ColdFire
MMU, no-MMU, Sun3, Motorola MMU, Q40, Macintosh, Amiga, MVME, HP300 and virt configurations. Runtime
validation should cover boot to userspace, syscall tracing/seccomp, signal delivery and return,
fork/clone/vfork, module loading, DMA cache coherency tests, serial/early console output, interrupt
delivery, TLB flush stress, and userspace ABI checks for ptrace, stat, signal, cacheflush, and
bootinfo records.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/ptrace.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/q40_master.h -->
# sources/distributed-fs/ceph-client/arch/m68k/include/asm/q40_master.h

## Purpose

`q40_master.h` defines Q40 master I/O registers and bit helpers. It belongs to the m68k architecture support inside the ceph-client Linux source snapshot, so its behavior is architecture/kernel plumbing rather than Ceph protocol logic. Source read size: 70 lines and 2357 bytes.

## Important APIs, Types, And Data

Primary surface: keyboard, display, LED, interrupt, audio, floppy, serial, frame and sample
registers plus Q40 LED macros. Representative preprocessor definitions seen in the file are
`_Q40_MASTER_H`, `q40_master_addr`, `IIRQ_REG`, `EIRQ_REG`, `KEYCODE_REG`, `DISPLAY_CONTROL_REG`,
`FRAME_CLEAR_REG`, `LED_REG`, `Q40_LED_ON()`, `Q40_LED_OFF()`, `INTERRUPT_REG`,
`KEY_IRQ_ENABLE_REG`, `KEYBOARD_UNLOCK_REG`, `SAMPLE_ENABLE_REG`. Representative callable or
assembly entry symbols are none. Representative structs/unions/enums are none. Direct includes are
`asm/kmap.h`, `asm/q40ints.h`, `asm/raw_io.h`.

## Control Flow And Integration

used by Q40 platform, interrupt, console, and device drivers. Most headers in this subset contribute
through compile-time selection and inline helpers; the C and assembly files add runtime entry
points. Control reaches these definitions from generic Linux subsystems such as memory management,
scheduler context switching, traps, syscall dispatch, DMA mapping, console setup, procfs, module
loading, or board-specific drivers.

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

raw MMIO addresses have side effects; register polling/ack ordering needs hardware smoke tests.
Additional cross-cutting risks are conditional compilation drift between MMU families, inline
assembly constraints that differ between 68000/020/030/040/060/ColdFire, register-endianness
mistakes on memory-mapped buses, and ABI changes to exported bootinfo, ptrace, signal, stat, or
syscall structures.

## Test Signals

Useful signals are m68k `defconfig`, allmodconfig where practical, and targeted builds for ColdFire
MMU, no-MMU, Sun3, Motorola MMU, Q40, Macintosh, Amiga, MVME, HP300 and virt configurations. Runtime
validation should cover boot to userspace, syscall tracing/seccomp, signal delivery and return,
fork/clone/vfork, module loading, DMA cache coherency tests, serial/early console output, interrupt
delivery, TLB flush stress, and userspace ABI checks for ptrace, stat, signal, cacheflush, and
bootinfo records.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/q40_master.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/q40ints.h -->
# sources/distributed-fs/ceph-client/arch/m68k/include/asm/q40ints.h

## Purpose

`q40ints.h` defines Q40 interrupt numbers and masks. It belongs to the m68k architecture support inside the ceph-client Linux source snapshot, so its behavior is architecture/kernel plumbing rather than Ceph protocol logic. Source read size: 27 lines and 749 bytes.

## Important APIs, Types, And Data

Primary surface: Q40 IRQ max, sample/keyboard/frame IRQ numbers, and external IRQ mask bits.
Representative preprocessor definitions seen in the file are `Q40_IRQ_MAX`, `Q40_IRQ_SAMPLE`,
`Q40_IRQ_KEYBOARD`, `Q40_IRQ_FRAME`, `Q40_IRQ_KEYB_MASK`, `Q40_IRQ_SER_MASK`, `Q40_IRQ_FRAME_MASK`,
`Q40_IRQ_EXT_MASK`, `Q40_IRQ3_MASK`, `Q40_IRQ4_MASK`, `Q40_IRQ5_MASK`, `Q40_IRQ6_MASK`,
`Q40_IRQ7_MASK`, `Q40_IRQ10_MASK`. Representative callable or assembly entry symbols are none.
Representative structs/unions/enums are none. Direct includes are none.

## Control Flow And Integration

shared by Q40 interrupt controller and board code. Most headers in this subset contribute through
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

mask names must match `q40_master.h` interrupt register bits. Additional cross-cutting risks are
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/q40ints.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/quicc_simple.h -->
# sources/distributed-fs/ceph-client/arch/m68k/include/asm/quicc_simple.h

## Purpose

`quicc_simple.h` declares simple QUICC/SCC/SMC support routines. It belongs to the m68k architecture support inside the ceph-client Linux source snapshot, so its behavior is architecture/kernel plumbing rather than Ceph protocol logic. Source read size: 53 lines and 1830 bytes.

## Important APIs, Types, And Data

Primary surface: SCC global IDs, initialization, command issue, SCC/SMC start/loopback, interrupt
enable/disable, and descriptor print helpers. Representative preprocessor definitions seen in the
file are `__SIMPLE_H`, `GLB_SCC_0`, `GLB_SCC_1`, `GLB_SCC_2`, `GLB_SCC_3`. Representative callable
or assembly entry symbols are `quicc_issue_cmd`, `quicc_init`, `quicc_scc_init`, `quicc_smc_init`,
`quicc_scc_start`, `quicc_scc_loopback`, `IntrEna`, `print_rbd`, `print_tbd`. Representative
structs/unions/enums are none. Direct includes are none.

## Control Flow And Integration

used by older 68k QUICC platform serial/network support. Most headers in this subset contribute
through compile-time selection and inline helpers; the C and assembly files add runtime entry
points. Control reaches these definitions from generic Linux subsystems such as memory management,
scheduler context switching, traps, syscall dispatch, DMA mapping, console setup, procfs, module
loading, or board-specific drivers.

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

declarations lack rich typing in places, so implementation signatures and callers need compile
coverage. Additional cross-cutting risks are conditional compilation drift between MMU families,
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/quicc_simple.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/raw_io.h -->
# sources/distributed-fs/ceph-client/arch/m68k/include/asm/raw_io.h

## Purpose

`raw_io.h` implements endian-aware raw memory-mapped and port I/O helpers. It belongs to the m68k architecture support inside the ceph-client Linux source snapshot, so its behavior is architecture/kernel plumbing rather than Ceph protocol logic. Source read size: 474 lines and 12104 bytes.

## Important APIs, Types, And Data

Primary surface: `in_8`, `in_be16/32`, `in_le16/32`, `out_*`, raw read/write aliases, stream I/O
copy helpers, and ROM variants. Representative preprocessor definitions seen in the file are
`_RAW_IO_H`, `in_8(addr)`, `in_be16(addr)`, `in_be32(addr)`, `in_le16(addr)`, `in_le32(addr)`,
`out_8(addr,b)`, `out_be16(addr,w)`, `out_be32(addr,l)`, `out_le16(addr,w)`, `out_le32(addr,l)`,
`raw_inb`, `raw_inw`, `raw_inl`. Representative callable or assembly entry symbols are `raw_insb`,
`raw_outsb`, `raw_insw`, `raw_outsw`, `raw_insl`, `raw_outsl`, `raw_insw_swapw`, `raw_outsw_swapw`,
`raw_rom_insb`, `raw_rom_outsb`, `raw_rom_insw`, `raw_rom_outsw`, `raw_rom_insw_swapw`,
`raw_rom_outsw_swapw`. Representative structs/unions/enums are none. Direct includes are
`asm/byteorder.h`.

## Control Flow And Integration

foundation for m68k bus-specific headers such as NuBus, Zorro, Q40, VGA, and drivers. Most headers
in this subset contribute through compile-time selection and inline helpers; the C and assembly
files add runtime entry points. Control reaches these definitions from generic Linux subsystems such
as memory management, scheduler context switching, traps, syscall dispatch, DMA mapping, console
setup, procfs, module loading, or board-specific drivers.

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

endianness, volatile ordering, and address-space assumptions are the core risks. Additional cross-
cutting risks are conditional compilation drift between MMU families, inline assembly constraints
that differ between 68000/020/030/040/060/ColdFire, register-endianness mistakes on memory-mapped
buses, and ABI changes to exported bootinfo, ptrace, signal, stat, or syscall structures.

## Test Signals

Useful signals are m68k `defconfig`, allmodconfig where practical, and targeted builds for ColdFire
MMU, no-MMU, Sun3, Motorola MMU, Q40, Macintosh, Amiga, MVME, HP300 and virt configurations. Runtime
validation should cover boot to userspace, syscall tracing/seccomp, signal delivery and return,
fork/clone/vfork, module loading, DMA cache coherency tests, serial/early console output, interrupt
delivery, TLB flush stress, and userspace ABI checks for ptrace, stat, signal, cacheflush, and
bootinfo records.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/raw_io.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/seccomp.h -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/seccomp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/serial.h -->
# sources/distributed-fs/ceph-client/arch/m68k/include/asm/serial.h

## Purpose

`serial.h` defines default 8250 serial port descriptors for selected m68k machines. It belongs to the m68k architecture support inside the ceph-client Linux source snapshot, so its behavior is architecture/kernel plumbing rather than Ceph protocol logic. Source read size: 36 lines and 1165 bytes.

## Important APIs, Types, And Data

Primary surface: `BASE_BAUD`, `STD_COM_FLAGS`, `STD_COM4_FLAGS`, and `SERIAL_PORT_DFNS`.
Representative preprocessor definitions seen in the file are `BASE_BAUD`, `STD_COM_FLAGS`,
`STD_COM4_FLAGS`, `SERIAL_PORT_DFNS`. Representative callable or assembly entry symbols are none.
Representative structs/unions/enums are none. Direct includes are none.

## Control Flow And Integration

consumed by serial8250 platform discovery on m68k. Most headers in this subset contribute through
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

conditional flags and addresses vary by Q40/MVME/other systems; bad values produce stuck probes or
broken consoles. Additional cross-cutting risks are conditional compilation drift between MMU
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/serial.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/setup.h -->
# sources/distributed-fs/ceph-client/arch/m68k/include/asm/setup.h

## Purpose

`setup.h` declares kernel-side boot machine state, memory chunks, and machine predicates. It belongs to the m68k architecture support inside the ceph-client Linux source snapshot, so its behavior is architecture/kernel plumbing rather than Ceph protocol logic. Source read size: 335 lines and 10415 bytes.

## Important APIs, Types, And Data

Primary surface: `MACH_IS_*` macros, `MACH_TYPE`, `m68k_mem_info`, memory globals, hardware-present
flags, command-line/bootinfo declarations, and init prototypes. Representative preprocessor
definitions seen in the file are `_M68K_SETUP_H`, `CL_SIZE`, `MACH_IS_AMIGA`, `MACH_AMIGA_ONLY`,
`MACH_TYPE`, `MACH_IS_ATARI`, `MACH_ATARI_ONLY`, `MACH_IS_MAC`, `MACH_MAC_ONLY`, `MACH_IS_SUN3`,
`MACH_SUN3_ONLY`, `MACH_IS_APOLLO`, `MACH_APOLLO_ONLY`, `MACH_IS_MVME147`. Representative callable
or assembly entry symbols are none. Representative structs/unions/enums are `m68k_mem_info`. Direct
includes are `uapi/asm/bootinfo.h`, `uapi/asm/setup.h`.

## Control Flow And Integration

included by most platform setup, memory, console, and driver code. Most headers in this subset
contribute through compile-time selection and inline helpers; the C and assembly files add runtime
entry points. Control reaches these definitions from generic Linux subsystems such as memory
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

machine predicates collapse to constants under single-machine builds; multi-platform code must
preserve both paths. Additional cross-cutting risks are conditional compilation drift between MMU
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/setup.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/signal.h -->
# sources/distributed-fs/ceph-client/arch/m68k/include/asm/signal.h

## Purpose

`signal.h` wraps UAPI signal definitions with kernel sigset helpers. It belongs to the m68k architecture support inside the ceph-client Linux source snapshot, so its behavior is architecture/kernel plumbing rather than Ceph protocol logic. Source read size: 66 lines and 1377 bytes.

## Important APIs, Types, And Data

Primary surface: `_NSIG`, `__ARCH_HAS_SA_RESTORER`, `sigaddset()`, `sigdelset()`, and optimized
`sigismember()`. Representative preprocessor definitions seen in the file are `_M68K_SIGNAL_H`,
`_NSIG`, `_NSIG_BPW`, `_NSIG_WORDS`, `__ARCH_HAS_SA_RESTORER`, `__HAVE_ARCH_SIG_BITOPS`,
`sigismember(set,sig)`. Representative callable or assembly entry symbols are `sigaddset`,
`sigdelset`, `__const_sigismember`, `__gen_sigismember`. Representative structs/unions/enums are
none. Direct includes are `asm/sigcontext.h`, `uapi/asm/signal.h`.

## Control Flow And Integration

used by signal delivery and generic signal code. Most headers in this subset contribute through
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

bit numbering must match UAPI signal constants and m68k signal frame layout. Additional cross-
cutting risks are conditional compilation drift between MMU families, inline assembly constraints
that differ between 68000/020/030/040/060/ColdFire, register-endianness mistakes on memory-mapped
buses, and ABI changes to exported bootinfo, ptrace, signal, stat, or syscall structures.

## Test Signals

Useful signals are m68k `defconfig`, allmodconfig where practical, and targeted builds for ColdFire
MMU, no-MMU, Sun3, Motorola MMU, Q40, Macintosh, Amiga, MVME, HP300 and virt configurations. Runtime
validation should cover boot to userspace, syscall tracing/seccomp, signal delivery and return,
fork/clone/vfork, module loading, DMA cache coherency tests, serial/early console output, interrupt
delivery, TLB flush stress, and userspace ABI checks for ptrace, stat, signal, cacheflush, and
bootinfo records.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/signal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/smp.h -->
# sources/distributed-fs/ceph-client/arch/m68k/include/asm/smp.h

## Purpose

`smp.h` is an intentionally empty SMP placeholder. It belongs to the m68k architecture support inside the ceph-client Linux source snapshot, so its behavior is architecture/kernel plumbing rather than Ceph protocol logic. Source read size: 1 lines and 32 bytes.

## Important APIs, Types, And Data

Primary surface: no exported symbols. Representative preprocessor definitions seen in the file are
none. Representative callable or assembly entry symbols are none. Representative
structs/unions/enums are none. Direct includes are none.

## Control Flow And Integration

satisfies generic includes for an architecture that this tree treats as single-CPU. Most headers in
this subset contribute through compile-time selection and inline helpers; the C and assembly files
add runtime entry points. Control reaches these definitions from generic Linux subsystems such as
memory management, scheduler context switching, traps, syscall dispatch, DMA mapping, console setup,
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

future SMP work would need real CPU bring-up and per-CPU interrupt support rather than extending
this stub casually. Additional cross-cutting risks are conditional compilation drift between MMU
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/smp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/string.h -->
# sources/distributed-fs/ceph-client/arch/m68k/include/asm/string.h

## Purpose

`string.h` declares selected m68k string/memory optimized operations. It belongs to the m68k architecture support inside the ceph-client Linux source snapshot, so its behavior is architecture/kernel plumbing rather than Ceph protocol logic. Source read size: 55 lines and 1281 bytes.

## Important APIs, Types, And Data

Primary surface: `strnlen()`, `strncpy()`, `memmove()`, `memcmp()`, `memset()`, and `memcpy()` arch
hooks/macros. Representative preprocessor definitions seen in the file are `_M68K_STRING_H_`,
`__HAVE_ARCH_STRNLEN`, `__HAVE_ARCH_STRNCPY`, `__HAVE_ARCH_MEMMOVE`, `memcmp(d, s, n)`,
`__HAVE_ARCH_MEMSET`, `memset(d, c, n)`, `__HAVE_ARCH_MEMCPY`, `memcpy(d, s, n)`. Representative
callable or assembly entry symbols are `strnlen`, `strncpy`, `memmove`, `memcmp`, `memset`,
`memcpy`. Representative structs/unions/enums are none. Direct includes are `linux/compiler.h`,
`linux/types.h`.

## Control Flow And Integration

used by generic string and kernel library code when arch hooks are enabled. Most headers in this
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

macro aliasing means prototypes and inline/built-in behavior must stay compiler-compatible.
Additional cross-cutting risks are conditional compilation drift between MMU families, inline
assembly constraints that differ between 68000/020/030/040/060/ColdFire, register-endianness
mistakes on memory-mapped buses, and ABI changes to exported bootinfo, ptrace, signal, stat, or
syscall structures.

## Test Signals

Useful signals are m68k `defconfig`, allmodconfig where practical, and targeted builds for ColdFire
MMU, no-MMU, Sun3, Motorola MMU, Q40, Macintosh, Amiga, MVME, HP300 and virt configurations. Runtime
validation should cover boot to userspace, syscall tracing/seccomp, signal delivery and return,
fork/clone/vfork, module loading, DMA cache coherency tests, serial/early console output, interrupt
delivery, TLB flush stress, and userspace ABI checks for ptrace, stat, signal, cacheflush, and
bootinfo records.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/string.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/sun3-head.h -->
# sources/distributed-fs/ceph-client/arch/m68k/include/asm/sun3-head.h

## Purpose

`sun3-head.h` defines early Sun3 boot constants and function-code values. It belongs to the m68k architecture support inside the ceph-client Linux source snapshot, so its behavior is architecture/kernel plumbing rather than Ceph protocol logic. Source read size: 11 lines and 353 bytes.

## Important APIs, Types, And Data

Primary surface: `LOAD_ADDR`, `FC_CONTROL`, `FC_SUPERD`, and `FC_CPU`. Representative preprocessor
definitions seen in the file are `__SUN3_HEAD_H`, `KERNBASE`, `LOAD_ADDR`, `FC_CONTROL`,
`FC_SUPERD`, `FC_CPU`. Representative callable or assembly entry symbols are none. Representative
structs/unions/enums are none. Direct includes are none.

## Control Flow And Integration

used by Sun3 head/startup assembly and MMU code. Most headers in this subset contribute through
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

changing load address or function codes breaks earliest boot before diagnostics exist. Additional
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/sun3-head.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/sun3_pgalloc.h -->
# sources/distributed-fs/ceph-client/arch/m68k/include/asm/sun3_pgalloc.h

## Purpose

`sun3_pgalloc.h` implements Sun3 page-table allocation hooks. It belongs to the m68k architecture support inside the ceph-client Linux source snapshot, so its behavior is architecture/kernel plumbing rather than Ceph protocol logic. Source read size: 51 lines and 1218 bytes.

## Important APIs, Types, And Data

Primary surface: `pmd_populate_kernel()`, `pmd_populate()`, `pgd_alloc()`, `__pte_free_tlb`, and no-
op PMD free. Representative preprocessor definitions seen in the file are `_SUN3_PGALLOC_H`,
`__pte_free_tlb(tlb, pte, addr)`, `pmd_free(mm, x)`. Representative callable or assembly entry
symbols are `pmd_populate_kernel`, `pmd_populate`, `pgd_alloc`. Representative structs/unions/enums
are none. Direct includes are `asm-generic/pgalloc.h`, `asm/tlb.h`.

## Control Flow And Integration

used by Sun3 MMU builds with generic pgalloc. Most headers in this subset contribute through
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

Sun3 page tables are PMEG/segment based; generic freeing assumptions are intentionally constrained.
Additional cross-cutting risks are conditional compilation drift between MMU families, inline
assembly constraints that differ between 68000/020/030/040/060/ColdFire, register-endianness
mistakes on memory-mapped buses, and ABI changes to exported bootinfo, ptrace, signal, stat, or
syscall structures.

## Test Signals

Useful signals are m68k `defconfig`, allmodconfig where practical, and targeted builds for ColdFire
MMU, no-MMU, Sun3, Motorola MMU, Q40, Macintosh, Amiga, MVME, HP300 and virt configurations. Runtime
validation should cover boot to userspace, syscall tracing/seccomp, signal delivery and return,
fork/clone/vfork, module loading, DMA cache coherency tests, serial/early console output, interrupt
delivery, TLB flush stress, and userspace ABI checks for ptrace, stat, signal, cacheflush, and
bootinfo records.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/sun3_pgalloc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/sun3_pgtable.h -->
# sources/distributed-fs/ceph-client/arch/m68k/include/asm/sun3_pgtable.h

## Purpose

`sun3_pgtable.h` defines Sun3 MMU PTE/PMD encodings and helpers. It belongs to the m68k architecture support inside the ceph-client Linux source snapshot, so its behavior is architecture/kernel plumbing rather than Ceph protocol logic. Source read size: 190 lines and 6615 bytes.

## Important APIs, Types, And Data

Primary surface: Sun3 PTE flags, protection presets, page/PMD helpers, PTE state mutators, and swap-
entry encoding. Representative preprocessor definitions seen in the file are `_SUN3_PGTABLE_H`,
`VTOP(addr)`, `PTOV(addr)`, `_PAGE_NOCACHE030`, `_CACHEMASK040`, `_PAGE_NOCACHE_S`,
`SUN3_PAGE_VALID`, `SUN3_PAGE_WRITEABLE`, `SUN3_PAGE_SYSTEM`, `SUN3_PAGE_NOCACHE`,
`SUN3_PAGE_ACCESSED`, `SUN3_PAGE_MODIFIED`, `_PAGE_PRESENT`, `_PAGE_ACCESSED`. Representative
callable or assembly entry symbols are `pte_modify`, `pmd_page_vaddr`, `pte_none`, `pte_present`,
`pte_clear`, `pmd_none2`, `pmd_bad2`, `pmd_present2`, `pmd_clear`, `pte_write`, `pte_dirty`,
`pte_young`, `pte_wrprotect`, `pte_mkclean`. Representative structs/unions/enums are none. Direct
includes are `asm/sun3mmu.h`, `asm/virtconvert.h`, `linux/linkage.h`.

## Control Flow And Integration

included by `pgtable_mm.h` for `CONFIG_SUN3`. Most headers in this subset contribute through
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

Sun3 has nonstandard segment/page-map hardware; valid/write/system/cache bits must align with
`sun3mmu.h`. Additional cross-cutting risks are conditional compilation drift between MMU families,
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/sun3_pgtable.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/sun3ints.h -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/sun3ints.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/sun3mmu.h -->
# sources/distributed-fs/ceph-client/arch/m68k/include/asm/sun3mmu.h

## Purpose

`sun3mmu.h` implements Sun3 MMU control-space accessors and constants. It belongs to the m68k architecture support inside the ceph-client Linux source snapshot, so its behavior is architecture/kernel plumbing rather than Ceph protocol logic. Source read size: 172 lines and 5027 bytes.

## Important APIs, Types, And Data

Primary surface: PMEG/context sizes, control-space addresses, bus-error bits,
`sun3_get/put_segmap()`, `sun3_get/put_pte()`, context accessors, and `sun3_map_test()`.
Representative preprocessor definitions seen in the file are `__SUN3_MMU_H__`,
`SUN3_SEGMAPS_PER_CONTEXT`, `SUN3_PMEGS_NUM`, `SUN3_CONTEXTS_NUM`, `SUN3_PMEG_SIZE_BITS`,
`SUN3_PMEG_SIZE`, `SUN3_PMEG_MASK`, `SUN3_PTE_SIZE_BITS`, `SUN3_PTE_SIZE`, `SUN3_PTE_MASK`,
`SUN3_CONTROL_MASK`, `SUN3_INVALID_PMEG`, `SUN3_INVALID_CONTEXT`, `AC_IDPROM`. Representative
callable or assembly entry symbols are `sun3_get_buserr`, `sun3_get_segmap`, `sun3_put_segmap`,
`sun3_get_pte`, `sun3_put_pte`, `sun3_get_context`, `sun3_put_context`, `sun3_ioremap`,
`sun3_map_test`. Representative structs/unions/enums are none. Direct includes are `asm/movs.h`,
`asm/sun3-head.h`, `linux/types.h`.

## Control Flow And Integration

called by Sun3 paging, fault, and context-switch code. Most headers in this subset contribute
through compile-time selection and inline helpers; the C and assembly files add runtime entry
points. Control reaches these definitions from generic Linux subsystems such as memory management,
scheduler context switching, traps, syscall dispatch, DMA mapping, console setup, procfs, module
loading, or board-specific drivers.

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

uses `movs` control-space accesses, so CPU function-code setup and interrupt state matter.
Additional cross-cutting risks are conditional compilation drift between MMU families, inline
assembly constraints that differ between 68000/020/030/040/060/ColdFire, register-endianness
mistakes on memory-mapped buses, and ABI changes to exported bootinfo, ptrace, signal, stat, or
syscall structures.

## Test Signals

Useful signals are m68k `defconfig`, allmodconfig where practical, and targeted builds for ColdFire
MMU, no-MMU, Sun3, Motorola MMU, Q40, Macintosh, Amiga, MVME, HP300 and virt configurations. Runtime
validation should cover boot to userspace, syscall tracing/seccomp, signal delivery and return,
fork/clone/vfork, module loading, DMA cache coherency tests, serial/early console output, interrupt
delivery, TLB flush stress, and userspace ABI checks for ptrace, stat, signal, cacheflush, and
bootinfo records.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/sun3mmu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/sun3x.h -->
# sources/distributed-fs/ceph-client/arch/m68k/include/asm/sun3x.h

## Purpose

`sun3x.h` defines Sun3x memory-mapped hardware addresses. It belongs to the m68k architecture support inside the ceph-client Linux source snapshot, so its behavior is architecture/kernel plumbing rather than Ceph protocol logic. Source read size: 28 lines and 868 bytes.

## Important APIs, Types, And Data

Primary surface: IOMMU, interrupt, diagnostic, Zilog serial, Lance Ethernet, EEPROM, IDPROM, video,
ESP SCSI, and floppy controller addresses. Representative preprocessor definitions seen in the file
are `SUN3X_H`, `SUN3X_IOMMU`, `SUN3X_ENAREG`, `SUN3X_INTREG`, `SUN3X_DIAGREG`, `SUN3X_ZS1`,
`SUN3X_ZS2`, `SUN3X_LANCE`, `SUN3X_EEPROM`, `SUN3X_IDPROM`, `SUN3X_VIDEO_BASE`, `SUN3X_VIDEO_P4ID`,
`SUN3X_ESP_BASE`, `SUN3X_ESP_DMA`. Representative callable or assembly entry symbols are none.
Representative structs/unions/enums are none. Direct includes are none.

## Control Flow And Integration

used by Sun3x platform and device code. Most headers in this subset contribute through compile-time
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

hard-coded physical addresses must match Sun3x hardware revisions. Additional cross-cutting risks
are conditional compilation drift between MMU families, inline assembly constraints that differ
between 68000/020/030/040/060/ColdFire, register-endianness mistakes on memory-mapped buses, and ABI
changes to exported bootinfo, ptrace, signal, stat, or syscall structures.

## Test Signals

Useful signals are m68k `defconfig`, allmodconfig where practical, and targeted builds for ColdFire
MMU, no-MMU, Sun3, Motorola MMU, Q40, Macintosh, Amiga, MVME, HP300 and virt configurations. Runtime
validation should cover boot to userspace, syscall tracing/seccomp, signal delivery and return,
fork/clone/vfork, module loading, DMA cache coherency tests, serial/early console output, interrupt
delivery, TLB flush stress, and userspace ABI checks for ptrace, stat, signal, cacheflush, and
bootinfo records.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/sun3x.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/sun3xflop.h -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/sun3xflop.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/sun3xprom.h -->
# sources/distributed-fs/ceph-client/arch/m68k/include/asm/sun3xprom.h

## Purpose

`sun3xprom.h` defines Sun3x PROM entry addresses and helper declarations. It belongs to the m68k architecture support inside the ceph-client Linux source snapshot, so its behavior is architecture/kernel plumbing rather than Ceph protocol logic. Source read size: 44 lines and 1343 bytes.

## Important APIs, Types, And Data

Primary surface: PROM base/trap function offsets, reboot/abort/init/PTOV helpers, and PROM
getchar/putchar entry points. Representative preprocessor definitions seen in the file are
`SUN3X_PROM_H`, `SUN3X_IOMMU`, `SUN3X_ENAREG`, `SUN3X_INTREG`, `SUN3X_DIAGREG`, `SUN3X_ZS1`,
`SUN3X_ZS2`, `SUN3X_LANCE`, `SUN3X_EEPROM`, `SUN3X_IDPROM`, `SUN3X_VIDEO_BASE`, `SUN3X_VIDEO_REGS`,
`SUN3X_PROM_BASE`, `SUN3X_P_GETCHAR`. Representative callable or assembly entry symbols are `void`,
`int`, `sun3x_reboot`, `sun3x_abort`, `sun3x_prom_init`, `sun3x_prom_ptov`. Representative
structs/unions/enums are none. Direct includes are none.

## Control Flow And Integration

used by early Sun3x console and boot setup. Most headers in this subset contribute through compile-
time selection and inline helpers; the C and assembly files add runtime entry points. Control
reaches these definitions from generic Linux subsystems such as memory management, scheduler context
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

PROM function pointers are firmware ABI; invalid mapping can hang before the kernel console starts.
Additional cross-cutting risks are conditional compilation drift between MMU families, inline
assembly constraints that differ between 68000/020/030/040/060/ColdFire, register-endianness
mistakes on memory-mapped buses, and ABI changes to exported bootinfo, ptrace, signal, stat, or
syscall structures.

## Test Signals

Useful signals are m68k `defconfig`, allmodconfig where practical, and targeted builds for ColdFire
MMU, no-MMU, Sun3, Motorola MMU, Q40, Macintosh, Amiga, MVME, HP300 and virt configurations. Runtime
validation should cover boot to userspace, syscall tracing/seccomp, signal delivery and return,
fork/clone/vfork, module loading, DMA cache coherency tests, serial/early console output, interrupt
delivery, TLB flush stress, and userspace ABI checks for ptrace, stat, signal, cacheflush, and
bootinfo records.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/sun3xprom.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/switch_to.h -->
# sources/distributed-fs/ceph-client/arch/m68k/include/asm/switch_to.h

## Purpose

`switch_to.h` defines the m68k `switch_to()` macro and resume entry. It belongs to the m68k architecture support inside the ceph-client Linux source snapshot, so its behavior is architecture/kernel plumbing rather than Ceph protocol logic. Source read size: 42 lines and 1549 bytes.

## Important APIs, Types, And Data

Primary surface: `resume()` and the inline macro assigning `last`. Representative preprocessor
definitions seen in the file are `_M68K_SWITCH_TO_H`, `switch_to(prev,next,last)`. Representative
callable or assembly entry symbols are `resume`. Representative structs/unions/enums are none.
Direct includes are none.

## Control Flow And Integration

used by scheduler context switching. Most headers in this subset contribute through compile-time
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

assembly `resume` must preserve the calling convention expected by the macro and thread_struct
offsets. Additional cross-cutting risks are conditional compilation drift between MMU families,
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/switch_to.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/syscall.h -->
# sources/distributed-fs/ceph-client/arch/m68k/include/asm/syscall.h

## Purpose

`syscall.h` implements syscall inspection and mutation helpers for tracing/seccomp/audit. It belongs to the m68k architecture support inside the ceph-client Linux source snapshot, so its behavior is architecture/kernel plumbing rather than Ceph protocol logic. Source read size: 76 lines and 1574 bytes.

## Important APIs, Types, And Data

Primary surface: `syscall_get_nr()`, `syscall_set_nr()`, rollback, error/return helpers, argument
get/set, and `syscall_get_arch()`. Representative preprocessor definitions seen in the file are
`_ASM_M68K_SYSCALL_H`. Representative callable or assembly entry symbols are `syscall_get_nr`,
`syscall_set_nr`, `syscall_rollback`, `syscall_get_error`, `syscall_get_return_value`,
`syscall_set_return_value`, `syscall_get_arguments`, `syscall_set_arguments`, `syscall_get_arch`.
Representative structs/unions/enums are none. Direct includes are `asm/unistd.h`,
`uapi/linux/audit.h`.

## Control Flow And Integration

used by ptrace, seccomp, audit, and syscall tracing code. Most headers in this subset contribute
through compile-time selection and inline helpers; the C and assembly files add runtime entry
points. Control reaches these definitions from generic Linux subsystems such as memory management,
scheduler context switching, traps, syscall dispatch, DMA mapping, console setup, procfs, module
loading, or board-specific drivers.

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

argument registers are m68k ABI-specific; wrong indexing breaks tracers and seccomp emulation.
Additional cross-cutting risks are conditional compilation drift between MMU families, inline
assembly constraints that differ between 68000/020/030/040/060/ColdFire, register-endianness
mistakes on memory-mapped buses, and ABI changes to exported bootinfo, ptrace, signal, stat, or
syscall structures.

## Test Signals

Useful signals are m68k `defconfig`, allmodconfig where practical, and targeted builds for ColdFire
MMU, no-MMU, Sun3, Motorola MMU, Q40, Macintosh, Amiga, MVME, HP300 and virt configurations. Runtime
validation should cover boot to userspace, syscall tracing/seccomp, signal delivery and return,
fork/clone/vfork, module loading, DMA cache coherency tests, serial/early console output, interrupt
delivery, TLB flush stress, and userspace ABI checks for ptrace, stat, signal, cacheflush, and
bootinfo records.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/syscall.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/syscalls.h -->
# sources/distributed-fs/ceph-client/arch/m68k/include/asm/syscalls.h

## Purpose

`syscalls.h` declares m68k-specific syscall entry points. It belongs to the m68k architecture support inside the ceph-client Linux source snapshot, so its behavior is architecture/kernel plumbing rather than Ceph protocol logic. Source read size: 19 lines and 653 bytes.

## Important APIs, Types, And Data

Primary surface: `sys_cacheflush`, `sys_atomic_cmpxchg_32`, `sys_getpagesize`, thread-area syscalls,
and `sys_atomic_barrier`. Representative preprocessor definitions seen in the file are
`_ASM_M68K_SYSCALLS_H`. Representative callable or assembly entry symbols are `sys_cacheflush`,
`sys_atomic_cmpxchg_32`, `sys_getpagesize`, `sys_get_thread_area`, `sys_set_thread_area`,
`sys_atomic_barrier`. Representative structs/unions/enums are none. Direct includes are `asm-
generic/syscalls.h`, `linux/compiler_types.h`, `linux/linkage.h`.

## Control Flow And Integration

implemented in m68k kernel syscall code and referenced by syscall tables. Most headers in this
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

signatures are UAPI ABI; changing types breaks userspace syscall compatibility. Additional cross-
cutting risks are conditional compilation drift between MMU families, inline assembly constraints
that differ between 68000/020/030/040/060/ColdFire, register-endianness mistakes on memory-mapped
buses, and ABI changes to exported bootinfo, ptrace, signal, stat, or syscall structures.

## Test Signals

Useful signals are m68k `defconfig`, allmodconfig where practical, and targeted builds for ColdFire
MMU, no-MMU, Sun3, Motorola MMU, Q40, Macintosh, Amiga, MVME, HP300 and virt configurations. Runtime
validation should cover boot to userspace, syscall tracing/seccomp, signal delivery and return,
fork/clone/vfork, module loading, DMA cache coherency tests, serial/early console output, interrupt
delivery, TLB flush stress, and userspace ABI checks for ptrace, stat, signal, cacheflush, and
bootinfo records.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/syscalls.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/thread_info.h -->
# sources/distributed-fs/ceph-client/arch/m68k/include/asm/thread_info.h

## Purpose

`thread_info.h` defines low-level thread-info flags and stack size. It belongs to the m68k architecture support inside the ceph-client Linux source snapshot, so its behavior is architecture/kernel plumbing rather than Ceph protocol logic. Source read size: 80 lines and 2344 bytes.

## Important APIs, Types, And Data

Primary surface: `struct thread_info`, `THREAD_SIZE_ORDER`, `THREAD_SIZE`, `INIT_THREAD_INFO`, TIF
bits, and work masks. Representative preprocessor definitions seen in the file are
`_ASM_M68K_THREAD_INFO_H`, `THREAD_SIZE_ORDER`, `THREAD_SIZE`, `INIT_THREAD_INFO(tsk)`,
`TIF_NOTIFY_SIGNAL`, `TIF_NOTIFY_RESUME`, `TIF_SIGPENDING`, `TIF_NEED_RESCHED`, `TIF_SECCOMP`,
`TIF_DELAYED_TRACE`, `TIF_SYSCALL_TRACE`, `TIF_MEMDIE`, `TIF_RESTORE_SIGMASK`, `_TIF_NOTIFY_RESUME`.
Representative callable or assembly entry symbols are `current_thread_info`. Representative
structs/unions/enums are `thread_info`. Direct includes are `asm/page.h`, `asm/types.h`.

## Control Flow And Integration

used by entry assembly, scheduler, signal, seccomp, and syscall tracing. Most headers in this subset
contribute through compile-time selection and inline helpers; the C and assembly files add runtime
entry points. Control reaches these definitions from generic Linux subsystems such as memory
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

bit positions are read by assembly offsets; changes require regenerated asm offsets and entry tests.
Additional cross-cutting risks are conditional compilation drift between MMU families, inline
assembly constraints that differ between 68000/020/030/040/060/ColdFire, register-endianness
mistakes on memory-mapped buses, and ABI changes to exported bootinfo, ptrace, signal, stat, or
syscall structures.

## Test Signals

Useful signals are m68k `defconfig`, allmodconfig where practical, and targeted builds for ColdFire
MMU, no-MMU, Sun3, Motorola MMU, Q40, Macintosh, Amiga, MVME, HP300 and virt configurations. Runtime
validation should cover boot to userspace, syscall tracing/seccomp, signal delivery and return,
fork/clone/vfork, module loading, DMA cache coherency tests, serial/early console output, interrupt
delivery, TLB flush stress, and userspace ABI checks for ptrace, stat, signal, cacheflush, and
bootinfo records.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/thread_info.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/timex.h -->
# sources/distributed-fs/ceph-client/arch/m68k/include/asm/timex.h

## Purpose

`timex.h` defines m68k timer frequency and cycle helpers. It belongs to the m68k architecture support inside the ceph-client Linux source snapshot, so its behavior is architecture/kernel plumbing rather than Ceph protocol logic. Source read size: 42 lines and 974 bytes.

## Important APIs, Types, And Data

Primary surface: `CLOCK_TICK_RATE`, `get_cycles()`, and `random_get_entropy`. Representative
preprocessor definitions seen in the file are `_ASMm68K_TIMEX_H`, `CLOCK_TICK_RATE`,
`random_get_entropy`. Representative callable or assembly entry symbols are `get_cycles`, `long`,
`random_get_entropy`. Representative structs/unions/enums are none. Direct includes are
`asm/coldfire.h`.

## Control Flow And Integration

used by generic timekeeping and entropy code. Most headers in this subset contribute through
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

ColdFire may expose a different tick rate; `get_cycles()` returns zero here so callers must not
assume high-resolution cycle counters. Additional cross-cutting risks are conditional compilation
drift between MMU families, inline assembly constraints that differ between
68000/020/030/040/060/ColdFire, register-endianness mistakes on memory-mapped buses, and ABI changes
to exported bootinfo, ptrace, signal, stat, or syscall structures.

## Test Signals

Useful signals are m68k `defconfig`, allmodconfig where practical, and targeted builds for ColdFire
MMU, no-MMU, Sun3, Motorola MMU, Q40, Macintosh, Amiga, MVME, HP300 and virt configurations. Runtime
validation should cover boot to userspace, syscall tracing/seccomp, signal delivery and return,
fork/clone/vfork, module loading, DMA cache coherency tests, serial/early console output, interrupt
delivery, TLB flush stress, and userspace ABI checks for ptrace, stat, signal, cacheflush, and
bootinfo records.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/timex.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/tlb.h -->
# sources/distributed-fs/ceph-client/arch/m68k/include/asm/tlb.h

## Purpose

`tlb.h` selects generic TLB-gather definitions. It belongs to the m68k architecture support inside the ceph-client Linux source snapshot, so its behavior is architecture/kernel plumbing rather than Ceph protocol logic. Source read size: 7 lines and 135 bytes.

## Important APIs, Types, And Data

Primary surface: `asm-generic/tlb.h` include. Representative preprocessor definitions seen in the
file are `_M68K_TLB_H`. Representative callable or assembly entry symbols are none. Representative
structs/unions/enums are none. Direct includes are `asm-generic/tlb.h`.

## Control Flow And Integration

used by page-table free paths and mmu_gather. Most headers in this subset contribute through
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

minimal wrapper; backend pgalloc files supply architecture-specific free hooks. Additional cross-
cutting risks are conditional compilation drift between MMU families, inline assembly constraints
that differ between 68000/020/030/040/060/ColdFire, register-endianness mistakes on memory-mapped
buses, and ABI changes to exported bootinfo, ptrace, signal, stat, or syscall structures.

## Test Signals

Useful signals are m68k `defconfig`, allmodconfig where practical, and targeted builds for ColdFire
MMU, no-MMU, Sun3, Motorola MMU, Q40, Macintosh, Amiga, MVME, HP300 and virt configurations. Runtime
validation should cover boot to userspace, syscall tracing/seccomp, signal delivery and return,
fork/clone/vfork, module loading, DMA cache coherency tests, serial/early console output, interrupt
delivery, TLB flush stress, and userspace ABI checks for ptrace, stat, signal, cacheflush, and
bootinfo records.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/tlb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/tlbflush.h -->
# sources/distributed-fs/ceph-client/arch/m68k/include/asm/tlbflush.h

## Purpose

`tlbflush.h` implements TLB flush helpers for ColdFire, Sun3, and Motorola MMUs. It belongs to the m68k architecture support inside the ceph-client Linux source snapshot, so its behavior is architecture/kernel plumbing rather than Ceph protocol logic. Source read size: 273 lines and 5853 bytes.

## Important APIs, Types, And Data

Primary surface: `flush_tlb_all/mm/page/range/kernel_range/kernel_page`, low-level `__flush_tlb*`
helpers, and ColdFire MMUOR invalidation sequences. Representative preprocessor definitions seen in
the file are `_M68K_TLBFLUSH_H`, `flush_tlb()`. Representative callable or assembly entry symbols
are `flush_tlb_kernel_page`, `__flush_tlb`, `__flush_tlb040_one`, `__flush_tlb_one`,
`flush_tlb_all`, `flush_tlb_mm`, `flush_tlb_page`, `flush_tlb_range`, `flush_tlb_kernel_range`.
Representative structs/unions/enums are none. Direct includes are `asm/current.h`, `asm/mcfmmu.h`.

## Control Flow And Integration

called by mm, fault handling, cache-mode changes, and context switch code. Most headers in this
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

flush scope differs by CPU family; under-flushing leaves stale translations while over-flushing
hurts performance but is safer. Additional cross-cutting risks are conditional compilation drift
between MMU families, inline assembly constraints that differ between
68000/020/030/040/060/ColdFire, register-endianness mistakes on memory-mapped buses, and ABI changes
to exported bootinfo, ptrace, signal, stat, or syscall structures.

## Test Signals

Useful signals are m68k `defconfig`, allmodconfig where practical, and targeted builds for ColdFire
MMU, no-MMU, Sun3, Motorola MMU, Q40, Macintosh, Amiga, MVME, HP300 and virt configurations. Runtime
validation should cover boot to userspace, syscall tracing/seccomp, signal delivery and return,
fork/clone/vfork, module loading, DMA cache coherency tests, serial/early console output, interrupt
delivery, TLB flush stress, and userspace ABI checks for ptrace, stat, signal, cacheflush, and
bootinfo records.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/tlbflush.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/traps.h -->
# sources/distributed-fs/ceph-client/arch/m68k/include/asm/traps.h

## Purpose

`traps.h` defines m68k exception vector numbers, frame formats, and trap handlers. It belongs to the m68k architecture support inside the ceph-client Linux source snapshot, so its behavior is architecture/kernel plumbing rather than Ceph protocol logic. Source read size: 276 lines and 8618 bytes.

## Important APIs, Types, And Data

Primary surface: vector constants, frame format structs/unions, `struct frame`, bus-error bits, and
handler declarations such as `buserr_c`, `trap_c`, `auto_inthandler`, and `berr_040cleanup`.
Representative preprocessor definitions seen in the file are `_M68K_TRAPS_H`, `VEC_RESETSP`,
`VEC_RESETPC`, `VEC_BUSERR`, `VEC_ADDRERR`, `VEC_ILLEGAL`, `VEC_ZERODIV`, `VEC_CHK`, `VEC_TRAP`,
`VEC_PRIV`, `VEC_TRACE`, `VEC_LINE10`, `VEC_LINE11`, `VEC_RESV12`. Representative callable or
assembly entry symbols are `auto_inthandler`, `user_inthandler`, `bad_inthandler`,
`berr_040cleanup`. Representative structs/unions/enums are `frame`. Direct includes are
`asm/ptrace.h`, `linux/linkage.h`.

## Control Flow And Integration

shared by entry assembly, traps C code, ptrace, signal, and platform interrupt code. Most headers in
this subset contribute through compile-time selection and inline helpers; the C and assembly files
add runtime entry points. Control reaches these definitions from generic Linux subsystems such as
memory management, scheduler context switching, traps, syscall dispatch, DMA mapping, console setup,
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

frame layout must match CPU-pushed exception frames and assembly save offsets exactly. Additional
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/traps.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/uaccess.h -->
# sources/distributed-fs/ceph-client/arch/m68k/include/asm/uaccess.h

## Purpose

`uaccess.h` implements m68k user-memory access primitives. It belongs to the m68k architecture support inside the ceph-client Linux source snapshot, so its behavior is architecture/kernel plumbing rather than Ceph protocol logic. Source read size: 452 lines and 12221 bytes.

## Important APIs, Types, And Data

Primary surface: `get_user`, `put_user`, raw copy helpers, inline constant-size copy paths, kernel
nofault helpers, `strncpy_from_user`, `strnlen_user`, and `clear_user`. Representative preprocessor
definitions seen in the file are `__M68K_UACCESS_H`, `MOVES`, `__put_user_asm(inst, res, x, ptr,
bwl, reg, err)`, `__put_user_asm8(inst, res, x, ptr)`, `__put_user(x, ptr)`, `put_user(x, ptr)`,
`__get_user_asm(inst, res, x, ptr, type, bwl, reg, err)`, `__get_user_asm8(inst, res, x, ptr)`,
`__get_user(x, ptr)`, `get_user(x, ptr)`, `__suffix0`, `__suffix1`, `__suffix2`, `__suffix4`.
Representative callable or assembly entry symbols are `__generic_copy_from_user`,
`__generic_copy_to_user`, `strncpy_from_user`, `strnlen_user`, `__clear_user`. Representative
structs/unions/enums are none. Direct includes are `asm-generic/access_ok.h`, `asm-
generic/uaccess.h`, `asm/extable.h`, `linux/compiler.h`, `linux/types.h`.

## Control Flow And Integration

used by syscalls, filesystem, networking, and generic copy-to/from-user paths. Most headers in this
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

exception-table fixups, `moves` versus `move`, and partial-copy return counts are correctness-
critical. Additional cross-cutting risks are conditional compilation drift between MMU families,
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/uaccess.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/unistd.h -->
# sources/distributed-fs/ceph-client/arch/m68k/include/asm/unistd.h

## Purpose

`unistd.h` wraps UAPI syscall numbers and declares generic syscall feature wants. It belongs to the m68k architecture support inside the ceph-client Linux source snapshot, so its behavior is architecture/kernel plumbing rather than Ceph protocol logic. Source read size: 34 lines and 962 bytes.

## Important APIs, Types, And Data

Primary surface: `NR_syscalls` and `__ARCH_WANT_*` compatibility syscall selection macros.
Representative preprocessor definitions seen in the file are `_ASM_M68K_UNISTD_H_`, `NR_syscalls`,
`__ARCH_WANT_NEW_STAT`, `__ARCH_WANT_OLD_READDIR`, `__ARCH_WANT_OLD_STAT`, `__ARCH_WANT_STAT64`,
`__ARCH_WANT_SYS_ALARM`, `__ARCH_WANT_SYS_GETHOSTNAME`, `__ARCH_WANT_SYS_IPC`,
`__ARCH_WANT_SYS_PAUSE`, `__ARCH_WANT_SYS_SIGNAL`, `__ARCH_WANT_SYS_TIME32`,
`__ARCH_WANT_SYS_UTIME32`, `__ARCH_WANT_SYS_WAITPID`. Representative callable or assembly entry
symbols are none. Representative structs/unions/enums are none. Direct includes are
`uapi/asm/unistd.h`.

## Control Flow And Integration

included by syscall tables and generic syscall implementation selection. Most headers in this subset
contribute through compile-time selection and inline helpers; the C and assembly files add runtime
entry points. Control reaches these definitions from generic Linux subsystems such as memory
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

must track generated UAPI `unistd_32.h` and legacy m68k ABI expectations. Additional cross-cutting
risks are conditional compilation drift between MMU families, inline assembly constraints that
differ between 68000/020/030/040/060/ColdFire, register-endianness mistakes on memory-mapped buses,
and ABI changes to exported bootinfo, ptrace, signal, stat, or syscall structures.

## Test Signals

Useful signals are m68k `defconfig`, allmodconfig where practical, and targeted builds for ColdFire
MMU, no-MMU, Sun3, Motorola MMU, Q40, Macintosh, Amiga, MVME, HP300 and virt configurations. Runtime
validation should cover boot to userspace, syscall tracing/seccomp, signal delivery and return,
fork/clone/vfork, module loading, DMA cache coherency tests, serial/early console output, interrupt
delivery, TLB flush stress, and userspace ABI checks for ptrace, stat, signal, cacheflush, and
bootinfo records.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/unistd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/user.h -->
# sources/distributed-fs/ceph-client/arch/m68k/include/asm/user.h

## Purpose

`user.h` defines legacy core-dump/user structures. It belongs to the m68k architecture support inside the ceph-client Linux source snapshot, so its behavior is architecture/kernel plumbing rather than Ceph protocol logic. Source read size: 83 lines and 3732 bytes.

## Important APIs, Types, And Data

Primary surface: `struct user_m68kfp_struct`, `struct user_regs_struct`, and `struct user`.
Representative preprocessor definitions seen in the file are `_M68K_USER_H`. Representative callable
or assembly entry symbols are none. Representative structs/unions/enums are `user_m68kfp_struct`,
`user_regs_struct`, `user`. Direct includes are none.

## Control Flow And Integration

used by ptrace/core dump compatibility and old tooling interfaces. Most headers in this subset
contribute through compile-time selection and inline helpers; the C and assembly files add runtime
entry points. Control reaches these definitions from generic Linux subsystems such as memory
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

field order and sizes are external ABI for debuggers and core-file readers. Additional cross-cutting
risks are conditional compilation drift between MMU families, inline assembly constraints that
differ between 68000/020/030/040/060/ColdFire, register-endianness mistakes on memory-mapped buses,
and ABI changes to exported bootinfo, ptrace, signal, stat, or syscall structures.

## Test Signals

Useful signals are m68k `defconfig`, allmodconfig where practical, and targeted builds for ColdFire
MMU, no-MMU, Sun3, Motorola MMU, Q40, Macintosh, Amiga, MVME, HP300 and virt configurations. Runtime
validation should cover boot to userspace, syscall tracing/seccomp, signal delivery and return,
fork/clone/vfork, module loading, DMA cache coherency tests, serial/early console output, interrupt
delivery, TLB flush stress, and userspace ABI checks for ptrace, stat, signal, cacheflush, and
bootinfo records.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/user.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/vga.h -->
# sources/distributed-fs/ceph-client/arch/m68k/include/asm/vga.h

## Purpose

`vga.h` maps VGA I/O helpers to m68k raw I/O and kmap routines. It belongs to the m68k architecture support inside the ceph-client Linux source snapshot, so its behavior is architecture/kernel plumbing rather than Ceph protocol logic. Source read size: 37 lines and 902 bytes.

## Important APIs, Types, And Data

Primary surface: `inb_p`, `inw_p`, `outb_p`, `outw`, `readb`, `writeb`, and `writew` aliases.
Representative preprocessor definitions seen in the file are `_ASM_M68K_VGA_H`, `inb_p(port)`,
`inw_p(port)`, `outb_p(port, val)`, `outw(port, val)`, `readb`, `writeb`, `writew`. Representative
callable or assembly entry symbols are none. Representative structs/unions/enums are none. Direct
includes are `asm/io.h`, `asm/kmap.h`.

## Control Flow And Integration

used by generic VGA/console drivers on m68k systems. Most headers in this subset contribute through
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

endianness and bus mapping depend on the underlying platform I/O implementation. Additional cross-
cutting risks are conditional compilation drift between MMU families, inline assembly constraints
that differ between 68000/020/030/040/060/ColdFire, register-endianness mistakes on memory-mapped
buses, and ABI changes to exported bootinfo, ptrace, signal, stat, or syscall structures.

## Test Signals

Useful signals are m68k `defconfig`, allmodconfig where practical, and targeted builds for ColdFire
MMU, no-MMU, Sun3, Motorola MMU, Q40, Macintosh, Amiga, MVME, HP300 and virt configurations. Runtime
validation should cover boot to userspace, syscall tracing/seccomp, signal delivery and return,
fork/clone/vfork, module loading, DMA cache coherency tests, serial/early console output, interrupt
delivery, TLB flush stress, and userspace ABI checks for ptrace, stat, signal, cacheflush, and
bootinfo records.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/vga.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/video.h -->
# sources/distributed-fs/ceph-client/arch/m68k/include/asm/video.h

## Purpose

`video.h` defines framebuffer page-protection adjustment. It belongs to the m68k architecture support inside the ceph-client Linux source snapshot, so its behavior is architecture/kernel plumbing rather than Ceph protocol logic. Source read size: 32 lines and 733 bytes.

## Important APIs, Types, And Data

Primary surface: `pgprot_framebuffer()` returning m68k `pgprot_noncached()` plus generic video
helpers. Representative preprocessor definitions seen in the file are `_ASM_VIDEO_H_`,
`pgprot_framebuffer`. Representative callable or assembly entry symbols are `pgprot_framebuffer`.
Representative structs/unions/enums are none. Direct includes are `asm-generic/video.h`,
`asm/page.h`, `asm/setup.h`.

## Control Flow And Integration

used by framebuffer/video mappings. Most headers in this subset contribute through compile-time
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

framebuffer mappings must be uncached to avoid stale display memory or write-combining mismatches.
Additional cross-cutting risks are conditional compilation drift between MMU families, inline
assembly constraints that differ between 68000/020/030/040/060/ColdFire, register-endianness
mistakes on memory-mapped buses, and ABI changes to exported bootinfo, ptrace, signal, stat, or
syscall structures.

## Test Signals

Useful signals are m68k `defconfig`, allmodconfig where practical, and targeted builds for ColdFire
MMU, no-MMU, Sun3, Motorola MMU, Q40, Macintosh, Amiga, MVME, HP300 and virt configurations. Runtime
validation should cover boot to userspace, syscall tracing/seccomp, signal delivery and return,
fork/clone/vfork, module loading, DMA cache coherency tests, serial/early console output, interrupt
delivery, TLB flush stress, and userspace ABI checks for ptrace, stat, signal, cacheflush, and
bootinfo records.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/video.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/virt.h -->
# sources/distributed-fs/ceph-client/arch/m68k/include/asm/virt.h

## Purpose

`virt.h` declares m68k virtual-machine boot data and IRQ setup. It belongs to the m68k architecture support inside the ceph-client Linux source snapshot, so its behavior is architecture/kernel plumbing rather than Ceph protocol logic. Source read size: 25 lines and 502 bytes.

## Important APIs, Types, And Data

Primary surface: `struct virt_booter_device_data`, `struct virt_booter_data`, and `virt_init_IRQ()`.
Representative preprocessor definitions seen in the file are `__ASM_VIRT_H`, `NUM_VIRT_SOURCES`.
Representative callable or assembly entry symbols are `virt_init_IRQ`. Representative
structs/unions/enums are `virt_booter_device_data`, `virt_booter_data`. Direct includes are none.

## Control Flow And Integration

used by the m68k virt platform boot and interrupt setup. Most headers in this subset contribute
through compile-time selection and inline helpers; the C and assembly files add runtime entry
points. Control reaches these definitions from generic Linux subsystems such as memory management,
scheduler context switching, traps, syscall dispatch, DMA mapping, console setup, procfs, module
loading, or board-specific drivers.

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

booter data is firmware/emulator ABI; base addresses and IRQs must be validated before registering
devices. Additional cross-cutting risks are conditional compilation drift between MMU families,
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/virt.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/virtconvert.h -->
# sources/distributed-fs/ceph-client/arch/m68k/include/asm/virtconvert.h

## Purpose

`virtconvert.h` provides legacy virtual/physical/bus conversion macros. It belongs to the m68k architecture support inside the ceph-client Linux source snapshot, so its behavior is architecture/kernel plumbing rather than Ceph protocol logic. Source read size: 40 lines and 815 bytes.

## Important APIs, Types, And Data

Primary surface: `virt_to_phys`, `phys_to_virt`, `virt_to_bus`, and optional `virt_to_phys()`
inline. Representative preprocessor definitions seen in the file are `__VIRT_CONVERT__`,
`virt_to_phys`, `phys_to_virt`, `virt_to_bus`. Representative callable or assembly entry symbols are
`virt_to_phys`, `phys_to_virt`. Representative structs/unions/enums are none. Direct includes are
`asm/page.h`, `asm/setup.h`, `linux/compiler.h`, `linux/mmzone.h`.

## Control Flow And Integration

used by older m68k drivers and platform code. Most headers in this subset contribute through
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

bus and physical addresses are not always equivalent on all systems; aliases can hide DMA
translation issues. Additional cross-cutting risks are conditional compilation drift between MMU
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/virtconvert.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/vmalloc.h -->
# sources/distributed-fs/ceph-client/arch/m68k/include/asm/vmalloc.h

## Purpose

`vmalloc.h` defines the m68k vmalloc header guard only. It belongs to the m68k architecture support inside the ceph-client Linux source snapshot, so its behavior is architecture/kernel plumbing rather than Ceph protocol logic. Source read size: 4 lines and 90 bytes.

## Important APIs, Types, And Data

Primary surface: no runtime API. Representative preprocessor definitions seen in the file are
`_ASM_M68K_VMALLOC_H`. Representative callable or assembly entry symbols are none. Representative
structs/unions/enums are none. Direct includes are none.

## Control Flow And Integration

included by generic vmalloc code for architecture overrides. Most headers in this subset contribute
through compile-time selection and inline helpers; the C and assembly files add runtime entry
points. Control reaches these definitions from generic Linux subsystems such as memory management,
scheduler context switching, traps, syscall dispatch, DMA mapping, console setup, procfs, module
loading, or board-specific drivers.

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

empty by design; vmalloc layout is defined in pgtable headers instead. Additional cross-cutting
risks are conditional compilation drift between MMU families, inline assembly constraints that
differ between 68000/020/030/040/060/ColdFire, register-endianness mistakes on memory-mapped buses,
and ABI changes to exported bootinfo, ptrace, signal, stat, or syscall structures.

## Test Signals

Useful signals are m68k `defconfig`, allmodconfig where practical, and targeted builds for ColdFire
MMU, no-MMU, Sun3, Motorola MMU, Q40, Macintosh, Amiga, MVME, HP300 and virt configurations. Runtime
validation should cover boot to userspace, syscall tracing/seccomp, signal delivery and return,
fork/clone/vfork, module loading, DMA cache coherency tests, serial/early console output, interrupt
delivery, TLB flush stress, and userspace ABI checks for ptrace, stat, signal, cacheflush, and
bootinfo records.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/vmalloc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/zorro.h -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/zorro.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/uapi/asm/Kbuild -->
# sources/distributed-fs/ceph-client/arch/m68k/include/uapi/asm/Kbuild

## Purpose

`Kbuild` declares generated UAPI header inclusion for m68k. It belongs to the m68k architecture support inside the ceph-client Linux source snapshot, so its behavior is architecture/kernel plumbing rather than Ceph protocol logic. Source read size: 2 lines and 62 bytes.

## Important APIs, Types, And Data

Primary surface: `generated-y += syscall_table.h` and `generic-y += kvm_para.h`. Representative
preprocessor definitions seen in the file are none. Representative callable or assembly entry
symbols are none. Representative structs/unions/enums are none. Direct includes are none.

## Control Flow And Integration

used by the kernel headers install/build machinery. Most headers in this subset contribute through
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

missing generated headers break userspace header export or syscall table generation. Additional
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/uapi/asm/Kbuild -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/uapi/asm/a.out.h -->
# sources/distributed-fs/ceph-client/arch/m68k/include/uapi/asm/a.out.h

## Purpose

`a.out.h` defines m68k a.out executable header layout helpers. It belongs to the m68k architecture support inside the ceph-client Linux source snapshot, so its behavior is architecture/kernel plumbing rather than Ceph protocol logic. Source read size: 21 lines and 772 bytes.

## Important APIs, Types, And Data

Primary surface: `struct exec`, `N_TRSIZE()`, `N_DRSIZE()`, and `N_SYMSIZE()`. Representative
preprocessor definitions seen in the file are `__M68K_A_OUT_H__`, `N_TRSIZE(a)`, `N_DRSIZE(a)`,
`N_SYMSIZE(a)`. Representative callable or assembly entry symbols are none. Representative
structs/unions/enums are `exec`. Direct includes are none.

## Control Flow And Integration

used by legacy binary format support and UAPI consumers. Most headers in this subset contribute
through compile-time selection and inline helpers; the C and assembly files add runtime entry
points. Control reaches these definitions from generic Linux subsystems such as memory management,
scheduler context switching, traps, syscall dispatch, DMA mapping, console setup, procfs, module
loading, or board-specific drivers.

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

external ABI; changing field widths breaks old a.out tools. Additional cross-cutting risks are
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/uapi/asm/a.out.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/uapi/asm/bootinfo-amiga.h -->
# sources/distributed-fs/ceph-client/arch/m68k/include/uapi/asm/bootinfo-amiga.h

## Purpose

`bootinfo-amiga.h` defines Amiga bootinfo record tags and model/chipset constants. It belongs to the m68k architecture support inside the ceph-client Linux source snapshot, so its behavior is architecture/kernel plumbing rather than Ceph protocol logic. Source read size: 64 lines and 1495 bytes.

## Important APIs, Types, And Data

Primary surface: `BI_AMIGA_*` tags, `AMI_*` model identifiers, chipset, clock and serial-period
values. Representative preprocessor definitions seen in the file are
`_UAPI_ASM_M68K_BOOTINFO_AMIGA_H`, `BI_AMIGA_MODEL`, `BI_AMIGA_AUTOCON`, `BI_AMIGA_CHIP_SIZE`,
`BI_AMIGA_VBLANK`, `BI_AMIGA_PSFREQ`, `BI_AMIGA_ECLOCK`, `BI_AMIGA_CHIPSET`, `BI_AMIGA_SERPER`,
`AMI_UNKNOWN`, `AMI_500`, `AMI_500PLUS`, `AMI_600`, `AMI_1000`. Representative callable or assembly
entry symbols are none. Representative structs/unions/enums are none. Direct includes are none.

## Control Flow And Integration

consumed by bootloaders and kernel setup parsing. Most headers in this subset contribute through
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

record numbers are UAPI; mismatches misidentify hardware capabilities. Additional cross-cutting
risks are conditional compilation drift between MMU families, inline assembly constraints that
differ between 68000/020/030/040/060/ColdFire, register-endianness mistakes on memory-mapped buses,
and ABI changes to exported bootinfo, ptrace, signal, stat, or syscall structures.

## Test Signals

Useful signals are m68k `defconfig`, allmodconfig where practical, and targeted builds for ColdFire
MMU, no-MMU, Sun3, Motorola MMU, Q40, Macintosh, Amiga, MVME, HP300 and virt configurations. Runtime
validation should cover boot to userspace, syscall tracing/seccomp, signal delivery and return,
fork/clone/vfork, module loading, DMA cache coherency tests, serial/early console output, interrupt
delivery, TLB flush stress, and userspace ABI checks for ptrace, stat, signal, cacheflush, and
bootinfo records.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/uapi/asm/bootinfo-amiga.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/uapi/asm/bootinfo-apollo.h -->
# sources/distributed-fs/ceph-client/arch/m68k/include/uapi/asm/bootinfo-apollo.h

## Purpose

`bootinfo-apollo.h` defines Apollo bootinfo model tags. It belongs to the m68k architecture support inside the ceph-client Linux source snapshot, so its behavior is architecture/kernel plumbing rather than Ceph protocol logic. Source read size: 29 lines and 582 bytes.

## Important APIs, Types, And Data

Primary surface: `BI_APOLLO_MODEL` and Apollo DN model constants. Representative preprocessor
definitions seen in the file are `_UAPI_ASM_M68K_BOOTINFO_APOLLO_H`, `BI_APOLLO_MODEL`,
`APOLLO_UNKNOWN`, `APOLLO_DN3000`, `APOLLO_DN3010`, `APOLLO_DN3500`, `APOLLO_DN4000`,
`APOLLO_DN4500`. Representative callable or assembly entry symbols are none. Representative
structs/unions/enums are none. Direct includes are none.

## Control Flow And Integration

used by Apollo bootloader/kernel setup. Most headers in this subset contribute through compile-time
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

limited UAPI surface but model values must remain stable. Additional cross-cutting risks are
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/uapi/asm/bootinfo-apollo.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/uapi/asm/bootinfo-atari.h -->
# sources/distributed-fs/ceph-client/arch/m68k/include/uapi/asm/bootinfo-atari.h

## Purpose

`bootinfo-atari.h` defines Atari bootinfo machine-cookie and model constants. It belongs to the m68k architecture support inside the ceph-client Linux source snapshot, so its behavior is architecture/kernel plumbing rather than Ceph protocol logic. Source read size: 45 lines and 1015 bytes.

## Important APIs, Types, And Data

Primary surface: `BI_ATARI_MCH_COOKIE`, `BI_ATARI_MCH_TYPE`, Atari machine IDs, and bootinfo
version. Representative preprocessor definitions seen in the file are
`_UAPI_ASM_M68K_BOOTINFO_ATARI_H`, `BI_ATARI_MCH_COOKIE`, `BI_ATARI_MCH_TYPE`, `ATARI_MCH_ST`,
`ATARI_MCH_STE`, `ATARI_MCH_TT`, `ATARI_MCH_FALCON`, `ATARI_MACH_NORMAL`, `ATARI_MACH_MEDUSA`,
`ATARI_MACH_HADES`, `ATARI_MACH_AB40`, `ATARI_BOOTI_VERSION`. Representative callable or assembly
entry symbols are none. Representative structs/unions/enums are none. Direct includes are none.

## Control Flow And Integration

used by Atari boot setup and hardware probing. Most headers in this subset contribute through
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

cookie/type values drive platform feature selection. Additional cross-cutting risks are conditional
compilation drift between MMU families, inline assembly constraints that differ between
68000/020/030/040/060/ColdFire, register-endianness mistakes on memory-mapped buses, and ABI changes
to exported bootinfo, ptrace, signal, stat, or syscall structures.

## Test Signals

Useful signals are m68k `defconfig`, allmodconfig where practical, and targeted builds for ColdFire
MMU, no-MMU, Sun3, Motorola MMU, Q40, Macintosh, Amiga, MVME, HP300 and virt configurations. Runtime
validation should cover boot to userspace, syscall tracing/seccomp, signal delivery and return,
fork/clone/vfork, module loading, DMA cache coherency tests, serial/early console output, interrupt
delivery, TLB flush stress, and userspace ABI checks for ptrace, stat, signal, cacheflush, and
bootinfo records.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/uapi/asm/bootinfo-atari.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/uapi/asm/bootinfo-hp300.h -->
# sources/distributed-fs/ceph-client/arch/m68k/include/uapi/asm/bootinfo-hp300.h

## Purpose

`bootinfo-hp300.h` defines HP300 bootinfo tags and model constants. It belongs to the m68k architecture support inside the ceph-client Linux source snapshot, so its behavior is architecture/kernel plumbing rather than Ceph protocol logic. Source read size: 51 lines and 1534 bytes.

## Important APIs, Types, And Data

Primary surface: `BI_HP300_*`, HP model IDs, and UART scode/address tags. Representative
preprocessor definitions seen in the file are `_UAPI_ASM_M68K_BOOTINFO_HP300_H`, `BI_HP300_MODEL`,
`BI_HP300_UART_SCODE`, `BI_HP300_UART_ADDR`, `HP_320`, `HP_330`, `HP_340`, `HP_345`, `HP_350`,
`HP_360`, `HP_370`, `HP_375`, `HP_380`, `HP_385`. Representative callable or assembly entry symbols
are none. Representative structs/unions/enums are none. Direct includes are none.

## Control Flow And Integration

used by HP300 setup and serial discovery. Most headers in this subset contribute through compile-
time selection and inline helpers; the C and assembly files add runtime entry points. Control
reaches these definitions from generic Linux subsystems such as memory management, scheduler context
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

incorrect model/UART metadata breaks early console and device probing. Additional cross-cutting
risks are conditional compilation drift between MMU families, inline assembly constraints that
differ between 68000/020/030/040/060/ColdFire, register-endianness mistakes on memory-mapped buses,
and ABI changes to exported bootinfo, ptrace, signal, stat, or syscall structures.

## Test Signals

Useful signals are m68k `defconfig`, allmodconfig where practical, and targeted builds for ColdFire
MMU, no-MMU, Sun3, Motorola MMU, Q40, Macintosh, Amiga, MVME, HP300 and virt configurations. Runtime
validation should cover boot to userspace, syscall tracing/seccomp, signal delivery and return,
fork/clone/vfork, module loading, DMA cache coherency tests, serial/early console output, interrupt
delivery, TLB flush stress, and userspace ABI checks for ptrace, stat, signal, cacheflush, and
bootinfo records.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/uapi/asm/bootinfo-hp300.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/uapi/asm/bootinfo-mac.h -->
# sources/distributed-fs/ceph-client/arch/m68k/include/uapi/asm/bootinfo-mac.h

## Purpose

`bootinfo-mac.h` defines Macintosh bootinfo tags and hardware identifiers. It belongs to the m68k architecture support inside the ceph-client Linux source snapshot, so its behavior is architecture/kernel plumbing rather than Ceph protocol logic. Source read size: 120 lines and 4558 bytes.

## Important APIs, Types, And Data

Primary surface: Mac model, video, SCC, time, memory, CPU, ROM, VIA, ADB, ASC, SCSI, IDE, and serial
hardware tags plus many model constants. Representative preprocessor definitions seen in the file
are `_UAPI_ASM_M68K_BOOTINFO_MAC_H`, `BI_MAC_MODEL`, `BI_MAC_VADDR`, `BI_MAC_VDEPTH`, `BI_MAC_VROW`,
`BI_MAC_VDIM`, `BI_MAC_VLOGICAL`, `BI_MAC_SCCBASE`, `BI_MAC_BTIME`, `BI_MAC_GMTBIAS`,
`BI_MAC_MEMSIZE`, `BI_MAC_CPUID`, `BI_MAC_ROMBASE`, `BI_MAC_VIA1BASE`. Representative callable or
assembly entry symbols are none. Representative structs/unions/enums are none. Direct includes are
none.

## Control Flow And Integration

used by m68k Mac bootloaders and kernel platform setup. Most headers in this subset contribute
through compile-time selection and inline helpers; the C and assembly files add runtime entry
points. Control reaches these definitions from generic Linux subsystems such as memory management,
scheduler context switching, traps, syscall dispatch, DMA mapping, console setup, procfs, module
loading, or board-specific drivers.

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

large UAPI table; numeric stability is essential for old bootloaders. Additional cross-cutting risks
are conditional compilation drift between MMU families, inline assembly constraints that differ
between 68000/020/030/040/060/ColdFire, register-endianness mistakes on memory-mapped buses, and ABI
changes to exported bootinfo, ptrace, signal, stat, or syscall structures.

## Test Signals

Useful signals are m68k `defconfig`, allmodconfig where practical, and targeted builds for ColdFire
MMU, no-MMU, Sun3, Motorola MMU, Q40, Macintosh, Amiga, MVME, HP300 and virt configurations. Runtime
validation should cover boot to userspace, syscall tracing/seccomp, signal delivery and return,
fork/clone/vfork, module loading, DMA cache coherency tests, serial/early console output, interrupt
delivery, TLB flush stress, and userspace ABI checks for ptrace, stat, signal, cacheflush, and
bootinfo records.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/uapi/asm/bootinfo-mac.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/uapi/asm/bootinfo-q40.h -->
# sources/distributed-fs/ceph-client/arch/m68k/include/uapi/asm/bootinfo-q40.h

## Purpose

`bootinfo-q40.h` defines Q40 bootinfo version metadata. It belongs to the m68k architecture support inside the ceph-client Linux source snapshot, so its behavior is architecture/kernel plumbing rather than Ceph protocol logic. Source read size: 17 lines and 358 bytes.

## Important APIs, Types, And Data

Primary surface: `Q40_BOOTI_VERSION`. Representative preprocessor definitions seen in the file are
`_UAPI_ASM_M68K_BOOTINFO_Q40_H`, `Q40_BOOTI_VERSION`. Representative callable or assembly entry
symbols are none. Representative structs/unions/enums are none. Direct includes are none.

## Control Flow And Integration

used by Q40 boot protocol validation. Most headers in this subset contribute through compile-time
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

minimal but externally visible to Q40 bootloaders. Additional cross-cutting risks are conditional
compilation drift between MMU families, inline assembly constraints that differ between
68000/020/030/040/060/ColdFire, register-endianness mistakes on memory-mapped buses, and ABI changes
to exported bootinfo, ptrace, signal, stat, or syscall structures.

## Test Signals

Useful signals are m68k `defconfig`, allmodconfig where practical, and targeted builds for ColdFire
MMU, no-MMU, Sun3, Motorola MMU, Q40, Macintosh, Amiga, MVME, HP300 and virt configurations. Runtime
validation should cover boot to userspace, syscall tracing/seccomp, signal delivery and return,
fork/clone/vfork, module loading, DMA cache coherency tests, serial/early console output, interrupt
delivery, TLB flush stress, and userspace ABI checks for ptrace, stat, signal, cacheflush, and
bootinfo records.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/uapi/asm/bootinfo-q40.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/uapi/asm/bootinfo-virt.h -->
# sources/distributed-fs/ceph-client/arch/m68k/include/uapi/asm/bootinfo-virt.h

## Purpose

`bootinfo-virt.h` defines virt-machine bootinfo device base tags. It belongs to the m68k architecture support inside the ceph-client Linux source snapshot, so its behavior is architecture/kernel plumbing rather than Ceph protocol logic. Source read size: 21 lines and 645 bytes.

## Important APIs, Types, And Data

Primary surface: `BI_VIRT_GF_PIC_BASE`, RTC/TTY/virtio/control base tags, and `VIRT_BOOTI_VERSION`.
Representative preprocessor definitions seen in the file are `_UAPI_ASM_M68K_BOOTINFO_VIRT_H`,
`BI_VIRT_QEMU_VERSION`, `BI_VIRT_GF_PIC_BASE`, `BI_VIRT_GF_RTC_BASE`, `BI_VIRT_GF_TTY_BASE`,
`BI_VIRT_VIRTIO_BASE`, `BI_VIRT_CTRL_BASE`, `VIRT_BOOTI_VERSION`. Representative callable or
assembly entry symbols are none. Representative structs/unions/enums are none. Direct includes are
none.

## Control Flow And Integration

used by m68k virt emulator/booter and kernel setup. Most headers in this subset contribute through
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

device base tags must match emulator layout or early device registration fails. Additional cross-
cutting risks are conditional compilation drift between MMU families, inline assembly constraints
that differ between 68000/020/030/040/060/ColdFire, register-endianness mistakes on memory-mapped
buses, and ABI changes to exported bootinfo, ptrace, signal, stat, or syscall structures.

## Test Signals

Useful signals are m68k `defconfig`, allmodconfig where practical, and targeted builds for ColdFire
MMU, no-MMU, Sun3, Motorola MMU, Q40, Macintosh, Amiga, MVME, HP300 and virt configurations. Runtime
validation should cover boot to userspace, syscall tracing/seccomp, signal delivery and return,
fork/clone/vfork, module loading, DMA cache coherency tests, serial/early console output, interrupt
delivery, TLB flush stress, and userspace ABI checks for ptrace, stat, signal, cacheflush, and
bootinfo records.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/uapi/asm/bootinfo-virt.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/uapi/asm/bootinfo-vme.h -->
# sources/distributed-fs/ceph-client/arch/m68k/include/uapi/asm/bootinfo-vme.h

## Purpose

`bootinfo-vme.h` defines VME board bootinfo tags, board types, and board info struct. It belongs to the m68k architecture support inside the ceph-client Linux source snapshot, so its behavior is architecture/kernel plumbing rather than Ceph protocol logic. Source read size: 71 lines and 1794 bytes.

## Important APIs, Types, And Data

Primary surface: `BI_VME_TYPE`, `BI_VME_BRDINFO`, VME board type constants, bootinfo versions, and
board-info structure. Representative preprocessor definitions seen in the file are
`_UAPI_ASM_M68K_BOOTINFO_VME_H`, `BI_VME_TYPE`, `BI_VME_BRDINFO`, `VME_TYPE_TP34V`,
`VME_TYPE_MVME147`, `VME_TYPE_MVME162`, `VME_TYPE_MVME166`, `VME_TYPE_MVME167`, `VME_TYPE_MVME172`,
`VME_TYPE_MVME177`, `VME_TYPE_BVME4000`, `VME_TYPE_BVME6000`, `MVME147_BOOTI_VERSION`,
`MVME16x_BOOTI_VERSION`. Representative callable or assembly entry symbols are none. Representative
structs/unions/enums are none. Direct includes are `linux/types.h`.

## Control Flow And Integration

used by MVME/BVME bootloaders and platform setup. Most headers in this subset contribute through
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

board type constants select address maps and interrupt layouts. Additional cross-cutting risks are
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/uapi/asm/bootinfo-vme.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/uapi/asm/bootinfo.h -->
# sources/distributed-fs/ceph-client/arch/m68k/include/uapi/asm/bootinfo.h

## Purpose

`bootinfo.h` defines the common m68k bootinfo record format and machine/CPU/FPU/MMU IDs. It belongs to the m68k architecture support inside the ceph-client Linux source snapshot, so its behavior is architecture/kernel plumbing rather than Ceph protocol logic. Source read size: 184 lines and 5201 bytes.

## Important APIs, Types, And Data

Primary surface: `struct bi_record`, `struct mem_info`, `struct bootversion`, `BI_*` tags, `MACH_*`,
`CPUTYPE_*`, `FPUTYPE_*`, `MMUTYPE_*`, and `COMPAT_*` flags. Representative preprocessor definitions
seen in the file are `_UAPI_ASM_M68K_BOOTINFO_H`, `BI_LAST`, `BI_MACHTYPE`, `BI_CPUTYPE`,
`BI_FPUTYPE`, `BI_MMUTYPE`, `BI_MEMCHUNK`, `BI_RAMDISK`, `BI_COMMAND_LINE`, `BI_RNG_SEED`,
`MACH_AMIGA`, `MACH_ATARI`, `MACH_MAC`, `MACH_APOLLO`. Representative callable or assembly entry
symbols are none. Representative structs/unions/enums are `bi_record`, `mem_info`, `bootversion`.
Direct includes are `linux/types.h`.

## Control Flow And Integration

core ABI between m68k bootloaders and kernel setup, included by kernel and UAPI headers. Most
headers in this subset contribute through compile-time selection and inline helpers; the C and
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

record alignment, tag IDs, and memory chunk semantics are ABI-critical. Additional cross-cutting
risks are conditional compilation drift between MMU families, inline assembly constraints that
differ between 68000/020/030/040/060/ColdFire, register-endianness mistakes on memory-mapped buses,
and ABI changes to exported bootinfo, ptrace, signal, stat, or syscall structures.

## Test Signals

Useful signals are m68k `defconfig`, allmodconfig where practical, and targeted builds for ColdFire
MMU, no-MMU, Sun3, Motorola MMU, Q40, Macintosh, Amiga, MVME, HP300 and virt configurations. Runtime
validation should cover boot to userspace, syscall tracing/seccomp, signal delivery and return,
fork/clone/vfork, module loading, DMA cache coherency tests, serial/early console output, interrupt
delivery, TLB flush stress, and userspace ABI checks for ptrace, stat, signal, cacheflush, and
bootinfo records.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/uapi/asm/bootinfo.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/uapi/asm/byteorder.h -->
# sources/distributed-fs/ceph-client/arch/m68k/include/uapi/asm/byteorder.h

## Purpose

`byteorder.h` declares m68k as big-endian for UAPI. It belongs to the m68k architecture support inside the ceph-client Linux source snapshot, so its behavior is architecture/kernel plumbing rather than Ceph protocol logic. Source read size: 7 lines and 188 bytes.

## Important APIs, Types, And Data

Primary surface: `linux/byteorder/big_endian.h` include. Representative preprocessor definitions
seen in the file are `_M68K_BYTEORDER_H`. Representative callable or assembly entry symbols are
none. Representative structs/unions/enums are none. Direct includes are
`linux/byteorder/big_endian.h`.

## Control Flow And Integration

used by userspace and kernel headers needing endian annotations. Most headers in this subset
contribute through compile-time selection and inline helpers; the C and assembly files add runtime
entry points. Control reaches these definitions from generic Linux subsystems such as memory
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

minimal wrapper; changing it would break all ABI interpretation. Additional cross-cutting risks are
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/uapi/asm/byteorder.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/uapi/asm/cachectl.h -->
# sources/distributed-fs/ceph-client/arch/m68k/include/uapi/asm/cachectl.h

## Purpose

`cachectl.h` defines cacheflush syscall scope and cache selector constants. It belongs to the m68k architecture support inside the ceph-client Linux source snapshot, so its behavior is architecture/kernel plumbing rather than Ceph protocol logic. Source read size: 15 lines and 559 bytes.

## Important APIs, Types, And Data

Primary surface: `FLUSH_SCOPE_*` and `FLUSH_CACHE_*` values. Representative preprocessor definitions
seen in the file are `_M68K_CACHECTL_H`, `FLUSH_SCOPE_LINE`, `FLUSH_SCOPE_PAGE`, `FLUSH_SCOPE_ALL`,
`FLUSH_CACHE_DATA`, `FLUSH_CACHE_INSN`, `FLUSH_CACHE_BOTH`. Representative callable or assembly
entry symbols are none. Representative structs/unions/enums are none. Direct includes are none.

## Control Flow And Integration

used by the m68k `cacheflush` syscall ABI. Most headers in this subset contribute through compile-
time selection and inline helpers; the C and assembly files add runtime entry points. Control
reaches these definitions from generic Linux subsystems such as memory management, scheduler context
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

constants are UAPI; changing them breaks JITs and self-modifying userspace. Additional cross-cutting
risks are conditional compilation drift between MMU families, inline assembly constraints that
differ between 68000/020/030/040/060/ColdFire, register-endianness mistakes on memory-mapped buses,
and ABI changes to exported bootinfo, ptrace, signal, stat, or syscall structures.

## Test Signals

Useful signals are m68k `defconfig`, allmodconfig where practical, and targeted builds for ColdFire
MMU, no-MMU, Sun3, Motorola MMU, Q40, Macintosh, Amiga, MVME, HP300 and virt configurations. Runtime
validation should cover boot to userspace, syscall tracing/seccomp, signal delivery and return,
fork/clone/vfork, module loading, DMA cache coherency tests, serial/early console output, interrupt
delivery, TLB flush stress, and userspace ABI checks for ptrace, stat, signal, cacheflush, and
bootinfo records.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/uapi/asm/cachectl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/uapi/asm/fcntl.h -->
# sources/distributed-fs/ceph-client/arch/m68k/include/uapi/asm/fcntl.h

## Purpose

`fcntl.h` defines m68k-specific open flag values before generic fcntl. It belongs to the m68k architecture support inside the ceph-client Linux source snapshot, so its behavior is architecture/kernel plumbing rather than Ceph protocol logic. Source read size: 12 lines and 376 bytes.

## Important APIs, Types, And Data

Primary surface: `O_NOFOLLOW`, `O_DIRECT`, `O_LARGEFILE`. Representative preprocessor definitions
seen in the file are `_M68K_FCNTL_H`, `O_DIRECTORY`, `O_NOFOLLOW`, `O_DIRECT`, `O_LARGEFILE`.
Representative callable or assembly entry symbols are none. Representative structs/unions/enums are
none. Direct includes are `asm-generic/fcntl.h`.

## Control Flow And Integration

used by userspace headers and syscall ABI. Most headers in this subset contribute through compile-
time selection and inline helpers; the C and assembly files add runtime entry points. Control
reaches these definitions from generic Linux subsystems such as memory management, scheduler context
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

flag values must remain compatible with historical m68k Linux. Additional cross-cutting risks are
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/uapi/asm/fcntl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/uapi/asm/ioctls.h -->
# sources/distributed-fs/ceph-client/arch/m68k/include/uapi/asm/ioctls.h

## Purpose

`ioctls.h` selects generic ioctl numbers for m68k. It belongs to the m68k architecture support inside the ceph-client Linux source snapshot, so its behavior is architecture/kernel plumbing rather than Ceph protocol logic. Source read size: 9 lines and 220 bytes.

## Important APIs, Types, And Data

Primary surface: `asm-generic/ioctls.h` include. Representative preprocessor definitions seen in the
file are `__ARCH_M68K_IOCTLS_H__`, `FIOQSIZE`. Representative callable or assembly entry symbols are
none. Representative structs/unions/enums are none. Direct includes are `asm-generic/ioctls.h`.

## Control Flow And Integration

exported to userspace terminal/ioctl consumers. Most headers in this subset contribute through
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

minimal wrapper; ABI comes from generic header. Additional cross-cutting risks are conditional
compilation drift between MMU families, inline assembly constraints that differ between
68000/020/030/040/060/ColdFire, register-endianness mistakes on memory-mapped buses, and ABI changes
to exported bootinfo, ptrace, signal, stat, or syscall structures.

## Test Signals

Useful signals are m68k `defconfig`, allmodconfig where practical, and targeted builds for ColdFire
MMU, no-MMU, Sun3, Motorola MMU, Q40, Macintosh, Amiga, MVME, HP300 and virt configurations. Runtime
validation should cover boot to userspace, syscall tracing/seccomp, signal delivery and return,
fork/clone/vfork, module loading, DMA cache coherency tests, serial/early console output, interrupt
delivery, TLB flush stress, and userspace ABI checks for ptrace, stat, signal, cacheflush, and
bootinfo records.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/uapi/asm/ioctls.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/uapi/asm/param.h -->
# sources/distributed-fs/ceph-client/arch/m68k/include/uapi/asm/param.h

## Purpose

`param.h` defines m68k execution page size before generic params. It belongs to the m68k architecture support inside the ceph-client Linux source snapshot, so its behavior is architecture/kernel plumbing rather than Ceph protocol logic. Source read size: 13 lines and 254 bytes.

## Important APIs, Types, And Data

Primary surface: `EXEC_PAGESIZE` variants and generic param include. Representative preprocessor
definitions seen in the file are `_M68K_PARAM_H`, `EXEC_PAGESIZE`. Representative callable or
assembly entry symbols are none. Representative structs/unions/enums are none. Direct includes are
`asm-generic/param.h`.

## Control Flow And Integration

used by userspace and kernel ABI headers. Most headers in this subset contribute through compile-
time selection and inline helpers; the C and assembly files add runtime entry points. Control
reaches these definitions from generic Linux subsystems such as memory management, scheduler context
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

MMU and no-MMU execution page size can differ; loaders must see stable values. Additional cross-
cutting risks are conditional compilation drift between MMU families, inline assembly constraints
that differ between 68000/020/030/040/060/ColdFire, register-endianness mistakes on memory-mapped
buses, and ABI changes to exported bootinfo, ptrace, signal, stat, or syscall structures.

## Test Signals

Useful signals are m68k `defconfig`, allmodconfig where practical, and targeted builds for ColdFire
MMU, no-MMU, Sun3, Motorola MMU, Q40, Macintosh, Amiga, MVME, HP300 and virt configurations. Runtime
validation should cover boot to userspace, syscall tracing/seccomp, signal delivery and return,
fork/clone/vfork, module loading, DMA cache coherency tests, serial/early console output, interrupt
delivery, TLB flush stress, and userspace ABI checks for ptrace, stat, signal, cacheflush, and
bootinfo records.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/uapi/asm/param.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/uapi/asm/poll.h -->
# sources/distributed-fs/ceph-client/arch/m68k/include/uapi/asm/poll.h

## Purpose

`poll.h` defines m68k poll event compatibility value. It belongs to the m68k architecture support inside the ceph-client Linux source snapshot, so its behavior is architecture/kernel plumbing rather than Ceph protocol logic. Source read size: 10 lines and 197 bytes.

## Important APIs, Types, And Data

Primary surface: `POLLWRBAND` plus generic poll include. Representative preprocessor definitions
seen in the file are `__m68k_POLL_H`, `POLLWRNORM`, `POLLWRBAND`. Representative callable or
assembly entry symbols are none. Representative structs/unions/enums are none. Direct includes are
`asm-generic/poll.h`.

## Control Flow And Integration

used by userspace poll/select ABI. Most headers in this subset contribute through compile-time
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

numeric event bit must not collide with generic values. Additional cross-cutting risks are
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/uapi/asm/poll.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/uapi/asm/posix_types.h -->
# sources/distributed-fs/ceph-client/arch/m68k/include/uapi/asm/posix_types.h

## Purpose

`posix_types.h` overrides selected legacy POSIX type widths. It belongs to the m68k architecture support inside the ceph-client Linux source snapshot, so its behavior is architecture/kernel plumbing rather than Ceph protocol logic. Source read size: 26 lines and 733 bytes.

## Important APIs, Types, And Data

Primary surface: `__kernel_mode_t`, `__kernel_ipc_pid_t`, `__kernel_uid_t`, and `__kernel_old_dev_t`
before generic types. Representative preprocessor definitions seen in the file are
`__ARCH_M68K_POSIX_TYPES_H`, `__kernel_mode_t`, `__kernel_ipc_pid_t`, `__kernel_uid_t`,
`__kernel_old_dev_t`. Representative callable or assembly entry symbols are none. Representative
structs/unions/enums are none. Direct includes are `asm-generic/posix_types.h`.

## Control Flow And Integration

exported to libc and userspace ABI consumers. Most headers in this subset contribute through
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

type width changes are ABI-breaking for old syscalls and structs. Additional cross-cutting risks are
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/uapi/asm/posix_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/uapi/asm/ptrace.h -->
# sources/distributed-fs/ceph-client/arch/m68k/include/uapi/asm/ptrace.h

## Purpose

`ptrace.h` defines UAPI register offsets and ptrace request numbers. It belongs to the m68k architecture support inside the ceph-client Linux source snapshot, so its behavior is architecture/kernel plumbing rather than Ceph protocol logic. Source read size: 85 lines and 1916 bytes.

## Important APIs, Types, And Data

Primary surface: `PT_*` register indices, `PTRACE_GETREGS/SETREGS/GETFPREGS/SETFPREGS`, `struct
pt_regs`, and `struct switch_stack`. Representative preprocessor definitions seen in the file are
`_UAPI_M68K_PTRACE_H`, `PT_D1`, `PT_D2`, `PT_D3`, `PT_D4`, `PT_D5`, `PT_D6`, `PT_D7`, `PT_A0`,
`PT_A1`, `PT_A2`, `PT_A3`, `PT_A4`, `PT_A5`. Representative callable or assembly entry symbols are
none. Representative structs/unions/enums are `pt_regs`, `switch_stack`. Direct includes are none.

## Control Flow And Integration

used by ptrace, core dumps, debuggers, and kernel entry offsets. Most headers in this subset
contribute through compile-time selection and inline helpers; the C and assembly files add runtime
entry points. Control reaches these definitions from generic Linux subsystems such as memory
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

offsets mirror assembly save layout; any change breaks debuggers and syscall restart logic.
Additional cross-cutting risks are conditional compilation drift between MMU families, inline
assembly constraints that differ between 68000/020/030/040/060/ColdFire, register-endianness
mistakes on memory-mapped buses, and ABI changes to exported bootinfo, ptrace, signal, stat, or
syscall structures.

## Test Signals

Useful signals are m68k `defconfig`, allmodconfig where practical, and targeted builds for ColdFire
MMU, no-MMU, Sun3, Motorola MMU, Q40, Macintosh, Amiga, MVME, HP300 and virt configurations. Runtime
validation should cover boot to userspace, syscall tracing/seccomp, signal delivery and return,
fork/clone/vfork, module loading, DMA cache coherency tests, serial/early console output, interrupt
delivery, TLB flush stress, and userspace ABI checks for ptrace, stat, signal, cacheflush, and
bootinfo records.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/uapi/asm/ptrace.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/uapi/asm/setup.h -->
# sources/distributed-fs/ceph-client/arch/m68k/include/uapi/asm/setup.h

## Purpose

`setup.h` is the UAPI setup include guard for m68k. It belongs to the m68k architecture support inside the ceph-client Linux source snapshot, so its behavior is architecture/kernel plumbing rather than Ceph protocol logic. Source read size: 17 lines and 461 bytes.

## Important APIs, Types, And Data

Primary surface: no extra exported constants in this snapshot. Representative preprocessor
definitions seen in the file are `_UAPI_M68K_SETUP_H`, `COMMAND_LINE_SIZE`. Representative callable
or assembly entry symbols are none. Representative structs/unions/enums are none. Direct includes
are none.

## Control Flow And Integration

included by kernel-side setup wrappers and userspace headers. Most headers in this subset contribute
through compile-time selection and inline helpers; the C and assembly files add runtime entry
points. Control reaches these definitions from generic Linux subsystems such as memory management,
scheduler context switching, traps, syscall dispatch, DMA mapping, console setup, procfs, module
loading, or board-specific drivers.

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

placeholder must remain stable for include compatibility. Additional cross-cutting risks are
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/uapi/asm/setup.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/uapi/asm/sigcontext.h -->
# sources/distributed-fs/ceph-client/arch/m68k/include/uapi/asm/sigcontext.h

## Purpose

`sigcontext.h` defines m68k signal context saved to userspace. It belongs to the m68k architecture support inside the ceph-client Linux source snapshot, so its behavior is architecture/kernel plumbing rather than Ceph protocol logic. Source read size: 25 lines and 627 bytes.

## Important APIs, Types, And Data

Primary surface: `struct sigcontext` with status, PC, format/vector, mask, address, register and FPU
state fields. Representative preprocessor definitions seen in the file are `_ASM_M68k_SIGCONTEXT_H`.
Representative callable or assembly entry symbols are none. Representative structs/unions/enums are
`sigcontext`. Direct includes are none.

## Control Flow And Integration

used by signal delivery/return and libc signal trampolines. Most headers in this subset contribute
through compile-time selection and inline helpers; the C and assembly files add runtime entry
points. Control reaches these definitions from generic Linux subsystems such as memory management,
scheduler context switching, traps, syscall dispatch, DMA mapping, console setup, procfs, module
loading, or board-specific drivers.

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

field layout is user ABI and tied to `do_sigreturn()` parsing. Additional cross-cutting risks are
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/uapi/asm/sigcontext.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/uapi/asm/signal.h -->
# sources/distributed-fs/ceph-client/arch/m68k/include/uapi/asm/signal.h

## Purpose

`signal.h` defines m68k UAPI signal numbers, sigaction, sigaltstack, and siginfo placeholders. It belongs to the m68k architecture support inside the ceph-client Linux source snapshot, so its behavior is architecture/kernel plumbing rather than Ceph protocol logic. Source read size: 89 lines and 1794 bytes.

## Important APIs, Types, And Data

Primary surface: `NSIG`, signal number constants, `SA_*`, `MINSIGSTKSZ`, `SIGSTKSZ`, `struct
sigaction`, and `stack_t`. Representative preprocessor definitions seen in the file are
`_UAPI_M68K_SIGNAL_H`, `NSIG`, `SIGHUP`, `SIGINT`, `SIGQUIT`, `SIGILL`, `SIGTRAP`, `SIGABRT`,
`SIGIOT`, `SIGBUS`, `SIGFPE`, `SIGKILL`, `SIGUSR1`, `SIGSEGV`. Representative callable or assembly
entry symbols are none. Representative structs/unions/enums are `siginfo`, `sigaction`,
`sigaltstack`. Direct includes are `asm-generic/signal-defs.h`, `linux/types.h`.

## Control Flow And Integration

exported to libc and used by kernel signal code through wrappers. Most headers in this subset
contribute through compile-time selection and inline helpers; the C and assembly files add runtime
entry points. Control reaches these definitions from generic Linux subsystems such as memory
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

m68k has historical signal numbering and restorer behavior; ABI stability is mandatory. Additional
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/uapi/asm/signal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/uapi/asm/stat.h -->
# sources/distributed-fs/ceph-client/arch/m68k/include/uapi/asm/stat.h

## Purpose

`stat.h` defines legacy and modern m68k stat layouts. It belongs to the m68k architecture support inside the ceph-client Linux source snapshot, so its behavior is architecture/kernel plumbing rather than Ceph protocol logic. Source read size: 78 lines and 1685 bytes.

## Important APIs, Types, And Data

Primary surface: `struct __old_kernel_stat`, `struct stat`, `struct stat64`, and
`STAT64_HAS_BROKEN_ST_INO`. Representative preprocessor definitions seen in the file are
`_M68K_STAT_H`, `STAT64_HAS_BROKEN_ST_INO`. Representative callable or assembly entry symbols are
none. Representative structs/unions/enums are `__old_kernel_stat`, `stat`, `stat64`. Direct includes
are none.

## Control Flow And Integration

used by old/new stat syscalls and libc. Most headers in this subset contribute through compile-time
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

padding and broken inode compatibility are intentional ABI details. Additional cross-cutting risks
are conditional compilation drift between MMU families, inline assembly constraints that differ
between 68000/020/030/040/060/ColdFire, register-endianness mistakes on memory-mapped buses, and ABI
changes to exported bootinfo, ptrace, signal, stat, or syscall structures.

## Test Signals

Useful signals are m68k `defconfig`, allmodconfig where practical, and targeted builds for ColdFire
MMU, no-MMU, Sun3, Motorola MMU, Q40, Macintosh, Amiga, MVME, HP300 and virt configurations. Runtime
validation should cover boot to userspace, syscall tracing/seccomp, signal delivery and return,
fork/clone/vfork, module loading, DMA cache coherency tests, serial/early console output, interrupt
delivery, TLB flush stress, and userspace ABI checks for ptrace, stat, signal, cacheflush, and
bootinfo records.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/uapi/asm/stat.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/uapi/asm/swab.h -->
# sources/distributed-fs/ceph-client/arch/m68k/include/uapi/asm/swab.h

## Purpose

`swab.h` provides optional m68k byte-swap acceleration. It belongs to the m68k architecture support inside the ceph-client Linux source snapshot, so its behavior is architecture/kernel plumbing rather than Ceph protocol logic. Source read size: 28 lines and 665 bytes.

## Important APIs, Types, And Data

Primary surface: `__SWAB_64_THRU_32__` and `__arch_swab32()` using rotate/swap assembly when
suitable. Representative preprocessor definitions seen in the file are `_M68K_SWAB_H`,
`__SWAB_64_THRU_32__`, `__arch_swab32`. Representative callable or assembly entry symbols are
`__arch_swab32`. Representative structs/unions/enums are none. Direct includes are
`linux/compiler.h`, `linux/types.h`.

## Control Flow And Integration

used by generic byte-swap helpers in kernel and exported headers. Most headers in this subset
contribute through compile-time selection and inline helpers; the C and assembly files add runtime
entry points. Control reaches these definitions from generic Linux subsystems such as memory
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

inline assembly is compiler/CPU conditional; build both ColdFire and classic m68k cases. Additional
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/uapi/asm/swab.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/uapi/asm/ucontext.h -->
# sources/distributed-fs/ceph-client/arch/m68k/include/uapi/asm/ucontext.h

## Purpose

`ucontext.h` defines m68k userspace ucontext/mcontext structures. It belongs to the m68k architecture support inside the ceph-client Linux source snapshot, so its behavior is architecture/kernel plumbing rather than Ceph protocol logic. Source read size: 34 lines and 647 bytes.

## Important APIs, Types, And Data

Primary surface: `NGREG`, `MCONTEXT_VERSION`, `struct fpregset`, `struct mcontext`, and `struct
ucontext`. Representative preprocessor definitions seen in the file are `_M68K_UCONTEXT_H`, `NGREG`,
`MCONTEXT_VERSION`. Representative callable or assembly entry symbols are none. Representative
structs/unions/enums are `fpregset`, `mcontext`, `ucontext`. Direct includes are `asm/sigcontext.h`,
`asm/signal.h`.

## Control Flow And Integration

used by signal frames, libc `ucontext_t`, and checkpoint/debug tools. Most headers in this subset
contribute through compile-time selection and inline helpers; the C and assembly files add runtime
entry points. Control reaches these definitions from generic Linux subsystems such as memory
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

layout and version fields are user ABI. Additional cross-cutting risks are conditional compilation
drift between MMU families, inline assembly constraints that differ between
68000/020/030/040/060/ColdFire, register-endianness mistakes on memory-mapped buses, and ABI changes
to exported bootinfo, ptrace, signal, stat, or syscall structures.

## Test Signals

Useful signals are m68k `defconfig`, allmodconfig where practical, and targeted builds for ColdFire
MMU, no-MMU, Sun3, Motorola MMU, Q40, Macintosh, Amiga, MVME, HP300 and virt configurations. Runtime
validation should cover boot to userspace, syscall tracing/seccomp, signal delivery and return,
fork/clone/vfork, module loading, DMA cache coherency tests, serial/early console output, interrupt
delivery, TLB flush stress, and userspace ABI checks for ptrace, stat, signal, cacheflush, and
bootinfo records.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/uapi/asm/ucontext.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/uapi/asm/unistd.h -->
# sources/distributed-fs/ceph-client/arch/m68k/include/uapi/asm/unistd.h

## Purpose

`unistd.h` includes generated m68k syscall numbers for UAPI. It belongs to the m68k architecture support inside the ceph-client Linux source snapshot, so its behavior is architecture/kernel plumbing rather than Ceph protocol logic. Source read size: 7 lines and 196 bytes.

## Important APIs, Types, And Data

Primary surface: `asm/unistd_32.h` include. Representative preprocessor definitions seen in the file
are `_UAPI_ASM_M68K_UNISTD_H_`. Representative callable or assembly entry symbols are none.
Representative structs/unions/enums are none. Direct includes are `asm/unistd_32.h`.

## Control Flow And Integration

exported to libc and syscall consumers. Most headers in this subset contribute through compile-time
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

must be regenerated consistently with syscall tables. Additional cross-cutting risks are conditional
compilation drift between MMU families, inline assembly constraints that differ between
68000/020/030/040/060/ColdFire, register-endianness mistakes on memory-mapped buses, and ABI changes
to exported bootinfo, ptrace, signal, stat, or syscall structures.

## Test Signals

Useful signals are m68k `defconfig`, allmodconfig where practical, and targeted builds for ColdFire
MMU, no-MMU, Sun3, Motorola MMU, Q40, Macintosh, Amiga, MVME, HP300 and virt configurations. Runtime
validation should cover boot to userspace, syscall tracing/seccomp, signal delivery and return,
fork/clone/vfork, module loading, DMA cache coherency tests, serial/early console output, interrupt
delivery, TLB flush stress, and userspace ABI checks for ptrace, stat, signal, cacheflush, and
bootinfo records.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/uapi/asm/unistd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/install.sh -->
# sources/distributed-fs/ceph-client/arch/m68k/install.sh

## Purpose

`install.sh` installs a built m68k kernel image into the user-specified boot path. It belongs to the m68k architecture support inside the ceph-client Linux source snapshot, so its behavior is architecture/kernel plumbing rather than Ceph protocol logic. Source read size: 32 lines and 667 bytes.

## Important APIs, Types, And Data

Primary surface: shell logic for `INSTALLKERNEL`, default image path, `verify`, `ln -fs`, and
`sync`. Representative preprocessor definitions seen in the file are none. Representative callable
or assembly entry symbols are none. Representative structs/unions/enums are none. Direct includes
are none.

## Control Flow And Integration

called by `make install` style build flows for m68k. Most headers in this subset contribute through
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

script trusts positional arguments and destination paths; test with missing image, custom installer,
and unwritable boot directories. Additional cross-cutting risks are conditional compilation drift
between MMU families, inline assembly constraints that differ between
68000/020/030/040/060/ColdFire, register-endianness mistakes on memory-mapped buses, and ABI changes
to exported bootinfo, ptrace, signal, stat, or syscall structures.

## Test Signals

Useful signals are m68k `defconfig`, allmodconfig where practical, and targeted builds for ColdFire
MMU, no-MMU, Sun3, Motorola MMU, Q40, Macintosh, Amiga, MVME, HP300 and virt configurations. Runtime
validation should cover boot to userspace, syscall tracing/seccomp, signal delivery and return,
fork/clone/vfork, module loading, DMA cache coherency tests, serial/early console output, interrupt
delivery, TLB flush stress, and userspace ABI checks for ptrace, stat, signal, cacheflush, and
bootinfo records.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/install.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/kernel/Makefile -->
# sources/distributed-fs/ceph-client/arch/m68k/kernel/Makefile

## Purpose

`Makefile` selects m68k kernel objects for the architecture build. It belongs to the m68k architecture support inside the ceph-client Linux source snapshot, so its behavior is architecture/kernel plumbing rather than Ceph protocol logic. Source read size: 25 lines and 661 bytes.

## Important APIs, Types, And Data

Primary surface: core objects, config-specific `dma.o`, `ints.o`, `irq.o`, `module.o`, `pcibios.o`,
`sys_m68k.o`, `time.o`, setup variants, and linker-script generation. Representative preprocessor
definitions seen in the file are none. Representative callable or assembly entry symbols are none.
Representative structs/unions/enums are none. Direct includes are none.

## Control Flow And Integration

consumed by Kbuild when building `arch/m68k/kernel`. Most headers in this subset contribute through
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

object selection must match MMU/no-MMU, PCI, module, and machine configs. Additional cross-cutting
risks are conditional compilation drift between MMU families, inline assembly constraints that
differ between 68000/020/030/040/060/ColdFire, register-endianness mistakes on memory-mapped buses,
and ABI changes to exported bootinfo, ptrace, signal, stat, or syscall structures.

## Test Signals

Useful signals are m68k `defconfig`, allmodconfig where practical, and targeted builds for ColdFire
MMU, no-MMU, Sun3, Motorola MMU, Q40, Macintosh, Amiga, MVME, HP300 and virt configurations. Runtime
validation should cover boot to userspace, syscall tracing/seccomp, signal delivery and return,
fork/clone/vfork, module loading, DMA cache coherency tests, serial/early console output, interrupt
delivery, TLB flush stress, and userspace ABI checks for ptrace, stat, signal, cacheflush, and
bootinfo records.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/kernel/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/kernel/asm-offsets.c -->
# sources/distributed-fs/ceph-client/arch/m68k/kernel/asm-offsets.c

## Purpose

`asm-offsets.c` generates assembly offsets for m68k entry and low-level assembly. It belongs to the m68k architecture support inside the ceph-client Linux source snapshot, so its behavior is architecture/kernel plumbing rather than Ceph protocol logic. Source read size: 109 lines and 3966 bytes.

## Important APIs, Types, And Data

Primary surface: `DEFINE()`/`OFFSET()` output for task/thread_info/thread_struct, pt_regs,
switch_stack, signal frames, and optional Amiga font fields. Representative preprocessor definitions
seen in the file are `COMPILE_OFFSETS`, `ASM_OFFSETS_C`. Representative callable or assembly entry
symbols are `main`. Representative structs/unions/enums are none. Direct includes are
`asm/amigahw.h`, `asm/bootinfo.h`, `asm/irq.h`, `linux/font.h`, `linux/kbuild.h`,
`linux/kernel_stat.h`, `linux/sched.h`, `linux/stddef.h`.

## Control Flow And Integration

compiled by Kbuild to produce `asm-offsets.h` consumed by `entry.S` and other assembly. Most headers
in this subset contribute through compile-time selection and inline helpers; the C and assembly
files add runtime entry points. Control reaches these definitions from generic Linux subsystems such
as memory management, scheduler context switching, traps, syscall dispatch, DMA mapping, console
setup, procfs, module loading, or board-specific drivers.

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

offset drift breaks assembly register saves/restores; every struct layout change needs regenerated
offsets. Additional cross-cutting risks are conditional compilation drift between MMU families,
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/kernel/asm-offsets.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/kernel/bootinfo_proc.c -->
# sources/distributed-fs/ceph-client/arch/m68k/kernel/bootinfo_proc.c

## Purpose

`bootinfo_proc.c` exports saved m68k bootinfo records through procfs. It belongs to the m68k architecture support inside the ceph-client Linux source snapshot, so its behavior is architecture/kernel plumbing rather than Ceph protocol logic. Source read size: 79 lines and 1705 bytes.

## Important APIs, Types, And Data

Primary surface: `save_bootinfo()`, `bootinfo_read()`, and `init_bootinfo_procfs()`. Representative
preprocessor definitions seen in the file are none. Representative callable or assembly entry
symbols are `bootinfo_read`, `save_bootinfo`, `init_bootinfo_procfs`. Representative
structs/unions/enums are none. Direct includes are `asm/bootinfo.h`, `asm/byteorder.h`,
`linux/fs.h`, `linux/init.h`, `linux/printk.h`, `linux/proc_fs.h`, `linux/slab.h`, `linux/string.h`.

## Control Flow And Integration

copies bootinfo during setup and creates `/proc/bootinfo` for inspection. Most headers in this
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

state is a persistent kmemdup copy; parsing stops at `BI_LAST` and must handle allocation failure.
Additional cross-cutting risks are conditional compilation drift between MMU families, inline
assembly constraints that differ between 68000/020/030/040/060/ColdFire, register-endianness
mistakes on memory-mapped buses, and ABI changes to exported bootinfo, ptrace, signal, stat, or
syscall structures.

## Test Signals

Useful signals are m68k `defconfig`, allmodconfig where practical, and targeted builds for ColdFire
MMU, no-MMU, Sun3, Motorola MMU, Q40, Macintosh, Amiga, MVME, HP300 and virt configurations. Runtime
validation should cover boot to userspace, syscall tracing/seccomp, signal delivery and return,
fork/clone/vfork, module loading, DMA cache coherency tests, serial/early console output, interrupt
delivery, TLB flush stress, and userspace ABI checks for ptrace, stat, signal, cacheflush, and
bootinfo records.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/kernel/bootinfo_proc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/kernel/dma.c -->
# sources/distributed-fs/ceph-client/arch/m68k/kernel/dma.c

## Purpose

`dma.c` implements m68k DMA cache-coherency hooks. It belongs to the m68k architecture support inside the ceph-client Linux source snapshot, so its behavior is architecture/kernel plumbing rather than Ceph protocol logic. Source read size: 45 lines and 1040 bytes.

## Important APIs, Types, And Data

Primary surface: `arch_dma_prep_coherent()`, `pgprot_dmacoherent()`, and
`arch_sync_dma_for_device()`. Representative preprocessor definitions seen in the file are none.
Representative callable or assembly entry symbols are `arch_dma_prep_coherent`,
`arch_sync_dma_for_device`. Representative structs/unions/enums are none. Direct includes are
`asm/cacheflush.h`, `linux/dma-map-ops.h`, `linux/kernel.h`.

## Control Flow And Integration

called by generic DMA mapping code for coherent allocation and device sync. Most headers in this
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

cache maintenance depends on CPU cache mode and direction; missing flush/invalidate causes data
corruption. Additional cross-cutting risks are conditional compilation drift between MMU families,
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/kernel/dma.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/kernel/early_printk.c -->
# sources/distributed-fs/ceph-client/arch/m68k/kernel/early_printk.c

## Purpose

`early_printk.c` implements early debug console registration for selected m68k machines. It belongs to the m68k architecture support inside the ceph-client Linux source snapshot, so its behavior is architecture/kernel plumbing rather than Ceph protocol logic. Source read size: 56 lines and 1430 bytes.

## Important APIs, Types, And Data

Primary surface: `debug_cons_nputs()`, `setup_early_printk()`, console write callback, and
unregister helper. Representative preprocessor definitions seen in the file are none. Representative
callable or assembly entry symbols are `debug_cons_nputs`, `setup_early_printk`,
`unregister_early_console`. Representative structs/unions/enums are none. Direct includes are
`../mvme147/mvme147.h`, `../mvme16x/mvme16x.h`, `asm/setup.h`, `linux/console.h`, `linux/init.h`,
`linux/kernel.h`, `linux/string.h`.

## Control Flow And Integration

wired through early param handling and platform debug putchar routines for MVME147/MVME16x and
possibly others. Most headers in this subset contribute through compile-time selection and inline
helpers; the C and assembly files add runtime entry points. Control reaches these definitions from
generic Linux subsystems such as memory management, scheduler context switching, traps, syscall
dispatch, DMA mapping, console setup, procfs, module loading, or board-specific drivers.

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

early console must avoid normal console assumptions; stale registration after init can duplicate
output. Additional cross-cutting risks are conditional compilation drift between MMU families,
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/kernel/early_printk.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/kernel/entry.S -->
# sources/distributed-fs/ceph-client/arch/m68k/kernel/entry.S

## Purpose

`entry.S` contains m68k low-level syscall, trap, interrupt, signal-return, fork, and exception-return assembly. It belongs to the m68k architecture support inside the ceph-client Linux source snapshot, so its behavior is architecture/kernel plumbing rather than Ceph protocol logic. Source read size: 439 lines and 9921 bytes.

## Important APIs, Types, And Data

Primary surface: entry points `system_call`, `buserr`, `trap`, `ret_from_fork`, signal return
thunks, interrupt handlers, trace/seccomp hooks, and syscall-table dispatch. Representative
preprocessor definitions seen in the file are none. Representative callable or assembly entry
symbols are `system_call`, `sys_call_table`, `__sys_fork`, `bad_interrupt`, `auto_irqhandler_fixup`,
`user_irqvec_fixup`, `__sys_clone`, `__sys_vfork`, `__sys_clone3`, `sys_sigreturn`,
`sys_rt_sigreturn`, `buserr`, `trap`, `ret_from_fork`, `ret_from_kernel_thread`, `dbginterrupt`.
Representative structs/unions/enums are none. Direct includes are `asm/asm-offsets.h`,
`asm/entry.h`, `asm/errno.h`, `asm/setup.h`, `asm/traps.h`, `asm/unistd.h`, `linux/linkage.h`.

## Control Flow And Integration

central integration point between CPU exception frames, scheduler, syscall table, ptrace/seccomp,
signal handling, and C trap handlers. Most headers in this subset contribute through compile-time
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

assembly offsets, stack frame shape, interrupt state, and syscall restart semantics are high-risk;
failures usually boot-crash or corrupt userspace state. Additional cross-cutting risks are
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/kernel/entry.S -->
