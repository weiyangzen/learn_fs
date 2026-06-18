# sources/distributed-fs/ceph-client/drivers/gpu/drm/renesas/rcar-du/rcar_du_writeback.c

## Purpose

`rcar_du_writeback.c` implements DRM writeback connector support for R-Car DU when the display pipeline is VSP-backed. It validates writeback jobs, maps the destination framebuffer for VSP DMA, programs VSP writeback configuration during atomic flush, and signals completion from the VSP callback.

## Important APIs, Types, and Functions

Driver-private `rcar_du_wb_conn_state` adds the selected `rcar_du_format_info` to DRM connector state, and `rcar_du_wb_job` stores mapped SG tables. Public functions are `rcar_du_writeback_init()`, `rcar_du_writeback_setup()`, and `rcar_du_writeback_complete()`. Internal callbacks implement connector modes, job prepare/cleanup, connector state duplication/reset, and encoder atomic validation.

## Control Flow

Initialization registers a writeback connector for one CRTC and advertises RGB-only formats. During an atomic commit with a writeback job, encoder atomic check verifies the framebuffer matches the active mode size and a supported R-Car DU format. `prepare_writeback_job` allocates private job state and maps the framebuffer through `rcar_du_vsp_map_fb()`. During CRTC/VSP atomic flush, `rcar_du_writeback_setup()` copies V4L2 format, pitch, and DMA addresses into `vsp1_du_writeback_config` and queues the job. The VSP completion callback later invokes `drm_writeback_signal_completion()`.

## State and Persistence Behavior

Connector state persists across atomic commits and carries the resolved format for the active job. Job-private SG mappings persist only between prepare and cleanup. Queued DRM writeback jobs are owned by the DRM writeback core after `drm_writeback_queue_job()`.

## Dependencies and Integration Points

This file depends on DRM writeback helpers, connector/encoder atomic helpers, R-Car DU format lookup, CRTC writeback storage, and VSP framebuffer mapping. It is invoked from `rcar_du_vsp_atomic_flush()` and `rcar_du_vsp_complete()`.

## Risks and Edge Cases

- Only RGB writeback formats are advertised because VSP outputs RGB to DU; YUV writeback is intentionally unsupported.
- `rcar_du_writeback_setup()` assumes atomic check and prepare populated `wb_state->format` and `job->priv`.
- Destination framebuffer plane count must fit the three SG table slots inherited from the VSP map helper.
- Completion depends on VSP reporting `VSP1_DU_STATUS_WRITEBACK`; missing status would leave jobs incomplete.

## Test Signals

Run DRM writeback tests for supported RGB formats, mismatched framebuffer sizes, unsupported formats, imported dma-buf destinations, completion signaling, cancellation/cleanup, and no leaked SG mappings after job failure.
