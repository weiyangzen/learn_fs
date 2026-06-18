# sources/distributed-fs/ceph-client/drivers/gpu/drm/vmwgfx/vmwgfx_binding.h

## Purpose
Declares the binding-manager data model shared by execbuf validation, context lifecycle, resource eviction, and cotable code. The header defines abstract binding types and per-binding metadata structs that store enough SVGA device data to reconstruct unbind and rebind commands.

## Important APIs, Types, And Functions
- `enum vmw_ctx_binding_type` covers legacy shader/render-target/texture bindings and DX shader, render target, shader resource, depth-stencil, stream-output, vertex/index buffer, UAV, compute UAV, and stream-output state bindings.
- `struct vmw_ctx_bindinfo` is the common list node with context/resource pointers, binding type, and scrubbed flag.
- Derived structs add device-specific fields such as shader slot, texture stage, view slot, constant-buffer offset/size, stream-output target range, vertex-buffer stride, index-buffer format, UAV splice index, and stream-output slot.
- `struct vmw_dx_shader_bindings` groups shader, constant-buffer, and shader-resource state per shader type.
- Public functions add/update bindings, commit staged state, scrub/kill resource or context lists, rebind all scrubbed state, allocate/free/reset binding state, expose the active list, and report whether a binding dirties its resource.

## Control Flow
Callers prepare a `vmw_ctx_bindinfo`-derived object from parsed command data, then call `vmw_binding_add()` with shader and slot indexes. Execbuf later commits staged state into persistent context state. Eviction/destruction callers scrub or kill by context or resource list. Restore callers rebind all scrubbed entries.

## State, Persistence, Dependencies, And Integration
The opaque `struct vmw_ctx_binding_state` is allocated in the implementation. The metadata structs store non-refcounted pointers, so callers must hold the global binding mutex and maintain resource lifetime ordering. The header depends on Linux lists and SVGA3D register definitions and is consumed by binding implementation, context code, resource validation/destruction, and resources with binding lists.

## Risks And Test Signals
Risks include constructing the wrong derived bindinfo for a binding type, slot/shader indexes beyond fixed arrays, and using returned lists after dropping the binding mutex. Test signals include each binding type's add, commit, scrub, rebind, and kill path; constant-buffer offset updates; UAV splice index tracking; and dirty classification for render/depth/stream-output/UAV resources.
