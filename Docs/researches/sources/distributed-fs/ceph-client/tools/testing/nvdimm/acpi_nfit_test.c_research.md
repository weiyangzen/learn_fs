# sources/distributed-fs/ceph-client/tools/testing/nvdimm/acpi_nfit_test.c

## Purpose
`acpi_nfit_test.c` supplies a test watermark for the ACPI NFIT module and overrides `nfit_intel_shutdown_status()` so tests receive deterministic dirty-shutdown data.

## Important APIs, Types, And Functions
The `nfit_test_watermark(acpi_nfit)` macro emits and exports `acpi_nfit_test()`. The strong definition `nfit_intel_shutdown_status(struct nfit_mem *nfit_mem)` sets `NFIT_MEM_DIRTY_COUNT` and assigns `dirty_shutdown = 42`.

## Control Flow
The watermark function returns success when called by the test harness. The shutdown-status override is called by ACPI NFIT code in place of the production implementation and unconditionally marks the DIMM as having a dirty shutdown count.

## State And Persistence
The file mutates only the passed `struct nfit_mem`: its flag bitmap and `dirty_shutdown` field. There is no independent persistent state.

## Dependencies And Integration Points
It includes `watermark.h` and `<nfit.h>`, and relies on kbuild linking this object into the test `nfit` module after real ACPI NFIT sources. It integrates with sysfs/user tests expecting a stable dirty shutdown count.

## Risks
The override assumes the target symbol remains replaceable and that `NFIT_MEM_DIRTY_COUNT`/`dirty_shutdown` semantics remain stable. If production code changes to require additional shutdown-status fields, this deterministic stub could become incomplete.

## Test Signals
Calling `acpi_nfit_test()` confirms the test-linked module is active. Observing a dirty shutdown value of `42` confirms the override path was used.
