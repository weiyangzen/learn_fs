# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_2_3_sh_mask.h lines 80988-83608

## Scope

This chunk covers generated NBIO 2.3 shift and mask definitions for SR-IOV virtual-function NBIF/RCC registers. It starts inside the VF6 `BIFPFVFDEC1` block at `BIF_BX_DEV0_EPF0_VF6_BIF_ATOMIC_ERR_LOG`, contains the VF6 mailbox and graphics MSI-X tail, covers complete VF7 through VF15 `SYSPFVFDEC`, `BIFPFVFDEC1`, and `BIFDEC2` field maps, and ends in VF16 after `BIF_BX_DEV0_EPF0_VF16_BIF_TRANS_PENDING`.

The chunk is data-only C preprocessor material. It defines no functions, structs, variables, allocations, locks, or direct MMIO accesses. Its interface is the generated field convention:

- `<REGISTER>__<FIELD>__SHIFT` for the field bit offset.
- `<REGISTER>__<FIELD>_MASK` for the field mask.

Within this range there are 2,022 generated macros: 1,011 shift macros and 1,011 matching mask macros, covering 479 register-name families.

## Purpose

`nbio_2_3_sh_mask.h` is the bitfield half of the AMD NBIO 2.3 register ABI. The companion offset header names register addresses, while this header tells register helpers how to encode or decode individual fields. For this chunk, the ABI surface is per-virtual-function SR-IOV state for VF6 through VF16 around:

- VF indirect MMIO index/data access.
- RCC error, memory-size, doorbell-aperture, and IOV function-identifier state.
- BIF bus-master, unsupported atomic, doorbell self-ring aperture, HDP coherency flush, transaction-pending, address-LUT bypass, mailbox, and VM-hypervisor mailbox state.
- Per-VF graphics MSI-X vector table and pending-bit-array fields.

These definitions let AMDGPU, firmware-facing code, and virtualization paths compose register values without open-coded bit numbers. They are especially sensitive because each VF has its own generated macro namespace; a valid C identifier can still target the wrong virtual function if the VF number is copied incorrectly.

## Important Macro Families

### Chunk Boundary: VF6 Tail

The first visible VF6 definition is `BIF_BX_DEV0_EPF0_VF6_BIF_ATOMIC_ERR_LOG__UR_ATOMIC_OPCODE__SHIFT`; the VF6 `MM_INDEX`, `MM_DATA`, `MM_INDEX_HI`, RCC fields, and `BIF_BME_STATUS` begin in the previous chunk. This chunk then covers the rest of VF6 `BIFPFVFDEC1`:

- `BIF_ATOMIC_ERR_LOG` status bits for unsupported atomic opcode, request-enable-low, length, and non-relaxed-request conditions, plus clear bits at positions 16-19.
- `DOORBELL_SELFRING_GPA_APER_BASE_HIGH`, `LOW`, and `CNTL` fields for the self-ring guest physical address aperture, enable bit, mode bit, and aperture size.
- `HDP_REG_COHERENCY_FLUSH_CNTL` and `HDP_MEM_COHERENCY_FLUSH_CNTL` one-bit flush-address controls.
- `GPU_HDP_FLUSH_REQ` and `GPU_HDP_FLUSH_DONE` bits for CP0 through CP9 and SDMA0 through SDMA1 clients.
- `BIF_TRANS_PENDING` master/slave pending indicators and `NBIF_GFX_ADDR_LUT_BYPASS`.
- Four transmit and four receive mailbox dwords, `MAILBOX_CONTROL`, `MAILBOX_INT_CNTL`, and `BIF_VMHV_MAILBOX`.

The VF6 tail also includes `RCC_DEV0_EPF0_VF6_GFXMSIX_*` definitions for graphics MSI-X vectors 0-3. Each vector has low/high message address, message data, and a one-bit control mask, followed by `GFXMSIX_PBA` pending bits 0-3.

### Complete VF7 Through VF15 Maps

VF7, VF8, VF9, VF10, VF11, VF12, VF13, VF14, and VF15 repeat the same generated layout:

- `SYSPFVFDEC`: `MM_INDEX` with `MM_OFFSET` and `MM_APER`, `MM_DATA`, and `MM_INDEX_HI`.
- RCC `BIFPFVFDEC1`: `RCC_ERR_LOG` for invalid SR-IOV register access and doorbell-read access status, `RCC_DOORBELL_APER_EN`, `RCC_CONFIG_MEMSIZE`, `RCC_CONFIG_RESERVED`, and `RCC_IOV_FUNC_IDENTIFIER` with function identifier and IOV enable.
- BIF `BIFPFVFDEC1`: `BIF_BME_STATUS`, `BIF_ATOMIC_ERR_LOG`, doorbell self-ring GPA aperture base/control, HDP register and memory flush controls, `GPU_HDP_FLUSH_REQ`, `GPU_HDP_FLUSH_DONE`, `BIF_TRANS_PENDING`, `NBIF_GFX_ADDR_LUT_BYPASS`, mailbox dwords/control/interrupts, and `BIF_VMHV_MAILBOX`.
- RCC `BIFDEC2`: graphics MSI-X vector 0-3 address/data/control fields and the four-bit graphics MSI-X PBA.

The fields are mechanically identical across these complete VF blocks except for the `VF<n>` namespace. That repetition is useful for generated hardware coverage, but it makes layout drift, misnumbered names, or copied wrong-VF references high-risk.

### Chunk Boundary: VF16 Head

The final visible section starts VF16 with `SYSPFVFDEC`, RCC `BIFPFVFDEC1`, and BIF `BIFPFVFDEC1` through `BIF_TRANS_PENDING`. VF16 `NBIF_GFX_ADDR_LUT_BYPASS`, mailbox, VMHV mailbox, and graphics MSI-X fields continue in the next chunk. File-level research should merge this document with adjacent chunks before making complete claims about VF6 or VF16.

## Important APIs, Types, and Functions

There are no C APIs, types, or functions in this chunk. The effective public API is the macro naming contract consumed by AMD register helpers. In surrounding AMDGPU code, these generated names are normally paired with:

- Matching offset macros from `nbio_2_3_offset.h`.
- Reset/default values from `nbio_2_3_default.h`.
- Register helper macros such as `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, `WREG32_FIELD15`, and `SOC15_REG_OFFSET`.

Consumers include `drivers/gpu/drm/amd/amdgpu/nbio_v2_3.c`, `drivers/gpu/drm/amd/amdgpu/mxgpu_nv.c`, and SMU11 platform files `navi10_ppt.c` and `sienna_cichlid_ppt.c`, all of which include this NBIO 2.3 mask header. The specific VF6-VF16 names in this chunk are hardware ABI definitions; direct runtime use may be concentrated in virtualization, firmware, or generated register-table paths rather than hand-written references to every VF macro.

## Control Flow

The header has no executable control flow. Runtime flow belongs to code that includes it:

1. The driver selects a per-VF register offset from the offset header.
2. The driver uses the matching `__SHIFT` and `_MASK` macro to encode a field for a write or decode a field from a read.
3. The access reaches NBIO/RCC hardware through the SOC15/MMIO/indirect register path selected by the caller.
4. Hardware state changes or status is reported according to the register semantics.

Several hardware workflows are implied by the fields:

- HDP coherency flushing uses `GPU_HDP_FLUSH_REQ` client bits and observes `GPU_HDP_FLUSH_DONE` for CP and SDMA engines.
- Mailbox communication writes transmit dwords, asserts transmit valid bits, observes acknowledge/receive-valid bits, and may use valid/ack interrupt enables.
- VMHV mailbox communication uses compact transmit/receive message-data fields plus valid, ack, and interrupt-enable bits.
- Error/status handling reads `RCC_ERR_LOG`, `BIF_BME_STATUS`, and `BIF_ATOMIC_ERR_LOG`, then uses explicit clear fields where provided.
- MSI-X setup programs vector message address/data/control fields and observes pending bits in `GFXMSIX_PBA`.

The masks do not encode ordering, timeout, locking, or clear-on-write policy. Those details must come from the callers and the NBIO hardware specification.

## State and Persistence Behavior

The header stores no software state. It names hardware-visible state that persists until reset, FLR, VF teardown, power transition, firmware action, hypervisor action, or explicit driver writes.

Important state represented here includes:

- Per-VF indirect MMIO aperture selection through `MM_INDEX`, `MM_INDEX_HI`, and `MM_DATA`.
- SR-IOV access error state in `RCC_ERR_LOG`, including invalid register access and doorbell read access.
- VF resource presentation through `RCC_CONFIG_MEMSIZE`, `RCC_CONFIG_RESERVED`, and `RCC_IOV_FUNC_IDENTIFIER`.
- Doorbell aperture enablement and self-ring GPA aperture base/mode/size.
- Bus-master-low and unsupported atomic request status, with explicit clear bits.
- HDP register/memory coherency flush triggers and CP/SDMA flush completion state.
- BIF master/slave transaction-pending state and graphics address LUT bypass.
- Mailbox buffers, valid/ack handshake bits, interrupt enables, and VMHV mailbox message/ack state.
- Graphics MSI-X vector message address, message data, vector mask bits, and PBA pending bits.

Many of these registers are stateful control/status registers, not passive storage. Clearing error logs, toggling mailbox valid/ack fields, masking MSI-X vectors, changing doorbell apertures, or issuing HDP flushes can alter device behavior immediately.

## Dependencies and Integration Points

This chunk depends on the generated NBIO 2.3 register-header set:

- `nbio_2_3_offset.h` supplies the matching register offsets and base indices for the `BIF_BX_DEV0_EPF0_VF*` and `RCC_DEV0_EPF0_VF*` names.
- `nbio_2_3_default.h` supplies reset/default values for related NBIO registers.
- AMDGPU SOC15 and register-field helper macros consume the shift/mask pairs.

Tree-level integration points observed from includes and related references:

- `drivers/gpu/drm/amd/amdgpu/nbio_v2_3.c` is the primary NBIO 2.3 implementation using this generated header set.
- `drivers/gpu/drm/amd/amdgpu/mxgpu_nv.c` includes the same header in virtualization-oriented code.
- `drivers/gpu/drm/amd/pm/swsmu/smu11/navi10_ppt.c` and `sienna_cichlid_ppt.c` include NBIO 2.3 masks for platform management interactions.
- Adjacent NBIO generation families use the same HDP flush and VF register layout patterns, so cross-generation comparisons can catch accidental field-width or bit-position drift.

The names in this chunk are part of a broader generated ABI surface for many virtual functions. The hardware access rights for PF, VF guest, hypervisor, and firmware contexts are not represented in the header and must be enforced elsewhere.

## Risks

- Wrong masks or shifts can write unrelated control bits, corrupt per-VF doorbell apertures, break mailbox handshakes, hide SR-IOV access errors, or misprogram MSI-X vectors.
- Wrong VF namespace usage can compile cleanly while targeting another virtual function. This chunk has near-identical VF7-VF15 maps, making copy/paste mistakes hard to detect by type checking.
- Status and clear fields are mixed in the same generated family. Treating `CLEAR_*` fields as ordinary status bits, or writing status masks without preserving unrelated bits, can lose diagnostics or clear evidence prematurely.
- HDP flush request/done fields are synchronization-sensitive. Missing waits, wrong client bits, or stale done-bit interpretation can create memory-coherency bugs between CP/SDMA engines, host memory, and the driver.
- Doorbell aperture and LUT-bypass fields are security-sensitive in SR-IOV. Incorrect aperture base, size, enable, or bypass programming can expose the wrong guest physical address window or route doorbells incorrectly.
- Mailbox valid/ack fields implement hardware handshakes. Races, missing interrupt masking, or wrong clear ordering can deadlock PF/VF or VM/hypervisor communication.
- MSI-X vector address/data/control fields affect interrupt delivery. Bad masks can drop interrupts, deliver them to the wrong target, or leave pending bits uncleared.
- Chunk boundaries are partial for VF6 and VF16. A reconciled file-level document should avoid treating this chunk alone as a complete VF6 or VF16 map.

## Test and Validation Signals

Useful validation is mostly build, generated-header consistency, SR-IOV, and hardware bring-up coverage:

- Build AMDGPU paths that include `nbio_2_3_sh_mask.h`, especially NBIO 2.3, MXGPU, and SMU11 platform code.
- Generated-header checks should verify each `__SHIFT` has a matching `_MASK`, each VF7-VF15 block has the same field set, and the mask widths match the documented field widths.
- Cross-check `nbio_2_3_sh_mask.h` against `nbio_2_3_offset.h` so every register family in this chunk has a matching address/base-index definition.
- SR-IOV tests should create multiple VFs beyond VF6 and verify per-VF doorbell aperture setup, config memory-size reporting, IOV function identifiers, and VF isolation.
- HDP coherency tests should issue CP and SDMA flush requests and confirm matching done bits for all represented clients.
- Mailbox tests should exercise transmit/receive valid and ack handshakes, interrupt-enable bits, and VMHV mailbox fields under PF/VF or hypervisor-mediated scenarios.
- Error-injection tests should validate invalid SR-IOV register access, doorbell-read access, bus-master-low, and unsupported atomic logging plus clear behavior.
- MSI-X tests should program graphics vectors 0-3, toggle vector mask bits, deliver interrupts, and verify PBA pending-bit behavior for VFs covered by the complete blocks.

## Unresolved Cross-Chunk References

Line 80988 starts after the VF6 `SYSPFVFDEC`, RCC `BIFPFVFDEC1`, and `BIF_BME_STATUS` definitions, so the full VF6 map requires the previous chunk. Line 83608 ends immediately after VF16 `BIF_TRANS_PENDING`; the remaining VF16 LUT-bypass, mailbox, VMHV mailbox, and graphics MSI-X fields continue in the next chunk. The merge lane should stitch those boundaries before producing the final per-file research document.
