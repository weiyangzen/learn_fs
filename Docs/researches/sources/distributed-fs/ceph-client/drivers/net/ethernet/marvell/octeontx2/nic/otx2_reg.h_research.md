# sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeontx2/nic/otx2_reg.h

`otx2_reg.h` defines register offsets and address construction macros for RVU PF/VF, mailbox, NPA LF, NIX LF, LMT LF, and CN20K discovery blocks used by the NIC driver.

PF macros cover PF-VF mailbox windows, VF BAR4 discovery, block discovery, VF FLR/ME/mailbox interrupt status and enables, PF-AF mailbox registers, PF interrupt enables, MSI-X vector/PBA registers, VF mailbox address, and LMT line address. VF macros cover VF-PF mailbox, VF interrupts, block discovery, MSI-X, PBA, and mailbox region offsets. CN20K mailbox constants describe AF/PF alias regions. NPA macros cover aura/pool operations, interrupts, stats, and queue interrupts. NIX macros cover global/error/RAS registers, SQ/CQ/RQ operations, TX/RX stats, debug registers, queue interrupts, and completion interrupt moderation. LMT macros cover LMT line and cancel registers.

Callers use these logical offsets through `otx2_read64` and `otx2_write64`; `otx2_get_regaddr` decodes block type bits using `RVU_FUNC_BLKADDR_SHIFT` and `RVU_FUNC_BLKADDR_MASK`, substitutes the actual block address, and returns an MMIO address under `reg_base`.

The file has no runtime state. It depends on `rvu_struct.h` for block constants and is included by common/PF code. Risks are wrong offsets, shifts, or VF bank selection causing mailbox failure, interrupt loss, or queue corruption. Test signals include AF readiness, mailbox interrupts, PF-VF mailbox operation, NPA aura/pool operations, NIX queue interrupts, CQ moderation programming, stats reads, and SR-IOV with more than 64 VFs.
