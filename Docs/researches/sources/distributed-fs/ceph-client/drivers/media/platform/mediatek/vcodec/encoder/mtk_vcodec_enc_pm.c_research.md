## sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/vcodec/encoder/mtk_vcodec_enc_pm.c

Purpose: implements encoder power-management helpers for clock discovery, runtime PM power on/off, and clock enable/disable.

Important APIs/types/functions: exported helpers are `mtk_vcodec_init_enc_clk`, `mtk_vcodec_enc_pw_on`, `mtk_vcodec_enc_pw_off`, `mtk_vcodec_enc_clock_on`, and `mtk_vcodec_enc_clock_off`.

Control flow: clock init counts `clock-names`, allocates an array of `mtk_vcodec_clk_info`, reads each clock name, and obtains a managed clock handle. Encode dispatch powers on with `pm_runtime_resume_and_get`, enables all clocks in order before backend encode, disables clocks in reverse order afterward, and releases runtime PM with `pm_runtime_put`.

State and persistence behavior: discovered clocks are stored in `dev->pm.venc_clk` for the platform device lifetime. Runtime PM reference state is maintained by the PM core; this file does not track a separate refcount.

Dependencies and integration points: depends on device-tree `clock-names`, Linux clk API, runtime PM, and common `mtk_vcodec_pm` structures. Called by platform probe and `venc_if_encode`.

Risks: `mtk_vcodec_enc_clock_on` returns void, so clock-enable failures are logged but not propagated to encode callers. Partial clock-enable rollback is handled locally. Runtime PM failure is propagated by `mtk_vcodec_enc_pw_on`; callers must avoid enabling clocks when it fails.

Test signals: probe with missing/malformed clock names, encode path runtime PM balance, fault injection for `clk_prepare_enable`, and suspend/resume or repeated stream start/stop cycles checking no clock remains enabled.
