## sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/vcodec/encoder/venc_drv_base.h

Purpose: defines the common encoder backend vtable used by codec-specific H.264 and VP8 implementations.

Important APIs/types/functions: `struct venc_common_if` contains `init`, `encode`, `set_param`, and `deinit` callbacks. The encode callback accepts `enum venc_start_opt`, optional input frame buffer, output bitstream buffer, and `venc_done_result`.

Control flow: `venc_drv_if.c` selects a `venc_common_if` by capture FourCC, initializes the backend, and routes parameter and encode calls through this table while managing locks, power, clocks, and current IRQ context.

State and persistence behavior: this header owns no state. Backend init stores an opaque codec instance in `ctx->drv_handle`; deinit frees it.

Dependencies and integration points: includes encoder context definitions and `venc_drv_if.h`. It is the internal ABI between the generic encoder dispatch layer and codec-specific files.

Risks: callback signatures encode assumptions about synchronous encode completion and a single output result structure. Adding asynchronous or multi-part bitstream behavior would require extending this interface.

Test signals: compile/link coverage for all backend vtables and runtime smoke tests selecting H.264 and VP8 capture formats.
