<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/pcie_vdec0_brdg_ctrl_masks.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/pcie_vdec0_brdg_ctrl_masks.h

## Purpose
`pcie_vdec0_brdg_ctrl_masks.h` defines shifts and masks for PCIe VDEC0 bridge-control registers. It is the bitfield companion to `pcie_vdec0_brdg_ctrl_regs.h`.

## Important APIs, types, and functions
The file exports `PCIE_VDEC0_BRDG_CTRL_*_SHIFT` and `*_MASK` macros. Field groups cover CGM disable/idle masks and counters, APB arbitration watchdogs, graceful idle/stop status, cause/mask/clear registers, decoder/MSI-X AWADDR/WDATA fields, error-capture fields for LBW/HBW addresses, AXI response/status, free-run and busy counters, statistic counter enable, VCD interrupt mask/cause fields, and normal/L2C/abnormal interrupt source fields.

## Control flow
No code executes in the header. Driver code reads/writes bridge-control registers and uses these masks to set one field without corrupting adjacent fields. Interrupt handlers decode cause registers, mask selected classes, clear latched events, and inspect error address/data fields.

## State and persistence
The masks are stateless. Underlying bridge-control state includes interrupt latches, clear/mask bits, idle counters, decoder/MSI-X LBW transaction payload capture, and statistics counters. This state persists until clear or reset.

## Dependencies and integration points
Included by `gaudi2_regs.h`, this file pairs with `pcie_vdec0_brdg_ctrl_regs.h` and the AXUSER per-traffic-class headers. It is also related to decoder command masks and PCIe wrapper interrupt delivery.

## Risks and test signals
Mask drift can lead to read-modify-write corruption, especially in interrupt clear/mask and watchdog fields. Tests should cover normal/abnormal/L2C/VCD interrupt decode, masking and clearing individual bits, bridge idle detection, MSI-X LBW payload capture, and counter enable/disable without disturbing unrelated fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/pcie_vdec0_brdg_ctrl_masks.h -->
