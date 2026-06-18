# sources/distributed-fs/ceph-client/include/uapi/drm/radeon_drm.h

## Purpose
This file is the long-lived public ABI for the legacy Radeon DRM driver. It preserves pre-KMS SAREA/CP command submission interfaces, old memory-manager and IRQ ioctls, and newer KMS GEM/CS/VM ioctls. Much of the file exists for backward compatibility with old X server and Mesa userspace, so numeric constants and structure layouts are effectively immutable.

## Important APIs and types
The legacy side defines upload/state flags, command-buffer packet IDs, R100/R200/R300 command headers, clear/primitive flags, texture heap constants, context register snapshots, texture register snapshots, primitive records, and `drm_radeon_sarea_t` shared-area state. Legacy ioctls include CP init/start/stop/reset/idle, fullscreen, swap, clear, vertex/indices/vertex2, command buffer, texture upload, indirect buffer, get/set param, memory alloc/free/init heap, IRQ emit/wait, surface alloc/free, and tiling toggles.

The KMS/GEM side defines domains (`CPU`, `GTT`, `VRAM`), `drm_radeon_gem_info`, GEM create/userptr/mmap/pread/pwrite/set-domain/wait-idle/busy/set/get-tiling/op, VM mapping via `drm_radeon_gem_va`, command submission chunks via `drm_radeon_cs_chunk`, relocations via `drm_radeon_cs_reloc`, and `drm_radeon_info` query IDs for device identity, tiling, clocks, rings, firmware, memory usage, temperature, reset counters, and virtual-address support.

## Control flow and state
Legacy userspace initializes the command processor, communicates state through SAREA structures and command buffers, performs clears/draws/swaps, manages old GART/FB memory regions, and waits on IRQ sequence numbers. KMS userspace queries memory sizes, creates GEM BOs in an initial domain, optionally configures tiling and userptr backing, maps/preads/pwrites or sets access domains, maps BOs into a VM address with readable/writeable/system/snooped flags, and submits command streams as chunk arrays containing IBs, relocations, flags, and ring/priority selection.

## State and persistence behavior
Legacy SAREA fields persist in shared memory and include cliprects, throttle counters, texture LRU data, CRTC/page state, and tiling state. GEM handles persist until closed. Tiling flags, initial domain, userptr registration, and VM mappings are persistent BO attributes or VM entries. CS submission updates returned `gart_limit` and `vram_limit` budget fields, making memory-pressure state visible to userspace. Info queries expose dynamic telemetry such as usage, clocks, temperature, and reset counter.

## Dependencies and integration points
The file depends on `drm.h` for clip rectangles, texture regions, ioctl encoding, and pointer annotations. It integrates with old DRI/X server SAREA contracts, Mesa command stream generation, KMS GEM memory management, VM address-space management, UVD/VCE/compute rings, and GPU tiling mode arrays. Several comments explicitly warn that definitions are mirrored in X server headers and cannot be changed.

## Risks and test signals
Risks are high because this header combines historical ABI and modern GEM ABI. Changing packet IDs, SAREA layout, ioctl numbers, tiling bits, or info IDs can break old userspace. Security-sensitive areas include userptr memory, command stream parsing, relocations, register read queries, VM map/unmap, and legacy userspace pointers. Test signals should include old ioctl compat coverage, 32-bit pointer compat for legacy pointer fields, GEM domain transitions, tiling set/get, userptr fallback behavior, CS chunk validation, invalid ring IDs, VM duplicate/unmap results, info-query bounds, and reset-counter observation.
