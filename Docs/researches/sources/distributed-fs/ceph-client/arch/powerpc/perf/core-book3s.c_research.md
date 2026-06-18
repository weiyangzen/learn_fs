
# sources/distributed-fs/ceph-client/arch/powerpc/perf/core-book3s.c

## Purpose

This is the central Book3S PowerPC perf PMU implementation. It manages per-CPU hardware event state, event constraint solving, MMCR/PMC programming, BHRB branch stacks, EBB support, sampling data, PMU interrupts, CPU hotplug preparation, and registration of model-specific `struct power_pmu` backends.

## Important APIs, Types, And Functions

- `struct cpu_hw_events` holds per-CPU active events, event encodings, flags, computed MMCRs, limited-counter tracking, transaction state, BHRB state, and sampled PMC snapshots.
- `ppmu` is the registered model-specific `struct power_pmu`.
- Register helpers `read_pmc()`, `write_pmc()`, `write_mmcr0()`, `perf_read_regs()`, `perf_get_misc_flags()`, `perf_get_data_addr()`, and `perf_arch_instruction_pointer()` abstract PMC/MMCR/SIAR/SDAR/SIER behavior across CPU generations.
- BHRB helpers `power_pmu_bhrb_enable()`, `power_pmu_bhrb_disable()`, `power_pmu_sched_task()`, `power_pmu_bhrb_read()`, and `power_pmu_bhrb_to()` reset, configure, and export branch history.
- EBB helpers `is_ebb_event()`, `ebb_event_check()`, `ebb_event_add()`, `ebb_switch_out()`, and `ebb_switch_in()` validate exclusive per-task EBB events and context-switch user-visible PMU registers.
- Constraint and scheduling helpers `power_check_constraints()`, `check_excludes()`, `collect_events()`, `can_go_on_limited_pmc()`, and `normal_pmc_alternative()` decide if event groups fit hardware constraints and alternatives.
- PMU callbacks include `power_pmu_event_init()`, `power_pmu_add()`, `power_pmu_del()`, `power_pmu_start()`, `power_pmu_stop()`, `power_pmu_read()`, and transaction callbacks.
- Interrupt path functions `record_and_restart()`, `__perf_event_interrupt()`, and `perf_event_interrupt()` account overflows, generate samples, and restart counters.
- `register_power_pmu()` installs a model PMU and registers the generic `"cpu"` PMU.
- `init_ppc64_pmu()` probes model-specific PMUs then falls back to `init_generic_compat_pmu()`.

## Control Flow

Model drivers call `register_power_pmu()`, which sets `ppmu`, configures sysfs groups and capabilities, registers the perf PMU, and installs CPU hotplug preparation. Event initialization translates generic/cache/raw perf events through `ppmu`, checks blacklist and config validity, adjusts hypervisor exclusion, handles limited PMC alternatives, validates EBB and branch stack options, tests group constraints, reserves PMU hardware, and initializes period counters. Adding an event disables the PMU, appends the event, optionally checks constraints immediately or defers under transaction, enables BHRB if needed, and re-enables the PMU. Enabling recomputes MMCRs when events changed, moves counters if necessary, initializes PMCs, handles limited counters, configures BHRB and EBB, and unfreezes counters. Disabling freezes counters, clears pending PMI state, disables instruction sampling/BHRB, saves EBB user state, and clears SIAR/SDAR on capable CPUs. PMIs read all PMCs, identify overflows, account and restart events, handle POWER7 rollback quirks, restore MMCR0, and publish sample timing.

## State And Persistence

Runtime state is per-CPU in `cpu_hw_events`, global in `ppmu`, `freeze_events_kernel`, `num_events`, and `pmc_reserve_mutex`, and per-event in `event->hw`. EBB state persists in `current->thread` fields across context switches. BHRB context is tracked per CPU to avoid leaking branch entries between tasks. PMU hardware reservation is reference-counted by `num_events`.

## Dependencies And Integration Points

This file integrates deeply with Linux perf core, PowerPC SPR accessors, model PMU drivers (`power5` through `power11`, `ppc970`, generic compat), firmware feature detection, CPU hotplug, hard/soft IRQ handling, branch target decoding, BHRB assembly helper `read_bhrb()`, KVM/PMU in-use tracking, sysfs PMU attributes, and generic sample data APIs.

## Risks And Edge Cases

Risk concentrates around concurrency and hardware quirks: PMIs can behave like NMIs under soft-disabled interrupts; limited PMC5/6 counters do not respect freeze conditions; POWER7 can roll back speculative counts; POWER8E requires the PMAO restore workaround; SIAR/SIER validity varies across generations; Power10 privilege bits can be unreliable; BHRB can leak kernel or cross-task branch data if not reset/filtered; EBB has strict grouping semantics and user-visible register state; and event alternatives/constraints must match model-specific encodings exactly.

## Test Signals

Test signals include model-specific PowerPC perf selftests, `perf stat`/`perf record` for generic, raw, cache, branch-stack, and memory data source events; grouped event schedulability; EBB exclusive task events; limited PMC behavior; CPU hotplug; interrupt-heavy sampling; POWER7/POWER8E/POWER10 quirk coverage; sysfs event/caps exposure; and `perf_event_print_debug()` output on supported hardware. Build coverage should include PPC32 stubs and PPC64 Book3S configs.
