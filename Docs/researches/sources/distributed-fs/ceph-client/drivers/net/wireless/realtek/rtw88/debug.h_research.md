# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/debug.h

## Purpose

`debug.h` defines the public debug interface used throughout `rtw88`. It provides debug mask bits, conditional prototypes or stubs for debugfs helpers, the conditional `rtw_dbg()` logging API, and always-available `rtw_info`, `rtw_warn`, and `rtw_err` wrappers around device logging.

## Important APIs, Types, and Functions

`enum rtw_debug_mask` assigns one bit per debug category, including PCI, TX, RX, PHY, firmware, efuse, coexistence, RF calibration, regulatory, debugfs, power save, beamforming, WoWLAN, CFO, path diversity, adaptivity, hardware scan, state, SDIO, USB, unexpected events, and all-events. These masks are consumed by `rtw_dbg()` and `rtw_dbg_is_enabled()`.

When `CONFIG_RTW88_DEBUGFS` is enabled, the header declares `rtw_debugfs_init()`, `rtw_debugfs_deinit()`, and `rtw_debugfs_get_simple_phy_info()`. Without it, init/deinit become inline no-ops. When `CONFIG_RTW88_DEBUG` is enabled, `rtw_dbg()` is declared with printf checking and `rtw_dbg_is_enabled()` tests the global `rtw_debug_mask`; otherwise both compile to no-op/false.

## Control Flow

This header has no runtime control flow of its own beyond inline gating. Callers can invoke debugfs init/deinit unconditionally and let config stubs collapse away. Debug logging calls similarly compile in all call sites but become no-ops when debug support is disabled.

## State and Persistence

The only state referenced here is the external `rtw_debug_mask`, which controls whether debug messages emit in debug builds. The macros for `rtw_info`, `rtw_warn`, and `rtw_err` do not add state; they route messages to `rtwdev->dev`.

## Dependencies and Integration Points

`debug.h` is included broadly by driver subsystems that need categorized debug logging. It depends on the caller having visible `struct rtw_dev` and, for debugfs simple PHY information, `struct seq_file`. It integrates with Kconfig so debugfs and dynamic debug logging can be compiled out without changing call sites.

## Risks

The main risk is category misuse: excessive logging under hot paths can affect performance when debug masks are enabled, while using the wrong mask makes targeted diagnostics harder. Because disabled `rtw_dbg()` arguments are still type-checked but not evaluated in the inline stub, side-effectful arguments should be avoided.

## Test Signals

Build coverage should include debugfs/debug enabled and disabled combinations. Runtime checks should confirm category-specific logs appear only when `rtw_debug_mask` includes the category, while `rtw_info/warn/err` remain available regardless of config.
