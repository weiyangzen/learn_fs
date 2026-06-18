# sources/distributed-fs/ceph-client/tools/testing/cxl/cxl_mem_test.c

Purpose: watermark object for the mocked `cxl_mem` module.

Important APIs, types, and functions: expands `cxl_test_watermark(cxl_mem)` to define and export `cxl_mem_test()`.

Control flow: called from `cxl_test_init()` to prove that the test setup sees the mocked memory module, then returns zero.

State and persistence: none.

Dependencies and integration points: included in the `cxl_mem-y` module recipe.

Risks: missing or wrong symbol indicates the cxl_test module is not testing the intended module composition.

Test signals: successful symbol resolution and debug watermark message.
