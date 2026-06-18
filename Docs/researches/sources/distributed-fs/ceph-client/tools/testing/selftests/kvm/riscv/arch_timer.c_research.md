<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/riscv/arch_timer.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/riscv/arch_timer.c

## Purpose
`riscv/arch_timer.c` tests RISC-V KVM SSTC timer interrupt virtualization. It validates that guest writes to `vstimecmp` cause supervisor timer interrupts at the expected virtual time.

## Important APIs, Types, and Functions
Important functions are `guest_irq_handler()`, `guest_run()`, `guest_code()`, `test_vm_create()`, and `test_vm_cleanup()`. It uses `timer_set_next_cmp_ms()`, `timer_get_cycles()`, `timer_get_cmp()`, `timer_irq_enable()`, `timer_irq_disable()`, vector table helpers, and `vcpu_get_reg(... RISCV_TIMER_REG(frequency))`.

## Control Flow
Host setup creates vCPUs, requires `KVM_RISCV_ISA_EXT_SSTC`, installs interrupt handlers, initializes vector tables, reads and syncs timer frequency, and syncs test arguments. Guest code disables timer IRQs, enables local IRQs, then loops setting the next compare value, recording start cycles, enabling timer IRQs, delaying for period plus margin, and checking the interrupt count. The IRQ handler disables timer IRQs, verifies the cause is supervisor timer, and asserts current cycles are at or beyond compare.

## State and Persistence
State is shared through `timer_freq`, `test_args`, and per-vCPU `vcpu_shared_data`. Timer compare and interrupt-enable state is vCPU-local and reset by the handler/test loop.

## Dependencies and Integration Points
The file depends on RISC-V processor helpers, common timer test infrastructure, `kvm_util.h`, `ucall_common.h`, and KVM ISA extension discovery. It integrates with the generic architecture timer harness through `test_vm_create()`.

## Risks and Test Signals
Risks include SSTC absence, wrong interrupt cause decoding, timer frequency mismatch, late interrupt delivery under load, and not disabling IRQs between iterations. Test signals are the SSTC require skip, guest assertions on interrupt id and `xcnt >= cmp`, iteration count checks, and final `GUEST_DONE()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/riscv/arch_timer.c -->
