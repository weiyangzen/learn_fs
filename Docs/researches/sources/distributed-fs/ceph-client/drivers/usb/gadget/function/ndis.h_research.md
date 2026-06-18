# sources/distributed-fs/ceph-client/drivers/usb/gadget/function/ndis.h

## Purpose
This header provides small NDIS structure definitions used by the RNDIS gadget implementation for power-management and packet-pattern OIDs. It is a local adaptation of NDIS definitions needed to format or parse host-visible RNDIS data structures.

## Important APIs, types, and functions
`enum NDIS_DEVICE_POWER_STATE` defines D0 through D3 and sentinel power states. `struct NDIS_PM_WAKE_UP_CAPABILITIES` records minimum wake states for magic-packet, pattern, and link-change wake. `struct NDIS_PNP_CAPABILITIES` wraps flags and wake capabilities in little-endian form. `struct NDIS_PM_PACKET_PATTERN` describes a wake packet pattern with priority, mask size, offsets, size, and flags.

## Control flow
There is no executable control flow. The structures are included by `rndis.h` so RNDIS OID handling code can refer to NDIS PnP and wakeup payload layouts when those optional OID paths are enabled.

## State and persistence
No state is stored here. The structures describe wire-format or protocol-format data with explicit little-endian integer fields where appropriate.

## Dependencies and integration points
The header depends on Linux fixed-width endian typedefs such as `__le32`. It is an internal protocol companion for the USB gadget RNDIS code and not a general NDIS implementation.

## Risks and edge cases
The definitions must match host expectations exactly if optional power-management OIDs are enabled. Since RNDIS power-management behavior is historically underspecified, callers need conservative validation before trusting host-provided offsets and lengths.

## Test signals
Build coverage with RNDIS optional PM/wakeup configuration enabled is the main signal. Protocol tests should issue PnP and wakeup OIDs and confirm response sizes and endian layout.
