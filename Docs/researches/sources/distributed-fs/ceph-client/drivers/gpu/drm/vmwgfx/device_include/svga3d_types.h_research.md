# sources/distributed-fs/ceph-client/drivers/gpu/drm/vmwgfx/device_include/svga3d_types.h

## Purpose

`svga3d_types.h` is the foundational SVGA3D type and enum map. It defines IDs, geometry primitives, resource types, surface formats and flags, render and texture state enums, shader/query types, transfer/copy boxes, MOB/cotable identifiers, multisample settings, and query-result layouts used by the rest of the vmwgfx SVGA3D ABI.

## Important APIs, Types, and Functions

- Basic IDs and geometry: `SVGA3dSurfaceId`, `SVGA3dCopyRect`, `SVGA3dCopyBox`, `SVGA3dRect`, `SVGA3dBox`, `SVGA3dSignedBox`, `SVGA3dSize`, `SVGA3dSurfaceImageId`, and `SVGA3dSubSurfaceId`.
- `SVGA3dSurfaceFormat`: large format enum spanning legacy, DX, compressed, typeless, YUV, depth/stencil, integer, normalized, floating point, and buffer formats.
- Surface flags: 64-bit `SVGA3dSurfaceAllFlags` split into `Surface1`/`Surface2`, plus disallowed masks for host-backed, present, 2D, screen target, buffer, multisample, staging, logicops, DX-only, and SM5 cases.
- Render/texture/pipeline enums: render state names, blend/cull/fill/shade/compare/stencil/fog/primitive/transform/texture-stage enums, render targets, texture filters, addressing, and texture operations.
- Shader/query/cotable/MOB types: shader types and constants, query types/results, object-table types, cotable types, MOB formats, multisample pattern/quality, and frame update type.
- Logic operation and transfer definitions: logic op IDs, ROP3 values, transfer/copy types, and query result unions.

## Control Flow

The header has no executable control flow. Its enums and structs drive validation and serialization in command construction, resource creation, state tracking, and host capability interpretation.

## State and Persistence Behavior

The types model persistent virtual GPU objects and state but do not own storage. Persistent state appears in surfaces, contexts, shaders, queries, cotables, MOBs, and command buffers managed by vmwgfx and the host.

## Dependencies and Integration Points

- Includes `vm_basic_types.h` for VMware fixed-width integer aliases and constants.
- Included by command, DX, devcap, and surface-definition headers.
- Numeric values and bit masks are host ABI, so they must align with the VMware SVGA virtual device implementation.

## Risks and Edge Cases

- Enum values are serialized to the device. Renumbering or removing dead slots breaks ABI compatibility.
- Surface flags use 64-bit constants and masks; accidental 32-bit truncation can lose high feature bits such as multisample, UAV, raw views, structured buffers, or staging copy.
- Disallowed masks encode subtle capability rules. Validation must apply the mask appropriate to resource type and command generation.
- Geometry and size fields are unsigned in many places; arithmetic for boxes, pitches, mip levels, and array layers must guard overflow and underflow.
- Query-result unions are untagged and require the query type to choose the right interpretation.

## Test Signals

- ABI tests should check representative enum numeric values, surface flag width, and struct sizes.
- Resource validation tests should cover invalid formats, incompatible flag combinations, buffer stride limits, staging masks, multisample restrictions, and DX/SM feature gating.
- Query tests should cover each query type's result layout and state transitions.
