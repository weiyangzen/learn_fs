# sources/distributed-fs/ceph-client/tools/testing/cxl/cxl_port_test.c

Purpose: watermark object for the mocked `cxl_port` module.

Important APIs, types, and functions: expands `cxl_test_watermark(cxl_port)` to export `cxl_port_test()`.

Control flow: called from `cxl_test_init()` as part of linkage validation.

State and persistence: none.

Dependencies and integration points: linked into `cxl_port-y`.

Risks: only build/link risk if production/test module composition changes.

Test signals: successful load and callable `cxl_port_test()`.
