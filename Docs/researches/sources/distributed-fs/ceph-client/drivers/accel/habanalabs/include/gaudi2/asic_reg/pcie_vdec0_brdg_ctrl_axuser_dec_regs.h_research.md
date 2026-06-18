<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/pcie_vdec0_brdg_ctrl_axuser_dec_regs.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/pcie_vdec0_brdg_ctrl_axuser_dec_regs.h

## Purpose
`pcie_vdec0_brdg_ctrl_axuser_dec_regs.h` defines the AXUSER override/control registers for the PCIe VDEC0 bridge decoder traffic class.

## Important APIs, types, and functions
The file exports macros for high-bandwidth AXUSER attributes: `HB_ASID`, `HB_MMU_BP`, `HB_STRONG_ORDER`, `HB_NO_SNOOP`, `HB_WR_REDUCTION`, `HB_RD_ATOMIC`, `HB_QOS`, `HB_RSVD`, `HB_EMEM_CPAGE`, `HB_CORE`, `E2E_COORD`, read/write override low/high registers, and low-bandwidth attributes `LB_COORD`, `LB_LOCK`, `LB_RSVD`, and `LB_OVRD`. No functions or types are defined.

## Control flow
There is no executable flow. Security and bridge setup code programs these registers before PCIe decoder traffic is allowed to issue, selecting ASID, MMU bypass, ordering, snoop, QoS, and override behavior for decoder-originated AXI transactions.

## State and persistence
The hardware persists AXUSER policy for decoder traffic until reset or reprogramming. These fields influence every matching transaction rather than one command.

## Dependencies and integration points
Included by `gaudi2_regs.h`, this file works with `pcie_vdec0_brdg_ctrl_regs.h`, bridge masks, PCIe decoder command registers, MMU/security setup, and AXI fabric protection rules.

## Risks and test signals
Wrong AXUSER policy can bypass MMU/security unexpectedly, break ordering, or reduce performance through bad QoS/snoop settings. Tests should validate decoder transactions under secure and non-secure modes, MMU bypass policy, no-snoop behavior, and absence of AXI protection faults.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/pcie_vdec0_brdg_ctrl_axuser_dec_regs.h -->
