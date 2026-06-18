# sources/distributed-fs/ceph-client/tools/testing/nvdimm/watermark.h

## Purpose
`watermark.h` defines tiny exported test functions used to verify that test-composed nvdimm modules are linked and loaded instead of standard base-tree modules.

## Important APIs, Types, And Functions
It declares watermark functions for pmem, libnvdimm, acpi_nfit, device_dax, dax_pmem, and dax_pmem variants. The `nfit_test_watermark(x)` macro defines `int x##_test(void)` and exports it.

## Control Flow
Each generated watermark function emits a debug message containing `KBUILD_MODNAME` and returns `0`.

## State And Persistence
No state is stored or modified.

## Dependencies And Integration Points
Watermark C files include this header to generate exported symbols. `nfit.c` and `ndtest.c` call the symbols during module initialization.

## Risks
The macro requires including files to have `pr_debug`, `KBUILD_MODNAME`, and `EXPORT_SYMBOL` available. It validates module composition only, not behavior.

## Test Signals
Successful symbol resolution and return value `0` are the intended signals. Debug output identifies which module supplied the watermark.
