<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv04/disp.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv04/disp.c

## Purpose
This file creates and tears down the pre-NV50 Nouveau KMS display stack. It wires `nv04_display` into `nouveau_display`, creates CRTCs and encoders from VBIOS DCB outputs, saves/restores legacy mode state, manages suspend/resume framebuffer and cursor pinning, and enables flip-completion events.

## Important APIs, Types, and Functions
`nv04_display_create` is the public constructor. `nv04_display_init`, `nv04_display_fini`, and `nv04_display_destroy` become display lifecycle callbacks. `nv04_encoder_get_connector` maps a Nouveau encoder back to its attached connector. The file depends on `struct nv04_display`, `struct nouveau_encoder`, `struct nouveau_crtc`, DCB output entries, `nvif_event`, and GEM/BO helpers.

## Control Flow
Creation allocates `nv04_display`, disables atomic DRM ioctls for pre-NV50 hardware, creates an optional flip event on the channel software object, saves VGA fonts, instantiates one or two CRTCs, then walks DCB outputs to create DAC, DFP, on-chip TV, or external TV encoders. Connectors without encoders are removed, I2C buses are attached to encoders by DCB index, initial CRTC and encoder state is saved, and overlay planes are initialized. Resume init re-saves preexisting state, allows flip events, repins framebuffer and cursor BOs, invalidates LUT depth for reload, and forces modes unless runtime resume avoids modeset locking. Fini blocks flip events, disables vblank interrupts, cancels HPD work outside runtime suspend, and on suspend unpins scanout/cursor BOs. Destroy restores encoder/CRTC state, restores VGA fonts, destroys the flip event, and frees display private state.

## State and Persistence Behavior
Persistent state lives in `nouveau_display(dev)->priv`, `nv04_display.mode_reg`, `saved_reg`, `saved_vga_font`, per-CRTC cursor BO mappings, primary framebuffer BO pin state, and `disp->flip`. Suspend intentionally releases VRAM pins so memory can migrate; resume re-establishes pins and cursor mapping/position.

## Dependencies and Integration Points
The file integrates with DRM connector/encoder/CRTC lists, Nouveau DCB parsing, `nv04_crtc_create`, DAC/DFP/TV constructors, `nouveau_overlay_init`, GEM BO pin/map/unpin, `drm_helper_resume_force_mode`, HPD work, and NVIF software event delivery through `nv04_flip_complete`.

## Risks
Errors after `vzalloc` and before full teardown can leak partially initialized state if callers do not unwind display creation. BO pin failures during resume are logged but not fatal, so scanout may resume with broken framebuffer or cursor state. The initialization still relies on saved firmware/pre-driver register state, which is fragile across suspend and head ownership quirks. Connector pruning depends on `possible_encoders` being set correctly by encoder constructors.

## Test Signals
Useful signals include boot and module reload on NV04-NV4x GPUs, DCB coverage for analog, TMDS/LVDS, on-chip TV, and external TV outputs, suspend/resume with active framebuffer and cursor, runtime resume through connector wake, page-flip completion events, vblank interrupt suppression, and connector list cleanup for unsupported DCB outputs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv04/disp.c -->
