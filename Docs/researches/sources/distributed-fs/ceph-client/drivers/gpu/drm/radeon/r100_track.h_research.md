# sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/r100_track.h

## Purpose
`r100_track.h` declares the command-stream tracking structures and helper prototypes used by the R100/R200/R300 Radeon CS validators. It is the shared data model for proving that render targets, depth buffers, textures, cube faces, vertex arrays, AA resolve buffers, and draw parameters are valid before user command buffers are submitted to legacy GPUs.

## Important APIs, Types, And Functions
The core type is `struct r100_cs_track`, which stores hardware-family limits (`num_cb`, `num_texture`), current render height, vertex and draw metadata, color-channel mask, arrays for up to sixteen vertex buffers, color buffers up to `R300_MAX_CB`, depth and AA buffers, textures up to `R300_TRACK_MAX_TEXTURE`, and dirty/enable flags. Supporting types are `r100_cs_track_cb` for color/depth-like buffers, `r100_cs_track_array` for vertex buffers, `r100_cs_cube_info` for non-primary cube faces, and `r100_cs_track_texture` for texture dimensions, pitch, mip count, bytes per pixel, coordinate type, depth, compression, and flags. The header declares `r100_cs_track_check`, `r100_cs_track_clear`, `r100_cs_packet_parse_vline`, `r200_packet0_check`, `r100_reloc_pitch_offset`, and `r100_packet3_load_vbpntr`.

## Control Flow
The header has no local control flow. At runtime, `r100_cs_parse` allocates a `r100_cs_track`, `r100_cs_track_clear` initializes conservative defaults, PACKET0/PACKET3 checkers update fields as registers and draw packets are parsed, and `r100_cs_track_check` validates dirty state before draw packets. R200 and later parser code can reuse the same declarations while adding family-specific packet0 validation.

## State, Persistence, And Dependencies
Tracker state is per-command-submission and temporary. It persists only for the lifetime of the parser invocation and points to BOs from the parser relocation list; it does not own those BOs. The header depends on `radeon.h` for `struct radeon_bo`, `struct radeon_device`, `struct radeon_cs_parser`, and packet types, and on family constants that determine array sizes. Dirty flags allow incremental validation when command streams modify only some state.

## Integration Points
`r100.c` includes this header directly and implements the declared R100 functions. R200/R300 command-stream code uses the common structures and prototypes to share validation state. This header is part of the userspace command-submission trust boundary because its fields represent the driver's model of what hardware will read or write after a draw.

## Risks
The arrays are fixed-size and rely on parser code bounding texture units, color buffers, and vertex arrays correctly. Conservative defaults are intentionally huge or invalid, so forgetting to clear or update a field can cause false rejects or, worse, stale validation if dirty flags are mishandled. The tracker stores BO pointers without ownership, so lifetime must be tied to the parser relocation list. Several fields encode hardware units rather than bytes (`pitch`, `cpp`, mip dimensions), making unit consistency critical. Cube texture tracking has separate handling for older ASICs and can be easy to desynchronize from texture-format parsing.

## Test Signals
Useful tests include parser coverage for all texture units and cube faces, color/depth/AA resolve bounds, indexed and non-indexed vertex buffers, immediate draws, compressed DXT textures, non-power-of-two textures using pitch, R100/R200/R300 family limit differences, missing relocations, dirty-flag transitions, and shared R200 packet0 paths that call into the R100 tracking helpers.
