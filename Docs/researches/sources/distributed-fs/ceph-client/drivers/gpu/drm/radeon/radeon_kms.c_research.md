<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/radeon_kms.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/radeon_kms.c

## Purpose

`radeon_kms.c` provides the main DRM KMS driver lifecycle and several user-facing KMS callbacks. It loads/unloads the Radeon device, handles AGP/PCIe/PX runtime-PM setup, exposes the `RADEON_INFO` ioctl ABI, creates per-file VM state on open, releases per-file resources on close, and implements vblank counter and vblank interrupt callbacks for DRM core.

## Important APIs, Types, and Functions

- `radeon_driver_load_kms()`: detects AGP/PCI/PCIe flags, optional switchable-graphics PX support, initializes device core with `radeon_device_init()`, initializes modesetting, calls ACPI methods, and configures runtime PM autosuspend for PX devices.
- `radeon_driver_unload_kms()`: wakes PX devices if needed, finalizes ACPI, modeset, and core device state, removes AGP write-combine mappings, frees AGP metadata, and clears `dev_private`.
- `radeon_info_ioctl()`: large switch over `drm_radeon_info.request` returning hardware IDs, pipe/backend/tile configuration, acceleration status, VM limits, ring readiness, clocks, firmware versions, memory usage, temperature, allowed registers, reset count, and per-file HyperZ/CMASK ownership results.
- `radeon_set_filp_rights()`: serializes single-owner per-file feature rights under `rdev->gem.mutex`.
- `radeon_driver_open_kms()`: runtime-PM gets the device, allocates `struct radeon_fpriv` for Cayman+ clients, initializes a VM when acceleration works, and maps the IB pool read-only at `RADEON_VA_IB_OFFSET`.
- `radeon_driver_postclose_kms()`: drops HyperZ/CMASK ownership, frees UVD/VCE handles, removes the VM IB-pool mapping, finalizes VM state, and releases runtime PM.
- `radeon_get_vblank_counter_kms()`: reads the hardware frame counter and adjusts it to DRM's start-of-vblank semantics using scanout position.
- `radeon_enable_vblank_kms()` / `radeon_disable_vblank_kms()`: toggle per-CRTC vblank IRQ state under `rdev->irq.lock`.

## Control Flow

Load begins with bus classification and optional AGP setup/MTRR. PX is enabled only when runtime PM is allowed, ATPX is present, the device is not IGP, and it is not Thunderbolt-attached. Device initialization is expected to fail only on fatal resource/setup errors; modeset initialization should similarly fail only on fatal display setup errors. ACPI methods run after modeset because display objects must exist. PX runtime PM is configured after successful init.

The info ioctl normalizes the user pointer, defaults to a 32-bit return value, and switches by request. Some requests first read an input value from userspace, such as CRTC object ID, HyperZ/CMASK ownership intent, ring selector, or register offset. Requests returning 64-bit values redirect the output pointer to a local `u64` and change `value_size`. At the end, the selected value buffer is copied to userspace.

Open creates per-file VM state only for Cayman and later. It maps the shared IB pool BO into the client's VM read-only and snooped so IBs allocated from that pool can be referenced by virtual address. Postclose reverses those mappings, frees media handles, and clears single-owner feature grants.

The vblank counter path compensates for Radeon hardware incrementing at vsync rather than start of vblank. It reads count, queries scanout position relative to vblank start, retries if the counter changed during sampling, and increments the returned count when currently between vblank start and vsync.

## State and Persistence Behavior

Device lifetime state includes `rdev->agp`, bus flags, PX/runtime-PM state, modeset/core initialization, ACPI state, and `dev->dev_private`. Per-file state includes `struct radeon_fpriv`, `struct radeon_vm`, HyperZ/CMASK ownership pointers, and UVD/VCE handles. The info ioctl reads persistent hardware capability/configuration state and exposes it as ABI. Vblank enable state persists in `rdev->irq.crtc_vblank_int[]`.

## Dependencies and Integration Points

This file integrates with PCI/AGP, VGA switcheroo/ATPX, runtime PM, Radeon device/modeset/ACPI initialization, GEM/TTM memory managers, command submission VM support, UVD/VCE handle tracking, DRM ioctl ABI definitions, DRM vblank core, and scanout-position helpers. It is the central bridge between DRM core callbacks and Radeon internal subsystems.

## Risks and Edge Cases

- `radeon_info_ioctl()` is ABI-sensitive: changing return values, request gating, or array sizes can break Mesa/xf86-video-ati expectations.
- Some `RADEON_INFO_*` cases intentionally report historical compatibility values, such as false acceleration for Evergreen in `ACCEL_WORKING`; these are easy to "fix" incorrectly.
- The open error path must remove partially initialized VM/BO mappings and put runtime PM exactly once.
- `radeon_driver_unload_kms()` has early branches for partially initialized devices; teardown ordering must remain valid for failed probe paths.
- Vblank count correction depends on accurate scanout position. If that query is invalid, the raw hardware counter may not satisfy DRM timing semantics.

## Test Signals

Test with successful and failing probe paths, AGP and PCIe devices, PX runtime suspend/resume, every supported `RADEON_INFO` request including user-input requests and 64-bit outputs, Mesa startup capability queries, per-client VM creation and teardown, HyperZ/CMASK ownership transfer, UVD/VCE handle cleanup, vblank counter monotonicity around vblank/vsync edges, and invalid user pointer fault paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/radeon_kms.c -->
