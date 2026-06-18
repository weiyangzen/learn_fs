# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_7_0_sh_mask.h lines 46351-48822

## Scope And Purpose

This chunk is part of the generated AMD NBIO 7.7.0 register field header used by the amdgpu kernel driver. It contains C preprocessor constants for bit shifts and masks, not executable logic. The companion `nbio_7_7_0_offset.h` gives register addresses, while this file gives the field layout for safe read/modify/write operations through AMDGPU helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, `RREG32_PCIE_PORT`, and `WREG32_PCIE_PORT`.

The chunk starts in the middle of `DEV1_PF1_FLR_RST_CTRL`, continues through Dev1/Dev2 function reset and D-state fields, covers NBIF RAS and SION scheduling registers, then enters the PCI configuration-space field definitions for `BIF_CFG_DEV0_EPF0_0`. The last complete region in this slice reaches PCIe margining lane control/status definitions through lane 11, and the following lane 12+ definitions continue after this chunk.

## Register Groups Covered

The first block defines per-function reset and power-state masks for NBIO device/function instances:

- `BIF_DEV1_PF0_DSTATE_VALUE`, `BIF_DEV1_PF1_DSTATE_VALUE`, `BIF_DEV2_PF0_DSTATE_VALUE` through `BIF_DEV2_PF6_DSTATE_VALUE`, and `BIF_PORT0_DSTATE_VALUE` through `BIF_PORT2_DSTATE_VALUE`.
- `DEV1_PF0_D3HOTD0_RST_CTRL`, `DEV1_PF1_D3HOTD0_RST_CTRL`, and `DEV2_PF0_D3HOTD0_RST_CTRL` through `DEV2_PF6_D3HOTD0_RST_CTRL`.
- `DEV2_PF0_FLR_RST_CTRL` through `DEV2_PF6_FLR_RST_CTRL`, plus the tail of the richer `DEV1_PF1_FLR_RST_CTRL` definition.

The D-state registers expose target, acknowledge, and D3-to-D0 reset-needed fields. The FLR/D3 reset control registers expose configuration/private enable bits, sticky behavior, FLR exception handling, grace mode, grace timeout, and DMA/host dummy response status fields. `DEV1_PF1_FLR_RST_CTRL` also includes VF and soft-PF-specific controls such as `VF_CFG_EN`, `SOFT_PF_CFG_EN`, `VF_VF_PRV_EN`, `FLR_TWICE_EN`, and `SOFT_PF_PFCOPY_PRV_EN`.

The RAS block is marked as `nbio_nbif0_bif_ras_bif_ras_regblk` and defines fields for:

- `BIFL_RAS_CENTRAL_CNTL` and `BIFL_RAS_CENTRAL_STATUS`.
- `BIFL_RAS_LEAF0_CTRL` through `BIFL_RAS_LEAF2_CTRL`.
- `BIFL_RAS_LEAF0_STATUS` through `BIFL_RAS_LEAF2_STATUS`.
- `BIFL_IOHUB_RAS_IH_CNTL` and `BIFL_RAS_VWR_FROM_IOHUB`.

These macros describe error event generation, propagation, detection, debug, poison, parity, egress stall, receiver error, interrupt, and status fields for the BIF link RAS leaves.

The SION block is marked as `nbio_nbif0_nbif_sion_SIONDEC`. It defines three repeated client lanes, `SION_CL0`, `SION_CL1`, and `SION_CL2`, each with 64-bit scheduling and credit values split into `_REG0` and `_REG1` halves:

- `RdRsp`, `WrRsp`, and `Req` burst targets.
- `RdRsp`, `WrRsp`, and `Req` time slots.
- request, data, read-response, and write-response pool credit allocation.
- `SION_CNTL_REG0` and `SION_CNTL_REG1`.

The rest of the chunk starts the `nbio_nbif0_bif_cfg_dev0_epf0_bifcfgdecp` PCI configuration-space view for endpoint function `BIF_CFG_DEV0_EPF0_0`. It includes conventional PCI header fields, PCIe capability registers, MSI/MSI-X, vendor-specific capabilities, VC capabilities, AER, BAR enhanced capabilities, power budget, DPA, secondary PCIe, ACS, ATS, page request, PASID, multicast, LTR, ARI, SR-IOV, data link feature, 16GT PHY/equalization, and PCIe lane margining.

## Important APIs, Types, And Macros

This chunk does not declare functions, structs, enums, or runtime APIs. Its important interface is a generated naming contract:

- Every field has a `REGISTER__FIELD__SHIFT` macro and a matching `REGISTER__FIELD_MASK` macro.
- Field constants are consumed by generic bitfield helpers. For example, `REG_SET_FIELD(value, REGISTER, FIELD, new_value)` depends on the exact `REGISTER__FIELD__SHIFT` and `REGISTER__FIELD_MASK` token names.
- Address selection comes from `nbio_7_7_0_offset.h`; these masks are only meaningful when paired with the matching NBIO 7.7.0 register address and base index.
- The header is included by `drivers/gpu/drm/amd/amdgpu/nbio_v7_7.c`, which wires NBIO 7.7 behavior into `struct amdgpu_nbio_funcs` and uses adjacent generated masks for doorbells, HDP flushing, interrupt handling, memory access, clock gating, and register remapping.

The PCIe configuration block mirrors standard PCI/PCIe fields. Examples include command/status, BARs, MSI/MSI-X message data/masks/pending bits, PCIe device/link capabilities and controls, AER uncorrectable/correctable error status and masks, SR-IOV VF count/stride/BAR fields, ATS/PASID controls used by address translation paths, ACS isolation controls, 16GT equalization state, and margining control/status fields.

## Control Flow

There is no local control flow in the header. Runtime control flow appears when driver code includes this header and performs read/modify/write sequences:

1. Compute or use a register address from `nbio_7_7_0_offset.h`.
2. Read the current register value with an NBIO, PCIe index/data, or PCIe-port accessor.
3. Extract or update a field using these shift/mask constants.
4. Write the updated value back to hardware, often only if the value changed.

For this chunk, likely consumers include reset, virtualization, RAS, and PCIe capability management paths. FLR and D3/D0 control fields affect function reset behavior; RAS fields affect error detection and interrupt propagation; SION fields affect internal NBIF credit/scheduling behavior; PCIe config fields expose capability state to the host and to virtualization-related code.

## State And Persistence Behavior

The file itself is stateless generated source. The state described by the macros is hardware register state:

- FLR and D3HOT-to-D0 reset control fields can cause or gate reset behavior for physical functions, virtual-function-facing paths, and soft PF copies. Sticky enable bits may persist across parts of reset sequencing depending on hardware semantics.
- D-state target and acknowledge fields reflect PCI power-management state transitions and whether a D3-to-D0 reset is required.
- RAS status and control fields represent live hardware error state and interrupt/propagation configuration. Status bits may be latch-like or write-to-clear depending on the underlying register contract outside this header.
- SION burst target, time slot, and credit allocation registers are persistent hardware configuration while the device is powered and affect NBIF traffic arbitration.
- PCI config-space fields are the device-visible configuration image. Host firmware, the Linux PCI core, VFIO, SR-IOV setup, AER handling, and amdgpu may all observe or mutate parts of this state.
- SR-IOV, ATS, PASID, ACS, ARI, MSI/MSI-X, and BAR-related fields have virtualization and DMA isolation implications. Incorrect values can survive long enough to affect device enumeration, IOMMU integration, interrupt delivery, or VF resource layout until reset or reinitialization.

## Dependencies And Integration Points

The immediate dependency is the generated register-address header for NBIO 7.7.0. The broader integration points are:

- `amdgpu/nbio_v7_7.c`, which includes this header and registers the NBIO function table used by the amdgpu device initialization path.
- AMDGPU SOC15 register access helpers and bitfield helpers in the driver core.
- Linux PCI and PCIe capability handling, because the `BIF_CFG_DEV0_EPF0_0` block maps standard PCI config-space concepts such as MSI/MSI-X, AER, SR-IOV, ACS, ATS, PASID, LTR, ARI, DLF, 16GT link state, and margining.
- RAS infrastructure and interrupt handling for NBIF/BIF error reporting.
- SR-IOV and VFIO/IOMMU paths, especially for VF BAR layout, VF enablement, ATS/PASID translation, ACS isolation, and MSI/MSI-X exposure.
- Hardware-generation matching: these masks are for NBIO 7.7.0 and must not be mixed with offset headers or runtime ASIC paths for a different NBIO generation.

## Risks And Edge Cases

- The chunk begins mid-register with only the mask tail of `DEV1_PF1_FLR_RST_CTRL`; the corresponding shifts are immediately before the chunk. Any per-chunk consumer must not treat that register as fully described by this slice alone.
- Generated macro names are part of the build contract. A typo or generation mismatch breaks `REG_SET_FIELD`/`REG_GET_FIELD` users at compile time or, worse, silently programs the wrong bits if mask values are wrong.
- Many fields are repeated across PFs, lanes, and capability variants. Copy/paste or script-generation errors can be hard to spot because adjacent blocks look intentionally similar.
- FLR, D-state, and reset-control fields are high-risk. Wrong grace timeouts, dummy response statuses, sticky bits, or VF/soft-PF enables can produce failed PCI resets, device hangs, or broken virtualization recovery.
- RAS control/status fields are safety-sensitive. Incorrect masks can suppress error interrupts, misreport poison/parity events, or leave egress stall propagation enabled/disabled incorrectly.
- PCIe config-space masks need to match the PCIe specification widths. BAR, MSI/MSI-X, AER, ACS, ATS, PASID, ARI, LTR, SR-IOV, 16GT equalization, and margining fields are interpreted by host software outside amdgpu as well as by the device.
- SR-IOV fields are especially sensitive: VF enable, VF memory-space enable, first VF offset, VF stride, VF device ID, supported/system page sizes, and VF BAR masks must agree with hardware enumeration or VFs can map invalid resources.
- Lane margining and 16GT equalization fields are per-lane repeated definitions. This chunk ends at lane 11, so merged documentation or validation must join with the following chunk for lanes 12-15.

## Test Signals

Useful validation signals for this chunk are mostly compile-time and hardware-integration oriented:

- Kernel build of the amdgpu driver for NBIO 7.7.0 ASIC support succeeds with `nbio_v7_7.c` including both the offset and mask headers.
- Static checks or generation diffs confirm every `REGISTER__FIELD__SHIFT` has a matching `REGISTER__FIELD_MASK`, and repeated PF/lane blocks use the expected bit positions.
- Driver boot on NBIO 7.7.0 hardware successfully initializes NBIO, maps/remaps registers, enables doorbells, sets interrupt handling, and performs HDP flushes without register access faults.
- PCI enumeration reports expected device/vendor IDs, BARs, MSI/MSI-X capabilities, PCIe link capabilities/status, AER capability layout, and extended capability chains.
- Suspend/resume and D3HOT-to-D0 transitions work without requiring unexpected full device recovery.
- FLR tests for PF/VF paths complete without hangs, with expected dummy response behavior and reset acknowledgements.
- SR-IOV enable/disable tests create the expected number of VFs with correct VF stride, VF BAR layout, VF device ID, and interrupt behavior.
- RAS injection or error-reporting tests show expected BIF/NBIF error status, interrupt delivery, and clearing behavior.
- PCIe AER, ACS, ATS/PASID, LTR, ARI, 16GT equalization, and lane margining diagnostics report values consistent with hardware documentation and Linux PCI core expectations.
