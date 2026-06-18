# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_fru_eeprom.h

## Purpose
`amdgpu_fru_eeprom.h` declares the AMDGPU FRU product-information cache and sysfs lifecycle API.

## Important APIs, types, and functions
It defines `AMDGPU_PRODUCT_NAME_LEN`, `struct amdgpu_fru_info`, and prototypes for `amdgpu_fru_get_product_info()`, `amdgpu_fru_sysfs_init()`, and `amdgpu_fru_sysfs_fini()`.

## Control flow
The header has no executable control flow. It defines the data contract used by device initialization to fetch FRU data and by sysfs setup/teardown to expose it.

## State and persistence behavior
`struct amdgpu_fru_info` is runtime cached state containing product number, product name, serial, manufacturer name, and FRU ID. Persistent storage is the EEPROM read by the C file.

## Dependencies and integration points
It relies on `struct amdgpu_device` being visible to callers. The structure is stored as `adev->fru_info` and exported via sysfs attributes implemented in `amdgpu_fru_eeprom.c`.

## Risks and edge cases
Fixed-size string buffers require bounded copies and NUL termination in the implementation. New FRU fields or longer identifiers would require structure and sysfs contract changes.

## Test signals
Build coverage plus sysfs reads of all FRU fields on supported server GPUs validate the header.
