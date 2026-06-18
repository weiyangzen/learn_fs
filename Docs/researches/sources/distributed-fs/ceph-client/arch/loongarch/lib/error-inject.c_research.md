# sources/distributed-fs/ceph-client/arch/loongarch/lib/error-inject.c

Purpose: implements the LoongArch architecture hook for function error injection by forcing a probed function to return immediately.

Important APIs, types, and functions: `override_function_with_return(struct pt_regs *regs)` sets the instruction pointer to `regs->regs[1]` (return address) and is marked `NOKPROBE_SYMBOL`.

Control flow: when invoked by the error-injection framework, it overwrites PC with RA so execution resumes at the caller.

State and persistence: mutates only the supplied pt_regs PC.

Dependencies and integration points: integrated with Linux error injection and kprobes; depends on LoongArch RA in GPR1 and generic `instruction_pointer_set()`.

Risks: incorrect RA convention would redirect control flow badly. Must not itself be probed to avoid recursion.

Test signals: function error injection selftests and kprobe blacklist validation.
