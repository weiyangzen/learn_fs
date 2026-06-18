# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_2_3_sh_mask.h lines 19550-21952

## Scope

This chunk is a generated AMDGPU NBIO 2.3 register shift/mask header segment. It contains preprocessor constants only: 2,159 `#define` entries over 221 register names, with 1,076 `__SHIFT` macros and 1,083 `_MASK` macros in the requested line range. There are no C functions, structs, enums, executable branches, or storage objects in this chunk.

The range starts in the middle of `NBIF_SDP_VWR_VCHG_DIS_CTRL`: the shift definitions and the register comment are just before line 19550, while this chunk contains only its mask definitions. The range ends in the middle of `BIF_CFG_DEV0_EPF0_PCIE_DPA_ENH_CAP_LIST`: the shifts and `CAP_ID_MASK` are present, but `CAP_VER_MASK` and `NEXT_PTR_MASK` continue after line 21952. The merge lane should combine adjacent chunks before treating either boundary register as complete.

## Purpose

`nbio_2_3_sh_mask.h` supplies bitfield locations for NBIO/NBIF registers on AMD GPUs using the NBIO 2.3 IP block. The matching `nbio_2_3_offset.h` file names the MMIO/config offsets; this file names each register field's bit shift and mask. Driver code uses these macros through AMDGPU register helpers such as `REG_SET_FIELD()`, `REG_GET_FIELD()`, `WREG32_FIELD15()`, `RREG32_SOC15()`, `WREG32_SOC15()`, `RREG32_PCIE()`, and `WREG32_PCIE()` so code can program PCIe/NBIO hardware without hard-coding raw bit numbers.

This chunk covers several related NBIO surfaces:

- SDP virtual-wire voltage-change and reset controls for endpoint functions and a downstream switch port.
- BIFC A2S credit, tag, response-reorder, and virtual-channel mapping controls.
- RCC PFC blocks for AMDGFX, AMDGFXAZ, USB, and PD controller endpoints, including LTR, PME restore, sticky AER restore, TLP header/prefix restore, and auxiliary-power override fields.
- BIF reset, function-level reset, D3hot-to-D0 reset, instance-reset, interrupt status/mask, and PF/VF reset trigger fields.
- BIF link/RAS leaf control and status fields, plus IOHUB RAS interrupt wiring.
- SWUS SUM index/data fields.
- Device 0 endpoint function 0 PCI configuration-space fields from vendor/device IDs through PCIe, MSI, MSI-X, VC, serial-number, AER, enhanced BAR, power-budget, and the beginning of DPA enhanced capability fields.

## Important Macro Families

The macros follow the generated register-field naming convention:

- `REGISTER__FIELD__SHIFT` gives the bit position used to align a field value.
- `REGISTER__FIELD_MASK` gives the field's already-shifted bit mask.
- One-bit fields use masks such as `0x00000001L`; multi-bit fields use wider masks such as `0x000003FFL`, `0xFFF00000L`, or `0xFFFFFFFFL`.

The chunk's main families are:

- `NBIF_SDP_VWR_VCHG_*`: per-function `F0`-`F7` and `SWDS_P0` disable, reset-override-enable, reset-override-value, and trigger bits. These model sideband virtual-wire voltage-change/reset signaling.
- `BIFC_A2S_*`: SDP disconnect hysteresis, read-response error mapping, response selection, write-chain disable, read/write WRR weights, response reorder controls, write/read tag minimums, VC tag allocations, control-class mappings, and completion-buffer reservations.
- `RCC_PFC_*`: repeated PFC register layouts for AMDGFX, AMDGFXAZ, USB, and PD controller blocks. Each exposes snoop/nonsnoop LTR values and scales, PME restore enable/status, sticky restore status for PCIe errors, restored TLP header dwords, restored TLP prefix, and auxiliary current/power-detected override fields.
- `HARD_RST_CTRL`, `SELF_SOFT_RST`, `SELF_SOFT_RST_2`, and `BIF_RST_MISC_CTRL*`: reset-enable, sticky-reset, privileged-reset, core reset, strap reload, link reset, FLR auto-clear, grace timeout, DMA dummy response, timer scale, and PME turnoff mode fields.
- `DEV0_PF<n>_FLR_RST_CTRL` and `DEV0_PF<n>_D3HOTD0_RST_CTRL`: PF0 has the widest FLR control surface, including VF/soft-PF controls; PF1-PF7 carry PF reset, sticky, privilege, FLR grace, and dummy-response fields. D3hot/D0 reset control repeats across PF0-PF7.
- `BIF_*_INTR_STS`, `BIF_*_INTR_MASK`, `BIF_PF_FLR_RST`, and `BIF_PF0_VF_FLR_*`: status/mask/trigger fields for instance reset, PF FLR, D3hot/D0, power events, PF D-state events, and PF0 VF FLR events for VF0-VF30 plus soft-PF.
- `BIFL_RAS_*`: central RAS controls/status and five leaf control/status pairs for poison, parity, receive-error event detection, error-event generation/propagation, egress-stall generation/propagation, and RAS interrupt enable/status.
- `BIF_CFG_DEV0_EPF0_*`: PCI config-space field masks for the endpoint's base identification, command/status, BARs, PM capability, PCIe capability, device/link control and status, MSI/MSI-X, vendor-specific and VC capabilities, AER status/mask/severity/logging, enhanced BAR sizing, and power-budget metadata.

## Control Flow

This header has no runtime control flow. It is compile-time data consumed by driver code that performs read-modify-write sequences against hardware registers.

Observed integration code includes:

- `drivers/gpu/drm/amd/amdgpu/nbio_v2_3.c`, which includes this header with `nbio_2_3_offset.h` and programs NBIO doorbell apertures, interrupt control, memory-controller access, HDP flush remapping, clock gating, ASPM, and LTR.
- In `nbio_v2_3_program_ltr()`, the driver sets `BIF_CFG_DEV0_EPF0_DEVICE_CNTL2__LTR_EN_MASK` after programming TX LTR control and clearing the LTR disable strap.
- In `nbio_v2_3_program_aspm()`, the driver clears `BIF_CFG_DEV0_EPF0_DEVICE_CNTL2__LTR_EN_MASK` while staging ASPM programming, writes a raw PCIe LTR capability value, and later re-enables LTR when the PCI path supports it.
- `drivers/gpu/drm/amd/amdgpu/mxgpu_nv.c` includes the same header and uses NBIO mailbox register fields indirectly through generated aliases to exchange VF/PF messages, poll acknowledgements, service FLR notifications, and schedule RAS/reset work.
- `drivers/gpu/drm/amd/pm/swsmu/smu11/navi10_ppt.c` and `sienna_cichlid_ppt.c` include the header for NBIO register definitions used by SMU power-management paths, though the inspected direct references are concentrated in NBIO and MxGPU code.

## State and Persistence

The macros themselves do not store state. They describe bit positions for state stored in hardware registers:

- Reset/FLR/D3hot fields control or report hardware reset state. Some bits explicitly preserve sticky state across reset classes, and misprogramming them can change what survives FLR, D3hot/D0, link reset, or hard reset.
- Interrupt status and mask registers hold live hardware event state for reset, power, D-state, and PF/VF FLR events. Status handling is typically clear-on-write or hardware-defined, so masks must match the hardware manual exactly.
- AER and RCC PFC sticky-restore fields persist PCIe error state, TLP headers, and TLP prefixes so software or firmware can reconstruct faults after reset or power transitions.
- PCI config fields such as command, status, BARs, PM, PCIe device/link controls, MSI/MSI-X, VC, AER, power-budget, and DPA capabilities represent device-visible PCI state. Some fields are writable by the OS or firmware; others are capability/status surfaces populated by hardware.
- BIFC A2S credit/tag/VC/response controls affect in-flight fabric behavior and arbitration rather than kernel memory. Their effects persist until reset or later reprogramming.
- RAS leaf and central controls/status expose error-detection, poison/parity handling, stall generation, propagation, and interrupt-routing state for the BIF link.

Because this is a register contract, the persistence boundary is the GPU hardware function, not process memory. A wrong mask or shift can make a correct-looking `REG_SET_FIELD()` write alter a different bit until the relevant register is restored or the GPU/function is reset.

## Dependencies

This chunk depends on the AMDGPU SOC15 register model:

- `nbio_2_3_offset.h` provides the `mm*`, `reg*`, and base-index constants for the same register names.
- `nbio_2_3_default.h` provides generated default values for the same IP generation.
- `soc15.h` and AMDGPU register helpers combine offsets, base indices, and masks/shifts into actual MMIO or PCIe config-space reads/writes.
- The register names must stay synchronized with the ASIC register database for NBIO 2.3 and with firmware expectations for reset, RAS, PCIe, and SR-IOV behavior.
- Consumers are mostly in the AMDGPU kernel driver: `nbio_v2_3.c`, `mxgpu_nv.c`, and SMU 11 PPT files for Navi/Sienna-era ASICs.

No external library ABI is defined here. The ABI-like contract is between generated headers, kernel driver code, firmware, and the NBIO hardware layout.

## Integration Points

The key integration surface is the AMDGPU NBIO layer:

- NBIO callback implementations in `nbio_v2_3.c` use this family of masks to set fields while preserving neighboring bits in the same register. This is especially visible in ASPM/LTR programming, doorbell aperture setup, interrupt control, and power/clock-gating flows.
- PCIe capability masks in `BIF_CFG_DEV0_EPF0_*` line up with Linux PCI concepts: command/status, PM capability, device/link capability/control/status, MSI/MSI-X, AER, VC, enhanced BAR, power budget, and DPA. The driver can use either SOC15-style offsets or SMN/PCIE direct addresses for these registers.
- Reset and FLR field definitions align with virtualization flows. `mxgpu_nv.c` handles host FLR notifications, queues reset work, and exchanges VF/PF mailbox messages; the reset/status/mask definitions in this chunk describe the hardware bits behind those events even when direct references are hidden behind generated mailbox aliases or adjacent offset headers.
- RAS field definitions connect NBIO/BIF link errors to AMDGPU RAS handling. MxGPU mailbox code can request bad pages, receive unrecoverable-error notifications, and schedule reset-domain work when the host reports RAS-related events.
- PFC LTR/PME/sticky-restore fields connect PCIe power-management and error-reporting behavior to endpoint-specific blocks for graphics, USB, and PD controller functions.

## Risks

- Generated-header drift is the main risk. A single incorrect shift or mask can make `REG_SET_FIELD()` preserve the wrong bits or write the wrong field, causing PCIe link, reset, RAS, AER, interrupt, or power-management failures.
- Boundary incompleteness matters for this chunk. `NBIF_SDP_VWR_VCHG_DIS_CTRL` and `BIF_CFG_DEV0_EPF0_PCIE_DPA_ENH_CAP_LIST` are partial in this work item; per-file analysis should reconcile adjacent chunks before claiming complete coverage.
- Similar field names in status, mask, and severity registers can be confused. For example, AER has uncorrectable status, mask, severity, correctable status, and correctable mask registers with nearly parallel field names but different semantics.
- PF/VF reset fields are security and availability sensitive under SR-IOV. Incorrect FLR, D3hot/D0, or VF reset masks can leave transactions pending, fail to isolate virtual functions, or trigger broader reset effects than intended.
- PCIe config and BAR enhanced capability fields are OS-visible. Wrong masks for BAR size, MSI/MSI-X, AER, or link-control fields can break enumeration, interrupt delivery, error recovery, or link training.
- RAS leaf controls can amplify or hide hardware faults. Misprogrammed poison/parity/stall/error-event propagation fields can suppress expected interrupts or generate persistent stalls.
- Many macros are not directly referenced in the current source tree. Removing or "simplifying" apparently unused generated definitions would be risky because they serve future ASIC enablement, debug tooling, firmware-aligned register access, and indirect macro expansion.

## Test Signals

Useful validation signals are mainly build-time and hardware/runtime signals:

- Compile AMDGPU configurations that include `nbio_v2_3.c`, `mxgpu_nv.c`, `navi10_ppt.c`, and `sienna_cichlid_ppt.c`; undefined or renamed field macros should fail at build time where directly referenced.
- Run generated-header consistency checks against `nbio_2_3_offset.h` and the ASIC register database: every field should have the expected shift/mask pair, and every mask should match the documented width at its shift.
- Exercise ASPM/LTR paths on hardware with and without `pdev->ltr_path`; verify link power-management behavior and absence of PCIe AER regressions.
- Test PF and SR-IOV VF reset flows: FLR notifications, reset-domain work scheduling, `IDH_FLR_NOTIFICATION_CMPL` polling, and GPU init/fini/reset mailbox handshakes should complete without timeouts.
- Validate MSI/MSI-X interrupt delivery and masking for the endpoint after programming MSI/MSI-X capability registers.
- Trigger or inject PCIe AER/RAS events where supported and verify status, mask, severity, sticky restore, TLP header/prefix logging, RAS interrupt, and bad-page/unrecoverable-error handling paths report expected state.
- Exercise doorbell, HDP flush, and command submission smoke tests after reset and power transitions to catch NBIO register programming errors that may not appear at compile time.
