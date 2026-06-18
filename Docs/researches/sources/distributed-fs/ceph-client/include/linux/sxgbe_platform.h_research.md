<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/sxgbe_platform.h -->
# sources/distributed-fs/ceph-client/include/linux/sxgbe_platform.h

## Purpose

`sxgbe_platform.h` declares platform data for Samsung SXGBE Ethernet MAC support. It lets board or firmware glue describe PHY, bus, checksum, DMA, queue, and clock-related capabilities to the SXGBE driver.

## Important APIs, types, and functions

The file defines `struct sxgbe_mdio_bus_data` for MDIO IRQ/mask/probe behavior, `struct sxgbe_dma_cfg` for programmable burst and fixed/mixed burst settings, and `struct sxgbe_plat_data` for common MAC platform configuration: bus ID, PHY address/interface, MDIO bus data, DMA config, checksum offload, enhanced descriptor selection, force threshold/store-forward flags, maximum MTU, multicast/unicast filter counts, queue counts, and clock pointers.

## Control flow

Platform setup fills the data structure before driver probe. The driver reads it to create the MDIO bus, bind the PHY, configure DMA burst behavior, enable descriptor/checksum features, size queues and filters, and manage clocks.

## State and persistence behavior

The structures are caller-owned static or probe-time configuration. Runtime persistence is in the SXGBE driver state and hardware registers programmed from these fields. Clock pointers must remain valid according to device-driver lifetime rules.

## Dependencies and integration points

It depends on PHY interface definitions, netdevice/MDIO concepts, and common clock framework types. It integrates with platform/OF board code and the SXGBE network driver.

## Risks and test signals

Risks include mismatched PHY interface/address, bad queue counts, invalid MTU, enabling unsupported offloads, and clock lifetime/enable sequencing issues. Tests should cover probe with platform data and DT-derived data, PHY link up/down, DMA under load, checksum offload validation, multiple queue configurations, MTU limits, and suspend/resume clock handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/sxgbe_platform.h -->
