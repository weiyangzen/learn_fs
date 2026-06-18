# sources/distributed-fs/ceph-client/drivers/media/platform/renesas/vsp1/vsp1_clu.h

Purpose: declares private state for the VSP1 cubic LUT entity.

Important APIs and types: defines `CLU_PAD_SINK`, `CLU_PAD_SOURCE`, `struct vsp1_clu`, `to_clu()`, and `vsp1_clu_create()`. `struct vsp1_clu` embeds the common entity, V4L2 control handler, `yuv_mode`, spinlock, selected mode, pending table display-list body pointer, and display-list body pool.

Control flow role: the header lets `vsp1_drv.c` create a CLU entity and lets `vsp1_clu.c` convert subdev callbacks back to CLU-specific state. The pad macros align with the two-pad common entity format operations.

State and persistence: `yuv_mode` is cached from stream format and used by frame configuration. `mode` is control-backed. `clu` points to a pending DMA display-list body containing table writes; `pool` owns reusable bodies sized for CLU table uploads.

Dependencies and integration: includes spinlock, media entity, V4L2 controls/subdev, and `vsp1_entity.h`; forward-declares `vsp1_device` and `vsp1_dl_body`.

Risks and test signals: any structural change must preserve locking between control updates and frame configuration. Compile-test CLU-enabled variants and run control set/get plus stream tests that update the LUT during active pipelines.
