<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/pcie_vdec0_brdg_ctrl_axuser_msix_vcd_regs.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/pcie_vdec0_brdg_ctrl_axuser_msix_vcd_regs.h

## Purpose
`pcie_vdec0_brdg_ctrl_axuser_msix_vcd_regs.h` defines AXUSER registers for VCD-class MSI-X traffic from the PCIe VDEC0 bridge.

## Important APIs, types, and functions
It exports the same AXUSER macro families as the other bridge MSI-X blocks: HB ASID, MMU bypass, ordering, no-snoop, write reduction, read atomic, QoS, reserved/core/page fields, E2E coordinate, read/write overrides, and LB coordinate/lock/reserved/override. No code or types are present.

## Control flow
The header has no control flow. Runtime control is in initialization/error paths that program attributes before enabling VCD interrupt signaling and then rely on the hardware block to stamp outgoing MSI-X transactions.

## State and persistence
These registers are persistent per-traffic-class policy until reset or reconfiguration. They are normally static after bring-up.

## Dependencies and integration points
Included by `gaudi2_regs.h`, it integrates with bridge-control VCD interrupt masks/causes, MSI-X gateway logic in `pcie_wrap_regs.h`, and Gaudi2 security/MMU/fabric policy.

## Risks and test signals
Misconfigured VCD MSI-X attributes can cause event loss for only this interrupt class. Test signals include VCD event injection, correct vector delivery, no abnormal bridge interrupt escalation, and no AXI attribute/protection faults.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/pcie_vdec0_brdg_ctrl_axuser_msix_vcd_regs.h -->
