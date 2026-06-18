# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gvt/fb_decoder.c

## Purpose
`fb_decoder.c` decodes guest-programmed display plane registers into host-readable framebuffer metadata for GVT. It extracts primary plane and cursor plane format, dimensions, tiling, stride, base graphics address, translated guest physical address, and cursor position/hotspot.

## Important APIs And Functions
The exported APIs are `intel_vgpu_decode_primary_plane()` and `intel_vgpu_decode_cursor_plane()`. Internal helpers include `bdw_format_to_drm()`, `skl_format_to_drm()`, `intel_vgpu_get_stride()`, `get_active_pipe()`, and `cursor_mode_to_drm()`. Static format tables map hardware encodings to DRM fourcc formats and bits-per-pixel.

## Control Flow
Both decoders first locate the active pipe by scanning `pipe_is_enabled()`. Primary decode reads `DSPCNTR`, determines whether the plane is enabled, decodes format differently for Gen9+ universal plane encodings versus Broadwell-era display encodings, validates nonzero bpp, reads `DSPSURF`, validates the GMA range, translates the base through `intel_vgpu_gma_to_gpa()`, computes stride from `DSPSTRIDE` and tiling mode, reads width/height from `PIPESRC`, and reads X/Y offsets from `DSPTILEOFF`.

Cursor decode reads `CURCNTR`, rejects disabled or unsupported modes, fills ARGB cursor format metadata, validates and translates `CURBASE`, decodes signed X/Y position from `CURPOS`, and reads paravirtual cursor hotspot registers from the vGT interface.

## State And Persistence
The file does not own persistent state. It samples virtual display registers from `vgpu->mmio.vreg`, performs GGTT translation through `vgpu->gtt.ggtt_mm`, and writes a caller-provided plane descriptor. The descriptor is a snapshot and can become stale after a guest modeset or flip.

## Dependencies And Integration Points
Dependencies include i915 display register definitions, DRM fourcc constants, GVT display helpers, GTT address validation/translation, and vGT paravirtual info registers for cursor hotspots. Consumers are typically display, dmabuf, or mediated-device paths that need to expose guest framebuffer content to host userspace.

## Risks And Edge Cases
Only primary and cursor planes are exported despite sprite-related structures in the header. Unsupported pixel formats, invalid GM addresses, missing active pipes, and failed GMA-to-GPA translation return errors. Stride calculation is generation- and tiling-dependent; Y/Yf tiled and unusual bpp combinations are easy regression points. The active-pipe scan returns the first enabled pipe only, so multi-pipe scenarios may need higher-level coordination.

## Test Signals
Validation should exercise BDW and SKL+ format encodings, linear/X/Y/Yf tiling, cursor modes 64/128/256 ARGB, disabled plane paths returning `-ENODEV`, invalid GGTT mappings returning `-EINVAL`, and successful decoded GPA matching the guest GGTT entry.
