# sources/distributed-fs/ceph-client/arch/arm64/include/asm/kvm_host.h

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/kvm_host.h -->
## sources/distributed-fs/ceph-client/arch/arm64/include/asm/kvm_host.h

### Purpose
`kvm_host.h` is the main ARM64 KVM host architecture contract. It defines VM/vCPU architecture state, stage-2 MMU state, hypervisor memory caches, sysreg storage, feature flags, debug/FP ownership, pKVM state, request numbers, and host-facing KVM APIs.

### Important APIs, Types, And Functions
Major types include `enum kvm_mode`, `struct kvm_hyp_memcache`, `struct kvm_s2_mmu`, `struct kvm_arch`, `struct kvm_cpu_context`, `struct kvm_host_data`, `struct kvm_vcpu_arch`, `struct vcpu_reset_state`, `struct kvm_sysreg_masks`, `struct fgt_masks`, `struct kvm_vm_stat`, and `struct kvm_vcpu_stat`. Important helpers cover hyp memcache push/pop/top-up/free, MPIDR indexing, sysreg read/write/masking, vCPU flag accessors, hyp calls, debug ownership, PV time, VMID allocation, SVE/PAuth/MTE feature checks, ID-register access, and FGT grouping.

### Control Flow
VM creation allocates `struct kvm_arch`, initializes stage-2 MMU, VGIC/timer/PMU state, ID registers, and pKVM metadata. vCPU creation initializes `struct kvm_vcpu_arch`, feature flags, sysregs, debug/FP state, and MMU caches. Run paths load host data, select hardware MMU, call VHE directly or nVHE through SMCCC, then handle exits through declared trap handlers.

### State, Persistence, And Dependencies
The file describes durable in-memory VM/vCPU state for the lifetime of a KVM VM, plus per-CPU host data. It has no filesystem persistence. It depends on generic KVM, VGIC, arch timer, PMU, PSCI, maple tree filters, SMCCC, `kvm_asm.h`, FPSIMD/SVE, and CPU feature infrastructure.

### Integration Points
Almost every ARM64 KVM implementation file includes this header. It bridges userspace ioctls, generic KVM core, EL2 hyp code, pKVM, nested virtualization, performance/debug subsystems, and guest memory management.

### Risks
This is a high-blast-radius ABI surface. Flag accessor misuse can race with vCPU load/put. Sysreg enum ordering and VNCR offsets must stay synchronized. Shared/canonical stage-2 MMUs need correct refcount and pending-unmap handling. pKVM state transitions must prevent use-after-teardown.

### Test Signals
Run full ARM64 KVM selftests, nested virtualization tests, pKVM boot tests, VMID rollover stress, SVE/PAuth/MTE feature exposure tests, PMU/debug tests, and userspace register ioctl round trips.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/kvm_host.h -->
