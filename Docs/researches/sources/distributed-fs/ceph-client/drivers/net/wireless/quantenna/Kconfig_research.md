<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/quantenna/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/quantenna/Kconfig

## Purpose
This Kconfig file adds the Quantenna wireless vendor menu and conditionally includes the qtnfmac driver Kconfig.

## Important APIs, Types, And Functions
It defines `config WLAN_VENDOR_QUANTENNA` as a default-y boolean vendor selector and sources `drivers/net/wireless/quantenna/qtnfmac/Kconfig` when enabled.

## Control Flow
During kernel configuration, enabling the vendor selector exposes Quantenna FullMAC PCIe support options. The selector does not build code by itself.

## State And Persistence
The persistent configuration output is `CONFIG_WLAN_VENDOR_QUANTENNA` and any subordinate qtnfmac symbols.

## Dependencies And Integration Points
Integrated by the parent wireless Kconfig tree and delegates actual driver configuration to qtnfmac.

## Risks
Disabling the vendor gate hides all Quantenna driver options. Path drift in the sourced Kconfig would break menu traversal.

## Test Signals
Run Kconfig with the vendor enabled/disabled and verify qtnfmac options appear only under the enabled vendor menu.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/quantenna/Kconfig -->
