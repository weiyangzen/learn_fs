# sources/distributed-fs/ceph-client/arch/s390/kernel/perf_cpum_cf.c

Purpose: implements s390 CPU Measurement Counter Facility support for perf (`cpum_cf`), complete counter-set diagnostic sampling (`cpum_cf_diag`), and the `/dev/hwctr` ioctl interface.

Important APIs and state: `struct cpu_cf_events` holds per-CPU refcounts, counter-set reference counts, perf state, device state, flags, and page buffers for start/stop/data. Global `cpu_cf_root` anchors per-CPU pointers; `pmc_reserve_mutex` serializes perf allocation/removal; `cfset_ctrset_mutex`, `cfset_session`, and `cfset_opencnt` serialize `/dev/hwctr`. PMUs are `cpumf_pmu` and `cf_diag`; the misc device is `cfset_dev`.

Control flow: init queries CPU-MF info with `qctri()`, derives counter-set sizes, clears problem-state extraction auth, registers measurement-alert external IRQ, creates s390dbf, registers the perf PMU, optional `/dev/hwctr`, diagnostic PMU, and CPU hotplug state. Perf event init maps hardware/raw events to counter sets, validates authorization/version, and allocates per-CPU structures. PMU enable/disable writes LCCTL state; start/stop updates counter-set activation, snapshots ECCTR or full counter sets, computes deltas, and pushes raw samples for CF_DIAG.

Device behavior: `/dev/hwctr` open requires `perfmon_capable()`, allocates all online CPUs on first open, START copies a user cpumask and counter-set mask, starts sets on requested CPUs, READ extracts complete sets to user buffers, STOP/release deactivates and frees sessions. CPU hotplug extends or shrinks active device sessions.

Dependencies and integration: uses CPU-MF instructions `lcctl`, `ecctr`, `stcctm`, `qctri`, measurement-alert external interrupts, perf core, miscdevice, CPU hotplug, debug feature, irq subclass control, and user ABI structs from `asm/hwctrset.h`.

Risks and test signals: authorization changes, hotplug races, shared perf/device state, buffer sizing, user copy bounds, and counter wrap handling are key. Test perf raw/hardware events, exclude modifiers, CF_DIAG raw samples, `/dev/hwctr` START/READ/STOP, CPU hotplug with active sessions, measurement alerts, SMT MT-diagnostic counters, and machines with varying counter versions.
