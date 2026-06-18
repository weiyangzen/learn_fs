# sources/distributed-fs/ceph-client/drivers/media/platform/sunxi/sun4i-csi/sun4i_v4l2.c

Purpose: implements V4L2 ioctl, file-operation, format, and local subdevice pad handling for the sun4i CSI video node.

Important APIs and functions: exported internals are `sun4i_csi_find_format`, `sun4i_csi_subdev_ops`, `sun4i_csi_subdev_internal_ops`, and `sun4i_csi_v4l2_register`. It defines the format table, ioctl ops for querycap, enum/get/set/try mplane capture formats, input selection, and vb2 ioctls, plus file open/release and subdev pad operations.

Control flow: `sun4i_csi_v4l2_register` sets a default YUV420M capture format and default YUYV mbus subdev format, attaches file/ioctl ops, and registers the video device. Format try/set clamps and aligns dimensions to the single supported format's subsampling, fills per-plane bytesperline and sizeimage, and stores the chosen format. File open resumes runtime PM, powers the media pipeline, then opens a V4L2 file handle; release tears down vb2 state through `_vb2_fop_release`, drops pipeline PM, and runtime-suspends. Subdev init sets default sink format; get/set operate on try or active state and currently allow sink size/code updates.

State and persistence: active capture format is stored in `csi->fmt`; active subdev format is stored in `csi->subdev_fmt`. Try-state formats live in V4L2 subdev state. PM usage counts persist while file handles are open.

Dependencies and integration points: integrates with V4L2 ioctl core, videobuf2 V4L2 fops, V4L2 media controller PM, runtime PM, and the shared queue from `sun4i_dma.c`.

Risks: only one media-bus/pixel-format combination is supported. `s_fmt` does not check `vb2_is_busy`, so active queue use could be sensitive to V4L2 core serialization assumptions. Subdev source-pad format mirrors the stored format without explicit source propagation or validation. Capture width/height maxima do not use per-compatible `traits`.

Test signals: `v4l2-ctl --all`, format enumeration/try/set, open/close runtime PM balancing, mplane buffer requests, media-ctl format negotiation, and negative tests for unsupported inputs and formats.
