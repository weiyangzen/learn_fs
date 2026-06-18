# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_display.c

## Purpose

`amdgpu_display.c` implements shared AMDGPU display helpers used by legacy and DC display paths. It handles hotplug work, page flip scheduling, framebuffer creation and validation, format modifier conversion, display properties, scanout position queries, suspend/resume display buffer pinning, and DRM panic scanout-buffer access.

The file sits between DRM/KMS core interfaces and AMDGPU buffer/display internals. Its most sensitive responsibilities are fencing and pinning BOs during page flips, translating AMD tiling metadata into DRM format modifiers, proving framebuffer plane sizes fit in the backing BO, and making scanout state safe across runtime PM and panic paths.

## Important APIs, types, and functions

- `amdgpu_display_hotplug_work_func()` runs outside IRQ context, locks mode config, calls each connector hotplug handler, and emits a DRM HPD event.
- `amdgpu_display_crtc_page_flip_target()` implements the CRTC page-flip path: allocate flip work, pin the new BO, collect write fences, update CRTC state under `event_lock`, and schedule MMIO flip work.
- `amdgpu_display_flip_work_func()` waits on shared fences and avoids issuing a flip too early in vblank before calling the ASIC `page_flip` hook and marking `AMDGPU_FLIP_SUBMITTED`.
- `amdgpu_display_unpin_work_func()` asynchronously unpins and unreferences the old framebuffer BO after the flip lifecycle completes.
- `amdgpu_display_crtc_set_config()` wraps legacy mode setting with runtime PM reference handling and tracks `adev->have_disp_power_ref`.
- `amdgpu_display_user_framebuffer_create()` is `mode_config.fb_create`; it looks up the GEM handle, rejects imported DMA-BUF scanout when the buffer cannot live in a supported domain, allocates `struct amdgpu_framebuffer`, verifies, initializes, and publishes a DRM framebuffer.
- `amdgpu_display_framebuffer_init()` reads BO tiling/TMZ/GFX12-DCC state, verifies legacy tiling or converts tiling flags to modifiers, validates sizes, and aliases all planes to the same BO with proper object references.
- `convert_tiling_flags_to_modifier()` and `convert_tiling_flags_to_modifier_gfx12()` translate AMDGPU tiling flags into DRM AMD modifiers, including DCC and DCC-retile metadata.
- `amdgpu_lookup_format_info()` selects synthetic DRM format descriptions for DCC and DCC-retile buffers.
- `amdgpu_display_verify_sizes()` and `amdgpu_display_verify_plane()` check pitch, offset alignment, and minimum backing BO size for all image, DCC, and retile planes.
- `amdgpu_display_modeset_create_props()` creates common display connector properties, including coherent mode, load detection, scaling mode, underscan, audio, dither, and adaptive backlight modulation.
- `amdgpu_display_get_crtc_scanoutpos()` decodes vblank and current scanout position using display function hooks and applies vblank lead-line correction.
- `amdgpu_display_suspend_helper()` and `amdgpu_display_resume_helper()` disable polling/DPMS, unpin or repin cursor and scanout BOs, and restore modes.
- `amdgpu_display_get_scanout_buffer()` exposes a framebuffer to DRM panic handling, either by mapping the BO or by using indirect MMIO writes for no-CPU-access VRAM BOs.

## Control flow

Hotplug starts from an IRQ-scheduled work item. The worker serializes connector scanning with `mode_config->mutex`, invokes connector-specific handling, then notifies userspace with `drm_helper_hpd_irq_event()`.

Page flip flow starts with `amdgpu_display_crtc_page_flip_target()`. It references the old BO, reserves and pins the new BO in display-supported domains, ensures GART allocation, collects write fences from the new BO reservation object, computes the target vblank, and installs `work` in the CRTC under `event_lock` only if no flip is already pending. `amdgpu_display_flip_work_func()` then waits for each shared fence by registering callbacks; once fences are done and scanout is outside the unsafe pre-target vblank window, it calls the ASIC-specific `page_flip()` hook. Cleanup of the old BO happens in separate unpin work.

Framebuffer creation starts with a GEM handle lookup. Imported DMA-BUFs are rejected when they cannot be scanned out from GTT and cannot be migrated to VRAM. The helper fills DRM framebuffer fields, checks format/modifier support against planes, reads BO metadata, converts missing modifiers from tiling flags, validates image and metadata planes, initializes DRM framebuffer functions, and finally drops the lookup reference while the framebuffer owns its plane references.

Modifier conversion is split by generation. GFX12 uses `GFX12_SWIZZLE_MODE` and GFX12 DCC fields. GFX9-GFX11 derive tile version, block size, XOR bits, packers/RB/pipe metadata, DCC mode, DCC plane offsets, DCC pitch, and optional render DCC retile plane from BO metadata. Size verification recomputes natural block dimensions and ensures every plane offset and pitch satisfies hardware block alignment and does not exceed BO size.

Suspend flow disables KMS polling, DPMSes connectors off under modeset locks, and unpins cursor/front buffers not owned by fbdev helper. Resume repins cursors, restores mode, DPMSes connectors on, and reenables polling.

## State and persistence behavior

The file mutates CRTC page flip state (`pflip_status`, `pflip_works`, `primary->fb`), BO pin counts, BO flags such as `AMDGPU_GEM_CREATE_VRAM_CONTIGUOUS`, framebuffer modifier/format/plane arrays, `adev->have_disp_power_ref`, `adev->mode_info` property pointers, display priority, CRTC scaling state, cursor GPU addresses, and the static `panic_abo` pointer used only under DRM panic locking.

Asynchronous flip state persists between the initial ioctl/helper call, fence callback scheduling, delayed work retries around vblank, flip interrupt completion elsewhere in the driver, and unpin cleanup work. Framebuffer state persists in DRM objects until destroyed by `drm_gem_fb_destroy()`.

## Dependencies and integration points

This file depends on DRM KMS, GEM framebuffer helpers, damage helpers, vblank helpers, EDID/DDC helpers, runtime PM, AMDGPU BO/GEM/TTM helpers, connector/encoder structures, ASIC display function hooks in `adev->mode_info.funcs`, and AMD format modifier macros. It integrates with PRIME/DMA-BUF policy by rejecting imported buffers that cannot be displayed safely, and with `drm_panic` through `get_scanout_buffer`.

## Risks and edge cases

- Page-flip error paths must drop BO references, fences, pins, reservations, and allocated work exactly once. Mistakes produce leaks, stuck pinned BOs, or use-after-free in fence callbacks.
- Flip scheduling intentionally delays around vblank to avoid submitting too early. Incorrect scanout position or target vblank math can cause missed flips, tearing, or long delays.
- Framebuffer modifier conversion is generation-sensitive. New tiling modes, DCC variants, or incorrect `gb_addr_config_fields` can yield invalid modifiers or reject valid scanout buffers.
- The code requires all planes of multi-plane framebuffers to use the same BO before modifier conversion. This is an AMD-specific assumption that can reject otherwise legal DRM layouts.
- DCC retile offset extraction depends on opaque BO metadata layout and ASIC family. Bad metadata returns `-EINVAL` or omits the retile plane.
- Imported DMA-BUF scanout depends on `amdgpu_display_supported_domains()` and can be rejected on systems without GTT display support.
- Panic rendering supports no-CPU-access BOs only when they are VRAM-backed and 32 bpp; other cases fail to display panic output.
- Runtime PM reference tracking in legacy set_config relies on active CRTC enumeration after helper set_config; mismatches can affect power management.

## Test signals

Useful signals include KMS page-flip/vblank tests, IGT framebuffer modifier and size validation tests, hotplug and EDID/DDC tests, suspend/resume display tests, imported DMA-BUF scanout tests, debug logs for unsupported pixel format/modifier and pitch/offset failures, panic screen smoke tests on CPU-accessible and no-CPU-access BOs, and absence of pinned-BO leaks after repeated page flips.
