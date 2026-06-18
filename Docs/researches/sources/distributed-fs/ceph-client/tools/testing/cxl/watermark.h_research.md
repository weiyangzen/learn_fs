# sources/distributed-fs/ceph-client/tools/testing/cxl/watermark.h

Purpose: helper macro for exporting module-specific watermark functions so `cxl_test` can verify it is linked against mocked CXL modules.

Important APIs, types, and functions: declares `cxl_acpi_test()`, `cxl_core_test()`, `cxl_mem_test()`, `cxl_pmem_test()`, and `cxl_port_test()`. Macro `cxl_test_watermark(x)` defines `x##_test()` to log a debug message containing `KBUILD_MODNAME`, return zero, and export the symbol.

Control flow: each small `*_test.c` file expands the macro. `cxl_test_init()` calls all watermark functions at load time.

State and persistence: none.

Dependencies and integration points: depends on module and printk headers. Integrated into mocked CXL modules through Kbuild.

Risks: the mechanism validates symbol presence, not complete behavioral correctness. Exported names must stay aligned with declarations and caller expectations.

Test signals: all five watermark functions resolve and return zero during `cxl_test` initialization.
