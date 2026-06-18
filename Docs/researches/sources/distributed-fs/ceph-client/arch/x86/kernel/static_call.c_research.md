# sources/distributed-fs/ceph-client/arch/x86/kernel/static_call.c

## Purpose
`static_call.c` implements x86 text transformations for static-call sites and trampolines, patching instructions between calls, NOPs, jumps, returns, and conditional branches while respecting return thunk policy.

## Important APIs, Types, And Functions
Public hooks are `arch_static_call_transform()`, `__static_call_update_early()`, and `__static_call_fixup()` when rethunk mitigation is enabled. Internals include `enum insn_type`, `__static_call_transform()`, `__static_call_validate()`, `__sc_insn()`, `__is_Jcc()`, `tramp_ud`, `xor5rax`, `retinsn`, and `warninsn`.

## Control Flow
Validation confirms trampoline signatures and expected opcodes. Transform maps non-null calls to `CALL`, null calls to NOP, tail calls to `JMP`, null tail calls to `RET` or rethunk jump, and conditional trampolines to Jcc. Boot/module-init patching uses early text poke; runtime patching uses `smp_text_poke_single()` under `text_mutex`.

## State, Persistence, Dependencies, Integration
Persistent state is modified kernel text. Dependencies include text-patching helpers, `text_mutex`, callthunk translation, rethunk policy, and static-call core state. `traps.c` recognizes related UD1/WARN encodings, and rethunk alternatives call fixup after mitigation selection.

## Risks And Test Signals
Instruction size, branch target, trampoline signature, and runtime patch synchronization errors are fatal. Test early boot, module init, runtime updates, null/non-null calls, tail and conditional tail calls, return0 and WARN trap optimizations, rethunk on/off, and objtool validation.
