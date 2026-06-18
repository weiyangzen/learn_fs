# sources/distributed-fs/ceph-client/arch/x86/kernel/kprobes/common.h

Purpose: Shared x86 kprobes/optprobes header that defines assembly register save/restore templates and declares cross-file helpers for instruction recovery, copying, relative branch synthesis, and optimized probe detours.

Important APIs/types/functions: defines `SAVE_REGS_STRING` and `RESTORE_REGS_STRING` for x86_64 and x86_32. Declares `can_boost()`, `recover_probed_instruction()`, `__copy_instruction()`, `synthesize_reljump()`, `synthesize_relcall()`, `setup_detour_execution()`, and `__recover_optprobed_insn()`. Provides no-op inline fallbacks for optprobe helpers when `CONFIG_OPTPROBES` is disabled.

Control flow: the header itself has no runtime flow. Its strings are embedded by `opt.c` in the optprobe trampoline template. Its declarations allow `core.c`, `opt.c`, and `ftrace.c` to share instruction manipulation logic without exposing it outside the x86 kprobes directory.

State and persistence: no state is stored here. It codifies the exact `pt_regs` stack layout expected by optprobe trampoline code, including skipped slots for `cs`, `ip`, `orig_ax`, and segment registers.

Dependencies and integration points: depends on x86 assembly/frame macros and the x86 instruction decoder type `struct insn`. It is tightly integrated with `struct pt_regs` layout and with `core.c` and `opt.c` implementations.

Risks: register push/pop order is an ABI between inline assembly and C handlers. Any `pt_regs` layout change, 32-bit segment handling change, or frame-pointer encoding change must update these strings. Incorrect fallback behavior under `!CONFIG_OPTPROBES` would affect normal kprobe single-step flow.

Test signals: compile both 32-bit and 64-bit configurations with and without optprobes. Runtime optprobe tests should verify saved registers, flags, stack pointer, and segment fields delivered to pre-handlers match int3-based kprobes.
