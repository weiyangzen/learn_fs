# sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeon_ep/octep_regs_cn9k_pf.h

## Purpose
This header maps CN9K/CN93 PF hardware registers and bit definitions used by the OCTEON endpoint PF chip-specific implementation. It provides address formulas for reset, PCIe config, ring, mailbox, interrupt, ring mapping, MAC/PF ring control, firmware status, and indirect PCIe configuration space access.

## Important APIs, Types, And Functions
- Register base macros: `CN93_RST_*`, `CN93_SDP_WIN_*`, `CN93_SDP_EPF_RINFO`, `CN93_SDP_R_IN_*`, `CN93_SDP_R_OUT_*`, `CN93_SDP_R_MBOX_*`, and `CN93_SDP_EPF_*_RINT*`.
- Address calculators: `CN93_SDP_R_IN_* (ring)`, `CN93_SDP_R_OUT_* (ring)`, mailbox per-ring macros, interrupt bit-array macros, and ring mapping macros.
- Field helpers: `CN93_SDP_EPF_RINFO_SRN/RPVF/NVFS`, `CN93_SDP_MAC_PF_RING_CTL_*`, `CN98_SDP_MAC_PF_RING_CTL_*`, and interrupt masks such as `CN93_INTR_R_OUT_INT`.
- PCIe config helper: `cn9k_pemx_pfx_csx_pfcfgx()` builds a PEM/PF config-space address using `FIELD_PREP()` and alignment handling; exposed as `CN9K_PEMX_PFX_CSX_PFCFGX`.
- Constants: `CN93_NUM_NON_IOQ_INTR`, firmware status values, VSEC control offset, BAR4 index data, and interrupt-enable bit.

## Control Flow
This header is declarative. Chip-specific PF setup code uses these macros to calculate CSR offsets, then generic access helpers from `octep_main.h` perform MMIO or indirect PCI window reads/writes. Ring setup uses the IN/OUT register macros; mailbox setup uses per-ring PF/VF register macros; interrupt setup and handlers use EPF interrupt status, W1S, W1C, and enable registers.

## State And Persistence
The file defines no in-memory state. Its constants address hardware state that persists until reset or reconfiguration: ring base/size/control, packet counters, interrupt masks/status bits, mailbox data and interrupt flags, SR-IOV ring mapping, and firmware-running status.

## Dependencies And Integration Points
It includes `linux/bitfield.h` and is intended for CN9K PF hardware implementation files such as `octep_cn9k_pf.c`. It integrates with `octep_hw_ops` population and with generic PF logic that needs hardware register programming but should not embed CN9K offsets.

## Risks And Edge Cases
- Address macros are hardware ABI. A wrong offset or field width can corrupt unrelated CSRs.
- Several bit-array interrupt macros for DMA_VF and PP_VF use `((index) + CN93_BIT_ARRAY_OFFSET)` rather than multiplication, which deserves scrutiny against the hardware manual.
- `CN93_SDP_IN_RING_TB_MAP()` references `CN93_SDP_N_RING_TB_MAP_START`, which appears inconsistent with the defined `CN93_SDP_IN_RING_TB_MAP_START`; users may fail to compile if that macro is exercised.
- CN93 and CN98 MAC/PF ring control fields differ, so chip ID checks must select the correct extractor.

## Test Signals
Build chip-specific PF code with all referenced macros enabled, compare register dumps to hardware documentation, validate queue bring-up on CN93/CN98/CNF95N, test mailbox interrupts and non-IOQ interrupt counts, verify SR-IOV ring mapping values, and confirm indirect PCIe VSEC access through the computed PEM/PF config address.
