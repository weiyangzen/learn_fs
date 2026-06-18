# sources/distributed-fs/ceph-client/drivers/gpu/drm/rockchip/rockchip_drm_vop.c

## Purpose

`rockchip_drm_vop.c` implements the legacy Rockchip VOP display controller as a DRM CRTC with primary, cursor, and overlay planes. It programs windows, scaling, AFBC, color conversion, gamma LUTs, timings, vblank/event delivery, runtime PM, clocks, resets, and component bind/unbind.

## Important APIs, Types, and Functions

- `struct vop` is the persistent controller state: DRM CRTC, clocks, reset, register base, LUT base, register shadow, locks, IRQ, completions, pending event, flip-work, feature data, optional RGB encoder, and windows.
- `vop_reg_set()` centralizes masked register writes and maintains `regsbak`.
- Plane callbacks validate scaling/AFBC/YUV constraints and program addresses, format, mirrors, scaling, YUV coefficients, alpha, and AFBC.
- CRTC callbacks validate modes, round dclk, enable/disable hardware, program output/timings/dither/gamma, flush cfg-done, and deliver events.
- `rockchip_drm_wait_vact_end()` exports a line-flag wait helper.

## Control Flow

Bind allocates state, maps MMIO/LUT memory, initializes windows, creates planes/CRTC, enables runtime PM, resets hardware, snapshots registers, disables windows, requests IRQ, optionally creates RGB, and initializes DMA mapping. Atomic enable resumes PM, enables clocks, attaches DMA mapping, restores registers, disables stale windows, and programs output from `rockchip_crtc_state`. Plane update programs scanout from `rockchip_gem_object` DMA addresses. Flush enables AFBC if needed, writes cfg-done, handles page-flip events, and queues old framebuffer unrefs. Disable waits for DSP hold before detaching IOMMU and clocks.

## State and Persistence Behavior

`regsbak` mirrors registers across power loss. `win_enabled` tracks windows restored after self-refresh. `is_enabled` gates register and IRQ access. `event` and `pending` coordinate vblank completion and deferred framebuffer release. Completions synchronize DSP hold and line-flag interrupts.

## Dependencies and Integration Points

The driver depends on DRM atomic/GEM/vblank/flip-work/self-refresh helpers, runtime PM, clocks, resets, IOMMU attach/detach, SoC register data, Rockchip GEM DMA addresses, `rockchip_crtc_state`, and optional `rockchip_rgb`. Analogix DP CRC hooks are optional.

## Risks and Edge Cases

Register shadowing requires all non-write-mask updates to use `vop_reg_set`. AFBC is limited to one plane and rejects offsets/rotation. Async cursor updates can accumulate old framebuffer references before vblank. Disable relies on a DSP hold IRQ timeout to avoid memory-bus hangs. Shared IRQ handling must distinguish VOP from IOMMU interrupts.

## Test Signals

Test linear RGB/YUV scanout, AFBC validation, scaling limits, YUV odd-source rejection, reflection, alpha blending, async cursor updates, gamma, self-refresh, suspend/resume register restoration, vblank events, line-flag waits, shared IRQ behavior, and IOMMU faults.
