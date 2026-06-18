# sources/distributed-fs/ceph-client/arch/arm64/lib/error-inject.c

Purpose: supplies ARM64 function error-injection support by rewriting a kprobe-captured function entry context to return directly to the caller.

Important APIs/types/functions: `override_function_with_return`, `instruction_pointer_set`, `procedure_link_pointer`, and `NOKPROBE_SYMBOL`.

Control flow: when a kprobe captures a predefined injectable function on entry, this helper sets the saved instruction pointer to the procedure link pointer, so returning from the probe skips the probed function body and resumes at its caller.

State and persistence: mutates only the transient `pt_regs` exception frame. No persistent state.

Dependencies/integration: enabled by `CONFIG_FUNCTION_ERROR_INJECTION`; integrates with kprobes and Linux error-injection infrastructure.

Risks: only valid for contexts where the link pointer reflects the caller return address. Misuse on functions with unusual entry conventions or missing return-value setup can corrupt control flow.

Test signals: function error-injection selftests, kprobe entry-only invocation, return-value override tests, and `NOKPROBE_SYMBOL` recursion protection.
