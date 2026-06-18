<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/pcie_vdec0_brdg_ctrl_regs.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/pcie_vdec0_brdg_ctrl_regs.h

## Purpose
`pcie_vdec0_brdg_ctrl_regs.h` maps the PCIe VDEC0 bridge-control register block. It provides addresses for clock gating, idle/graceful control, interrupts, MSI-X LBW write capture, gateway access, address/error capture, counters, and VCD interrupt masking.

## Important APIs, types, and functions
Exports include `mmPCIE_VDEC0_BRDG_CTRL_CGM_DISABLE`, `IDLE_MASK`, APB watchdog/count registers, `GRACEFUL`, interrupt cause/mask/clear registers, normal and abnormal MSI-X LBW address/data registers, gateway address/data/go/status registers, decoder status/error capture registers, free-run/busy counters with set-value low/high pairs, statistic counter enable, and `VCD_INTR_MASK`. No functions or types are declared.

## Control flow
There is no executable control flow. Init code configures clock/idle behavior and interrupt masks. Reset/quiesce code checks graceful/idle and busy counters. Interrupt paths read cause registers, inspect captured MSI-X or decoder address/data fields, clear events, and may use gateway registers for indirect bridge access.

## State and persistence
The bridge persists interrupt latches, masks, counter values, captured transaction/error addresses, and gateway transaction state until clear or reset. Counters may accumulate operational evidence across normal runtime until explicitly disabled or reset.

## Dependencies and integration points
Included by `gaudi2_regs.h`, this file pairs with `pcie_vdec0_brdg_ctrl_masks.h`, AXUSER traffic-class headers, `pcie_dec0_cmd_regs.h`, and `pcie_vdec0_ctrl_special_regs.h`. It integrates with PCIe error handling, MSI-X delivery, and VDEC/decoder reset sequencing.

## Risks and test signals
Wrong bridge-control addresses can hide interrupts, corrupt MSI-X writes, or fail reset quiesce checks. Test signals include bridge idle/graceful transitions, normal and abnormal interrupt injection, correct captured LBW address/data for MSI-X events, gateway access completion, and counters advancing only when expected.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/pcie_vdec0_brdg_ctrl_regs.h -->
