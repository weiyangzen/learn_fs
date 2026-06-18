# sources/distributed-fs/ceph-client/arch/arm/lib/error-inject.c

Purpose: supports function error injection by redirecting execution to the caller return address. `override_function_with_return` sets the saved instruction pointer to `regs->ARM_lr`.

Control flow is invoked by kprobe/error-injection infrastructure for an intercepted function; it mutates pt_regs so execution returns immediately. There is no persistent state. Dependencies are `linux/error-injection.h`, kprobes, ARM pt_regs layout, and `instruction_pointer_set`. Risks are using it on functions where LR is not a valid return address or where skipped side effects are unsafe. Test signals include CONFIG_FUNCTION_ERROR_INJECTION tests and kprobe-based override behavior.
