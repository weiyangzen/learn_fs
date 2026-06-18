# sources/distributed-fs/ceph-client/drivers/net/wireless/intersil/Kconfig

## Purpose
This Kconfig file defines the top-level vendor menu switch for Intersil wireless devices and includes the p54 driver configuration subtree.

## Important APIs, Types, and Functions
- `config WLAN_VENDOR_INTERSIL` is a boolean, default `y`, titled "Intersil devices".
- The `if WLAN_VENDOR_INTERSIL` block sources `drivers/net/wireless/intersil/p54/Kconfig`.

## Control Flow
During kernel configuration, disabling `WLAN_VENDOR_INTERSIL` hides child questions for Intersil hardware without directly building code. Enabling it exposes p54 options.

## State and Persistence Behavior
The only persisted state is kernel `.config` choices. It has no runtime behavior.

## Dependencies and Integration Points
It integrates with the wireless drivers Kconfig hierarchy and gates the p54 Kconfig definitions.

## Risks and Edge Cases
If the source path changes or new Intersil subdrivers are added without sourcing them here, configuration options may become unreachable. Because it defaults to `y`, p54 options remain visible in typical configs.

## Test Signals
`make menuconfig`/`oldconfig` visibility and successful Kconfig parsing are the primary signals.
