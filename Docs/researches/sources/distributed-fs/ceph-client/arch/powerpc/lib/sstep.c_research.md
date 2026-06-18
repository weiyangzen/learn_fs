<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/lib/sstep.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/lib/sstep.c

## Purpose
This file implements PowerPC instruction analysis and software single-step emulation for instructions that cannot simply be executed while tracing, probing, or recovering from faults. It decodes branches, barriers, integer compute operations, load/store forms, cache operations, privileged MSR moves, and optional FP/VMX/VSX/prefixed Power10 forms into `struct instruction_op`, then either updates `pt_regs` directly or performs the required memory/register transfer.

## Important APIs, types, and functions
Externally visible APIs are `analyse_instr`, `emulate_update_regs`, `emulate_loadstore`, `emulate_dcbz`, and `emulate_step`; `analyse_instr` is exported GPL. Important helpers include effective-address builders (`dform_ea`, `dsform_ea`, `dqform_ea`, `xform_ea`, `mlsd_8lsd_ea`), access wrappers (`read_mem`, `write_mem`, `copy_mem_in`, `copy_mem_out`), FP/VMX/VSX transfer helpers, and arithmetic helpers for CR/XER updates.

## Control flow
`analyse_instr` first handles branches, system calls, barriers, and privileged operations, then decodes compute opcodes, and finally maps load/store opcode forms to `MKOP` type/size/update flags. Return `1` means `emulate_update_regs` can finish by editing `pt_regs`; return `0` means a later execution path must perform memory, cache, or privileged state work; return `-1` indicates unsupported feature state such as VSX unavailable. `emulate_step` calls the decoder, dispatches load/store or cache/MSR cases, refuses system calls and RFI-like operations, and advances NIP by instruction length after success.

## State and persistence behavior
The file mutates only live task/register state: `pt_regs` GPRs, CR, XER, LR, CTR, NIP, return MSR, DAR on faults, thread FP/vector save areas, and the PPC32 `TIF_EMULATE_STACK_STORE` flag for unsafe kernel stack update emulation. It performs user/kernel memory accesses through uaccess helpers and exception tables, sets reservations for larx/stcx emulation, and may change cache/TLB-visible state through cache operations and `dcbz`.

## Dependencies and integration points
It depends on `asm/sstep.h` operation encodings, `asm/disassemble.h` prefixed instruction helpers, CPU feature flags, uaccess scoped access APIs, FPU/vector save/restore helpers from assembly files, quadword atomic helpers, cache primitives, kprobe `NOKPROBE_SYMBOL`, and architecture exception return helpers. Consumers include kprobes, uprobes, ptrace/single-step handling, and the local `test_emulate_step` self-test.

## Risks and edge cases
Risk concentrates in instruction decoding parity with ISA revisions, 32-bit truncation, cross-endian loads/stores, update forms with illegal `ra`/`rd` overlap, kernel-mode FP/VMX state access, Power10 prefixed immediate sign extension, and reservation semantics for conditional stores. The code intentionally refuses to step `sc`, `scv`, `rfi`, and MSR writes clearing RI. Any new opcode support needs matching feature gating and test coverage.

## Test signals
`test_emulate_step.c` validates representative load/store, prefixed, FP/vector/VSX, and compute instructions against expected memory/register results. Its compute lane compares emulator output with actual execution via `exec_instr`, while load/store checks observe PASS/SKIP/FAIL messages for architecture and config feature combinations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/lib/sstep.c -->
