# sources/distributed-fs/ceph-client/drivers/media/platform/st/sti/delta/Kconfig

Purpose: defines Kconfig symbols for the STMicroelectronics Delta video decoder driver and its MJPEG decoder support.

Important APIs and symbols: `VIDEO_STI_DELTA` is the user-visible tristate for the multi-format Delta V4L2 decoder, depending on V4L mem2mem drivers, `VIDEO_DEV`, and `ARCH_STI || COMPILE_TEST`. `VIDEO_STI_DELTA_MJPEG` is a bool child option defaulting to enabled. `VIDEO_STI_DELTA_DRIVER` is the internal tristate that becomes buildable only when the base driver and MJPEG support are selected; it selects `VIDEOBUF2_DMA_CONTIG`, `V4L2_MEM2MEM_DEV`, and `RPMSG`.

Control flow: Kconfig selection determines whether the `st-delta` module is built and whether MJPEG-specific objects are linked. The base prompt explicitly warns that the driver builds only when at least one decoder is selected.

State and persistence: no runtime state. The selected symbols persist in the kernel build configuration and control module availability.

Dependencies and integration points: integrates with the media platform driver menu, videobuf2, V4L2 mem2mem, rpmsg firmware transport, and STi SoC architecture support.

Risks: only MJPEG exists in this snapshot, so disabling `VIDEO_STI_DELTA_MJPEG` effectively disables the driver object through `VIDEO_STI_DELTA_DRIVER`. Users may expect the base multi-format symbol alone to produce a module, but the hidden driver symbol prevents that without a decoder.

Test signals: menuconfig visibility, allmodconfig/allnoconfig with `COMPILE_TEST`, and module build checks for `VIDEO_STI_DELTA=m` plus MJPEG enabled/disabled.
