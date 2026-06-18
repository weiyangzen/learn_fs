<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/platform/uv/uv_nmi.c -->
# sources/distributed-fs/ceph-client/arch/x86/platform/uv/uv_nmi.c

## Purpose
Implements UV system-wide NMI handling for dump, instruction-pointer summaries, health checks, kdump, kdb, and kgdb actions on very large systems.

## Important APIs, Types, And Functions
Important state includes per-CPU `uv_cpu_nmi`, hub `uv_hub_nmi_s` lists, global atomics, cpumasks, module parameters for action/timing/statistics, and hubless PCH registers. Entry points are `uv_nmi_setup()`, `uv_nmi_setup_hubless()`, `uv_nmi_init()`, `uv_handle_nmi()`, and `uv_handle_nmi_ping()`.

## Control Flow
Setup selects hub MMRs or hubless PCH GPIO routing, allocates per-node hub state, and registers NMI handlers. Primary NMI checks UV source, elects a master CPU, optionally attempts kdump, waits for CPUs while pinging missing ones with local NMIs, performs the selected action, clears hub/PCH NMI state, resets global atomics, and touches watchdogs. Ping handler catches CPUs whose first NMI was consumed by perf/local sources.

## State And Persistence
Module parameters expose counters and runtime action selection. Atomic/cpumask state coordinates each NMI episode. MMR/PCH register configuration persists while the system runs.

## Dependencies And Integration Points
Depends on APIC/NMI notifiers, UV hub MMR definitions, PCH memory mapping for hubless systems, kexec/kdump, kgdb/kdb, scheduler debug dumps, clocksource watchdog handling, and CPU topology.

## Risks And Edge Cases
NMI context forbids sleeping and makes locking/counter ordering fragile. Large CPU counts require careful timeouts and ping retries. Kdump can fail and must fall back. Hubless PCH register programming is hardware-revision-sensitive.

## Test Signals
Manual UV NMI action tests, module counters (`nmi_count`, misses, ping counts), stack/IP dumps from all CPUs, successful kdump/kdb/kgdb action where configured, and no NMI lockups validate behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/platform/uv/uv_nmi.c -->
