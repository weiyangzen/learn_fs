# sources/distributed-fs/ceph-client/arch/powerpc/kernel/rethook.c

## Purpose
This file implements the PowerPC architecture hooks for generic `rethook`, using a kprobe on a return trampoline.

## Important APIs, Types, And Functions
It defines the assembly symbol `arch_rethook_trampoline`, exports `arch_rethook_prepare()`, `arch_rethook_fixup_return()`, and `arch_init_kprobes()`, and registers a `struct kprobe trampoline_p` with `trampoline_rethook_handler()`.

## Control Flow
`arch_rethook_prepare()` records the original link register and stack frame in the rethook node, then replaces the function return address with the trampoline address. When the trampoline is reached, the kprobe pre-handler calls `rethook_trampoline_handler(regs, regs->gpr[1])`. During fixup, `arch_rethook_fixup_return()` sets `nip` to `orig_ret_address - 4` for trap/kprobe emulation and sets `link` to the original return address for optimized probe paths.

## State And Persistence
Per-return state is stored in `struct rethook_node` (`ret_addr`, `frame`) and temporary `pt_regs` modifications. The registered kprobe persists after `arch_init_kprobes()`.

## Dependencies And Integration Points
It depends on generic kprobes and rethook frameworks. `NOKPROBE_SYMBOL` annotations prevent recursive instrumentation of the handler and arch hooks.

## Risks
Return-address fixup is path-sensitive: trap-based kprobes use `nip`, optimized probes use `link`. An off-by-one-instruction mistake would resume at the wrong address. The implementation assumes `gpr[1]` is the stack pointer frame key.

## Test Signals
Kretprobe/rethook tests should verify normal returns, optimized probes, nested hooks, stack-frame matching, and that instrumentation recursion does not occur.
