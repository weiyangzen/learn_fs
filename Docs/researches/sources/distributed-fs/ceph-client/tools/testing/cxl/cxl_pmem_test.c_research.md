# sources/distributed-fs/ceph-client/tools/testing/cxl/cxl_pmem_test.c

Purpose: watermark object for the mocked `cxl_pmem` module.

Important APIs, types, and functions: expands `cxl_test_watermark(cxl_pmem)` to export `cxl_pmem_test()`.

Control flow: invoked during CXL test setup to confirm the pmem module participating in the test is the mocked build.

State and persistence: none.

Dependencies and integration points: linked into `cxl_pmem-y` with production pmem/security sources and `config_check.c`.

Risks: low; its absence or wrong namespace breaks test validation.

Test signals: exported function resolves and logs debug watermark when called.
