# sources/distributed-fs/ceph-client/drivers/scsi/fnic/cq_desc.h

## Purpose

`cq_desc.h` defines the common 16-byte Cisco vNIC completion queue descriptor and an inline decoder used by FNIC/vNIC completion processing.

## Important APIs, types, and functions

`enum cq_desc_types` identifies WQ/RQ/FCP/copy completion variants. `struct cq_desc` contains little-endian `completed_index`, little-endian `q_number`, 11 bytes of type-specific payload, and `type_color`. Masks define type, color, queue number, and completed-index widths. `cq_desc_dec()` decodes these fields.

## Control flow

Callers pass a DMA-filled descriptor to `cq_desc_dec()`. The helper reads the color bit first, executes `rmb()`, then reads type, queue number, and completed index. This preserves the hardware contract that the color byte is written last.

## State and persistence behavior

The header stores no software state. Descriptors live in DMA rings owned by vNIC/FNIC queue code. The color bit represents producer/consumer generation.

## Dependencies and integration points

The header depends on endian helpers and memory barriers. It is included by FNIC/vNIC queue consumers that decode type-specific descriptor payloads after common fields.

## Risks and edge cases

The memory barrier is essential on weakly ordered systems. The `type_specfic` field is misspelled but part of local API. Field masks truncate queue and index values; wider hardware fields would require updates.

## Test signals

Build FNIC users, run sparse/endian checks, and test completion rings across wraparound with synthetic descriptors to validate color, type, queue, and index decoding.
