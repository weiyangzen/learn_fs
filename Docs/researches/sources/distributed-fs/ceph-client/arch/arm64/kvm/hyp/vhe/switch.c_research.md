# sources/distributed-fs/ceph-client/arch/arm64/kvm/hyp/vhe/switch.c

## Purpose
This is the VHE guest run and world-switch implementation. It computes HCR_EL2 for normal and nested guests, activates/deactivates traps, loads stage-2 context, handles fast hyp exits that can be resolved without returning to the host kernel, and restores host state after guest exit or hyp panic.

## Important APIs, Types, and Functions
- Per-CPU state: `kvm_host_data`, `kvm_hyp_ctxt`, and `kvm_hyp_vector`.
- `__compute_hcr()` merges KVM HCR policy with nested-virtualization guest HCR bits while excluding unsafe bits.
- `__activate_traps()` and `__deactivate_traps()` program HCR, timer offsets, CPTR traps, and exception vectors.
- `kvm_vcpu_load_vhe()` and `kvm_vcpu_put_vhe()` load/put long-lived vCPU sysregs and stage-2 state.
- Fast handlers include `kvm_hyp_handle_timer()`, `kvm_hyp_handle_eret()`, `kvm_hyp_handle_tlbi_el2()`, `kvm_hyp_handle_cpacr_el1()`, `kvm_hyp_handle_zcr_el2()`, and `kvm_hyp_handle_impdef()`.
- `__kvm_vcpu_run_vhe()` is the core run loop; `__kvm_vcpu_run()` wraps it with DAIF/PMR handling.

## Control Flow
On vCPU load, VHE stores the running vCPU in per-CPU host data, switches sysregs, activates common traps, and loads stage-2. The run loop lazily switches FPSIMD to the guest, saves host common state, activates traps, adjusts the guest PC, restores guest return state, switches debug state, enters the guest, and repeats while `fixup_guest_exit()` can handle exits locally. When a real exit remains, it saves guest state, deactivates traps, restores host state and debug state, issues an ISB, returns FPSIMD to the host, and saves 32-bit FP exception state if needed.

Fast exit handling synchronizes PSTATE, fixes virtual EL2 mode bits for nested guests, and dispatches by ESR class. Timer reads in virtual EL2 context can be satisfied locally. ERET from a VHE guest hypervisor can be converted to a canonical EL1 return when no forwarding is required. Nested EL2 TLBI operations can be remapped to EL1 operations through `__kvm_tlbi_s1e2()`. CPACR_EL1 accesses in virtual hyp context are redirected to CPTR_EL2 state. ZCR_EL2 forces FP context loading before slow-path handling.

## State and Persistence
State spans per-CPU host data flags, `__hyp_running_vcpu`, guest/host CPU contexts, vCPU sysreg arrays, HCR_EL2, VNCR_EL2 mappings, VBAR_EL1, timer CVAL/offset registers, CPTR/FP ownership, and debug registers. The code preserves the invariant that a vCPU entered in virtual hyp context exits in virtual hyp context.

## Dependencies and Integration Points
It depends on common hyp trap helpers, sysreg save/restore code, stage-2 loading, arch timer helpers, FPSIMD/SVE/SME handling, nested virtualization helpers, pointer-auth ERET authentication, PMR/DAIF interrupt masking, and VHE-specific vectors. It integrates with `sysreg-sr.c`, `debug-sr.c`, `tlb.c`, and the generic KVM vCPU run path.

## Risks and Edge Cases
Risks include HCR bits leaking guest control into host execution, incorrect virtual EL2 PSTATE fixup, timer CVAL offset mistakes when CNTPOFF is present, failing to restore host vectors, and fast-handling an exit that should be forwarded to a nested hypervisor. Erratum handling requires stage-1 and stage-2 to be configured before clearing TGE, and TLB handling must consider VNCR mappings that force slow-path processing.

## Test Signals
Test VHE guest entry/exit, nested virtualization with virtual EL2, timer virtualization with and without ECV/CNTPOFF, nested TLBI, CPACR/FP/SVE/SME traps, pointer-auth ERET, PMU implementation-defined traps, and hyp panic paths. Lockdep, KASAN, kprobes exclusion, and tracepoints around exit reasons are useful regression signals.
