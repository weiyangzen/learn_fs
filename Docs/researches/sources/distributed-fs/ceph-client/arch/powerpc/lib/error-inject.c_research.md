# sources/distributed-fs/ceph-client/arch/powerpc/lib/error-inject.c

This small file implements the PowerPC hook for function error injection. It exports `override_function_with_return(struct pt_regs *regs)` for the generic error-injection/kprobe machinery. The function emulates a `blr` at the probed function entry by setting the return instruction pointer from the link register saved in `regs`.

Control flow is intentionally single-step: a kprobe captures registers at entry of an allowlisted function, error-injection core arranges the desired return value elsewhere, then this helper redirects execution to the caller by calling `regs_set_return_ip(regs, regs->link)`. The comment notes that 32-bit userspace on a 64-bit kernel is not relevant for this kernel/module function-entry context. The symbol is marked `NOKPROBE_SYMBOL` to avoid probing the override hook itself.

There is no persistent state. Dependencies include kprobes, `pt_regs`, and the PowerPC calling convention where LR is the return address. Integration points are `CONFIG_FUNCTION_ERROR_INJECTION`, kernel fault-injection tests, and kprobe-based override paths. Risks are corrupting control flow if used for functions whose entry state or ABI is not compatible, or if LR is not the intended return target. Test signals include function error-injection selftests and kprobe blacklist validation.
