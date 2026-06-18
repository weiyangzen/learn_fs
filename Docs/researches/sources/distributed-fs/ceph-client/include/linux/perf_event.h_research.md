<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/perf_event.h -->
# sources/distributed-fs/ceph-client/include/linux/perf_event.h

## Purpose
Defines the kernel-internal perf event API, PMU driver interface, event/context state, sample construction helpers, software-event hooks, callchain APIs, guest perf callbacks, cgroup perf data, sysfs attribute helpers, and disabled stubs for builds without `CONFIG_PERF_EVENTS`.

## Important APIs, Types, And Functions
- Sample/raw/branch data types include `struct perf_callchain_entry`, `perf_callchain_entry_ctx`, `perf_raw_frag`, `perf_raw_record`, and `perf_branch_stack`.
- `struct hw_perf_event` stores PMU-specific hardware, AUX, software, tracepoint, breakpoint, AMD/IOMMU, sampling-period, throttling, and frequency state.
- `struct pmu` is the central PMU driver callback table: `event_init`, `add`, `del`, `start`, `stop`, `read`, transaction callbacks, `event_idx`, scheduler hooks, AUX setup/free/snapshot, address-filter validation/sync, aux-output match, CPU filter, and period check.
- Event state/capability definitions include `enum perf_event_state`, `PERF_EF_*`, `PERF_HES_*`, `PERF_PMU_CAP_*`, `enum perf_pmu_scope`, and `PERF_EV_CAP_*`.
- `struct perf_event` stores list/tree membership, group state, PMU pointers, state, attach state, counts, timings, attributes, hardware state, contexts, refs, child/owner/mmap/ring-buffer/poll/pending work/filter/AUX/BPF/security/cgroup fields.
- Context types include `struct perf_event_pmu_context`, `perf_event_groups`, `perf_time_ctx`, `perf_event_context`, `perf_ctx_data`, `perf_cpu_pmu_context`, `perf_cpu_context`, and `perf_cgroup`.
- Public APIs cover PMU registration, task sched-in/out/init/exit/free hooks, kernel counter creation, context migration, local/read-value helpers, callchains, sample preparation/output, perf output buffers, software events, BPF/ksymbol/text-poke events, mmap/fork/comm/exec/namespaces hooks, security checks, address-filter sync, AUX output, enable/disable/period/pause, CPU hotplug, and sysfs event/format attributes.
- Inline helpers build sample data (`perf_sample_data_init()`, `perf_sample_save_callchain()`, `perf_sample_save_raw_data()`, `perf_sample_save_brstack()`), test branch-sample flags, determine software/exclusive/AUX/address-filter properties, and perform scheduler software-event hooks.

## Control Flow
Userspace or kernel code creates events through perf APIs, which choose a PMU and call `pmu->event_init()`. Events attach to task or CPU contexts, join groups, and are scheduled by context switch, CPU hotplug, cgroup, or explicit enable/disable logic. PMU callbacks add/start/read/stop/del hardware state. Overflow handlers construct `perf_sample_data`, optionally save callchains/raw/branch/AUX data, and output records to ring buffers. Software events use static keys to avoid overhead when disabled. Task scheduling hooks emit context-switch/migration/cgroup events and call PMU scheduler callbacks. Disabled builds replace most APIs with stubs returning no-op or `-EINVAL`.

## State And Persistence
Perf maintains persistent PMU registrations, per-task and per-CPU contexts, event groups, refcounted events, ring buffers, mmap state, pending IRQ/task work, address filters, BPF attachments, cgroup time accounting, callchain buffers, sysctl limits, static keys, and optional guest callback static calls. Hardware counter state persists in PMU registers while active and is synchronized into `local64_t count`, time-enabled, and time-running fields.

## Dependencies And Integration Points
The header ties together UAPI perf definitions, BPF perf events, architecture perf/event and local64 support, hardware breakpoints, lists, RCU, spinlocks, hrtimers, files, pid namespaces, workqueues, ftrace, CPU hotplug, irq_work, static keys/calls, atomics, sysfs, cgroups, refcounts, security hooks, lockdep, local counters, guest/KVM callbacks, and PMU-specific architecture drivers such as ARM and RISC-V.

## Risks And Edge Cases
Risks include incorrect PMU callback locking or IRQ/NMI assumptions, group transaction rollback bugs, event state transition errors, refcount/RCU lifetime mistakes, ring-buffer overflow/lost-sample accounting, raw fragment padding errors, sample size miscalculation, branch-stack truncation, cgroup/task context races, filter generation mismatches, AUX pause/resume concurrency, security/paranoid bypasses, and inconsistent disabled-stub behavior.

## Test Signals
Use perf selftests, `perf stat`, `perf record`, sampling overflow, grouped pinned/flexible events, CPU and task events, cgroup events, BPF perf events, tracepoints, hardware breakpoints, AUX tracing, address filters, callchains, branch stacks, CPU hotplug, task fork/exec/exit, mmap output, permission/paranoid checks, PMU unregister/revoke, and `CONFIG_PERF_EVENTS=n` build coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/perf_event.h -->
