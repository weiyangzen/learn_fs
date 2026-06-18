# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/arm64/arch_timer.c

Purpose: this is the arm64 guest/VM implementation for the generic `kvm/arch_timer.c` runner. It validates virtual and physical arch-timer IRQs using both CVAL and TVAL programming.

Important APIs and functions: `enum guest_stage` enumerates virtual CVAL, virtual TVAL, physical CVAL, and physical TVAL stages. Guest functions include `guest_configure_timer_action()`, `guest_validate_irq()`, `guest_irq_handler()`, `guest_run_stage()`, and `guest_code()`. Host functions include `test_init_timer_irq()`, `test_vm_create()`, and `test_vm_cleanup()`.

Control flow: host `test_vm_create()` requires VGICv3, creates N vCPUs running `guest_code`, installs IRQ descriptor tables and an IRQ handler, optionally applies `KVM_ARM_SET_COUNTER_OFFSET`, discovers virtual/physical timer IRQs, and syncs arguments to the guest. The guest masks timers, initializes GICv3, enables timer IRQs, and runs four stages. Each stage programs the timer, delays for the period plus margin, and asserts exactly one IRQ arrived.

State and persistence: `vtimer_irq`, `ptimer_irq`, `test_args`, and `vcpu_shared_data` are synced as guest-visible globals. Per-vCPU shared data tracks current stage, iteration count, and timestamp. No durable state is written.

Dependencies and integration points: uses arm64 `arch_timer`, `gic`, `vgic`, delay helpers, descriptor table helpers, and KVM counter-offset capability. It plugs into the host runner in `kvm/arch_timer.c`.

Risks: delivery timing depends on host scheduling and timer emulation latency. Physical timer support and VGICv3 are required. Counter offset support is optional but hard-fails if requested and unavailable.

Test signals: guest assertions validate IRQ ID, timer condition (`cnt >= cval`), `CTL_ISTATUS`, and arrival within margin. Host reports guest assertion stage/iteration on abort and `PASS(vCPU-n)` on success.
