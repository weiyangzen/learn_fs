# sources/distributed-fs/ceph-client/tools/testing/cxl/test/cxl_translate.c

Purpose: kernel module test for CXL address translation helpers, covering DPA-to-HPA, HPA-to-DPA, interleave position extraction, XOR interleave mapping, random round trips, and parameter validation.

Important APIs, types, and functions: module parameter array `table` accepts up to 128 space-separated test vectors. Key functions are `to_hpa()`, `to_dpa()`, `to_pos()`, `run_translation_test()`, `parse_test_vector()`, `setup_xor_mapping()`, `test_random_params()`, `test_cxl_validate_translation_params()`, `cxl_translate_init()`, and `cxl_translate_exit()`. It calls CXL helpers `cxl_calculate_hpa_offset()`, `cxl_calculate_dpa_offset()`, `cxl_calculate_position()`, `cxl_do_xormap_calc()`, `cxl_validate_translation_params()`, and `eiw_to_ways()`.

Control flow: if no `table` entries are supplied, init runs internal validation: fixed valid/invalid encoded interleave parameter tests and 10,000 random round-trip modulo translation checks. If table entries are supplied, it allocates static XOR map data, parses each vector as `dpa pos r_eiw r_eig hb_ways math expect_hpa`, runs forward and reverse translations, logs pass/fail per vector, frees XOR state, and returns success from module init.

State and persistence: `cximsd` is allocated only for table-driven tests and freed before init returns. Module parameters persist in module state while loaded. No sysfs attributes beyond module params.

Dependencies and integration points: depends on CXL core translation APIs and namespace import `CXL`. It is built as `cxl_translate` from the CXL test Kbuild.

Risks: table-driven test failures are logged but do not cause a nonzero module init return after processing all entries, so automation must inspect logs. XOR maps are static and comments note they must change for new datasets. Random test only covers modulo helpers and uses shifted random DPA values.

Test signals: no-param load should print internal validation success. Table loads should print PASS per vector and detailed errors on mismatch. Parameter validation failures should return negative errors in no-param mode.
