<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kvm/vcpu_sbi_replace.c -->
# sources/distributed-fs/ceph-client/arch/riscv/kvm/vcpu_sbi_replace.c

## Purpose
`vcpu_sbi_replace.c` implements SBI v0.2 replacement extensions for timer, IPI, RFENCE, and system reset.

## Important APIs, Types, And Functions
Handlers include `kvm_sbi_ext_time_handler()`, `kvm_sbi_ext_ipi_handler()`, `kvm_sbi_ext_rfence_handler()`, and `kvm_sbi_ext_srst_handler()`. Exported descriptors are `vcpu_sbi_ext_time`, `vcpu_sbi_ext_ipi`, `vcpu_sbi_ext_rfence`, and `vcpu_sbi_ext_srst`.

## Control Flow
TIME validates `SET_TIMER`, forms the next cycle value, increments firmware PMU accounting, and programs the vCPU timer. IPI iterates vCPUs selected by hbase/hmask and injects VS software interrupts. RFENCE translates remote fence requests into KVM fence/hfence requests with the current VMID. SRST maps shutdown/reboot to KVM system event exits.

## State And Persistence
The file updates timer state, pending interrupt state, PMU firmware counters, system event exit state, and indirectly remote TLB/icache request queues. There is no disk persistence.

## Dependencies And Integration Points
It integrates with KVM timer, interrupt injection, PMU firmware counters, RISC-V TLB/fence helpers, VMID management, and userspace-visible KVM reset/shutdown events.

## Risks
Hart mask validation is guest ABI-sensitive; partial IPI delivery must report invalid parameters. RFENCE range interpretation must preserve zero/-1 full-range semantics. SRST must stop all vCPUs and exit cleanly to userspace.

## Test Signals
Run guest timer tests, SMP IPI tests with sparse hart masks, TLB shootdown stress, reboot/shutdown SBI tests, and PMU firmware event counter checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kvm/vcpu_sbi_replace.c -->
