# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gvt/fb_decoder.h

## Purpose
`fb_decoder.h` defines register bit masks, event enums, display port enums, and decoded plane metadata structures for GVT framebuffer extraction. It is the public interface for code that wants to decode a vGPU's guest display state.

## Important Types And APIs
The header declares `enum GVT_FB_EVENT` for modeset and flip notifications, `enum DDI_PORT` for DDI port identity, `struct intel_vgpu_primary_plane_format`, `struct intel_vgpu_sprite_plane_format`, and `struct intel_vgpu_cursor_plane_format`. The primary and cursor structs include enabled state, bpp, DRM format, guest graphics base, translated GPA, dimensions, stride/offsets, and cursor position/hotspot fields. Public APIs are `intel_vgpu_decode_primary_plane()` and `intel_vgpu_decode_cursor_plane()`.

## Control Flow And State
The header itself is declarative. Its masks are consumed by `fb_decoder.c` to isolate fields from display registers such as plane control, source size, stride, sprite/cursor position, and cursor alpha/mode bits. The decoded structs are snapshots populated by callers and are not retained by the decoder.

## Dependencies And Integration Points
It forward-declares `struct intel_vgpu` and includes Linux types. The structures integrate with dmabuf/display export code and with the GTT layer through `base_gpa` fields filled by the decoder implementation.

## Risks And Test Signals
Register masks are generation-specific and must stay aligned with i915 display register definitions. The sprite struct is declared but no sprite decoder is exported in this file set, so users should not assume sprite decode coverage. Tests should verify mask extraction boundaries for maximum width/height/position fields and ABI stability of the decoded structures.
