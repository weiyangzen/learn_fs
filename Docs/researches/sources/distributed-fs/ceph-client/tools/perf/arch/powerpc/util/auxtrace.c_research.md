# sources/distributed-fs/ceph-client/tools/perf/arch/powerpc/util/auxtrace.c

Purpose: Architecture auxtrace recorder setup for perf, selecting PMU trace events and filling AUXTRACE metadata.

Important APIs/types/functions: `powerpc_vpadtl_recording_options`, `powerpc_vpadtl_info_priv_size`, `powerpc_vpadtl_info_fill`, `powerpc_vpadtl_free`, `powerpc_vpadtl_reference`, `KiB`, `auxtrace_record`.

Control flow: Scans evlist events for architecture trace PMUs, sets full auxtrace mode, chooses mmap defaults, configures tracking events, and fills private metadata for perf.data.

State and persistence behavior: No persistent runtime state is owned directly here; the durable effect is build metadata, generated ELF contents, perf.data metadata, or process-local helper state as described by the declarations.

Dependencies and integration points: Depends on perf auxtrace/record/session APIs, PMU sysfs capabilities, event parser, and architecture trace drivers.

Risks: Mmap size defaults, privilege checks, event ordering, and metadata type/size must match decoder expectations.

Test signals: Record/report with architecture trace PMUs, invalid mmap sizes, missing PMUs, and snapshot/full-trace modes where supported.

Source coverage: researched from the complete local file (105 lines, 2313 bytes).
