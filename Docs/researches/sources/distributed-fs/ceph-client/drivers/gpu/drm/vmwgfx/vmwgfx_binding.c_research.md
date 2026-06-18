# sources/distributed-fs/ceph-client/drivers/gpu/drm/vmwgfx/vmwgfx_binding.c

## Purpose
Implements the vmwgfx context binding manager. It tracks every resource bound into a context so bindings can be scrubbed before resources or contexts are swapped out, killed before resources are destroyed, and rebound after guest-backed contexts are restored.

## Important APIs, Types, And Functions
- `struct vmw_ctx_binding_state` stores fixed arrays for legacy textures/shaders and DX render targets, depth-stencil view, shader resources, constant buffers, stream-output targets, vertex/index buffers, UAVs, stream output, dirty bitmaps, and temporary command buffers.
- Static `vmw_binding_infos[]` maps binding type to storage size, per-shader offsets, and scrub function.
- `vmw_binding_add()`, `vmw_binding_state_commit()`, and `vmw_binding_transfer()` move staged execbuf binding data into persistent context state.
- `vmw_binding_state_scrub()`, `vmw_binding_res_list_scrub()`, `vmw_binding_state_kill()`, and `vmw_binding_res_list_kill()` remove device-visible references.
- `vmw_binding_rebind_all()` recreates scrubbed bindings when resources have valid IDs.
- `vmw_binding_dirtying()` identifies bindings that make the referenced resource GPU-writable.

## Control Flow
Execbuf validation builds temporary binding state. After commands are submitted, commit transfers entries into the context state and adds each to both the context list and resource binding list. Scrub walks either a context list or a resource list, emits unbind commands or dirty marks, sets `scrubbed`, then flushes batched commands. Rebind walks scrubbed entries with valid resources, emits bind commands through the same scrub functions with `rebind=true`, clears `scrubbed`, and emits dirty batches.

## State, Persistence, Dependencies, And Integration
State is entirely in memory and protected externally by `dev_priv->binding_mutex`. Binding entries intentionally hold non-refcounted context/resource pointers and rely on the resource subsystem and binding lists for ordering. Commands are emitted through vmwgfx command reservation helpers. The code is called from context unbind/destroy, cotable scrub, resource eviction/destruction, execbuf validation, and dirty tracking.

## Risks And Test Signals
Risks include stale non-refcounted pointers, missing dirty-bit emission, binding type array offset mistakes, batched command size overflows, and adding a new binding type without updating build assertions or dirtying classification. Test signals include context swapout with active bindings, resource eviction while bound in multiple contexts, DX SRV/UAV/RT/VB batch ranges, rebind after MOB restore, and destruction of bound views/shaders/stream-output objects.
