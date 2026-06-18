# sources/distributed-fs/ceph-client/drivers/media/platform/ti/omap/omap_voutdef.h


Purpose: Defines shared constants, state structures, enums, and inline helpers for the OMAP V4L2 output driver and its VRFB/library helpers.

Important APIs/types: Size and capability constants cover pixel bytes-per-pixel, tile size, max video devices/overlays/displays/managers, default/min/max dimensions, VRFB transfer timeout, number of VRFB buffers, and maximum buffer size. `enum dma_channel_state`, `enum dss_rotation`, and `enum vout_rotaion_type` describe DMA allocation, DSS rotation encoding, and whether VRFB rotation is available. `struct vid_vrfb_dma` holds DMAengine channel/template/status/wait state. `struct omapvideo_info` binds a vout to overlays and rotation type. `struct omap2video_device` is the parent V4L2/DSS device aggregate. `struct omap_vout_buffer` wraps `vb2_v4l2_buffer`. `struct omap_vout_device` is the central per-video-node state object. Inline helpers convert vb2 buffers and answer/transform rotation+mirror state.

Control flow: The structures are allocated in `omap_vout_create_video_devices()`, populated during setup/probe, mutated by ioctls, consumed by vb2 callbacks, and read from the DISPC ISR. Rotation helpers drive both DSS overlay programming and VRFB offset/address selection.

State and persistence: All state is in memory and associated with the platform driver lifetime. `struct omap_vout_device` stores both userspace-visible V4L2 state and hardware-private details such as VRFB contexts, physical addresses, line length, field tracking, ISR handle, and frame queue pointers.

Dependencies/integration: Pulls in videobuf2 DMA-contig, V4L2 controls, OMAP DSS, OMAP VRFB, and DMAengine types. It is included by the main driver, VRFB backend, and helper library.

Risks and test signals: The misspelled `vout_rotaion_type` is ABI-internal but sticky. Fixed array sizes must match DSS discovery limits and `pdev->num_resources`; overflow checks live elsewhere. Rotation/mirror helper behavior reverses rotations under mirroring and should be covered for all four angles. Tests should focus on structure initialization, queue cleanup, VRFB disabled builds, and field interactions between ISR and streamoff.
