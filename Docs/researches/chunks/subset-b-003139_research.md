# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_11_0_sh_mask.h lines 41834-44284

## Scope

This chunk is a generated AMDGPU NBIO 7.11.0 shift/mask header segment. It contains 2,132 `#define` macros across 315 register-comment groups. There are no functions, structs, enums, globals, locks, allocations, or executable statements in this range.

The range starts in the middle of `BIF_CFG_DEV2_RC0_LANE_4_EQUALIZATION_CNTL_16GT`, covers the remainder of `BIF_CFG_DEV2_RC0` 16 GT/s lane equalization, PCIe margining, and readiness-to-return fields, then covers the complete `nbio_nbif0_bif_cfg_dev2_epf0_bifcfgdecp` endpoint-function block for `BIF_CFG_DEV2_EPF0_0`. It then begins the next address block, `nbio_nbif0_bif_cfg_dev2_epf1_bifcfgdecp`, and ends just after the first two `BIF_CFG_DEV2_EPF1_0_DEVICE_CNTL2` shift definitions. Adjacent chunks are needed for the earlier lane-4 equalization shifts and the rest of `EPF1_0_DEVICE_CNTL2` and later `EPF1_0` capability fields.

Although this source mirror is under `sources/distributed-fs/ceph-client`, the file is AMD GPU PCIe/NBIO hardware metadata and has no direct Ceph or distributed-filesystem behavior.

## Purpose

`nbio_7_11_0_sh_mask.h` is the generated bitfield-layout half of the NBIO 7.11.0 register interface. For each hardware field it provides:

- `<REGISTER>__<FIELD>__SHIFT`, the bit offset used to encode or decode the field.
- `<REGISTER>__<FIELD>_MASK`, the already shifted bit mask used to isolate, preserve, clear, or compose the field.

This chunk describes PCI Express configuration-space and extended-capability fields for NBIO device 2. The first part is root-complex port `RC0` metadata for 16 GT/s link equalization, lane margining, and readiness-to-return reporting. The second and largest part describes endpoint function `EPF0_0`: conventional PCI header fields, power-management capability fields, PCIe device/link controls and status, MSI/MSI-X, vendor-specific and virtual-channel capabilities, AER, BAR, power-budget, DPA, secondary PCIe equalization, ACS, PASID, LTR, ARI, data-link feature, 16 GT/s PHY/equalization, lane margining, and readiness-to-return registers. The final part begins the same PCI/PCIe capability layout for endpoint function `EPF1_0`.

These constants let AMDGPU code and bring-up/debug tooling decode or compose register words without hard-coding PCIe bit positions at call sites.

## Important Macro Families

The opening `BIF_CFG_DEV2_RC0` section covers root-complex link diagnostic and test-oriented fields:

- `BIF_CFG_DEV2_RC0_LANE_4_EQUALIZATION_CNTL_16GT` through `LANE_15_EQUALIZATION_CNTL_16GT` define downstream/upstream 16 GT/s TX preset fields. Lanes 5-15 are complete in this chunk; lane 4 starts with only the two mask lines because its shift lines are in the previous chunk.
- `BIF_CFG_DEV2_RC0_PCIE_MARGINING_ENH_CAP_LIST`, `MARGINING_PORT_CAP`, and `MARGINING_PORT_STATUS` expose the PCIe margining enhanced-capability header and port readiness/software-readiness bits.
- `BIF_CFG_DEV2_RC0_LANE_0_MARGINING_LANE_CNTL/STATUS` through lane 15 define the repeated receiver number, margin type, usage model, and margin payload fields for lane margining commands and status readback.
- `BIF_CFG_DEV2_RC0_PCIE_RTR_ENH_CAP_LIST`, `RTR_DATA1`, and `RTR_DATA2` describe readiness-to-return capability metadata and message timing/data fields.

The `BIF_CFG_DEV2_EPF0_0` address block is complete in this chunk and represents a full endpoint-function PCI configuration and enhanced-capability layout:

- Base PCI header fields: vendor/device ID, command/status, revision/class codes, cache line, latency, header/BIST, BAR1-BAR6, adapter ID, ROM base, capability pointer, interrupt line/pin, min grant, max latency, and vendor capability pointers.
- Power-management and USB-style legacy fields: `PMI_CAP_LIST`, `PMI_CAP`, `PMI_STATUS_CNTL`, `SBRN`, `FLADJ`, and `DBESL_DBESLD`.
- Core PCIe capability fields: `PCIE_CAP_LIST`, `PCIE_CAP`, `DEVICE_CAP`, `DEVICE_CNTL`, `DEVICE_STATUS`, `LINK_CAP`, `LINK_CNTL`, `LINK_STATUS`, `DEVICE_CAP2`, `DEVICE_CNTL2`, `DEVICE_STATUS2`, `LINK_CAP2`, `LINK_CNTL2`, and `LINK_STATUS2`.
- Interrupt capabilities: MSI list/control/message address/data/mask/pending fields and MSI-X list/control/table/PBA fields.
- Vendor, virtual-channel, and SATA-like capability windows: vendor-specific enhanced capability headers/data, VC port/resource capability/control/status for VC0 and VC1, and SATA IDP index/data fields.
- Error and diagnostic fields: AER enhanced capability, uncorrectable/correctable error status/mask/severity, AER control, header logs, TLP prefix logs, lane error status, parity mismatch status for 16 GT/s, and readiness-to-return fields.
- Link tuning and isolation features: BAR enhanced capability controls, power budget, Dynamic Power Allocation, secondary PCIe link control/equalization for lanes 0-15, ACS, PASID, LTR, ARI, data-link feature capability/status, 16 GT/s PHY/equalization, margining, and per-lane margining command/status fields.

The `BIF_CFG_DEV2_EPF1_0` block begins at line 43917. This chunk covers its base PCI header, vendor and power-management capabilities, PCIe device/link capability/control/status fields, and all of `DEVICE_CAP2`. It ends immediately after the `CPL_TIMEOUT_VALUE` and `CPL_TIMEOUT_DIS` shift definitions for `DEVICE_CNTL2`, so the masks and remaining `DEVICE_CNTL2` fields are outside this chunk.

## APIs, Types, And Functions

There are no callable APIs or C types in this range. The public interface is the generated preprocessor namespace. The macro values are untyped integer literals, mostly with an `L` suffix, and encode field geometry only.

These definitions do not provide register addresses, reset values, read/write permissions, access width, write-one-to-clear behavior, firmware ownership, or sequencing rules. Consumers must combine them with matching address macros from `nbio_7_11_0_offset.h`, defaults from any generated default metadata, and AMDGPU helper macros/functions such as `REG_GET_FIELD`, `REG_SET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, `RREG32_PCIE_PORT`, and `WREG32_PCIE_PORT`.

The ASIC implementation file `amdgpu/nbio_v7_11.c` includes both `nbio_7_11_0_offset.h` and this shift/mask header and uses the generated constants through SOC15 and PCIe-port register access helpers. A tree search in this snapshot shows direct NBIO 7.11 code using this header mostly for other NBIO fields; these `BIF_CFG_DEV2_*` PCIe configuration fields may be consumed by conditional paths, generated tooling, debug code, or downstream hardware-management code not visible in the sampled file.

## Control Flow

This header has no runtime control flow. Runtime behavior is supplied by code that includes it:

1. Driver, firmware-facing, or diagnostic code selects a `regBIF_CFG_DEV2_*` address from `nbio_7_11_0_offset.h`.
2. The code reads the register, extracts fields with the `__SHIFT` and `_MASK` constants, or constructs an updated register value while preserving unrelated and reserved bits.
3. Hardware observes the write or returns status through PCIe configuration, link training, error-reporting, margining, interrupt, power-management, or routing logic.

Several represented fields imply asynchronous protocol flow even though the header does not implement it: link retraining and link-training status, data-link active reporting, MSI/MSI-X enable and pending state, AER status/log capture and clearing, DPA substate power allocation, secondary PCIe equalization phases and presets, ACS/PASID/ARI/LTR policy enablement, 16 GT/s parity mismatch reporting, lane margining command/status exchange, and readiness-to-return timing/message reporting.

## State And Persistence Behavior

The header owns no state and persists nothing. It describes hardware-visible state in NBIO PCIe configuration registers. Persistence depends on PCIe reset, GPU reset domains, function-level reset, link reset/retrain, firmware/BIOS initialization, suspend/resume restore, power management, and explicit AMDGPU or platform writes.

Represented state includes PCI command/status bits, BAR and ROM decode fields, class and revision identity, capability-list pointers, interrupt routing values, power-management control/status, PCIe device and link capability/control/status, completion-timeout and atomic/ARI/LTR/OBFF controls, MSI/MSI-X configuration and masks, VC/ACS/PASID policy, AER status/masks/severity and captured logs, BAR and power-budget metadata, DPA status/control and substate allocations, per-lane equalization presets, 16 GT/s equalization and parity status, margining command/status payloads, and readiness-to-return timing fields.

Some fields are read-only capability values, some are writable policy controls, and some are status or log bits with protocol-specific clear semantics. That access behavior is not encoded by the shift/mask macros and must come from PCIe/NBIO hardware documentation and the surrounding driver sequence.

## Dependencies And Integration Points

This chunk depends on the rest of AMD's generated NBIO 7.11.0 register package:

- `nbio_7_11_0_offset.h` supplies the corresponding `regBIF_CFG_DEV2_*` register addresses and base indices.
- Other chunks of `nbio_7_11_0_sh_mask.h` supply the boundary fields before `RC0_LANE_4_EQUALIZATION_CNTL_16GT` and after `EPF1_0_DEVICE_CNTL2`.
- AMDGPU register helpers provide field packing/extraction and the actual MMIO, SOC15, or PCIe-port register access path.
- PCIe core policy, platform firmware setup, and GPU reset/suspend-resume paths determine when these fields are valid to read, write, restore, or clear.

Integration points include NBIO initialization, PCIe endpoint-function configuration, PCI enumeration support, BAR/ROM decode setup, MSI/MSI-X programming, link speed/width negotiation, link equalization diagnostics, lane margining support, AER and error-log handling, power management, DPA/power-budget reporting, ACS/PASID/ARI/LTR configuration for virtualization and memory-translation policy, and low-level hardware bring-up/debug flows.

## Risks And Edge Cases

- Generated shift/mask drift can compile cleanly while directing reads or writes to the wrong PCIe bit. Symptoms can include failed enumeration, broken BAR decode, misrouted interrupts, link-training failures, lost error reporting, or incorrect virtualization isolation.
- The chunk boundaries split real register groups. `RC0_LANE_4_EQUALIZATION_CNTL_16GT` and `EPF1_0_DEVICE_CNTL2` are incomplete here, so merged research must reconcile adjacent chunks before treating either boundary register as fully documented.
- Many PCIe status and AER fields are latch-like or write-one-to-clear in hardware. The shift/mask header does not mark those semantics, so code must capture associated header/TLP-prefix/source logs before clearing status bits.
- Link equalization, retraining, margining, readiness-to-return, DPA, PME, FLR, and reset-related controls can trigger asynchronous hardware state changes. Writers need bounded polling, timeout handling, and reset/power-state awareness.
- Reserved fields and capability readbacks should not be used as writable feature controls. Read-modify-write paths should preserve unrelated bits unless the hardware documentation says otherwise.
- Endpoint-function instances are mechanically repeated. Copy/paste or generator mistakes can affect `EPF0_0` and `EPF1_0` differently, making failures function-specific.
- Security-sensitive policy fields such as ACS, PASID, ARI, relaxed ordering, no-snoop, atomic operations, and LTR can change DMA routing, ordering, and isolation behavior if programmed incorrectly.

## Test Signals

- Build AMDGPU with NBIO 7.11 support enabled. Compile-time coverage catches missing or renamed generated symbols referenced by consumers.
- Run generated-header consistency checks: each complete field should have a matching `__SHIFT` and `_MASK`, masks should align with their shifts, and repeated lane/function blocks should match where the hardware layout is intended to be identical.
- Cross-check this chunk against `nbio_7_11_0_offset.h` so every `BIF_CFG_DEV2_RC0`, `BIF_CFG_DEV2_EPF0_0`, and visible `BIF_CFG_DEV2_EPF1_0` field maps to the expected register address and base index.
- On supported hardware or simulator traces, validate PCIe enumeration, BAR sizing/decode, ROM decode behavior, MSI/MSI-X delivery, negotiated link speed/width, link retraining, data-link-active reporting, and suspend/resume or reset restore.
- Exercise error and diagnostic paths: AER correctable/nonfatal/fatal status, AER masks/severity, captured header/TLP-prefix logs, 16 GT/s equalization completion and parity mismatch status, lane error status, and readiness-to-return status.
- For margining and equalization users, verify per-lane command/status payload encoding, receiver selection, margin type, usage model, 16 GT/s preset programming, hardware readiness bits, timeout behavior, and preservation of reserved bits during read-modify-write sequences.
- Merged per-file research should connect this document with adjacent chunks for the complete `nbio_7_11_0_sh_mask.h` register map rather than treating this line range as a standalone final report.
