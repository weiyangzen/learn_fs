# sources/distributed-fs/ceph-client/drivers/media/platform/renesas/vsp1/vsp1_hgo.c

Purpose: implements the VSP1 1D histogram generator entity and metadata readout path. It configures HGO sampling/crop/downscale parameters and reads histogram registers into queued metadata buffers at frame end.

Important APIs and functions: `vsp1_hgo_create()`, `vsp1_hgo_frame_end()`, `hgo_configure_stream()`, plus controls for maximum RGB mode and number of bins. It reuses `vsp1_histogram_init()` for the subdev and metadata capture node.

Control flow: frame-end handling obtains a queued histogram buffer, reads max/min and sum registers, then reads either 256 green bins, 64 green bins, or separate 64-bin RGB histograms depending on controls. Stream configuration resets HGO registers, writes offset and size from crop selection, snapshots controls under the handler lock, computes horizontal/vertical ratio from crop and compose rectangles, and writes `VI6_HGO_MODE`.

State and persistence: persistent state includes `max_rgb`, `num_bins`, V4L2 control pointers, and the embedded histogram queue/entity state. Readout uses IRQ queue state from `vsp1_histo.c`; hardware register configuration is persisted through display-list entries.

Dependencies and integration: depends on HGO registers, display-list writes, V4L2 controls, vmalloc metadata buffers, and shared histogram infrastructure. `vsp1_drv.c` only creates HGO in UAPI mode on variants with the feature flag.

Risks and test signals: risks include control/layout changes while streaming, buffer payload size differences by mode, gen-dependent 256-bin support, and register read latency in frame-end context. Test metadata capture with all modes, no-buffer frame ends, crop/compose ratio changes, and `v4l2-compliance` metadata queues.
