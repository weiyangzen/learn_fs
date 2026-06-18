# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/iavf/iavf_type.h

## Purpose
Defines common IAVF hardware-facing types, descriptor formats, descriptor bit masks, hardware capability structures, bus/MAC metadata, debug masks, and Ethernet statistics. It is the main local hardware ABI header for the VF driver.

## Important APIs, Types, and Functions
Important definitions include `IAVF_MASK`, `IAVF_DESC_UNUSED`, queue/VSI constants, `enum iavf_debug_mask`, `enum iavf_vsi_type`, `enum iavf_queue_type`, `struct iavf_hw_capabilities`, `struct iavf_mac_info`, bus enums and `struct iavf_bus_info`, `struct iavf_hw`, `struct iavf_rx_desc`, `struct iavf_tx_desc`, `struct iavf_tx_context_desc`, and `struct iavf_eth_stats`. The header defines legacy and flexible Rx descriptor fields, Tx data descriptor command/type/offset/length fields, Tx context descriptor tunnel/TSO/VLAN fields, and status/error enums used by Rx parsing.

## Control Flow
The file is almost entirely declarative. Runtime behavior appears indirectly when callers use field masks with `FIELD_GET` or construct descriptor command words. `IAVF_DESC_UNUSED` computes ring free space from `next_to_clean`, `next_to_use`, and ring count.

## State and Persistence
The structures mirror persistent hardware and driver state: PCI identity, MMIO base, AdminQ data, MAC addresses, capabilities, descriptor memory formats, and statistics returned by the PF. Descriptor definitions govern the exact DMA writeback and transmit command layout shared with hardware.

## Dependencies and Integration Points
Includes `iavf_status.h`, OS dependency wrappers, register definitions, AdminQ declarations, and device IDs. It is included transitively by most IAVF files, including queue setup, Tx/Rx, AdminQ, virtchnl, and stats code. It also uses Linux endian and bitmask types through included headers.

## Risks
This is hardware ABI. Wrong masks, shifts, endian annotations, struct sizes, or descriptor alignment can corrupt packet IO or metadata parsing. Flexible descriptor timestamp fields must match PTP handling, and RSS/checksum/VLAN masks must match `iavf_txrx.c`. `IAVF_DESC_UNUSED` assumes a one-descriptor gap ring discipline.

## Test Signals
Build-time static assertions, traffic with legacy and flexible Rx descriptors, checksum/hash/VLAN metadata validation, TSO/tunnel Tx offloads, stats updates from virtchnl, reset/probe on supported PCI IDs, and comparing descriptor/register definitions against hardware documentation are the primary signals.
