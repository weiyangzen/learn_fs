# sources/distributed-fs/ceph-client/drivers/scsi/hptiop.h

## Purpose

`hptiop.h` is the private protocol and state header for the HighPoint RocketRAID IOP driver. It defines the memory-mapped register blocks, queue constants, firmware message and request formats, S/G descriptors, per-request and per-command private state, adapter-family enum, per-HBA state, ioctl context, adapter-ops vtable, and debug/result macros used by `hptiop.c`.

## Important APIs, Types, and Functions

- Register layouts include `struct hpt_iopmu_itl` for Intel-style mailboxes/queues, `struct hpt_iopmu_mv` and `struct hpt_iopmv_regs` for Marvell queues/doorbells, and `struct hpt_iopmu_mvfrey` plus `mvfrey_inlist_entry`/`mvfrey_outlist_entry` for MVFREY list-based communication.
- Queue and interrupt constants define empty queue values, host-address marker bits, request-size/result bits, message/postqueue interrupt bits, MV queue length, MVFREY pointer toggles, and doorbell message bits.
- `enum hpt_iopmu_message` lists host-to-IOP control messages such as NOP, reset, flush, shutdown, stop/start background task, and reset communication, plus outbound device registration/unregistration/revalidation ranges.
- `struct hpt_iop_request_header` is the common firmware request header carrying size, type, flags, result, and 64-bit host context split into two fields.
- `enum hpt_iop_request_type` and `enum hpt_iop_result_type` describe GET_CONFIG, SET_CONFIG, block, SCSI, ioctl requests, and their completion status values.
- Request payloads include `hpt_iop_request_get_config`, `hpt_iop_request_set_config`, `hpt_iop_request_block_command`, `hpt_iop_request_scsi_command`, and `hpt_iop_request_ioctl_command`.
- `struct hptiop_request` tracks a host request slot, virtual request buffer, shifted DMA address, active `scsi_cmnd`, and index.
- `struct hpt_cmd_priv` is the SCSI command-private extension used through `HPT_SCP(scp)` to remember DMA mapping and S/G count.
- `struct hptiop_hba` stores family-specific register and internal-memory pointers in a union, Linux host and PCI pointers, firmware limits, flags, free-list and request arrays, DMA allocations, atomics, and wait queues.
- `struct hptiop_adapter_ops` is the family vtable consumed by the C file for BAR mapping, interrupt control, config I/O, request/message posting, reset communication, and DMA addressing policy.

## Control Flow and State

The header itself has no executable flow, but it encodes the state machines used by the driver. Firmware requests start as a common header with `IOP_RESULT_PENDING`, get posted through a family queue with an encoded host context, and return through outbound queues/doorbells with the same context. Messages use the `IOPMU_INBOUND_MSG0_*` namespace and complete by setting `msg_done` in the HBA. The HBA state persists from PCI probe to remove and holds all per-adapter queue, request, DMA, and reset state needed by `hptiop.c`.

## Dependencies and Integration Points

This header assumes Linux endian types, DMA address types, SCSI command structures, atomic and waitqueue types, and MMIO annotations are available from the including C file. It is tightly coupled to `hptiop.c` and to HighPoint firmware ABIs for RocketRAID 3xxx/4xxx controllers. It also bridges the SCSI mid-layer through `struct scsi_cmnd`, `Scsi_Host`, and per-command private storage.

## Risks

- Register structs are hardware ABI overlays; packing, reserved array sizes, and field offsets must remain exact.
- The request header's `context`/`context_hi32` fields are reused differently by adapter families, so shared code must not assume one encoding.
- `HPTIOP_MAX_REQUESTS` caps the static request array at 256 even if firmware advertises more; probe correctly clamps but future changes must keep allocation and tag decoding aligned.
- Flexible-array request payloads require careful `struct_size()` calculations to avoid request-buffer overflow.
- `HPT_SCP()` depends on `driver_template.cmd_size` matching `sizeof(struct hpt_cmd_priv)`.

## Test Signals

- Compile coverage of `hptiop.c` validates register and request layout references.
- Probe-time config should confirm firmware values populate `hptiop_hba` fields and that max requests are clamped to `HPTIOP_MAX_REQUESTS`.
- Family-specific hardware tests should validate ITL, MV, and MVFREY message, postqueue, and completion paths.
- DMA/SCSI tests should verify `hpt_cmd_priv` mapping state, S/G descriptor eot markers, request-size calculations, and context tag round trips.
