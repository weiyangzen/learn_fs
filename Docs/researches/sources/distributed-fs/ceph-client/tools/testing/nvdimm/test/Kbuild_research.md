# sources/distributed-fs/ceph-client/tools/testing/nvdimm/test/Kbuild

## Purpose
The nested nvdimm test `Kbuild` builds the synthetic platform modules: the NFIT/ND test module and the iomap wrapper module.

## Important APIs, Types, And Functions
It sets include paths for `drivers/nvdimm` and `drivers/acpi/nfit`, declares `obj-m += nfit_test.o` and `obj-m += nfit_test_iomap.o`, conditionally chooses `nfit.o` or `ndtest.o` as the body of `nfit_test-y`, and maps `nfit_test_iomap-y := iomap.o`.

## Control Flow
At build time, if `CONFIG_ACPI_NFIT=m`, `nfit_test` is built from `nfit.c` and `ndtest.o` is also built as its own module. Otherwise, `nfit_test` is backed by `ndtest.c`. The iomap wrapper module is always built from `iomap.c`.

## State And Persistence
No runtime state is stored. The build output persists the chosen module composition.

## Dependencies And Integration Points
This file integrates the wrapper layer in `iomap.c` with either the ACPI NFIT emulator or the non-NFIT test bus. It relies on config state already checked by the parent nvdimm build.

## Risks
The conditional means module names and behavior differ depending on `CONFIG_ACPI_NFIT`. Test scripts must know whether to load `nfit_test` as NFIT or non-NFIT and whether `ndtest` exists separately.

## Test Signals
Build output showing `nfit_test`, `nfit_test_iomap`, and optionally `ndtest` is the main signal. Runtime module insertion validates the selected branch.
