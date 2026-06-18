# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_2_3_sh_mask.h lines 17172-19549

## Scope

This chunk is a generated AMDGPU NBIO 2.3 register shift/mask header segment. It contains preprocessor constants only: 2,170 `#define` macros across 194 register groups, split almost evenly between `__SHIFT` and `_MASK` definitions. There are no functions, types, structs, enums, storage definitions, or executable C control flow in this range.

The line range starts in the tail of `RCC_STRAP1_RCC_DEV0_EPF0_STRAP4`, covers a large set of PCIe endpoint strap fields for functions on device 0 and devices 1-2, then covers NBIO/RCC port control, endpoint and downstream PCIe control, BIF miscellaneous controls, DMA attribute overrides, error logs, performance counters, power-gating controls, SMN master controls, virtual-wire controls, and ends in `NBIF_SDP_VWR_VCHG_DIS_CTRL`.

## Purpose

The header provides bit positions and masks for NBIO/NBIF registers used by Navi-era AMD GPUs with NBIO IP version 2.3. The matching offset header names the register addresses; this file names the fields inside those 32-bit registers. Driver code uses these macros with `RREG32_*()` and `WREG32_*()` read/modify/write sequences so it can set or test individual hardware bits without embedding numeric constants in C code.

The chunk's main hardware surfaces are:

- PCIe function straps for endpoint functions: device ID, revision ID, function enablement, power-state support, PASID, ATS, ACS, AER, DPA, VC, MSI/MSI-X, PM, FLR, atomics, class code, subsystem IDs, BAR/aperture sizing, ROM aperture, TPH, resize BAR support, SR-IOV VF aperture sizing, and VF mapping.
- RCC port controls: VDM support, bus/master disable gates, root/error-log handling, max payload/read request sizing, link-down entry/exit, common link PM/LTR controls, endpoint requester ID restore, multi-host arbitration, and PCIe margining capability parameters.
- Endpoint/downstream PCIe controls: interrupt enables/status bits, unsupported-request handling, LTR transmit parameters, DPA capability and power allocation, PME, TX/RX error handling, link speed straps, and downstream strap controls.
- BIF miscellaneous controls: interrupt-line polarity/enable, outstanding virtual-channel allocations, DMA/GMI/GSI behavior toggles, BME and RCC/BIH BME error logs, DMA transaction attribute overrides, PASID checks/status, SDP controls, performance counter controls and values, power-gating and deep-sleep controls, SMN behavior, and virtual-wire trigger/reset controls.

## Important Macro Families

The endpoint strap definitions repeat a common PCIe configuration pattern across physical functions:

- `RCC_STRAP1_RCC_DEV0_EPF0_STRAP5`, `STRAP8`, `STRAP9`, and `STRAP13` finish function 0 fields in this chunk. The key fields include subsystem vendor ID, doorbell/FB/register/ROM/VF aperture sizes, VF MSI capability, SR-IOV VF mapping mode, outstanding page request capability, BAR compliance, ROM BAR chicken bit, VF register protection disable, and class code.
- `RCC_STRAP1_RCC_DEV0_EPF1_STRAP0/2/3/4/5/6/7/10/11/12/13` provide the complete function 1 strap set. This is the fullest strap group in the chunk and includes PASID/ATS/ACS/AER, DPA, MSI/MSI-X, power management, FLR/PME, BAR and ROM apertures, TPH, and resize BAR support for apertures 1-3.
- `RCC_DEV0_EPF2_STRAP*` through `RCC_DEV0_EPF6_STRAP*` define similar strap sets for functions 2-6, with some functions exposing fewer aperture or TPH fields than function 1.
- `RCC_DEV1_EPF0_STRAP*` and `RCC_DEV2_EPF0_STRAP*` repeat the device 1 and device 2 function 0 strap surfaces, including function enablement, PASID capability, interrupts, FLR/PME, apertures, and class code.

The RCC and PCIe port-control blocks are grouped by address block comments:

- `nbio_nbif0_rcc_dev0_RCCPORTDEC` contains `RCC_DEV0_1_RCC_*` fields for VDM support, bus control, feature workaround/compatibility controls, link entry/exit, LTR, multi-host arbitration, and PCIe margining parameters.
- `nbio_nbif0_rcc_ep_dev0_RCCPORTDEC` contains `RCC_EP_DEV0_1_*` endpoint-side PCIe fields: scratch, control, interrupt enable/status, RX/TX controls, LTR fields, DPA capability/latency/control/power allocation, PME, error controls, and link speed.
- `nbio_nbif0_rcc_dwn_dev0_RCCPORTDEC` and `nbio_nbif0_rcc_dwnp_dev0_RCCPORTDEC` contain downstream-side equivalents for reserved/scratch/control/config/RX/bus/cfg/strap/error/link-speed/LTR-message fields.

The BIF miscellaneous block is the densest part:

- `BIFC_MISC_CTRL0` and `BIFC_MISC_CTRL1` expose behavior toggles for virtual wire unit-ID checks, DMA/GSI/GMI ordering, atomic checks, SR-IOV VF/PF behavior, PCIe capability protection, D-state/PME behavior, poison/ACS/unsupported-command reporting, BME-drop handling, SDP data forcing, and GMI message block-level selection.
- `BIFC_BME_ERR_LOG` and `BIFC_RCCBIH_BME_ERR_LOG0` define per-function status and clear bits for DMA/RCCBIH activity while bus mastering is low.
- `BIFC_DMA_ATTR_OVERRIDE_DEV0_F0_F1`, `_F2_F3`, `_F4_F5`, and `_F6_F7` define paired per-function fields for ID-based ordering, relaxed ordering, snoop/no-snoop, and block-level override behavior.
- `BIF_ATOMIC_ERR_LOG_DEV0_F0` through `_F7`, `BIF_DMA_MP4_ERR_LOG`, `BIF_PASID_ERR_LOG`, and `BIF_PASID_ERR_CLR` define latched error and explicit clear bits for atomic and PASID-related failures.
- `BIFC_PERF_CNTL_0`, `BIFC_PERF_CNTL_1`, and the four `BIFC_PERF_CNT_*` value registers define enable/reset/select fields and counter values for MMIO and DMA read/write performance observations.
- `NBIF_PGMST_CTRL`, `NBIF_PGSLV_CTRL`, `NBIF_PG_MISC_CTRL`, `NBIF_MGCG_CTRL_LCLK`, and `NBIF_DS_CTRL_LCLK` define NBIF power-gating, medium-grain clock-gating, and LCLK deep-sleep controls.
- `SMN_MST_CNTL0`, `SMN_MST_CNTL1`, and `SMN_MST_EP_CNTL1` through `SMN_MST_EP_CNTL5` define SMN arbitration, zero byte-enable read/write handling, posted-mask behavior, multi-transaction-ID disable bits, and error-response data behavior for upstream, downstream, and endpoint PF paths.
- `NBIF_VWIRE_CTRL`, `NBIF_SMN_VWR_VCHG_DIS_CTRL`, `NBIF_SMN_VWR_VCHG_RST_CTRL0`, `NBIF_SMN_VWR_VCHG_TRIG`, `NBIF_SMN_VWR_WTRIG_CNTL`, `NBIF_SMN_VWR_VCHG_DIS_CTRL_1`, and `NBIF_SDP_VWR_VCHG_DIS_CTRL` define SMN/SDP virtual-wire disable, reset-default, trigger, write-trigger, and differential-detect behavior.

## Control Flow

There is no runtime control flow in this header. Runtime control flow is in users that include this generated mask header with `nbio_2_3_offset.h`.

`drivers/gpu/drm/amd/amdgpu/nbio_v2_3.c` is the primary in-tree consumer. It includes this header and uses masks from the same generated register family in read/modify/write sequences for NBIO setup. One direct use from this chunk is `NBIF_MGCG_CTRL_LCLK__NBIF_MGCG_REG_DIS_LCLK_MASK` in `nbio_v2_3_program_aspm()`: the code reads `smnNBIF_MGCG_CTRL_LCLK`, sets the register-disable clock-gating bit, and writes the register only if the value changed. The same source also programs PCIe/ASPM/LTR, interrupt, doorbell, HDP flush, and SR-IOV-related NBIO state with other NBIO 2.3 macros from adjacent chunks.

`drivers/gpu/drm/amd/amdgpu/mxgpu_nv.c` includes this header for the NBIO 2.3 virtualization register surface. Even where this exact chunk is not directly referenced by name, its PASID, doorbell, interrupt, atomic-error, and virtual-wire definitions describe the same PF/VF coordination and error-state hardware used by MxGPU paths.

`drivers/gpu/drm/amd/pm/swsmu/smu11/navi10_ppt.c` and `sienna_cichlid_ppt.c` include the NBIO 2.3 offset and mask headers so SMU power-management code can reference NBIO register definitions. Display resource code includes the offset header but not this mask header.

## State and Persistence

The header itself has no mutable state. Its macros describe hardware register state with different persistence characteristics:

- Strap fields describe boot/configuration state consumed by PCIe configuration and capability presentation. Some strap-write controls, such as `NBIF_STRAP_WRITE_CTRL__NBIF_STRAP_WRITE_ONCE_ENABLE_MASK`, indicate write-once behavior where an incorrect program sequence can survive until reset.
- Interrupt, error-log, PASID, atomic, BME, and performance-counter registers expose live or latched hardware state. Several error-log registers provide separate status bits in the low halfword and clear bits in the high halfword, so software must preserve the status/clear semantics when writing.
- Doorbell, aperture, VF mapping, DMA attribute, SMN, virtual-wire, power-gating, and clock-gating controls persist as programmed hardware configuration until changed by the driver, firmware, PF/hypervisor, or device reset.
- Power-management and clock-gating fields can affect subsequent register access timing and availability, especially `NBIF_PGMST_CTRL`, `NBIF_PG_MISC_CTRL`, `NBIF_MGCG_CTRL_LCLK`, and `NBIF_DS_CTRL_LCLK`.

Because these masks are compile-time constants, any incorrect bit assignment becomes a runtime hardware programming error in every driver build that consumes the generated header.

## Dependencies

This chunk depends on the AMDGPU SOC15/NBIO register-access conventions:

- Matching register offset macros live in `nbio_2_3_offset.h`; this file only supplies field masks and shifts.
- Consumers combine offsets and masks through helpers such as `RREG32_SOC15()`, `WREG32_SOC15()`, `RREG32_PCIE()`, and `WREG32_PCIE()`.
- Register update helpers typically read a 32-bit register, clear a field with `~FIELD_MASK`, set field bits shifted by `FIELD__SHIFT`, and write the result back.
- Field names and bit positions must stay synchronized with AMD's generated ASIC register database, reset/default headers, firmware expectations, PCIe capability layout, and SR-IOV PF/VF model for NBIO 2.3.

The chunk also has cross-generation neighbors. Similar field families appear in `nbif_6_3_1_sh_mask.h` and later `nbio_7_2_0_sh_mask.h`, but field sets and bit positions are not guaranteed identical. Code must include the versioned header matching the ASIC IP block.

## Integration Points

The main integration point is the AMDGPU NBIO layer:

- NBIO bring-up and power-management callbacks in `nbio_v2_3.c` use these masks to program ASPM/LTR behavior, clock gating, doorbell ranges, HDP flush behavior, interrupt handling, and register-remap behavior.
- PCIe capability presentation and SR-IOV behavior depend on the strap masks in this chunk. Misstating PASID, ATS, ACS, AER, MSI/MSI-X, FLR, BAR, or VF aperture fields can change what capabilities the function exposes to the OS or hypervisor.
- Error reporting and RAS/debug paths depend on the BIFC, atomic, PASID, and PCIe error-log masks to distinguish status bits from write-one-clear bits.
- Virtualization integration depends on the per-function fields in `BIFC_DMA_ATTR_OVERRIDE_*`, BME/PASID/atomic logs, doorbell/VF aperture straps, and virtual-wire controls; these fields help separate PF/VF behavior and coordinate PF/VF communication.
- Power-management integration depends on NBIF power-gating, deep-sleep, and LCLK clock-gating fields, including the directly used `NBIF_MGCG_CTRL_LCLK__NBIF_MGCG_REG_DIS_LCLK_MASK`.

## Risks

- Hardware contract drift: this is generated register data. A wrong mask or shift can program the wrong bit while still compiling cleanly.
- Read/modify/write hazards: many registers contain unrelated fields. Using a stale mask, failing to preserve reserved bits, or confusing a mask with a shifted value can alter adjacent hardware behavior.
- Write-one-clear confusion: BME, atomic, DMA, and PASID error-log registers include clear bits separate from status bits. Treating the whole register as ordinary persistent control state can accidentally clear diagnostics or fail to clear latched errors.
- Virtualization sensitivity: SR-IOV VF aperture, doorbell, PASID, BME, and virtual-wire fields sit on PF/VF boundaries. Bad programming can cause guest-visible failures, mailbox timeouts, interrupt loss, or isolation problems.
- Power-state sensitivity: NBIF clock-gating and power-gating bits affect register access and link behavior. Incorrect settings can produce intermittent failures that depend on ASPM, D-state, or idle timing.
- Chunk-boundary risk: this work item begins in the middle of `RCC_STRAP1_RCC_DEV0_EPF0_STRAP4` and ends before `NBIF_SDP_VWR_VCHG_DIS_CTRL` is complete. The final per-file document must reconcile adjacent chunks before claiming complete coverage of those two register groups.

## Test Signals

Useful validation signals are mostly compile-time, generated-header consistency, and hardware/runtime tests:

- Build AMDGPU configurations that include `nbio_v2_3.c`, `mxgpu_nv.c`, `navi10_ppt.c`, and `sienna_cichlid_ppt.c`; undefined or conflicting macros catch include/version drift.
- Run generated-header consistency checks: every field should generally have one `__SHIFT` and one `_MASK`, masks should align with shifts and field widths, and repeated per-function blocks should differ only by function/device naming where expected.
- Compare selected fields against the matching NBIO 2.3 register database and `nbio_2_3_offset.h` register names, especially chunk-boundary registers and repeated `DEV0_F0` through `DEV0_F7` error-log/override groups.
- Exercise PCIe probe/resume paths with ASPM enabled and disabled; the direct `NBIF_MGCG_CTRL_LCLK` programming path should not break link entry/exit or register access.
- Exercise SR-IOV PF/VF probe, reset, mailbox/access-request, doorbell, MSI/MSI-X, PASID, and FLR paths. Failures here are strong signals of wrong strap, aperture, interrupt, virtual-wire, or error-clear fields.
- Exercise RAS/debug paths that read and clear BIFC, PASID, atomic, and DMA error logs; expected status bits should latch and clear without disturbing unrelated fields.
- Exercise power-management suspend/resume and idle workloads; NBIF power-gating, deep-sleep, and clock-gating fields should not produce hangs, missing interrupts, or stale HDP/SMN behavior.
