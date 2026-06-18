# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/Kconfig

## Purpose
`Kconfig` defines build-time configuration for the modern Intel `iwlwifi` driver, operation modes, debug support, device tracing, KUnit tests, LED support, and the disabled-by-default MEI-over-WLAN companion module.

## Important APIs, Types, and Options
- `IWLWIFI`: main tristate driver, depending on PCI, I/O memory, CFG80211, and MEI compatibility.
- `IWLDVM`, `IWLMVM`, `IWLMLD`: firmware operation mode modules for DVM, MVM, and MLD-capable devices.
- `IWLWIFI_OPMODE_MODULAR`: internal boolean that becomes true when opmode modules or tests are modular.
- `IWLWIFI_KUNIT_TESTS`: optional KUnit tests.
- `IWLWIFI_LEDS`: LED class integration, selecting LED triggers and mac80211 LEDs when supported.
- `IWLWIFI_DEBUG`, `IWLWIFI_DEBUGFS`, `IWLWIFI_DEVICE_TRACING`: debug logging, debugfs state, and ftrace event tracing.
- `IWLMEI`: Intel Management Engine communication over WLAN, currently depending on `BROKEN`.

## Control Flow and Integration
Kconfig controls which objects the Makefile builds and whether runtime features are compiled in. Enabling `IWLWIFI` alone is insufficient for a useful driver unless at least one opmode (`IWLDVM`, `IWLMVM`, or `IWLMLD`) is enabled. Debug options add sysfs/debugfs/tracing surfaces used by the shared driver and opmodes.

## State and Persistence Behavior
There is no runtime state. The options persist in the kernel build configuration and determine the available module set and compiled feature surfaces.

## Dependencies and Integration Points
This file integrates with kernel kbuild, mac80211/cfg80211, PCI, firmware loader, LED class, event tracing, devcoredump, PTP clock optional support, KUnit, and MEI. The top-level `iwlwifi/Makefile` consumes these symbols.

## Risks and Edge Cases
- A build with `IWLWIFI=y/m` but all opmodes disabled yields a warning and no useful hardware support.
- `IWLMEI` is explicitly broken; enabling it on unsuitable platforms can affect Wi-Fi behavior.
- Debug/tracing options increase module size and runtime overhead.
- LED support depends on specific LED class combinations.

## Test Signals
Build matrix coverage should include built-in and modular `IWLWIFI`, each opmode, debugfs/debug/tracing enabled and disabled, KUnit all-tests mode, and configuration where opmodes are intentionally disabled to confirm the warning path.
