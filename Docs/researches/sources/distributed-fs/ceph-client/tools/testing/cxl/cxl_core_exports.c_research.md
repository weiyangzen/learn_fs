# sources/distributed-fs/ceph-client/tools/testing/cxl/cxl_core_exports.c

Purpose: exports CXL core symbols needed only by the test environment.

Important APIs, types, and functions: includes `cxl.h` and exports `cxl_num_decoders_committed` in namespace `CXL` with `EXPORT_SYMBOL_NS_GPL`.

Control flow: no runtime control flow; it makes an otherwise internal core helper available to CXL test modules.

State and persistence: none.

Dependencies and integration points: part of the mocked `cxl_core` module; consumed by `tools/testing/cxl/test/cxl.c` decoder commit/reset emulation.

Risks: exporting test-only internals can mask production encapsulation assumptions if used outside tests. Namespace and symbol name must track CXL core changes.

Test signals: modules using `cxl_num_decoders_committed()` should link and load with `MODULE_IMPORT_NS("CXL")`.
