# sources/distributed-fs/ceph-client/arch/alpha/kernel/ptrace.c

## Purpose
`ptrace.c` implements Alpha architecture ptrace support: register access, user memory peek/poke, software single-step through breakpoint patching, regset access, syscall trace entry/exit, audit integration, and seccomp enforcement.

## Important APIs, Types, And Functions
- `BREAKINST` is the Alpha breakpoint instruction `call_pal bpt`.
- `regoff[]` maps Alpha integer registers, floating registers, and PC to offsets in the task stack or `thread_info`.
- `get_reg_addr()`, `get_reg()`, and `put_reg()` read/write Alpha register slots, including special handling for user stack pointer (`r30`), UNIQUE (`65`), zero register, and FPCR/software IEEE state.
- `read_int()` and `write_int()` patch child text through `access_process_vm()`.
- `ptrace_set_bpt()` computes future execution addresses and writes breakpoint instructions for single-step.
- `ptrace_cancel_bpt()` restores saved instructions and clears pending breakpoint state.
- `user_enable_single_step()`, `user_disable_single_step()`, and `ptrace_disable()` integrate with generic ptrace stepping hooks.
- `arch_ptrace()` handles Alpha-specific peek/poke, register, and regset requests, delegating unknown requests to `ptrace_request()`.
- `syscall_trace_enter()` handles syscall-entry ptrace, seccomp, audit entry, syscall cancellation, and return-value setup.
- `syscall_trace_leave()` emits audit and ptrace syscall-exit notifications.

## Control Flow
Register peek/poke requests route through `arch_ptrace()`. Legacy `PTRACE_PEEKUSR/POKEUSR` access register numbers directly; `GETREGSET/SETREGSET` currently supports only `NT_PRSTATUS` and copies raw `pt_regs` to/from a user iovec, updating `iov_len`.

Single-step is software-based. `user_enable_single_step()` marks stepping with `bpt_nsaved = -1`; the signal path later calls `ptrace_set_bpt()`. That function reads the current instruction at PC, determines whether it is a branch, jump, or normal instruction, computes one or two possible next PCs, saves original instructions, and writes `BREAKINST` at those addresses. `ptrace_cancel_bpt()` restores those instructions before signal handling or detach.

Syscall entry reports to ptrace first; if tracing cancels the syscall, it sets syscall number to `-1` and may synthesize `-ENOSYS`. Seccomp runs after ptrace and follows the same cancellation convention. Audit entry runs only if the syscall remains valid.

## State And Persistence
Single-step state persists in `thread_info` fields `bpt_addr[]`, `bpt_insn[]`, and `bpt_nsaved` between ptrace operations and signal handling. Register writes mutate saved task stack frames and `thread_info` FPU/IEEE state. There is no persistent storage.

## Dependencies And Integration Points
This file depends on Alpha stack layout, `pt_regs`, `switch_stack`, FPU state helpers, Linux ptrace core, seccomp, audit, generic ptrace memory helpers, signal delivery (`signal.c` calls breakpoint helpers), and syscall register helpers from `asm/syscall.h`.

## Risks
- Breakpoint single-step writes into traced process memory; failures during partial installation can leave inconsistent state.
- Branch displacement and jump-target decoding must match Alpha instruction encoding.
- `GETREGSET/SETREGSET` copies raw `pt_regs`, not the legacy full register numbering including FP registers.
- `get_reg_addr()` returns a shared static `zero` for invalid/zero registers; writes to invalid registers silently write that temporary.
- Seccomp/ptrace ordering is intentional and sensitive to syscall cancellation semantics.

## Test Signals
- `strace` and `gdb` on Alpha for syscall tracing, register reads/writes, and single-step through branches and jumps.
- Ptrace tests for `PTRACE_GETREGSET/SETREGSET` with `NT_PRSTATUS`.
- Seccomp trace/errno actions combined with ptrace syscall cancellation.
- Signal delivery while single-stepping should restore old instructions and deliver `SIGTRAP`.
