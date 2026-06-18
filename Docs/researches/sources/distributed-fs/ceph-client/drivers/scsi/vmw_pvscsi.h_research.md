# sources/distributed-fs/ceph-client/drivers/scsi/vmw_pvscsi.h

## Purpose

`vmw_pvscsi.h` defines the VMware PVSCSI adapter ABI used by `vmw_pvscsi.c`: PCI ID, register offsets, command opcodes, ring state, request/completion/message descriptors, SG element format, config page format, interrupt bits, and ring sizing limits. It is the contract between the guest driver and VMware virtual hardware.

## Important APIs, Types, And Functions

Key enums are `HostBusAdapterStatus`, `ScsiDeviceStatus`, `PVSCSIRegOffset`, `PVSCSICommands`, config page types/address types, and message types. Important command descriptors are `PVSCSICmdDescSetupRings`, `PVSCSICmdDescSetupMsgRing`, `PVSCSICmdDescAbortCmd`, `PVSCSICmdDescResetDevice`, `PVSCSICmdDescConfigCmd`, and `PVSCSICmdDescSetupReqCall`.

Ring ABI types are `PVSCSIRingsState`, `PVSCSIRingReqDesc`, `PVSCSISGElement`, `PVSCSIRingCmpDesc`, `PVSCSIRingMsgDesc`, and `PVSCSIMsgDescDevStatusChanged`. Configuration query output is represented by `PVSCSIConfigPageHeader` and `PVSCSIConfigPageController`.

## Control Flow And State

The header has no executable flow, but defines producer/consumer indexes for request, completion, and message rings. Requests carry a non-zero 64-bit context, data address/length, sense address/length, flags, CDB, LUN, tag, bus/target, and vCPU hint. Completions return the same context, transfer length, sense length, host status, and SCSI status. Message descriptors notify device add/remove events.

Setup commands pass page frame numbers for ring memory to the device. The rings state page also contains a request call threshold used for driver-side request coalescing when supported by the virtual adapter.

## Dependencies And Integration Points

The header includes Linux integer types and is consumed directly by the PVSCSI PCI driver. Its constants determine SCSI host limits such as maximum SG entries, maximum ring depth, supported interrupt bits, and MMIO mapping size.

## Risks And Test Signals

Because all descriptors are `__packed` ABI structures, field size, ordering, and alignment are critical. The `MASK(n)` macro uses `1 << n`, so callers must avoid widths that overflow an `int`; current ring log2 values are small. The request context restrictions documented in comments matter because the driver maps contexts to 1-based indexes.

Test signals include successful setup-ring command negotiation, correct max queue depth from page counts, completion context round trips, hotplug message decoding, config page query status, and interrupt masking/unmasking behavior for completion and message bits.
