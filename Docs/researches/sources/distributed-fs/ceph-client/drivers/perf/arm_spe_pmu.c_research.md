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
