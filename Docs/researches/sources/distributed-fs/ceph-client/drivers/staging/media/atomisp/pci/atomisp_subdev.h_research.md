# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/atomisp_subdev.h

Purpose: defines the V4L2/media subdevice side of the atomisp driver, including the ISP subdevice, its sink/source pads, the single video output pipe, cached CSS parameter blocks, metadata/statistics queues, streaming flags, and helper prototypes used by the main PCI/V4L2 driver.

Important APIs/types/functions: key types are `atomisp_video_pipe`, `atomisp_pad_format`, `atomisp_css_params`, `atomisp_subdev_params`, `atomisp_css_params_with_list`, and `atomisp_sub_device`. The exported helpers cover media-bus format lookup/conversion, active/try format and selection access, pending event cleanup, entity registration, subdevice initialization, and teardown.

Control flow: this header does not execute logic directly, but it defines the state container that `atomisp_v4l2.c`, format negotiation, vb2 queue handling, CSS parameter setting, and IRQ completion paths share. The video pipe tracks buffers in CSS, buffers pending CSS handoff, and per-frame parameter lists. The subdevice tracks the current input, streaming state, stream preparation, resume recreation, raw-buffer locking, and CSS statistics queues.

State and persistence: all state is runtime-only in the `atomisp_device`/`atomisp_sub_device` graph. Persistent behavior is delegated to sensor firmware, PCI config, and CSS firmware; this header mainly describes in-memory queues, cached frame formats, and cached ISP parameter values.

Dependencies and integration: depends on V4L2 controls/subdevs, media pads/pipelines, videobuf2, atomisp common/compat layers, and the Intel CSS `ia_css` API. It is the central contract between atomisp video nodes, the internal ISP subdevice, MIPI CSI2 entities, and CSS parameter code.

Risks and test signals: lock ordering is explicitly constrained because `vb_queue_mutex` must precede `isp->mutex`. The many lists and IRQ-protected buffer states need stress tests around stream-on/off, per-frame parameter queuing, metadata/statistics dequeue, suspend/resume, and error unwinds. Format negotiation tests should cover compressed/uncompressed media-bus codes and source/sink selection rectangles.
