<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kvm/vcpu_sbi_v01.c -->
# sources/distributed-fs/ceph-client/arch/riscv/kvm/vcpu_sbi_v01.c

## Purpose
`vcpu_sbi_v01.c` implements legacy SBI v0.1 calls for older RISC-V guests.

## Important APIs, Types, And Functions
`kvm_sbi_ext_v01_handler()` handles legacy set timer, clear/send IPI, shutdown, console forwarding, remote fence.i, and remote sfence.vma variants. `vcpu_sbi_ext_v01` registers the legacy extension id range.

## Control Flow
The handler switches on `a7` rather than `a6`. Console calls are forwarded to userspace. Timer and shutdown use modern KVM timer/reset helpers. IPI and RFENCE obtain a hart mask either from guest memory through `kvm_riscv_vcpu_unpriv_read()` or from the online vCPU count, then inject interrupts or issue fence requests.

## State And Persistence
It updates timer compare state, VS software interrupt pending bits, system event exit state, and remote TLB/icache request state. No private persistent state is owned.

## Dependencies And Integration Points
It integrates legacy SBI ABI, unprivileged guest memory reads, KVM timer, interrupt injection, VMID-based hfence helpers, and userspace console handling.

## Risks
Legacy calls use different return conventions and the top-level dispatcher must avoid writing `a1`. Guest memory faults during mask reads are redirected through `retdata->utrap`. Mask construction from online vCPU count must avoid invalid vCPU ids.

## Test Signals
Boot older firmware/guest images, exercise console forwarding, legacy IPI/fence calls with NULL and explicit masks, timer programming, and shutdown exits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kvm/vcpu_sbi_v01.c -->
