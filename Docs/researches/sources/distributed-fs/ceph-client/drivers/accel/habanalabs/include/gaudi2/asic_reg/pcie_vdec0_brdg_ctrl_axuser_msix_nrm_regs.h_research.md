<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/pcie_vdec0_brdg_ctrl_axuser_msix_nrm_regs.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/pcie_vdec0_brdg_ctrl_axuser_msix_nrm_regs.h

## Purpose
`pcie_vdec0_brdg_ctrl_axuser_msix_nrm_regs.h` maps AXUSER attributes for normal MSI-X traffic from PCIe VDEC0 bridge control.

## Important APIs, types, and functions
The file exports the standard bridge AXUSER register set for HB ASID/MMU bypass/ordering/no-snoop/write-reduction/read-atomic/QoS/reserved/emem/core/E2E/override controls plus LB coordinate/lock/reserved/override controls. There are no functions or types.

## Control flow
There is no C flow. During interrupt setup, driver or firmware code programs this block so normal MSI-X writes are accepted by the PCIe/fabric path and use the correct transaction metadata.

## State and persistence
The settings persist in hardware until reset and govern normal interrupt traffic. They are part of device bring-up state rather than per-interrupt state.

## Dependencies and integration points
Included by `gaudi2_regs.h`, this header ties bridge-control normal interrupt causes to PCIe wrapper/MSI-X gateway behavior and to the broader AXI security/MMU setup.

## Risks and test signals
The common risk is interrupt delivery failure due to wrong ASID/MMU bypass/security/no-snoop attributes. Test signals include normal bridge interrupt delivery, successful MSI-X masking/unmasking, no dropped vectors under load, and no AXI protection errors during interrupt writes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/pcie_vdec0_brdg_ctrl_axuser_msix_nrm_regs.h -->
