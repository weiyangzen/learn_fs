# sources/distributed-fs/ceph-client/drivers/gpu/drm/panthor/panthor_hw.h

`panthor_hw.h` defines Panthor architecture-specific hardware operation dispatch and wrapper APIs for reset, L2 power, and power-status tracing.

`struct panthor_hw_ops` contains function pointers for `soft_reset`, `l2_power_off`, `l2_power_on`, optional `power_changed_on`, and optional `power_changed_off`. `struct panthor_hw` currently stores the ops table. The header declares `panthor_hw_init()`, `panthor_hw_power_status_register()`, and `panthor_hw_power_status_unregister()`, and provides inline wrappers `panthor_hw_soft_reset()`, `panthor_hw_l2_power_on()`, `panthor_hw_l2_power_off()`, and `panthor_hw_has_pwr_ctrl()`.

Runtime flow is dispatch through `ptdev->hw->ops` after `panthor_hw_init()` has selected the table. `panthor_hw_has_pwr_ctrl()` derives behavior from `GPU_ARCH_MAJOR(ptdev->gpu_info.gpu_id) >= 14`, letting code choose PWR-register layouts for newer hardware.

The header owns no state, but defines the persistent dispatch shape stored in `ptdev->hw`. Dependencies are `panthor_device.h` and `panthor_regs.h`. Risks are dereferencing wrappers before `ptdev->hw` is initialized or assuming optional power-change callbacks exist. Test signals are compile coverage, reset/L2 power on arch10-13 and arch14, and power-status trace registration across both operation families.
