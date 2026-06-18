# sources/distributed-fs/ceph-client/arch/x86/include/asm/vdso/sys_call.h

Purpose: Defines inline syscall macros for x86 vDSO fallback paths, abstracting 64-bit `syscall` and 32-bit fast-vsyscall/int80 selection.

Important APIs/types/functions: Internal macros define instruction, clobbers, syscall-number suffixing, and argument registers. `_VDSO_SYSCALL(name,suf32,...)` is the common inline asm body. `VDSO_SYSCALL0` through `VDSO_SYSCALL5` bind arguments to ABI registers and return the syscall result.

Control flow: vDSO fallback wrappers expand these macros. On x86-64, `syscall` is emitted with `rax` as both syscall number and return value and `rdi/rsi/rdx/r10/r8` for args. On 32-bit, an `ALTERNATIVE()` sequence chooses between padded `int $0x80` and `call __kernel_vsyscall` when `X86_FEATURE_SYSFAST32` is available.

State and persistence: No state. The macros cross into the kernel syscall path and return kernel results directly.

Dependencies and integration points: Uses `linux/compiler.h`, x86 CPU feature definitions, alternatives, syscall number macros, and vDSO time fallbacks.

Risks: Register binding is fragile, especially for 32-bit frame-pointer use; the header intentionally omits a 6-argument macro because `%ebp` needs special handling. Incorrect suffix use can call the wrong compat syscall.

Test signals: vDSO fallback tests for clock syscalls, 32-bit compat runs with and without SYSFAST32, objtool/build checks, and syscall ABI tests.
