# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_11_0_sh_mask.h lines 54020-56559

## Purpose

This chunk is part of AMDGPU's generated NBIO 7.11.0 shift/mask header. It defines bit-field geometry for NBIO/BIF/RCC/GDC registers used by the AMDGPU driver to program PCIe endpoint behavior, BIOS and SBIOS scratch registers, BIF interrupt and doorbell handling, HDP coherency flush signaling, PF mailbox registers, power-management controls, and per-engine doorbell range/fence registers.

The file is not executable logic. Its purpose is to provide C preprocessor constants that pair with `nbio_7_11_0_offset.h` register-address macros and AMDGPU register helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, `RREG32_PCIE_PORT`, and `WREG32_PCIE_PORT`.

## Important APIs, Types, and Macros

There are no functions, structs, typedefs, or enums in this range. The public interface is the generated macro pattern:

- `<REGISTER>__<FIELD>__SHIFT`: the field's starting bit.
- `<REGISTER>__<FIELD>_MASK`: the field mask already shifted into register position.

Major register families in this chunk are:

- `RCC_EP_DEV0_1_*` and `RCC_EP_DEV0_2_*`: PCIe endpoint and downstream-port control fields. These cover correctable/nonfatal/fatal/user/misc/power-state interrupt enables and status bits, PASID/prefix/max-payload/TC completion-timeout receive error handling, hidden config-space decode enables for Gen2 through Gen5, LTR message values and requirements, DPA capabilities/control/substate power allocation, PME service timer, TX snoop/relaxed-ordering/TPH controls, requester ID fields, error-reporting disable, and immediate-error-message behavior.
- `BIF_BX0_*` and `BIF_BX1_*`: paired BIF instances with the same register shapes. They expose indirect PCIe index/data windows, SBIOS/BIOS scratch dwords, RLC/VCE/UVD interrupt control fields, GFX MMIO register CAM address/remap/CPL fields, BIF MM indirect access, bus coherency and flush-stall policy, reset and config-register routing controls, IH interrupt dummy-read setup, CLKREQ/PERST/PX/REF/PWRBRK pad controls, BIF feature/atomic controls, BIF doorbell control and doorbell interrupt/RAS status controls, framebuffer read/write enable, BACO entry/exit controls and timers, memory-type control, graphics address LUT control and entries, HDP remap controls, BIF ring-buffer control/base/pointers, mailbox index, and GPUIOV sizing.
- `BIF_BX_PF0_*` and `BIF_BX_PF1_*`: per-physical-function register fields. These include BME status, doorbell self-ring GPA aperture base/control, HDP coherency flush/invalidate control addresses, per-engine HDP flush-only, invalidate-only, flush, and flush-done request masks, PF transaction-pending status, address-LUT bypass, four-dword transmit and receive mailbox buffers, mailbox valid/ack interrupt controls, and compact VM/HV mailbox data/valid/ack bits.
- `RCC_STRAP1_RCC_DEV0_EPF0_STRAP0` and `RCC_STRAP2_RCC_DEV0_EPF0_STRAP0`: endpoint function strap fields for vendor/device identification, revision ID, subsystem vendor/device IDs, class code, function enable, legacy device type, and D1/D2 support. The NBIO 7.11 implementation reads revision ID from this strap family.
- `RCC_DEV0_EPF0_0_RCC_DOORBELL_APER_EN` and `RCC_DEV0_EPF0_0_RCC_CONFIG_MEMSIZE`: device-level doorbell aperture enable and config-space memory-size fields.
- `GDC0_*` and `GDC1_*`: graphics doorbell controller fields. This chunk covers queue FIFO arbitration priorities/modes, doorbell-sent status, per-engine doorbell range `OFFSET` and `SIZE` fields for SDMA0-5, IH, VCN0/1, RLC, CSDMA, and VPE, VCN `NEED_DEDUCT` bits, ATDMA arbitration mode and VC weights, and doorbell fence enables for CP, SDMA, RLC, CSDMA, and VPE.

The macros in this chunk are consumed directly by `drivers/gpu/drm/amd/amdgpu/nbio_v7_11.c`, which includes `nbio_7_11_0_sh_mask.h` and its matching offset header.

## Control Flow and Runtime Behavior

This header has no runtime control flow. The runtime behavior is created by driver code that uses these constants in register read-modify-write operations.

Important implied flows include:

1. NBIO setup uses `BIF_BX1_BIF_FB_EN__FB_READ_EN_MASK` and `BIF_BX1_BIF_FB_EN__FB_WRITE_EN_MASK` to enable or disable memory-controller access through BIF.
2. Doorbell programming uses `GDC0_BIF_CSDMA_DOORBELL_RANGE`, `GDC0_BIF_VPE_DOORBELL_RANGE`, `GDC0_BIF_VCN0_DOORBELL_RANGE`, `GDC0_BIF_VCN1_DOORBELL_RANGE`, and `GDC0_BIF_IH_DOORBELL_RANGE` fields to set a doorbell base offset and range size, or to zero the size when a ring does not use doorbells.
3. Doorbell aperture setup uses `RCC_DEV0_EPF0_0_RCC_DOORBELL_APER_EN__BIF_DOORBELL_APER_EN` and PF self-ring aperture fields to expose CPU/GPU doorbell writes and self-ring behavior.
4. Interrupt setup uses `BIF_BX1_INTERRUPT_CNTL2__IH_DUMMY_RD_ADDR` and `BIF_BX1_INTERRUPT_CNTL` fields to program IH dummy-read and snoop behavior.
5. HDP flush handling uses `BIF_BX_PF1_GPU_HDP_FLUSH_REQ` and `BIF_BX_PF1_GPU_HDP_FLUSH_DONE` offsets and masks to request coherency flushes and wait for the correct CP/SDMA engine completion bits.
6. PCIe indirect accesses use `BIF_BX1_PCIE_INDEX2`, `BIF_BX1_PCIE_DATA2`, `BIF_BX_PF1_RSMU_INDEX`, and `BIF_BX_PF1_RSMU_DATA` addresses from the offset header; this chunk defines field shapes for nearby index/data windows and PF support registers.
7. RAS and virtualization-related flows can use doorbell interrupt status/clear/disable bits, BME-low status bits, mailbox valid/ack fields, VM/HV mailbox fields, and transaction-pending fields.

The header does not enforce ordering. Callers must know when to disable a range before changing it, when to clear status bits, when to wait for HDP flush done, and when writes are safe during reset, BACO, suspend/resume, or SR-IOV transitions.

## State and Persistence

The header owns no state, allocates no memory, performs no I/O, and persists nothing. The represented state lives in NBIO 7.11 hardware registers.

State categories represented here include:

- PCIe endpoint policy state: interrupt enables/status, DPA capability/control/substate allocation, LTR message configuration, PME timer, requester ID, TX/RX error-handling controls, hidden configuration decode enables, and Gen2-Gen5 decode gating.
- Firmware and boot coordination state: SBIOS and BIOS scratch dwords, revision/device/class/subsystem strap fields, and memory-size reporting.
- BIF data-path and ordering state: bus coherency disables/enables, zero-byte enable policy, read/write stall controls, HDP flush stall controls, BIF feature disable bits, atomic outstanding limits, framebuffer read/write enables, BIF transaction pending fields, and address LUT entries/bypass.
- Interrupt and RAS-related state: IH dummy-read configuration, BIF doorbell/RAS/ATHUB interrupt status/clear/disable bits, RAS vector selection, BME-low status/clear bits, and doorbell monitor/intgen settings.
- Power-management state: BACO enable/power-off/mode/auto-exit bits, BACO exit timers, CLKREQB and other pad controls, D-state support straps, and DPA/LTR fields.
- Doorbell and ring-buffer state: global doorbell aperture enable, PF self-ring aperture base/control, GDC per-engine doorbell ranges, doorbell fence enables, GDC doorbell-sent status, BIF ring-buffer base/read/write pointers, and write-pointer host address fields.
- Mailbox state: PF transmit/receive mailbox data dwords, mailbox valid/ack controls, mailbox interrupts, and compact VM/HV mailbox payload/status bits.

Retention across GPU reset, PCI reset, BACO, suspend/resume, FLR, or SR-IOV PF/VF state changes is not described by the header. Those semantics depend on hardware and the AMDGPU initialization paths that rewrite these registers.

## Dependencies and Integration Points

Primary dependencies are adjacent generated NBIO 7.11 files:

- `nbio_7_11_0_offset.h` supplies `reg*` addresses and base indices for the registers whose fields are described here.
- `nbio_7_11_0_default.h`, if used by callers or validation scripts, supplies reset/default values.
- Adjacent chunks of this same `nbio_7_11_0_sh_mask.h` supply fields before `RCC_EP_DEV0_1_EP_PCIE_INT_CNTL` and after `GDC1_BIF_DOORBELL_FENCE_CNTL`.

Concrete AMDGPU integration points observed in the source tree include:

- `amdgpu/nbio_v7_11.c` includes this header and uses its fields for MC access enable, doorbell range programming, VCN/VPE/CSDMA/IH doorbells, doorbell aperture enable, self-ring aperture setup, IH control, HDP flush register offsets/masks, memory-size reads, revision ID reads, and register remapping.
- `amdgpu/nbio_v7_7.c`, `amdgpu/nbio_v7_9.c`, `amdgpu/nbio_v7_2.c`, and `amdgpu/nbif_v6_3_1.c` use similarly named BIF/GDC/HDP doorbell and flush fields, giving useful comparison points for expected register geometry and behavior.
- Display resource code references `BIF_BX1_BIOS_SCRATCH_*` offsets for BIOS scratch state, so the scratch fields in this chunk are part of broader display/firmware integration even when the exact mask macros are simple full-dword definitions.
- SR-IOV and VM/HV mailbox paths in older NBIO/NBIF generations use the PF mailbox register family represented here. The field layout supports message-buffer dwords, valid/ack bits, and valid/ack interrupt enables.

Because this is generated hardware metadata, integration is by exact symbol naming. A caller must use a field macro whose register name matches the address macro passed to the SOC15/PCIE-port accessor.

## Risks

- Incorrect shifts or masks can silently program the wrong hardware bit. In this chunk, that can break PCIe error reporting, LTR/DPA power behavior, hidden config decode, doorbell routing, HDP coherency flush completion, interrupt delivery, or BACO exit behavior.
- `BIF_BX0` and `BIF_BX1`, and `PF0` and `PF1`, are near-duplicate register families. Using a PF0 mask with a PF1 address, or a BIF_BX0 field with a BIF_BX1 address, can compile but target the wrong instance.
- NBIO 7.11 code uses `PF1` for HDP flush, self-ring aperture, PCIe index/data, and memory-controller access in several places. Porting code from older generations that use PF0 can introduce subtle instance-selection bugs.
- Doorbell range fields have compact masks: offsets use bits 11:2 and most sizes use bits 20:16, while CSDMA uses a wider size field. Bad range values can overlap engines or disable rings.
- VCN doorbell range registers include `NEED_DEDUCT`, but the active NBIO 7.11 helper only programs `OFFSET` and `SIZE`. Callers changing VCN doorbell behavior need to preserve that bit correctly during read-modify-write.
- HDP flush request/done registers expose CP0-CP9, SDMA0/1, and many reserved engine bits. Reusing reserved bits as if they were new engines without matching hardware documentation can create false waits or missed flushes.
- Doorbell interrupt/RAS status registers combine status, clear, disable, and set-on-ring-enable bits. Write-one-to-clear and disable semantics must be handled carefully by driver code; this header only provides masks.
- BACO, DPA, LTR, PME, and CLKREQ/pad fields are power-management sensitive. Incorrect values can create resume, link-training, or low-power-state failures that may only appear under suspend/resume, runtime PM, or platform firmware flows.
- The chunk boundary splits the generated GDC1 family: it contains all of `GDC1_BIF_DOORBELL_FENCE_CNTL`, while `GDC1_S2A_MISC_CNTL` begins in the next chunk. Merge/reconciliation should not treat the absence of GDC1 S2A fields here as a source omission.

## Test and Validation Signals

Useful validation signals are mostly generated-header consistency checks plus hardware bring-up coverage:

- Build AMDGPU configurations that include `amdgpu/nbio_v7_11.c` to catch missing or malformed macros from this header.
- Mechanically verify every complete register in lines 54020-56559 has paired `__SHIFT` and `_MASK` definitions for each field. The only intentional chunk-boundary continuation is the next register after this chunk, `GDC1_S2A_MISC_CNTL`.
- Cross-check register names against `nbio_7_11_0_offset.h` so field macros used by `REG_SET_FIELD` and `REG_GET_FIELD` have matching address macros.
- Compare repeated `BIF_BX0` versus `BIF_BX1`, `PF0` versus `PF1`, `RCC_EP_DEV0_1` versus `RCC_EP_DEV0_2`, and `GDC0` versus `GDC1` field layouts for symmetry, allowing expected differences such as GDC0 having `S2A_MISC_CNTL` within this chunk while GDC1's starts in the next chunk.
- Exercise NBIO 7.11 boot and resume paths on supported ASICs and confirm memory-controller access, register remapping, HDP flush request/done polling, and interrupt dummy-read setup behave correctly.
- Validate CSDMA, VPE, VCN0/1, and IH doorbell programming by checking that ring writes reach the intended engine and that disabling a ring zeros only the `SIZE` field while preserving unrelated bits.
- Validate doorbell aperture and self-ring aperture programming with real doorbell writes, including high/low 64-bit base programming and aperture enable/disable transitions.
- Validate HDP coherency by issuing CP/SDMA work that requires HDP flushes and observing that the correct `GPU_HDP_FLUSH_DONE` mask bits are set before software proceeds.
- Run SR-IOV or virtualization mailbox coverage where applicable: mailbox valid/ack fields and interrupt enables should transition as expected without losing messages.
- Run RAS/doorbell interrupt tests or fault injection where available to confirm doorbell interrupt status, clear, and disable bits are read and written with the intended masks.

## Chunk Boundary Notes

This work item starts at `RCC_EP_DEV0_1_EP_PCIE_INT_CNTL`, after the previous endpoint PCIe section, and ends after the complete `GDC1_BIF_DOORBELL_FENCE_CNTL` register. The next line in the source starts `GDC1_S2A_MISC_CNTL`, so GDC1 S2A arbitration and 64-bit doorbell support fields belong to the following chunk, not this one.
