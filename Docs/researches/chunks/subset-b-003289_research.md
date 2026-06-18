# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_7_0_sh_mask.h lines 73185-75598

## Chunk Scope

- Work item: `subset-b-003289`
- Source chunk: `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_7_0_sh_mask.h`, lines 73185-75598
- Parent file role: generated AMDGPU NBIO 7.7.0 register field shift/mask definitions. The matching offset header supplies register addresses; this file supplies the bit layouts used by `REG_SET_FIELD`, `REG_GET_FIELD`, and direct mask/shift operations.
- Chunk shape: 2,414 lines of preprocessor constants, covering about 1,336 distinct register-field macro names. It starts inside the `BIFPLR3_0_LANE_1_MARGINING_LANE_CNTL` field list and ends inside `BIFPLR4_0_PCIE_ESM_CAP_7`, so cross-chunk continuity is required.

## Purpose

This chunk defines bit positions and masks for two adjacent PCIe logical-root-port register families in NBIO 7.7.0:

- The tail of `BIFPLR3_0`, focused on PCIe lane margining, CCIX/ESM capability/control, 20 GT and 25 GT ESM per-lane equalization presets, CCIX transaction mode, and 32 GT link capability/control/status fields.
- The beginning and middle of `BIFPLR4_0`, beginning a new `nbio_pcie0_bifplr4_cfgdecp` address block. This portion covers PCI-compatible bridge configuration fields, PCIe capability fields, MSI and vendor-specific capabilities, virtual channels, device serial number, AER, secondary PCIe capability, lane equalization, ACS, multicast, L1 PM substates, DPC, RP PIO logging, and ESM capability tables through the first part of `PCIE_ESM_CAP_7`.

The file does not implement runtime behavior. It is a generated hardware ABI surface that lets AMDGPU code write and decode NBIO/PCIe registers using symbolic field names instead of hard-coded bit arithmetic.

## Important APIs, Types, And Symbols

There are no C functions, structs, enums, or storage objects in this slice. The effective API is the generated macro namespace:

- `BIFPLR3_0_LANE_n_MARGINING_LANE_CNTL` and `BIFPLR3_0_LANE_n_MARGINING_LANE_STATUS` fields for lanes 1 through 15. Each lane uses receiver number bits at shift `0x0`, margin type at `0x3`, usage model at `0x6`, and margin payload at `0x8`, with matching status fields. The lane 1 control group begins in the previous chunk; this chunk contains its trailing fields.
- `BIFPLR3_0_PCIE_CCIX_*` fields for CCIX capability list/header data, CCIX ESM capability, required/optional ESM data-rate support, ESM status, ESM control, CCIX transaction capability, and transaction control.
- `BIFPLR3_0_ESM_LANE_n_EQUALIZATION_CNTL_20GT` and `_25GT` fields for lanes 0 through 15. Each lane exposes downstream-port and upstream-port TX preset nibbles.
- `BIFPLR3_0_LINK_CAP_32GT`, `BIFPLR3_0_LINK_CNTL_32GT`, and `BIFPLR3_0_LINK_STATUS_32GT`, describing 32 GT equalization bypass/no-equalization support and control, modified training sequence usage, equalization phase success, link equalization requests, enhanced link behavior, transmitter precoding, and no-equalization-needed status.
- `BIFPLR4_0_VENDOR_ID` through `BIFPLR4_0_EXT_BRIDGE_CNTL`, which describe the PCI bridge-compatible identity, command/status, class-code, bus-number, I/O/memory/prefetchable aperture, ROM, interrupt, and bridge-control views.
- `BIFPLR4_0_PMI_*`, `BIFPLR4_0_PCIE_*`, `BIFPLR4_0_DEVICE_*`, `BIFPLR4_0_LINK_*`, `BIFPLR4_0_SLOT_*`, and `BIFPLR4_0_ROOT_*`, which define standard power-management and PCIe capability fields for device, link, slot, root, and extended capability status/control.
- `BIFPLR4_0_MSI_*`, `BIFPLR4_0_SSID_*`, `BIFPLR4_0_MSI_MAP_*`, and `BIFPLR4_0_PCIE_VENDOR_SPECIFIC*`, covering MSI enable/address/data, subsystem IDs, MSI remap metadata, and vendor-specific capability header/scratch fields.
- `BIFPLR4_0_PCIE_VC*` fields for port VC capability/control/status and VC0/VC1 resource capability/control/status, including traffic-class-to-VC mapping and negotiation status.
- `BIFPLR4_0_PCIE_ADV_ERR_*`, `BIFPLR4_0_PCIE_UNCORR_ERR_*`, `BIFPLR4_0_PCIE_CORR_ERR_*`, `BIFPLR4_0_PCIE_HDR_LOG*`, `BIFPLR4_0_PCIE_ROOT_ERR_*`, and `BIFPLR4_0_PCIE_TLP_PREFIX_LOG*`, which define AER status, mask, severity, logging, root error command/status, source ID, and TLP prefix logging fields.
- `BIFPLR4_0_PCIE_LINK_CNTL3`, `BIFPLR4_0_PCIE_LANE_ERROR_STATUS`, and `BIFPLR4_0_PCIE_LANE_n_EQUALIZATION_CNTL` for secondary PCIe/equalization status and per-lane downstream/upstream preset/hint fields.
- `BIFPLR4_0_PCIE_ACS_*`, `BIFPLR4_0_PCIE_MC_*`, and `BIFPLR4_0_PCIE_L1_PM_SUB_*`, defining ACS routing/translation controls, multicast overlay/block/receive fields, and L1 PM substate timing and enablement.
- `BIFPLR4_0_PCIE_DPC_*` and `BIFPLR4_0_PCIE_RP_PIO_*`, defining DPC capability/control/status/error-source fields plus RP PIO status/mask/severity/syserror/exception/header-log/prefix-log fields.
- `BIFPLR4_0_PCIE_ESM_*`, including ESM capability headers, status/control, and `PCIE_ESM_CAP_1` through the start of `PCIE_ESM_CAP_7`. These bitmap fields represent supported ESM data rates from 8.0G upward in 0.1G increments.

## Control Flow

The header has no executable control flow. Runtime control flow is driven by consumers of these constants:

1. Driver or diagnostic code selects a generated register offset from `nbio_7_7_0_offset.h`.
2. The code reads, writes, or polls the register through SOC15/NBIO helpers such as `SOC15_REG_OFFSET`, `RREG32_SOC15`, `WREG32_SOC15`, `RREG32_PCIE_PORT`, or `WREG32_PCIE_PORT`.
3. Field helpers combine the register value with this chunk's `__SHIFT` and `_MASK` macros. `REG_GET_FIELD` extracts status/capability values; `REG_SET_FIELD` updates control fields while preserving unrelated bits.
4. Hardware, not this header, performs link training, error logging, DPC handling, lane margining, ESM equalization, MSI generation, and power-state transitions.

`sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/nbio_v7_7.c` includes both `nbio_7_7_0_offset.h` and `nbio_7_7_0_sh_mask.h`, binding this generated field namespace into the NBIO 7.7.0 implementation. The particular symbols in this chunk are mostly a hardware-definition surface for PCIe root-port configuration, validation, and diagnostics rather than ordinary hot-path procedural code.

## State And Persistence Behavior

This source file has no mutable software state and persists no data. The state represented by its fields lives in PCIe/NBIO hardware registers:

- `BIFPLR3_0` lane margining control/status fields can affect or report per-lane receiver margining operations. Control fields are stateful hardware commands; status fields report the current or last sampled margining response.
- `BIFPLR3_0` CCIX/ESM and 20 GT/25 GT equalization fields expose supported data rates, calibration state, retimer/reach policy, quick equalization timeouts, and per-lane TX preset choices.
- `BIFPLR3_0` 32 GT link fields report or control high-speed link equalization behavior, modified training sequence support, transmitter precoding, and phase success.
- `BIFPLR4_0` bridge and PCIe capability fields describe root-port identity, class, bus numbering, memory and I/O windows, command/status bits, link speed/width, slot behavior, root PME, completion timeout policy, atomic operations, LTR, OBFF, DRS, and related capability state.
- MSI, VC, ACS, multicast, L1 PM substate, DPC, RP PIO, AER, ESM, and lane-equalization fields are a mix of capabilities, software-controlled enables, transient status bits, sticky error bits, and hardware logs. Some status bits are likely clear-on-write or write-one-to-clear according to the PCIe specification or AMD hardware behavior.

Persistence risk is therefore indirect. Incorrect masks or shifts can cause a driver or debug tool to preserve the wrong bits, clear the wrong sticky error, enable the wrong control, or misinterpret a hardware status value.

## Dependencies And Integration Points

- Depends on the matching `nbio_7_7_0_offset.h` register offsets. The masks in this chunk only make sense when applied to the corresponding `BIFPLR3_0_*` and `BIFPLR4_0_*` register addresses.
- Included by `amdgpu/nbio_v7_7.c`, which uses the NBIO 7.7.0 generated headers for register access, revision discovery, memory-controller access, doorbell ranges, interrupt setup, HDP flush offsets, PCIe index/data offsets, and BIF clock-gating/light-sleep control.
- Depends on AMDGPU's generic register-field helpers, especially `REG_SET_FIELD` and `REG_GET_FIELD`, which expect the `REGISTER__FIELD__SHIFT` and `REGISTER__FIELD_MASK` naming convention used here.
- Integrates with SOC15/NBIO access helpers, PCIe-port index/data windows, and any register-dump or debug tooling that decodes NBIO 7.7.0 PCIe root-port registers.
- Cross-generation neighbors such as `nbio_7_2_0_sh_mask.h`, `nbio_7_9_0_sh_mask.h`, and `nbio_7_11_0_sh_mask.h` contain similar names with generation-specific layouts. Code must include the mask header matching the active ASIC/IP version.

## Risks And Edge Cases

- The chunk starts and ends mid-family. It begins after the first fields of `BIFPLR3_0_LANE_1_MARGINING_LANE_CNTL` and ends before completing `BIFPLR4_0_PCIE_ESM_CAP_7`. The merge lane must combine adjacent chunks to avoid describing lane 1 or ESM cap 7 as incomplete hardware features.
- The generated content is highly repetitive. Lane 1 through 15 margining fields, 20 GT/25 GT equalization fields, lane 0 through 15 PCIe equalization fields, and ESM data-rate bitmaps are easy places for generator drift, copy/paste prefix errors, or off-by-one lane/rate bugs.
- Field aliases and shared bit positions are intentional. Many PCI and PCIe registers expose separate views of the same DWORD or WORD, so uniqueness checks must understand capability layouts rather than flagging every repeated shift/mask pattern.
- Link training fields are sensitive. Wrong masks for `LINK_CNTL2`, `LINK_STATUS2`, `LINK_CAP_32GT`, `LINK_CNTL_32GT`, `LINK_STATUS_32GT`, or per-lane equalization presets can cause incorrect speed targeting, misleading equalization diagnostics, or unstable high-speed links.
- Error-reporting fields are policy-critical. Incorrect AER, DPC, RP PIO, header-log, prefix-log, severity, mask, or source-ID masks can hide errors, report the wrong requester, clear sticky state unexpectedly, or trigger incorrect recovery actions.
- Power-management and latency fields can affect resume stability and performance. Incorrect L1 PM substate masks, common-mode restore time, T_POWER_ON, LTR, OBFF, or clock/power-management controls can create suspend/resume and low-power-state regressions.
- MSI and MSI-map fields are adjacent to capability metadata. Misdecoding address/data/enable bits could affect interrupt delivery or debugging of root-port MSI behavior.
- ESM capability bitmaps encode many adjacent rate points. A one-bit shift error changes the advertised rate by 0.1G and could be hard to detect without hardware validation across the affected speed range.

## Test And Validation Signals

- Build coverage: compile AMDGPU with NBIO 7.7.0 support and verify `nbio_v7_7.c` resolves the generated offset and mask headers without missing or renamed symbols.
- Generated-header consistency: mechanically verify that every field group has paired `__SHIFT` and `_MASK` definitions, that lane groups cover the expected lanes, and that this chunk aligns with adjacent chunks at `BIFPLR3_0_LANE_1_MARGINING_LANE_CNTL` and `BIFPLR4_0_PCIE_ESM_CAP_7`.
- Offset/mask pairing: validate that each register name in this mask chunk has a matching register offset in `nbio_7_7_0_offset.h`, especially `BIFPLR3_0` CCIX/ESM/32GT fields and the `BIFPLR4_0` root-port address block.
- Runtime smoke on matching hardware: successful GPU initialization, PCIe port access, interrupt delivery, HDP flush setup, memory-controller enablement, and doorbell setup indicate the broader NBIO 7.7.0 register map is coherent.
- PCIe link validation: exercise link speed and width negotiation, retraining, 8 GT/16 GT/20 GT/25 GT/32 GT equalization status reads, lane error status, margining diagnostics, and retimer/reach configurations where hardware supports them.
- Error-path validation: use controlled AER, DPC, RP PIO, and TLP-prefix/header-log scenarios to confirm status, mask, severity, source ID, and log fields decode and clear as expected.
- Power-management validation: test suspend/resume, L1 PM substates, LTR, OBFF, PME, and slot/link status transitions to catch incorrect masks in low-power and root-port status fields.
- Register-dump validation: decode dumps from all `BIFPLR*_0` ports and compare `BIFPLR4_0` against sibling `BIFPLR2_0`/`BIFPLR3_0` layouts for expected repetition with the correct port prefix.

## Notes For Merge/Reconciliation

- This is a chunk-level report only for `subset-b-003289`; no final per-file report was produced.
- Keep this artifact under `Docs/researches/chunks/`. The final source-tree-aligned report for `nbio_7_7_0_sh_mask.h` should be created later after all chunks for the source file are available.
- Adjacent chunks are needed to complete the preceding `BIFPLR3_0` lane 1 control register and the following `BIFPLR4_0_PCIE_ESM_CAP_7` bitmap.
