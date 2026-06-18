# sources/distributed-fs/ceph-client/drivers/scsi/fnic/cq_exch_desc.h

## Purpose

`cq_exch_desc.h` defines completion queue descriptors for Fibre Channel exchange-oriented work in the FNIC/vNIC SCSI datapath. It decodes work-queue exchange completions, FCP receive completions, and SGL completion/error descriptors. These descriptors bridge low-level CQ polling with higher-level FCP I/O, abort, and SGL error handling.

## Important APIs, Types, and Functions

- `struct cq_exch_wq_desc`: exchange work-queue completion containing completed index, queue number, exchange ID, template field, status, and type/color.
- `enum cq_exch_status_types`: completion status values for complete, abort, SGL EOF, and template error.
- `cq_exch_wq_desc_dec()`: decodes generic CQ fields and masks `exch_status`.
- `struct cq_fcp_rq_desc`: FCP receive descriptor carrying completed index, SOP/EOP, ingress port, exchange ID, template, byte count, VLAN, SOF/EOF, FC CRC, FCoE error, and FCS status.
- `cq_fcp_rq_desc_dec()`: extracts FCP receive state and packet/error metadata.
- `struct cq_sgl_desc`: SGL completion/error descriptor with exchange ID, queue number, active burst offset, total data bytes, template, SGL error, and type/color.
- `enum cq_sgl_err_types`: SGL failure codes for overflow, local address errors, response errors, zero/max counts, ordering, host CQ write errors, and no-error.
- `cq_sgl_desc_dec()`: decodes SGL CQ metadata and SGL-specific fields.

## Control Flow

All decode helpers first call `cq_desc_dec()` to obtain common CQ type, color, queue number, and completion index. `cq_exch_wq_desc_dec()` then returns the two-bit exchange status. `cq_fcp_rq_desc_dec()` interprets packed SOP/EOP/port bits from `completed_index_eop_sop_prt`, extracts template and byte-count masks, shifts packet/VLAN/error bits, and returns raw SOF/EOF and VLAN values. `cq_sgl_desc_dec()` treats `exchange_id` as the completed index for generic CQ decode, then returns transfer offsets, total byte count, template, and masked SGL error.

## State and Persistence Behavior

This header maintains no persistent state. It turns a hardware-owned descriptor snapshot into caller-owned scalar values. The operational state represented by the decoded fields belongs to firmware exchanges, FCP receive paths, and SGL engines elsewhere in the driver.

## Dependencies and Integration Points

The file depends on `cq_desc.h`. It is consumed by vNIC CQ completion handlers and FNIC SCSI/FCP code that must map hardware CQ entries into `fcpio` completions, receive-frame processing, abort handling, and SGL error accounting. The descriptor status values should be correlated with `fcpio_status` and FNIC SCSI error handling when diagnosing I/O failures.

## Risks and Edge Cases

- Unlike `cq_enet_desc.h`, these structures use plain integer types and the helpers do not perform explicit endian conversion. That is safe only if this hardware ABI is already CPU-endian for this path or the surrounding CQ copy layer normalizes it.
- `cq_sgl_desc_dec()` deliberately "cheats" by using `exchange_id` as the completed index. Any hardware layout change that breaks that equivalence would misroute SGL completions.
- Byte-count and VLAN-stripped fields share packed storage; mask/shift mistakes can convert packet errors into data length corruption.
- Error handling depends on distinguishing SGL EOF from abort/template errors and on mapping detailed `CQ_SGL_ERR_*` reasons to the right reset or retry policy.

## Test Signals

Validation should cover normal exchange completions, abort completions, template errors, FCP receive SOP/EOP combinations, VLAN-stripped receive frames, packet/FCoE/FCS/FC-CRC error injection, SGL overflow and address errors, SGL order errors, and CQ wrap/color behavior while multiple copy work queues are active.
