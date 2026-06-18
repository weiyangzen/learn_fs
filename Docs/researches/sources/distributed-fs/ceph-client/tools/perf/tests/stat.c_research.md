## sources/distributed-fs/ceph-client/tools/perf/tests/stat.c

Purpose: unit tests for synthetic perf stat metadata events.
Important functions: `has_term`, `process_stat_config_event`, `test__synthesize_stat_config`, `process_stat_event`, `test__synthesize_stat`, `process_stat_round_event`, and `test__synthesize_stat_round`.
Control flow: constructs `perf_stat_config` and `perf_counts_values`, synthesizes stat config/stat/stat round records, and validates callback event payload fields.
State and persistence: no persistent state; all data is stack-local synthetic event content.
Dependencies and integration: `perf_event__synthesize_stat_config`, `perf_event__read_stat_config`, `perf_event__synthesize_stat`, and `perf_event__synthesize_stat_round`.
Risks: tests assume the enum count `PERF_STAT_CONFIG_TERM__MAX` and exact AGGR_CORE/scale/interval values; note `process_stat_event` labels `ena`/`run` assertion messages inversely to fields.
Test signals: three suites registered with `DEFINE_SUITE` return success when synthesized payloads match expected values.
