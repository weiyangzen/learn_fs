# sources/distributed-fs/ceph-client/tools/testing/nvdimm/test/ndtest.h

## Purpose
`ndtest.h` defines the private data model for the non-NFIT nvdimm test platform.

## Important APIs, Types, And Functions
Important structures are `ndtest_priv`, `ndtest_blk_mmio`, `ndtest_dimm`, `ndtest_mapping`, `ndtest_region`, and `ndtest_config`. These types describe synthetic platform devices, DIMM metadata, label and MMIO resources, region mappings, and per-bus configuration.

## Control Flow
The header contains declarations only. Runtime behavior is implemented in `ndtest.c`, which allocates and populates these structures during platform probe.

## State And Persistence
The structures hold module-lifetime state: registered device pointers, resource lists, nvdimm bus descriptors, DMA addresses, labels, command failure settings, region definitions, and mappings. None is persisted outside the module.

## Dependencies And Integration Points
The header depends on Linux platform-device and libnvdimm types. It is included by `ndtest.c` and complements `nfit_test.h` resource definitions used by the shared iomap wrapper.

## Risks
The structures expose raw pointers and fixed-size counters without helper APIs, so consistency is maintained by convention in `ndtest.c`. Expanding mappings beyond `NDTEST_MAX_MAPPING` in implementation would require coordinated changes.

## Test Signals
There are no direct test signals. Compile success verifies structural compatibility with current libnvdimm headers; runtime signals come from the module using these structures.
