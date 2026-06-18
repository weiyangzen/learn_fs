# sources/distributed-fs/ceph-client/tools/perf/arch/s390/util/auxtrace.c

Purpose: Architecture auxtrace recorder setup for perf, selecting PMU trace events and filling AUXTRACE metadata.

Important APIs/types/functions: `cpumsf_free`, `cpumsf_info_priv_size`, `cpumsf_info_fill`, `cpumsf_recording_options`, `cpumsf_parse_snapshot_options`, `PERF_EVENT_CPUM_SF`, `PERF_EVENT_CPUM_SF_DIAG`, `DEFAULT_AUX_PAGES`, `DEFAULT_FREQ`, `auxtrace_record`.

Control flow: Scans evlist events for architecture trace PMUs, sets full auxtrace mode, chooses mmap defaults, configures tracking events, and fills private metadata for perf.data.

State and persistence behavior: No persistent runtime state is owned directly here; the durable effect is build metadata, generated ELF contents, perf.data metadata, or process-local helper state as described by the declarations.

Dependencies and integration points: Depends on perf auxtrace/record/session APIs, PMU sysfs capabilities, event parser, and architecture trace drivers.

Risks: Mmap size defaults, privilege checks, event ordering, and metadata type/size must match decoder expectations.

Test signals: Record/report with architecture trace PMUs, invalid mmap sizes, missing PMUs, and snapshot/full-trace modes where supported.

Source coverage: researched from the complete local file (126 lines, 3087 bytes).
