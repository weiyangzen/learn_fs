## sources/distributed-fs/ceph-client/drivers/gpu/drm/loongson/lsdc_ttm.h

### Purpose

`lsdc_ttm.h` declares the Loongson LSDC TTM/GEM buffer-object interface and defines the domain flags used by the driver to describe preferred storage in system memory, TT/GTT, or VRAM.

### Important APIs, types, and functions

The central type is `struct lsdc_bo`, embedding `struct ttm_buffer_object` plus GEM list linkage, `iosys_map`, vmap/sharing counters, kmap state, size, initial domain, and a fixed placement array. Inline helpers convert `drm_gem_object` and `ttm_buffer_object` pointers to `struct lsdc_bo`. Public declarations cover BO allocation, pinned kernel allocation, reservation, pinning, references, GPU offset/size, kernel mapping, clearing, VRAM eviction, TTM init, and debugfs setup.

### Control flow

The header has no runtime flow beyond type-safe conversions. Callers create an LSDC BO, reserve it, pin or map it as needed, and release it through GEM references. The declared TTM initialization entry point is called during LSDC device bring-up.

### State and persistence behavior

The header defines the object fields that persist across BO lifetime: placement policy, current kmap pointer and IO-memory flag, list membership under `gem.mutex`, and counters used by sharing and virtual mapping paths. Actual resource state is owned by TTM.

### Dependencies

It includes Linux list/container/iosys-map headers and DRM GEM/TTM BO, placement, range-manager, and TT headers. It relies on the surrounding LSDC driver for `struct lsdc_device` declarations.

### Integration points

The API is consumed by LSDC GEM, plane, framebuffer, and device initialization code. It is the common contract between object creation, scanout pinning, CPU access, PRIME sharing, and TTM debugfs.

### Risks

The placement array has four entries, so future domain expansion must keep that capacity in sync. `sharing_count` is documented but not managed here; callers must coordinate cross-device sharing rules. Conversion helpers assume embedded layout and will break if object embedding changes.

### Test signals

Build coverage is the main header-level signal. Runtime validation comes from all users of the declared API: GEM allocation, PRIME import, scanout pinning, CPU mapping, and TTM initialization.
