# sources/distributed-fs/ceph-client/tools/testing/nvdimm/test/nfit_test.h

## Purpose
`nfit_test.h` defines shared contracts for the nvdimm test wrapper layer and synthetic NFIT/ND command payloads.

## Important APIs, Types, And Functions
Important resource types are `struct nfit_test_request` and `struct nfit_test_resource`. Command structures cover NFIT translate-SPA and ARS error injection plus Intel SMART, SMART thresholds, SMART injection, firmware update, firmware query, and latch-shutdown-status payloads. Callback typedefs `nfit_test_lookup_fn` and `nfit_test_evaluate_dsm_fn` connect resource providers to `iomap.c`. The header declares all wrapper functions and setup/teardown/resource lookup APIs.

## Control Flow
There is no implementation control flow. The declarations enable `nfit.c`, `ndtest.c`, and `iomap.c` to share resource lookup and command structure definitions.

## State And Persistence
The defined structures model module-lifetime resource state: resource ranges, vmalloc buffers, request subregions, locks, device owners, and command payloads. Actual storage is allocated by `nfit.c` or `ndtest.c`.

## Dependencies And Integration Points
The header depends on ACPI, list, UUID, resource, and spinlock kernel headers. It is the central ABI between the synthetic platform modules and the link-time wrappers.

## Risks
The packed command structures must match driver/user ABI expectations exactly. Comments note variable input data layouts, making offset and status placement easy to break. Adding wrapper declarations requires matching linker flags in `Kbuild`.

## Test Signals
Compile success verifies that wrapper prototypes and command payloads match the current kernel headers. Runtime signals are produced by the modules that allocate `nfit_test_resource` instances and service these command payloads.
