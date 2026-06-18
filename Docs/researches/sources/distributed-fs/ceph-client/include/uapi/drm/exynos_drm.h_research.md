# sources/distributed-fs/ceph-client/include/uapi/drm/exynos_drm.h

## Purpose

`exynos_drm.h` defines Samsung Exynos DRM driver-specific UAPI for GEM buffers, virtual display connection, legacy G2D command submission, and IPP v2 image post-processing. It maps Exynos-specific memory and image-processing hardware onto DRM GEM handles, FourCC formats, modifiers, rotation flags, and DRM events.

## Important APIs, Types, And Constants

GEM APIs are `drm_exynos_gem_create`, `drm_exynos_gem_map`, and `drm_exynos_gem_info`, with memory/cache flags for contiguous/non-contiguous, cacheable/non-cacheable, and write-combine memory. VIDI uses `drm_exynos_vidi_connection` for virtual connector state and optional EDID.

G2D APIs include version, command, userptr, command-list, and exec structs plus event type constants. IPP v2 provides resource enumeration, capabilities and formats, limits, task chunks for buffers/rectangles/transforms/alpha, and commit. IPP flags support event generation, test-only validation, and nonblocking execution. Events are `DRM_EXYNOS_G2D_EVENT` and `DRM_EXYNOS_IPP_EVENT`.

## Control Flow

GEM flow creates a BO, maps it through a fake offset, or queries size/flags. VIDI flow changes virtual display connection and optional EDID state. G2D flow queries version, sends a command list and buffers/userptrs, then executes synchronously or asynchronously with optional events. IPP flow enumerates modules, queries formats/capabilities, queries limits for a FourCC/modifier/type pair, then commits a packed typed task array. `TEST_ONLY` validates without execution; `NONBLOCK` and `EVENT` select asynchronous completion behavior.

## State And Persistence

GEM handles and mmap offsets persist for the DRM file/object lifetime. VIDI connection state persists until changed or reset. G2D and IPP commits are transient jobs, while event structs carry user data, timestamps, and sequence/cmdlist identifiers. IPP hardware capabilities are queried runtime state and can vary by SoC.

## Dependencies And Integration Points

The file includes `drm.h` and consumes `drm_fourcc.h` and `drm_mode.h` concepts by contract. Integration points include Exynos GEM memory backends, G2D, VIDI, IPP hardware, DRM events, libdrm/test tools, and media/compositor pipelines using scaling, rotation, crop, conversion, and alpha.

## Risks

`drm_exynos_g2d_userptr` uses `unsigned long`, which is a 32/64-bit ABI concern. Pointer arrays need strict copy-from-user and size validation. GEM cache/memory flags may be unsupported on some SoCs. IPP task arrays are self-describing and can be malformed by missing, duplicated, or inconsistent task chunks. `TEST_ONLY` must not mutate state, and event `user_data` must round-trip correctly.

## Test Signals

Tests should cover GEM create/map/get flags, VIDI connect/disconnect and EDID extension handling, G2D version and command-list validation, async event delivery, IPP resource/caps/limits enumeration, IPP test-only commits, valid/invalid task arrays, rotation/reflection support, FourCC/modifier rejection, nonblocking completion, and 32-bit compat behavior.
