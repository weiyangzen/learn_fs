## sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/vcodec/decoder/vdec_drv_base.h

Purpose: defines the common decoder backend vtable used by codec-specific MediaTek decoder implementations. It gives the generic decoder layer a uniform contract for initialization, decode, parameter query, and teardown.

Important APIs/types/functions: the only exported type is `struct vdec_common_if` with callbacks `init`, `decode`, `get_param`, and `deinit`. Callback signatures use `struct mtk_vcodec_dec_ctx`, `struct mtk_vcodec_mem`, `struct vdec_fb`, and `enum vdec_get_param_type` from the decoder interface headers.

Control flow: no runtime flow exists in the header. Implementations such as the VP9 LAT backend populate a constant `vdec_common_if`; `vdec_drv_if.c` selects the correct table based on FourCC and invokes callbacks while managing hardware power/current context.

State and persistence behavior: the header owns no state. It defines that implementations store opaque backend state in `ctx->drv_handle` after `init`, use it during `decode`/`get_param`, and release it during `deinit`.

Dependencies and integration points: includes `vdec_drv_if.h` and is included by dispatcher and codec files. It is an internal ABI between generic V4L2 decoder code and codec-specific hardware/firmware drivers.

Risks: callback contract comments mention an output handle for `init`, but the actual signature only returns status and relies on `ctx->drv_handle`; implementations must remain consistent. Because the vtable has no capability flags, dispatch logic must know which callback table is valid for each format and hardware architecture.

Test signals: compile coverage should catch signature drift. Runtime validation comes from opening each supported decoder format and verifying `vdec_if_init`, decode, param query, and deinit route to the expected backend without null callback or stale `drv_handle` use.
