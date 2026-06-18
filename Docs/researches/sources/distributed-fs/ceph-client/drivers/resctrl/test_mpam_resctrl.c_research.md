# sources/distributed-fs/ceph-client/drivers/resctrl/test_mpam_resctrl.c

Purpose: KUnit coverage for the MPAM resctrl memory-bandwidth conversion helpers included into `mpam_resctrl.c`. It validates architectural fixed-point MBW_MAX percentage tables, usable MBA granularity, round-trip stability, and rounding policy.

Important APIs/types/functions: `struct percent_value_case`, `struct percent_value_test_info`, `percent_value_cases[]`, `test_percent_value_desc()`, `__prepare_percent_value_test()`, `test_get_mba_granularity()`, `test_mbw_max_to_percent()`, `test_percent_to_mbw_max()`, `test_mbw_max_to_percent_limits()`, `test_percent_max_roundtrip_stability()`, and `test_percent_to_max_rounding()` exercise `mpam_set_feature()`, `mba_class_use_mbw_max()`, `get_mba_granularity()`, `get_mba_min()`, `mbw_max_to_percent()`, and `percent_to_mbw_max()`.

Control flow: parameter generators feed exact MPAM reference vectors and all `bwa_wd` widths 1..16 into KUnit cases. Each case builds fake `mpam_props`, enables `mpam_feat_mbw_max`, sets width, converts values both ways, and asserts exact or bounded results.

State and persistence: no persistent state; fake props are local per test and the KUnit suite registers at load time.

Dependencies and integration: compiled by inclusion into the MPAM resctrl implementation, so tests can reach static helpers. Depends on KUnit, math/bit helpers, and MPAM internal structures.

Risks and test signals: the suite intentionally tolerates round-to-nearest differences from reference tables but checks the round-up rate is plausible. Gaps are invalid widths, 0% table coverage, and integration with real MPAM device discovery. Signals are KUnit pass/fail for all width parameters and warnings about rounding policy mismatch.
