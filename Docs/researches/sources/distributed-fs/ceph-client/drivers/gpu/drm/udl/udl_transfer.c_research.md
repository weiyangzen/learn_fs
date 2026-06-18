<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/udl/udl_transfer.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/udl/udl_transfer.c

Purpose: Encodes horizontal framebuffer spans into DisplayLink 16bpp command streams and submits them through reusable URBs.

Important APIs/types/functions: `pixel32_to_be16()` converts XRGB8888-style pixels to RGB565 big-endian. `get_pixel_val16()` reads 16bpp or converted 32bpp source pixels. `udl_compress_hline16()` emits `UDL_CMD_WRITERLX16` commands combining raw and repeat spans with a 256-pixel protocol limit. `udl_render_hline()` repeatedly compresses a line segment, submits full URBs, fetches new URBs, and returns the updated buffer pointer.

Control flow: The caller supplies source offsets, device framebuffer offset, byte width, and current URB/buffer pointers. Compression advances source pixels and command pointer until either the line is complete or the command buffer fills. Full buffers are submitted immediately and replaced with new URBs.

State and persistence: No durable state; transient state is source pointer, device address, command pointer, and current URB.

Dependencies and integration points: Depends on UDL protocol constants, URB helpers from `udl_main.c`, and modeset damage upload from `udl_modeset.c`.

Risks and test signals: Risks include unaligned 16/32-bit reads, command-buffer boundary errors, run-length count encoding off-by-one, conversion correctness, and partial failure leaving URBs completed/submitted correctly. Tests should compare encoded output for solid, alternating, and random lines; exercise buffer-boundary fills; and validate 16bpp/32bpp paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/udl/udl_transfer.c -->
