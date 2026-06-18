# sources/distributed-fs/ceph-client/drivers/net/wireless/virtual/Kconfig

## Purpose
`virtual/Kconfig` declares build-time configuration symbols for virtual wireless drivers: `MAC80211_HWSIM` and `VIRT_WIFI`. These options make simulated or wrapper wireless devices available for testing and integration without real WLAN hardware.

## Important Options
- `MAC80211_HWSIM` is a tristate simulated radio testing tool for mac80211. It depends on `MAC80211`, builds the `mac80211_hwsim` module when selected as `M`, and is described as a developer testing tool rather than normal WLAN support.
- `VIRT_WIFI` is a tristate wrapper that makes ethernet connections appear as wifi connections through a special rtnetlink device. It depends on `CFG80211`.

## Control Flow And Integration
Kconfig controls whether the corresponding objects in `virtual/Makefile` are compiled. The dependency chain ensures hwsim only appears when mac80211 is enabled and virt_wifi only appears when cfg80211 is enabled. Users and test kernels select these symbols through kernel configuration.

## State And Persistence Behavior
This file has no runtime state. Selection persists only in the generated kernel `.config` and build artifacts.

## Dependencies
The symbols depend on the kernel wireless stack (`MAC80211` or `CFG80211`) and integrate with the parent wireless driver Kconfig menu.

## Risks And Test Signals
Risks are mostly configuration-level: missing dependencies, unclear help text, or Makefile mismatch. Test by running Kconfig dependency checks, building each option built-in and as a module, and loading `mac80211_hwsim`/creating `virt_wifi` devices in wireless-stack tests.
