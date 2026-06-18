## sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/vcodec/encoder/Makefile

Purpose: defines the objects linked into the MediaTek vcodec encoder module when `CONFIG_VIDEO_MEDIATEK_VCODEC` is enabled.

Important APIs/types/functions: no C API is defined. The build target is `mtk-vcodec-enc.o`, composed from VP8 and H.264 codec backends, V4L2 encoder frontend/driver files, power management, encoder dispatch, and VPU transport.

Control flow: Kbuild compiles listed objects into one module object. Link order ensures backend symbols such as `venc_vp8_if` and `venc_h264_if` are available to `venc_drv_if.o` and frontend code.

State and persistence behavior: build-only file with no runtime state.

Dependencies and integration points: tied to kernel Kbuild, the parent MediaTek vcodec Kconfig, and the source files in the encoder directory. Adding a new encoder backend requires updating this object list and dispatch logic.

Risks: missing objects cause unresolved symbols or unavailable formats. The trailing backslash after `venc_vpu_if.o` is tolerated by Kbuild in this context but is a style footgun when appending lines. Conditional per-codec builds are not present, so all listed encoder backends build together under the shared config.

Test signals: kernel build with `CONFIG_VIDEO_MEDIATEK_VCODEC=m/y`, link checks for H.264 and VP8 backend symbols, and module load smoke tests.
