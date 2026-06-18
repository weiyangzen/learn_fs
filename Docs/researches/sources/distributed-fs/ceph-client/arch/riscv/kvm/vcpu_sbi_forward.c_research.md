<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kvm/vcpu_sbi_forward.c -->
# sources/distributed-fs/ceph-client/arch/riscv/kvm/vcpu_sbi_forward.c

## Purpose
`vcpu_sbi_forward.c` declares SBI extension descriptors whose calls are intentionally handled by userspace rather than KVM kernel code.

## Important APIs, Types, And Functions
It exports `vcpu_sbi_ext_experimental`, `vcpu_sbi_ext_vendor`, `vcpu_sbi_ext_dbcn`, and `vcpu_sbi_ext_mpxy`. Each descriptor maps an SBI extension range or id to `kvm_riscv_vcpu_sbi_forward_handler()`. DBCN and MPXY are default-disabled.

## Control Flow
When the central dispatcher finds one of these descriptors and it is enabled, control jumps to the shared forward handler, which populates `KVM_EXIT_RISCV_SBI` and exits the KVM_RUN ioctl to userspace.

## State And Persistence
No private state is kept. Enabled/disabled status lives in the vCPU SBI context and can be exposed through SBI extension ONE_REG controls before first run.

## Dependencies And Integration Points
This file is a policy bridge between kernel KVM and VMM userspace for debug console, message proxy, vendor, and experimental SBI behavior.

## Risks
Default-disabled extensions must not be accidentally exposed to guests. VMMs need to handle forwarded calls and write return values; otherwise guests see not-supported defaults or hang.

## Test Signals
Tests should enable DBCN/MPXY via ONE_REG, confirm KVM exits with expected extension/function ids and argument registers, and verify disabled extensions probe as absent.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kvm/vcpu_sbi_forward.c -->
