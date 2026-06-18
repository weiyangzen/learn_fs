# sources/distributed-fs/ceph-client/tools/perf/arch/arm/util/cs-etm.c

Purpose: ARM CoreSight ETM perf recording support and metadata declarations.

Important APIs/types/functions: `cs_etm_is_ete`, `cs_etm_get_ro`, `cs_etm_pmu_path_exists`, `cs_etm_validate_context_id`, `cs_etm_validate_timestamp`, `cs_etm_validate_config`, `cs_etm_parse_snapshot_options`, `cs_etm_set_sink_attr`, `cs_etm_recording_options`, `cs_etm_synth_etmcr`, `cs_etmv4_synth_trcconfigr`, `cs_etm_info_priv_size`.

Control flow: Validates ETMv3/ETMv4/ETE capabilities per CPU, checks context ID/timestamp options, configures AUX buffers/snapshot mode, and records metadata paths needed by decoders.

State and persistence behavior: No persistent runtime state is owned directly here; the durable effect is build metadata, generated ELF contents, perf.data metadata, or process-local helper state as described by the declarations.

Dependencies and integration points: Depends on CoreSight PMU sysfs files, perf auxtrace APIs, CPU maps, event config terms, and page-size/privilege helpers.

Risks: Heterogeneous CPUs with missing metadata, unsupported context/timestamp options, and AUX size rounding can fail late or produce undecodable traces.

Test signals: Perf record with ETMv3, ETMv4, ETE, per-thread/per-cpu modes, snapshot mode, and invalid option combinations.

Source coverage: researched from the complete local file (925 lines, 28272 bytes).
