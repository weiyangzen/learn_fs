# sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeon_ep/octep_regs_cnxk_pf.h

## Purpose
This header maps CNXK PF hardware registers and bit definitions for the OCTEON endpoint PF driver. It is the CNXK counterpart to the CN9K register header, with CNXK-specific offsets, field widths, interrupt counts, output queue watermark register, and PCIe VSEC address calculation.

## Important APIs, Types, And Functions
- Register base macros: `CNXK_RST_*`, `CNXK_SDP_WIN_*`, `CNXK_SDP_EPF_RINFO`, ring IN/OUT register starts, mailbox register starts, EPF interrupt registers, ring mapping registers, and MAC/PF ring-control registers.
- Address calculators: `CNXK_SDP_R_IN_* (ring)`, `CNXK_SDP_R_OUT_* (ring)`, `CNXK_SDP_R_OUT_WMARK(ring)`, `CNXK_SDP_R_MBOX_*`, and EPF interrupt bit-array macros.
- Field helpers: `CNXK_SDP_EPF_RINFO_SRN/RPVF/NVFS`, `CNXK_SDP_MAC_PF_RING_CTL_NPFS/SRN/RPPF`, and ring control masks.
- PCIe config macro: `CNXK_PEMX_PFX_CSX_PFCFGX(pem, pf, offset)` constructs an indirect config-space address for CNXK.
- Constants: `CNXK_NUM_NON_IOQ_INTR`, firmware status values, CNXK VSEC control offset, BAR4 index data, and `CNXK_INT_ENA_BIT`.

## Control Flow
The header does not run control flow directly. CNXK PF setup code uses the macros during device setup, queue reset/setup, interrupt enable/disable, mailbox register binding, and register dumps. Generic PF code reaches those operations through `octep_hw_ops`.

## State And Persistence
No in-memory state is declared. The macros address hardware state for reset domains, queue configuration, OQ watermark/backpressure, counters, mailbox data, interrupt status/enables, SR-IOV mapping, and firmware status. Values written by users persist in device registers until hardware reset or subsequent writes.

## Dependencies And Integration Points
This header is consumed by CNXK PF implementation files and integrates with `octep_main.h` CSR helpers. It complements `octep_regs_cn9k_pf.h` and allows the generic PF driver to handle CN10KA/CNF10KA/CNF10KB/CN10KB devices through a different hardware operation vector.

## Risks And Edge Cases
- CNXK field widths differ from CN9K, especially SRN/NVFS extraction; copying CN9K assumptions into CNXK code can misconfigure rings or VFs.
- OQ register layout includes `CNXK_SDP_R_OUT_WMARK`; missing watermark setup can affect backpressure behavior.
- Like the CN9K header, `CNXK_SDP_IN_RING_TB_MAP()` references `CNXK_SDP_N_RING_TB_MAP_START`, which is not defined in this file and should be checked if used.
- DMA_VF and PP_VF interrupt address macros use addition with the bit-array offset instead of multiplication; confirm against spec.

## Test Signals
Validate CNXK PF probe, queue register programming, OQ watermark programming, MSI-X/non-IOQ interrupt count of 32, mailbox interrupt routing, SR-IOV VF ring mapping, firmware status reads, register dump sanity, and compile coverage for all macros used by CNXK PF code.
