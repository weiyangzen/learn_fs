<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/via/via_modesetting.c -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/via/via_modesetting.c

Purpose: Basic CRTC register programming helpers for primary and secondary VIA display engines, plus start address, pitch, and color-depth programming.

Important APIs/types/functions: Implements `via_set_primary_timing()`, `via_set_secondary_timing()`, `via_set_primary_address()`, `via_set_secondary_address()`, `via_set_primary_pitch()`, `via_set_secondary_pitch()`, `via_set_primary_color_depth()`, and `via_set_secondary_color_depth()`.

Control flow and state: Timing setters convert logical `via_display_timing` values into raw register encodings, split high bits across legacy VGA CRTC extension registers, and write them in the order required by each engine. Primary timing unlocks CRTC register `0x11`, writes standard and extended timing bits, relocks it, and toggles timing control reset. Secondary timing writes the secondary CRTC register block directly. Address and pitch helpers encode framebuffer offsets/pitch into register fields; secondary address is quadword aligned. Color-depth helpers map fb depths to hardware bit patterns and warn on unsupported depths.

Dependencies and integration points: Depends on `via_modesetting.h`, `share.h`, `debug.h`, and `via_write_reg*` helpers. Called by LCD, CRT/DVI, pan-display, and mode-setting code in the viafb stack. Risks are off-by-one/shift errors in raw timing packing, no value range validation inside these helpers, unsupported 15-bpp secondary depth, and direct hardware mutation without locking in the helper itself. Test signals are register traces for known modes, fbdev mode switches, panning on both engines, color-depth changes, and secondary engine alignment behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/via/via_modesetting.c -->
