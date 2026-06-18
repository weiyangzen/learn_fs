# sources/distributed-fs/ceph-client/arch/x86/kernel/uprobes.c

Purpose: supplies the x86 architecture backend for uprobes and uretprobes: instruction validation, out-of-line execution fixups, optimized trampoline calls, syscall trampolines, breakpoint/debug exception integration, and return-address hijacking.

Important APIs/functions: `arch_uprobe_analyze_insn()`, `arch_uprobe_pre_xol()`, `arch_uprobe_post_xol()`, `arch_uprobe_abort_xol()`, `arch_uprobe_skip_sstep()`, `arch_uprobe_exception_notify()`, `set_swbp()`, `set_orig_insn()`, `arch_uprobe_optimize()`, `arch_uretprobe_trampoline()`, `arch_uretprobe_hijack_return_addr()`, `arch_uretprobe_is_alive()`, `is_uprobe_at_func_entry()`, and the x86-64 `uprobe`/`uretprobe` syscalls.

Control flow: analysis decodes the copied instruction, rejects unsafe prefixes and exception-masking instructions, checks opcode allow tables, records branch/push/default XOL operations, rewrites RIP-relative memory addressing through a scratch register when needed, and marks eligible 5-byte NOP probes optimizable. Normal probe execution installs an INT3, redirects IP to the XOL slot, sets TF, then post-fixes IP, return addresses, scratch registers, and TF state. Optimized probes patch a CALL to a per-mm special trampoline mapped near the probed address; the trampoline enters `sys_uprobe`, restores user register context, invokes generic uprobe handling, and returns through sysret/iret-safe state. Uretprobes use either a native syscall trampoline or breakpoint fallback and can update shadow stack state.

State and persistence: per-instruction state is stored in `struct arch_uprobe` flags, copied instruction bytes, fixups, branch/push parameters, and ops pointer. Per-task XOL state uses `current->utask->autask` for saved TF, trap number, and scratch registers. Per-mm state stores an hlist of trampoline mappings; trampoline pages persist until mm teardown, while the special VMA is intentionally not unmapped during individual trampoline destruction.

Dependencies and integration: depends on x86 instruction decoder/evaluator, generic uprobes core, user access, mm special mappings, page access helpers, text-poke synchronization, shadow stack helpers, syscall entry semantics, die notifiers for INT3/DEBUG, and Kconfig-controlled 32-bit compatibility.

Risks: instruction classification is conservative but hard to keep complete. Wrong RIP-relative rewrite or stack/IP fixup can corrupt user execution. Multi-byte optimization relies on INT3 synchronization and verification callbacks. Trampoline reachability must stay within CALL rel32 range, and shadow-stack handling must match normal return semantics.

Test signals: uprobe selftests for single-step and optimized probes, branch/call/push instructions, RIP-relative loads/stores, native and compat tasks, uretprobe return hijacking, shadow stack enabled tasks, concurrent probe install/remove, and invalid opcode/prefix rejection.
