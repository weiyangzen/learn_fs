<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/pcie_vdec0_ctrl_special_regs.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/pcie_vdec0_ctrl_special_regs.h

## Purpose
`pcie_vdec0_ctrl_special_regs.h` defines the PCIe VDEC0 bridge special/control register block for privilege/security, memory gateway, ECC, global error reporting, spare registers, and security registers.

## Important APIs, types, and functions
The file exports `mmPCIE_VDEC0_CTRL_SPECIAL_*` macros. Major groups are `GLBL_PRIV_0` through `GLBL_PRIV_31`, memory gateway data/request/number/ECC select/control/error mask/global error mask/status/address/RM, global error mask/address/cause, spare registers, and `GLBL_SEC_0` through `GLBL_SEC_31`. No functions or types are present.

## Control flow
No code executes. Security initialization programs privilege and security arrays; diagnostic or RAS paths use the memory gateway and ECC controls; error handlers read global error cause/address and clear or mask relevant bits according to generated masks in related special mask headers.

## State and persistence
Hardware state includes privilege/security policy, memory gateway transaction state, ECC injection/reporting state, and global error latches. These values are reset-sensitive and may be reprogrammed during security init or device reset.

## Dependencies and integration points
Included by `gaudi2_regs.h`, this block is adjacent to PCIe VDEC bridge control and decoder command blocks. It integrates with `gaudi2_security.c`, bridge RAS/error handling, and any firmware policy for protected register access.

## Risks and test signals
Privilege/security register mistakes can expose protected VDEC/PCIe controls or block legitimate driver access. ECC/global error misconfiguration can mask real faults. Test signals include expected security aperture behavior, successful access to allowed registers, blocked unauthorized access, ECC/error injection producing the right global cause/address, and clean reset reprogramming.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/pcie_vdec0_ctrl_special_regs.h -->
