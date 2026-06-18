# sources/distributed-fs/ceph-client/tools/testing/selftests/mm/test_page_frag.sh

Purpose: wrapper for the page fragment allocator kernel-module selftest, providing smoke and performance parameter presets plus manual module-parameter validation.

Important APIs and functions: CPU selection derives two test CPUs from `/proc/cpuinfo`; presets are `SMOKE_PARAM`, `NONALIGNED_PARAM`, and `ALIGNED_PARAM`; `check_test_requirements()` validates root, `insmod`, and `./page_frag/page_frag_test.ko`; `validate_passed_args()` checks keys against `modinfo`; `check_test_failed_prefix()` scans dmesg.

Control flow and state: accepts `smoke`, `nonaligned`, `aligned`, or manual parameters, inserts the module, scans dmesg for `"page_frag_test failed:"`, and prints completion guidance. It does not explicitly remove the module after insertion.

Dependencies and risks: depends on root, built module, `modinfo`, `insmod`, and readable dmesg. Pass/fail is dmesg-string based and can be confused by restricted logs or stale failure messages.
