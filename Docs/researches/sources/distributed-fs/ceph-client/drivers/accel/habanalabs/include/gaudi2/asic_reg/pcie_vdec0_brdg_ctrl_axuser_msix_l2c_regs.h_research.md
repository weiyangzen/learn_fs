<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/pcie_vdec0_brdg_ctrl_axuser_msix_l2c_regs.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/pcie_vdec0_brdg_ctrl_axuser_msix_l2c_regs.h

## Purpose
`pcie_vdec0_brdg_ctrl_axuser_msix_l2c_regs.h` defines AXUSER policy registers for PCIe VDEC0 bridge MSI-X traffic associated with L2C events.

## Important APIs, types, and functions
The exported macros follow the AXUSER template: `HB_ASID`, `HB_MMU_BP`, ordering/snoop/reduction/atomic/QoS/reserved/core attributes, E2E coordinates, read/write override registers, and LB coordinate/lock/reserved/override registers. It defines no functions or data structures.

## Control flow
No executable flow exists. Initialization programs these registers before enabling bridge interrupts so L2C-related MSI-X writes use the desired ASID, security, MMU, ordering, and fabric metadata.

## State and persistence
AXUSER settings are persistent hardware policy for this interrupt class until reset or explicit reconfiguration. They affect interrupt write transactions rather than software-visible memory.

## Dependencies and integration points
Included through `gaudi2_regs.h`, this block works with bridge-control interrupt masks/causes and PCIe wrapper MSI-X delivery. It also depends on systemwide security/MMU assumptions encoded by Gaudi2 init.

## Risks and test signals
Incorrect policy can make L2C MSI-X interrupts fail only under cache/fabric events, which makes regressions hard to notice. Test signals include L2C event injection, correct MSI-X vector arrival, and no protection, MMU, or ordering violations in bridge/fabric logs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/pcie_vdec0_brdg_ctrl_axuser_msix_l2c_regs.h -->
