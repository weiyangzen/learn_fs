# sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeon_ep_vf/octep_vf_regs_cn9k.h

Purpose: Defines CN93/CN9K VF PCI config, input queue, output queue, and PF/VF mailbox register offsets for the Octeon EP VF Ethernet driver. It is a pure hardware contract header: no code, persistence, or allocation, but every macro feeds MMIO register setup in chip-specific VF setup code and queue paths.

Important APIs/types/functions: The exported surface is macro-only. `CN93_VF_RING_OFFSET` spaces per-ring register windows by bit 17. `CN93_VF_SDP_R_IN_*()` macros compute input-ring control, enable, descriptor base, ring size, doorbell, counters, interrupt levels, packet and byte counter addresses. `CN93_VF_SDP_R_OUT_*()` mirrors that for output rings. `CN93_VF_R_IN_CTL_*` and `CN93_VF_R_OUT_CTL_*` define control bits for idle, 64-byte instruction mode, read size, endian/swap behavior, interrupt mode, and error/status fields. Mailbox macros expose PF-to-VF data, PF-to-VF interrupt, VF-to-PF data, and interrupt enable/status bits.

Control flow and integration: Higher-level CN9K device code includes this header when populating `hw_ops` register callbacks. Setup code writes descriptor DMA bases and sizes, enables queues, rings doorbells, and polls counts through these offsets. Mailbox code uses the mailbox register triplet to exchange PF/VF control messages.

State and persistence: The header models volatile hardware state only. Counter, doorbell, enable, control, and mailbox fields persist in device registers until reset or rewritten; the driver must treat them as MMIO state rather than cached software state.

Dependencies: Requires kernel bit helpers such as `BIT_ULL` from included transitive headers. It depends on CN93/CN9K register layout remaining stable and aligned with firmware/hardware documentation.

Risks: An incorrect base, ring stride, or bit mask breaks DMA queue setup and can produce silent traffic loss or device wedging. This file lacks compile-time validation against a register specification, so cross-chip copy/paste drift is the main risk.

Test signals: Build coverage should verify macro visibility through CN9K code. Runtime signals are successful probe, queue enable, Tx/Rx traffic, mailbox exchange, interrupt delivery, and monotonically increasing packet/byte counters.
