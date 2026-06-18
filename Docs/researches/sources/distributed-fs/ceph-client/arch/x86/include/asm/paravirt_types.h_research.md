# sources/distributed-fs/ceph-client/arch/x86/include/asm/paravirt_types.h

Purpose: defines the paravirtualization operation tables and the inline-assembly machinery used to call and patch those operations. It is the ABI between normal x86 architecture code and native/hypervisor-specific paravirt backends.

Important APIs, types, and functions: operation tables include `struct pv_lazy_ops`, `struct pv_cpu_ops`, `struct pv_irq_ops`, `struct pv_mmu_ops`, and aggregate `struct paravirt_patch_template pv_ops`. Macro APIs include `paravirt_ptr()`, `PARAVIRT_CALL`, `PVOP_CALL*`, `PVOP_VCALL*`, `PVOP_CALLEE*`, `PVOP_ALT_*`, `PV_SAVE_ALL_CALLER_REGS`, `PV_RESTORE_ALL_CALLER_REGS`, `PV_CALLEE_SAVE_REGS_THUNK()`, `PV_CALLEE_SAVE()`, and `__PV_IS_CALLEE_SAVE()`.

Control flow: `PVOP_*` macros marshal up to four arguments into x86 calling-convention registers, emit an indirect call through a table slot, and mark it for runtime alternative patching to direct calls or inline native sequences. Callee-save variants call generated thunks that preserve scratch registers around functions used from constrained assembly contexts.

State and persistence: global `pv_ops` is runtime state set by boot/hypervisor code. Alternative patching changes executable text during boot but has no external persistence.

Dependencies and integration points: depends on descriptor and page-table types, nospec/retpoline annotations, alternative call patching, ENDBR/IBT constraints, `CONFIG_X86_32` versus `CONFIG_X86_64` calling conventions, and paravirt backends.

Risks: this file is highly sensitive to compiler constraints and CPU control-flow protections. Wrong clobbers, argument constraints, return masking, or thunk definitions can silently corrupt state. Operation struct layout is intentionally not randomized because offsets identify patch targets.

Test signals: build 32-bit and 64-bit paravirt configurations, boot native and Xen PV, run objtool/CFI/IBT validation, inspect alternative patch sites, exercise all PV CPU/MMU/IRQ operations, and compile with `CONFIG_ZERO_CALL_USED_REGS`.
