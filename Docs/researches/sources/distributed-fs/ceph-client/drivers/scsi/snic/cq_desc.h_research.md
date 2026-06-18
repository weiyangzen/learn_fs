# sources/distributed-fs/ceph-client/drivers/scsi/snic/cq_desc.h

Purpose: this header defines the common 16-byte vNIC completion queue descriptor layout and decoding helper.

Important APIs, types, and functions: `enum cq_desc_types` assigns descriptor types for WQ/RQ/FCP/copy completions. `struct cq_desc` contains completed index, queue number, type-specific bytes, and a combined type/color byte. `cq_desc_dec()` extracts color, type, queue number, and completed index using masks.

Control flow: completion service loops call `cq_desc_dec()` before consuming an entry. The helper reads the color bit first, issues `rmb()`, then reads the rest of the descriptor. This matches the hardware contract that color is written last and prevents stale descriptor fields.

State and persistence: no state is stored here. State is in hardware-owned CQ rings and consumer fields such as `vnic_cq.to_clean` and `last_color`.

Dependencies and integration: included by Ethernet CQ descriptors and `vnic_cq.h`. It depends on little-endian conversion helpers and memory barriers from kernel headers included by users.

Risks: descriptor bit masks are protocol-critical. If hardware changes field widths or write ordering, all CQ consumers can mis-handle completions. The helper assumes descriptor memory is DMA coherent and color toggling is valid.

Test signals: exercise CQ wraparound, color toggles, and mixed descriptor types. Hardware or emulator tests should confirm completed indexes and queue numbers match WQ service expectations under interrupt load.
