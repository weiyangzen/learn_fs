# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/arm64/arch_timer_edge_cases.c

Purpose: this arm64 KVM selftest stresses edge cases in virtual and physical arch-timer emulation: timers beyond TVAL range, timers in the past, counter jumps, timer reprogramming, repeated firing, masking/unmasking, long delays, userspace sleeps, scheduler yields, and vCPU migration.

Important APIs and functions: `struct test_args`, `struct test_vcpu_shared_data`, `sleep_method[]`, and `irq_wait_method[]` define the test matrix. Guest helpers include `set_cval_irq()`, `set_tval_irq()`, `guest_irq_handler()`, timer wait/sleep helpers, `reset_timer_state()`, `test_basic_functionality()`, `timers_sanity_checks()`, `test_timers_above_tval_max()`, `test_timers_in_the_past()`, counter-move tests, reprogramming tests, repeated-fire tests, and `guest_code()`. Host helpers include `kvm_set_cntxct()`, `handle_sync()`, `test_run()`, `test_vm_create()`, and `set_counter_defaults()`.

Control flow: `main()` requires VGICv3, parses timer selection and timing options, records the default cpuset, computes counter width/max defaults, then runs separate VMs for virtual and/or physical timers. Guest code initializes GIC/timers and repeatedly runs the edge-case suite. Guest syncs ask userspace to set counters, sleep, yield, or migrate; host `handle_sync()` performs those actions and resumes the vCPU.

State and persistence: shared atomic counters track handled and spurious IRQs. Host global `CVAL_MAX`, `DEF_CNT`, timer IRQ numbers, and cpuset state influence tests. No persistent files are used.

Dependencies and integration points: depends on arm64 timer sysregs, VGIC/GIC helpers, KVM timer count registers (`KVM_REG_ARM_TIMER_CNT`, `KVM_REG_ARM_PTIMER_CNT`), CPU affinity, and kselftest timeout protection for theoretically infinite waits.

Risks: many waits can hang if timer emulation is broken, relying on the outer runner timeout. Counter width inference is conservative but architecture-sensitive. Migration/yield/sleep paths can be noisy on loaded systems.

Test signals: guest assertions check IRQ counts, ISTATUS/timer-condition consistency, cval/tval relationships, no-IRQ windows, and expected firing after counter manipulation. Host unexpected ucalls or guest aborts are failures.
