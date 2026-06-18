# sources/distributed-fs/ceph-client/drivers/net/ethernet/fungible/Kconfig

## Purpose
Defines the top-level Kconfig menu for Fungible network devices and exposes the shared `FUN_CORE` service module plus the nested Ethernet driver configuration.

## Important APIs, Types, And Functions
The configuration symbols are `NET_VENDOR_FUNGIBLE` and `FUN_CORE`. `NET_VENDOR_FUNGIBLE` is a vendor menu gate defaulting to yes. `FUN_CORE` is a hidden tristate selected by device drivers and selects `SBITMAP`.

## Control Flow
When the vendor option is enabled, Kconfig makes `FUN_CORE` available and sources `drivers/net/ethernet/fungible/funeth/Kconfig`. Selecting `FUN_ETH` later selects `FUN_CORE`, causing the shared core module to build.

## State And Persistence
The file contributes build-time configuration only. It does not create runtime state or persistent data.

## Dependencies And Integration Points
Integrates with the kernel networking driver Kconfig hierarchy. `FUN_CORE` depends indirectly on `SBITMAP` because the core admin command tag allocator uses `struct sbitmap_queue`.

## Risks
Because `FUN_CORE` has no prompt, it must be selected correctly by leaf drivers. Disabling `NET_VENDOR_FUNGIBLE` hides the entire subtree and can make the Ethernet driver unavailable.

## Test Signals
Kconfig tests should verify vendor menu visibility, `FUN_ETH=m/y` selects `FUN_CORE=m/y`, and generated `.config` includes `SBITMAP` when the Fungible Ethernet driver is enabled.
