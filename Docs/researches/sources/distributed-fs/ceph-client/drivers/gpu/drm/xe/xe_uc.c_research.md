# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_uc.c

Purpose: Coordinates Xe microcontroller lifecycle across GuC, HuC, GSC, and WOPCM: initialization, post-hwconfig setup, firmware load, reset/sanitize, start/stop, suspend/resume, and wedging.

Important APIs/types/functions: Public lifecycle functions are `xe_uc_init_noalloc`, `xe_uc_init`, `xe_uc_init_post_hwconfig`, `xe_uc_load_hw`, `xe_uc_reset_prepare`, `xe_uc_stop_prepare`, `xe_uc_stop`, `xe_uc_start`, `xe_uc_suspend_prepare`, `xe_uc_suspend`, `xe_uc_runtime_suspend`, `xe_uc_runtime_resume`, `xe_uc_sanitize_reset`, and `xe_uc_declare_wedged`. Internal helpers map `xe_uc` to GT/device, reset GuC, sanitize HuC/GuC, wait for reset, and handle SR-IOV VF hardware load.

Control flow: Early init initializes GuC noalloc state. Full init initializes GuC/HuC/GSC even when uC is disabled so firmware status moves to disabled, then initializes WOPCM and performs a minimal GuC load for hwconfig on enabled non-VF devices. Post-hwconfig sanitizes/resets uC, then initializes GuC/HuC/GSC post-hwconfig. Hardware load for PF uploads HuC and GuC, enables GuC communication, records default LRCs, does GuC post-load init, starts power/RC features, enables engine activity stats, attempts HuC auth without failing driver load, and starts async GSC load. VF load resets, enables communication, connects to PF, marks submission enabled, enables opt-in features, and records LRCs.

State and persistence behavior: Mutates firmware/submission/power-management state inside `uc->guc`, `uc->huc`, `uc->gsc`, and `uc->wopcm`. Most operations are no-ops when `xe_device_uc_enabled()` is false. Suspend waits for reset completion, stops GuC, and calls GuC suspend. Runtime suspend/resume delegate to GuC runtime PM.

Dependencies and integration points: Integrates with GuC, HuC, GSC, WOPCM, GT, SR-IOV VF, power control, render C-state, engine activity, default LRC recording, and wedge handling. Uses GT logging and assertions.

Risks: Lifecycle ordering is critical: communication must be enabled after firmware upload, WOPCM must exist before loading, reset/sanitize must clear stale states, and GSC async load must be stopped/waited during suspend/stop prepare. HuC auth failures are logged but non-fatal by design. VF path diverges significantly and relies on PF-preloaded firmware.

Test signals: Boot/load, GT reset, suspend/resume, runtime PM, SR-IOV VF startup, GuC disabled mode, HuC auth failure, and wedge tests. Trace/log evidence should show firmware upload, GuC communication, RC/PC startup, and non-fatal HuC handling.
