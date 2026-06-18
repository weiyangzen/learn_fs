<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/purelifi/plfxlc/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/purelifi/plfxlc/Kconfig

## Purpose
This Kconfig file defines the pureLiFi X/XL/XC USB LiFi driver option.

## Important APIs, Types, And Functions
`config PLFXLC` is a tristate option named "pureLiFi X, XL, XC device support". It depends on `CFG80211`, `MAC80211`, and `USB`. Help text states that the driver supports pureLiFi USB adapters based on an 802.11 OFDM PHY using light as the medium and common 802.11 authentication/encryption modes.

## Control Flow
When selected as built-in or module, Kbuild compiles the plfxlc object list. As a module, the resulting module name is `plfxlc`.

## State And Persistence
The selected value persists in the kernel `.config` as `CONFIG_PLFXLC`.

## Dependencies And Integration Points
The option is sourced by the parent pureLiFi vendor Kconfig and consumed by the plfxlc Makefile. The dependencies match the code's use of USB device IDs, mac80211 hardware registration, and cfg80211/wiphy integration.

## Risks
Missing dependency updates could allow build failures if code gains new subsystem calls. Because the option is a driver leaf under a default-y vendor menu, users still need to explicitly select the device support.

## Test Signals
Kconfig validation should show `PLFXLC` unavailable without USB/mac80211/cfg80211 and buildable as module or built-in when dependencies are present.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/purelifi/plfxlc/Kconfig -->
