# sources/distributed-fs/ceph-client/tools/testing/nvdimm/test/ndtest.c

## Purpose
`ndtest.c` implements a synthetic non-ACPI nvdimm platform for exercising libnvdimm, pmem, DAX, labels, region registration, and PAPR-style sysfs attributes without real NFIT firmware.

## Important APIs, Types, And Functions
Important static data defines two bus instances, DIMM groups, and region mappings. Core functions include `ndtest_ctl()`, `ndtest_resource_lookup()`, `ndtest_alloc_resource()`, `ndtest_create_region()`, `ndtest_init_regions()`, `ndtest_dimm_register()`, `ndtest_nvdimm_init()`, `ndtest_bus_register()`, `ndtest_probe()`, `ndtest_init()`, and `ndtest_exit()`. Sysfs attributes expose DIMM handles, failure injection fields, PAPR metadata, region range indexes, and health flags.

## Control Flow
Module init calls watermark functions, registers the nfit test lookup provider, creates a class and a 4 GiB aligned gen_pool, registers two platform devices, and then registers the platform driver. Probe registers an nvdimm bus, allocates DMA arrays, creates label/DIMM/DCR synthetic resources, registers nvdimms, creates pmem or IO regions, and installs devres cleanup. Control commands support label config size/get/set and optional failure injection through per-DIMM `fail_cmd` and `fail_cmd_code`.

## State And Persistence
Global state includes `instances[NUM_INSTANCES]`, `ndtest_pool`, and static bus/dimm/region descriptors. Runtime state is stored in each `struct ndtest_priv`: platform device, resource list, bus descriptor, nvdimm bus, DMA arrays, and selected config. DIMM state includes label buffers, flags, command failure masks, and registered device pointers. No state persists beyond module lifetime.

## Dependencies And Integration Points
The file integrates with libnvdimm through `nvdimm_bus_register()`, `nvdimm_create()`, `nvdimm_pmem_region_create()`, and command masks. It integrates with the mapping wrapper through `nfit_test_setup(ndtest_resource_lookup, NULL)` and resource records compatible with `iomap.c`. It also exposes PAPR SCM-like attributes and flags for userspace nvdimm tests.

## Risks
The global static configs are mutated in-place when DIMMs are registered, so repeated load/unload depends on cleanup resetting all observable state. `NUM_DCR` is four while the second bus pushes IDs using `dimm_start`; the code sizes DMA arrays to `NUM_DCR`, so additions to the configured DIMM count need careful bounds review. Failure injection uses bit shifts of command numbers; large command IDs would overflow the mask.

## Test Signals
Signals include successful module insertion, creation of two nvdimm buses, DIMM and region sysfs attributes, functioning label get/set commands, and ability to inject command failures through sysfs. Runtime resource lookup warnings indicate missing synthetic-resource registration.
