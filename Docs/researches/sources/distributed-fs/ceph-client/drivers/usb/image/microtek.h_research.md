# sources/distributed-fs/ceph-client/drivers/usb/image/microtek.h

## Purpose
`microtek.h` defines the private state structures and endpoint constants shared by the Microtek USB scanner driver. It is intentionally small and exists to separate the SCSI transfer context and USB descriptor state from the implementation file.

## Important APIs, Types, And Functions
`typedef void (*mts_scsi_cmnd_callback)(struct scsi_cmnd *)` records the SCSI completion callback type. `struct mts_transfer_context` tracks the active SCSI command, final callback, data pointer and length, selected USB pipe, current scatterlist element, returned SCSI status byte, and owning `mts_desc`. `struct mts_desc` stores endpoint numbers, `usb_device`, `usb_interface`, `Scsi_Host`, one active URB, and embedded transfer context.

Constants define expected endpoint numbers: `MTS_EP_OUT` 1, `MTS_EP_RESPONSE` 2, `MTS_EP_IMAGE` 3, and `MTS_EP_TOTAL` 3. `MTS_SCSI_ERR_MASK` preserves upper SCSI result bits while replacing status bits.

## Control Flow
The header has no executable control flow. Its structures are filled in `mts_usb_probe()`, updated by `mts_build_transfer_context()`, and consumed by URB completion callbacks. The endpoint constants are used as warnings/sanity checks after endpoint discovery.

## State And Persistence
State described here lives for the lifetime of a bound USB interface and is freed on disconnect. The embedded transfer context is mutable per command and relies on the host template limiting queue depth to one.

## Dependencies And Integration Points
The types assume Linux USB, SCSI command, SCSI host, URB, scatterlist, and integer types are already included by `microtek.c`. The header is private to this driver and is not a general subsystem API.

## Risks
The header documents a single-URB, single-context architecture. Raising queue depth or adding parallel transfers would require redesigning `struct mts_transfer_context`, status storage, and URB ownership. The `next`/`prev` fields in `struct mts_desc` are unused by the current implementation and could mislead future maintainers into assuming a descriptor list exists.

## Test Signals
Build coverage should catch structure/API drift against SCSI and USB core types. Runtime tests are indirect through `microtek.c`: endpoint discovery, SCSI command completion, scatter/gather, and disconnect cleanup validate that the state layout remains coherent.
