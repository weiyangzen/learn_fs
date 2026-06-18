# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gem/i915_gem_internal.c

## Purpose
Implements volatile driver-private GEM objects backed by directly allocated pages rather than swappable shmem. These are for internal hardware-facing buffers whose contents are valid only while pinned and may be discarded by the shrinker.

## Important APIs and Functions
`i915_gem_object_get_pages_internal()` allocates sg-table backing with high-order page fallback and DMA segment limits. `i915_gem_object_put_pages_internal()` finishes GTT mappings, frees pages, clears dirty state, and restarts CPU write-domain tracking. `__i915_gem_object_create_internal()` initializes the private object with supplied ops, and `i915_gem_object_create_internal()` uses the default internal ops.

## Control Flow
Creation checks nonzero page-aligned size and size overflow, allocates an i915 object, initializes private DRM GEM metadata, marks struct-page and volatile flags, sets CPU domains, and configures default cache coherency. Page population lazily allocates an sg table, fills it with decreasing allocation orders, retries single-page segments if DMA mapping high-order segments fails, then installs pages. Release reverses GTT preparation and frees all pages.

## State and Persistence Behavior
Object metadata persists, but contents are volatile and only valid while active/pinned. State includes struct-page backing, shrinkable backend ops, volatile flag, CPU read/write domains, cache coherency/dirty flags, and `mm.dirty`.

## Dependencies and Integration Points
Uses scatterlist/page allocation, i915 sg segment sizing, GTT page prepare/finish helpers, object initialization, and cache-domain helpers. Internal driver users consume these objects through normal GEM object APIs.

## Risks
Pages are not cleared on allocation, so consumers must initialize before hardware visibility. DMA segment and i965 DMA32 restrictions must remain correct. Exposing volatile internal objects as durable userspace buffers would be wrong.

## Test Signals
Object/shrinker selftests and internal users that pin/unpin/repopulate buffers exercise this backend. Fault injection and low-memory stress cover allocation fallback. Assertions validate size/alignment.
