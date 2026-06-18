<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/pcie_wrap_special_regs.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/pcie_wrap_special_regs.h

## Purpose
`pcie_wrap_special_regs.h` maps the PCIe wrapper special register block for privilege/security, memory gateway/ECC, global error capture, spare values, and security policy registers.

## Important APIs, types, and functions
Exports include `mmPCIE_WRAP_SPECIAL_GLBL_PRIV_0` through `GLBL_PRIV_31`, memory gateway data/request/number/ECC select/control/error mask/global error mask/status/address/RM registers, `GLBL_ERR_MASK`, `GLBL_ERR_ADDR`, `GLBL_ERR_CAUSE`, spare registers, and `GLBL_SEC_0` through `GLBL_SEC_31`. There are no functions or types.

## Control flow
No C flow exists. Security setup writes privilege/security arrays; diagnostic/RAS code accesses gateway and ECC registers; global error handlers read cause/address and apply masks. Reset code should reinitialize policy after wrapper reset.

## State and persistence
Hardware persists access-control policy, memory gateway state, ECC/error latches, spare values, and security bits until reset or reprogramming. This state controls access to the surrounding PCIe wrapper block.

## Dependencies and integration points
Included by `gaudi2_regs.h`, the header integrates with `pcie_wrap_regs.h`, Gaudi2 security initialization, RAS/global error reporting, and firmware access policy.

## Risks and test signals
Wrong special-register policy can either expose protected PCIe wrapper controls or block required driver/firmware access. Test signals include security tests against privileged and secure registers, global error capture on injected illegal access, ECC status behavior if supported, and successful reprogramming after FLR/device reset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/pcie_wrap_special_regs.h -->
