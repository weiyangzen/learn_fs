# Research: subset-b-005021

Grouped research for ARM perf PMU sources. Each section title preserves the original source path and is wrapped for reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/perf/arm_pmu.c -->
# sources/distributed-fs/ceph-client/drivers/perf/arm_pmu.c

## Purpose
Common ARM CPU PMU perf core. It provides the `struct pmu` callbacks shared by ARMv5/v6/v7/v8 CPU PMU implementations, including event initialization, counter allocation validation, start/stop/read/add/delete handling, counter period accounting, IRQ/NMI request/free, CPU hotplug reset, and CPU power-management save/restore.

## Important APIs, Types, And Functions
- `armpmu_alloc()`, `armpmu_free()`, and `armpmu_register()` allocate `struct arm_pmu`, per-CPU `struct pmu_hw_events`, install common PMU callbacks, register CPU hotplug and CPU PM notifiers, then call `perf_pmu_register()`.
- `armpmu_map_event()` maps perf hardware, cache, raw, and PMU-specific event encodings through architecture-specific maps.
- `armpmu_event_set_period()` and `armpmu_event_update()` are the central counter accounting helpers used by all CPU PMU IRQ handlers.
- `armpmu_add()`, `armpmu_del()`, `armpmu_start()`, `armpmu_stop()`, and `armpmu_read()` implement the perf event lifecycle.
- `armpmu_request_irq()` and `armpmu_free_irq()` select normal IRQ, NMI, percpu IRQ, or percpu NMI operations through `struct pmu_irq_ops`.
- `arm_perf_starting_cpu()` and `arm_perf_teardown_cpu()` are CPUHP callbacks; `cpu_pm_pmu_notify()` handles CPU low-power entry and exit.

## Control Flow
Architecture drivers call `armpmu_alloc()`, fill hardware callbacks and supported CPU/counter masks, request IRQs, then call `armpmu_register()`. Perf opens call `armpmu_event_init()`, which rejects unsupported CPUs and branch-stack requests without BRBE, maps the event, installs filters, and validates groups against a fake PMU allocation. Scheduling calls `armpmu_add()`, which allocates an index with the hardware-specific `get_event_idx()` and optionally starts the event. IRQ delivery enters `armpmu_dispatch_irq()`, dereferences the per-CPU `arm_pmu *`, invokes the hardware handler, and reports handler latency to perf.

## State And Persistence
Runtime state is per CPU in `pmu->hw_events`: active events, used counter bitmap, IRQ number, branch-stack users, and per-CPU back-pointers. Global static state tracks requested IRQs (`cpu_irq`, `cpu_irq_ops`) and whether any PMU uses NMIs (`has_nmi`). No durable storage exists; all state is reconstructed on probe and hotplug. Counter values persist only in perf event atomics and hardware registers.

## Dependencies And Integration Points
This file depends on Linux perf core, CPU hotplug, CPU PM, IRQ/NMI APIs, KVM PMU host hooks, cpumask/topology helpers, and architecture-specific callbacks installed by files such as `arm_pmuv3.c`, `arm_v7_pmu.c`, `arm_v6_pmu.c`, and `arm_xscale_pmu.c`. The sysfs `cpus` attribute exposes supported CPUs for heterogeneous systems.

## Risks
IRQ handling is delicate: shared PPIs must only be freed when the last CPU user is gone, and NMI fallback must match the free/disable operation. Period programming intentionally caps periods to half counter width to reduce missed wraps, but extreme IRQ latency can still affect counts. CPU PM and hotplug reset paths must run on supported CPUs or stale PMU registers may corrupt subsequent samples. Group validation uses a fake bitmap and depends on architecture-specific `get_event_idx()` behavior being side-effect-free except for the passed bitmap.

## Test Signals
Useful signals include boot logs showing `enabled with ... PMU driver`, `/sys/bus/event_source/devices/<pmu>/cpus`, perf stat/counting on each supported CPU, sampling overflow delivery, CPU hotplug cycles, suspend/resume or CPU idle transitions with active events, heterogeneous CPU rejection tests, and IRQ/NMI registration failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/perf/arm_pmu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/perf/arm_pmu_acpi.c -->
# sources/distributed-fs/ceph-client/drivers/perf/arm_pmu_acpi.c

## Purpose
ACPI discovery glue for ARM CPU PMUs and related per-CPU tracing devices. It parses MADT GICC PMU interrupt fields, requests per-CPU PMU IRQs before PMU registration, associates CPUs with homogeneous PMU instances by MIDR, and opportunistically creates ACPI platform devices for SPE and TRBE when their MADT interrupt fields are present.

## Important APIs, Types, And Functions
- `arm_pmu_acpi_probe()` is the exported entry used by the PMUv3 driver on ACPI systems.
- `arm_pmu_acpi_parse_irqs()` walks possible CPUs, converts GICC performance interrupt GSIs to Linux IRQs, and calls `armpmu_request_irq()`.
- `arm_pmu_acpi_associate_pmu_cpu()` records `probed_pmus` and fills per-CPU IRQ fields in the PMU's `hw_events`.
- `arm_pmu_acpi_cpu_starting()` is a CPUHP callback that associates late-starting CPUs before common PMU hotplug code runs.
- `arm_acpi_register_pmu_device()` registers homogeneous SPE/TRBE platform devices using ACPI GSI fields.

## Control Flow
`arm_pmu_acpi_probe()` first parses all PMU IRQs, then registers an ACPI-specific CPUHP startup state. It scans online CPUs, skips CPUs already associated with a PMU, allocates an `arm_pmu`, records the current CPU MIDR in `pmu->acpi_cpuid`, associates all online CPUs with the same MIDR, calls the architecture init function, gives each PMU a unique suffix, and registers it with `armpmu_register()`. SPE/TRBE registration happens earlier from `subsys_initcall(arm_pmu_acpi_init)`.

## State And Persistence
Per-CPU static variables `probed_pmus` and `pmu_irqs` store ACPI PMU ownership and IRQ numbers. State is runtime-only and rebuilt on boot. PMU names are dynamically allocated with `kasprintf()` for multiple heterogeneous PMUs.

## Dependencies And Integration Points
The file integrates ACPI MADT/GICC parsing, ACPI GSI registration, CPU topology heterogeneity IDs, common `arm_pmu.c` IRQ helpers, PMUv3 initialization, and platform-device registration for `ARMV8_SPE_PDEV_NAME` and `ARMV8_TRBE_PDEV_NAME`.

## Risks
The code assumes homogeneous interrupt layouts for SPE/TRBE and currently requires at least one CPU of a PMU class to be online during probe. GSI zero is rejected pragmatically despite being spec-valid. Error paths after allocation can leak some previously allocated PMUs or names because this probe path mostly returns immediately on failures. PPI mismatch detection prevents unsafe mixed IRQ layouts, but bad firmware can still leave CPUs unassociated.

## Test Signals
ACPI boot with PMUv3 should show PMU registration and no `Unable to associate CPU` warnings. Validate `/sys/bus/event_source/devices/armv8_pmuv3_*`, perf on heterogeneous ACPI systems, CPU hotplug association, invalid or zero GSI handling, and ACPI SPE/TRBE platform device creation when MADT fields are present.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/perf/arm_pmu_acpi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/perf/arm_pmu_platform.c -->
# sources/distributed-fs/ceph-client/drivers/perf/arm_pmu_platform.c

## Purpose
Device-tree/platform probing helper for ARM CPU PMU drivers. It allocates a common `arm_pmu`, parses PMU IRQ topology and optional interrupt affinity, invokes either OF match init callbacks or CPU-ID probe tables, requests per-CPU IRQs, and registers the PMU with perf.

## Important APIs, Types, And Functions
- `arm_pmu_device_probe()` is the public platform probe helper used by ARMv6, ARMv7, ARMv8, and XScale drivers.
- `pmu_parse_irqs()` supports no-IRQ PMUs, single percpu PPI PMUs, and per-CPU SPI IRQ lists.
- `pmu_parse_irq_affinity()` reads `interrupt-affinity` CPU phandles when present.
- `probe_current_pmu()` reads the current CPU ID and matches `struct pmu_probe_info` entries for non-DT-detailed legacy platforms.
- `armpmu_request_irqs()` and `armpmu_free_irqs()` wrap common IRQ request/free per supported CPU.

## Control Flow
Platform drivers call `arm_pmu_device_probe()` from their `.probe`. The helper allocates and initializes `arm_pmu`, stores the platform device, parses IRQs and supported CPUs, resolves an init function from OF match data or a probe table, applies `secure-reg-access` for 32-bit systems, calls hardware init, requests IRQs for all supported CPUs, and finally calls `armpmu_register()`. Failures unwind IRQs and free the PMU.

## State And Persistence
The helper fills `pmu->supported_cpus`, per-CPU `hw_events->irq`, `pmu->plat_device`, `pmu->secure_access`, and `pmu->pmu.parent`. State is all runtime probe state; no persistent configuration is written.

## Dependencies And Integration Points
It depends on platform IRQ APIs, OF match data, `interrupt-affinity` bindings, `irq_is_percpu_devid()`, common `arm_pmu.c` IRQ registration, and architecture init callbacks from the hardware-specific PMU files.

## Risks
Missing `interrupt-affinity` on SMP triggers fallback to logical CPU order, which is explicitly fragile. Multiple PPIs, mixed PPI/SPI layouts, duplicate CPU IRQ mappings, or invalid phandles fail probe. No-IRQ mode sets `PERF_PMU_CAP_NO_INTERRUPT`, so counting can work but sampling cannot. ARM64 ignores `secure-reg-access`, so firmware relying on that property would not get secure debug access.

## Test Signals
Use DT systems with no IRQ, one PPI, and per-CPU SPI layouts. Check warnings for missing affinity, duplicate IRQs, or mismatched PPIs; verify perf sampling fails cleanly with no IRQ; verify `/sys/.../cpus` matches affinity; and confirm error unwind leaves no requested IRQs after failed probe.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/perf/arm_pmu_platform.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/perf/arm_pmuv3.c -->
# sources/distributed-fs/ceph-client/drivers/perf/arm_pmuv3.c

## Purpose
ARMv8/ARMv9 PMUv3 hardware driver. It supplies PMUv3 event maps, sysfs event/format/capability attributes, register accessors, overflow handling, event filtering, branch-record support, user-space counter read support, KVM coordination, PMUv3 feature probing, ACPI/DT driver registration, and mmap user page time/counter metadata.

## Important APIs, Types, And Functions
- `armv8_pmu_init()` installs the hardware callbacks into `struct arm_pmu`.
- `armv8pmu_probe_pmu()` and `__armv8pmu_probe_pmu()` read PMU version, PMCR counter count, PMCEID bitmaps, PMMIR, instruction counter support, and BRBE support.
- `armv8pmu_handle_irq()` clears overflow flags, stops the PMU, updates/reloads overflowing events, saves BRBE stacks when requested, and restarts the PMU.
- `armv8pmu_get_event_idx()` chooses the cycle counter, instruction counter, a single programmable counter, or a chained pair.
- `armv8pmu_set_event_filter()` encodes EL filters, guest/host filters, branch-stack validation, and threshold controls.
- `arch_perf_update_userpage()` exports rdpmc and arch timer conversion data to perf mmap pages.

## Control Flow
On DT, `armv8_pmu_driver_init()` registers a platform driver; on ACPI, it calls `arm_pmu_acpi_probe()`. Probe invokes common platform/ACPI code, then PMUv3 init probes hardware on a supported CPU, allocates per-CPU BRBE stacks if available, installs callbacks, and registers sysfs groups. Event init maps common architectural events if PMCEID advertises them, falls back to implementation-specific cache maps, rejects standalone chain events, and handles user-read constraints. Scheduling starts counters by programming event type, IRQ enable, KVM event masks, and counter enable registers.

## State And Persistence
Important runtime state is stored in `struct arm_pmu`: `pmuver`, `cntr_mask`, `pmceid_bitmap`, `pmceid_ext_bitmap`, `reg_pmmir`, BRBE metadata, and callback pointers. Global `sysctl_perf_user_access` controls user-space direct counter access and is exposed under `kernel/perf_user_access`. Hardware registers hold live counter configuration; no durable state exists.

## Dependencies And Integration Points
This file integrates Linux perf, PMUv3 sysregs from `asm/perf_event.h` and `linux/perf/arm_pmuv3.h`, KVM host/guest PMU hooks, BRBE (`arm_brbe.h`), arch timer/sched_clock user-page metadata, CPU feature helpers, ACPI/OF platform probing, lockup detector retry, and common `arm_pmu.c`.

## Risks
Counter selection has many architectural constraints: chained 64-bit counters require adjacent pairs, user-readable events cannot be chained, PMCCNTR is avoided for thresholds, branch stacks, and SMT, and PMICNTR is not exposed to userspace. User access must clear or restrict unused counters to avoid leaking data. Threshold and branch filters depend on feature registers. KVM deferred counters require correct host/guest synchronization. IRQ handling stops and restarts the whole PMU, so bugs can skew event groups.

## Test Signals
Run perf stat and perf record on PMUv3 systems, including raw events, common PMCEID-visible events, implementation cache events, 64-bit `long` events, user `rdpmc`, threshold formats, BRBE branch stacks, KVM guest/host filtered events, CPU hotplug, and heterogeneous PMUs. Inspect sysfs `events`, `format`, `caps`, `cpus`, and `kernel/perf_user_access` behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/perf/arm_pmuv3.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/perf/arm_smmuv3_pmu.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/perf/arm_smmuv3_pmu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/perf/arm_spe_pmu.c -->
# sources/distributed-fs/ceph-client/drivers/perf/arm_spe_pmu.c

## Purpose
Perf AUX trace driver for ARM Statistical Profiling Extension (SPE). It exposes per-CPU SPE profiling as `arm_spe_N` PMUs, configures SPE sampling/filter registers from perf attributes, manages AUX buffers, handles buffer management interrupts, probes SPE feature registers, and participates in CPU hotplug.

## Important APIs, Types, And Functions
- `struct arm_spe_pmu` tracks supported CPUs, PPI IRQ, PMS version, feature flags, minimum interval, counter size, max record size, alignment, and per-CPU perf output handles.
- `arm_spe_pmu_event_init()` validates perf attributes against probed SPE features and privilege requirements.
- `arm_spe_pmu_start()` programs buffer pointers, filter registers, interval registers, and enables profiling.
- `arm_spe_pmu_stop()` disables profiling, drains trace, finalizes AUX output, and saves interval count.
- `arm_spe_pmu_setup_aux()` and `arm_spe_pmu_free_aux()` map/unmap perf AUX pages.
- `arm_spe_pmu_irq_handler()` handles PMBSR buffer events and resumes or stops profiling.
- `__arm_spe_pmu_dev_probe()` reads PMBIDR/PMSIDR and records feature capability state.

## Control Flow
Probe rejects KPTI configurations where the profiling buffer is inaccessible from EL0, allocates per-CPU handles, parses a percpu PPI and its affinity, probes hardware on a supported CPU, requests the percpu IRQ, registers CPU hotplug setup, and registers the perf PMU. Perf creates AUX buffers via `setup_aux`, then event start opens an AUX output session, aligns and limits buffer space, writes PMBPTR/PMBLIMITR, configures filters and sampling interval, and enables PMSCR. Buffer-full interrupts finalize the current AUX region, run perf IRQ work, then reopen output unless truncated.

## State And Persistence
Driver state is in `struct arm_spe_pmu` and per-event `hw` fields. AUX buffer metadata is `struct arm_spe_pmu_buf` with vmapped pages and snapshot mode. Hardware state is held in SPE sysregs and reset on CPU startup/teardown. No durable state exists.

## Dependencies And Integration Points
The driver integrates perf AUX/ITRACE support, ARM64 sysregs, cpufeature checks, percpu IRQ affinity, CPU hotplug, vmalloc/vmap, capability checks (`perf_allow_kernel()`), optional ACPI-created platform devices, and DT compatible `arm,statistical-profiling-extension-v1`.

## Risks
Buffer management is high risk: head alignment, snapshot half-buffer limits, wakeup boundaries, padding, truncation, collision flags, and fatal PMBSR syndromes all affect trace parsability. Frequency-based sampling is rejected; callers must use explicit periods. Filter attributes are feature-gated, and physical address or physical timestamp collection requires kernel permission. KPTI can make profiling buffers inaccessible. IRQ handling must disable and drain on fatal faults to avoid repeated exceptions.

## Test Signals
Validate `arm_spe_*` sysfs `caps`, `format`, and `cpumask`; `perf record -e arm_spe_*/.../ --aux-buffer` in normal and snapshot mode; tiny/odd AUX buffer rejection; feature-gated filters; discard mode; collision/truncation flags under pressure; CPU hotplug; and KPTI refusal messaging.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/perf/arm_spe_pmu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/perf/arm_v6_pmu.c -->
# sources/distributed-fs/ceph-client/drivers/perf/arm_v6_pmu.c

## Purpose
ARMv6 CPU PMU hardware implementation for ARM1136 and ARM1176. It maps generic perf events to ARMv6 event numbers, accesses CP15 PMU registers, handles three counters, and plugs hardware callbacks into the common ARM PMU core.

## Important APIs, Types, And Functions
- Event maps `armv6_perf_map` and `armv6_perf_cache_map` translate generic perf events to ARMv6 encodings.
- `armv6_pmcr_read()` and `armv6_pmcr_write()` access the PMCR.
- `armv6pmu_read_counter()` and `armv6pmu_write_counter()` access cycle, counter0, and counter1 registers.
- `armv6pmu_enable_event()` and `armv6pmu_disable_event()` program event select and interrupt bits.
- `armv6pmu_handle_irq()` processes overflow flags and calls common period/update helpers.
- `armv6pmu_get_event_idx()` reserves the cycle counter for CPU cycles and two event counters for other events.
- `armv6_1136_pmu_init()` and `armv6_1176_pmu_init()` install callbacks and names.

## Control Flow
The built-in platform driver matches `arm,arm1176-pmu` or `arm,arm1136-pmu` and calls `arm_pmu_device_probe()`. Hardware init fills the callback table and counter mask. Perf add chooses an index through common core; start reloads the period and calls `armv6pmu_enable_event()`. IRQ reads PMCR, writes it back to clear overflow flags, updates each overflowing active event, reloads its period, raises perf overflow, and runs pending IRQ work.

## State And Persistence
State is mostly common `arm_pmu` per-CPU event state plus PMCR event select, interrupt enable, and overflow bits. The file has no durable state. ARMv6 counters cannot be individually stopped; disabled programmable counters are switched to the NOP-like ETM external output event and their interrupts disabled.

## Dependencies And Integration Points
It depends on CP15 access, `asm/irq_regs.h`, platform/OF matching, generic perf event maps and common ARM PMU helpers from `arm_pmu.c`.

## Risks
The hardware cannot individually disable counters, so disabled counters may still physically count unless pointed at the expected inactive event. The cycle counter cannot be independently stopped, so interrupt masking and period reload are used to ignore stale counts. Cache mappings combine read/write accesses because the hardware cannot distinguish them. NMI-delivered PMU interrupts are called out as incompatible with `irq_work_run()` assumptions.

## Test Signals
On ARM1136/1176 DT systems, validate driver registration, three counters in the boot log, `perf stat` for cycles/instructions/branches/cache misses, sampling overflow, counter exhaustion with groups larger than three, and behavior after CPU hotplug or reset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/perf/arm_v6_pmu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/perf/arm_v7_pmu.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/perf/arm_v7_pmu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/perf/arm_xscale_pmu.c -->
# sources/distributed-fs/ceph-client/drivers/perf/arm_xscale_pmu.c

## Purpose
ARMv5 XScale PMU driver for XScale PMU architecture v1 and v2. It maps perf events to XScale encodings, accesses coprocessor 14 PMU registers, handles v1 three-counter and v2 five-counter layouts, and probes by CPU ID rather than OF match data.

## Important APIs, Types, And Functions
- `xscale_perf_map` and `xscale_perf_cache_map` translate generic events.
- XScale1 callbacks include `xscale1pmu_handle_irq()`, `xscale1pmu_enable_event()`, `xscale1pmu_disable_event()`, `xscale1pmu_get_event_idx()`, and counter read/write helpers.
- XScale2 callbacks include separate PMNC, overflow flag, event select, interrupt enable, and five-counter read/write helpers.
- `xscale_map_event()` delegates to `armpmu_map_event()`.
- `xscale_pmu_probe_table` matches `ARM_CPU_XSCALE_ARCH_V1` and `ARM_CPU_XSCALE_ARCH_V2`.

## Control Flow
The built-in platform driver invokes `arm_pmu_device_probe()` with no OF table and an XScale CPU-ID probe table. `probe_current_pmu()` matches the current CPU and calls the v1 or v2 init function. Perf scheduling uses v1 allocation for cycle/counter0/counter1, while v2 reuses that logic then adds counter3 and counter2. IRQ handlers disable the PMU, read overflow status, update and reload overflowing events through common helpers, run IRQ work, and re-enable the PMU.

## State And Persistence
State is held in common per-CPU PMU structures plus XScale PMNC/event-select/interrupt/overflow registers. XScale1 stores event select fields in PMNC; XScale2 uses separate registers. No persistent state exists.

## Dependencies And Integration Points
The file depends on ARM CPU ID definitions, coprocessor 14 inline assembly, platform probing, OF-independent CPU probe tables, and common ARM PMU callbacks from `arm_pmu.c`.

## Risks
XScale1 has an A-stepping erratum where a second overflow can clear a previous overflow bit; the driver documents no workaround. Some macros for reset use names that appear inherited and must match included definitions at compile time. IRQ handlers return `IRQ_NONE` after disabling the PMU if no overflow is found, so spurious interrupts rely on later paths to re-enable only when handled. Cache mappings are limited and approximate. XScale2 counter allocation order is unusual, preferring counter3 before counter2 after v1 counters.

## Test Signals
On XScale v1/v2 hardware, validate CPU-ID probe, reported counter count, `perf stat` for cycles/instructions/cache/TLB events, overflow sampling, groups exceeding available counters, spurious interrupt behavior, and raw event masking to 8-bit values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/perf/arm_xscale_pmu.c -->
