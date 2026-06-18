## `sources/distributed-fs/ceph-client/arch/x86/events/zhaoxin/core.c`

Purpose: implements the Zhaoxin PMU backend, modeled after Intel Architectural PerfMon v2 but with ZXC/ZXD/ZXE-specific event maps, fixed-counter constraints, overflow acknowledgement, and cache-event tables.

Important APIs and functions: `zhaoxin_pmu_init()` detects supported CPUID version/family/model and populates global `x86_pmu`. Runtime callbacks include `zhaoxin_pmu_handle_irq()`, `zhaoxin_pmu_enable_all()`, `disable_all()`, `enable_event()`, `disable_event()`, `event_map()`, and `get_event_constraints()`. Static maps define generic perf events and cache event encodings for ZXD/ZXE.

Control flow: init requires architectural perfmon CPUID leaf 10, version 2, and known Zhaoxin family/model. ZXC disables several generic events and uses special status-clear behavior requiring global control to be enabled. ZXD/ZXE install cache maps and branch event encodings. IRQ handling disables all counters, reads global overflow status, acknowledges status, ignores condition-changed bit 63, updates and reloads each active overflowing event, invokes `perf_event_overflow()`, loops while status remains, then reenables counters.

State and persistence: global `x86_pmu` and shared `hw_cache_event_ids` are initialized at boot. Hardware state lives in Zhaoxin performance MSRs, global control/status/overflow-control registers, fixed counter control, and per-event `hw_perf_event` state.

Dependencies and integration points: depends on shared x86 perf scheduling and counter update code, APIC perf NMIs, CPUID model data, MSR helpers, and sysfs format/event display from `perf_event.h`.

Risks: event encodings and constraints are model-specific; wrong tables produce misleading counts or unusable fixed counters. ZXC acknowledgement ordering is special. IRQ loops must avoid losing overflow bits while preventing repeated false handling of bit 63.

Test signals: boot on ZXC/ZXD/ZXE reports the selected event family; `perf stat` for cycles/instructions/cache/branch events; overflow sampling; fixed counter use; CPUID-unavailable events hidden through the quirk.
