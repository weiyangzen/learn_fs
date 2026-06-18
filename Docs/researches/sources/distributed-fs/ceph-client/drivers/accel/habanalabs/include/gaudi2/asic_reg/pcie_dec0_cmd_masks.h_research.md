<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/pcie_dec0_cmd_masks.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/pcie_dec0_cmd_masks.h

## Purpose
`pcie_dec0_cmd_masks.h` defines generated bit shifts and masks for the PCIe decoder command software registers. These masks describe fields inside `pcie_dec0_cmd_regs.h` `SWREG*` registers.

## Important APIs, types, and functions
The file exports `PCIE_DEC0_CMD_*_SHIFT` and `*_MASK` macros. Field groups cover software hardware version/build metadata, external normal/abnormal interrupt sources, reset or ready indications, AXI read/write channel status signals (`AR*`, `AW*`, `R*`, `B*`, `W*`), decoder idle/busy or protocol state, and interrupt/status fields encoded in the SWREG register bank.

## Control flow
There is no executable flow. Driver or diagnostic code reads `mmPCIE_DEC0_CMD_SWREG*` registers and applies these masks to extract individual status bits. Initialization may write fields by composing shifted values with these masks.

## State and persistence
The masks have no state. The underlying SWREG fields represent decoder status, version, interrupt causes, and AXI handshake state that persists in hardware until cleared, updated, or reset.

## Dependencies and integration points
This header is included by `gaudi2_regs.h` and pairs directly with `pcie_dec0_cmd_regs.h`. It also matches similar decoder command masks for dcore VDEC blocks, allowing shared decode/interrupt handling across PCIe and dcore decoders.

## Risks and test signals
Mask drift is subtle: code may read the right register but interpret the wrong bit. Test signals include version fields decoding to expected values, normal and abnormal interrupt bits matching hardware events, AXI status bits agreeing with bridge/controller traces, and interrupt clear/mask flows affecting only intended fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/pcie_dec0_cmd_masks.h -->
