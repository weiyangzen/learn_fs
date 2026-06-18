# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dc_hw_types.h

## Purpose
`dc_hw_types.h` defines the hardware-facing data model for DC programming: plane addresses, surface formats, tiling/swizzle metadata, cursor state, gamma/CSC/color, CRTC timing, DSC, PSR context, DPCD-decoded capabilities, stream/link state fragments, writeback buffers, histogram control, and hardware context metadata. It is intended for virtual hardware layer programming and intentionally excludes higher-level logic-only types.

## Important APIs, Types, And Data Contracts
Memory and plane programming is represented by `union large_integer`, `struct dc_plane_address`, `struct dc_flip_addrs`, `struct plane_size`, `struct dc_plane_dcc_param`, `enum surface_pixel_format`, `enum dc_pixel_format`, tiling/swizzle enums, and `struct dc_tiling_info`. These structures carry GPU addresses, metadata addresses, VMID, TMZ, DCC const color, and GFX-version-specific tiling descriptions.

Cursor and color contracts include `struct dc_cursor_position`, `struct dc_cursor_mi_param`, `enum dc_cursor_color_format`, `struct dc_cursor_attributes`, `struct dpp_cursor_attributes`, `struct dc_gamma`, `struct dc_csc_transform`, `struct colorspace_transform`, color-space and dither enums, and histogram structures.

Timing and display output are modeled by `struct dc_crtc_timing`, `struct dc_crtc_timing_flags`, `struct dc_crtc_timing_adjust`, `enum dc_timing_standard`, `enum dc_color_depth`, `enum dc_pixel_encoding`, `enum dc_aspect_ratio`, and `enum scanning_type`. DSC timing fields embed `struct dc_dsc_config` and fixed bpp values.

Power, link, and platform context include `struct psr_context`, `struct dc_context`, `struct dsc_dec_dpcd_caps`, `struct hblank_expansion_dpcd_caps`, `struct dc_golden_table`, `enum dc_link_encoding_format`, display endpoint identifiers, panel/backlight enums, HDCP caps, MST allocation tables, PSR and Replay settings, panel config, DPIA bandwidth allocation, commit/create params, and validation params.

## Control Flow And State
The header has no functions, but many structures are persistent state containers embedded in `dc`, `dc_state`, `dc_link`, `dc_stream_state`, plane state, and hardware sequencer resources. `struct dc_gamma` includes a `kref`, so lifetime management is reference-counted. `struct dc_context` is a long-lived root object holding driver context, logger, BIOS/GPIO/DMUB services, ASIC IDs, register offsets, and firmware security/PSP context.

## Dependencies And Integration Points
It includes `os_types.h`, `fixed31_32.h`, and `signal_types.h`, and refers to many forward-declared DC objects. It is consumed by resource validation, hardware sequencers, link encoders, color management, cursor programming, writeback, PSR/Replay firmware paths, DSC, HDCP, MST, and DM/DC integration layers.

## Risks
Many enum values map directly to hardware register encodings; renumbering can silently break programming. Several structs contain raw GPU addresses and VMIDs, so stale or improperly synchronized state can cause memory faults. `struct dc_gamma` is large and reference-counted; incorrect retain/release can leak or use freed LUTs. Bitfields and unions are compact hardware contracts and need compiler layout consistency. Some comments document unit subtleties such as `pix_clk_100hz`, DSC bpp x16, luminance millinits, and DWB fixed-point formats.

## Test Signals
Validation should include plane format/tiling combinations, cursor attributes and movement, color/gamma programming, DSC timing validation, PSR/Replay entry/exit, MST allocation, writeback capture, HDCP cap reads, secure display CRC windows when enabled, and ASIC-version-specific tiling/swizzle cases. Compile-time coverage across DCN generations is important because many fields are conditionally consumed.
