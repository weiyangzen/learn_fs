<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/include/arm64/arch_timer.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/include/arm64/arch_timer.h

Purpose: this arm64 helper header provides guest-side generic timer accessors for KVM selftests. It abstracts virtual versus physical timer sysregs, conversion between time units and counter cycles, and host-side helpers for querying the timer IRQ assigned to a vCPU.

Important APIs, types, and functions: `enum arch_timer` distinguishes `VIRTUAL` and `PHYSICAL`. Control bits `CTL_ENABLE`, `CTL_IMASK`, and `CTL_ISTATUS` mirror timer control register fields. Conversion macros use `timer_get_cntfrq()`. Inline helpers read counter values (`timer_get_cntct()`), compare/timer values (`timer_set_cval()`, `timer_get_cval()`, `timer_set_tval()`, `timer_get_tval()`), and control registers (`timer_set_ctl()`, `timer_get_ctl()`). `timer_set_next_cval_ms()` and `timer_set_next_tval_ms()` schedule future events. `vcpu_get_vtimer_irq()` and `vcpu_get_ptimer_irq()` select virtual/hypervisor or physical/hypervisor timer IRQ attributes based on `vcpu_has_el2()`.

Control flow: each accessor switches on timer type and fails the guest on invalid enum values. Reads of counters and TVAL include `isb()` where needed to synchronize system register state.

State, persistence, and dependencies: state is hardware/KVM virtual timer register state only. Dependencies include `processor.h` sysreg accessors and KVM arm64 timer device attributes.

Risks and edge cases: conversions divide by the runtime counter frequency and assume nonzero `CNTFRQ_EL0`. EL2-capable vCPUs use HVTIMER/HPTIMER attributes instead of VTIMER/PTIMER. Invalid timer enum values intentionally fail guest execution.

Test signals: downstream timer tests use these helpers to verify IRQ delivery, compare values, masking, and counter conversions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/include/arm64/arch_timer.h -->
