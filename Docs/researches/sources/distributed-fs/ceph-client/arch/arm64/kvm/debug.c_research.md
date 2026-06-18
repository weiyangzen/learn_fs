# sources/distributed-fs/ceph-client/arch/arm64/kvm/debug.c

## Purpose
`debug.c` manages ARM64 KVM debug, guest debug, profiling, trace, and debug-register ownership transitions. It configures `MDCR_EL2`, records host debug capabilities, selects whether breakpoint/watchpoint registers are host-owned, guest-owned, or unused, virtualizes OS Lock effects, preserves software single-step state across KVM/user debugging, and exposes TRBE/tracing hooks used by tracing code.

## Important APIs, Types, and Functions
`cpu_has_spe` detects usable Statistical Profiling Extension support by checking ID_AA64DFR0 and PMBIDR. `kvm_init_host_debug_data` records host PMU counter count, breakpoint/watchpoint counts, and capability flags such as `HAS_SPE`, `HAS_BRBE`, `HAS_TRBE`, and `EL1_TRACING_CONFIGURED`. `kvm_debug_init_vhe` sanitizes VHE SPE state by clearing PMSCR_EL1.

`kvm_arm_setup_mdcr_el2` builds the vCPU's `mdcr_el2` trap configuration. `setup_external_mdscr` computes the external MDSCR_EL1 image used when KVM or userspace owns debug state. `kvm_vcpu_load_debug` selects debug ownership and prepares MDCR/MDSCR state before vCPU entry. `kvm_vcpu_put_debug` restores host MDCR_EL2 on VHE and repairs guest/host software-step pending state on exit. `kvm_debug_set_guest_ownership` gives ownership of debug registers to the guest after trapped access when the host is not already using them. `kvm_debug_handle_oslar` emulates writes to OSLAR_EL1 and reloads vCPU state to apply the changed ownership/trap behavior.

Trace/TRBE exported APIs are `kvm_enable_trbe`, `kvm_disable_trbe`, and `kvm_tracing_set_el1_configuration`. They are guarded by `skip_trbe_access`, which rejects preemptible callers, protected KVM, uninitialized KVM, and VHE-only cases where applicable.

## Control Flow
Host debug initialization reads `id_aa64dfr0_el1`, records PMU event counter count if PMUv3 is implemented, records BRP/WRP counts, marks SPE if implemented and not prohibited by PMBIDR, and for nVHE additionally records BRBE and TRBE/trace-filter availability. In protected mode without TRBE, EL1 tracing is forced disabled by marking `EL1_TRACING_CONFIGURED`. VHE debug initialization clears unknown reset values in PMSCR when SPE is present.

On vCPU load, KVM first asserts sysregs are not already loaded on CPU. In VHE it saves host `MDCR_EL2`. It then selects a debug owner. If userspace requested guest debugging or the guest OS Lock is enabled, KVM takes host ownership, computes an external MDSCR value, and, for userspace single-step, steals the guest single-step state machine by tracking `GUEST_SS_ACTIVE_PENDING` and `HOST_SS_ACTIVE_PENDING` around the CPSR SS bit. Otherwise it reads guest `MDSCR_EL1`: if KDE or MDE is set, debug registers are guest-owned and should be loaded eagerly; if neither is set, the state is free. Finally it calls `kvm_arm_setup_mdcr_el2`.

`kvm_arm_setup_mdcr_el2` disables preemption, initializes `vcpu->arch.mdcr_el2` with the host counter count and trap bits for PMU, SPE, trace filter, PMCR, debug ROM, and OS-related debug registers. It routes software debug exceptions to EL2 when userspace is debugging, traps debug registers with `TDA` when the guest does not own them, lets nested virtualization adjust MDCR when needed, and writes MDCR_EL2 directly on VHE. vCPU put restores host MDCR_EL2 on VHE and undoes the single-step state swap before returning to userspace.

## State and Persistence Behavior
Persistent runtime state lives in per-CPU host debug data and per-vCPU arch fields. Host data stores PMU counter count, breakpoint/watchpoint counts, debug capability flags, saved VHE `mdcr_el2`, and trace configuration. vCPU state includes `arch.mdcr_el2`, `arch.external_mdscr_el1`, `arch.debug_owner`, guest sysregs such as MDSCR/OSLSR, and software-step pending flags. No file or disk state is written. OSLAR handling updates guest OS Lock state and immediately reloads vCPU state under preemption disable so trap ownership takes effect on the current CPU.

## Dependencies and Integration Points
This file depends on ARM64 PMU/debug/trace sysreg definitions, KVM host data helpers, VHE/nVHE mode predicates, pKVM mode checks, nested virtualization MDCR setup, vCPU flag helpers, sysreg emulation accessors, and exported trace/TRBE consumers. It is called from `arm.c` during CPU hyp context initialization (`kvm_init_host_debug_data`, `kvm_debug_init_vhe`) and vCPU scheduling (`kvm_vcpu_load_debug`, `kvm_vcpu_put_debug`). The OSLAR path calls back into `kvm_arch_vcpu_put` and `kvm_arch_vcpu_load` to reapply the full scheduling state.

## Risks and Edge Cases
Debug ownership has high ABI sensitivity because userspace debugging, guest debugging, OS Lock semantics, and nested virtualization all compete for the same registers. Single-step state stealing must preserve both host-requested and guest-pending SS bits or userspace can see spurious/missing step events. `MDCR_EL2` trap bits must prevent unintended guest access to PMU, SPE, TRBE, trace, and debug resources, especially in protected or nVHE modes. The TRBE exported APIs require non-preemptible callers; misuse is warned and ignored. The OSLAR reload path is broad because it puts and reloads the whole vCPU, so callers must already be in a valid loaded-vCPU context.

## Test Signals
Relevant tests include KVM guest debug selftests for software single-step, hardware breakpoints/watchpoints, guest-owned debug register access, OS Lock enable/disable, VHE and nVHE MDCR save/restore, nested virtualization MDCR behavior, and PMU/SPE/TRBE trap exposure. Trace tests should verify `kvm_enable_trbe`, `kvm_disable_trbe`, and `kvm_tracing_set_el1_configuration` under preemption-disabled contexts and confirm protected KVM rejects TRBE manipulation. Regression checks should assert host debug state is restored after vCPU exit.
