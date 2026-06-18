<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/cisco/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/cisco/Kconfig

## Purpose

This Kconfig file introduces the Cisco Ethernet vendor menu. `NET_VENDOR_CISCO` is a PCI-dependent boolean that controls whether Cisco NIC driver options are shown.

## Important APIs, Types, and Functions

The only symbol defined here is `NET_VENDOR_CISCO`, defaulting to `y` and depending on `PCI`. When enabled, it sources `drivers/net/ethernet/cisco/enic/Kconfig`.

## Control Flow

There is no runtime flow. During kernel configuration, this file gates access to ENIC configuration under the Cisco vendor section.

## State and Persistence Behavior

The selected Kconfig value persists only in the kernel build configuration. It does not create runtime state and does not directly build code except by exposing child options.

## Dependencies and Integration Points

It integrates with the networking driver Kconfig hierarchy and the ENIC child Kconfig. The PCI dependency matches the ENIC driver's PCI-only probe model.

## Risks and Edge Cases

Turning this symbol off hides ENIC even if `CONFIG_ENIC` would otherwise be desired. The help text correctly notes the symbol only controls visibility of vendor-specific questions.

## Test Signals

Configuration tests should confirm the Cisco menu appears when PCI is enabled, disappears when disabled, and sources the ENIC option correctly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/cisco/Kconfig -->
