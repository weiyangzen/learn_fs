# sources/distributed-fs/ceph-client/drivers/media/test-drivers/vicodec/Makefile

Purpose: Kbuild recipe for the vicodec module.

Important APIs/types/functions: `vicodec-objs := vicodec-core.o codec-fwht.o codec-v4l2-fwht.o`; `obj-$(CONFIG_VIDEO_VICODEC) += vicodec.o`.

Control flow: Kbuild links the V4L2 mem2mem core wrapper, raw FWHT codec, and V4L2 FWHT adapter into one module.

State and persistence: build metadata only.

Dependencies and integration points: ensures internal symbols from the FWHT codec and wrapper resolve inside the single `vicodec` module.

Risks: changing object order or omitting one object breaks exported-internal functions such as `v4l2_fwht_encode()`/`decode()` or `fwht_encode_frame()`/`decode_frame()`.

Test signals: module link success and `modinfo vicodec`/device registration smoke tests.
