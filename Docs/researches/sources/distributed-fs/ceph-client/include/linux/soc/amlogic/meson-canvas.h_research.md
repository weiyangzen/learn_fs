# sources/distributed-fs/ceph-client/include/linux/soc/amlogic/meson-canvas.h

Purpose: This Amlogic Meson header defines the canvas allocator/configuration API used by video/display clients to program hardware canvas entries that describe pixel-buffer layout.

Important APIs/types/functions: It defines wrap modes (`MESON_CANVAS_WRAP_NONE`, `_X`, `_Y`), block modes (`LINEAR`, `32x32`, `64x64`), endian-swap modes, an opaque `struct meson_canvas`, and APIs `meson_canvas_get`, `meson_canvas_alloc`, `meson_canvas_free`, and `meson_canvas_config`.

Control flow: A consumer gets a canvas provider from its device, allocates a canvas index, configures the index with physical address, stride, height, wrapping, tiling, and endian mode, then frees the index when done.

State and persistence: The provider tracks canvas index ownership and writes persistent hardware table entries until reconfigured or freed. The caller owns buffer lifetime and physical address validity.

Dependencies and integration: Includes `linux/kernel.h` and uses `struct device`. Integrates with Meson DRM, VPU, video decoder, and other multimedia drivers using shared canvas hardware.

Risks and test signals: Wrong stride, block mode, endian mode, or stale physical address causes corrupted scanout/video. Test allocation exhaustion, double-free handling, display/video rendering for each block mode, and suspend/resume restoration if the provider loses register state.
