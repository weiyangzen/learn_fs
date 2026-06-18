# sources/distributed-fs/ceph-client/drivers/nvdimm/dimm_devs.c

## Purpose
`dimm_devs.c` implements NVDIMM device creation helpers, DIMM sysfs attributes, config-data command wrappers, DIMM driver-data lifetime, security and firmware sysfs plumbing, DPA resource allocation/accounting, and DIMM count validation. It is the core per-DIMM support file behind the `nvdimm` device type.

## Important APIs, Types, And Functions
Config-data APIs are `nvdimm_check_config_data()`, `nvdimm_init_nsarea()`, `nvdimm_get_config_data()`, and `nvdimm_set_config_data()`. Device/lifetime APIs include `__nvdimm_create()`, `nvdimm_delete()`, `to_nvdimm()`, `to_ndd()`, `get_ndd()`, `put_ndd()`, `nvdimm_drvdata_release()`, `nvdimm_name()`, `nvdimm_kobj()`, `nvdimm_cmd_mask()`, and `nvdimm_provider_data()`.

Security and firmware helpers include `nvdimm_security_setup_events()`, `nvdimm_in_overwrite()`, `nvdimm_security_freeze()`, and sysfs attributes `security`, `frozen`, `firmware/activate`, and `firmware/result`. DPA helpers include `nd_pmem_max_contiguous_dpa()`, `nd_pmem_available_dpa()`, `nvdimm_allocate_dpa()`, `nvdimm_free_dpa()`, `nvdimm_allocated_dpa()`, and `nvdimm_bus_check_dimm_count()`.

## Control Flow
`__nvdimm_create()` allocates a DIMM ID and object, records provider data, command mask, flush hints, security and firmware ops, initializes security flags before sysfs visibility, initializes the device, and registers it synchronously or asynchronously depending on flags. `nvdimm_delete()` marks security frozen during shutdown, cancels delayed overwrite work, drops pending work references, and synchronously unregisters the device.

Config-data wrappers validate command support, enforce bounds against `nsarea.config_size`, split reads/writes by `max_xfer`, and call provider `ndctl()` with `ND_CMD_GET_CONFIG_DATA` or `ND_CMD_SET_CONFIG_DATA`. `nvdimm_init_nsarea()` obtains label-area geometry through `ND_CMD_GET_CONFIG_SIZE`.

Sysfs attributes expose command names, flags, active/idle state, available label slots, security state/mutation, firmware arm/disarm, and firmware result. Visibility depends on security flags/ops and provider firmware capability.

DPA helpers operate on the `ndd->dpa` resource tree under the bus lock. Availability checks align free ranges to per-DIMM region alignment and account for existing allocations. Max-contiguous checks temporarily reserve all free pmem space as `pmem-reserve`, scan it, then release the reservation.

## State And Persistence Behavior
The file maintains volatile `struct nvdimm` state, `struct nvdimm_drvdata`, and resource-tree DPA allocations that mirror persistent namespace labels. Config-data read/write commands persist label indexes and labels through provider firmware/ACPI methods. Security sysfs can persistently change DIMM passphrase/security state through `nvdimm_security_store()` and freeze/overwrite operations, while firmware sysfs arms activation state.

`nvdimm_drvdata_release()` frees all DPA resource allocations under the bus lock, releases cached label data, frees driver data, and drops the DIMM device reference.

## Dependencies And Integration Points
This file integrates with provider `nvdimm_bus_descriptor.ndctl`, security ops, firmware ops, label helpers, namespace allocation code, bus device registration, Linux resource trees, sysfs, delayed work, and badblock/flush infrastructure. `dimm.c` calls its config and lifetime helpers during probe/remove.

## Risks And Edge Cases
Config-data command sizes are provider constrained; incorrect `max_xfer` handling can truncate label reads/writes. `to_ndd()` warns if called without the bus lock, since the driver data can disappear during DIMM remove. Available-label reporting subtracts one slot as a reserve and warns on underflow. DPA alignment failures return zero availability, which can look like no capacity rather than explicit corruption. Security operations must not run during overwrite or active region use.

## Test Signals
Tests should cover command support detection, config-data chunking and bounds checks, provider command status failures, driver-data kref release freeing DPA resources, sysfs visibility for security/firmware combinations, freeze/overwrite busy behavior, DPA allocation/free/merge accounting, available label slot reporting, active/idle state under region use, and DIMM count checks after async registration.
