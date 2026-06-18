# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_11_0_offset.h lines 1-2478

## Scope

This chunk covers the first 2,478 lines of the generated NBIO 7.11.0 register offset header. The complete file is larger; this slice starts at the license/header guard and covers early NBIO, RAS, IOMMU L2, USB4/PCIe direction, root-complex configuration, and the beginning of endpoint-function PCI configuration spaces through `regBIF_CFG_DEV0_EPF2_0_PCIE_ARI_CNTL`.

The file contains no executable C logic. Its functional role is to publish preprocessor constants that other AMDGPU code passes into SOC15 register access helpers. For almost every `reg...` offset macro, the chunk also defines a companion `..._BASE_IDX` macro, and in this slice those base indices are consistently `5`.

## Purpose

`nbio_7_11_0_offset.h` is the NBIO 7.11.0 address map for AMDGPU. It gives symbolic names to hardware register offsets so driver code can avoid hard-coded numeric addresses when programming the NBIO/PCIe/IOMMU portions of an ASIC. The companion `nbio_7_11_0_sh_mask.h` provides field shifts and masks for many of the same logical registers; driver code combines both headers with `RREG32_SOC15()`, `WREG32_SOC15()`, `SOC15_REG_OFFSET()`, `REG_SET_FIELD()`, and related AMDGPU register helpers.

Within this chunk, the register groups fall into several broad areas:

- Top-level NB configuration and scratch registers.
- NB miscellaneous registers for MMIO/DRAM windows, PSP/SMU/FASTREG/MISC aperture base addresses, trap registers, secondary-bus bridge registers, USB QoS, and MCA SMN interrupt routing.
- NB RAS and PSP RAS status/control offsets for parity, poison, sync flood, NMI, APML, and PSP poison reporting.
- Indirect SMN index/data windows for PCIe root-complex bridge configuration.
- IOMMU L2A performance, cache, credit, error-rule, page-size, and memory power-gating controls.
- USB4/PCIe direction registers used by the `nbio_v7_11` clock-gating path.
- Root-complex and endpoint-function PCI/PCIe configuration register offsets, including standard config-space registers and extended capabilities such as AER, ACS, ATS, PASID, SR-IOV, 16GT PHY, margining, and BAR/power-budget/DPA capability registers.

## Important Macros and Address Blocks

The chunk starts with an include guard `_nbio_7_11_0_OFFSET_HEADER` and the AMD MIT-style license. After that, it is organized by generated comments of the form `// addressBlock:` and `// base address:`.

Observed address blocks in this slice:

- `nbio_iohub_nb_nbcfg_nb_cfgdec`, base `0x0`: short config aliases for `cfgNBCFG_SCRATCH_0` through `cfgNBCFG_SCRATCH_4`.
- `nbio_iohub_iommu_l2_iommul2cfg`, base `0x0`: present as an empty address block in this chunk.
- `nbio_nbif0_bif_cfg_dev0_epf0_bifcfgdecp`, base `0x0`: defines `cfgPCIE_VENDOR_SPECIFIC_ENH_CAP_LIST_GPUIOV`.
- `nbio_iohub_nb_nbcfg_nb_cfgdec`, base `0x13b00000`: `regNB_NBCFG0_*` aliases for NB vendor/device IDs, command/status, class code, header, adapter ID, capabilities pointer, scratch registers, PCI arbitration, DRAM slot base, index/data mutexes, and writable ID aliases.
- `nbio_iohub_nb_fastreg_fastreg_cfgdec`, base `0x13b07000`: `regFASTREG_APERTURE`.
- `nbio_iohub_nb_misc_misc_cfgdec`, base `0x13b10000`: the largest non-PCI-config block in this chunk. It includes `regNB_CNTL`, revision and bus/MMIO/DRAM mapping registers, software interrupt controls, CAM target registers, VDM controls, stall controls for xbar ports, PSP/SMU/FASTREG/MISC aperture base address low/high pairs, scratch and SMU block/status registers, trap request/response registers, trap comparators `regTRAP0_*` through `regTRAP15_*`, secondary-bus bridge window/control registers, `regUSB_QoS_CNTL`, and `regMCA_SMN_INT_*` registers.
- `nbio_iohub_nb_rascfg_ras_cfgdec`, base `0x13b20000`: parity controls, severity controls, RAS scratch registers, sync flood/NMI/internal poison/egress poison status and masks, egress poison severity, and APML status/control/trigger.
- `nbio_iohub_nb_psprascfg_pspras_cfgdec`, base `0x13b23000`: PSP poison status offsets.
- `nbio_iohub_nb_intSBdevindcfg0_devind_cfgdecp`, base `0x13b3c000`: internal secondary-bus device-indirect steering and latency registers.
- `nbio_iohub_nb_PCIE0rcbdg_indcfg[0-2]_pciercbdgind_cfgdec`, bases `0x13b7d600`, `0x13b7d700`, and `0x13b7d800`: three pairs of `RC_SMN_INDEX` and `RC_SMN_DATA` offsets.
- `nbio_iohub_iommu_l2a_l2acfg`, base `0x15700000`: IOMMU L2A performance counters, status/control, DTC/ITC/PTC controls, credit controls, update-filter control, error-rule controls, page-size control, memory power-gating controls, and ECO control.
- `nbio_iohub_nb_ioapiccfg_ioapic_cfgdec`, base `0x14300000`: `regFEATURES_ENABLE`.
- `nbio_pcie0_pciedir`, base `0x11180000`: USB4/PCIe adapter-layer and controller offsets such as `regPCIE_USB4_TXAL_CNTL1`, `regPCIE_USB4_RXAL_CNTL1`, `regPCIE_USB4_AL_CNTL*`, `regPCIE_USB4_ERR_CNTL5`, `regPCIE_USB4_LC_CNTL1`, and `regBIF_BIF256_CI256_RC3X4_USB4_*`.
- `nbio_nbif0_bif_cfg_dev0_rc_bifcfgdecp`, base `0x10100000`: root-complex config-space aliases with `regBIF_CFG_DEV0_RC0_*`.
- `nbio_nbif0_bif_cfg_dev0_epf0_bifcfgdecp`, base `0x10140000`: endpoint function 0 config-space aliases with `regBIF_CFG_DEV0_EPF0_0_*`.
- `nbio_nbif0_bif_cfg_dev0_epf1_bifcfgdecp`, base `0x10141000`: endpoint function 1 aliases with `regBIF_CFG_DEV0_EPF1_0_*`.
- `nbio_nbif0_bif_cfg_dev0_epf2_bifcfgdecp`, base `0x10142000`: endpoint function 2 aliases, ending in this chunk at `regBIF_CFG_DEV0_EPF2_0_PCIE_ARI_CNTL`.

The chunk contains 2,378 `#define` lines in total: 1,193 offset/config aliases and 1,185 `_BASE_IDX` aliases. The heavy macro concentration is under `regBIF_*`, which accounts for most PCIe root-complex and endpoint-function configuration definitions.

## API and Type Surface

This header does not define C functions, structs, enums, or runtime data. Its API is the macro namespace.

The key macro forms are:

- `cfg...`: raw config-space offsets that are not paired with `_BASE_IDX` in the same way as SOC15 `reg...` entries. Examples in this chunk include `cfgNBCFG_SCRATCH_0` through `cfgNBCFG_SCRATCH_4` and `cfgPCIE_VENDOR_SPECIFIC_ENH_CAP_LIST_GPUIOV`.
- `reg...`: register offsets consumed by AMDGPU register helpers. Examples include `regNB_CNTL`, `regTRAP_REQUEST0`, `regPARITY_CONTROL_0`, `regL2_CONTROL_0`, `regBIF_BIF256_CI256_RC3X4_USB4_CPM_CONTROL`, `regBIF_CFG_DEV0_RC0_DEVICE_CNTL`, and `regBIF_CFG_DEV0_EPF0_0_PCIE_SRIOV_CONTROL`.
- `reg..._BASE_IDX`: base-index metadata used by SOC15 register macros. In this chunk, every observed `_BASE_IDX` value is `5`.

The standard PCI/PCIe configuration aliases map multiple logical fields to the same dword offset when the hardware register contains multiple fields. Examples include vendor/device ID sharing offset `0x0000` or `0x10000`, command/status sharing `0x0001` or `0x10001`, capability/control/status pairs sharing one dword, MSI message data variants sharing offsets, and PCIe lane equalization or DPA substate allocation registers packing multiple lanes/substates into the same dword. This sharing is intentional and requires the shift/mask companion header for field-level access.

## Control Flow

There is no branch, loop, call, or interrupt flow in this file. Runtime control flow appears in consumers that include this header.

The main direct consumer for this ASIC version is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/nbio_v7_11.c`, which includes both `nbio/nbio_7_11_0_offset.h` and `nbio/nbio_7_11_0_sh_mask.h`. That C file uses the generated offsets to:

- Read and write NBIO registers with `RREG32_SOC15(NBIO, 0, reg...)` and `WREG32_SOC15(NBIO, 0, reg..., value)`.
- Convert generated register names into MMIO offsets with `SOC15_REG_OFFSET(NBIO, 0, reg...)`.
- Program USB4/PCIe clock-gating and light-sleep behavior using `regBIF_BIF256_CI256_RC3X4_USB4_CPM_CONTROL`, `regBIF_BIF256_CI256_RC3X4_USB4_PCIE_CNTL2`, `regBIF_BIF256_CI256_RC3X4_USB4_PCIE_TX_POWER_CTRL_1`, and `regBIF_BIF256_CI256_RC3X4_USB4_PCIE_MST_CTRL_3`, all of which appear in this chunk.

Most offsets used by `nbio_v7_11.c` are in later chunks of the same header, but the USB4/PCIe direction constants used by `nbio_v7_11_init_registers()`, `nbio_v7_11_update_medium_grain_clock_gating()`, `nbio_v7_11_update_medium_grain_light_sleep()`, and `nbio_v7_11_get_clockgating_state()` are present in this chunk.

## State and Persistence Behavior

This header itself stores no runtime state and has no persistence behavior. Its constants are compiled into the kernel driver and become part of the static hardware programming interface for NBIO 7.11.0.

The hardware registers named here do represent persistent device state while the GPU is powered:

- Scratch and RAS scratch registers may retain firmware/driver diagnostic values during a boot session.
- PCI/PCIe config registers hold device identity, command/status bits, BARs, capability lists, MSI/MSI-X state, AER status/masks/severity, SR-IOV configuration, PASID/ATS/ACS state, and link training/equalization state.
- NB misc aperture registers hold base addresses for PSP, SMU, FASTREG, and MISC windows.
- RAS poison, parity, sync flood, and APML status registers expose error state that may be sticky until explicitly cleared by hardware-specific flows.
- IOMMU L2 counters and controls represent performance, cache, credit, page-size, power-gating, and error-rule state.

Because the generated offsets are compile-time constants, changing them changes where the runtime driver reads and writes hardware state. An incorrect offset can silently target the wrong register and cause persistent malfunction until reset or power cycle.

## Dependencies and Integration Points

Primary dependencies and integration points:

- `nbio_7_11_0_sh_mask.h`: provides field masks and shifts for the same register families. The offset header names dwords; the shift/mask header names fields within those dwords.
- `amdgpu/soc15.h`: defines helper macro patterns such as `SOC15_REG_ENTRY`, `SOC15_REG_GOLDEN_VALUE`, and related constructs that depend on `reg##_BASE_IDX` and `reg` macro pairs.
- AMDGPU register access helpers such as `RREG32_SOC15`, `WREG32_SOC15`, `SOC15_REG_OFFSET`, `RREG32_PCIE_PORT`, and `WREG32_PCIE_PORT`: these use the generated offsets to resolve MMIO or indirect register accesses.
- `amdgpu/nbio_v7_11.c`: the ASIC-specific NBIO function table implementation. It directly includes this header and uses the USB4/PCIe direction registers from this chunk for clock-gating, light-sleep, and initialization programming.
- PCIe/AER/SR-IOV/IOMMU/KFD integration: although this chunk is only definitions, the named capabilities correspond to Linux-visible functionality such as PCIe link control, MSI/MSI-X, AER logging, SR-IOV virtual functions, PASID/ATS/ACS for IOMMU and process address spaces, and GPU doorbell/MMIO behavior in adjacent NBIO code.

The values are ASIC-version-specific. Similar generated headers exist for other NBIO versions (`nbio_7_0_*`, `nbio_7_2_0_*`, `nbio_7_7_0_*`, `nbio_7_9_0_*`, etc.), so consumers must include the matching header for the IP version being compiled.

## Risks and Edge Cases

- Offset drift from the hardware specification is the largest risk. These values are authoritative for low-level register access; a single wrong address or base index can corrupt unrelated state.
- Packed dword aliases can be misused if code writes a full register while intending to alter only one field. Many aliases share the same numeric offset, so consumers should use masks and read-modify-write helpers where appropriate.
- `_BASE_IDX` consistency matters. This chunk uses base index `5` throughout the SOC15-style register definitions. A mismatched base index would make otherwise correct offsets resolve through the wrong IP base.
- Some address blocks are intentionally empty or very small. The empty `nbio_iohub_iommu_l2_iommul2cfg` block and short config aliases should not be interpreted as missing driver logic by themselves; generated headers often preserve address-block structure even when no registers are emitted for a block.
- This chunk cuts off in the middle of the endpoint-function 2 block. Any per-file conclusions about the complete NBIO 7.11.0 address map must wait for later chunks.
- RAS and poison status offsets are sensitive because debug, health reporting, and recovery code may depend on exact bit locations from the matching shift/mask header.
- PCIe capability-list offsets encode standardized layout plus AMD-specific vendor capabilities. Misnaming or moving these can break capability discovery, SR-IOV setup, AER handling, or virtualization-related paths.

## Test Signals

Useful validation signals for this chunk are mostly build-time and hardware-probe oriented:

- Compile AMDGPU with `nbio_v7_11.c` included; missing or renamed macros from this header should fail compilation immediately.
- Verify that `nbio_v7_11.c` clock-gating paths can compile and use the chunk-local USB4/PCIe constants: `regBIF_BIF256_CI256_RC3X4_USB4_CPM_CONTROL`, `regBIF_BIF256_CI256_RC3X4_USB4_PCIE_CNTL2`, `regBIF_BIF256_CI256_RC3X4_USB4_PCIE_TX_POWER_CTRL_1`, and `regBIF_BIF256_CI256_RC3X4_USB4_PCIE_MST_CTRL_3`.
- On matching NBIO 7.11.x hardware, boot logs should show normal AMDGPU PCIe/NBIO initialization without register access faults, AER storms, failed BAR setup, or SR-IOV capability inconsistencies.
- Runtime power-management testing should exercise BIF medium-grain clock gating and light-sleep enable/disable paths and confirm expected flags from `nbio_v7_11_get_clockgating_state()`.
- PCIe capability visibility can be checked indirectly through normal Linux PCI enumeration, MSI/MSI-X availability, AER reporting, SR-IOV capability exposure where supported, and link status consistency.
- RAS diagnostics should be checked for sane parity/poison/APML/sync-flood status reporting on hardware and firmware combinations that expose those features.

## Chunk Summary

Lines 1-2478 provide the initial generated register-offset namespace for NBIO 7.11.0. The slice is definition-only, but it is critical infrastructure for the AMDGPU NBIO driver because it binds symbolic NBIO, PCIe, RAS, IOMMU L2, and USB4/PCIe register names to ASIC-specific offsets and SOC15 base indices. The most directly visible integration from this chunk is the `nbio_v7_11.c` USB4/PCIe clock-gating and light-sleep code; the broader register families support PCIe config-space access, RAS/error reporting, IOMMU L2 control, and low-level NB/MMIO aperture programming.
