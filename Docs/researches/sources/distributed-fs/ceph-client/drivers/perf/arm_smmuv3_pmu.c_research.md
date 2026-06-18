# sources/distributed-fs/ceph-client/drivers/perf/arm_smmuv3_pmu.c

## Purpose
Perf PMU driver for ARM SMMUv3 Performance Monitor Counter Groups (PMCG). It exposes SMMU transaction events as uncore perf PMUs named from the PMCG physical address, supports optional StreamID filtering, handles MSI or wired interrupts, and migrates the perf context when the selected CPU goes offline.

## Important APIs, Types, And Functions
- `struct smmu_pmu` stores PMCG MMIO bases, supported event bitmap, active events, counter bitmap, IRQ, selected CPU, quirks, and perf PMU object.
- `smmu_pmu_probe()` maps resources, reads CFGR/CEID/IIDR, configures IRQ/MSI, resets hardware, applies ACPI quirks, registers CPUHP state and perf PMU.
- `smmu_pmu_event_init()` rejects wrong PMU types, sampling, per-task mode, unsupported events, mixed PMU groups, and incompatible global filters.
- `smmu_pmu_event_add/start/stop/del/read()` implement the perf lifecycle.
- `smmu_pmu_handle_irq()` clears overflow status, updates counts, and reloads periods.
- `smmu_pmu_apply_event_filter()` programs per-counter or global StreamID filtering.

## Control Flow
Probe allocates `smmu_pmu`, maps page 0 and optionally relocated counter page 1, reads supported events from CEID0/1, computes counter count and width, resets counters and interrupts, sets up MSI if advertised or requests a platform IRQ, creates a stable PMU name, applies ACPI model quirks, pins PMU context to the current CPU, registers hotplug migration, then registers with perf. Event add finds a free counter, programs filter registers, enables interrupt, and optionally starts the counter.

## State And Persistence
Runtime state lives in `struct smmu_pmu`: MMIO pointers, bitmaps, event slots, selected CPU, IRQ, counter mask, options, and global-filter flag. Hardware counter values and StreamID filter registers are live MMIO state only. There is no persistent state.

## Dependencies And Integration Points
The driver depends on platform devices from DT or ACPI/IORT, MMIO accessors, MSI domain helpers, IRQ affinity, CPU hotplug, perf uncore PMU APIs, sysfs PMU attributes, and PMCG architectural registers. ACPI platform data supplies HiSilicon PMCG model quirks.

## Risks
Sampling and task mode are unsupported by design; users must use CPU-wide counting. Global filter PMCGs require all grouped events to share filter configuration, so grouping may fail with `-EAGAIN` or `-EINVAL`. Read-only counters rely on large counter width to make missed wraps remote. HiSilicon disable quirks force invalid event types to stop counting. MSI setup silently falls back only if an IRQ is already available; no IRQ means probe failure. CPU hotplug migration must keep IRQ affinity and perf context aligned.

## Test Signals
Check `/sys/bus/event_source/devices/smmuv3_pmcg_*` for events, format, cpumask, and identifier. Run `perf stat -e smmuv3_pmcg_*/transaction/ -a`, filter-enabled StreamID events, incompatible global-filter groups, CPU offline migration, overflow interrupts, MSI and wired IRQ platforms, and ACPI HiSilicon quirk systems.
