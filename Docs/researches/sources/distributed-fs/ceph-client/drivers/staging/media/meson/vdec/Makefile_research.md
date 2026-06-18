# sources/distributed-fs/ceph-client/drivers/staging/media/meson/vdec/Makefile

Purpose: this Makefile defines the composite object list for the Amlogic Meson VDEC driver and connects it to `CONFIG_VIDEO_MESON_VDEC`.

Important build API: `meson-vdec-objs` includes shared infrastructure (`esparser.o`, `vdec.o`, `vdec_helpers.o`, `vdec_platform.o`), hardware-block support (`vdec_1.o`, `vdec_hevc.o`), and codec implementations (`codec_mpeg12.o`, `codec_h264.o`, `codec_hevc_common.o`, `codec_vp9.o`). The final line `obj-$(CONFIG_VIDEO_MESON_VDEC) += meson-vdec.o` builds them as one module or built-in object.

Control flow and integration: composite object ordering ensures common infrastructure and codec ops are linked into one driver that registers a single platform driver/video device. Header-declared extern ops such as `vdec_1_ops`, `codec_mpeg12_ops`, `codec_h264_ops`, and `codec_vp9_ops` are resolved inside this module.

State and persistence behavior: no runtime state is maintained here. Build composition determines which codecs and hardware back ends are present for platform format tables.

Risks: adding or removing a codec requires updating both this object list and platform format tables. Since all codecs link into one module, a build break in one codec disables the entire VDEC driver.

Test signals: verify `meson-vdec.ko` contains all required codec and hardware symbols, and that modpost sees no unresolved references for codec ops, VDEC ops, platform tables, or exported helper functions.
