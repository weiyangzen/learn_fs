# sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/radeon_display.c

## Purpose

`radeon_display.c` implements common Radeon KMS display management: CRTC allocation, gamma/LUT programming, page-flip scheduling and completion, display connector setup, pixel PLL calculations, framebuffer creation, mode properties, AFMT/HDMI audio block allocation, mode-setting init/fini, scaling decisions, and scanout-position reporting for vblank timestamping.

## Important APIs, Types, and Functions

- LUT paths `legacy_crtc_load_lut()`, `avivo_crtc_load_lut()`, `dce4_crtc_load_lut()`, `dce5_crtc_load_lut()`, and `radeon_crtc_load_lut()` program family-specific gamma hardware.
- Page-flip paths `radeon_crtc_page_flip_target()`, `radeon_flip_work_func()`, `radeon_crtc_handle_vblank()`, and `radeon_crtc_handle_flip()` pin the new BO, wait on fences, program the flip, send events, put vblank references, and asynchronously unpin the old BO.
- `radeon_crtc_init()` allocates each `struct radeon_crtc`, creates its high-priority workqueue, installs CRTC funcs, sets cursor bounds, and dispatches Atom or legacy CRTC initialization.
- `radeon_compute_pll_avivo()` and `radeon_compute_pll_legacy()` calculate pixel-clock dividers under family/PLL constraints.
- `radeon_framebuffer_init()` and `radeon_user_framebuffer_create()` bridge GEM BOs to DRM framebuffers, rejecting imported dma-buf scanout.
- `radeon_modeset_init()` and `radeon_modeset_fini()` create DRM mode config, properties, I2C, CRTCs, connectors/encoders, HPD, AFMT, polling, and late PM state.
- `radeon_crtc_scaling_mode_fixup()` and `radeon_get_crtc_scanoutpos()` handle panel/HDMI scaling and vblank position queries.

## Control Flow

Mode-setting initialization starts with `drm_mode_config_init()`, max dimension selection by ASIC generation, property creation, I2C setup, optional hardcoded COMBIOS EDID loading, CRTC allocation, BIOS-derived connector/encoder setup, Atom encoder/PLL init, HPD init, AFMT allocation, polling init, and PM late init. Connector setup first tries Atom supported-device or object tables, then COMBIOS or fallback legacy tables, then configures clone masks and logs topology.

Page flips are split between IOCTL context and workqueues. The IOCTL path allocates `radeon_flip_work`, references the old BO, pins the new BO into VRAM, captures a write fence from the new reservation object, calculates legacy base offsets/tiling adjustment when needed, marks the CRTC pending under `event_lock`, swaps `primary->fb`, and queues work. The worker waits for the fence, may trigger GPU reset on `-EDEADLK`, waits out unsafe vblank windows, enables page-flip IRQs, programs hardware, and marks submitted. IRQ/vblank completion sends the event and queues old-BO unpin.

## State and Persistence Behavior

Persistent display state is in `rdev->mode_info`: CRTC pointers, properties, hardcoded EDID, AFMT blocks, backlight encoder, HPD data, and `mode_config_initialized`. Each CRTC tracks flip status, flip work, native/scaling values, cursor limits, workqueue, and vblank lead lines. Page flip state is protected by DRM `event_lock`; reset interaction is protected by `exclusive_lock`.

## Dependencies and Integration Points

The file depends on DRM CRTC/mode/fb/vblank helpers, runtime PM, TTM/GEM BOs, Radeon IRQ, fence, Atom/COMBIOS connector parsers, I2C, HPD, PM, backlight/encoder code, and family register definitions. `radeon_fbdev.c` reuses `radeon_framebuffer_init()`, while `radeon_device.c` calls mode init/fini and resume/reset reinitializes Atom display blocks.

## Risks and Edge Cases

- Page-flip completion has known race windows on older ASICs; the code mixes pflip IRQs and vblank polling depending on `radeon_use_pflipirq`.
- Imported dma-buf framebuffer creation is rejected because the BO cannot be migrated to VRAM for scanout.
- PLL computation is constraint-heavy and can produce poor clocks if BIOS limits are wrong.
- `radeon_modeset_init()` returns `ret` directly when connector setup fails, but `ret` is boolean in that block, so failure is returned as 0/false-style success semantics only because caller context expects nonzero as success earlier; this path needs careful review if refactored.
- AFMT allocation is best-effort and sparse; users must tolerate missing blocks.

## Test Signals

Test page flips with and without pflip IRQs, async flips, fenced BOs, reset during flip, legacy and DCE scanout, gamma updates, framebuffer creation rejection for imported dma-buf, PLL results for known modes, HDMI underscan/scaling properties, suspend/resume display restore, and vblank timestamp accuracy across CRTC families.
