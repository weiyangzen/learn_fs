<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/openrisc/kernel/vmlinux.lds.S -->
# sources/distributed-fs/ceph-client/arch/openrisc/kernel/vmlinux.lds.S

## Purpose
Defines the OpenRISC kernel link layout, output format, section order, and key linker symbols.

## Important APIs, Types, And Functions
Sets `LOAD_OFFSET`/`LOAD_BASE` to `PAGE_OFFSET`, chooses `elf32-or1k` or `elf32-or32`, defines `jiffies`, and lays out `_text`, `_stext`, `_etext`, `_s_kernel_ro`, `_e_kernel_ro`, `_sdata`, `_edata`, `__init_begin`, `__init_end`, BSS, `_end`, exception table, percpu, debug, modinfo, and discarded sections.

## Control Flow
The linker script has declarative build-time flow. Runtime code depends on section boundaries for memory reservation, RO mapping, and initial mm setup.

## State And Persistence
Determines the persistent in-memory kernel image layout.

## Dependencies And Integration Points
Uses generic vmlinux linker macros and OpenRISC page/cache/thread constants. Consumed by `setup.c`, `mm/init.c`, exception tables, and module/debug tooling.

## Risks
Alignment controls page permissions; wrong `_s_kernel_ro`/`_e_kernel_ro` boundaries can leave text writable or data read-only. Output-format mismatch breaks boot loaders and tools.

## Test Signals
Link success, section boundary inspection, RO text after paging init, exception table fixups, and boot on both OR1K output-format configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/openrisc/kernel/vmlinux.lds.S -->
