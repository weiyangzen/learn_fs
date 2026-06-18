# sources/distributed-fs/ceph-client/arch/x86/lib/error-inject.c

Purpose: supplies a tiny architecture hook for function error injection by redirecting execution to an immediate-return stub.

Important APIs/functions: defines assembly symbol `just_return_func` and C function `override_function_with_return(struct pt_regs *regs)`. Marks the override helper with `NOKPROBE_SYMBOL`.

Control flow: `just_return_func` contains an annotated no-ENDBR function entry and `ASM_RET`. `override_function_with_return()` sets `regs->ip` to the stub address, causing the probed/injected function to return immediately when execution resumes.

State and persistence behavior: no persistent state. Mutates the instruction pointer in the supplied register frame.

Dependencies/integration points: built with `CONFIG_FUNCTION_ERROR_INJECTION`; integrates with kprobes, Linux error-injection infrastructure, objtool annotations, and x86 return/IBT annotations.

Risks: redirecting IP must preserve calling-convention assumptions for injected sites. The helper must not itself be probed. IBT/ENDBR annotations must match kernel control-flow enforcement expectations.

Test signals: function error-injection selftests, kprobe exclusion validation, objtool/IBT builds, and tests that injected functions return without executing body side effects.
