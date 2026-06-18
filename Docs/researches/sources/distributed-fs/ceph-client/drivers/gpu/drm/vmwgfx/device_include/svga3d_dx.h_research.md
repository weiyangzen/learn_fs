# sources/distributed-fs/ceph-client/drivers/gpu/drm/vmwgfx/device_include/svga3d_dx.h

## Purpose

`svga3d_dx.h` defines the VMware SVGA DX command and state ABI. It maps Direct3D 10/11-style resources, views, shaders, constant buffers, samplers, blend/depth/rasterizer state, queries, stream output, unordered-access views, staging copies, shader interfaces, and context MOB layouts into packed FIFO payload structures.

## Important APIs, Types, and Functions

- DX limits and IDs: vertex buffers, inputs, stream-output targets, shader-resource views, constant buffers, samplers, class instances, and object ID typedefs.
- Pipeline commands: `SVGA3dCmdDXSetSingleConstantBuffer`, shader resource/sampler/shader binds, draw/dispatch variants, input layout, vertex/index buffers, topology, render targets, blend/depth/rasterizer state, viewports, scissor rects, and clears.
- Query commands: define/destroy/bind/begin/end/readback/move/all-query/predication payloads and `SVGADXQueryDeviceState`.
- Copy/transfer commands: predicated copies, staging copies, buffer copies, convert/resolve transfers, surface copy/readback, transfer-to/from-buffer, and subresource update/readback/invalidate.
- View definitions: shader-resource, render-target, depth-stencil, unordered-access, and buffer-ex view descriptors.
- State-object definitions: input element layout, blend state, depth/stencil state, rasterizer state, sampler state, shader signatures, shader definitions, stream-output definitions, and COTable commands.
- Context MOB formats: `SVGADXInputAssemblyMobFormat`, `SVGADXContextMobFormat`, and `SVGADXShaderIfaceMobFormat` define host/guest shared backing layouts for DX context state.

## Control Flow

The file is declarative. Runtime flow is command submission: vmwgfx emits command IDs from `svga3d_cmd.h` and payloads from this header to mutate DX context state, bind resources, issue draws/dispatches, manage queries, and copy data. Context MOB structures provide a persistent snapshot format for binding, readback, invalidation, and recovery of complex DX pipeline state.

## State and Persistence Behavior

Most structures represent persistent virtual GPU state: context bindings, shader/interface state, cotables, view objects, state objects, query results, stream-output declarations, UAV bindings, and resource views. The header also defines transient operation payloads for draw, dispatch, clear, copy, update, and transfer commands. State lives in host resources and guest MOBs; packed structures are the serialized representation.

## Dependencies and Integration Points

- Includes `svga_reg.h`, `svga3d_limits.h`, and `svga3d_types.h`.
- Integrated by vmwgfx DX context, cotable, shader, surface/view, binding, stream-output, and execbuf validation code.
- Shares object type and command ID contracts with `svga3d_cmd.h`, `svga3d_types.h`, and host SVGA DX implementation.

## Risks and Edge Cases

- Many structures are packed ABI payloads with mixed 8/16/32-bit fields. Padding or signedness changes can break host compatibility.
- Several command families use implicit arrays following a fixed header, controlled by counts such as number of views, samplers, viewports, scissor rects, stream-output entries, or shader class instances.
- Context MOB formats contain large fixed arrays and reserved padding. Size drift or incomplete initialization can leak stale state to the host or corrupt context restore.
- Resource view descriptors are unions keyed by resource type/format. Validators must ensure the active union arm matches the surface/resource type.
- UAV and DX11.1 limits differ from earlier DX limits; capability gating must be precise.

## Test Signals

- ABI tests should check `sizeof` and offsets for packed command and MOB format structures.
- Execbuf validation should cover count-driven variable payloads, invalid object IDs, unsupported command IDs under lower caps, view/resource type mismatches, and copy/transfer bounds.
- Context save/restore and readback/invalidate tests should compare `SVGADXContextMobFormat` contents across bind/readback cycles.
- Rendering tests should cover draw/dispatch, queries, predication, stream output, UAVs, shader interfaces, and staging copies on supported virtual hardware.
