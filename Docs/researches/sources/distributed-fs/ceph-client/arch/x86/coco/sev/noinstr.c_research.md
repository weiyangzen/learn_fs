# sources/distributed-fs/ceph-client/arch/x86/coco/sev/noinstr.c

## Purpose
Noinstr-safe low-level support for SEV-ES #VC handling. It protects the #VC IST stack during NMI nesting, notifies the hypervisor when NMI handling is complete, and arbitrates per-CPU GHCB ownership without instrumentation.

## Important APIs, Types, And Functions
`__sev_es_ist_enter()` and `__sev_es_ist_exit()` adjust and restore the VC IST entry when NMI hits an active #VC stack. `__sev_es_nmi_complete()` sends `SVM_VMGEXIT_NMI_COMPLETE`. `__sev_get_ghcb()` returns the active GHCB and optionally saves current contents into `backup_ghcb`; `__sev_put_ghcb()` restores or invalidates it. `on_vc_stack()` identifies kernel-mode stack frames in the VC IST range.

## Control Flow And State
The GHCB acquisition path requires interrupts disabled. Before runtime GHCB initialization it returns `boot_ghcb`. After initialization it marks the per-CPU GHCB active. If a nested #VC occurs, the original GHCB content is copied to `backup_ghcb` and later restored. A second nested use with both GHCBs active panics after clearing flags to preserve panic output ability. IST enter always stores the old IST below the new top so exit can unroll unconditionally.

## Dependencies And Integration
Depends on TSS/IST layout, per-CPU `runtime_data`, GHCB invalidation helpers, VMGEXIT, native physical-address macros safe for noinstr paths, and NMI entry code. Runtime #VC handlers in `vc-handle.c` and core GHCB setup rely on these functions.

## Risks And Test Signals
Risks are recursive instrumentation, stack overwrite under NMI/#VC nesting, invalid GHCB reuse, and incorrect interrupt-state assumptions. Signals include objtool/noinstr validation, SEV-ES boot under tracing-disabled paths, NMI storm tests, nested #VC cases such as NMI over MMIO/MSR emulation, and panic-path output when GHCB backup exhaustion is forced.
