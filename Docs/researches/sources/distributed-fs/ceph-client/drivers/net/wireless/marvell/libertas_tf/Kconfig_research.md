# sources/distributed-fs/ceph-client/drivers/net/wireless/marvell/libertas_tf/Kconfig

## Purpose
Declares Kconfig options for the Libertas thinfirm driver family.

## Important Options
`LIBERTAS_THINFIRM` is the main tristate library and depends on `MAC80211`, selecting `FW_LOADER`. `LIBERTAS_THINFIRM_DEBUG` enables full thinfirm debugging output when the library is enabled. `LIBERTAS_THINFIRM_USB` builds USB support for 8388 devices and depends on both thinfirm and USB.

## Control Flow And State
No runtime control flow. The selected symbols determine whether the thinfirm core, debug macros, and USB module are compiled.

## Dependencies And Integration
Integrates with kernel build configuration and the `libertas_tf/Makefile`. Thinfirm differs from the full Libertas stack by integrating with mac80211 rather than the full-firmware cfg80211/netdev core.

## Risks And Test Signals
Risks include missing dependency selections for firmware loading or mac80211 APIs, and debug code compiled unexpectedly. Test signals are successful builds for module/built-in combinations and correct object inclusion for USB.
