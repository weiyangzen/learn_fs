<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kvm/vcpu_timer.c -->
# sources/distributed-fs/ceph-client/arch/riscv/kvm/vcpu_timer.c

## Purpose
`vcpu_timer.c` virtualizes the RISC-V timer for KVM guests. It handles time delta, compare programming, hrtimer fallback, SSTC support, ONE_REG timer state, and save/restore around vCPU scheduling.

## Important APIs, Types, And Functions
`kvm_riscv_current_cycles()`, `kvm_riscv_delta_cycles2ns()`, hrtimer callbacks, `kvm_riscv_vcpu_timer_next_event()`, `kvm_riscv_vcpu_timer_pending()`, timer get/set ONE_REG handlers, init/deinit/reset, restore/sync/save, and `kvm_riscv_guest_timer_init()` are the main APIs.

## Control Flow
Without SSTC, next-event clears pending timer interrupt and starts an hrtimer that injects `IRQ_VS_TIMER` at expiry. With SSTC, next-event writes `VSTIMECMP`; VM exit syncs the CSR back into `next_cycles`, save disables host-local `VSTIMECMP`, and blocking vCPUs get an hrtimer to wake them. Time register writes adjust guest `time_delta`.

## State And Persistence
Per-vCPU state includes `next_cycles`, `next_set`, `sstc_enabled`, `init_done`, hrtimer, and function pointer. Per-VM state includes `time_delta`, `nsec_mult`, and `nsec_shift`. ONE_REG exposes frequency, time, compare, and state.

## Dependencies And Integration Points
It depends on `riscv_timebase`, clocksource conversion helpers, hrtimer, NaCl CSR wrappers, KVM interrupts, KVM blocking hooks, and the SBI TIME handler.

## Risks
Timer behavior differs sharply between SSTC and hrtimer fallback. RV32 high/low CSR write ordering must prevent transient wrong compare values. `set_reg_timer(state)` uses the provided register value as a next-event argument when enabling, so migration tooling must set compare before state.

## Test Signals
Guest clockevent tests, timer interrupt latency checks, migration of timer ONE_REG state, blocking WFI wakeups, SSTC vs non-SSTC host coverage, and RV32 compare tests are key.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kvm/vcpu_timer.c -->
