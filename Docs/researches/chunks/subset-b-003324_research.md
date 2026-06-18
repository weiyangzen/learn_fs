# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_9_0_offset.h lines 2714-6013

## Chunk Scope

- Work item: `subset-b-003324`
- Source chunk: `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_9_0_offset.h`, lines 2714-6013
- Parent file role: generated AMDGPU NBIO 7.9.0 register offset map used with SOC15/NBIO register access helpers.
- Chunk shape: 3,252 preprocessor definitions, representing 1,626 register symbols plus one paired `*_BASE_IDX` definition for each symbol. Every visible `*_BASE_IDX` in this span is `8`.

## Purpose

This chunk provides symbolic register offsets for NBIO 7.9.0 BIF/NBIF PCI configuration, RCC control, MSI-X table/PBA, strap, reset, doorbell, and PF/VF base-address register spaces. It has no executable logic. AMDGPU code combines these generated `reg*` names with the matching `_BASE_IDX` metadata through helpers such as `SOC15_REG_OFFSET`, `RREG32_SOC15`, `WREG32_SOC15`, `WREG32_SOC15_OFFSET`, and `WREG32_FIELD15_PREREG`.

The range begins in the tail of the previous `aid_nbio_nbif0_bif_cfg_dev0_epf0_bifcfgdecp` address block, where EPF0 vendor-specific GPUIOV scheduler dwords and interrupt-enable/status registers are still being listed. It then covers a complete direct-MMIO config-space view for `DEV0_EPF1`, RCC link/endpoint/downstream controls, a 256-entry MSI-X vector table and 8-dword pending-bit array, SUM indirect index/data registers, a large RCC strap region, BIF reset/interrupt/D-state registers, and the beginning of the BIF miscellaneous region through PF/VF AID base-address maps.

This is register ABI documentation, not Ceph or distributed-filesystem logic. The `ceph-client` path is the repository mirror location; the content is AMD GPU kernel hardware interface data.

## Major Register Families In This Chunk

- Lines 2714-2806 finish the visible tail of `aid_nbio_nbif0_bif_cfg_dev0_epf0_bifcfgdecp`. The visible symbols include `BIF_CFG_DEV0_EPF0_0_PCIE_VENDOR_SPECIFIC_HDR_GPUIOV_GFX2SCH_DW0` through `GFX7SCH_DW8`, followed by GPUIOV `ENGA`/`ENGB` interrupt enable and status registers for engine ranges `A0_7`, `A8_15`, `B0_7`, and `B8_15`.
- Lines 2808-3048 define `aid_nbio_nbif0_bif_cfg_dev0_epf1_bifcfgdecp` at base address `0x10141000`. This is a direct register-index view of PCI function `DEV0_EPF1`, starting at register index `0x10400`. It includes standard PCI header aliases, BARs, ROM BAR, capability pointer, interrupt fields, PM capability, PCIe device/link capabilities, MSI/MSI-X capability registers, vendor-specific enhanced capability dwords, AER status/mask/severity/logging, TLP prefix logs, enhanced BAR capability/control registers, power-budget registers, DPA, ACS, PASID, and ARI.
- Lines 3050-3072 define `aid_nbio_nbif0_rcc_dev0_RCCPORTDEC` at base `0x10131000`. These `RCC_DEV0_1_*` registers expose VDM support, bus control, feature/misc control, device/common link controls, requester-ID restore, LTR switch control, memory-hub arbitration, and link margining parameter controls.
- Lines 3074-3132 define `aid_nbio_nbif0_rcc_ep_dev0_RCCPORTDEC`, the endpoint side of RCC/PCIe control. It includes scratch/control/status, interrupt control/status, RX/TX/bus/config controls, TX LTR control, strap misc registers, function-0 DPA capability/control/substate allocation aliases, PME control, TX requester ID, error control, and link speed control.
- Lines 3134-3156 define `aid_nbio_nbif0_rcc_dwn_dev0_RCCPORTDEC`, the downstream-side RCC/PCIe controls: reserved/scratch/control/config/RX/bus/cfg registers plus downstream strap fields for function 0.
- Lines 3158-3172 define `aid_nbio_nbif0_rcc_dwnp_dev0_RCCPORTDEC`, downstream-port error, RX, link-speed/link-control, strap, and LTR message information registers.
- Lines 3174-3194 define `aid_nbio_nbif0_rcc_pfc_amdgfx_RCCPFCDEC`, with PFC LTR, PME restore, sticky restore dwords 0-5, and auxiliary power control.
- Lines 3196-5246 define `aid_nbio_nbif0_pciemsix_0_usb_MSIXTDEC` at base `0x10168000`. This is the MSI-X table window, with vector entries `0` through `255`; each vector has `ADDR_LO`, `ADDR_HI`, `MSG_DATA`, and `CONTROL` dwords at a regular four-register stride from `0x1a000` through `0x1a3ff`.
- Lines 5248-5266 define `aid_nbio_nbif0_pciemsix_0_usb_MSIXPDEC` at base `0x10169000`, the MSI-X pending-bit array registers `PCIEMSIX_PBA_0` through `PCIEMSIX_PBA_7`.
- Lines 5268-5276 define `aid_nbio_nbif0_bif_swus_SUMDEC`, containing `SUM_INDEX`, `SUM_DATA`, and `SUM_INDEX_HI` for an indexed sideband/summary register access path.
- Lines 5278-5648 define `aid_nbio_nbif0_rcc_strap_rcc_strap_internal`. This region lists strap registers for RCC device ports, BIF straps, `DEV0_EPF0` and `DEV0_EPF1`, `DEV0_EPF2` through `DEV0_EPF7`, `DEV1_EPF0/1`, and `DEV2_EPF0/1/2`. Several strap sequences intentionally skip numbers where the generated register database has no visible macro in this span.
- Lines 5650-5702 define `aid_nbio_nbif0_bif_rst_bif_rst_regblk`. Important symbols include hard and self soft reset controls, VPU reset, reset miscellaneous controls, PF0/PF1 FLR and D3hot-to-D0 reset controls, instance/PF FLR/D3hot/power/PF D-state interrupt status and mask registers, PF FLR reset, and D-state value registers.
- Lines 5704-6013 begin `aid_nbio_nbif0_bif_misc_bif_misc_regblk`. The visible portion contains ROM offset and BIOS strap controls, `DOORBELL0_CTRL_ENTRY_0` through `DOORBELL0_CTRL_ENTRY_20`, and base-address mapping registers for `VF0` through `VF7` plus `PF` across AID, XCC, NBIF, ATHUB, IH, and HDP destinations. The chunk ends after `regAID0_XCC1_PF_BASE_ADDR`.

## Important APIs, Types, And Symbols

There are no C functions, structs, enums, or storage objects in this chunk. The public API is entirely preprocessor constants:

- Register-offset macros such as `regBIF_CFG_DEV0_EPF1_0_COMMAND`, `regRCC_EP_DEV0_1_EP_PCIE_INT_STATUS`, `regPCIEMSIX_VECT255_CONTROL`, `regPCIEMSIX_PBA_7`, `regSUM_INDEX_HI`, `regRCC_STRAP1_RCC_DEV0_EPF1_STRAP25`, `regDEV0_PF0_FLR_RST_CTRL`, `regDOORBELL0_CTRL_ENTRY_20`, and `regAID0_NBIF_VF7_BASE_ADDR`.
- Paired base-index macros such as `regBIF_CFG_DEV0_EPF1_0_COMMAND_BASE_IDX`, `regPCIEMSIX_VECT0_ADDR_LO_BASE_IDX`, and `regBIF_PF_FLR_INTR_MASK_BASE_IDX`, all set to `8`. The base index selects the generated NBIO register-base segment; the numeric offset alone is not enough to compute an MMIO address.
- PCI configuration aliases in `BIF_CFG_DEV0_EPF1_0_*`. Multiple logical fields can share one dword index: vendor/device IDs at `0x10400`, command/status at `0x10401`, class-code bytes at `0x10402`, cache/latency/header/BIST at `0x10403`, MSI address/data/mask/pending aliases, DPA status/control aliases, DPA substate allocations packed four per dword, ACS capability/control aliases, PASID capability/control aliases, and ARI capability/control aliases.
- MSI-X table symbols with a strict vector layout: `regPCIEMSIX_VECTN_ADDR_LO`, `ADDR_HI`, `MSG_DATA`, and `CONTROL`. This layout is normally consumed by PCI/MSI-X programming and interrupt validation code rather than by bespoke per-vector logic.
- Strap and reset symbols that are stateful hardware configuration points. AMDGPU NBIO 7.9 code reads the EPF0 strap revision ID via `regRCC_STRAP0_RCC_DEV0_EPF0_STRAP0` from an earlier chunk of this same header, and this chunk continues many adjacent strap names used by the same register family.
- Doorbell and base-address mapping symbols in the visible `bif_misc` portion. `nbio_v7_9.c` uses `regDOORBELL0_CTRL_ENTRY_*` macros for SDMA/VCN doorbell routing, and the AID/XCC/NBIF/ATHUB/IH/HDP base-address symbols describe per-PF/VF routing apertures.

## Control Flow

This header has no executable control flow. Runtime flow is created by AMDGPU users of the symbols:

1. Driver code selects a generated NBIO 7.9.0 register macro matching the active hardware path.
2. SOC15/NBIO access helpers combine the macro value, its `*_BASE_IDX`, the NBIO IP block, and an instance/AID offset into an MMIO address.
3. The driver reads, writes, polls, or field-updates that address, often using the matching `nbio_7_9_0_sh_mask.h` definitions with `REG_GET_FIELD`, `REG_SET_FIELD`, or `WREG32_FIELD15_PREREG`.

The control-flow significance of this chunk is data-driven. PCI config setup depends on the `BIF_CFG_DEV0_EPF1_0_*` layout; interrupt setup depends on MSI/MSI-X table/PBA and doorbell offsets; reset and power-state handling depends on BIF reset/D-state offsets; and PCIe link, LTR, DPA, PME, and error paths depend on RCC endpoint/downstream offsets.

## State And Persistence Behavior

The file itself owns no mutable state, allocates no memory, performs no I/O, and persists nothing. The registers it names represent hardware state:

- PCI function identity and configuration state for `DEV0_EPF1`: command/status, class codes, BARs, ROM, PM capability, PCIe capability, MSI/MSI-X, AER, enhanced BAR, power-budget, DPA, ACS, PASID, and ARI fields.
- GPUIOV vendor-specific scheduler and interrupt state in the EPF0 tail: visible GFX scheduler dwords and ENGA/ENGB interrupt enable/status registers.
- PCIe/RCC link and endpoint state: VDM, requester ID restore, LTR, arbitration, DPA, PME, error controls, link speed controls, downstream config controls, and PFC restore/sticky/aux power settings.
- MSI-X state: 256 vector address/data/control entries and 8 pending-bit-array dwords. Vector control fields may mask delivery, while PBA bits reflect pending interrupts.
- Strap state: configuration straps for ports, BIF, endpoint functions, and devices. These are generally sampled/configuration-like hardware state and may be reset- or firmware-dependent.
- Reset and power transition state: hard/self resets, FLR, D3hot-to-D0 reset controls, interrupt status/mask registers, and D-state value registers.
- Doorbell and routing aperture state: `DOORBELL0_CTRL_ENTRY_*` ranges and per-PF/VF AID/XCC/NBIF/ATHUB/IH/HDP base-address maps that route queue notifications or function apertures.

Persistence across GPU reset, FLR, D3 transitions, BACO, suspend/resume, or firmware handoff is not described by this header. Those semantics belong to the hardware and driver sequences. A stale generated offset can still create persistent driver behavior because compiled code will keep targeting the wrong register until the header is regenerated and rebuilt.

## Dependencies And Integration Points

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/nbio_v7_9.c` includes this header and `nbio_7_9_0_sh_mask.h`. It uses NBIO 7.9 register offsets for revision ID, framebuffer access, memory size, HDP remap, doorbell ranges, doorbell aperture enabling, and other NBIO setup paths.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/ras/ras_mgr/amdgpu_ras_nbio_v7_9.c` includes the same offset/mask pair for NBIO RAS interrupt integration, although the visible functions in that file mostly register dummy interrupt handlers because the relevant BIFring path is disabled by hardware behavior.
- The matching `nbio_7_9_0_sh_mask.h` supplies bit positions and masks. Offset macros in this chunk identify dword/register locations; safe field manipulation requires the sibling mask/shift header.
- The AMDGPU SOC15 register-base infrastructure supplies the meaning of base index `8`. These constants should not be used as flat physical addresses.
- Adjacent generated NBIO headers such as `nbio_7_2_0_offset.h`, `nbio_7_7_0_offset.h`, and `nbio_7_11_0_offset.h` define similar families with generation-specific offsets and base indices. Porting code across ASIC generations must use the header selected by the owning NBIO implementation.

## Risks And Edge Cases

- The chunk starts inside an already-open EPF0 config block and ends inside the BIF miscellaneous block. Merge/reconciliation must preserve the previous block context for the GPUIOV tail and the next block continuation for remaining PF/VF base-address or misc registers.
- All visible base indices are `8`; using these numeric offsets with a helper expecting another base index can silently address the wrong register window.
- PCI config aliases intentionally share dword offsets. Treating every macro name as a unique physical register would be wrong for command/status, capability/control/status pairs, MSI aliases, packed DPA allocations, ACS/PASID/ARI cap/control pairs, and interrupt-line/pin/grant/latency fields.
- The MSI-X table is large and mechanically regular. Off-by-one vector indexing or stride mistakes can program one vector's address/data/control while the driver believes it has programmed another vector.
- MSI-X vector table and PBA registers are interrupt-critical. Wrong offsets can cause missed interrupts, stale pending bits, vectors delivered to the wrong CPU address/data pair, or stuck masked vectors.
- RCC link, DPA, PME, LTR, requester-ID, and link-speed controls are PCIe behavior controls. Incorrect writes can cause link training failures, broken low-power transitions, ordering/latency regressions, or enumeration problems.
- Strap registers are configuration-sensitive and often reset-sampled. Debug or bring-up code should avoid broad write sweeps across strap ranges unless the hardware programming model explicitly allows it.
- Reset and D-state registers are high blast-radius controls. Misaddressed FLR, D3hot-to-D0, hard reset, or interrupt-mask writes can hang a function, lose device state, or hide recovery events.
- Doorbell and AID/PF/VF base-address registers affect queue notification and virtualization routing. Wrong values can break SDMA/VCN queue wakeups, PF/VF isolation, or per-AID routing.
- Similar symbol families repeat across EPF numbers, device numbers, VF numbers, AID numbers, and XCC instances. Manual edits or cross-generation copy/paste are especially likely to compile cleanly but route to the wrong hardware function.

## Test And Validation Signals

- Build coverage: compile AMDGPU paths that include `nbio_7_9_0_offset.h` and `nbio_7_9_0_sh_mask.h`, especially `amdgpu/nbio_v7_9.c` and `ras/ras_mgr/amdgpu_ras_nbio_v7_9.c`, to catch missing or renamed generated symbols.
- Generated-header consistency: verify each visible `reg*` macro has exactly one matching `reg*_BASE_IDX` macro, and that every visible base index remains the expected value `8`.
- PCI config validation: on matching NBIO 7.9 hardware, decode `DEV0_EPF1` config-space reads using these offsets and the sibling masks; verify identity, BARs, capability chain, PM/PCIe/MSI/MSI-X/AER/enhanced capability offsets, ACS/PASID/ARI presence, and intentional aliasing.
- MSI-X validation: program representative low, middle, and high vectors, including vector 0 and vector 255, then confirm address/data/control and PBA behavior match the four-dword stride and 8-dword PBA layout.
- Doorbell validation: exercise SDMA and VCN queues through `nbio_v7_9.c` doorbell programming paths, including multi-AID offsets, and confirm interrupts/work submissions arrive without spurious routing.
- Reset and power validation: exercise FLR, D3hot-to-D0, suspend/resume, and recovery paths while checking BIF reset interrupt status/mask and D-state value registers.
- PCIe/RCC validation: cover link speed changes, LTR behavior, PME/DPA paths, requester-ID restore, and AER/error-control behavior under normal operation and controlled PCIe error tests.
- Strap and revision validation: compare strap-derived values and function strap layouts against hardware documentation or known-good register dumps for NBIO 7.9 devices.
- Static cross-version checks: compare repeated EPF, RCC, MSI-X, strap, doorbell, and AID/PF/VF base-address families against adjacent NBIO generated headers to catch accidental use of NBIO 7.2/7.7/7.11 offsets in NBIO 7.9 code.

## Notes For Merge/Reconciliation

- This is a chunk-level report only for `subset-b-003324`; no final per-file report was produced.
- The chunk starts at line 2714 inside the previous `aid_nbio_nbif0_bif_cfg_dev0_epf0_bifcfgdecp` address block, whose marker appears earlier in the file. The visible EPF0 content here is only the GPUIOV/vendor-specific tail.
- The chunk includes a complete `DEV0_EPF1` direct config-space block and complete visible RCC/MSI-X/PBA/SUM/strap/reset blocks, then ends in the middle of the BIF miscellaneous register block after `regAID0_XCC1_PF_BASE_ADDR`.
- Keep this report under `Docs/researches/chunks/`; the merge lane should synthesize the source-file report after all chunks for `nbio_7_9_0_offset.h` are available.
