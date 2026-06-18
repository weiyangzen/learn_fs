# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_4_3_0_offset.h lines 14905-17348

## Scope

This chunk is a generated AMD NBIO 4.3 register-offset header segment. It contains C preprocessor constants only: register/config-space offset macros and matching `_BASE_IDX` macros for selected memory-mapped register blocks. There are no functions, structs, variables, allocations, locks, branches, loops, or direct register reads/writes in this range.

The assigned slice starts at the body of `nbio_nbif0_gdc_GDCDEC` after its address-block label, covers GDC RAS/reset/syshub offsets, then maps a large set of PCIe configuration-space images: the `PSWUSCFG0` upstream bridge, `BIF_CFG_DEV0_RC1`, EPF0 physical function, EPF0 VF0 through VF15, EPF1, EPF2, and the beginning of EPF3. The chunk ends at `cfgBIF_CFG_DEV0_EPF3_1_PCIE_BAR4_CNTL`, so EPF3 is incomplete here.

Although this source tree is under a local `ceph-client` mirror, this header is AMDGPU hardware metadata. It does not implement Ceph or distributed filesystem logic.

## Purpose

The purpose of this range is to publish numeric offsets for NBIO 4.3 GDC/NBIF registers and PCIe configuration-space registers. Runtime AMDGPU code uses these constants with generated field masks from the matching `nbio_4_3_0_sh_mask.h` header and with register-access helpers to read, write, decode, or program hardware state.

Two macro forms appear:

- `reg...` macros name memory-mapped NBIO/GDC registers. In this chunk they use base index `3` and offsets under the `0x1400000` NBIO base window.
- `cfg...` macros name PCI/PCIe configuration-space registers. These are offsets inside the corresponding PCI config image and generally do not carry `_BASE_IDX` companions in this slice.

The header provides addresses only. It does not describe bit layouts, reset defaults, access widths, ownership rules, write-one-to-clear behavior, polling requirements, or side effects.

## Important Macro Families

The opening `GDCDEC` tail defines offsets for SHUB/GDC interface and control registers: `regGDC1_SHUB_REGS_IF_CTL`, NGDC memory/clock-gating control, reserved NGDC slots, GFX doorbell status, ATDMA/S2A miscellaneous controls, early wakeup control, and NGDC power-gating master/slave/misc controls. These offsets are integration points for doorbell visibility, data-mover behavior, wakeup, clock gating, and power gating.

The `nbio_nbif0_gdc_ras_gdc_ras_regblk` block defines GDC RAS/error offsets: `regGDCSOC_ERR_RSP_CNTL`, central RAS status, leaf control registers for leaves 0 through 4, leaf 2 misc controls, and leaf status registers. These are used by diagnostics and reliability flows that need to locate error-response control and per-leaf status.

The `nbio_nbif0_gdc_rst_GDCRST_DEC` block maps GDC/SHUB reset controls: PF FLR reset, GFX driver VPU reset, link reset, hard reset, soft reset, SDP port reset, and reset misc trailer. These offsets support reset sequencing and recovery paths, but the header itself does not encode reset ordering or delays.

The `nbio_nbif0_syshub_mmreg_syshubdirect` block contains two host-clock switch/control offsets, `regHST_CLK0_SW0_CL0_CNTL` and `regHST_CLK0_SW1_CL0_CNTL`, for direct syshub host-clock control.

The `nbio_pcie0_pswuscfg0_cfgdecp` block maps a PCIe upstream bridge-style configuration image. It includes standard identity/header fields, bus number and bridge window registers, capability pointers, power-management capability, PCIe capability, device/link capability/control/status registers, MSI registers, subsystem/vendor-specific capability entries, virtual channel and multicast capability registers, device serial number, AER status/mask/severity/logging, secondary PCIe capability, lane error/equalization controls, ACS, and MC registers.

The `nbio_nbif0_bif_cfg_dev0_rc_bifcfgdecp` block maps the root-complex function config image as `cfgBIF_CFG_DEV0_RC1_*`. It contains standard PCI config header fields, bridge window registers, PCIe capability, slot capability/control/status including second-generation slot registers, MSI fields, vendor-specific and AER extended capability registers, VC/MC/ACS/PASID/ARI registers, and several PCIe 16 GT/s extended capability regions such as PL16, link 16 GT, lane equalization, and lane margining.

The `nbio_nbif0_bif_cfg_dev0_epf0_bifcfgdecp` block maps endpoint physical function 0. It includes Type 0 header fields, BAR1 through BAR6, ROM and capability pointers, PM/PCIe/MSI/MSI-X capabilities, vendor-specific and AER logs, BAR enhanced capability registers, power budget, DPA substate power allocation registers, ACS, PASID, LTR, ARI, SR-IOV capability/control/status and VF resource registers, lane margining, VF resizable BAR registers, and 32 GT/s link registers. This is the richest complete physical-function block in the assigned slice.

The EPF0 VF0 through VF15 blocks are repetitive virtual-function config-space maps. Each VF block covers a compact VF PCIe image: identity/header bytes, BAR1 through BAR6, ROM/capability/interrupt fields, PCIe capability and device/link controls, MSI/MSI-X capability registers, vendor-specific capability registers, AER status/mask/severity and header/TLP prefix logs, and ARI capability/control registers. Each VF block has 78 defines in this slice and uses the same register ordering with a different VF suffix.

The EPF1 physical-function block resembles EPF0 but is smaller in this slice. It covers standard endpoint header fields, PM/PCIe/MSI/MSI-X, vendor-specific and AER logs, BAR enhanced capability, power budget, DPA, ACS, PASID, LTR, ARI, SR-IOV control/status/VF resource registers, and VF resizable BAR registers. It does not include the EPF0-only 16 GT/s/32 GT/s and lane-margining tail visible earlier in the chunk.

The EPF2 physical-function block maps standard endpoint header fields, PM/PCIe/MSI/MSI-X, vendor-specific and AER logs, BAR enhanced capability, power budget, DPA, ACS, PASID, and ARI. It does not include the SR-IOV, LTR, VF resizable BAR, or high-speed link extension coverage present in EPF0/EPF1 within this slice.

The EPF3 physical-function block begins at the end of the chunk and is incomplete. Covered offsets run from vendor/device ID through standard header, PM/PCIe capability, MSI/MSI-X, vendor-specific capability, AER logs, TLP prefix logs, and BAR enhanced capability registers through `PCIE_BAR4_CNTL`. EPF3 BAR5/BAR6, power/DPA, ACS/PASID/ARI, and any later capability offsets are outside this work item.

## Control Flow

There is no executable control flow in this header. Runtime behavior occurs only in code that includes and applies the generated constants:

1. AMDGPU selects a macro such as `regGDC1_NGDC_PG_MISC_CTRL`, `cfgBIF_CFG_DEV0_EPF0_1_PCIE_SRIOV_CONTROL`, or `cfgBIF_CFG_DEV0_EPF0_VF15_1_MSI_MSG_DATA`.
2. The selected offset is combined with the correct hardware access path, such as SOC15/NBIO MMIO access for `reg...` offsets or PCIe/config-space access for `cfg...` offsets.
3. Code pairs this offset with bit masks/shifts from generated `*_sh_mask.h` headers, often through helper macros such as `SOC15_REG_OFFSET`, `RREG32_SOC15`, `WREG32_SOC15`, `RREG32_PCIE`, `WREG32_PCIE`, `REG_SET_FIELD`, and `REG_GET_FIELD`.
4. Higher-level flows then program controls, inspect hardware status, poll reset/link bits, set up MSI/MSI-X, expose SR-IOV VFs, decode AER diagnostics, or manage PCIe capabilities.

Typical consumers are NBIO initialization, PCIe link setup and reporting, reset/FLR recovery, RAS/error handling, SR-IOV/MxGPU virtualization, interrupt delivery setup, power-management policy, and display or SMU code that needs NBIO 4.3 register locations.

## State And Persistence Behavior

This file stores no software state and persists nothing. It is generated address metadata for hardware-owned or firmware/platform-owned state.

The represented state includes GDC control/status, NGDC clock/power-gating control, doorbell status, ATDMA/S2A controls, RAS leaf control/status, reset controls, syshub clock controls, bridge and endpoint PCI configuration fields, BAR/resource windows, PM capability state, PCIe link/device capability and control state, MSI/MSI-X address/data/mask/pending registers, vendor-specific capability payloads, AER status/mask/severity/log fields, VC/MC/ACS/PASID/LTR/ARI controls, SR-IOV VF counts/strides/BARs, DPA power allocation, lane equalization/margining, and higher-speed link capability registers.

Some of those hardware fields are static capabilities, some are software-programmed controls, some are live hardware status, and some are sticky diagnostic values. The offset header alone cannot tell whether a register is safe for read/modify/write, whether a status bit is write-one-to-clear, or whether firmware, PCI core, guests, or the PF driver owns a field at a given time.

## Dependencies And Integration Points

This chunk depends on the NBIO 4.3 generated register database staying internally synchronized:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_4_3_0_sh_mask.h` supplies the bitfield shifts and masks for the same register names.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_4_3_0_default.h`, where present for these names, supplies reset/default values.
- AMDGPU register access wrappers and SOC15 register macros supply the actual MMIO/config-space access mechanism and base-index handling.

Direct include points found in this tree include `drivers/gpu/drm/amd/amdgpu/nbio_v4_3.c`, `drivers/gpu/drm/amd/pm/swsmu/smu13/smu_v13_0_0_ppt.c`, `drivers/gpu/drm/amd/pm/swsmu/smu13/smu_v13_0_7_ppt.c`, `drivers/gpu/drm/amd/display/dc/resource/dcn32/dcn32_resource.c`, and `drivers/gpu/drm/amd/display/dc/resource/dcn321/dcn321_resource.c`.

The most important integration surfaces are the Linux PCI core, AMDGPU NBIO/BIF code, SMU13 power-management code, DCN32/DCN321 display resource code, SR-IOV virtualization paths, MSI/MSI-X interrupt setup, AER reporting, reset and FLR handlers, suspend/resume, runtime power management, and platform firmware that may preconfigure parts of PCIe config space before the driver runs.

## Risks And Edge Cases

- The chunk boundaries are artificial. The assigned range starts immediately after the `nbio_nbif0_gdc_GDCDEC` address-block label and ends in the middle of EPF3's BAR enhanced capability map, so adjacent chunks are required for full GDCDEC and EPF3 analysis.
- These are untyped preprocessor constants. A stale or duplicated offset can compile successfully while sending register traffic to the wrong hardware location.
- The PCIe config-space blocks are highly repetitive. Suffix mistakes among `RC1`, `EPF0_1`, `EPF0_VF*_1`, `EPF1_1`, `EPF2_1`, and `EPF3_1` can silently target the wrong function or virtual function.
- `reg...` offsets use NBIO base-index semantics, while `cfg...` offsets are config-space offsets. Mixing the access paths can produce plausible-looking constants with incorrect hardware effects.
- Reset-related offsets are hazardous if used without the hardware sequence from driver code or firmware documentation. Wrong ordering around PF FLR, hard reset, soft reset, link reset, or SDP port reset can strand devices or lose diagnostic evidence.
- RAS/AER registers may contain sticky or write-one-to-clear fields. Generic read/modify/write code can clear error evidence, leave errors masked, or report the wrong severity.
- MSI/MSI-X offsets include aliases for 32-bit and 64-bit MSI layouts. Incorrect width assumptions can misprogram interrupt address/data, masks, or pending bits.
- BAR, VF BAR, and SR-IOV offsets affect resource exposure and guest-visible virtual functions. Incorrect offsets can break enumeration, isolate resources incorrectly, or expose invalid apertures.
- PCIe link, equalization, margining, power budget, DPA, LTR, ACS, PASID, and ARI controls are platform-sensitive. Bad programming can cause link instability, DMA ordering/security issues, IOMMU/ATS problems, poor power behavior, or virtualization isolation failures.
- EPF3 is only partially visible in this chunk; claims about EPF3's complete capability chain require the next chunk.

## Test Signals

Useful validation is mostly build-time and hardware-integration oriented:

- Build AMDGPU with NBIO 4.3 support enabled; missing or renamed macros should surface in `nbio_v4_3.c`, SMU13, or DCN32/DCN321 include paths.
- Compare generated `nbio_4_3_0_offset.h`, `nbio_4_3_0_sh_mask.h`, and `nbio_4_3_0_default.h` for the same register names so offsets, masks, and defaults remain aligned.
- Boot affected NBIO 4.3 ASICs and verify PCI enumeration: bridge windows, endpoint BARs, capability lists, MSI/MSI-X, AER, ACS/PASID/ARI, SR-IOV, and VF resource fields should decode consistently.
- Exercise SR-IOV creation/removal across EPF0 VF0 through VF15 and validate VF config access, VF BAR sizing, MSI/MSI-X delivery, ARI behavior, FLR, and guest bind/unbind paths.
- Run reset and recovery tests covering PF FLR, link reset, hard reset, soft reset, and suspend/resume while checking that devices re-enumerate and that RAS/AER state is not lost unexpectedly.
- Run graphics, display, compute, and DMA workloads with interrupt traffic enabled; lost interrupts or stuck pending bits can indicate MSI/MSI-X offset or alias mistakes.
- Use PCIe diagnostics or error injection where available to verify AER status, masks, severity, header logs, TLP prefix logs, and GDC RAS leaf status reporting.
- Exercise link retraining, high-speed link modes, equalization, and lane margining on hardware paths that expose the EPF0/RC extended capability offsets in this chunk.

## Chunk Notes

- Lines 14905-14927 cover the in-progress `nbio_nbif0_gdc_GDCDEC` block body, including 11 value macros and 11 `_BASE_IDX` macros.
- Lines 14930-14987 cover complete GDC RAS, GDC reset, and syshub-direct mini-blocks.
- Lines 14988-15177 cover the complete `PSWUSCFG0` upstream bridge config image visible in this file segment.
- Lines 15178-15359 cover the `BIF_CFG_DEV0_RC1` root-complex config image.
- Lines 15360-15625 cover the EPF0 physical-function config image, including SR-IOV, VF resizable BAR, margining, and 32 GT/s link offsets.
- Lines 15626-16937 cover complete repeated EPF0 VF0 through VF15 config images.
- Lines 16938-17128 cover the EPF1 physical-function config image through VF resizable BAR offsets.
- Lines 17129-17254 cover the EPF2 physical-function config image through ARI offsets.
- Lines 17255-17348 begin EPF3 and stop at `cfgBIF_CFG_DEV0_EPF3_1_PCIE_BAR4_CNTL`; later EPF3 offsets are outside this chunk.
