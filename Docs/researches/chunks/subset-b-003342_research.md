# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_9_0_sh_mask.h lines 37219-38900

## Scope

This chunk is the tail of the generated AMD NBIO 7.9.0 shift/mask header. It contains C preprocessor constants only: bit-position `__SHIFT` macros and bit-field `MASK` macros for NBIO/BIF/RCC registers. The range begins with the final four masks for the VF2 RCC MSI-X pending-bit array, then covers the complete repeated virtual-function field definitions for `DEV0_EPF0` VF3 through VF7, and ends at the header guard's closing `#endif`.

The source is part of AMDGPU's generated register database under `drivers/gpu/drm/amd/include/asic_reg/nbio`. It defines no executable code, functions, types, storage, locks, callbacks, or direct register access helpers. Its role is to describe field layouts for register addresses supplied by companion offset headers.

## Purpose and Register Families

The macros describe bit layouts for SR-IOV virtual-function register windows in NBIO 7.9.0 hardware. For each VF3 through VF7, the chunk repeats the same register families with the VF number encoded in the macro name:

- `BIF_BX_DEV0_EPF0_VF<n>_BIF_BME_STATUS`: bus-master enable status, including `DMA_ON_BME_LOW` and a clear bit at bit 16.
- `BIF_BX_DEV0_EPF0_VF<n>_BIF_ATOMIC_ERR_LOG`: unsupported or invalid PCIe atomic operation flags plus corresponding clear bits at bits 16-19.
- `DOORBELL_SELFRING_GPA_APER_BASE_HIGH`, `_BASE_LOW`, and `_CNTL`: doorbell self-ring guest-physical aperture base and enable/mode/size fields.
- `HDP_REG_COHERENCY_FLUSH_CNTL`, `HDP_MEM_COHERENCY_FLUSH_CNTL`, `HDP_MEM_COHERENCY_FLUSH_ONLY_CNTL`, and `HDP_MEM_COHERENCY_INVALIDATE_ONLY_CNTL`: one-bit HDP register/memory coherency control fields.
- `GPU_HDP_FLUSH_REQ` and `GPU_HDP_FLUSH_DONE`: one bit per request/completion source, covering CP0-CP9, SDMA0-SDMA1, and reserved engine bits through bit 31.
- `BIF_TRANS_PENDING`: master and slave transaction-pending status bits.
- `NBIF_GFX_ADDR_LUT_BYPASS`: a one-bit graphics address LUT bypass field.
- `MAILBOX_MSGBUF_TRN_DW0..DW3` and `MAILBOX_MSGBUF_RCV_DW0..DW3`: full 32-bit transmit and receive mailbox data words.
- `MAILBOX_CONTROL` and `MAILBOX_INT_CNTL`: transmit/receive valid/ack bits and valid/ack interrupt enables.
- `BIF_VMHV_MAILBOX`: compact VM/HV mailbox fields for interrupt enables, 4-bit transmit/receive message payloads, valid bits, and ack bits.
- `MM_INDEX`, `MM_DATA`, and `MM_INDEX_HI`: indexed register access fields in the VF system PF/VF decode block.
- `RCC_ERR_LOG`, `RCC_DOORBELL_APER_EN`, `RCC_CONFIG_MEMSIZE`, `RCC_CONFIG_RESERVED`, and `RCC_IOV_FUNC_IDENTIFIER`: RCC-side SR-IOV status/configuration fields.
- `RCC_GFXMSIX_VECT0..3_{ADDR_LO,ADDR_HI,MSG_DATA,CONTROL}` and `RCC_GFXMSIX_PBA`: MSI-X vector address/data/mask and pending-bit fields.

The trailing VF7 block is immediately followed by `#endif`, so this chunk closes the file. The first four lines belong to the prior VF2 MSI-X PBA block and should be reconciled with the preceding chunk during merge.

## Important APIs, Types, and Macros

This file's interface is the AMDGPU register-field macro naming convention:

- `<REGISTER>__<FIELD>__SHIFT` gives the least-significant bit position of a field.
- `<REGISTER>__<FIELD>_MASK` gives the already-shifted mask used for extraction, composition, or clearing.
- The register prefix includes the hardware path and VF number, for example `BIF_BX_DEV0_EPF0_VF5_MAILBOX_CONTROL__RCV_MSG_VALID_MASK`.

These macros are normally paired with the same register names from `nbio_7_9_0_offset.h` and accessed through AMDGPU/SOC15 helpers such as `REG_GET_FIELD`, `REG_SET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, `SOC15_REG_OFFSET`, and related instance-aware variants. The chunk itself does not call those helpers.

The header is included directly by:

- `drivers/gpu/drm/amd/amdgpu/nbio_v7_9.c`, which performs NBIO 7.9.0 initialization, register remapping, doorbell setup, memory-controller access toggles, and revision/memsize queries.
- `drivers/gpu/drm/amd/ras/ras_mgr/amdgpu_ras_nbio_v7_9.c`, which wires NBIO RAS interrupt sources and includes the register database even though its handlers are currently dummy hooks.

Specific VF3-VF7 macros in this chunk are generated definitions and may be consumed indirectly by future or configuration-specific NBIO, SR-IOV, RAS, debug, or register-dump paths.

## Control Flow and Data Flow

There is no runtime control flow in the chunk. The effective flow at runtime is:

1. AMDGPU builds NBIO 7.9.0 support and includes the offset and shift/mask headers.
2. Driver code reads a hardware register identified by a `reg...` macro from the companion offset file.
3. Driver code uses these `__SHIFT` and `_MASK` macros, usually through `REG_GET_FIELD` or `REG_SET_FIELD`, to extract or compose a field value.
4. The result affects hardware state such as VF doorbell apertures, HDP coherency operations, mailbox handshakes, BIF transaction status, RCC error reporting, function identification, or MSI-X interrupt delivery.

The repeated VF blocks imply per-virtual-function isolation: the same field layout exists for VF3, VF4, VF5, VF6, and VF7, but each macro names a separate VF register window. The field values themselves are not held in software; they are MMIO/configuration-visible hardware register bits.

## State and Persistence

The header has only compile-time constants and no mutable state or persistence.

The hardware state described by the masks is persistent according to NBIO, PCIe, SR-IOV, reset, and power-domain semantics:

- Doorbell aperture base/control fields define where a VF's doorbell self-ring aperture is exposed and whether it is enabled.
- HDP coherency request/control fields coordinate CPU/GPU-visible memory ordering and cache flush/invalidate behavior.
- `GPU_HDP_FLUSH_REQ` and `GPU_HDP_FLUSH_DONE` form a request/acknowledgement register pair across command processor, SDMA, and reserved engine sources.
- Mailbox message buffers and control bits represent PF/VF or VM/HV communication state; valid and ack bits are handshake state that can be updated asynchronously by hardware/firmware peers.
- BME, atomic error, transaction-pending, and RCC error-log fields are status or clear-on-write style indicators; their precise clear/read behavior comes from the hardware specification, with this header only providing the bit geometry.
- MSI-X vector table and PBA fields hold interrupt target addresses, message data, mask bits, and pending indicators for VF interrupt delivery.

An incorrect mask or shift is a compile-time constant bug that can systematically corrupt field extraction/composition wherever used.

## Dependencies and Integration Points

This chunk depends on the generated AMD register-header ecosystem for NBIO 7.9.0:

- `nbio_7_9_0_offset.h` supplies the corresponding register addresses and base indices.
- AMDGPU register helper macros consume the shifts and masks for field-level reads and writes.
- `nbio_v7_9.c` is the main NBIO 7.9.0 integration point; it includes this file alongside the offset header and uses related NBIO fields for hardware initialization paths.
- `amdgpu_ras_nbio_v7_9.c` includes this header for NBIO RAS integration with BIF interrupt source IDs.
- SR-IOV/virtualization code paths depend on the VF-numbered register layout remaining isolated and consistent across VF3-VF7.
- PCIe/MSI-X behavior depends on the RCC MSI-X vector/PBA field layout matching the device's PCI configuration semantics.

The repeated macro blocks also mirror generated NBIF/NBIO headers for other ASIC revisions, which can help reviewers spot generator drift, but NBIO 7.9.0 hardware documentation remains the authority for semantics.

## Risks and Edge Cases

- The chunk boundary starts inside the VF2 RCC MSI-X PBA block. The merge lane should preserve those four VF2 field definitions with the preceding VF2 material.
- Repetition across VF3-VF7 makes generator or copy errors easy to miss. A single wrong VF number, mask, or shift may only fail when that virtual function is enabled.
- Full-width fields such as mailbox data, config memsize/reserved, MM data, and address high/low masks use `0xFFFFFFFFL`; callers must avoid extra shifts or signed assumptions.
- MSI-X address-low fields start at bit 2 and mask with `0xFFFFFFFC`, reflecting alignment. Treating them as full 32-bit low addresses would mishandle the low reserved bits.
- Clear/status pairs use separate low status bits and high clear bits for BME and atomic error logs. Code must not blindly write a readback value without understanding write-one-to-clear semantics.
- HDP flush request/done fields are synchronization-sensitive. Wrong bit selection can produce hangs, stale memory visibility, or false completion.
- Mailbox valid/ack and interrupt-enable bits cross software/firmware or PF/VF boundaries. Misusing the masks can lose messages, wedge a handshake, or signal the wrong side.
- `RCC_IOV_FUNC_IDENTIFIER` exposes a one-bit function identifier plus `IOV_ENABLE` at bit 31 in this generated block; code assuming a wider function id would not match these masks.

## Test and Validation Signals

Useful validation is mostly compile-time plus hardware integration:

- Build AMDGPU with NBIO 7.9.0 enabled so the include paths and generated macro names are validated.
- Compare this shift/mask header against `nbio_7_9_0_offset.h` to ensure every VF3-VF7 register address has matching field definitions.
- Exercise SR-IOV with multiple VFs, especially VF3 through VF7, and verify doorbell programming, queue submission, and mailbox handshakes per VF.
- Validate HDP coherency paths under GPU memory workloads by checking that flush requests reach done bits without hangs or stale host/GPU data.
- Test MSI-X interrupt delivery per VF: vector address/data programming, mask/unmask behavior, and PBA pending-bit updates.
- Check BME, atomic error, RCC error-log, and BIF transaction-pending reporting during reset, FLR, illegal access, and PCIe stress scenarios.
- Run suspend/resume and GPU reset flows to confirm VF doorbell, mailbox, HDP, and MSI-X state is either restored by the responsible driver path or reset by hardware/firmware as expected.
