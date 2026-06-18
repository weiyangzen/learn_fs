# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_lrc.h

## Purpose
`xe_lrc.h` declares the Logical Ring Context public API, creation flags, snapshot structure, fixed PPHWSP scratch offsets, WA BB size, and inline refcount/ring-size helpers.

## Important APIs, Types, And Functions
- `struct xe_lrc_snapshot` captures context descriptor, ring pointers, seqnos, timestamps, and optional copied HW context data.
- Creation flags include runalone, PXP, user context, and disabling a state-cache performance fix.
- Declares lifecycle, ring, descriptor, seqno, GGTT-address, context-register, memory IRQ update, default dump/lookup, HWE state emission, priority, snapshot, scratch, and timestamp APIs.
- `xe_lrc_ring_size()` currently returns 16 KiB.

## Control Flow
Execution queue and GT code use this API to allocate contexts, write rings, create fences, dump/debug contexts, and update utilization. Refcount helpers wrap `kref`.

## State And Persistence
The header defines snapshot persistence fields and exposes operations over the LRC state defined in `xe_lrc_types.h`.

## Dependencies And Integration Points
It includes `xe_lrc_types.h` and forward-declares Xe execution, GT, VM, HWE, DRM printer, and BB structures. It is a central contract for scheduler, exec queue, debug, and reset/recovery code.

## Risks
API breadth means changes to LRC layout or flags can ripple widely. Snapshot structures carry BO references and must be freed with the matching helper. Callers must respect ring-space and register-index conventions.

## Test Signals
Build coverage for all users, refcount lifetime tests, snapshot allocation/free paths, and ABI-like validation of creation flags and fixed offsets used by other modules.
