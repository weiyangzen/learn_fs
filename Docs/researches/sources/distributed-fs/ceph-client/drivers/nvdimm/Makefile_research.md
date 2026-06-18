# sources/distributed-fs/ceph-client/drivers/nvdimm/Makefile

## Purpose
Maps NVDIMM Kconfig symbols to built objects and composes the `libnvdimm` aggregate module/object.

## Important APIs, Types, And Functions
No runtime APIs. It builds top-level objects for `libnvdimm`, `nd_pmem`, `nd_btt`, legacy e820 PMEM, OF PMEM, virtio PMEM, and RAMDAX. `libnvdimm-y` includes core, bus, DIMM, region, namespace, label, badrange, and optional perf, claim, BTT, PFN, DAX, and security files.

## Control Flow
The kernel build system includes object fragments according to `CONFIG_*` values. `TOOLS` and `TEST_SRC` locate the nvdimm unit-test `iomap.o` when `CONFIG_NVDIMM_TEST_BUILD` is enabled.

## State And Persistence
Build-only state.

## Dependencies And Integration Points
Integrates directly with `drivers/nvdimm/Kconfig`, PMEM/BTT/DAX/security source files, virtio PMEM helpers, and the tools testing source tree.

## Risks And Edge Cases
Object list drift can cause unresolved symbols or missing feature code. The test-build object path reaches outside the driver directory into `tools/testing/nvdimm/test`, so source tree layout matters.

## Test Signals
Build matrix should cover `LIBNVDIMM`, `BLK_DEV_PMEM`, `ND_BTT`, `NVDIMM_PFN`, `NVDIMM_DAX`, `NVDIMM_KEYS`, `VIRTIO_PMEM`, and `NVDIMM_TEST_BUILD` combinations.
