# sources/distributed-fs/ceph-client/drivers/gpu/drm/panthor/panthor_hw.c

`panthor_hw.c` binds GPU architecture versions to hardware operation tables, reads GPU identity and feature registers, names GPU models, applies optional NVMEM shader masks, and enables/disables power-status tracing.

Private data includes `struct panthor_hw_entry`, static arch v10 and v14 `struct panthor_hw` tables, and `panthor_hw_match[]`. Public APIs are `panthor_hw_init()`, `panthor_hw_power_status_register()`, and `panthor_hw_power_status_unregister()`. Helpers read `GPU_ID`, bind ops by architecture major, fill `ptdev->gpu_info`, derive model names, read optional `"shader-present"` NVMEM data, and iterate platform devices to toggle power-change IRQs for tracing.

Init reads GPU ID, rejects zero, binds arch10-13 to GPU-register reset/L2/power-change ops and arch14 to PWR ops, reads features/present masks, optionally overrides shader-present, and logs model and feature data. For arch14, present masks come from PWR registers; earlier versions use GPU registers.

Persistent state is `ptdev->hw` plus the populated `ptdev->gpu_info` exposed via uAPI and consumed by MMU/GPU/FW/devfreq code. Dependencies are Panthor GPU/PWR/register/device helpers, NVMEM, platform bus, and DRM logging. Risks include unsupported new architectures, heuristic model naming, global shader mask override, and partial failure while unregistering power tracing. Tests should boot arch10-14 devices, verify GPU info, test NVMEM override, trace power IRQ registration, and confirm arch14 routes through PWR ops.
