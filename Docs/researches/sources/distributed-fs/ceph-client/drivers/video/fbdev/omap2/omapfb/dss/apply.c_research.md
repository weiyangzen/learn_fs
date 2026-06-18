# sources/distributed-fs/ceph-client/drivers/video/fbdev/omap2/omapfb/dss/apply.c

## Purpose

`apply.c` is the legacy OMAP DSS compatibility apply layer that bridges fbdev overlay/manager APIs to DISPC hardware programming. The complete 1690-line file was read. It manages cached overlay/manager state, validates configurations, writes DISPC registers, schedules GO bits, handles VSYNC/FRAMEDONE completion, and installs compatibility manager/overlay operations.

## Important APIs, Types, and Functions

`struct ovl_priv_data` holds user overlay info, active info, dirty/shadow flags, enabled/enabling state, and FIFO thresholds. `struct mgr_priv_data` holds manager info, busy/updating/enabled flags, timing/LCD config, and framedone callback. Global `dss_data` is protected by `data_lock`; blocking sequences use `apply_lock`; extra-info waits use `extra_updated_completion`. Key functions include `dss_check_settings_low()`, `need_isr()`, `dss_mgr_wait_for_vsync()`, `dss_mgr_wait_for_go()`, `dss_ovl_write_regs()`, `dss_mgr_write_regs()`, `dss_set_go_bits()`, `dss_apply_irq_handler()`, `omap_dss_mgr_apply()`, manager/overlay enable/disable/set-info/set-manager helpers, and exported `omapdss_compat_init()` / `omapdss_compat_uninit()`.

## Control Flow

The layer maintains four configuration levels: user cache from `set_info()`, apply cache after `apply()`, DISPC shadow registers after register writes, and live registers after VFP or output enable. User calls set overlay/manager info under spinlock, then `apply()` validates current plus dirty state, copies user info into active info, writes registers when the manager can accept them, and sets GO bits. For automatic update managers, VSYNC IRQs clear busy/shadow state and advance pending writes. For manual update managers, `start_update` writes registers, enables output, and waits for FRAMEDONE to invoke callbacks.

## State and Persistence Behavior

State is entirely in kernel memory and DISPC shadow/live registers. Dirty flags model pending updates across IRQ boundaries. Manager `busy` tracks GO bit ownership; `updating` tracks enabled DISPC output; `extra_info_dirty` is used for enable, FIFO threshold, timing, and LCD-config changes that must be written even for disabled overlays. `compat_refcnt` allows nested compatibility init/uninit.

## Dependencies and Integration Points

The file depends on overlay/manager lists from DSS core, `dss_mgr_check()` / simple checks from manager/overlay code, DISPC programming APIs, `dispc-compat` IRQ helpers, display sysfs initialization, overlay/manager sysfs initialization, and runtime PM via `dispc_runtime_get()`. It installs `dss_mgr_ops` and populates function pointers in every `omap_overlay_manager` and `omap_overlay`.

## Risks and Edge Cases

Most correctness depends on lock ordering between `apply_lock`, `data_lock`, and DISPC IRQ callbacks. GO waits use fixed 500 ms timeouts and tolerate the fourth-iteration failure by returning 0 after logging. Manual update overlays may need a dummy update before manager detachment; current code returns `-EINVAL`. Register writes can be skipped if validation fails, leaving dirty state pending. Error paths in init must balance display sysfs, manager ops, overlay sysfs, IRQ setup, and runtime PM.

## Test Signals

Signals include overlay enable/disable, manager enable/disable, changing overlay info while active, GO wait behavior on automatic outputs, manual update FRAMEDONE callbacks, FIFO threshold recalculation, invalid configuration rejection, changing managers while overlays are disabled/enabled, suspend/resume display state, and repeated `omapdss_compat_init()` / `uninit()` refcount coverage.
