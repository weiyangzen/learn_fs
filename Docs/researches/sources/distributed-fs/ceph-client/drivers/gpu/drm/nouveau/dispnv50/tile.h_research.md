
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/tile.h

## Purpose
Defines inline helpers for NVIDIA block-linear tiling geometry used by display scanout and panic scanout writes.

## Important APIs, types, and functions
- Constants: `NV_TILE_GOB_HEIGHT_TESLA`, `NV_TILE_GOB_HEIGHT`, and `NV_TILE_GOB_WIDTH_BYTES`.
- `nouveau_get_width_in_blocks()` converts byte stride to 64-byte GOB columns.
- `nouveau_get_gob_height()` returns Tesla versus Fermi+ GOB height.
- `nouveau_get_height_in_blocks()` rounds pixel height to block rows.
- `nouveau_get_gob_size()` returns bytes per GOB.
- `nouveau_get_gobs_in_block()` decodes log2 block height from tile mode, with chipset-specific bit handling.
- `nouveau_check_tile_mode()` validates the tile mode against chipset-specific maximum block height.

## Control flow
All helpers are static inline arithmetic. They branch on GPU family/chipset thresholds to account for Tesla GOB height, pre-C0 tile mode fields, and the wider block-height encoding used by newer chips.

## State and persistence
No state is stored. The helpers derive geometry from caller-supplied stride, height, tile mode, family, and chipset.

## Dependencies and integration points
Uses `nvif/device.h` for chipset/family constants. `wndw.c` uses these helpers for DRM panic scanout pixel placement and modifier validation paths depend on matching tiling semantics elsewhere in Nouveau.

## Risks
Off-by-one rounding or wrong chipset thresholds corrupt block-linear addressing. Panic rendering currently assumes limited formats, so these helpers must remain consistent with `nouveau_framebuffer_get_layout()` and DRM modifier encodings.

## Test signals
Validation signals include correct display of tiled framebuffers, successful panic text rendering on tiled scanout, and modifier acceptance/rejection tests for pre-C0, C0+, and Blackwell-era layouts.
