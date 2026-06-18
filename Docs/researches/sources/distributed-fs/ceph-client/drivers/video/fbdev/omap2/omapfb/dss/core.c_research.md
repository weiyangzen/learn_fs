# sources/distributed-fs/ceph-client/drivers/video/fbdev/omap2/omapfb/dss/core.c

## Purpose

`core.c` is the top-level OMAP DSS platform driver and module init/exit coordinator. The complete 287-line source was read. It stores the core platform device, exposes board-level helpers, initializes feature tables and debugfs, registers PM notifications, and registers/unregisters all DSS output platform drivers.

## Important APIs, Types, and Functions

Global `core` stores `pdev` and `default_display_name`; `def_disp` is a module parameter. Exported helpers include `omapdss_get_default_display_name()`, `omapdss_get_version()`, `dss_get_core_pdev()`, `dss_dsi_enable_pads()`, `dss_dsi_disable_pads()`, and `dss_set_min_bus_tput()`. Debugfs helpers include `dss_debugfs_create_file()` when enabled. Platform lifecycle is handled by `omap_dss_probe()`, `remove()`, `shutdown()`, `omap_dss_init()`, and `omap_dss_exit()`.

## Control Flow

Module init probes the `omapdss` platform driver, initializes DSS features from board data, creates debugfs, stores default display override, registers a PM notifier, then iterates `dss_output_drv_reg_funcs` to register DSS, DISPC, and configured output drivers. On registration failure it unwinds with the reverse unregistration table. PM notifications suspend active displays before suspend/hibernate/restore and resume them afterward. Shutdown disables all active displays.

## State and Persistence Behavior

Persistent runtime state is limited to the static `core` struct and registered driver/module state. Default display name persists for the module lifetime. Display suspend intent is held per `omap_dss_device` in display code, not here.

## Dependencies and Integration Points

The file depends on platform data `struct omap_dss_board_info`, DSS feature initialization, display suspend/resume helpers, debugfs, and each output driver's init/uninit function. It is the source for `dss_get_core_pdev()`, used by compatibility init for sysfs parentage.

## Risks and Edge Cases

The code assumes platform data is valid when `omapdss_get_version()` is called. The init error unwind index expression is subtle and depends on registration array ordering matching unregistration order. PM notifier callbacks call into display drivers and can fail only by returning the display helper's status, which is currently always 0.

## Test Signals

Signals include module init/uninit with every Kconfig output combination, failure injection in output driver registration, PM notifier suspend/resume path with active displays, shutdown disabling displays, debugfs creation/removal, and `def_disp` module parameter behavior.
