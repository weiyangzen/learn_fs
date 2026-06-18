# sources/distributed-fs/ceph-client/tools/testing/cxl/cxl_acpi_test.c

Purpose: watermark object for the mocked `cxl_acpi` module.

Important APIs, types, and functions: includes `watermark.h` and expands `cxl_test_watermark(cxl_acpi)` to define and export `cxl_acpi_test()`.

Control flow: callers invoke `cxl_acpi_test()` from `cxl_test_init()` to confirm the mocked module is linked/loaded. The function logs a debug message and returns zero.

State and persistence: none.

Dependencies and integration points: depends on `watermark.h` and is included in the `cxl_acpi-y` module composition.

Risks: if omitted or linked against the wrong module, `cxl_test` may fail to resolve or may not validate the intended mocked path.

Test signals: successful call from `cxl_test_init()` and resolved exported symbol.
