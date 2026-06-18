## sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/vcodec/encoder/mtk_vcodec_enc.h

Purpose: declares encoder frontend constants and helper APIs shared between the encoder platform driver and V4L2 frontend implementation.

Important APIs/types/functions: defines encoder IRQ status bits and register offsets for status/acknowledge. `struct mtk_video_enc_buf` extends `v4l2_m2m_buffer` with per-buffer parameter-change flags and a snapshot of `mtk_enc_params`. It declares V4L2 ioctl/m2m operation tables plus lock, queue initialization, release, control setup, and default-parameter functions.

Control flow: source VB2 buffers are allocated with `struct mtk_video_enc_buf` as private storage, allowing `vb2ops_venc_buf_queue` to latch pending control changes onto the specific frame before m2m scheduling.

State and persistence behavior: per-buffer state persists from QBUF until the encode worker consumes the source buffer. IRQ constants are stateless register ABI definitions used by the IRQ handler and codec backends waiting for SPS/PPS/frame completion.

Dependencies and integration points: includes videobuf2 and V4L2 mem2mem headers plus `mtk_vcodec_enc_drv.h`. Consumed by `mtk_vcodec_enc.c`, `mtk_vcodec_enc_drv.c`, and codec backend files.

Risks: IRQ bit definitions must match hardware across supported SoCs. Per-buffer parameter snapshots can become stale if controls are changed after QBUF, but that is the intended frame-specific behavior and should be documented in userspace expectations.

Test signals: buffer queue tests for parameter-change latching; IRQ register tests on hardware confirming SPS/PPS/frame bits are acknowledged correctly; compile checks after modifying `mtk_enc_params`.
