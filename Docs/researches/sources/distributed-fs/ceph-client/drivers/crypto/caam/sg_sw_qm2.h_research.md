# sources/distributed-fs/ceph-client/drivers/crypto/caam/sg_sw_qm2.h

Purpose: provides the DPAA2 variant of CAAM scatterlist-to-hardware scatter/gather conversion using `struct dpaa2_sg_entry`.

Important APIs: `dma_to_qm_sg_one()` programs address, single-entry format, non-final flag, length, BPID zero, and offset through DPAA2 accessors. `sg_to_qm_sg()` converts a mapped Linux scatterlist into a sequence of DPAA2 SG entries, and `sg_to_qm_sg_last()` sets the final bit on the last produced entry.

Control flow and state: the loop is the same contract as the DPAA1 helper: consume the requested byte count from `sg_dma_len()` chunks and return the last populated entry. The header stores no state; hardware-visible state is only the caller-provided SG table.

Dependencies and integration points: depends on `<soc/fsl/dpaa2-fd.h>` and Linux scatterlist DMA fields. It is also included by `sg_sw_sec4.h`, where DPAA2 CAAM can alias SEC4 entries onto DPAA2 SG entries when `caam_dpaa2` is active.

Risks and test signals: risks are incorrect final-bit handling, caller-provided offset semantics differing between DPAA2 and SEC4, table overflow, and undefined behavior if the SG chain ends before `len`. Test signals include DPAA2 frame descriptors completing with multi-segment data, final flag set only on the last entry, and matching lengths on requests split across several SG segments.
