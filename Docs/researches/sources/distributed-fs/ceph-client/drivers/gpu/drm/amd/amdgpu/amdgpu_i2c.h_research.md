# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_i2c.h

## Purpose
`amdgpu_i2c.h` declares the AMDGPU I2C bus creation, lifecycle, lookup, and router-selection helpers used by display/AtomBIOS code.

## Important APIs, types, and functions
The declared API is `amdgpu_i2c_create()`, `amdgpu_i2c_destroy()`, `amdgpu_i2c_init()`, `amdgpu_i2c_fini()`, `amdgpu_i2c_lookup()`, `amdgpu_i2c_router_select_ddc_port()`, and `amdgpu_i2c_router_select_cd_port()`.

## Control flow
The header has no executable logic. Display code calls these helpers to create adapters from BIOS bus records, initialize legacy bus lists, find existing buses by ID, and switch connector routers before DDC/clock-data transactions.

## State and persistence behavior
State is external in `struct amdgpu_i2c_chan`, connector router metadata, and `adev->i2c_bus[]`. No persistent state is defined here.

## Dependencies and integration points
It depends on AMDGPU display/connector and DRM device types. It integrates with AtomBIOS I2C, EDID probing, and connector router control.

## Risks and edge cases
The declaration of `amdgpu_i2c_destroy()` requires a matching definition elsewhere or dead code avoidance. Callers must handle NULL bus returns and router helpers that silently skip invalid router metadata.

## Test signals
Compile/link coverage, display probe EDID reads, router switching, and bus lookup tests validate the header contract.
