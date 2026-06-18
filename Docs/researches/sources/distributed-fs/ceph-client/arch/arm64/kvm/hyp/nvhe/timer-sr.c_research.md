<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kvm/hyp/nvhe/timer-sr.c -->
# sources/distributed-fs/ceph-client/arch/arm64/kvm/hyp/nvhe/timer-sr.c

## Purpose
`timer-sr.c` manages nVHE timer trap state and virtual counter offset writes. It switches CNTHCTL_EL2 settings between host-friendly and guest-constrained access modes.

## Important APIs, Types, and Functions
`__kvm_timer_set_cntvoff()` writes `cntvoff_el2`. `__timer_disable_traps()` allows host physical timer/counter access. `__timer_enable_traps()` disallows guest physical timer access as required, allows physical counter access for protected mode or no physical offset, handles hVHE bit shifts, and traps virtual timer/counter on broken CNTVOFF implementations.

## Control Flow, State, and Persistence
Timer state is stored in system registers, primarily `cnthctl_el2` and `cntvoff_el2`. Guest entry calls enable traps; guest exit calls disable traps. The hVHE path shifts control bits by 10. Protected mode avoids physical counter offsetting and therefore allows PCT access.

## Dependencies and Integration Points
It depends on arch timer definitions, KVM timer data in `struct kvm`, hVHE detection, protected-mode status, and `switch.c` guest entry/exit plus host hypercall dispatch for CNTVOFF updates.

## Risks and Test Signals
Risks include exposing physical timer/counter access incorrectly, bit-shift mistakes on hVHE, broken CNTVOFF workaround regressions, and offset policy differences for protected VMs. Test signals are timer interrupts in guests, physical counter access trapping expectations, hVHE/nVHE configurations, protected VM timer behavior, and hosts with broken CNTVOFF.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kvm/hyp/nvhe/timer-sr.c -->
