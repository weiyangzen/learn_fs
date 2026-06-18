# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_4_sh_mask.h lines 22068-24525

## Purpose

This chunk is a generated AMD NBIO 7.4 register shift/mask slice. It contains no executable logic; its purpose is to publish C preprocessor constants that tell AMDGPU NBIO, power-management, debug, and RAS code where individual bitfields live inside NBIO/PCIe configuration and sideband registers.

The selected range starts in the tail of the `GDCSOC_RAS_LEAF4_STATUS` field definitions, covers `GDCSOC_RAS_LEAF5_STATUS`, `GDCSOC_RAS_LEAF6_STATUS`, `GDCSHUB_RAS_CENTRAL_STATUS`, the full `nbio_nbif0_bif_cfg_dev0_swds_bifcfgdecp` / `BIF_CFG_DEV0_SWDS0_*` PCIe config-space block, RCC strap/endpoint/downstream/shadow register blocks for BIF decode and RCC port decode views, then enters `nbio_nbif0_bif_misc_bif_misc_regblk` and ends partway through `BIFC_DMA_ATTR_OVERRIDE_DEV0_F0_F1`.

## Public Surface In This Chunk

The public surface is 2,136 `#define` macros over 283 register names in the assigned line range. The macros are split into 1,073 `__SHIFT` constants and 1,063 `_MASK` constants. The counts are not balanced because the chunk begins in the middle of `GDCSOC_RAS_LEAF4_STATUS` and stops in the middle of `BIFC_DMA_ATTR_OVERRIDE_DEV0_F0_F1`.

Macro names follow the generated AMD register-field pattern:

- `<REGISTER>__<FIELD>__SHIFT` gives the field's starting bit.
- `<REGISTER>__<FIELD>_MASK` gives the pre-shifted bit mask.
- Prefixes such as `BIF_CFG_DEV0_SWDS0`, `RCC_EP_DEV0_0`, `RCC_EP_DEV0_1`, `RCC_DWN_DEV0_0`, `RCC_DWN_DEV0_1`, `SHADOW`, and `BIFC` identify the hardware register namespace that must be paired with same-generation NBIO 7.4 offsets.

There are no functions, structs, enums, variables, or inline helpers. The ABI-like contract is the exact macro spelling and numeric value, because downstream register helpers such as `REG_GET_FIELD`, `REG_SET_FIELD`, `RREG32_PCIE`, `WREG32_PCIE`, `RREG32_SOC15`, and `WREG32_SOC15` depend on these names matching the generated offset and SMN headers.

## Register Coverage

The opening RAS definitions expose leaf and hub status bits:

- `GDCSOC_RAS_LEAF4_STATUS` tail fields plus full `GDCSOC_RAS_LEAF5_STATUS` and `GDCSOC_RAS_LEAF6_STATUS` definitions for received error events, poison/parity detection, generated-status propagation, and egress-stall propagation.
- `GDCSHUB_RAS_CENTRAL_STATUS` fields for L2C/C2L egress-stall and error-event detection.

The `BIF_CFG_DEV0_SWDS0_*` block models a PCI-to-PCI/PCIe bridge-style configuration space:

- Conventional PCI identity and command/status fields: vendor/device ID, I/O and memory enable, bus master enable, SERR, interrupt disable, parity/abort/system-error status, revision/class bytes, cache line, latency, header type, BIST, BAR1, bridge bus numbers, I/O and memory windows, prefetchable memory windows, interrupt line/pin, and bridge control.
- Power-management and PCIe capability structures: PM capability/status/control, PCIe capability header, device/link/slot capability/control/status, Device Capabilities 2, Device Control 2, Link Capabilities 2, Link Control 2, Link Status 2, and slot capability/control/status 2.
- Interrupt and identity capabilities: MSI capability list/control/address/data, SSID capability, and PCIe vendor-specific enhanced capability headers and payload words.
- Virtual-channel and isolation features: VC enhanced capability, port VC capability/control/status, VC0/VC1 resource capability/control/status, device serial number, Advanced Error Reporting, ACS capability/control, Data Link Feature capability/status, 16 GT PHY capability/status, and lane margining.
- Diagnostics and error logs: AER uncorrectable status/mask/severity, correctable status/mask, AER capability/control, PCIe header logs, TLP prefix logs, secondary PCIe link control 3, lane error status, local/RTM parity mismatch at 16 GT, and per-lane equalization and margining status.

The per-lane groups are highly repetitive and cover lanes 0 through 15:

- `BIF_CFG_DEV0_SWDS0_PCIE_LANE_<n>_EQUALIZATION_CNTL` with downstream/upstream transmit preset fields and preset hint.
- `BIF_CFG_DEV0_SWDS0_LANE_<n>_EQUALIZATION_CNTL_16GT` with 16 GT transmit preset fields.
- `BIF_CFG_DEV0_SWDS0_LANE_<n>_MARGINING_LANE_CNTL` and `_STATUS` with receiver number, margin type, usage model, payload, request, software-ready, independent error sampler, and margin status fields.

The RCC endpoint/downstream sections expose internal NBIO controls around the same PCIe function:

- `RCC_STRAP0_RCC_DEV0_EPF0_STRAP0` and `RCC_STRAP1_RCC_DEV0_EPF0_STRAP0` for strapped device ID, revision ID, function enable, legacy device type, and D1/D2 support.
- `RCC_EP_DEV0_0_*` under `BIFDEC1` and `RCC_EP_DEV0_1_*` under `RCCPORTDEC`, including scratch, endpoint PCIe control, interrupt enable/status, RX control, bus/config control, transmit LTR control, DPA capability/latency/control/substate power allocation, PME control, TX control/requester ID, endpoint error control, RX error ignores, and link speed strap controls.
- `RCC_DWN_DEV0_0_*` and `RCC_DWN_DEV0_1_*` downstream controls for scratch/reserved, control, config, RX, bus, and CFG control.
- `RCC_DWNP_DEV0_0_*` and `RCC_DWNP_DEV0_1_*` downstream port controls for error control, RX control, link speed control, link control 2, and LTR message information from the endpoint.

The shadow and miscellaneous blocks cover bridge decode mirrors and BIFC policy/status:

- `SHADOW_*` bridge window mirrors for command, BAR1/BAR2, secondary/subordinate bus numbers, I/O base/limit, memory and prefetchable memory windows, upper prefetchable limits, high I/O base/limit, bridge control, and `SUC_INDEX`/`SUC_DATA`.
- `MISC_SCRATCH`, interrupt line polarity/enable, and `OUTSTANDING_VC_ALLOC` for outstanding request allocation per VC.
- `BIFC_MISC_CTRL0` and `BIFC_MISC_CTRL1` for BIFC/GMI/GSI/DMA policy bits: unit ID checking, DMA VC status, chain locking, split-read stall behavior, DMA atomic handling, SR-IOV/BME-drop handling, SDP read-response error forcing, unsupported command status, request ordering, request attribute masks, credit suppression, completion buffering, and message block-level selection.
- `BIFC_BME_ERR_LOG` and `BIFC_RCCBIH_BME_ERR_LOG0` for DMA/RCCBIH activity while bus mastering is low across dev0 functions 0-7, with corresponding clear bits.
- The beginning of `BIFC_DMA_ATTR_OVERRIDE_DEV0_F0_F1`, which provides two-bit override fields for ID-based ordering, relaxed ordering, snoop/no-snoop, and block-level behavior for dev0 functions 0 and 1. The rest of this override family continues after the chunk.

## Field Semantics

Most `BIF_CFG_DEV0_SWDS0_*` fields mirror PCI/PCI Express configuration-space semantics. Command/status fields determine whether the device decodes I/O or memory, can bus-master, reports parity or system errors, and exposes capability lists. Bridge window fields control how bus numbers and I/O/memory apertures are decoded. PCIe device/link/slot fields describe max payload/read request sizing, relaxed ordering, no-snoop, FLR, LTR/OBFF, link speed/width, ASPM, retrain and bandwidth events, slot power/attention signaling, and downstream presence.

AER and correctable/uncorrectable status fields are diagnostic and policy-sensitive. Status fields report error classes such as data link protocol, poisoned TLP, flow-control protocol, completion timeout, completer abort, unexpected completion, receiver overflow, malformed TLP, ECRC, unsupported request, ACS violation, internal error, MC blocked TLP, atomic egress blocked, TLP prefix blocked, and poisoned TLP egress blocked. Mask and severity fields decide what is suppressed and which errors are treated as fatal/nonfatal. Header and TLP prefix log masks are whole-register payloads, not ordinary feature enables.

Lane equalization, 16 GT PHY, and margining fields describe link-training and receiver-margin controls. The driver or firmware must keep lane indexes, speed-generation suffixes, and downstream/upstream preset directions aligned with the correct hardware lane. Misusing one repeated lane macro can corrupt only a single lane's training policy, which makes failures intermittent and platform-dependent.

RCC endpoint/downstream fields are lower-level PCIe fabric controls than the config-space capability fields. They cover unsupported-request reporting, malformed atomic handling, LTR message behavior, interrupt sources, DPA power allocation, PME, requester ID, AER header-log timer behavior, RX error ignores for payload/traffic-class/prefix/PASID/TPH cases, and link generation straps up to Gen5. These fields are integrated with `nbio_v7_4.c`; for example NBIO 7.4 ASPM/LTR programming writes `smnRCC_EP_DEV0_0_EP_PCIE_TX_LTR_CNTL` and clears `EP_PCIE_TX_LTR_CNTL__LTR_PRIV_MSG_DIS_IN_PM_NON_D0_MASK`.

BIFC controls are crossbar/fabric policy fields. They influence DMA ordering, atomic request handling, GMI/RCC/BIH BME-drop behavior, SDP/GSI error response forcing, outstanding VC allocation, and per-function bus-master error logging. These fields should be treated as low-level hardware policy and status bits, not as generic software flags.

## Control Flow And State

There is no runtime control flow in this header. The effective flow is compile-time substitution:

1. NBIO 7.4 consumers include `nbio/nbio_7_4_offset.h`, `nbio/nbio_7_4_sh_mask.h`, and, where needed, `nbio/nbio_7_4_0_smn.h`.
2. Driver or PM code reads a register through AMDGPU MMIO/SMN helpers such as `RREG32_PCIE` or `RREG32_SOC15`.
3. `REG_GET_FIELD` uses the generated `_MASK` and `__SHIFT` constants to decode fields, or `REG_SET_FIELD`/open-coded masks are used before writing back.
4. Actual state changes happen in NBIO/PCIe hardware registers, not in this file.

The header itself stores no state and persists nothing. Persistence belongs to the hardware registers: straps reflect sampled hardware/firmware configuration, config-space controls can persist until reset or function-level reset, link training fields persist until retrain or reprogramming, and error/log/status registers may be sticky or write-one-to-clear depending on the register. The RAS flow in `amdgpu/nbio_v7_4.c` demonstrates this pattern by reading RAS status, incrementing software error counters elsewhere, and writing hardware status values back to clear latched conditions.

## Dependencies And Integration Points

The direct generated-header dependencies are the matching NBIO 7.4 offset and SMN headers in the same `include/asic_reg/nbio` directory. Masks in this chunk must not be mixed with offsets from another NBIO generation or from a different decode prefix.

Known source-tree consumers include:

- `drivers/gpu/drm/amd/amdgpu/nbio_v7_4.c`, which includes this header for NBIO 7.4 register access, RAS interrupt handling, RAS error counting, doorbell control, clock/power setup, ASPM, and LTR programming.
- Power-management code such as `pm/powerplay/hwmgr/vega20_hwmgr.c`, `pm/powerplay/hwmgr/vega20_inc.h`, `pm/swsmu/smu11/arcturus_ppt.c`, `pm/swsmu/smu13/aldebaran_ppt.c`, and `pm/swsmu/smu13/smu_v13_0_6_ppt.c`, which include the same NBIO 7.4 headers while programming ASIC power/link behavior.
- AMDGPU discovery and RAS plumbing that selects `nbio_v7_4_funcs` / `nbio_v7_4_ras` for applicable ASIC IP versions.

Semantic dependencies include the PCI and PCI Express specifications, AMD's generated NBIO 7.4 register database, and ASIC-specific programming guides for side effects, read/write permissions, reset values, and write-one-to-clear behavior. The macros alone do not encode access type, reset value, ordering constraints, or whether firmware owns a field.

## Risks And Maintenance Notes

- The chunk boundaries are partial. It starts after the first `GDCSOC_RAS_LEAF4_STATUS` shift definition and ends before the rest of the `BIFC_DMA_ATTR_OVERRIDE_DEV0_*` definitions, so adjacent chunks are required for a complete per-file view.
- Generated names with prefixes that differ only by `0` versus `1`, such as `RCC_EP_DEV0_0_*` and `RCC_EP_DEV0_1_*`, are not interchangeable. They represent different decode views and must stay paired with their matching offsets.
- The per-lane equalization and margining blocks are repetitive; lane number, speed suffix, and preset direction are the primary differences. Manual edits or copied code can easily target the wrong lane or speed generation.
- Full-width masks such as `0xFFFFFFFFL` normally indicate an entire data/log/register payload. They should not be interpreted as permission to blindly write all bits as one.
- Error status, AER, RAS, BME log, and interrupt status fields may be sticky, hardware-updated, or write-one-to-clear. Incorrect read-modify-write sequences can lose error evidence or fail to clear interrupts.
- Link and power-management fields can affect ASPM/LTR, DPA, PME, link retraining, and link generation capability. Bad values can produce performance loss, hangs, hot-reset behavior, or platform-specific link instability.
- Fields whose hardware name contains `MASK` can generate identifiers ending in `_MASK_MASK`; tooling should not normalize or de-duplicate these names.

## Test Signals

Useful validation signals for this chunk are:

- Compile coverage for all NBIO 7.4 consumers, especially `amdgpu/nbio_v7_4.c` and the SMU/power-management files that include `nbio_7_4_sh_mask.h`.
- Cross-header checks that every register prefix represented here has a matching `reg*` or `smn*` definition in the NBIO 7.4 offset/SMN headers where expected.
- Generated-header comparison against AMD's authoritative NBIO 7.4 register database, focusing on repeated lane 0-15 blocks, AER status/mask/severity fields, RCC endpoint/downstream duplicates, and BIFC BME/DMA policy fields.
- Static validation that each field mask fits within its register width and corresponds to the documented shift and bit width; this is especially useful for multi-bit fields and partial chunks.
- Hardware register dumps decoded with these masks and compared with PCIe config-space tools such as `lspci -vvxxx` for command/status, capability chain, MSI, AER, ACS, link, slot, DLF, 16 GT PHY, and lane margining fields.
- RAS/error-injection testing that verifies NBIO RAS leaf/hub status, AER status, BME logs, interrupt status, and clear paths are decoded and cleared correctly without losing counts.
- ASPM/LTR and link-training tests on NBIO 7.4 hardware, including Gen4/Gen5 link speed policy, 16 GT equalization status, lane margining readiness, DPA/PME behavior, and absence of unexpected retrains.
- SR-IOV and BME policy tests for per-function DMA/RCCBIH BME-low logs and BIFC drop/override behavior, since several fields distinguish dev0 functions and VF/PF handling.
