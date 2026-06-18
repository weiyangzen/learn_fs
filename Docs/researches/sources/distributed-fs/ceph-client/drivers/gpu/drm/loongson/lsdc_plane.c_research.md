# sources/distributed-fs/ceph-client/drivers/gpu/drm/loongson/lsdc_plane.c

Purpose: implements Loongson primary and cursor DRM planes, framebuffer BO pinning, primary scanout register programming, cursor update/disable paths, async cursor updates, and chip-specific cursor quirks.

Important APIs/types/functions: `lsdc_primary_plane_init`, `ls7a1000_cursor_plane_init`, `ls7a2000_cursor_plane_init`, plane prepare/cleanup helpers, primary/cursor atomic check/update/disable helpers, hardware ops tables, and register update functions.

Control flow: prepare pins framebuffer BOs into VRAM, refs them, and delegates to GEM plane helper; cleanup unpins and unrefs. Primary atomic update computes physical scanout address from BO GPU offset plus VRAM base and source offset, writes address/stride, and updates format when needed. Cursor checks enforce no scaling and 32x32 on LS7A1000 or 32/64 square on LS7A2000. Cursor updates program position, BO address, and cursor format/size; disables program cursor format disable. Async update mutates current plane state for cursor moves under DRM helper constraints.

State and persistence: plane wrappers store hardware ops and `ldev`. BO pin counts and pinned memory counters are maintained by TTM helpers. Hardware FB address, stride, format, cursor address/position/config registers persist.

Dependencies and integration points: depends on DRM atomic/GEM plane helpers, local TTM BO helpers, CRTC pipe index, and register macros.

Risks and test signals: primary address update appears to write the currently in-use FB register based on `FB_REG_IN_USING`; verify against hardware expectations for page flip. Async cursor path swaps FB references and must remain DRM-helper compliant. Test page flips, panning via src offsets, cursor move/resize/disable, LS7A1000 shared-cursor quirk, BO pin/unpin leak checks, and suspend unpin behavior.
