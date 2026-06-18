# sources/distributed-fs/ceph-client/drivers/media/platform/st/sti/hva/Makefile

Purpose: defines the object composition of the `st-hva` video encoder module.

Important APIs and entries: `obj-$(CONFIG_VIDEO_STI_HVA) += st-hva.o`; core objects are `hva-v4l2.o`, `hva-hw.o`, `hva-mem.o`, and `hva-h264.o`; `hva-debugfs.o` is conditional on `CONFIG_VIDEO_STI_HVA_DEBUGFS`.

Control flow: kbuild links the V4L2 front end, hardware executor, DMA memory helpers, and H.264 backend into one module.

State and persistence: no runtime state. It controls what implementation files are present in the module.

Dependencies and integration points: must stay aligned with HVA Kconfig and the encoder registry in `hva-v4l2.c`; the H.264 backend exports encoder descriptors referenced by that registry.

Risks: forgetting to add a new codec object or conditional symbol will produce a driver that enumerates fewer formats than expected or fails to link.

Test signals: build with `CONFIG_VIDEO_STI_HVA=m`, with and without `CONFIG_VIDEO_STI_HVA_DEBUGFS`.
