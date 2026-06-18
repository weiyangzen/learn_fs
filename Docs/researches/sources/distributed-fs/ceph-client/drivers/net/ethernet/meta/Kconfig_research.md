# sources/distributed-fs/ceph-client/drivers/net/ethernet/meta/Kconfig

## Purpose

`meta/Kconfig` introduces the Meta Platforms Ethernet vendor menu and the `FBNIC` driver configuration option for the Meta Host Network Interface.

## Important APIs, Types, And Functions

`config NET_VENDOR_META` is a boolean vendor gate, defaulting to `y`, that controls whether Meta device questions are shown. `config FBNIC` is a tristate driver option with architecture and feature dependencies: 64-bit or compile-test, not S390, `MAX_SKB_FRAGS < 22`, PCI MSI, and optional PTP clock support. It selects devlink, page pool, XPCS PCS, phylink, and PLDM firmware support.

## Control Flow

Kconfig evaluation first decides whether the Meta vendor submenu is active. If active, the user can build `FBNIC` built-in or as module. The selected dependencies influence which kernel subsystems are enabled and whether the Makefile descends into `meta/fbnic/`.

## State And Persistence

Kconfig state is persisted in the kernel build configuration, not at runtime. Selecting `FBNIC=m` produces an `fbnic` module; selecting `y` links it built-in.

## Dependencies And Integration Points

The option integrates with PCI/MSI, PTP, devlink, page-pool RX allocation, PCS_XPCS, phylink, and PLDM firmware infrastructure. The dependency on `MAX_SKB_FRAGS < 22` documents a driver/hardware limit relevant to skb fragment handling.

## Risks And Edge Cases

Changing dependencies can expose the driver on unsupported architectures or without required interrupt/firmware/link-management subsystems. The vendor gate does not disable already-selected objects directly; it hides questions, matching normal kernel vendor menu behavior.

## Test Signals

Build tests should cover `FBNIC=y`, `FBNIC=m`, and `COMPILE_TEST` configurations, dependency rejection on S390 or too-large `MAX_SKB_FRAGS`, and module naming as `fbnic`. No local executable tests were run for this research item.
