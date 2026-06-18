# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_discovery.h

## Purpose

`amdgpu_discovery.h` is the public header for the discovery subsystem. It defines the cached discovery state carried by `struct amdgpu_device`, constants for default TMR placement, and the small API used by AMDGPU core, memory code, and diagnostics to initialize, query, dump, and tear down hardware discovery data.

## Important APIs, types, and functions

- `DISCOVERY_TMR_SIZE` and `DISCOVERY_TMR_OFFSET` define the default 10 KiB table size and 64 KiB-from-end offset used when firmware/registers do not supply a more specific discovery TMR location.
- `struct amdgpu_discovery_info` stores the `debugfs_blob_wrapper`, sysfs topology root `ip_top`, binary offset, size, loaded binary pointer, and `reserve_tmr` flag.
- `amdgpu_discovery_set_ip_blocks()` is the main setup API.
- `amdgpu_discovery_fini()` releases sysfs and binary resources.
- `amdgpu_discovery_get_nps_info()` returns NPS partitioning and memory ranges.
- `amdgpu_discovery_dump()` emits discovery topology to a `drm_printer`.

## Control flow

Callers treat this header as the lifecycle contract: set IP blocks during device initialization, optionally query NPS information after discovery has populated the cached binary, dump topology during diagnostics, and call fini during device teardown.

## State and persistence behavior

`struct amdgpu_discovery_info` persists the loaded discovery binary and sysfs/debugfs representation across the device lifetime. `reserve_tmr` records whether the table memory reservation is required, which matters when the discovery table was sourced from VRAM/TMR rather than a standalone firmware file.

## Dependencies and integration points

The header includes `<linux/debugfs.h>` for `debugfs_blob_wrapper` and forward-declares `ip_discovery_top` and `drm_printer` to avoid broad include dependencies. It is consumed by `amdgpu_discovery.c` and any AMDGPU component that needs discovery lifecycle or NPS queries.

## Risks and edge cases

The header exposes only opaque discovery topology state, so ABI risk is internal to the driver. The main risk is that fields in `amdgpu_discovery_info` must stay consistent with teardown logic in `amdgpu_discovery.c`; stale `bin` or `ip_top` pointers would cause removal/debug paths to fail.

## Test signals

Compile coverage is the primary header-level test. Runtime signals come from successful discovery initialization and teardown, a valid debugfs blob size/data pair, valid NPS query behavior, and absence of sysfs lifetime errors during module unload or GPU hot-unplug.
