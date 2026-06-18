<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/kvm_vcpu_pmu.h -->
# sources/distributed-fs/ceph-client/arch/riscv/include/asm/kvm_vcpu_pmu.h

## Purpose
Declares KVM virtual PMU counters, firmware events, SBI PMU handlers, and snapshot shared-memory support.

## Important APIs, Types, And Functions
types `kvm_fw_event`, `kvm_pmc`, `perf_event`, `sbi_pmu_ctr_info`, `kvm_vcpu`, `kvm_pmu`, `riscv_pmu_snapshot_data`, `kvm_vcpu_sbi_return`; functions/prototypes `kvm_riscv_vcpu_pmu_incr_fw`, `kvm_riscv_vcpu_pmu_read_hpm`, `kvm_riscv_vcpu_pmu_num_ctrs`, `kvm_riscv_vcpu_pmu_ctr_info`, `kvm_riscv_vcpu_pmu_ctr_start`, `kvm_riscv_vcpu_pmu_ctr_stop`, `kvm_riscv_vcpu_pmu_ctr_cfg_match`, `kvm_riscv_vcpu_pmu_fw_ctr_read`, `kvm_riscv_vcpu_pmu_fw_ctr_read_hi`, `kvm_riscv_vcpu_pmu_init`, `kvm_riscv_vcpu_pmu_snapshot_set_shmem`, `kvm_riscv_vcpu_pmu_event_info`, plus 3 more; macros/constants `__KVM_VCPU_RISCV_PMU_H`, `RISCV_KVM_MAX_FW_CTRS`, `RISCV_KVM_MAX_HW_CTRS`, `RISCV_KVM_MAX_COUNTERS`, `vcpu_to_pmu(vcpu) (&(vcpu)->arch.pmu_context)`, `pmu_to_vcpu(pmu) (container_of((pmu), struct kvm_vcpu, arch.pmu_context))`, `KVM_RISCV_VCPU_HPMCOUNTER_CSR_FUNCS`.

## Control Flow
Runtime flow is driven by KVM VM/vCPU creation, guest entry/exit, SBI or MMIO/CSR emulation, interrupt injection, and TLB/fence processing. This header supplies state layouts and function contracts consumed by the C implementation files rather than executing logic itself. Configuration-sensitive branches in this header mean build coverage must include the enabled and disabled forms of the relevant `CONFIG_*` options.

## State And Persistence
Persistent state is per-VM and per-vCPU architecture state: guest registers, CSRs, timers, interrupt bitmaps, VMIDs, guest-stage page tables, AIA/IMSIC state, PMU counters, SBI state, and optional NACL shared memory. Lifetimes are tied to KVM objects and CPU entry/exit serialization.

## Dependencies And Integration Points
Direct includes are `linux/perf/riscv_pmu.h`, `asm/kvm_vcpu_insn.h`, `asm/sbi.h`. Integrates with generic KVM, SBI, RISC-V virtualization CSRs, guest-stage MMU code, AIA/IMSIC/APLIC interrupt controllers, hrtimers, perf, one-reg ioctls, QEMU/KVM userspace ABI, and low-level guest entry assembly.

## Risks And Edge Cases
Risks concentrate around guest-visible ABI drift, incorrect CSR or interrupt state migration, missing memory ordering around atomic bitmaps and fences, stale VMID/TLB state, incorrect shared-memory endian conversion, and mismatches with QEMU/KVM one-reg expectations.

## Test Signals
Test signals include RISC-V KVM selftests, QEMU/KVM guest boot and migration, SBI extension tests, timer and PMU tests, AIA/IMSIC interrupt injection, dirty logging, MMIO/CSR emulation, nested-acceleration availability, and TLB/fence stress.

Source read size: 135 lines, 4837 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/kvm_vcpu_pmu.h -->
