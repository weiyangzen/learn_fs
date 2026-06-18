<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/sections.h -->
# sources/distributed-fs/ceph-client/arch/riscv/include/asm/sections.h

Purpose: Declares RISC-V linker section symbols and text-address classification helpers.

Important APIs/types/functions: Exports `_start`, `_start_kernel`, init/exit/alternative section bounds, `is_va_kernel_text()`, and `is_va_kernel_lm_alias_text()`.

Control flow: Inline helpers compare virtual addresses against linker-symbol ranges for kernel text and linear-map aliases.

State and persistence: State is linker-defined section boundaries rather than mutable data.

Dependencies and integration points: Used by alternatives, ftrace/kprobes, text patching, memory permissions, and address sanitization helpers.

Risks: Incorrect bounds can permit patching/nonpatching wrong memory or misclassify kernel text aliases.

Test signals: Boot/link tests, kallsyms/ftrace/kprobe tests, module/text permission transitions, and vmlinux linker script changes.

Source read size: 34 lines, 883 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/sections.h -->
