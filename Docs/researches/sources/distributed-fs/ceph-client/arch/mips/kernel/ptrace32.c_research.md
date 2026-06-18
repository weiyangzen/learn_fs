# sources/distributed-fs/ceph-client/arch/mips/kernel/ptrace32.c

## Purpose
Implements compat ptrace handling for 32-bit tracers/tasks on 64-bit-capable MIPS configurations, including special 3264 memory peek/poke requests and 32-bit USER-area access.

## Important APIs, Types, and Functions
- `compat_arch_ptrace()` is the compat dispatcher.
- Handles `PTRACE_PEEKTEXT_3264`, `PTRACE_PEEKDATA_3264`, `PTRACE_POKETEXT_3264`, and `PTRACE_POKEDATA_3264` using a user-provided 64-bit target address pointer.
- Reuses native helpers for bulk GPR/FPR/watch register requests.
- Supports `PTRACE_GET_THREAD_AREA` and `PTRACE_GET_THREAD_AREA_3264`.

## Control Flow
The dispatcher narrows compat `addr`/`data`, then switches on request. The 3264 peek/poke cases first fetch the target process address from the tracer's user memory, then call `ptrace_access_vm()` with `FOLL_FORCE` and optional `FOLL_WRITE`. USER-area peek/poke mirrors native handling with 32-bit values, including FPU odd-register layout for 32-bit FP regs, DSP checks, PC/HI/LO writes, and syscall-number updates when r2 or indirect r4 changes. Unknown requests fall back to `compat_ptrace_request()`.

## State and Persistence
Mutates traced task pt_regs, FPU, DSP, and thread TLS/watch state. No persistent storage.

## Dependencies and Integration Points
Integrates with compat ptrace, native `ptrace_getregs/setregs`, `ptrace_getfpregs/setfpregs`, watch helpers from `ptrace.c`, FPU/DSP helpers, and MIPS syscall update helpers.

## Risks
Tracing mixed 32/64-bit processes is explicitly limited by comments. Pointer truncation/extension is the main risk: compat addresses must be cast carefully, while 3264 requests fetch a wider target address indirectly. Unlike native `ptrace_setfcr31()`, compat direct FCSR writes assign `fcr31` directly in some paths, so writable-bit masking differences are worth auditing. Partial VM access must return `-EIO`.

## Test Signals
32-bit `strace`/`gdb` on compat kernels should read/write GPRs, FPRs, DSP, watchpoints, TLS, and target memory. 3264 peek/poke should correctly access 64-bit target addresses supplied from compat user memory.
