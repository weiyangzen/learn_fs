# sources/distributed-fs/ceph-client/include/trace/events/timer_migration.h

Purpose: Instruments timer migration hierarchy behavior, including group setup, CPU/group connection, idle transitions, event updates, and remote timer handling.

Important APIs/types/functions: Defines templates `tmigr_group_set`, `tmigr_connect_child_parent`, `tmigr_connect_cpu_parent`, `tmigr_group_and_cpu`, `tmigr_cpugroup`, `tmigr_idle`, plus events such as `tmigr_cpu_new_timer`, `tmigr_cpu_active`, `tmigr_cpu_online`, `tmigr_cpu_offline`, `tmigr_cpu_idle`, `tmigr_cpu_new_timer_idle`, `tmigr_update_events`, and `tmigr_handle_remote`.

Control flow: Timer migration code emits records as CPUs enter/exit idle, join or leave groups, enqueue migratable timers, and process remote expiry decisions. Event templates capture group pointer/topology, CPU id, wake-up state, nextevt, expiry, and active/idle masks.

State/persistence: This header does not maintain migration state; it samples hierarchy state into trace buffers.

Dependencies/integration: Depends on timer migration internal structs and the trace event generator; used by NO_HZ and power-management diagnostics.

Risks: Tracepoint fields mirror internal hierarchy structures, so refactors can silently desynchronize field meaning. CPU hotplug and idle paths require low-overhead, race-tolerant reads.

Test signals: Build with timer migration enabled; exercise CPU hotplug, idle, and timer migration workloads and verify coherent parent/child and remote-event traces.
