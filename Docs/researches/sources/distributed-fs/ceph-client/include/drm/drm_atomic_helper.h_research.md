# sources/distributed-fs/ceph-client/include/drm/drm_atomic_helper.h

## Purpose
This header declares the standard helper layer for atomic KMS validation, commit sequencing, legacy ioctl emulation, suspend/resume duplication, nonblocking commit synchronization, plane iteration, and plane enable/disable predicates. It is the common path for drivers that rely on DRM core helpers instead of implementing the full atomic sequence manually.

## Important APIs, types, and functions
Important declarations include `drm_atomic_helper_check_modeset`, `drm_atomic_helper_check_plane_state`, `drm_atomic_helper_check_planes`, `drm_atomic_helper_check`, `drm_atomic_helper_commit`, `drm_atomic_helper_commit_tail`, `drm_atomic_helper_commit_tail_rpm`, async check/commit helpers, fence/vblank/flip waits, modeset disable/enable helpers, plane prepare/commit/cleanup helpers, `drm_atomic_helper_swap_state`, and nonblocking helpers `drm_atomic_helper_setup_commit`, `drm_atomic_helper_wait_for_dependencies`, `drm_atomic_helper_commit_hw_done`, and `drm_atomic_helper_commit_cleanup_done`. Macros include `DRM_PLANE_NO_SCALING`, plane commit flags, and CRTC plane iterators.

## Control Flow
A helper commit normally checks modesets and planes, prepares plane resources, swaps state, disables old modesets, programs modes and planes, enables new modesets, waits for fences/vblanks/flips, and cleans old planes. Nonblocking commits first set up `drm_crtc_commit` dependencies, run the tail in work context, and signal the hardware and cleanup completion points.

## State and Persistence
The helpers mutate atomic state ownership and current object state through `swap_state`, but this header itself only declares the flow. Legacy helpers translate `set_config`, update-plane, disable-plane, and page-flip requests into atomic transactions. Suspend/resume helpers duplicate and restore display state.

## Dependencies and Integration Points
It integrates with mode config helper vtables, CRTC/plane/connector state, fences, bridge chaining, writeback connectors, runtime PM variants, and legacy IOCTL entry points. `drm_atomic_helper_bridge_propagate_bus_fmt` ties bridge bus-format negotiation into the atomic helper path.

## Risks and Test Signals
Risk areas are incorrect commit-stage ordering, missing cleanup signaling, plane enable/disable states where CRTC and framebuffer are inconsistent, failures after plane preparation, async update checks bypassing full validation, and legacy entry points producing incomplete atomic state. Tests should exercise blocking and nonblocking commits, dependency waits across multiple CRTCs, vblank/flip waits, plane scaling limits, active-only plane commit flags, suspend/resume duplicated-state commits, and legacy page-flip target paths.
