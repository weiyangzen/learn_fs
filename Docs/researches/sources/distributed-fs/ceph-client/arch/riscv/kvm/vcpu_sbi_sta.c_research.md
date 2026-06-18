<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kvm/vcpu_sbi_sta.c -->
# sources/distributed-fs/ceph-client/arch/riscv/kvm/vcpu_sbi_sta.c

## Purpose
`vcpu_sbi_sta.c` implements SBI Steal-Time Accounting for RISC-V KVM. It lets a guest provide a shared memory page where KVM records host scheduling delay.

## Important APIs, Types, And Functions
`kvm_riscv_vcpu_record_steal_time()` updates the guest `sbi_sta_struct`. `kvm_sbi_sta_steal_time_set_shmem()` validates and registers guest shared memory. `kvm_sbi_ext_sta_handler()` handles `STEAL_TIME_SET_SHMEM`. State register callbacks expose `shmem_lo` and `shmem_hi`.

## Control Flow
Set-shmem rejects nonzero flags, accepts the disable sentinel, checks 64-byte alignment, builds RV32 high bits when needed, zeroes the guest structure with `kvm_vcpu_write_guest()`, then records the GPA and current run delay. Record path maps the GPA to HVA, increments the sequence field before and after updating the little-endian steal value, marks the page dirty, and disables the GPA on invalid mapping.

## State And Persistence
Per-vCPU state is `arch.sta.shmem` and `arch.sta.last_steal`. Guest-visible persistence is the shared memory structure. Migration state is available through SBI state ONE_REG registers.

## Dependencies And Integration Points
It depends on scheduler `sched_info`, KVM guest memory translation, user access helpers for HVA writes, dirty logging, and the shared SBI dispatcher.

## Risks
The shared memory structure must remain within one page, hence strict 64-byte alignment. HVA errors must not continue writing stale addresses. Sequence updates are lockless and rely on guest seqlock-style reads.

## Test Signals
Enable STA in a guest, validate nonzero steal accumulation under vCPU preemption, test dirty logging, disable sentinel handling, alignment rejection, and migration restore of shmem registers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kvm/vcpu_sbi_sta.c -->
