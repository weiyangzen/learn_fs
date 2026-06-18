# sources/distributed-fs/ceph-client/drivers/perf/arm_v7_pmu.c

## Purpose
ARMv7 CPU PMU hardware driver covering Cortex-A5/A7/A8/A9/A12/A15/A17 plus Qualcomm Krait and Scorpion variants. It provides event/cache maps, sysfs event/format attributes, CP15 register access, overflow handling, PMUv2 privilege filters, counter probing, and vendor-specific event-region programming.

## Important APIs, Types, And Functions
- Multiple `*_perf_map` and `*_perf_cache_map` tables encode CPU-specific event mappings.
- `armv7pmu_read_counter()`, `armv7pmu_write_counter()`, `armv7pmu_enable_event()`, `armv7pmu_disable_event()`, `armv7pmu_handle_irq()`, `armv7pmu_get_event_idx()`, and `armv7pmu_reset()` are the generic ARMv7 callback set.
- `armv7pmu_set_event_filter()` encodes PMUv2 exclude-user/kernel/hypervisor fields.
- `armv7_probe_num_events()` reads PMNC counter count on a supported CPU.
- Krait/Scorpion helpers program PMRESR/LPM/Venum registers and add constraint bits to `used_mask`.
- `armv7_pmu_of_device_ids` maps DT compatible strings to init functions.

## Control Flow
The platform driver calls `arm_pmu_device_probe()`, which invokes the matched init function. Generic ARMv7 init installs callbacks, event maps, sysfs groups, optional filters, and probes available counters. Perf event setup maps events and optionally installs filters. Scheduling reserves the dedicated cycle counter for CPU cycles and programmable counters for other events. Overflow IRQ reads and clears PMNC flags, updates/reloads each overflowing event, calls perf overflow, and runs IRQ work. Krait/Scorpion override enable/disable/reset/index paths to program auxiliary event-selection regions.

## State And Persistence
Common per-CPU PMU state tracks active events and counter allocation. Hardware state is PMNC, selected counter registers, event type registers, interrupt enable registers, overflow flags, secure debug enable, and vendor PMRESR/LPM/Venum registers. No durable state is written.

## Dependencies And Integration Points
The driver integrates CP15 PMU registers, VFP/CPACR access for Venum events, OF platform probing, common ARM PMU core, perf sysfs event attributes, and Qualcomm DT properties such as `qcom,no-pc-write`.

## Risks
Event maps are CPU-specific and sometimes approximate because older PMUs do not distinguish read/write accesses. Secure register access modifies SDER for non-invasive debug. Krait/Scorpion constraints reuse `used_mask` bits beyond hardware counters; mistakes can allow conflicting region/group events. Venum programming temporarily enables CP10/CP11 and FPEXC and requires non-preemptible context. Cycle counter event filtering differs between generic, Krait, and Scorpion paths. IRQ work has the same non-NMI caveat as older PMU handlers.

## Test Signals
Validate each compatible string on matching hardware or emulation, sysfs PMUv1 versus PMUv2 event groups, counter-count probing, exclude_user/exclude_kernel filters on PMUv2 cores, Krait `qcom,no-pc-write`, raw Krait/Scorpion region events with conflict groups, overflow sampling, and CPU hotplug reset.
