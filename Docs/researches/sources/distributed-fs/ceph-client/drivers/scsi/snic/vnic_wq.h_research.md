## sources/distributed-fs/ceph-client/drivers/scsi/snic/vnic_wq.h

### Purpose
Defines the SNIC vNIC work queue MMIO register layout, software queue metadata, inline descriptor accounting/post/service helpers, and lifecycle function prototypes implemented in `vnic_wq.c`.

### Important APIs, Types, and Constants
- `struct vnic_wq_ctrl` maps hardware registers for ring base/size, posted/fetch indices, CQ index, enable/running bits, DCA value, error interrupt controls, and error status.
- `struct vnic_wq_buf` tracks one descriptor's associated OS buffer, DMA address, length, index, SOP flag, descriptor pointer, and linked-list next pointer.
- Buffer block macros define 32/64-entry block sizing and `VNIC_WQ_BUF_BLKS_MAX` for up to 4096 descriptors.
- `struct vnic_wq` stores queue index, owning `vnic_dev`, MMIO `ctrl`, descriptor ring, buffer-block array, `to_use`, `to_clean`, and outstanding packet count.
- Inline helpers include `svnic_wq_desc_avail()`, `svnic_wq_desc_used()`, `svnic_wq_next_desc()`, `svnic_wq_post()`, and `svnic_wq_service()`.

### Control Flow and State
`svnic_wq_post()` attaches DMA/user metadata to the current buffer, advances `to_use`, and for end-of-packet descriptors issues a write memory barrier before updating the hardware `posted_index`. `svnic_wq_service()` walks from `to_clean` through the completed index, invokes a caller callback for each buffer, increments descriptor availability, and advances the clean cursor. Queue state is split between MMIO indices and software cursors.

### Dependencies and Integration Points
The header includes `vnic_dev.h` and `vnic_cq.h` because queue service callbacks receive completion queue descriptors. SNIC request submission code builds descriptors using `wq_enet_desc.h`, posts through these helpers, and completion handlers clean through `svnic_wq_service()`.

### Risks and Test Signals
The file contains a duplicated `VNIC_WQ_BUF_BLKS_NEEDED` macro definition, currently identical but still a maintainability risk. The most important correctness point is the `wmb()` before publishing `posted_index`; removing or weakening it can let hardware read stale descriptors. Tests should stress descriptor wraparound, multi-descriptor requests with SOP/EOP, completion index handling, and memory-order-sensitive DMA posting.
