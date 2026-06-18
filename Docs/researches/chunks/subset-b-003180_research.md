# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_2_0_sh_mask.h lines 48775-51180

## Purpose

This chunk is an auto-generated AMD NBIO 7.2 shift/mask register-definition slice. It contains preprocessor constants for decoding and composing fields in NBIF/BIF reset-control, function-level reset, power-state, RAS, SION scheduling/credit, and `DEV0_EPF0` PCI/PCIe configuration registers. It is the field-layout companion to the NBIO 7.2 offset header: offset macros identify where a register lives, while this header tells driver code which bits inside the register represent a named hardware field.

The chunk has no executable code. It exports `#define` macros in the generated AMD register format:

- `REGISTER__FIELD__SHIFT` gives the low bit position for a field.
- `REGISTER__FIELD_MASK` gives the raw bit mask for the same field.

The selected range covers 2,406 source lines, 239 register/comment sections, 1,078 shift macros, and 1,083 mask macros. It begins in the tail of `SELF_SOFT_RST` masks and ends at `BIF_CFG_DEV0_EPF0_0_PCIE_VC0_RESOURCE_CAP`; the following `VC0_RESOURCE_CNTL` and later virtual-channel fields are outside this chunk.

## Public Surface In This Chunk

The public surface is entirely macro definitions. There are no C types, functions, structs, enums, or inline helpers in this range. Consumers are expected to combine these constants with register-access helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, `RREG32_PCIE_PORT`, `WREG32_PCIE_PORT`, and offset/base-index constants from `nbio_7_2_0_offset.h`.

The important macro families are:

- Reset and link reset controls: trailing `SELF_SOFT_RST` masks, `BIF_GFX_DRV_VPU_RST`, `BIF_RST_MISC_CTRL`, `BIF_RST_MISC_CTRL2`, and `BIF_RST_MISC_CTRL3`.
- Per-device/per-PF reset controls: `DEV0_PF0_FLR_RST_CTRL` through `DEV2_PF7_FLR_RST_CTRL`, plus `DEV0/1/2_PF*_D3HOTD0_RST_CTRL`.
- Reset and power interrupt status/mask fields: `BIF_INST_RESET_INTR_STS`, `BIF_PF_FLR_INTR_STS`, `BIF_D3HOTD0_INTR_STS`, `BIF_POWER_INTR_STS`, `BIF_PF_DSTATE_INTR_STS`, and their corresponding `*_INTR_MASK` registers.
- Function-level reset trigger and D-state value fields: `BIF_PF_FLR_RST`, `BIF_DEV{0,1,2}_PF{0..7}_DSTATE_VALUE`, and `BIF_PORT{0..2}_DSTATE_VALUE`.
- RAS register fields under `addressBlock: nbio_nbif0_bif_ras_bif_ras_regblk`, including central control/status, leaf controls/status, IOHUB interrupt handling, and virtual-wire reporting.
- SION decode/scheduling fields under `addressBlock: nbio_nbif0_nbif_sion_SIONDEC`, covering client groups `CL0`, `CL1`, and `CL2`.
- `DEV0_EPF0` PCI/PCIe configuration-space fields under `addressBlock: nbio_nbif0_bif_cfg_dev0_epf0_bifcfgdecp`, from vendor/device IDs through the beginning of the PCIe virtual-channel capability.

## Register Families

The reset-control block defines how the NBIF/BIF hardware exposes software, function-level, D3hot-to-D0, link, and self-reset behavior. `BIF_RST_MISC_CTRL` contains policy bits such as driver reset mode, auto-clear behavior for reset bits, FLR auto-clear, SR-IOV VF preservation on VF enable clear, link reset grace mode/timeouts, and dummy response controls. `BIF_RST_MISC_CTRL2` exposes transaction-idle status for link reset paths, while `BIF_RST_MISC_CTRL3` provides timer scaling and strap reload delays for hard, soft, and self resets.

The `DEV*_PF*_FLR_RST_CTRL` groups describe which reset domains are affected by FLR or software-initiated reset for physical functions. `DEV0_PF0_FLR_RST_CTRL` is the most detailed in this chunk: it includes PF config, PF FLR exception, PF sticky, PF private, VF config, VF sticky/private, software PF, VF-to-VF, FLR twice, grace mode/timeouts, dummy DMA/host response status, and soft PF copy-private controls. Other PF blocks expose a smaller repeated set of PF config/private, grace, timeout, and dummy-response fields. The same repeated pattern exists for `DEV1` and `DEV2`.

The interrupt status/mask groups expose reset and power-management event bits. `BIF_INST_RESET_INTR_STS` tracks instance reset requests across PFs on devices 0-2. `BIF_PF_FLR_INTR_STS` tracks PF FLR interrupt status for devices 0-2. `BIF_D3HOTD0_INTR_STS` tracks D3hot-to-D0 transitions, and `BIF_POWER_INTR_STS` tracks PME turnover, Dstate update, and secondary-bus reset events. The corresponding mask registers define which of those events can be masked. `BIF_PF_DSTATE_INTR_STS` and `BIF_DEV*_PF*_DSTATE_VALUE` expose per-function PCI power-state transitions and stored D-state values.

The RAS block defines central and leaf-level controls/status fields. `BIFL_RAS_CENTRAL_CNTL` controls interrupt enablement and poison-mode policy. `BIFL_RAS_CENTRAL_STATUS` exposes interrupt and poison mode status. Leaf controls allow masks or enables for corrected, nonfatal, fatal, and poison events; leaf status registers report the corresponding error state. `BIFL_IOHUB_RAS_IH_CNTL` controls interrupt handler generation/clearing, and `BIFL_RAS_VWR_FROM_IOHUB` exposes virtual-wire event bits.

The SION block describes traffic scheduling and pool-credit allocation. For each client group `CL0`, `CL1`, and `CL2`, it provides burst-target and time-slot fields for read responses, write responses, and requests, plus request, data, read-response, and write-response pool credit allocation fields. `SION_CNTL_REG0` and `SION_CNTL_REG1` then expose control bits for enablement, credit accounting, and scheduling behavior. These macros describe the register layout only; the arbitration policy and side effects are implemented by hardware and by any code that writes these registers.

The `BIF_CFG_DEV0_EPF0_0_*` section maps bitfields inside the endpoint function 0 PCI configuration-space view. It includes standard PCI header fields such as vendor/device ID, command/status, revision/class, BARs, subsystem adapter ID, ROM BAR, capability pointer, and interrupt line/pin. It then covers PM capability fields, PCIe capability/device/link capability and control/status fields, Device/Link Capability 2 and Control/Status 2, MSI and MSI-X capability fields, vendor-specific enhanced capability header/scratch fields, and the start of PCIe virtual-channel capability fields. Packed PCI config words intentionally have adjacent field definitions with 8-bit, 16-bit, or 32-bit masks, depending on the register layout.

## Control Flow And Data Flow

There is no runtime control flow in this header. The effective flow is compile-time substitution:

1. A translation unit includes `nbio_7_2_0_sh_mask.h` and the matching offset header.
2. Driver code selects a register offset and reads a 32-bit, 16-bit, or config-space value using the AMDGPU register access path appropriate for NBIO or PCIe-port access.
3. Code extracts fields by masking and shifting with these macros, or constructs an updated value through `REG_SET_FIELD`.
4. The caller writes the result back when it wants to program hardware.

The macros are intentionally dumb constants. They do not validate access width, field range, side effects, write-one-to-clear semantics, reset sequencing, or whether a field is writable on a given ASIC/SRIOV role. Those concerns belong to callers and to the hardware programming guides.

## State And Persistence

The header itself stores no state and has no persistence behavior. It describes hardware state that lives in NBIO/NBIF registers and PCI/PCIe configuration-space registers.

Several described fields affect persistent device-visible state until a reset, power transition, or explicit reprogramming changes it. Examples include D-state values, reset-mask controls, FLR/D3hot reset routing, interrupt masks, RAS masks, SION credit allocation, PCI command bits, BAR fields, MSI/MSI-X enable/mask/pending state, PCIe link controls, and virtual-channel controls. Several names explicitly include sticky reset or sticky status behavior, which means hardware may preserve or report information across selected reset scopes. The macros do not identify reset defaults; validation must come from the register specification or hardware dumps.

## Dependencies And Integration Points

This chunk depends on the generated AMD register-header naming contract and on the matching `nbio_7_2_0_offset.h` offsets. The main NBIO 7.2 implementation file, `drivers/gpu/drm/amd/amdgpu/nbio_v7_2.c`, includes both headers and uses this generation's shift/mask style for field manipulation in NBIO setup paths such as revision ID reads, memory-controller access enablement, doorbell aperture setup, interrupt control, clock-gating/light-sleep control, HDP flush masks, and ASIC-specific initialization.

The semantic dependencies are broader than the local C code:

- PCI and PCI Express configuration-space layout for standard header, PM, MSI, MSI-X, PCIe device/link, Device/Link Capability 2, vendor-specific, and virtual-channel capabilities.
- AMD NBIO/NBIF reset sequencing and SR-IOV behavior for PF/VF reset, FLR, D3hot-to-D0, link reset, sticky reset domains, and dummy responses.
- AMD RAS/IOHUB event routing for BIFL central/leaf status and interrupt handling.
- NBIF SION arbitration and credit allocation hardware for the `SION_CL*` registers.

The generated names align with related NBIF/NBIO generation headers, but they should not be treated as interchangeable across ASIC generations. Identical-looking field names can move, grow, shrink, or gain different side effects in another generation.

## Risks And Maintenance Notes

- The chunk starts mid-register family with trailing `SELF_SOFT_RST` masks. Adjacent earlier chunk research is needed for the matching `SELF_SOFT_RST__*__SHIFT` definitions that precede line 48775.
- The chunk ends mid-PCIe virtual-channel capability at `BIF_CFG_DEV0_EPF0_0_PCIE_VC0_RESOURCE_CAP`. The matching resource control/status fields and following PCIe capability fields are in the next chunk.
- These definitions are generated and highly repetitive. A one-bit shift error or stale mask can silently corrupt reset routing, interrupt masking, PCI config decoding, or PCIe link capability programming.
- Reset-related fields are high risk. Incorrect use of FLR, D3hot/D0, soft reset, sticky reset, or link reset controls can reset the wrong PF/VF, preserve stale state, break SR-IOV isolation, or leave transactions in flight.
- Interrupt status and mask fields may have hardware-specific clear semantics. Treating status fields as ordinary read/write storage can lose events or fail to clear them.
- RAS status/mask fields are reliability-critical. Incorrect masks can hide corrected, nonfatal, fatal, or poison events from the driver and from IOHUB interrupt handling.
- PCI config-space fields are packed and sometimes share storage. Callers must use the correct mask/shift and access width rather than assuming each named field is an independent register.
- MSI/MSI-X fields directly affect interrupt delivery. Incorrect field composition can disable interrupts, misroute vectors, or leave pending bits masked.
- SION credit and scheduling fields can affect NBIF traffic fairness and forward progress. Writes require hardware-specific values and sequencing; this header only exposes bit locations.

## Test Signals

Useful validation signals for this chunk include:

- Build coverage for `amdgpu/nbio_v7_2.c` and any other translation unit that includes `nbio_7_2_0_sh_mask.h`.
- Static generated-header checks that every `REGISTER__FIELD__SHIFT` in this chunk has the expected matching `REGISTER__FIELD_MASK`, and vice versa, except where adjacent chunks contain the other half of a split register family.
- Cross-header checks that the `BIF_CFG_DEV0_EPF0_0_*` field names here match the corresponding register offsets in `nbio_7_2_0_offset.h`.
- Hardware register dump comparison on NBIO 7.2 ASICs for reset status, D-state values, RAS status, MSI/MSI-X state, PCIe device/link capability fields, and virtual-channel capability fields.
- SR-IOV and FLR tests that exercise PF/VF reset, FLR interrupt status/masking, VF preservation policy, D3hot-to-D0 transitions, and dummy response behavior.
- RAS injection or error-reporting tests that confirm BIFL leaf/central status bits and IOHUB interrupt controls report and clear as expected.
- PCIe interoperability tests using kernel PCI enumeration and tools such as `lspci -vvxxx` to compare decoded command/status, PM, MSI/MSI-X, PCIe link, Device/Link Capability 2, vendor-specific, and virtual-channel fields against the generated masks.
