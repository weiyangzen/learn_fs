# sources/distributed-fs/ceph-client/include/trace/events/power_cpu_migrate.h

Purpose: Defines a trace event for CPU migration decisions tied to power/performance balancing. It exposes source CPU, destination CPU, and load information.

Important APIs/types/functions: `DECLARE_EVENT_CLASS(cpu_migrate)` and the derived migration event record `src_cpu`, `dest_cpu`, and load. The trace system is `power`.

Control flow: Scheduler or power-aware migration code emits the event when a task/load decision moves work between CPUs. The trace entry captures the migration endpoints and load metric used by the caller.

State and persistence: No state is owned. It observes scheduler CPU/load state at a decision point.

Dependencies and integration points: Depends on tracepoints and integrates with scheduler energy-aware scheduling, CPU topology, cpufreq/cpuidle analysis, and power tracing.

Risks and test signals: Risks include ambiguous load units, missing task identity, and high volume on migration-heavy workloads. Test CPU hotplug, schedutil/EAS workloads, asymmetric CPU capacity systems, migration stress, and tracing with scheduler latency tools.

Source-read signal: read `sources/distributed-fs/ceph-client/include/trace/events/power_cpu_migrate.h` completely for this pass (68 lines, 1625 bytes). Final split target: `Docs/researches/sources/distributed-fs/ceph-client/include/trace/events/power_cpu_migrate.h_research.md`.
