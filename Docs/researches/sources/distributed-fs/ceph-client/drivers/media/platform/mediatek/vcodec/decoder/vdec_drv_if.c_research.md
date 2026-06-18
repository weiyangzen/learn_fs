## sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/vcodec/decoder/vdec_drv_if.c

Purpose: generic decoder dispatch layer. It maps V4L2 compressed formats to codec-specific `vdec_common_if` tables, handles hardware enable/disable around backend calls, validates DMA alignment for decode buffers, and serializes parameter queries.

Important APIs/types/functions: public functions are `vdec_if_init`, `vdec_if_decode`, `vdec_if_get_param`, and `vdec_if_deinit`. `vdec_if_init` selects backends including H.264, VP8, VP9, HEVC, AV1, and multi-core/LAT variants. `vdec_if_decode` validates 64-byte bitstream alignment and 512-byte frame-buffer plane alignment before invoking `ctx->dec_if->decode`.

Control flow: init chooses `ctx->dec_if` and `ctx->hw_id` based on FourCC plus platform hardware architecture and subdev support, powers the selected block, calls backend init, then disables hardware. Decode checks optional bitstream and framebuffer alignment, rejects missing `drv_handle`, powers hardware, installs current context for IRQ routing, calls backend decode, clears current context, and powers down. Get-param requires a driver handle and wraps backend query in `mtk_vdec_lock`. Deinit powers hardware, calls backend deinit, powers down, and clears `ctx->drv_handle`.

State and persistence behavior: this layer mutates `ctx->dec_if`, `ctx->hw_id`, and `ctx->drv_handle` indirectly through backend init/deinit. It does not persist buffers itself, but controls when hardware context is active and visible to interrupt handlers.

Dependencies and integration points: depends on format constants, MediaTek decoder platform data, hardware power helpers, current-context routing, and backend symbols declared in `vdec_drv_if.h`. It is the key integration point between the V4L2 decoder frontend and codec backend implementations.

Risks: wrong FourCC-to-backend mapping can select incompatible firmware ABI or hardware block. Alignment checks reject only provided buffers, so header-only/flush calls rely on backend handling. Init/deinit power sequencing assumes backend init/deinit may touch hardware even when most firmware state is remote. Hardware ID selection for LAT architectures must match interrupt and queue routing.

Test signals: verify each advertised decode FourCC initializes on each compatible SoC data path, including subdev-supported H.264 and LAT VP9/AV1. Negative tests should cover unsupported FourCC, uninitialized decode, misaligned bitstream/framebuffer DMA, and deinit after partial init failure.
