# sources/distributed-fs/ceph-client/drivers/gpu/drm/vmwgfx/device_include/svga3d_devcaps.h

## Purpose

`svga3d_devcaps.h` defines SVGA3D device capability indices and result types. The driver uses these constants to query and interpret host-advertised 3D, DX, shader-model, multisample, logic operation, format, and resource limits.

## Important APIs, Types, and Functions

- `SVGA3D_MAKE_HWVERSION`, `SVGA3D_MAJOR_HWVERSION`, `SVGA3D_MINOR_HWVERSION`: helpers for encoded hardware-version values.
- `SVGA3dHardwareVersion`: historical/current virtual hardware version constants.
- `SVGA3dDevCapIndex`: integer capability selector type.
- `SVGA3D_DEVCAP_*`: dense capability index list from core 3D support and fixed-function limits through DX format support, SM4.1/SM5, multisampling, logicops, GL43, and `SVGA3D_DEVCAP_MAX`.
- `SVGA3D_DXFMT_*`: bit flags describing DX format support properties such as shader sampling, render-target use, blending, mips, arrays, volume, vertex-buffer use, and multisampling.
- `SVGA3dDevCapResult`: union view of a capability result as bool, unsigned, signed, or float.

## Control Flow

There is no runtime control flow in the header. Driver code selects a capability index, reads the corresponding device result, and interprets the union member according to the documented capability.

## State and Persistence Behavior

Capability values are usually read during device initialization or feature probing and then cached in driver state. The header defines the index ABI but owns no storage.

## Dependencies and Integration Points

- Includes `svga3d_types.h` for VMware fixed-width and 3D types.
- Integrates with `vmwgfx_devcaps.o`, feature checks, format validation, shader-model gating, and command validation paths.
- Numeric indices must match host SVGA device firmware/hypervisor expectations.

## Risks and Edge Cases

- The capability table has missing/dead slots preserved for ABI numbering. Renumbering or compacting it would corrupt all later queries.
- `SVGA3dDevCapResult` is untagged; callers must know whether a specific index returns bool, integer, or float.
- Format capability flags are bitmasks, not enum values. Misinterpreting zero or unsupported flags can enable invalid render paths.
- `SVGA3D_DEVCAP_MAX` must stay consistent with host-provided capability table sizing.

## Test Signals

- Device-probe tests should verify queried caps are in range and cached values gate DX/SM/multisample/logicops paths correctly.
- ABI tests should detect changes to numeric capability indices and `SVGA3D_DEVCAP_MAX`.
- Format validation tests should cross-check `SVGA3D_DXFMT_*` flags against accepted surface/view/buffer uses.
