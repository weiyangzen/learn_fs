# sources/distributed-fs/ceph-client/tools/testing/nvdimm/libnvdimm_test.c

## Purpose
`libnvdimm_test.c` provides a watermark function for the test-linked `libnvdimm` module.

## Important APIs, Types, And Functions
`nfit_test_watermark(libnvdimm)` defines and exports `libnvdimm_test()`.

## Control Flow
The generated watermark logs the current module name at debug level and returns success.

## State And Persistence
No state is stored.

## Dependencies And Integration Points
The file depends on `watermark.h` and is linked into the test `libnvdimm` module. Both ACPI NFIT and non-NFIT test modules call this watermark at init.

## Risks
It does not verify libnvdimm runtime behavior; it only confirms test linkage.

## Test Signals
Success is the presence and successful call of `libnvdimm_test()`.
