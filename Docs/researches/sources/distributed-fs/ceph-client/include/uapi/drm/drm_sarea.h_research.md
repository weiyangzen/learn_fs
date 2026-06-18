# sources/distributed-fs/ceph-client/include/uapi/drm/drm_sarea.h

## Purpose

`drm_sarea.h` defines the legacy DRM shared area (SAREA) ABI used by old direct-rendering stacks. SAREA is a shared memory area containing DRM locks, drawable metadata, frame dimensions, and a dummy context. It remains UAPI for compatibility, although modern GEM/KMS paths generally do not depend on it.

## Important APIs, Types, And Constants

`SAREA_MAX` is architecture-dependent: 8 KiB for most architectures and Alpha, 16 KiB for MIPS, and 64 KiB for IA-64. `SAREA_MAX_DRAWABLES` is 256, and `SAREA_DRAWABLE_CLAIMED_ENTRY` marks claimed drawable entries. `struct drm_sarea_drawable` stores a stamp and flags. `struct drm_sarea_frame` stores x/y/width/height/fullscreen. `struct drm_sarea` embeds `struct drm_hw_lock lock`, `struct drm_hw_lock drawable_lock`, a drawable table, a frame, and `drm_context_t dummy_context`. Legacy typedef aliases are exposed outside the kernel.

## Control Flow

The header defines shared-memory layout rather than functions. Legacy userspace maps the SAREA, synchronizes through `drm_hw_lock`, and reads or updates drawable and frame records. The first member of `struct drm_sarea` must remain the primary DRM locking structure so old lock code can interpret the mapped region.

## State And Persistence

SAREA contents are mutable shared kernel/userspace state for the lifetime of the mapping and DRM context. They do not persist across device close, driver unload, or process lifetime. Locks and drawable records can become stale if old clients fail or exit while holding state.

## Dependencies And Integration Points

The file includes `drm.h` for `struct drm_hw_lock` and `drm_context_t`. Its integration points are legacy DRM locking/context APIs and old DRI clients/drivers. It is not the path for modern dma-fence, DRM syncobj, GEM BO synchronization, or atomic KMS.

## Risks

ABI layout changes would break clients that directly map and dereference the shared area. Architecture-specific sizing must keep `struct drm_sarea` within `SAREA_MAX`. Shared lock failure can deadlock old clients. The fixed 256-entry drawable table is a hard capacity limit. Memory-ordering expectations are historical and not described with modern primitives.

## Test Signals

Compatibility signals include UAPI compile checks, `sizeof(struct drm_sarea) <= SAREA_MAX` on supported architectures, legacy DRI/SAREA smoke tests if available, field-offset checks for the leading lock, and ABI-diff checks that no fields are reordered or resized.
