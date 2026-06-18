# sources/distributed-fs/ceph-client/fs/unicode/tests/utf8_kunit.c

`utf8_kunit.c` provides KUnit tests for kernel Unicode normalization. It validates supported Unicode versions, NFDI normalization, NFDICF casefolding, and comparison helpers.

Static vectors `nfdi_test_data` and `nfdicf_test_data` contain UTF-8 inputs and expected normalized/casefolded byte strings, including canonical decomposition, combining-class ordering, ASCII folding, sharp-s expansion, Cherokee, Old Hungarian, Osage, and Georgian examples. `check_utf8_nfdi()` validates `utf8nlen()`, `utf8ncursor()`, and `utf8byte()` in NFDI mode. `check_utf8_nfdicf()` validates casefolded normalization. `check_utf8_comparisons()` verifies `utf8_strncmp()` and `utf8_strncasecmp()` over `struct qstr`s. `check_supported_versions()` checks accepted and rejected Unicode ages. Suite init calls `utf8_load(UTF8_LATEST)` and stores the map in `test->priv`; exit calls `utf8_unload()`.

State is limited to the loaded `unicode_map` and cursor-local iteration. Dependencies are KUnit, `<linux/unicode.h>`, and internal `utf8n.h`; module test builds rely on test-only exports from `utf8-norm.c`. Risks are limited vector breadth, especially invalid/truncated input and buffer-boundary cases. Passing tests signal table loading, normalization, folding, comparison, and version checks are functional.
