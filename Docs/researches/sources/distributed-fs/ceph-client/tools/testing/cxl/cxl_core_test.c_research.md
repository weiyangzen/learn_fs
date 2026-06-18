# sources/distributed-fs/ceph-client/tools/testing/cxl/cxl_core_test.c

Purpose: watermark object for the mocked `cxl_core` module.

Important APIs, types, and functions: expands `cxl_test_watermark(cxl_core)` to export `cxl_core_test()`.

Control flow: `cxl_test_init()` calls the function to validate test linkage; it logs debug output and returns zero.

State and persistence: none.

Dependencies and integration points: depends on `watermark.h`; linked into `cxl_core-y`.

Risks: minimal, but missing export breaks the setup module's linkage validation.

Test signals: exported `cxl_core_test()` resolves and returns zero.
