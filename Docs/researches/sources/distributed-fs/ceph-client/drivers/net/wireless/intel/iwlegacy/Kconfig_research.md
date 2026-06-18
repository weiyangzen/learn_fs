# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlegacy/Kconfig

## Purpose

`Kconfig` defines the build-time configuration surface for the legacy Intel wireless drivers in this directory. It introduces the shared hidden `IWLEGACY` symbol, user-visible device driver choices for Intel 4965AGN and 3945ABG/BG hardware, and optional debugging/debugfs features shared by both drivers.

## Important Symbols

- `IWLEGACY` is a tristate selected by concrete drivers. It selects firmware loading, LED triggers, and mac80211 LED integration.
- `IWL4965` is the user-visible tristate for Intel Wireless WiFi 4965AGN. It depends on `PCI`, `MAC80211`, and compatible `LEDS_CLASS` configuration, selects `IWLEGACY`, builds module `iwl4965`, and documents the required microcode.
- `IWL3945` is the corresponding user-visible tristate for Intel PRO/Wireless 3945ABG/BG and builds module `iwl3945`.
- `IWLEGACY_DEBUG` enables full debug tracing and the runtime `debug_level` sysfs control.
- `IWLEGACY_DEBUGFS` enables low-impact debugfs inspection and depends on both `IWLEGACY` and `MAC80211_DEBUGFS`.

## Control Flow and Build Integration

Kconfig selection starts from a user or distribution enabling `IWL4965` or `IWL3945`. Either driver selects `IWLEGACY`, which then pulls in shared firmware-loader and LED integration dependencies. The `Makefile` uses these symbols to build `iwlegacy.o`, `iwl4965.o`, optional debug objects, and `iwl3945.o`.

The debug options are placed in a menu gated by `IWLEGACY`, so they are visible only when at least one legacy driver is selected or otherwise enabled. The device options mention firmware installation because the runtime driver requires external uCode in `/lib/firmware`.

## State and Persistence Behavior

This file has no runtime state, but it determines which object files and code paths exist in the kernel build. Built-in versus module choice persists in the kernel configuration and changes driver load/unload behavior. Debug symbols increase module size and expose runtime diagnostics through sysfs/debugfs when combined with matching code.

## Dependencies and Integration Points

The symbols integrate with:

- Linux kbuild through `obj-$(CONFIG_...)` and conditional object lists in the directory `Makefile`;
- mac80211 through `MAC80211`, `MAC80211_LEDS`, and `MAC80211_DEBUGFS`;
- firmware loading through `FW_LOADER`;
- LED class/trigger support through `LEDS_CLASS` and `LEDS_TRIGGERS`;
- user-space firmware packaging for `iwlwifi-4965-2.ucode` and 3945 firmware.

## Risks and Edge Cases

- `IWL4965` and `IWL3945` require `LEDS_CLASS=y || LEDS_CLASS=MAC80211`. Configurations with LED support as an incompatible module state will make the driver unavailable.
- The help text points to an old `intellinuxwireless.org` URL, which may no longer be useful for users obtaining firmware.
- `IWLEGACY_DEBUG` help names a specific example interface path under `wlan0`; actual interface names can differ.
- Because `IWLEGACY` is selected rather than directly prompted, shared code must remain valid when either or both concrete drivers are enabled.

## Test Signals

- Kconfig dependency tests with `PCI`, `MAC80211`, `LEDS_CLASS`, `MAC80211_DEBUGFS`, and module/built-in combinations.
- Build matrix for `IWL4965=m/y`, `IWL3945=m/y`, both enabled, and debug/debugfs toggles.
- Runtime module-load tests should verify firmware-loader requests and LED/debugfs/sysfs surfaces match the selected options.
