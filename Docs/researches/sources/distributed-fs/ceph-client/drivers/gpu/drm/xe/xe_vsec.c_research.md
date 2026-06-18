# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_vsec.c

## Purpose

`xe_vsec.c` registers Intel VSEC auxiliary telemetry/crashlog capabilities for supported Xe platforms and implements a PMT telemetry read callback for Battlemage-style GUID encoded telemetry regions.

## Important APIs, Types, and Functions

The public functions are `xe_vsec_init(struct xe_device *xe)` and `xe_pmt_telem_read(struct device *dev, u32 guid, u64 *data, loff_t user_offset, u32 count)`. Static platform data includes `bmg_telemetry`, `bmg_crashlog`, `bmg_capabilities`, `xe_vsec_info[]`, and `vsec_platforms[]`. `xe_guid_decode()` decodes GUID fields into a SoC remapper memory region index and register offset. `xe_pmt_cb` supplies the `.read_telem` callback to the intel_vsec PMT layer.

## Control Flow and State

`xe_vsec_init()` maps the Xe platform to an internal VSEC platform id, rejects unsupported platforms or missing headers, attaches private PMT callbacks for BMG, and calls `intel_vsec_register()` with device-managed cleanup handled by the VSEC subsystem.

`xe_pmt_telem_read()` decodes the GUID, computes an MMIO address from `BMG_TELEMETRY_OFFSET` plus decoded offset plus user offset, takes `xe->pmt.lock`, checks that the SoC remapper callback exists, requires the device to be runtime-PM active via `xe_pm_runtime_get_if_active()`, selects the telemetry region through `soc_remapper.set_telem_region()`, copies MMIO data with `memcpy_fromio()`, drops runtime PM, and returns the byte count.

## Dependencies and Integration Points

This file depends on Linux `intel_vsec`, PMT register definitions, Xe MMIO, platform types, runtime PM, SoC remapper callbacks, and device type conversion. It imports the `INTEL_VSEC` namespace. Userspace-facing telemetry flows through the intel_vsec auxiliary device rather than Xe-specific ioctls.

## Risks and Edge Cases

GUID decoding is strict: only the BMG device id is accepted, capability type must be valid, and some record/capability pairs deliberately map to zero offset. Reads fail with `-ENODEV` when the GUID or remapper is unsupported and `-ENODATA` when the device is not at an active power level. The telemetry address calculation depends on `count` and `user_offset` supplied by the VSEC layer; bounds expectations should remain aligned with the VSEC header metadata.

## Test Signals

Tests should cover supported and unsupported platforms, GUID decode success for PUNIT/OOBMSM telemetry, watcher, and crashlog records, invalid device id and cap type errors, missing remapper behavior, runtime-suspended reads returning `-ENODATA`, lock serialization, and correct intel_vsec registration with telemetry and crashlog capabilities.
