<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/devfreq/event/exynos-ppmu.c -->
# sources/distributed-fs/ceph-client/drivers/devfreq/event/exynos-ppmu.c

Purpose: registers Samsung Exynos PPMU v1.1 and v2.0 performance monitor blocks as devfreq-event providers, usually for bus or memory utilization sampling.

Important APIs and control flow: `exynos_ppmu_probe()` parses MMIO and clock resources, discovers child `events` nodes, allocates a descriptor per event, registers devfreq-event devices, and enables the optional `ppmu` clock. Event names map through `ppmu_events[]` to one of four hardware counters. v1 callbacks `exynos_ppmu_set_event()`, `exynos_ppmu_get_event()`, and `exynos_ppmu_disable()` enable the cycle counter plus selected PM counter, program event type, reset counters, sample `CCNT` and PM counter values, then disable the selected counter. v2 callbacks reset more registers, program `PPMU_V2_CH_EVx_TYPE`, use manual start mode, and handle the wider counter 3 high/low pair.

State and persistence behavior: per-controller state includes regmap, clock, ppmu type, descriptor array, event-device array, and event count. Individual event state is mostly descriptor data (`name`, `event_type`, ops, driver_data). Hardware counters are reset on `set_event` and sampled on `get_event`; no software accumulation is kept.

Dependencies and integration points: depends on devfreq-event core, `exynos-ppmu.h`, regmap-mmio, DT child nodes under `events`, optional `event-name` and `event-data-type` properties, OF compatibles `samsung,exynos-ppmu` and `samsung,exynos-ppmu-v2`, and consumers such as Exynos bus. `MODULE_SOFTDEP` in Exynos bus expects this provider to load first.

Risks and test signals: unknown child names are skipped but `info->num_events` remains the original child count, leaving trailing zero descriptors that can fail registration. v2 `set_event()` does not explicitly reject a negative ID before shifting. The clock is enabled after event-device registration. `exynos_ppmu_v2_get_event()` returns success if reading `PPMU_V2_CNTENC` fails. Test signals include DTs with all valid event children, v1 and v2 counter reads, default event data type selection, skipped unknown child behavior, counter 3 high/low handling, clocked register access, and consumer utilization values under generated traffic.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/devfreq/event/exynos-ppmu.c -->
