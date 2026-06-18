# sources/distributed-fs/ceph-client/arch/arm64/kernel/ftrace.c

Purpose: Provides arm64 dynamic ftrace text patching, callsite address adjustment, module PLT fallback, call-ops literal management, and function graph return rewriting.

Important APIs and state: main functions are `ftrace_call_adjust()`, `arch_ftrace_get_symaddr()`, `ftrace_make_call()`, `ftrace_make_nop()`, `ftrace_modify_call()`, `ftrace_init_nop()`, `arch_ftrace_update_code()`, `prepare_ftrace_return()`, `ftrace_graph_func()`, and graph caller enable/disable helpers. With dynamic call ops, each callsite stores an `ftrace_ops` literal near the patch site and updates it via `aarch64_insn_write_literal_u64()`.

Control flow: ftrace normalizes compiler patchable-entry locations, accounting for pre-function NOPs and optional BTI. Enabling tracing writes a per-site ops literal, finds a branch target reachable by `BL`, uses module ftrace PLTs if necessary, then validates and patches a NOP into a branch. Disabling reverses the branch to NOP. Graph tracing replaces the saved LR with `return_to_handler` after `function_graph_enter*()` accepts the call.

Dependencies and integration: depends on `asm/insn.h`, `asm/text-patching.h`, module PLT allocation, `entry-ftrace.S` symbols, BTI configuration, and ftrace core locking. Module integration uses `get_ftrace_plt()` for core and init text trampoline slots.

Risks and test signals: primary risks are wrong patch-site adjustment with BTI/call-ops, out-of-range module branch without PLT, stale ops literals, and validating against the wrong old instruction. Test with dynamic ftrace enable/disable, function graph tracer, direct trampolines, modules loaded far from core text, BTI kernels, and tracing selftests.
