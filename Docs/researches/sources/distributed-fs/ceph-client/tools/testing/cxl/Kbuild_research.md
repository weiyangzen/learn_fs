# sources/distributed-fs/ceph-client/tools/testing/cxl/Kbuild

Purpose: top-level Kbuild file for CXL test modules, compiling selected production CXL/DAX sources together with mock wrappers and test-specific watermarks.

Important APIs, types, and functions: uses linker `--wrap` flags for ACPI, CXL, nvdimm, hmem, and region functions. Defines source roots `DRIVERS`, `DAX_HMEM_SRC`, `CXL_SRC`, and `CXL_CORE_SRC`; adds include paths and `-D__mock=__weak`, `-DCXL_TEST_ENABLE=1`, and trace include path. Builds modules `cxl_acpi`, `cxl_pmem`, `cxl_port`, `cxl_mem`, `cxl_core`, `dax_hmem`, and recurses into `test/`.

Control flow: Kbuild composes each module from production driver files plus `config_check.c` and a module-specific watermark file. The `cxl_core` module includes core CXL objects conditional on Kconfig symbols. Linker wrapping redirects selected external symbols to `__wrap_*` functions implemented in `test/mock.c`.

State and persistence: no runtime state here; it determines module link composition and symbol interposition.

Dependencies and integration points: depends on kernel CXL, ACPI, dax/hmem, libnvdimm, tracing, and region Kconfig. It must be kept synchronized with production driver file names and wrapped symbol signatures.

Risks: stale `--wrap` entries or production source lists can break builds or silently stop mocking a path. Conditional core object inclusion must match exported symbols expected by tests. `KBUILD_CFLAGS` filters missing prototype/declaration warnings, which can hide interface drift.

Test signals: all CXL test modules should build as modules. Loading `cxl_test` should call watermarks from these mocked modules, proving the test linked against the intended objects.
