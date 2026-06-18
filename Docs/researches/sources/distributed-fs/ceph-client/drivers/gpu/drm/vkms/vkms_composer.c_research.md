# sources/distributed-fs/ceph-client/drivers/gpu/drm/vkms/vkms_composer.c

## Purpose

`vkms_composer.c` is VKMS's software composition engine. It blends active planes line by line into an internal 16-bit ARGB buffer, applies per-plane color operations and CRTC gamma LUTs, computes CRC entries for vblank frames, and writes composed pixels into writeback buffers.

## Important APIs and functions

Exported or externally used entry points are `vkms_composer_worker()`, `vkms_get_crc_sources()`, `vkms_verify_crc_source()`, `vkms_set_crc_source()`, and `vkms_set_composer()`. KUnit-visible helpers include `lerp_u16()`, `get_lut_index()`, `apply_lut_to_channel_value()`, and `apply_3x4_matrix()`. Internal helpers handle premultiplied alpha blending, background fill, gamma LUT application, colorop traversal, rotation-to-read-direction mapping, source/destination clamping, scanline blending, format/map validation, and active-plane composition.

## Control flow and state

The CRTC vblank path queues `vkms_composer_worker()` when CRC or writeback composition is enabled. The worker snapshots `frame_start`, `frame_end`, `crc_pending`, and `wb_pending` under `composer_lock`, prepares gamma LUT metadata from the live CRTC state, and composes only if CRC work is pending. Composition allocates one staging and one output line buffer, then for each CRTC scanline fills the background color, blends active planes in z-order, applies gamma, updates a CRC32 over the raw 16-bit ARGB line, and optionally writes a row to the writeback buffer. Once complete, writeback completion is signaled and CRC entries are emitted for every pending frame.

## Dependencies and integration

The composer consumes `vkms_crtc_state`, `vkms_plane_state`, pixel read/write functions from `vkms_formats.c`, LUT tables from `vkms_luts.h`, DRM rotation/rect/fixed-point helpers, DRM CRC APIs, and DRM writeback completion. It is synchronized with CRTC atomic commit via `vkms_crtc.c`, which flushes work before cleanup.

## Risks and test signals

High-risk areas are buffer bounds during rotated reads, subsampled format callback correctness, slow worker backpressure across vblank frames, lock ordering between `lock` and `composer_lock`, color pipeline state lifetime, and memory allocation during composition. KUnit tests cover LUT/matrix math; broader signals include IGT CRC/writeback/rotation/alpha/color-management tests and KMS atomic stress.
