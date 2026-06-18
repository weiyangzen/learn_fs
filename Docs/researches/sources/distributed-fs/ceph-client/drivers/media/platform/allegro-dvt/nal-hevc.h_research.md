# sources/distributed-fs/ceph-client/drivers/media/platform/allegro-dvt/nal-hevc.h

## Purpose

`nal-hevc.h` defines C representations of HEVC VPS, SPS, PPS, VUI, HRD, and profile-tier-level syntax and supplies inline helpers to map V4L2 HEVC controls and colorimetry to HEVC bitstream values.

## Important APIs, Types, And Symbols

- Main structs are `nal_hevc_profile_tier_level`, `nal_hevc_vps`, `nal_hevc_hrd_parameters`, `nal_hevc_vui_parameters`, `nal_hevc_sps`, and `nal_hevc_pps`.
- `N_HRD_PARAMS` is set to 1, limiting represented HRD CPB entries.
- Inline mapping helpers include `nal_hevc_profile()`, `nal_hevc_tier()`, `nal_hevc_level()`, `nal_hevc_full_range()`, `nal_hevc_color_primaries()`, `nal_hevc_transfer_characteristics()`, and `nal_hevc_matrix_coeffs()`.
- Public prototypes expose VPS/SPS/PPS/filler read and write helpers.

## Control Flow

Inline helper flow is simple switch-based mapping from V4L2 enums into HEVC syntax values. Larger control flow is in `nal-hevc.c`, which traverses these structs to emit or parse RBSP.

## State And Persistence

The header declares transient struct layouts and pure conversion functions. It has no persistent state.

## Dependencies And Integration Points

It depends on kernel integer/error helpers and V4L2 control/color enums. It is used directly by `allegro-core.c` when building HEVC VPS/SPS/PPS metadata and by `nal-hevc.c` for serialization.

## Risks

Some arrays model only small subsets of the HEVC syntax, for example one HRD parameter set and one explicit tile width/height entry in PPS, even though the firmware response can carry more tile dimensions. Helper defaults return generic values for unsupported color metadata, which can reduce precision. Future support for Main 10 or advanced profiles must audit both struct fields and writer branches for unsupported syntax.

## Test Signals

Compile coverage across current V4L2 HEVC enum values, unit tests for profile/tier/level mapping, generated stream validation with HEVC decoders, and boundary tests around tile counts and HRD parameters are useful signals.
