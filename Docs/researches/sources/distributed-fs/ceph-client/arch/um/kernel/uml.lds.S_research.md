# sources/distributed-fs/ceph-client/arch/um/kernel/uml.lds.S

## Purpose
Static UML linker script defining executable layout, section order, symbols, and discard/debug handling.

## Important APIs, Types, and Functions
Sets ELF output format/architecture and entry `_start`, aliases `jiffies = jiffies_64`, hides symbols by default with a version script, defines `__binary_start`, `_text`, `_stext`, `__syscall_stub_start/end`, `__init_begin/end`, data/bss boundaries, and standard debug/modinfo/discard sections.

## Control Flow, State, and Persistence
No runtime flow; layout decisions persist in the linked kernel image. The `.syscall_stub` section is page-aligned after `.text` so stub code can be mapped/copied precisely.

## Dependencies and Integration Points
Includes kernel linker fragments such as `asm/common.lds.S`, relies on `START`, `PAGE_SIZE`, `ELF_FORMAT`, and UML section macros. Consumed by `vmlinux.lds.S` for static links.

## Risks and Test Signals
Risks include wrong stub section bounds, glibc relocation symbol omissions, discarded init/runtime sections, or symbol visibility surprises. Test static UML links, boot, syscall stub mapping, kallsyms, and module/debug section generation.
