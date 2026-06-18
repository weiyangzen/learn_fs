# sources/distributed-fs/ceph-client/drivers/scsi/fnic/vnic_wq.h

## Purpose

`vnic_wq.h` defines vNIC work queue control registers, software buffer metadata, queue state, and inline helpers for descriptor posting and completion servicing.

## Important APIs, types, and data

- `struct vnic_wq_ctrl` maps WQ MMIO registers.
- `struct vnic_wq_buf` tracks one posted descriptor's OS buffer, DMA address, length, SOP flag, descriptor pointer, and index.
- `struct vnic_wq` stores queue identity, device, MMIO control, DMA ring, buffer blocks, producer/consumer pointers, and outstanding packet count.
- `vnic_wq_desc_avail()`/`vnic_wq_desc_used()` expose ownership counts.
- `vnic_wq_next_desc()` returns the next descriptor to fill.
- `vnic_wq_post()` records buffer metadata, advances producer state, and posts to hardware on end-of-packet.
- `vnic_wq_service()` cleans descriptors through a completed index.

## Control flow

Transmit paths fill one or more descriptors, call `vnic_wq_post()` for each, and set `eop` on the final descriptor to update hardware after a write barrier. Completion paths start at `to_clean`, call a buffer-service callback for each descriptor through the completed index, increment availability, and advance consumer state.

## State and persistence behavior

Descriptor ownership is tracked by `ring.desc_avail`, `to_use`, `to_clean`, and hardware posted/fetch indexes. Multi-descriptor packets retain the OS buffer pointer only on the EOP descriptor.

## Dependencies and integration points

It depends on PCI types, `vnic_dev.h`, and `vnic_cq.h`. It integrates with Ethernet/FCoE descriptor encoders, completion queues, and devcmd2 setup.

## Risks and edge cases

- The alias `vnic_wq_next_desc` maps to `fni_cwq_next_desc`, which looks inconsistent with the other `fnic_*` aliases and should be compile-verified.
- Posting decrements availability for every descriptor but only writes hardware on EOP; callers must set EOP correctly.
- Completion service loops until a completed index is found; a bad completion index can overrun logical work.

## Test signals

Tests should validate availability math, multi-descriptor packet posting, EOP hardware posting, completion cleanup through wraparound, and alias compilation with ENIC also enabled.
