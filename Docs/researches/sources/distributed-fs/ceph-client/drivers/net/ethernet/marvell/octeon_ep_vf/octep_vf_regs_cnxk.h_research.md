# sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeon_ep_vf/octep_vf_regs_cnxk.h

Purpose: Defines CNXK VF register offsets and bit masks for the Octeon EP VF Ethernet driver. It is the CNXK counterpart to the CN93 header and supplies register address macros for input/output rings, queue watermarks, error type reporting, counters, and PF/VF mailbox communication.

Important APIs/types/functions: The file exports macros only. `CNXK_VF_RING_OFFSET` is the per-ring stride. `CNXK_VF_SDP_R_IN_*()` and `CNXK_VF_SDP_R_OUT_*()` produce MMIO offsets for ring control, enable, base, size, doorbell, count, interrupt level, packet counter, byte counter, output watermark, and `CNXK_VF_SDP_R_ERR_TYPE()`. Control masks define rings-per-VF fields, 64-byte instruction mode, read size, idle bits, swap/relax-order bits, and output interrupt mode. Mailbox macros define PF-to-VF data/interrupt and VF-to-PF data registers plus enable/status bits.

Control flow and integration: CNXK-specific VF setup code uses these macros behind `hw_ops` to initialize IQ/OQ registers, post credits and doorbells, poll hardware progress, and service mailbox interrupts. Compared with CN93, CNXK adds an error-type register and shifts the output enable address after the output watermark register, so callers must choose the correct chip header.

State and persistence: All represented state is volatile MMIO hardware state. Software queue structures cache pointers to these registers, but the authoritative state is in hardware until device reset or explicit writes.

Dependencies: Requires Linux bit macros and inclusion from the Octeon EP VF driver family. It depends on CNXK silicon/firmware register ABI compatibility.

Risks: Register layout differences from CN93 are subtle. Accidentally using CN93 offsets on CNXK, especially for output enable/watermark, can misconfigure receive rings. Error-type exposure is useful but only if consumers correctly read and decode it.

Test signals: Chip-specific probe must map correct offsets, queues must transition to enabled state, Rx credits and Tx doorbells must move traffic, mailbox interrupts must arrive, and CNXK error registers should remain clear under normal traffic.
