# sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/sch_ets_tests.sh

Purpose: reusable assertion library for ETS qdisc behavior. It interprets ETS band configuration, starts stream traffic, samples per-band stats, and checks strict-priority and DWRR scheduling ratios.

Important functions include `qdisc_describe`, `strict_eval`, `notraf_eval`, `__ets_dwrr_test`, `ets_qdisc_setup`, `ets_set_*`, `ets_change_quantum`, `ets_test_strict`, `ets_test_mixed`, `ets_test_dwrr`, and `ets_test_plug`. It expects callbacks/global variables from a driver: `put`, `collect_stats`, `ets_start_traffic`, and `ets_change_qdisc`. The `WS` array models each band, with zero meaning strict and nonzero values meaning DWRR quantum.

Control flow for a test sets qdisc shape, starts selected traffic streams in a defer scope, sleeps, samples counters twice, computes deltas/total, and checks that strict traffic dominates, lower strict bands are starved, or DWRR ratios match configured quanta through `multipath_eval`. State is the shell `WS` array, qdisc configuration, and background traffic. Risks include timing sensitivity, `bc` availability, low traffic counts, and strict thresholds of >95% or <5%. Test signals are `log_test` for band ratios and failures from `check_err`.
