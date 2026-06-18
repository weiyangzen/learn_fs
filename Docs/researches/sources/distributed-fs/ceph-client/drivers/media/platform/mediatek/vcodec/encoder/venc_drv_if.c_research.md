## sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/vcodec/encoder/venc_drv_if.c

Purpose: generic encoder backend dispatcher. It selects codec-specific backends, serializes hardware access with the encoder mutex, manages runtime PM/clocks around encode, and routes deinit/parameter calls.

Important APIs/types/functions: public functions are `venc_if_init`, `venc_if_set_param`, `venc_if_encode`, and `venc_if_deinit`.

Control flow: init selects VP8 or H.264 backend by capture FourCC and calls backend init under `mtk_venc_lock`. Set-param calls backend `set_param` under the same lock. Encode locks, installs `ctx` as `dev->curr_ctx` under `irqlock`, powers on runtime PM, enables clocks, invokes backend encode, disables clocks/power, clears `curr_ctx`, and unlocks. Deinit no-ops if `drv_handle` is null, otherwise calls backend deinit under lock and clears the handle.

State and persistence behavior: manages `ctx->enc_if`, `ctx->drv_handle`, and `dev->curr_ctx`. It does not own codec buffers but defines the active hardware window during which IRQs are routed to the current context.

Dependencies and integration points: depends on encoder frontend lock helpers, PM helpers, codec vtables, and platform IRQ handler. It bridges V4L2 m2m worker code to backend firmware/hardware operations.

Risks: `mtk_vcodec_enc_clock_on` failures are not propagated, so backend encode may run after a logged clock-enable failure. If power-on fails, `curr_ctx` is not cleared before the goto label in the current code path, which can leave stale IRQ routing until a later encode clears it. The single encoder mutex serializes instances and may limit concurrency but protects shared hardware.

Test signals: H.264/VP8 init with unsupported FourCC, PM failure injection, encode timeout/error propagation, concurrent contexts contending for `enc_mutex`, and IRQ routing validation using `curr_ctx`.
