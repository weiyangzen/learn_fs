<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kvm/sys_regs.c -->
# sources/distributed-fs/ceph-client/arch/arm64/kvm/sys_regs.c

## Purpose
This is the main arm64 KVM system register emulation and userspace register ABI implementation. It defines the descriptor tables for AArch64 system registers, AArch32 CP14/CP15 aliases, trapped system instructions, feature ID registers, timer/PMU/debug/GIC traps, nested virtualization EL2 register exposure, reset behavior, and the `KVM_GET_ONE_REG` / `KVM_SET_ONE_REG` plumbing.

## Important APIs, Types, And Functions
- `vcpu_read_sys_reg()` / `vcpu_write_sys_reg()` choose whether a virtual register is read from backing memory, live CPU state, a mapped EL1 register, or special merged state such as `CNTHCTL_EL2` when VHE/E2H applies.
- `sys_reg_descs[]`, `sys_insn_descs[]`, `cp14_regs[]`, `cp14_64_regs[]`, `cp15_regs[]`, and `cp15_64_regs[]` are sorted descriptor tables. Each `struct sys_reg_desc` entry supplies encoding, access handler, reset callback, backing register index, userspace get/set callbacks, value or writable mask, and visibility callback.
- Generic helpers include `access_rw()`, `access_vm_reg()`, `trap_raz_wi()`, `undef_access()`, `read_from_write_only()`, `write_to_read_only()`, `perform_access()`, `emulate_cp()`, and `emulate_sys_reg()`.
- Feature-ID logic is concentrated in `kvm_read_sanitised_id_reg()`, `read_id_reg()`, `arm64_check_features()`, `set_id_reg()`, and per-register setters such as `set_id_aa64pfr0_el1()`, `set_id_aa64dfr0_el1()`, `set_id_aa64mmfr0_el1()`, and `set_ctr_el0()`.
- Runtime trap entry points are `kvm_handle_sys_reg()`, `kvm_handle_cp15_64()`, `kvm_handle_cp15_32()`, `kvm_handle_cp14_64()`, `kvm_handle_cp14_32()`, `kvm_handle_cp10_id()`, and `kvm_handle_cp14_load_store()`.
- Userspace ABI entry points are `kvm_arm_sys_reg_get_reg()`, `kvm_arm_sys_reg_set_reg()`, `kvm_sys_reg_get_user()`, `kvm_sys_reg_set_user()`, `kvm_arm_num_sys_reg_descs()`, `kvm_arm_copy_sys_reg_indices()`, and `kvm_vm_ioctl_get_reg_writable_masks()`.
- Lifecycle functions include `kvm_reset_sys_regs()`, `kvm_calculate_traps()`, `kvm_finalize_sys_regs()`, `kvm_sys_regs_create_debugfs()`, and `kvm_sys_reg_table_init()`.

## Control Flow
On a trapped AArch64 MRS/MSR or system instruction, `kvm_handle_sys_reg()` decodes ESR into `sys_reg_params`, asks `triage_sysreg_trap()` for the descriptor index, selects `sys_reg_descs[]` for Op0 2/3 or `sys_insn_descs[]` otherwise, and calls `perform_access()`. `perform_access()` traces the access, rejects hidden registers with UNDEF, requires an access callback, calls it, and increments the guest PC if the callback reports completion. Reads write `params.regval` back to the guest general register.

AArch32 CP14/CP15 traps follow a similar flow but decode CP encodings from ESR. 64-bit CP traps combine two guest registers into `params.regval`; 32-bit traps use one register. AArch32 feature ID reads are rerouted into the AArch64 descriptor table so KVM has one feature-ID policy source. Unmatched accesses log an unimplemented sysreg message and inject UNDEF.

Reset iterates `sys_reg_descs[]`, runs reset callbacks, writes VM-scoped ID registers only once under `config_lock`, and reloads PMU state when PMU is enabled. Finalization adjusts ID registers just before first run, including nested virtualization setup and GIC/GICv5 ID-field reconciliation.

## State And Persistence Behavior
Most emulated registers persist in `vcpu->arch.ctxt.sys_regs[]` through descriptor `.reg` indexes. Some state is VM-wide, especially feature ID registers stored under `kvm->arch`, and is immutable after the VM has run. PMU counter counts and event types route through PMU helpers rather than only the raw sysreg array. Debug breakpoint/watchpoint state is stored in `vcpu->arch.vcpu_debug_state` and accessed through demux helpers. Cache geometry overrides allocate `vcpu->arch.ccsidr` lazily. Sanitized registers may be masked through per-VM RES0/RES1 mask state. Debugfs exposes current VM ID registers and RESX masks via seq files.

## Dependencies And Integration Points
This file depends on arm64 sysreg encoding helpers, cpufeature sanitization, PMU virtualization, VGIC interfaces, nested virtualization helpers, arch timer helpers, KVM MMU/stage-2 invalidation, debug monitor support, tracepoints from `trace.h`, and userspace copy helpers. It imports VGIC sysreg descriptors through `vgic_v3_get_sysreg_table()` during table validation. GIC trap handlers call VGIC functions for SGI dispatch, deactivate, GICv5 PPI enables, and virtual ICH state. Timer descriptors delegate to `kvm_arm_timer_*`. TLBI and AT system instructions delegate to nested MMU helpers and stage-2 unmap/invalidations.

## Risks And Edge Cases
- Descriptor tables must remain strictly sorted by encoding; `kvm_sys_reg_table_init()` fails if ordering or required reset callbacks are wrong.
- Feature ID writes are ABI-sensitive. KVM must allow old userspace-restored values in some cases while preventing guests from seeing impossible capabilities.
- VM-scoped ID registers become immutable once the VM has run; late userspace writes may fail with `-EBUSY`.
- Live CPU sysreg access is only valid with VHE-style loaded state. The register location logic warns if non-VHE paths try to read loaded CPU registers.
- Nested virtualization paths have special mappings for EL2 registers, VNCR-backed registers, redirected EL2-to-EL1 registers, E2H/TGE behavior, and TLBI shadow stage-2 invalidation.
- PMU access must enforce `PMUSERENR_EL0` privilege and accessible counter masks, or guests can observe/influence unsupported counters.
- Cache line and CLIDR/CCSIDR values are deliberately fabricated for stable migration; accepting invalid userspace cache geometry could create guest-visible inconsistency.
- GICv5 and legacy GICv3 ID field compatibility is explicitly handled and is easy to regress.

## Test Signals
- Build coverage should catch descriptor initializer and symbol errors.
- Boot/init tests should exercise `kvm_sys_reg_table_init()` table ordering and reset validation.
- KVM selftests for `KVM_GET_ONE_REG`, `KVM_SET_ONE_REG`, writable ID masks, feature ID immutability after run, and migration restore are direct signals.
- Guest tests for PMU, arch timers, GICv3 SGIs, GICv5 PPIs, debug register traps, MTE/SVE/Pointer Authentication visibility, and AArch32 CP15 ID reads cover major descriptor classes.
- Nested virtualization tests should cover EL2 sysregs, VNCR, AT/TLBI handlers, E2H/TGE combinations, and GIC ICH register visibility.
- Tracepoint observation through `kvm_sys_access` and debugfs `idregs`/`resx` provides runtime diagnostics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kvm/sys_regs.c -->
