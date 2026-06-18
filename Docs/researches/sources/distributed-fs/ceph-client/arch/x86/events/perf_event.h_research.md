## `sources/distributed-fs/ceph-client/arch/x86/events/perf_event.h`

Purpose: central private contract for the x86 perf-event subsystem. It defines the data structures, event flags, scheduling constraints, PMU operation table, per-CPU PMU state, Intel PEBS/LBR/Topdown support, AMD BRS/LBR hooks, and vendor init entry points used by the x86 perf backends.

Important APIs, types, and functions: `struct event_constraint` and the `EVENT_CONSTRAINT*` macros describe legal counter placement; `struct extra_reg` and `struct intel_shared_regs` manage event-specific shared MSRs; `struct cpu_hw_events` is the per-CPU active-event state; `struct x86_pmu` is the main backend vtable; `struct x86_hybrid_pmu` holds hybrid-core PMU overrides. Inline helpers include `is_topdown_event()`, `x86_pmu_config_addr()`, `__x86_pmu_enable_event()`, `x86_pmu_disable_event()`, `kernel_ip()`, and `set_linear_ip()`.

Control flow and integration: generic perf code calls into the `x86_pmu` callbacks for add/delete/start/stop/read/IRQ and hardware configuration. Model-specific backends populate `x86_pmu`, constraints, cache-event maps, PEBS constraints, LBR methods, and sysfs format/event attributes. Static calls wrap hot paths such as period setting, counter update, PEBS draining, and PEBS enable/disable. Hybrid support transparently resolves global fields to per-PMU fields through `hybrid()`, `hybrid_var()`, and `hybrid_bit()`.

State and persistence: most state is per-CPU (`cpu_hw_events`, `pmc_prev_left`) or global read-mostly backend metadata (`x86_pmu`, capability masks, constraint arrays). Hardware state is persistent in PMU MSRs until explicitly disabled or overwritten. Extra-register references use locking and atomic refs because sibling threads or events can share MSRs.

Dependencies and integration points: depends on Linux perf core, x86 MSR accessors, Intel debug store, XSAVE/LBR definitions, APIC/NMI perf interrupts, KVM guest/host masks, CPU feature config, and vendor backends (`intel_pmu_init()`, `amd_pmu_init()`, `zhaoxin_pmu_init()`). The header also exposes sysfs event formatting helpers and branch classification constants consumed by `utils.c`.

Risks: constraint macros are scheduler-critical; bad masks can silently mis-schedule events or cause factorial retry costs for overlap constraints. MSR writes must respect virtualization masks and counter-pair state. Compile-time feature guards must keep stubs behaviorally compatible. PEBS/LBR and hybrid fields are highly coupled to CPU model detection.

Test signals: successful kernel build across Intel/AMD/Zhaoxin and feature-disabled configs; perf selftests for raw events, fixed counters, topdown, PEBS/LBR, and hybrid PMUs; boot logs showing PMU init; `perf stat`, `perf record`, and NMI overflow behavior on supported hardware and virtualized guests.
