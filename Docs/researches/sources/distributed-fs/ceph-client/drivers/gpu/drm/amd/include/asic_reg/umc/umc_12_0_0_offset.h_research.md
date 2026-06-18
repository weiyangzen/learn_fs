# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/umc/umc_12_0_0_offset.h

## Purpose
This generated AMDGPU register-offset header names the UMC 12.0.0 registers used by RAS code for on-die ECC counter control, ECC error counters, and MCA status/address reporting. It gives symbolic offsets and base-index selectors for the first UMC channel register view.

## Important APIs, Types, and Functions
The public interface is four offset macros plus matching `_BASE_IDX` macros: `regUMCCH0_OdEccCntSel`, `regUMCCH0_OdEccErrCnt`, `regMCA_UMC_UMC0_MCUMC_STATUST0`, and `regMCA_UMC_UMC0_MCUMC_ADDRT0`. There are no functions or types. Consumers pass these names to `SOC15_REG_OFFSET(UMC, 0, ...)`, then add a per-node, per-UMC, and per-channel offset before using PCIe extended 32-bit or 64-bit register accessors.

## Control Flow
The file has no internal control flow. In `amdgpu/umc_v12_0.c`, reset and initialization paths calculate `SOC15_REG_OFFSET` from these macros, then clear or initialize `OdEccErrCnt` and program `OdEccCntSel`. RAS query paths read `MCUMC_STATUST0` to classify correctable, uncorrectable, and deferred errors, then read `MCUMC_ADDRT0` when an address-bearing error must be translated into a system physical address.

## State and Persistence Behavior
This header stores no state. The registers it names are persistent GPU hardware state. `regUMCCH0_OdEccErrCnt` holds a correctable-error counter that driver code clears or initializes. `regMCA_UMC_UMC0_MCUMC_STATUST0` and `regMCA_UMC_UMC0_MCUMC_ADDRT0` hold machine-check status and address information until read and cleared by the RAS flow.

## Dependencies and Integration Points
It is included by `amdgpu/umc_v12_0.c` together with `umc_12_0_0_sh_mask.h`. It depends on SOC15 register offset infrastructure, UMC instance/channel topology in `adev->umc`, extended PCIe register accessors such as `RREG64_PCIE_EXT` and `WREG32_PCIE_EXT`, and AMDGPU RAS data structures.

## Risks
Incorrect offsets or base indices would send RAS code to the wrong hardware register, causing missed ECC events, clearing the wrong counter, or reading a bogus MCA address. Because UMC v12.0 has multi-node and cross-node address arithmetic in the caller, these base offsets must remain channel-local and compatible with `get_umc_v12_0_reg_offset()`.

## Test Signals
Build-test `amdgpu/umc_v12_0.c`. Runtime validation should check ECC counter initialization, MCA status reads, address collection, and status clearing on UMC 12.0 ASICs. Register dumps should show access to offsets `0x032c`, `0x032d`, `0x03c2`, and `0x03c4` plus the caller-computed UMC channel offset.
