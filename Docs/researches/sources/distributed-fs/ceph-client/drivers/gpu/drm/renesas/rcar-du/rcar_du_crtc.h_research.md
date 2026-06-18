# sources/distributed-fs/ceph-client/drivers/gpu/drm/renesas/rcar-du/rcar_du_crtc.h

## Purpose

`rcar_du_crtc.h` declares the R-Car DU CRTC data structures, state extensions, conversion helpers, and cross-file APIs for CRTC creation, page-flip completion, and DSYSR updates.

## Important APIs, Types, and Functions

- `struct rcar_du_crtc` embeds `struct drm_crtc` and stores DU device/group links, clocks, hardware index, MMIO offset, cached DSYSR, vblank/event state, CMM/VSP/writeback links, and CRC source metadata.
- `struct rcar_du_crtc_state` extends DRM CRTC state with VSP CRC configuration and a bitmask of driven DU outputs.
- `to_rcar_crtc()`, `wb_to_rcar_crtc()`, and `to_rcar_crtc_state()` provide container conversions.
- Exported functions: `rcar_du_crtc_create()`, `rcar_du_crtc_finish_page_flip()`, and `rcar_du_crtc_dsysr_clr_set()`.

## Control Flow

The header supports KMS setup (`rcar_du_crtc_create()`), group start/stop (`rcar_du_crtc_dsysr_clr_set()`), and VSP/writeback/IRQ paths that need to complete page flips.

## State and Persistence Behavior

The structures define the persistent per-CRTC state used for runtime PM, vblank synchronization, page-flip events, output routing, and CRC configuration. `dsysr` is a software cache of a hardware register to keep read/modify/write operations coherent.

## Dependencies and Integration Points

- Includes DRM CRTC/writeback, Linux wait/spinlock/mutex, and media VSP1 CRC definitions.
- Referenced by driver, group, KMS, VSP, writeback, and CRTC implementation files.

## Risks and Edge Cases

- Several fields are touched from IRQ and atomic paths; event and vblank fields require the locks documented by implementation, not enforced in the structure.
- `sources` strings are dynamically allocated for CRC and must be cleaned only on Gen3 paths that allocate them.

## Test Signals

- Build and runtime tests should verify CRTC state duplication/reset preserves CRC defaults and output routing state.
- Lockdep should remain clean for vblank/event wait paths.
