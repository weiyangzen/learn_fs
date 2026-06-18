<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/pcie_vdec0_brdg_ctrl_axuser_msix_abnrm_regs.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/pcie_vdec0_brdg_ctrl_axuser_msix_abnrm_regs.h

## Purpose
`pcie_vdec0_brdg_ctrl_axuser_msix_abnrm_regs.h` defines AXUSER controls for abnormal MSI-X traffic emitted by the PCIe VDEC0 bridge-control block.

## Important APIs, types, and functions
Exports mirror the common AXUSER schema: high-bandwidth ASID, MMU bypass, strong ordering, no-snoop, write reduction, read atomic, QoS, reserved, emem cpage, core, end-to-end coordinate, write/read override low/high, and low-bandwidth coordinate/lock/reserved/override registers. There are no functions or types.

## Control flow
The header has no control flow. Interrupt setup/security code programs this policy so abnormal MSI-X writes carry the expected AXI attributes when an error path signals the host.

## State and persistence
The programmed AXUSER registers persist as transaction policy until reset. Because this path is for abnormal interrupts, bugs may only appear during error injection or real fault handling.

## Dependencies and integration points
It is included by `gaudi2_regs.h` and integrates with PCIe VDEC bridge interrupt cause/mask registers, MSI-X gateway/wrapper registers, and host interrupt delivery.

## Risks and test signals
If abnormal MSI-X attributes are wrong, fatal/error interrupts may be dropped, blocked by protection, or written with incorrect ordering. Test signals include injected abnormal bridge events producing MSI-X, correct host vector routing, and no AXI security/protection error on the interrupt write.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/pcie_vdec0_brdg_ctrl_axuser_msix_abnrm_regs.h -->
