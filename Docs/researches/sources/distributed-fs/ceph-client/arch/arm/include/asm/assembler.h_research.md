<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/assembler.h -->
# sources/distributed-fs/ceph-client/arch/arm/include/asm/assembler.h

## Purpose
Central ARM assembly macro header for low-level kernel code. It provides endian helpers, interrupt control, tracing hooks, SMP alternatives, current-task/per-CPU access, user access exception table helpers, branch/return helpers, bug annotations, and long-address load/store macros.

## Important APIs/types/functions
- Byte/endian macros: `lspull`, `lspush`, `get_byte_*`, `put_byte_*`, `ARM_BE8`.
- Barriers and IRQ macros: `disable_irq_notrace`, `enable_irq_notrace`, `dsb`, `isb`, `asm_trace_hardirqs_*`, `save_and_disable_irqs`, `restore_irqs`.
- Address/control helpers: `badr*`, `get_thread_info`, `set_current`, `get_current`, `reload_current`, `this_cpu_offset`, `ldr_this_cpu`.
- SMP alternatives: `ALT_SMP`, `ALT_UP`, `ALT_UP_B`.
- User access helpers: `USERL`, `USER`, `usracc`, `strusr`, `ldrusr`.
- Utility macros: `safe_svcmode_maskall`, `setmode`, `string`, `ret*`, `bug`, `_ASM_NOKPROBE`, `mov_l`, `adr_l`, `ldr_l`, `str_l`, `ldr_va`, `str_va`, `rev_l`, and `bl_r`.

## Control flow
The header is included only from assembly and emits instruction sequences conditionally based on architecture level, ARM/Thumb2 mode, SMP, tracing, endian mode, V7M, CPUv6, module PLT support, and relocation capabilities. Many macros create local labels, exception-table entries, or alternative instruction sections.

## State and persistence behavior
No runtime variables are defined here, but emitted macros mutate CPU state: CPSR/PRIMASK, current task TLS registers, per-CPU address registers, barriers, exception tables, bug tables, and kprobe blacklist sections. These generated sections persist in object files.

## Dependencies and integration points
Depends on ARM assembler syntax, `asm/ptrace.h`, `asm/opcodes-virt.h`, generated asm offsets, page/table/thread info headers, and uaccess assembly helpers. Used throughout ARM entry, exception, MMU, copy, crypto, and power-management assembly.

## Risks and edge cases
Macros must assemble to exact sizes for SMP alternatives, especially Thumb2 `ALT_UP()`. Incorrect CPSR/mode manipulation can break boot or exception return. User access macros must create correct exception table entries. Long-address macros vary by architecture and module relocation support; wrong assumptions cause relocation or literal-range failures.

## Test signals
Full ARM builds in ARM and Thumb2 modes, SMP and UP, V7M and classic ARM, big/little endian, modules, kprobes, lockdep IRQ tracing, and boot/exception/uaccess tests all exercise this header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/assembler.h -->
