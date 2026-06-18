# sources/distributed-fs/ceph-client/drivers/net/ethernet/oki-semi/Kconfig

## Purpose
Introduces the OKI Semiconductor Ethernet vendor menu.

## Important APIs, Types, And Functions
Defines `NET_VENDOR_OKI`, a bool defaulting to `y`, depending on `PCI`, and sources `drivers/net/ethernet/oki-semi/pch_gbe/Kconfig` when enabled.

## Control Flow
Kernel configuration uses this vendor selector to show or hide OKI-specific driver prompts. The concrete driver prompt comes from the sourced PCH GBE Kconfig.

## State And Persistence
Only generated kernel configuration state; no runtime state.

## Dependencies And Integration Points
Integrates with the Ethernet vendor menu and gates the PCI-based PCH GBE driver configuration.

## Risks And Edge Cases
The default `y` keeps prompts visible on PCI-capable configs. A broken `source` path would make the concrete driver unreachable.

## Test Signals
`menuconfig`/`oldconfig` should expose OKI devices when PCI is available and hide `PCH_GBE` when the vendor menu is disabled.
