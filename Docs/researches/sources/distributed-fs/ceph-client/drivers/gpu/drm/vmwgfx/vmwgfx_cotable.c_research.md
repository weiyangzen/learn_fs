# sources/distributed-fs/ceph-client/drivers/gpu/drm/vmwgfx/vmwgfx_cotable.c

## Purpose
Treats DX context object tables as vmwgfx resources with guest-memory backing so they participate in the same MOB validation, eviction, readback, fencing, and resize mechanisms as other resources. Cotables hold device-side records for views, shaders, stream output, queries, UAVs, and fixed-function DX state objects.

## Important APIs, Types, And Functions
- `struct vmw_cotable` embeds `vmw_resource`, stores owning context, readback size, highest seen entry, cotable type, scrubbed state, and active resource list.
- `co_info[]` defines initial entry counts, entry sizes, and optional unbind/scrub callbacks per cotable type.
- `vmw_cotable_scrub_order[]` enforces a safe scrub order for binding-bearing cotables.
- Resource callbacks `vmw_cotable_create()`, `vmw_cotable_bind()`, `vmw_cotable_unbind()`, and `vmw_cotable_destroy()` implement validation lifecycle.
- `vmw_cotable_scrub()` partially unbinds without requiring backup BO reservation.
- `vmw_cotable_unscrub()` rebinds the cotable MOB to the context.
- `vmw_cotable_resize()` allocates a larger MOB, reads back old contents, page-copies data, switches backing, and rebinds.
- `vmw_cotable_notify()` records highest used object-table ID and triggers resize on next validate.

## Control Flow
Allocation initializes a guest-backed resource with at least one page or type-specific minimum size, marks it scrubbed, and stores the owning context. Notify raises `seen_entries` and invalidates `res->id` so validation calls create. Create either unscrubs an attached MOB or doubles the backing size until it fits the highest seen entry. Scrub optionally calls type-specific list cleanup, emits readback plus `SET_COTABLE` with invalid MOB, marks scrubbed, and invalidates the resource. Full unbind delegates to context cotable scrub under binding mutex and fences the backup BO.

## State, Persistence, Dependencies, And Integration
Cotable contents live in guest-memory MOBs and are read back across eviction, but there is no disk persistence. Dependencies include vmwgfx resource core, BO creation/mapping/fencing, command submission, binding mutex, MKS statistics, and type-specific view/shader/stream-output cleanup helpers. Cotables are allocated by DX context initialization and accessed by `vmw_context_cotable()`.

## Risks And Test Signals
Risks include unrecoverable state if resize fails after device switch, incorrect readback size, scrub order regressions causing invalid context swapin, page-copy assumptions when old/new sizes differ, and missing type info when new cotables are added. Test signals include notify-triggered growth, resize after high object IDs, readback and unbind fencing, scrub/unscrub cycles, cotable destruction while resources are listed, SM4 versus SM5 cotable count, and callbacks for views/shaders/stream-output resources.
