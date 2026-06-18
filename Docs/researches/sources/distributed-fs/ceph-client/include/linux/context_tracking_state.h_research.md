## sources/distributed-fs/ceph-client/include/linux/context_tracking_state.h

Purpose: This header defines the per-CPU context tracking data layout, state encoding, and inline readers used by RCU, nohz, and entry code.

Important APIs, types, and functions: `CT_NESTING_IRQ_NONIDLE` distinguishes IRQ vs task idle transitions. `enum ctx_state` defines disabled, kernel, idle, user, guest, and max values. `struct context_tracking` contains `active` and `recursion` for user tracking, atomic `state` for context/RCU watching bits, and idle/NMI nesting counters. Bit layout macros define `CT_STATE_WIDTH`, `CT_RCU_WATCHING_WIDTH`, masks, start/end positions, and `CT_RCU_WATCHING`. Readers include `__ct_state`, `ct_rcu_watching`, `ct_rcu_watching_cpu`, `ct_rcu_watching_cpu_acquire`, `ct_nesting`, `ct_nesting_cpu`, `ct_nmi_nesting`, `ct_nmi_nesting_cpu`, `context_tracking_enabled`, `context_tracking_enabled_cpu`, `context_tracking_enabled_this_cpu`, and `ct_state`.

Control flow: Callers sample per-CPU state using raw or acquire atomics depending on ordering needs. `ct_state()` disables preemption while reading current CPU state. Static key `context_tracking_key` eliminates overhead when user tracking is off.

State and persistence: The persistent runtime state is per-CPU `struct context_tracking`. Its atomic `state` packs low bits for context state and higher bits for RCU watching generation/counter state. Idle and NMI nesting fields track transition depth.

Dependencies and integration points: It depends on percpu APIs, static keys, bit macros, atomics, RCU dynticks torture sizing, and IRQ tracking declarations.

Risks and test signals: Risks include bitfield width mistakes, missing acquire ordering when observing remote CPUs, reading current CPU state with preemption enabled, and static-key mismatch with per-CPU active flags. Test signals include compile-time static assertions, RCU torture, nohz full, CPU hotplug, preemption debug, and remote CPU watching checks.
