# sources/distributed-fs/ceph-client/drivers/gpu/drm/arm/malidp_mw.c

## Purpose

`malidp_mw.c` implements the Mali-DP writeback connector using the scaling engine memory-write path. It exposes an always-connected writeback connector, validates writeback framebuffer size/format/pitches, records DMA addresses in connector state, queues writeback jobs, and calls hardware `enable_memwrite` or `disable_memwrite` callbacks during atomic commit.

## Important APIs, Types, And Functions

The exported APIs are `malidp_mw_connector_init()` and `malidp_mw_atomic_commit()`. The private `struct malidp_mw_connector_state` extends connector state with up to two DMA addresses, pitches, internal format ID, plane count, and RGB-to-YUV coefficient tracking. `malidp_mw_encoder_atomic_check()` performs most validation. `get_writeback_formats()` builds a format list from hardware map entries that support `SE_MEMWRITE`.

## Control Flow

Connector initialization skips devices without `enable_memwrite`, attaches helper funcs, builds the writeback format list, and calls `drm_writeback_connector_init()` with the CRTC mask for the single CRTC. Atomic check ignores commits without a writeback job. With a job, it requires framebuffer dimensions to match the CRTC mode, rejects modifiers, maps the FourCC to a `SE_MEMWRITE` format ID, validates pitch alignment using non-rotated pitch rules, and records GEM DMA addresses plus offsets. Atomic commit queues the writeback job before programming hardware, optionally writes RGB-to-YUV coefficients for YUV targets once, and disables memwrite when no job is present.

## State And Persistence Behavior

Per-connector atomic state stores DMA programming values and whether RGB-to-YUV coefficients have already been initialized. Hardware writeback state is stored in `hwdev->mw_state` and handled in `malidp_hw.c` SE IRQs. Writeback job completion is signaled from SE IRQ completion paths, not directly here.

## Dependencies And Integration Points

The file depends on DRM writeback, DRM atomic helpers, GEM DMA framebuffer helpers, Mali-DP format mapping, pitch alignment, and hardware memwrite callbacks. It integrates with `malidp_drv.c` commit tail, which calls `malidp_mw_atomic_commit()` between plane commit and modeset enables, and with SE IRQ code that signals completion.

## Risks And Edge Cases

Writeback framebuffers must exactly match current mode dimensions; scaling into writeback is not supported here. Modifiers are rejected even if display planes support AFBC. Only up to two planes are recorded. The RGB-to-YUV initialization flag is carried across duplicated connector state; stale coefficients could matter if formats or colorimetry support expands. `malidp_mw_atomic_commit()` assumes `disable_memwrite` exists when connector state exists.

## Test Signals

IGT writeback tests, each advertised memory-write format, YUV writeback coefficient programming, invalid pitch rejection, modifier rejection, size mismatch rejection, job completion signaling on SE IRQ, repeated writeback jobs without repeated coefficient writes, and no-writeback disable commits are the main signals.
