# sources/distributed-fs/ceph-client/arch/arm64/include/asm/kvm_hyp.h

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/kvm_hyp.h -->
## sources/distributed-fs/ceph-client/arch/arm64/include/asm/kvm_hyp.h

### Purpose
`kvm_hyp.h` declares helpers used inside ARM64 KVM hypervisor code for host context access, timer/sysreg handling, VGIC, debug, FP/SVE, pKVM and hyp memory services.

### Important APIs, Types, And Functions
The file declares hyp entry helpers such as `__host_enter()`, `__guest_enter()`, `__fpsimd_*`, `__debug_*`, `__vgic_*`, `__timer_*`, `__sysreg_*`, `__pkvm_*`, `__hyp_*` helpers, and accessors for host context/sysregs depending on VHE/nVHE build mode.

### Control Flow
World-switch code calls these helpers around guest entry/exit to save host state, restore guest state, program timers/GIC/debug registers, and perform protected hypervisor operations. Many calls are only valid while executing at EL2.

### State, Persistence, And Dependencies
State is CPU register state, per-CPU host data, hyp page tables, and pKVM metadata. It depends on `kvm_host.h`, `kvm_asm.h`, sysreg definitions, VGIC/timer/debug support, and build-time VHE/nVHE separation.

### Integration Points
Used by hyp C and assembly, KVM host wrappers, protected-mode code, and nested virtualization paths.

### Risks
EL1/EL2 context misuse is dangerous. Missing save/restore calls corrupt host or guest registers. pKVM helpers must preserve host/hyp isolation.

### Test Signals
Exercise VHE/nVHE guest entry/exit, timer interrupts, VGIC state, debug register handoff, SVE/FPSIMD ownership, and pKVM memory transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/kvm_hyp.h -->
