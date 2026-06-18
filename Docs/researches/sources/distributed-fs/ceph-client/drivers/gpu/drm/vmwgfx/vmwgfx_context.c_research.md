# sources/distributed-fs/ceph-client/drivers/gpu/drm/vmwgfx/vmwgfx_context.c

## Purpose
Implements user-visible SVGA3D context resources for legacy, guest-backed, and DX contexts. It connects TTM handle lifetime, vmwgfx resource lifetime, context MOB binding/unbinding, binding state, command-buffer resource managers, DX cotables, and DX query MOB ownership.

## Important APIs, Types, And Functions
- `struct vmw_user_context` embeds `ttm_base_object`, `vmw_resource`, binding state, command-buffer resource manager, cotable array, cotable lock, and optional DX query MOB.
- Resource function tables define legacy, GB, and DX context capabilities, memory domains, and callbacks.
- `vmw_context_init()` chooses legacy FIFO context creation or guest-backed initialization depending on MOB support.
- `vmw_gb_context_create/bind/unbind/destroy()` and `vmw_dx_context_create/bind/unbind/destroy()` emit context commands.
- `vmw_dx_context_scrub_cotables()` scrubs bindings and all cotables in safe order.
- User ioctls create/destroy handles and select legacy versus DX context type.
- Accessors expose binding list/state, command-buffer resource manager, cotables, and DX query MOB binding.

## Control Flow
Context define allocates `vmw_user_context`, initializes a vmwgfx resource, optionally creates binding state, command-buffer resource manager, and DX cotables, then creates a TTM base handle. Legacy contexts emit `CONTEXT_DEFINE` immediately. Guest-backed and DX contexts allocate IDs on create, bind a MOB on validation, scrub bindings/cotables before unbind, optionally read back state, then bind invalid MOB and fence the backup BO. Destroy tears down resource-manager state, binding state, device context, pinned query BOs, cotable references, and TTM handle references.

## State, Persistence, Dependencies, And Integration
State is in memory: resource ID, guest-memory dirty flag, binding state, cotable resources, command-buffer managed resources, and DX query MOB pointer. It depends on TTM object handles, vmwgfx resource core, command submission, BO fencing, binding mutex, cmdbuf mutex, and SVGA context/cotable command definitions. The file is central to execbuf context lookup, resource validation, cotable allocation, query management, binding scrub/rebind, and user ioctls.

## Risks And Test Signals
Risks include lock-order violations during context/cotable scrub, leaked cotables or command-buffer resources on partial initialization, invalid query MOB association, and failing to scrub bindings before context swapout. Test signals include legacy and DX define/destroy ioctls, unsupported DX rejection, context MOB bind/unbind with readback, cotable scrub order, query MOB replacement denial, file-close cleanup, and context destruction while resources remain bound.
