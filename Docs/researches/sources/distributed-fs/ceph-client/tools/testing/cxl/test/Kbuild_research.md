# sources/distributed-fs/ceph-client/tools/testing/cxl/test/Kbuild

Purpose: Kbuild file for the CXL test-side setup, mock dispatcher, mock memory device, and translation test modules.

Important APIs, types, and functions: adds include paths for `drivers/cxl` and `drivers/cxl/core`. Builds `cxl_test.o` from `cxl.o` and `hmem_test.o`, `cxl_mock.o` from `mock.o`, `cxl_mock_mem.o` from `mem.o`, and standalone `cxl_translate.o`. Filters missing prototype/declaration warnings.

Control flow: Kbuild compiles these modules under the top-level CXL testing Kbuild. `cxl_mock` provides wrapped-symbol dispatch; `cxl_test` creates platform topology; `cxl_mock_mem` probes fake memory devices; `cxl_translate` tests address translation helpers.

State and persistence: no runtime state in the build file.

Dependencies and integration points: depends on the top-level Kbuild's wrapped symbol setup and CXL driver headers.

Risks: module names and split object lists must stay synchronized with source files and symbols expected by wrapper code. Warning filtering can hide interface drift.

Test signals: `make M=tools/testing/cxl` should emit all four test modules from this directory.
