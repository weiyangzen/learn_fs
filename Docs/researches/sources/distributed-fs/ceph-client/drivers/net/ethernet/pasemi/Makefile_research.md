# sources/distributed-fs/ceph-client/drivers/net/ethernet/pasemi/Makefile

## Purpose
Builds the PA Semi MAC driver from its core and ethtool objects.

## Important APIs, Types, And Functions
`obj-$(CONFIG_PASEMI_MAC) += pasemi_mac_driver.o`; `pasemi_mac_driver-objs := pasemi_mac.o pasemi_mac_ethtool.o`.

## Control Flow
kbuild links core MAC logic and ethtool support into a single target according to `CONFIG_PASEMI_MAC`.

## State And Persistence
No runtime state.

## Dependencies And Integration Points
Depends on `PASEMI_MAC` from Kconfig and participates in the parent Ethernet build hierarchy.

## Risks And Edge Cases
Comment typo says "A Semi"; functional risk is stale object names if source files are renamed.

## Test Signals
`CONFIG_PASEMI_MAC=m` should produce `pasemi_mac_driver.ko` with both component objects.
