# sources/distributed-fs/ceph-client/arch/powerpc/platforms/pseries/hvCall.S

Purpose: Provides low-level pseries hypervisor call wrappers in assembly for no-return-buffer, 4-return, 9-return, raw real-mode-capable, and tracepoint-instrumented hcalls.

Important APIs/types/functions: Defines `plpar_hcall_norets_notrace`, `plpar_hcall_norets`, `plpar_hcall`, `plpar_hcall_raw`, `plpar_hcall9`, and `plpar_hcall9_raw`. Trace support uses `HCALL_INST_PRECALL`, `HCALL_INST_POSTCALL_NORETS`, `HCALL_INST_POSTCALL`, `HCALL_BRANCH`, `hcall_tracepoint_refcount`, and static branch/jump-label integration.

Control flow: Each wrapper saves condition register state, arranges arguments into the ABI registers expected by `HVSC`, invokes the hypervisor, stores return registers into the caller-supplied buffer where applicable, clears `PACASRR_VALID`, restores condition register state, and returns the hcall status in r3. Trace variants snapshot arguments, call `__trace_hcall_entry`, perform the hcall, store returns, call `__trace_hcall_exit`, and restore LR/stack.

State and persistence: The assembly mutates caller return buffers, PACA SRR-valid state, tracepoint refcount/static branch state, and volatile registers according to the PowerPC ABI. Raw variants intentionally avoid per-CPU/stat memory so they can be used in real mode.

Dependencies and integration points: Depends on PowerPC assembly ABI, `HVSC`, PACA offsets, stack parameter offsets, tracepoint C hooks, jump labels, feature fixups, and many pseries callers using `plpar_*` wrappers.

Risks: Register save/restore and stack layout are correctness-critical. Trace instrumentation must preserve all hcall arguments and return values. Raw wrappers must remain safe for real-mode kexec/kdump contexts. Clearing `PACASRR_VALID` must happen after every hypervisor call path.

Test signals: Hcall-heavy boot, tracepoint enable/disable, hcall return-buffer correctness for 4- and 9-return calls, kdump/kexec raw hcalls in real mode, objdump review after asm-offset changes, and lockdep/tracing recursion checks are relevant.

Source read size: 370 lines, 6975 bytes.
