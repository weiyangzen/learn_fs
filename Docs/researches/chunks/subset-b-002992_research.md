# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_4_3_0_sh_mask.h lines 76467-78893

## Scope

This chunk is a generated AMD NBIO 4.3.0 register shift/mask header segment. It contains only C preprocessor constants; there are no functions, structs, variables, locks, allocations, loops, branches, or direct MMIO/config-space accesses in this range.

The range starts inside `BIF_CFG_DEV0_EPF0_VF13_1_COMMAND`, covers the remainder of `BIF_CFG_DEV0_EPF0_VF13_1`, then defines complete repeated PCIe configuration-space field layouts for `BIF_CFG_DEV0_EPF0_VF14_1` and `BIF_CFG_DEV0_EPF0_VF15_1`. It then enters the `addressBlock: nbio_nbif0_bif_cfg_dev0_epf1_bifcfgdecp` block and covers `BIF_CFG_DEV0_EPF1_1` from vendor/device identity through the first half of `LINK_CAP`; later EPF1 link-control/status, MSI/MSI-X, vendor-specific, AER, VC, serial-number, BAR, and GPUIOV-related fields continue after this chunk.

Although this source tree is under a local `ceph-client` mirror, this header is AMDGPU hardware metadata. It does not implement Ceph or distributed filesystem behavior.

## Purpose

The purpose of this header range is to publish bitfield positions for NBIO 4.3.0 PCIe/BIF configuration registers. Every represented field follows the generated AMD register-header convention:

- `<REGISTER>__<FIELD>__SHIFT` gives the bit offset for packing or extracting a field.
- `<REGISTER>__<FIELD>_MASK` gives the mask used to isolate, clear, preserve, or update the field.

The matching address side is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_4_3_0_offset.h`, which supplies the register offsets. This source tree has no local `nbio_4_3_0_default.h` companion, so reset/default-value analysis for these exact registers cannot be derived from a same-generation default header here.

Runtime code combines these constants with AMDGPU access helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, `RREG32_PCIE`, `WREG32_PCIE`, and `SOC15_REG_OFFSET`. The constants themselves are a compile-time ABI between generated hardware register descriptions and the C code that reads, programs, or decodes the NBIO block.

## Important Macro Families

The opening `VF13_1` fragment completes most of virtual function 13's PCIe configuration image after the command-register boundary. It covers PCI status, revision and class-code bytes, cache-line/latency/header/BIST fields, BAR1 through BAR6, CardBus CIS pointer, subsystem adapter ID, ROM base address, capability pointer, interrupt line/pin, min grant, and max latency.

The same `VF13_1` block then defines PCIe capability fields: `PCIE_CAP_LIST`, `PCIE_CAP`, `DEVICE_CAP`, `DEVICE_CNTL`, `DEVICE_STATUS`, `LINK_CAP`, `LINK_CNTL`, `LINK_STATUS`, `DEVICE_CAP2`, `DEVICE_CNTL2`, `DEVICE_STATUS2`, `LINK_CAP2`, `LINK_CNTL2`, and `LINK_STATUS2`. Important fields include max payload support/size, max read request size, relaxed ordering, no-snoop, extended tag, FLR capability/initiation, completion-timeout controls, ARI forwarding, atomic operation enables, ID-based ordering, LTR, OBFF, 10-bit tag support, link speed/width, ASPM/power-management controls, link disable/retrain, common clock, target link speed, equalization status, and link bandwidth notification state.

The VF MSI and MSI-X families describe capability-list linkage, MSI enable/multiple-message/64-bit/per-vector masking controls, MSI address/data/mask/pending storage, 64-bit aliases, MSI-X table size/function mask/enable bits, MSI-X table BIR/offset, and MSI-X PBA BIR/offset fields. These masks describe how interrupt programming state is packed in the virtual function's config image.

The VF vendor-specific and AER families define PCIe vendor-specific enhanced capability headers and payload dwords, AER enhanced capability headers, uncorrectable error status/mask/severity bits, correctable error status/mask bits, advanced error capability/control bits, four TLP header log dwords, and four TLP prefix log dwords. Covered AER conditions include DLP, surprise down, poisoned TLP, flow control, completion timeout, completion abort, unexpected completion, receiver overflow, malformed TLP, ECRC, unsupported request, ACS violation, internal error, MC blocked TLP, atomic-op egress blocked, and TLP prefix blocked.

The VF ARI and RTR tails define `PCIE_ARI_ENH_CAP_LIST`, `PCIE_ARI_CAP`, `PCIE_ARI_CNTL`, `PCIE_RTR_ENH_CAP_LIST`, `RTR_DATA1`, and `RTR_DATA2`. ARI fields expose MFVC/ACS function-group support, next-function number, function-group enable bits, and selected function group. RTR data fields expose readiness time reporting method/value/scale and readiness-valid state.

`BIF_CFG_DEV0_EPF0_VF14_1` and `BIF_CFG_DEV0_EPF0_VF15_1` are complete within this slice. Each repeats the full VF config-space pattern: identity/header/BAR fields, PCIe device/link capabilities and controls, MSI/MSI-X state, vendor-specific capability dwords, AER diagnostics, ARI fields, and RTR fields. This repetition is important for SR-IOV or GPU virtualization paths that address a specific virtual-function config image by suffix.

The final EPF1 fragment begins a physical or exposed function 1 config block rather than another EPF0 VF block. It covers vendor/device ID, command/status, revision and class-code bytes, header/BIST, BARs, adapter ID, ROM base address, cap pointer, interrupt and legacy timing fields, a vendor capability list, a writeable adapter ID alias, power-management capability/status/control fields, PCIe capability headers, device capability/control/status fields, and the first `LINK_CAP` shift fields through `ASPM_OPTIONALITY_COMPLIANCE__SHIFT`. Unlike the VF blocks in this chunk, EPF1 uses PMI and vendor-capability families before its PCIe capability chain and is incomplete at the chunk boundary.

## Control Flow

There is no executable control flow in this header. Runtime behavior occurs only in code that includes these macros:

1. AMDGPU code selects a register offset from `nbio_4_3_0_offset.h`, usually through generated `reg...` names and SOC15/NBIO access helpers.
2. The driver reads a 16-bit or 32-bit hardware/config-space value, or prepares a value to write.
3. The driver applies this header's `__SHIFT` and `_MASK` constants directly or through `REG_SET_FIELD` and `REG_GET_FIELD`.
4. The resulting value is written, decoded for diagnostics, polled as hardware-owned state, cleared as sticky status, or propagated to higher-level PCIe, SR-IOV, reset, interrupt, power, or RAS logic.

Typical consumers of these fields are VF PCI config-space presentation, MSI/MSI-X setup, AER error reporting and clearing, function-level reset, PCIe link and power policy, ARI virtualization support, readiness-time reporting, and physical-function PCIe capability management.

## State And Persistence Behavior

This file stores no software state and persists nothing to disk. It describes hardware-backed PCIe configuration and capability state owned by the GPU, platform firmware, host PCIe fabric, Linux PCI core policy, and AMDGPU NBIO/SR-IOV management code.

The represented state includes identity and class-code values, BAR and ROM apertures, command/status bits, capability-list pointers, PCIe device/link capability and control/status fields, MSI/MSI-X address/data/mask/pending state, vendor-specific payloads, AER status/mask/severity/log data, ARI function-group controls, RTR readiness fields, and EPF1 power-management capability state. Some fields are static capabilities, some are software-programmed controls, some are hardware-updated status, and some are sticky or write-one-to-clear diagnostics. The generated masks do not encode access width, reset defaults, ownership, polling requirements, or side effects.

VF14 and VF15 are complete in this chunk. VF13 and EPF1 are boundary fragments and require adjacent chunks before making complete per-function claims.

## Dependencies And Integration Points

The primary dependency is the generated NBIO 4.3.0 register database:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_4_3_0_offset.h` supplies matching register addresses.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_4_3_0_sh_mask.h` supplies the field masks and shifts documented here.
- AMDGPU SOC15 and register helper macros consume the `__SHIFT`/`_MASK` convention for field composition, extraction, and register addressing.

Observed direct include sites for `nbio_4_3_0_sh_mask.h` in this tree include `drivers/gpu/drm/amd/amdgpu/nbio_v4_3.c`, `drivers/gpu/drm/amd/pm/swsmu/smu13/smu_v13_0_0_ppt.c`, and `drivers/gpu/drm/amd/pm/swsmu/smu13/smu_v13_0_7_ppt.c`. `nbio_v4_3.c` actively uses NBIO-generated masks for doorbell aperture setup, interrupt control, HDP flush registers, ROM offset control, LTR enablement, and doorbell interrupt handling. The SMU13 power-management files include the same NBIO 4.3.0 header family and use SOC15/PCIE access helpers for firmware flag and debug-register paths.

The semantic integration surface overlaps generic PCIe and platform components: command/status, BAR sizing/exposure, MSI/MSI-X delivery, PCIe link state, AER, ARI, RTR, LTR, OBFF, completion timeout, FLR, and power management. Correct behavior depends on pairing the right field mask with the right NBIO 4.3.0 register offset and access path.

## Risks And Edge Cases

- The chunk boundaries are artificial. It starts after the first `VF13_1_COMMAND` shift fields and ends before EPF1 `LINK_CAP` masks or any later EPF1 PCIe capability families.
- These are untyped preprocessor constants. A stale or misgenerated mask can compile cleanly while reading or programming the wrong hardware bit.
- The VF blocks are mechanically repetitive. Suffix mistakes around `VF13_1`, `VF14_1`, and `VF15_1` can silently address the wrong virtual function and affect SR-IOV isolation, guest-visible config state, or diagnostics.
- Register-offset and field-mask mismatches are easy in generated headers. A valid `VF15_1_LINK_CNTL` mask applied to a `VF14_1`, EPF1, or non-NBIO offset may still produce plausible bit operations while corrupting unrelated config state.
- PCIe control fields are interoperability-sensitive. Incorrect max payload, max read request, relaxed ordering, no-snoop, FLR, completion timeout, LTR, OBFF, atomic-op, ARI, link-control, or target-link-speed programming can cause DMA ordering bugs, enumeration failures, link instability, reset failures, or platform-specific hangs.
- MSI/MSI-X fields have interrupt-delivery side effects. Wrong table BIR/offset, 64-bit alias, vector mask, pending, or enable handling can lose interrupts, route interrupts incorrectly, or unexpectedly unmask vectors.
- AER status, masks, severity, header logs, and TLP prefix logs may be sticky, hardware-owned, or write-one-to-clear. Generic read/modify/write treatment can clear useful diagnostics or leave errors masked incorrectly.
- BAR and ROM fields affect resource exposure. Incorrect masks can expose invalid apertures, confuse resource sizing, or break guest-visible VF config space.
- EPF1 PMI fields interact with PCI power management. Wrong power-state, PME enable/status, data-select/scale, or bus-power handling can break suspend/resume or wake signaling.
- The source tree lacks a same-generation default header, so tests that depend on reset values need hardware reads, firmware specifications, or another authoritative register database.

## Test Signals

Useful validation is primarily build-time and hardware-integration oriented:

- Build AMDGPU paths that include `nbio/nbio_4_3_0_sh_mask.h`; missing, duplicated, or renamed macros should surface in `nbio_v4_3.c` or SMU13 power-management files.
- Compare the covered register names against `nbio_4_3_0_offset.h` to confirm the VF13/VF14/VF15 and EPF1 register names and ordering remain synchronized.
- Boot affected NBIO 4.3.0 hardware and inspect PCIe config exposure: VF identity/header fields, BARs, capability list, PCIe capability, MSI/MSI-X, vendor-specific capability, AER, ARI, and RTR fields should decode consistently.
- In SR-IOV or virtualization configurations, create/remove VFs around the VF13-VF15 range, bind guest drivers, exercise VF FLR, and verify VF isolation, config-space access, ARI behavior, interrupt delivery, and reset paths.
- Exercise graphics, compute, and DMA workloads with MSI/MSI-X enabled; lost interrupts, stuck pending bits, or unexpected vector masking can indicate interrupt field layout or offset drift.
- Run PCIe reset, suspend/resume, runtime power, and link retraining tests while monitoring link speed/width, completion timeout behavior, LTR/OBFF state, and FLR completion.
- Use AER/error-injection or platform diagnostics where available to verify uncorrectable/correctable status, masks, severity fields, header logs, and TLP prefix logs map to expected PCIe errors.
- For EPF1, validate power-management capability and PME behavior across D-state transitions, suspend/resume, and runtime power-management paths.

## Chunk Notes

- Lines 76467-77173 are the trailing part of `BIF_CFG_DEV0_EPF0_VF13_1`, beginning inside `COMMAND` and ending after `RTR_DATA2`.
- Lines 77174-77895 are a complete `BIF_CFG_DEV0_EPF0_VF14_1` config-space shift/mask block.
- Lines 77896-78617 are a complete `BIF_CFG_DEV0_EPF0_VF15_1` config-space shift/mask block.
- Lines 78618-78893 begin `BIF_CFG_DEV0_EPF1_1` and stop inside `LINK_CAP`; subsequent EPF1 fields are outside this work item.
