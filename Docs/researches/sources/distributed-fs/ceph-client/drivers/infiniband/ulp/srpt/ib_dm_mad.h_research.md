# sources/distributed-fs/ceph-client/drivers/infiniband/ulp/srpt/ib_dm_mad.h

## Purpose

`ib_dm_mad.h` defines the InfiniBand Device Management MAD structures and constants used by the SRPT target to advertise SRP I/O controller information through management datagrams.

## Important APIs, Types, and Functions

The header defines device-management MAD status values, attribute IDs for `ClassPortInfo`, `IOUnitInfo`, `IOControllerProfile`, and `ServiceEntries`, and packed protocol-facing structures `ib_dm_hdr`, `ib_dm_mad`, `ib_dm_iou_info`, `ib_dm_ioc_profile`, `ib_dm_svc_entry`, and `ib_dm_svc_entries`.

## Control Flow

The header has no functions. `ib_srpt.c` receives a device-management MAD, creates a reply MAD, switches on `mad_hdr.attr_id`, and fills these structures with `srpt_get_class_port_info()`, `srpt_get_iou()`, `srpt_get_ioc()`, or `srpt_get_svc_entries()`.

## State and Persistence Behavior

The structures are transient wire-format payloads. They persist only inside received and transmitted MAD buffers. Their field layout must remain compatible with InfiniBand device-management definitions and SRP discovery expectations.

## Dependencies and Integration Points

It includes `<rdma/ib_mad.h>` for MAD header sizes and base structures. `ib_srpt.h` includes this file so the SRPT source can cast `ib_dm_mad.data` to the appropriate payload type. The 64-byte header invariant is checked in `ib_srpt.c` before creating send MADs with `IB_MGMT_DEVICE_HDR`.

## Risks and Edge Cases

The main risk is ABI/layout drift: MAD payloads are parsed by remote management clients, so field order, endian types, and header size are part of the protocol. ServiceEntries supports four entries structurally, while SRPT currently fills one. Status values must be returned in big-endian MAD status fields.

## Test Signals

MAD discovery tests should query each supported attribute, invalid attributes, invalid IOC slots, unsupported SET methods, service-entry ranges, and verify payload sizes, endian values, status codes, SRP service names, and advertised RDMA/send limits.
