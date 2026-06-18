## `sources/distributed-fs/ceph-client/arch/x86/hyperv/mshv_vtl_asm.S`

Purpose: implements the noinstr assembly context switch for returning from the current VTL to VTL0 through a Hyper-V static-call trampoline.

Important APIs and labels: `__mshv_vtl_return_call(struct mshv_vtl_cpu_context *vtl0)` is called by `hv_vtl.c`. It uses generated `MSHV_VTL_CPU_CONTEXT_*` offsets. A discard-addressable record keeps the static-call key symbol reachable.

Control flow: the function saves host callee-saved registers, loads guest/VTL0 registers from the context, restores guest CR2, pushes host `rax/rcx`, calls the configured `__mshv_vtl_return_hypercall`, then saves returned guest registers and CR2 back into the context before restoring host callee-saved registers and returning.

State and persistence: mutates the caller-provided `mshv_vtl_cpu_context`. Uses stack for temporary host register storage. Does not maintain global state itself; the static-call target is initialized by C.

Dependencies and integration points: `mshv-asm-offsets.h`, static call infrastructure, Hyper-V VTL return hypercall page offset, and C-side FPU save/restore around the call.

Risks: this runs in `.noinstr.text`, so instrumentation must not be introduced. Register clobber assumptions are strict: the VTL switch preserves only `rax/rcx` by contract, and CR2 handling protects fault state.

Test signals: VTL transitions preserve all saved registers and CR2, objtool/noinstr validation, and static-call target initialization before use.
