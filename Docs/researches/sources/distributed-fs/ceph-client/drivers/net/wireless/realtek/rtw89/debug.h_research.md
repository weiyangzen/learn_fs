# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/debug.h

Purpose: Declares the rtw89 debug categories, debugfs lifecycle hooks, and logging helpers shared across the driver. It provides compile-time fallbacks so most call sites can use `rtw89_debugfs_init()`, `rtw89_debugfs_deinit()`, `rtw89_debug()`, `rtw89_hex_dump()`, and `rtw89_debug_is_enabled()` regardless of whether debugfs or debug messages are enabled in the kernel configuration.

Important APIs, types, and functions: `enum rtw89_debug_mask` defines bit positions for TX/RX, RFK, RFK tracking, CFO, TSSI, TX power, HCI, rate adaptation, regulatory, PHY tracking, DIG, SER, firmware, BTC, beamforming, hardware scan, SAR, state, WoW, UL TB, channel, ACPI, EDCCA, power-save, and unexpected-event messages. `enum rtw89_debug_mac_reg_sel` declares the MAC/BB/IQK/RFC page selectors consumed by `debug.c`'s `mac_reg_dump` file. Under `CONFIG_RTW89_DEBUGFS`, the header declares `rtw89_debugfs_init()` and `rtw89_debugfs_deinit()`; otherwise both are empty inline stubs. It also maps `rtw89_info()`, `rtw89_info_once()`, `rtw89_warn()`, and `rtw89_err()` to device logging macros.

Control flow: For debug messages, `CONFIG_RTW89_DEBUGMSG` exposes the external `rtw89_debug_mask` and declares `rtw89_debug()`. `rtw89_hex_dump()` first checks `rtw89_debug_mask & mask`, then emits a byte dump through `print_hex_dump_bytes()`. `rtw89_debug_is_enabled()` returns the same mask test. Without `CONFIG_RTW89_DEBUGMSG`, all three are inline no-ops or `false`, allowing call sites to compile out runtime logging support while keeping source code simple.

State and persistence behavior: The only declared mutable global state is `rtw89_debug_mask`, implemented in `debug.c` as a module parameter when debug messages are enabled. Debugfs state is opaque to this header and owned by `struct rtw89_dev`. The logging macros do not persist data; they route messages to the device's kernel log stream.

Dependencies and integration points: Includes `core.h` for `struct rtw89_dev`, chip and device definitions, and kernel helpers such as `BIT()`. The mask enum is used throughout rtw89 subsystems to categorize `rtw89_debug()` and `rtw89_hex_dump()` messages. The MAC register selector enum is part of the debugfs ABI implemented by `debug.c`.

Risks: Adding or reordering enum values changes the user-visible meaning of `debug_mask` bits and can break scripts or field debugging workflows. The logging macros assume a valid `rtwdev->dev`. Because no-op stubs hide debugfs/debugmsg calls in non-debug builds, code must not rely on those calls for required side effects.

Test signals: Compile tests should cover enabled and disabled `CONFIG_RTW89_DEBUGFS` and `CONFIG_RTW89_DEBUGMSG` configurations. Runtime checks should confirm setting the `debug_mask` module parameter enables only the intended categories and that debugfs init/deinit calls are harmless in non-debugfs builds.
