# sources/distributed-fs/ceph-client/drivers/video/fbdev/omap2/omapfb/dss/manager.c

## Purpose
`manager.c` allocates and exposes OMAP DSS overlay manager objects and provides validation helpers for manager and overlay configurations before applying them to DISPC.

## Important APIs, types, and functions
Public functions include `dss_init_overlay_managers`, `dss_init_overlay_managers_sysfs`, uninit counterparts, `omap_dss_get_num_overlay_managers`, `omap_dss_get_overlay_manager`, `dss_mgr_simple_check`, `dss_mgr_check_timings`, and `dss_mgr_check`. Internal helpers include `dss_mgr_check_zorder` and `dss_mgr_check_lcd_config`.

## Control Flow
Initialization queries DSS feature data for manager count, allocates the manager array, assigns stable names/ids (`lcd`, `tv`, `lcd2`, `lcd3`), fills supported display/output masks, and initializes overlay lists. Sysfs init creates a kobject for each manager. Validation checks feature-specific alpha/keying constraints, unique zorder when free zorder is supported, manager timing validity via DISPC, LCD clock divisor and data-line constraints, and then calls `dss_ovl_check` for each active overlay on the manager.

## State and Persistence
Global runtime state is `num_managers` and the allocated `managers` array. Each manager stores name, id, capability masks, overlay list, kobject, and function pointers filled by other DSS code. No state persists across driver teardown.

## Dependencies and Integration Points
It depends on DSS feature tables, DISPC timing validation, overlay validation from `overlay.c`, manager sysfs from `manager-sysfs.c`, and exported fbdev/DSS APIs used by output drivers and omapfb.

## Risks
Allocation failure uses `BUG_ON`, which is harsh for memory pressure. `omap_dss_get_overlay_manager` checks only upper bound and not negative indices. Validation depends on callers passing complete `overlay_infos` arrays. LCD config checks are generic and defer some interface-specific validation.

## Test Signals
Test manager count/name/id per SoC, sysfs kobject creation/removal, invalid duplicate zorders, alpha/keying constraints on OMAP3, invalid timing and LCD divisors, unsupported video port widths, overlay bounds failures, and manager lookup edge cases.
