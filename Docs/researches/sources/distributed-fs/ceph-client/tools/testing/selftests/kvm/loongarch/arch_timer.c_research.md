<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/loongarch/arch_timer.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/loongarch/arch_timer.c

## Purpose
`loongarch/arch_timer.c` tests LoongArch KVM timer virtualization. It validates time counter monotonicity, periodic timer interrupts, one-shot timer interrupts, and idle wakeup/emulated timer behavior through CSR timer registers.

## Important APIs, Types, and Functions
Key functions are `guest_irq_handler()`, `guest_test_period_timer()`, `guest_test_oneshot_timer()`, `guest_test_emulate_timer()`, `guest_time_count_test()`, `guest_code()`, `test_vm_create()`, and `test_vm_cleanup()`. The test uses `timer_get_cycles()`, `timer_get_cfg()`, `timer_get_val()`, `timer_set_next_cmp_ms()`, `disable_timer()`, `timer_irq_enable()`, `csr_read()`, and `csr_write()`.

## Control Flow
The guest first verifies the counter starts within an expected early window and monotonically increases. It enables timer interrupts, runs periodic mode until the shared iteration counter reaches zero, runs repeated one-shot timers while checking each IRQ increments `nr_iter`, and tests idle wakeup with local IRQs disabled around `idle 0`. The IRQ handler validates timer interrupt identity, clears TI, and either decrements periodic remaining count or validates one-shot TVAL/cycle timing.

## State and Persistence
State is shared through `vcpu_shared_data[]` and `test_args`, synchronized into the guest before execution. Timer CSR state persists in the vCPU during the test and is explicitly cleared or disabled by handlers.

## Dependencies and Integration Points
The file depends on LoongArch `processor.h`, `arch_timer.h`, common `timer_test.h`, `kvm_util.h`, and `ucall_common.h`. It integrates with the generic timer test harness through `test_vm_create()` and `test_vm_cleanup()`.

## Risks and Test Signals
Risks include timer IRQ delivery latency, wrong CSR emulation, nonmonotonic virtual counters, timer clear failures, and too-small error margins on loaded hosts. Test signals are guest assertions on interrupt id, iteration counts, TVAL/cfg relationship, elapsed cycles, and final `GUEST_DONE()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/loongarch/arch_timer.c -->
