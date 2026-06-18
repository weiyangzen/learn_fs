<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/pcie_dec0_cmd_regs.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/pcie_dec0_cmd_regs.h

## Purpose
`pcie_dec0_cmd_regs.h` defines the PCIe decoder command register bank as generated `SWREG` addresses. It is the address companion to `pcie_dec0_cmd_masks.h`.

## Important APIs, types, and functions
The file exports `mmPCIE_DEC0_CMD_SWREG0` through selected higher registers including `SWREG26` and `SWREG64`-`SWREG67`. There are no functions or types.

## Control flow
No code runs here. Driver diagnostics and interrupt handling read the SWREG bank, use `pcie_dec0_cmd_masks.h` to decode fields, and may write command/status fields when clearing or configuring decoder behavior.

## State and persistence
The hardware SWREG bank stores decoder-visible software/status state: version metadata, interrupt causes, AXI channel observations, and command/status words. State is reset by decoder or PCIe reset and otherwise persists until hardware updates or driver clears fields.

## Dependencies and integration points
Included by `gaudi2_regs.h`, this file integrates with PCIe VDEC bridge-control registers and special registers. `gaudi2_regs.h` also defines `BRDG_CTRL_BLOCK_OFFSET` and `SPECIAL_BLOCK_OFFSET` using decoder-command bases, making this block an anchor for nearby PCIe VDEC address calculations.

## Risks and test signals
Wrong SWREG addresses break decoder status and interrupt diagnosis while leaving the driver build clean. Test signals include expected hardware version/builddate decode, interrupt status matching bridge-control cause registers, and correct behavior when abnormal decoder conditions are injected.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/pcie_dec0_cmd_regs.h -->
