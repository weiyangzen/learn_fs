# sources/distributed-fs/ceph-client/drivers/net/ethernet/pasemi/Kconfig

## Purpose
Defines the PA Semi Ethernet vendor menu and on-chip PA Semi 1/10Gbit MAC driver option.

## Important APIs, Types, And Functions
`NET_VENDOR_PASEMI` is a bool defaulting to `y`, depending on `PPC_PASEMI && PCI`. `PASEMI_MAC` is a tristate depending on the same platform/PCI requirements and selecting `PHYLIB`.

## Control Flow
On PA Semi PPC PCI configurations, enabling the vendor menu exposes the PWRficient on-chip MAC driver as built-in or module.

## State And Persistence
Kernel configuration state only.

## Dependencies And Integration Points
Integrates with the Ethernet vendor menu and PA Semi Makefile; selects phylib for PHY management.

## Risks And Edge Cases
Strict platform dependency hides the driver outside `PPC_PASEMI && PCI`; no generic compile-test path is provided here.

## Test Signals
On matching configs, menuconfig should show `PASEMI_MAC`, and enabling it should select `PHYLIB`.
