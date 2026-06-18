# sources/distributed-fs/ceph-client/drivers/media/platform/renesas/vsp1/vsp1_hgo.h

Purpose: declares the 1D histogram generator private structure and frame-end API.

Important APIs and types: `struct vsp1_hgo` embeds `struct vsp1_histogram`, a nested control handler with `max_rgb` and optional `num_bins` controls, plus cached `max_rgb` and `num_bins` values. `to_hgo()` converts from subdev. `vsp1_hgo_create()` constructs the entity and metadata node; `vsp1_hgo_frame_end()` reads data at frame completion.

Control flow role: pipeline/frame-end code calls `vsp1_hgo_frame_end()` for HGO entities, while probe-time entity creation uses `vsp1_hgo_create()`. Control state is cached by stream configuration before register programming.

State and persistence: cached control values determine output payload layout. Embedded histogram state owns vb2 queue, wait queue, IRQ queue, metadata format, and media entity state.

Dependencies and integration: includes V4L2 control/subdev and `vsp1_histo.h`, which supplies the shared metadata capture implementation.

Risks and test signals: ensure consumers understand payload size varies by mode. Test both 64-bin and 256-bin capable hardware, max-RGB mode, and metadata buffer sequencing.
