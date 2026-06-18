# sources/distributed-fs/ceph-client/drivers/net/ethernet/fungible/funeth/Kconfig

## Purpose
Defines the Fungible Ethernet driver Kconfig symbol.

## Important APIs, Types, And Functions
`FUN_ETH` is a tristate prompted as "Fungible Ethernet device driver". It depends on `PCI_MSI` and on compatible TLS settings, selects `NET_DEVLINK`, and selects `FUN_CORE`.

## Control Flow
When enabled, kbuild compiles the `funeth` module and ensures the core service module and devlink support are enabled. The TLS dependency allows the driver when TLS device offload support is enabled or when `TLS_DEVICE=n`.

## State And Persistence
Build-time configuration only.

## Dependencies And Integration Points
Connects the Ethernet driver to PCI MSI, optional kTLS device offload, devlink, and `funcore`.

## Risks
The TLS expression can be confusing and should be tested across TLS built-in/module/disabled combinations. Because `FUN_CORE` is selected, core build issues surface when Ethernet is enabled.

## Test Signals
Kconfig matrix builds for `FUN_ETH=y/m/n`, with `TLS_DEVICE` enabled and disabled, should verify expected module composition and dependencies.
