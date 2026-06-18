<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_edma1_qm_axuser_nonsecured_regs.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_edma1_qm_axuser_nonsecured_regs.h

## Purpose
`dcore0_edma1_qm_axuser_nonsecured_regs.h` is an auto-generated Gaudi2 register-address header for the `DCORE0_EDMA1_QM_AXUSER_NONSECURED` AXUSER register bank. It exposes 19 `mm...` address macros in the `0x41DAB80-0x41DABCC` region for programming AXI user attributes on high-bandwidth (HB) and low-bandwidth (LB) DMA or queue-manager traffic. This is the non-secure AXUSER bank for EDMA1 QMAN traffic.

## Important APIs, types, and functions
The file exports preprocessor constants only; there are no C types or functions. The important register groups are `HB_ASID`, `HB_MMU_BP`, `HB_STRONG_ORDER`, `HB_NO_SNOOP`, `HB_WR_REDUCTION`, `HB_RD_ATOMIC`, `HB_QOS`, `HB_RSVD`, `HB_EMEM_CPAGE`, `HB_CORE`, `E2E_COORD`, HB write/read override low/high pairs, and the LB `COORD`, `LOCK`, `RSVD`, and `OVRD` registers. These addresses pair with AXUSER mask headers that define write/read ASID fields, MMU-bypass bits, cache/snoop controls, reduction/atomic encodings, QOS, coordinate routing, and override payload masks.

## Control flow
The header has no runtime control flow. Its constants are consumed by Gaudi2 initialization, queue setup, DMA context programming, firmware bring-up, and debug/error paths that issue `WREG32`/`RREG32` accesses. Typical sequencing is to program ASID and MMU bypass attributes before enabling or committing DMA/QMAN work, then leave the values resident while the corresponding queue or DMA context issues AXI transactions.

## State and persistence behavior
State is purely hardware-resident. Values written through these macros persist in the AXUSER register bank until reset or reprogramming, and they affect subsequent bus transactions from the associated block. The split HB/LB and read/write override registers mean stale values can survive across contexts if reset/init code does not explicitly reinitialize the bank.

## Dependencies and integration points
This generated header integrates with `gaudi2/asic_reg/*_axuser_masks.h`, common HabanaLabs register accessors, and Gaudi2 queue/DMA initialization code. It has no include dependencies beyond its guard. Its address base must stay synchronized with generated block base maps and with any driver tables that select EDMA, KDMA, or QMAN AXUSER windows by engine id.

## Risks and edge cases
The main risk is programming the right field at the wrong engine's AXUSER base, which can silently change ASID, MMU bypass, snoop, QOS, or security attributes for unrelated traffic. Nonsecured QMAN banks are especially sensitive because their name encodes the security domain. Register layout drift between the address header and mask header can also produce correct-looking writes to semantically wrong fields.

## Test signals
Useful signals are successful Gaudi2 probe/reset with MMU enabled, DMA or QMAN traffic using expected ASIDs, no RAZWI/protection errors after AXUSER programming, and queue stress that exercises host, HBM, and LB paths. Negative signals include access faults, unexpected secure/nonsecure violations, bad QOS behavior, or device traffic observed with stale ASID/MMU-bypass attributes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_edma1_qm_axuser_nonsecured_regs.h -->
