# sources/distributed-fs/ceph-client/arch/powerpc/kernel/static_call.c

## Purpose
Implements PowerPC runtime patching for Linux static calls, converting call sites and trampolines between NOP/return, direct branches, and long trampoline dispatch.

## Important APIs, Types, and Functions
- `arch_static_call_transform(site, tramp, func, tail)` is the exported architecture hook.
- Uses `patch_instruction()`, `patch_branch()`, `patch_ulong()`, `text_mutex`, `PPC_SCT_RET0`, and `PPC_SCT_DATA`.

## Control Flow and State
The function serializes on `text_mutex`, classifies the requested target as NULL, `__static_call_return0`, short branch range, or trampoline-backed long target, then patches either a call site, tail-call site, or trampoline. For long trampoline targets it stores the real function pointer in trampoline data before patching trampoline code.

## State and Persistence Behavior
Persists changes directly in kernel text/trampoline memory. Failures panic because static-call text patching must not leave inconsistent executable code.

## Dependencies and Integration Points
Integrates with generic `static_call` infrastructure and PowerPC text patching. Branch range checks must match instruction encoding limits.

## Risks
Wrong branch-range decisions or partial patch failure can redirect kernel execution. Concurrency is protected by `text_mutex`, but callers rely on instruction patching to handle cache coherency.

## Test Signals
Boot with static calls enabled, toggle static keys using return0 and NULL targets, test long out-of-range call targets, and run under ftrace/livepatch text-patching stress.
