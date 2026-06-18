## sources/distributed-fs/ceph-client/drivers/gpu/drm/ast/ast_cursor.c

Purpose: hardware cursor plane for AST devices, using a reserved VRAM block with ARGB4444 cursor pixels plus a signature/checksum area consumed by hardware.

Important functions are `ast_cursor_vram_offset`, `ast_cursor_calculate_checksum`, `ast_set_cursor_image`, `ast_set_cursor_base`, `ast_set_cursor_location`, `ast_set_cursor_enabled`, `ast_cursor_plane_get_argb4444`, `ast_cursor_plane_helper_atomic_check/update/disable`, and `ast_cursor_plane_init`. Supported cursor formats are `ARGB4444` and `ARGB8888` converted to ARGB4444.

Control flow: init reserves the last aligned cursor-sized block in VRAM. Atomic check rejects scaled or oversized cursors. Update merges damage, converts/copies the framebuffer into ARGB4444 memory, writes cursor pixels and signature, programs base address, writes signed/negative-position offsets, and toggles the hardware enable bit to make changes visible. Disable clears the enable bit.

State persists in cursor VRAM, signature fields, indexed cursor registers, and the software conversion buffer. Dependencies are shadow-plane helpers, GEM CPU access, DRM format conversion, `ast_plane_vaddr`, and CRTC mode validity. Risks include fallback white square on CPU-access failure, endian-specific copy handling, checksum/signature correctness, cursor memory reducing primary framebuffer space, and hardware requiring a valid active primary/CRTC. Test signals are cursor size rejection, ARGB8888 conversion correctness, negative-position clipping, disable during full modesets, and no corruption of primary framebuffer VRAM.
