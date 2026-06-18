# sources/distributed-fs/ceph-client/drivers/media/platform/renesas/vsp1/vsp1_wpf.c

Purpose: implements the Write Pixel Formatter entity, the VSP1 output block that writes processed frames to memory, feeds display pipelines, handles writeback, and applies WPF0 flip/rotation controls.

Important APIs/functions: `vsp1_wpf_create()` allocates/registers WPF instances and creates a display-list manager. `vsp1_wpf_stop()` disables WPF interrupts and sources directly during stream stop. Control helpers initialize VFLIP/HFLIP/ROTATE where supported and update pending flip state. Entity callbacks configure stream, frame, partition, max width, destruction, and partition mapping. `wpf_configure_writeback_chain()` builds a chained display list to disable one-shot writeback after a frame.

Control flow/state: rotation changes that swap width/height are rejected while VB2 buffers are busy. Stream configuration writes output format, stride, byte swap, optional rotation memory config, CSC mode, source RPF/virtual source selection, interrupts, and writeback enable. Per frame, pending flip bits are latched into active bits and merged into `VI6_WPF_OUTFMT` with alpha. Partition configuration clips output size, returns early for display-only LIF paths without writeback, computes destination plane addresses with partition offset, rotation, H/V flip, subsampling, and Gen3 U/V swap, then clears `wpf->writeback` because writeback is one-shot.

Dependencies/integration: shares `vsp1_rwpf` state, uses VSP1 display-list manager, pipeline and partition helpers, V4L2 controls, WPF register macros, and feature flags for H/V flip availability. It is the output side used by `vsp1_video.c` and VSPX.

Risks and test signals: output address arithmetic is complex and sensitive to rotation/flip/subsampling/partition combinations. Writeback must be disabled safely to avoid memory corruption. WPF0-only flip feature checks vary by SoC. Test all rotation values, horizontal/vertical flip combinations, multi-planar YUV, rotated partition widths, LIF display pipeline with and without writeback, Gen2 vs Gen3 max sizes, and stream stop cleanup.
