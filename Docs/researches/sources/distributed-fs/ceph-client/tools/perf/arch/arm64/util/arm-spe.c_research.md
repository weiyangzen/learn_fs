# sources/distributed-fs/ceph-client/tools/perf/arch/arm64/util/arm-spe.c

Purpose: ARM64 SPE perf recording support, including PMU defaults, AUX buffer sizing, CPU metadata, snapshot handling, and tracking events.

Important APIs/types/functions: `arm_spe_is_set_freq`, `arm_spe_info_priv_size`, `arm_spe_save_cpu_header`, `arm_spe_info_fill`, `arm_spe_snapshot_resolve_auxtrace_defaults`, `arm_spe_setup_evsel`, `arm_spe_setup_aux_buffer`, `arm_spe_setup_tracking_event`, `arm_spe_recording_options`, `arm_spe_parse_snapshot_options`, `arm_spe_snapshot_start`, `arm_spe_snapshot_finish`.

Control flow: Detects SPE aux events, rejects frequency mode, sets sample period and DATA_SRC/PHYS_ADDR bits, calculates AUX mmap/snapshot sizes, records per-CPU MIDR/caps, tracks wrap state for snapshots, and emits auxtrace metadata.

State and persistence behavior: No persistent runtime state is owned directly here; the durable effect is build metadata, generated ELF contents, perf.data metadata, or process-local helper state as described by the declarations.

Dependencies and integration points: Depends on perf PMU sysfs caps, CPU maps, record options, auxtrace callbacks, cpuid helpers, and page-size/privilege checks.

Risks: Snapshot wrap detection relies on zeroed buffers; min interval/capability reads may be absent; discard mode skips tracking setup.

Test signals: SPE record/report in full, discard, per-cpu, snapshot, privileged/unprivileged, and invalid frequency/mmap-size modes.

Source coverage: researched from the complete local file (695 lines, 18521 bytes).
