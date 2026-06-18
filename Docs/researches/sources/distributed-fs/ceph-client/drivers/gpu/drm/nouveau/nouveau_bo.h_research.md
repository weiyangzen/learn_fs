# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nouveau_bo.h

Purpose: Declares Nouveau's BO wrapper around `struct ttm_buffer_object` and the BO management/migration API used by GEM, display, channels, VMM, and TTM callbacks.

Important APIs/types: `struct nouveau_bo` stores placement, valid domains, kernel map, reserve metadata, root GEM sharing state, GPU offset, VMA list, contiguity/page/kind/compression/tile metadata, and legacy tile region. Public APIs cover allocation/init/new helpers, pin/unpin, map/unmap, placement changes, register-style read/write helpers, TTM fault notification, fence attachment, validation, CPU/device DMA sync, IO-reserve LRU management, and convenience create-pin-map helpers. It also declares generation-specific move init/copy entry points: `nv04`, `nv50`, `nv84`, `nva3`, `nvc0`, and `nve0`.

Control flow/state contract: Callers allocate and initialize BOs through `nouveau_bo_new()` or convenience helpers, reserve before locked pin/unpin paths, use `nouveau_bo_validate()` after changing placement, and finish through `nouveau_bo_fini()` or `nouveau_bo_unpin_del()`. `nvbo_kmap_obj_iovirtual()` asserts that a mapped BO is iomem when raw MMIO-style access is needed.

Dependencies/integration: Includes DRM GEM and TTM placement/BO headers and forward-declares Nouveau channel, client, DRM, fence, and VMA types. The DRF macros at the end adapt Nouveau register field helpers to BO-backed memory accesses.

Risks: API misuse can break TTM reservation rules, leak pins, or access unmapped `kmap` memory. The compact bitfields for page/kind/comp/zeta must stay aligned with hardware/MMU limits. Test signals include compile coverage from all users, BO lifetime under error injection, mmap/page-fault tests, migration tests across all declared copy engines, and lockdep for reserve-held operations.
