# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbif/nbif_6_3_1_sh_mask.h - subset-b-002883

## Scope

- Chunk id: `subset-b-002883`
- Source lines: 14841-17760
- Source file: `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbif/nbif_6_3_1_sh_mask.h`
- Observed content: 2,920 source lines from a generated AMD NBIF 6.3.1 shift/mask header; 2,014 `#define` constants, including 1,014 `__SHIFT` entries and 1,203 `_MASK` entries.

This chunk contains register field metadata, not executable logic. It exports preprocessor constants named `REGISTER__FIELD__SHIFT` and `REGISTER__FIELD_MASK` for NBIF PCIe/MSI-X, root-complex power-function, shadow, indirect-index, and strap registers. Register addresses and base-index selectors are supplied by the companion `nbif_6_3_1_offset.h` header.

## Purpose

The largest part of the chunk completes the MSI-X vector table definitions for `PCIEMSIX_VECT54` through `PCIEMSIX_VECT255`. Each vector has the standard table fields:

- `ADDR_LO`, where `MSG_ADDR_LO` starts at bit 2 and masks off the low 2 naturally aligned address bits.
- `ADDR_HI`, with a full 32-bit high message address.
- `MSG_DATA`, with a full 32-bit MSI-X payload.
- `CONTROL`, with bit 0 as the per-vector mask bit.

The later regions define smaller NBIF blocks:

- `nbif_rcc_pfc_usb_RCCPFCDEC` and `nbif_rcc_pfc_pd_controller_RCCPFCDEC` power-function controls for USB and PD-controller endpoints, covering LTR snoop/non-snoop latency fields, PME restore bits, sticky error/TLP restore registers, and auxiliary power override fields.
- `nbif_pciemsix_0_usb_MSIXPDEC` MSI-X pending-bit-array registers `PCIEMSIX_PBA_0` through `PCIEMSIX_PBA_7`, each exposing 32 pending bits.
- `nbif_rcc_shadow_reg_shadowdec` shadowed upstream command, BAR, bridge-control, and SUC indirect index/data fields.
- `nbif_bif_swus_SUMDEC` SUM indirect index/data fields, including an 8-bit high index register.
- `nbif_rcc_strap_rcc_strap_internal` strap fields for downstream/root-port behavior on device 0 and the beginning of BIF global strap fields.

The strap macros describe PCIe identity, advertised capabilities, link behavior, power-management support, atomic/ACS/ARI/AER/LTR/OBFF features, MSI/MSI-X capability exposure, power-budget entries, Gen2/Gen3/Gen4/Gen5 capability and equalization settings, 10-bit tag support, requester/completer behavior, routing timers, alternate protocol details, and DOE/CTO/error subclass support.

## Important APIs, Types, and Macros

There are no functions, structs, enums, or mutable objects in this chunk. The public interface is the generated macro namespace.

Important macro families include:

- MSI-X vector table fields: `PCIEMSIX_VECT54_*` through `PCIEMSIX_VECT255_*`. The visible pattern is repeated for every vector: `ADDR_LO__MSG_ADDR_LO`, `ADDR_HI__MSG_ADDR_HI`, `MSG_DATA__MSG_DATA`, and `CONTROL__MASK_BIT`.
- MSI-X pending bit arrays: `PCIEMSIX_PBA_0__MSIX_PENDING_BITS` through `PCIEMSIX_PBA_7__MSIX_PENDING_BITS`.
- PFC LTR and restore fields: `RCC_PFC_USB_RCC_PFC_LTR_CNTL`, `RCC_PFC_USB_RCC_PFC_PME_RESTORE`, `RCC_PFC_USB_RCC_PFC_STICKY_RESTORE_0..5`, `RCC_PFC_USB_RCC_PFC_AUXPWR_CNTL`, and the equivalent `RCC_PFC_PD_CONTROLLER_*` registers.
- Shadow register fields: `SHADOW_COMMAND__IOEN_UP`, `SHADOW_COMMAND__MEMEN_UP`, `SHADOW_BASE_ADDR_1__BAR1_UP`, `SHADOW_BASE_ADDR_2__BAR2_UP`, and `SHADOW_IRQ_BRIDGE_CNTL` upstream ISA/VGA/reset controls.
- Indirect window fields: `SUC_INDEX`, `SUC_DATA`, `SUM_INDEX`, `SUM_DATA`, and `SUM_INDEX_HI`.
- Device-0 port strap fields: `RCC_STRAP1_RCC_DEV0_PORT_STRAP0` through `RCC_STRAP1_RCC_DEV0_PORT_STRAP14`, covering identity, PCIe capabilities, link/power/error behavior, ACS, atomics, virtual channels, 10-bit tags, equalization presets, modified TS data, routing timers, alternate protocol metadata, and DOE/CTO/error subclass capability flags.
- Placeholder comments for `RCC_DEV1_PORT_STRAP0..14` and `RCC_DEV2_PORT_STRAP0..14`; this range has no shift/mask constants for those placeholders.
- BIF strap start: `RCC_STRAP1_RCC_BIF_STRAP0__STRAP_*__SHIFT` begins at the end of the chunk. The matching masks continue after this chunk.

## Control Flow

The header has no local runtime control flow. Runtime behavior is implied by code that includes this generated register database and uses AMD register helper macros.

For MSI-X, the hardware flow is the PCIe-defined table/PBA model: software or hardware writes each vector message address, message data, and mask state; pending interrupt state is reflected through PBA bits; an unmasked pending vector can generate the programmed MSI-X memory write. This chunk covers the table tail, so any code walking all 256 vectors depends on the regular four-register stride remaining correct.

For PFC/PME restore, the flow is power-management oriented. LTR fields advertise snoop and non-snoop latency tolerance; PME restore fields retain/restore PME enable, PME status, and sent-flag state; sticky restore registers preserve error status and captured TLP header/prefix information across a relevant low-power or reset transition; auxiliary-power fields override current and power-detected inputs.

For shadow/SUC/SUM blocks, the implied flow is indirect access: write an index register, then read or write the corresponding data register. Shadow command/BAR/bridge-control fields mirror or stage upstream-visible PCI configuration state.

For straps, the flow is mostly reset-time or early-initialization configuration. Strap bits describe the hardware defaults and advertised PCIe capability surface that later enumeration, link training, and driver policy observe. Driver code should treat these definitions as hardware layout constants rather than ordinary configurable software policy.

## State and Persistence Behavior

The macros are compile-time constants and keep no state. They describe hardware register fields whose values persist according to their register domain:

- MSI-X table values are persistent programmed interrupt routing state until rewritten, reset, or masked by device/function reset semantics. `ADDR_LO`, `ADDR_HI`, and `MSG_DATA` determine interrupt target and payload; `CONTROL__MASK_BIT` suppresses delivery per vector.
- MSI-X PBA fields are transient/latched pending bits. Pending state can be set by hardware while a vector is masked or while delivery is otherwise blocked, and is cleared according to MSI-X hardware protocol rather than by generic register retention assumptions.
- PFC LTR and auxiliary-power fields are retained control/advertisement state. PME restore and sticky restore fields preserve wake/error context such as PME state, PCIe error status, TLP headers, and TLP prefix values.
- Shadow command, BAR, and bridge-control fields hold upstream-visible or staged configuration state. SUC/SUM index registers hold the currently selected indirect address, and data registers expose the selected target.
- Strap registers represent sampled hardware configuration. Some may be read-only from the driver's point of view or only meaningful during reset/bring-up; changing them after enumeration can desynchronize PCIe capability advertisement from OS state.

Several fields have write-one, clear, restore, or latched semantics in hardware even though this header only provides masks. Consumers must follow the hardware programming model and avoid treating every field as a normal read-modify-write bit.

## Dependencies

This chunk depends on:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbif/nbif_6_3_1_offset.h`, which provides matching register offsets and base indices. Examples in this range include `regPCIEMSIX_VECT54_ADDR_LO` at `0x1e0d8`, `regPCIEMSIX_VECT255_CONTROL` at `0x1e3ff`, PFC USB registers around `0xd140`, PFC PD-controller registers around `0xd1c0`, shadow registers around `0xc001`, SUM registers around `0xec38`, port straps around `0xc400`, and BIF straps beginning at `0xc600`.
- AMDGPU SOC15/NBIO register access helpers such as `RREG32_SOC15`, `WREG32_SOC15`, `REG_GET_FIELD`, `REG_SET_FIELD`, and field-table macros that expect generated `REGISTER__FIELD__SHIFT` and `REGISTER__FIELD_MASK` names.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/nbif_v6_3_1.c`, which includes both `nbif_6_3_1_offset.h` and `nbif_6_3_1_sh_mask.h` for NBIF 6.3.1 programming.
- AMD PCIe/NBIO infrastructure, MSI/MSI-X semantics, power-management/PME restore behavior, and PCIe capability advertisement controlled by strap values.

The file path is inside a Ceph client source corpus, but this source is Linux AMDGPU hardware register metadata and is not Ceph filesystem logic.

## Integration Points

The direct integration point is the NBIF 6.3.1 AMDGPU driver layer. `amdgpu/nbif_v6_3_1.c` includes this header and uses the same generated mask/shift naming convention for NBIF fields; exact fields in this chunk are not directly referenced by current C source searches, but they remain part of the exported generated register ABI for the ASIC.

MSI-X integration is with PCI interrupt setup, masking, and diagnostic paths. The vector table definitions must stay aligned with the PCIe MSI-X table and PBA offsets so any table walker, firmware path, debug path, or future endpoint-specific driver logic programs the correct vector.

PFC integration is with PCIe power management for USB and PD-controller functions. LTR, PME restore, sticky error restore, and auxiliary power override fields influence suspend/resume, wake, and error recovery behavior for those NBIF-exposed functions.

Shadow/SUC/SUM integration is with indirect register access and upstream-visible PCI configuration state. These registers can be used by firmware, bring-up tools, or low-level driver code to stage or inspect state that is not represented by a simple direct MMIO register.

Strap integration is with PCI enumeration, capability discovery, link training, error handling, power management, and virtualization/security features. Fields such as ACS, ARI, AER, atomics, LTR, OBFF, VC, 10-bit tags, MSI mapping, target link speed, link width, equalization presets, and device/vendor IDs define what Linux and the PCIe fabric believe the device/root port supports.

## Risks and Edge Cases

- The chunk begins at line 14841 with `PCIEMSIX_VECT54_ADDR_LO__MSG_ADDR_LO_MASK`; the corresponding shift for that field is in the previous chunk. The merge lane must combine adjacent chunks for complete `VECT54_ADDR_LO` coverage.
- The chunk ends in the middle of `RCC_STRAP1_RCC_BIF_STRAP0`; only shifts through `STRAP_RX_IGNORE_TC_ERR_DN__SHIFT` are visible here, with masks and later fields in the next chunk.
- MSI-X vector definitions are highly repetitive. A single off-by-one vector number, stride mismatch, or low-address mask error can route interrupts to the wrong address/data pair or leave the wrong vector masked.
- `MSG_ADDR_LO` masks bits 31:2. Callers must preserve PCIe/MSI address alignment semantics and not try to encode data in the low two address bits.
- PBA registers expose pending state, not durable configuration. Treating pending bits as ordinary writable state can lose interrupt evidence or fight hardware delivery semantics.
- PME and sticky restore registers mix enable/status/sent flags with captured PCIe error data. Misinterpreting restore fields can break wake recovery or obscure the original TLP that triggered an error.
- LTR value/scale fields are split into snoop and non-snoop halves. Wrong values can cause platform power-management latency assumptions to be too aggressive or too conservative.
- Shadow and indirect index/data windows are stateful. Concurrent access without serialization can read or write the wrong indexed target if another path changes the index between operations.
- Strap fields may be sampled or hardware-owned. Runtime writes, if allowed at all, can produce inconsistent PCIe capability exposure after the OS has already enumerated the device.
- Capability straps for ACS, atomics, ARI, AER, PASID-adjacent routing behavior, 10-bit tags, and MSI/MSI-X affect isolation, error handling, and interrupt routing. Incorrect masks can become security or reliability bugs rather than simple feature toggles.
- Placeholder comments for device 1 and device 2 port straps have no macros in this range. Consumers must not assume every commented register has generated fields.

## Test Signals

Useful validation signals for this chunk include:

- Build coverage for AMDGPU NBIF 6.3.1 code that includes `nbif_6_3_1_offset.h` and `nbif_6_3_1_sh_mask.h`.
- Generated consistency checks that every complete `PCIEMSIX_VECT55` through `PCIEMSIX_VECT255` instance has the same four field groups and the expected masks: low message address `0xFFFFFFFC`, high address `0xFFFFFFFF`, message data `0xFFFFFFFF`, and mask bit `0x00000001`.
- Boundary checks that `PCIEMSIX_VECT54_ADDR_LO` is completed by the previous chunk and `RCC_STRAP1_RCC_BIF_STRAP0` is completed by the next chunk.
- Offset/mask alignment checks against `nbif_6_3_1_offset.h`, especially the MSI-X vector table stride from `regPCIEMSIX_VECT54_ADDR_LO` through `regPCIEMSIX_VECT255_CONTROL`, PBA registers, PFC USB/PD-controller register blocks, shadow/SUM windows, and strap registers.
- Hardware or emulation smoke tests for MSI-X vector programming and masking, including delivery to the programmed message address/data and correct PBA pending behavior for masked vectors.
- Suspend/resume and wake tests that exercise PME restore, LTR programming, auxiliary power override behavior, and sticky error restore capture for USB and PD-controller NBIF functions.
- PCIe enumeration/link tests that verify advertised IDs, link width/speed, AER/ACS/ARI/atomics/LTR/OBFF/VC/10-bit-tag/MSI capability behavior, and equalization settings match expected board or ASIC strap values.
- Error-injection tests that confirm restored sticky fields report PCIe poisoned, completion-timeout, completion-abort, unexpected-completion, malformed-TLP, ECRC, unsupported-request, advisory-nonfatal, header, and prefix information accurately.

## Chunk Boundary Notes

This report covers only lines 14841-17760. The first visible line is a mask without its paired shift, and the final visible region starts `RCC_STRAP1_RCC_BIF_STRAP0` but does not include its masks. The final per-file research document should reconcile these boundaries with adjacent chunks before presenting complete register families.
