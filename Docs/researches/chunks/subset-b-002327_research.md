# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_0_sh_mask.h lines 92907-95285

## Scope

This chunk covers 2,379 lines from the generated AMD DPCS 4.2.0 shift/mask header. The chunk starts in the final mask entries for `DPCSSYS_CR4_RAWLANE1_DIG_PCS_XF_TX_OVRD_IN` and then contains complete register-field macro groups from `DPCSSYS_CR4_RAWLANE1_DIG_PCS_XF_TX_OVRD_IN_1` through the heading for `DPCSSYS_CR4_RAWLANE3_DIG_PCS_XF_RX_ADAPT_FOM`. The matching offset header and other chunks define the register addresses; this file supplies the field positions and masks used by register helper code.

## Purpose

The source is a hardware register description header for the AMD display DPCS block, specifically CR4 rawlane digital PCS/PMA/FSM/IRQ/TX/RX control fields for DPCS 4.2.0. It exports preprocessor constants named as:

- `<register>__<field>__SHIFT`
- `<register>__<field>_MASK`

These constants let C code form and extract fields from 16-bit-style register payloads without hard-coding bit positions. The chunk is mostly lane-local register vocabulary for rawlane 1 and rawlane 2, then begins the same PCS TX/RX vocabulary for rawlane 3.

## Important API Surface

There are no functions, structs, enums, or runtime objects in this chunk. Its API is entirely macro constants. Important macro families include:

- `DPCSSYS_CR4_RAWLANE1_DIG_PCS_XF_*`: lane 1 PCS transfer/interface controls for TX override input, TX PCS input/output, RX override input, RX PCS input/output, RX adaptation status, loopback direction, lane number, ATE overrides, RX equalization override, TX/RX termination, and RX phase-2 calibration.
- `DPCSSYS_CR4_RAWLANE1_DIG_FSM_*`: lane 1 FSM controls and monitors, including `FSM_OVRD_CTL`, `MEM_ADDR_MON`, `STATUS_MON`, fast RX/TX calibration/adaptation flags, common calibration MPLL/RCAL status, CR lock bits, OCLA hooks, TX DCC state, TX EQ update flag, and RX IQ phase offset.
- `DPCSSYS_CR4_RAWLANE1_DIG_IRQ_CTL_*`: lane 1 IRQ status, clear, and mask definitions for RX reset/request/rate/pstate/adaptation/phase-2-calibration events, lane mode and loopback events, DCC on-demand IRQ, and TX reset/request IRQs.
- `DPCSSYS_CR4_RAWLANE1_DIG_PMA_XF_*`: lane 1 PCS-to-PMA interface fields for lane/supervisor override, TX/RX PMA handshakes, RTUNE, MPHY override, and RX adaptation output override.
- `DPCSSYS_CR4_RAWLANE1_DIG_TX_CTL_*` and `DPCSSYS_CR4_RAWLANE1_DIG_RX_CTL_*`: lane 1 local control/status bits for TX FSM, TX clock selection, TX DCC continuous status, OCLA, RX FSM, LOS mask count, RX data-enable override count, and continuous adaptation/off-cancellation status.
- `DPCSSYS_CR4_RAWLANE2_DIG_*`: the same broad PCS, FSM, IRQ, PMA, TX control, RX control, and ATE register families repeated for rawlane 2.
- `DPCSSYS_CR4_RAWLANE3_DIG_PCS_XF_*`: the beginning of rawlane 3 PCS TX/RX handshaking and override definitions through `RX_ADAPT_ACK`; the `RX_ADAPT_FOM` heading appears at the end boundary but its field macros are outside this chunk.

Field names carry the hardware contract. Examples:

- TX override fields expose `RESET_OVRD_VAL/EN`, `REQ_OVRD_VAL/EN`, `DETRX_REQ_OVRD_VAL/EN`, `VBOOST_EN_OVRD_VAL/EN`, `IBOOST_LVL_OVRD_VAL/EN`, and beacon/async-data enable fields.
- RX override fields expose link rate/width/pstate/low-power data, adaptation enables, loopback override, RX data enable override, reset/request override, LOS threshold override, adaptation request/continuous/off-cancellation control, VCO load/low-frequency override, and reference-load override.
- RX PCS input status fields expose request, rate, width, pstate, CDR low-frequency state, adaptation request/continuous/off-cancellation, reset, reference/VCO load values, and EQ state such as attenuation level, VGA gains, CTLE boost/pole, and DFE tap 1.
- IRQ clear registers use one-bit `*_IRQ_CLR` fields; mask registers use `*_IRQ_MSK` fields. The value semantics are implemented by hardware and callers, not by this header.

## Control Flow

There is no executable control flow. The generated header is consumed at C preprocessing and compilation time. Runtime register control flow in the display driver is external:

1. A driver file includes `dpcs_4_2_0_offset.h` for addresses and `dpcs_4_2_0_sh_mask.h` for field encodings.
2. Register helper macros or inline functions combine a register address with one or more `*_MASK` and `*__SHIFT` constants.
3. Hardware accessors read, update, or write the corresponding DPCS MMIO/register-space value.

Within this chunk, the only ordering dependency is textual: each comment heading identifies a register, then its field shifts are listed, followed by matching masks. Some chunk boundaries are partial; line 92907 continues the preceding `RAWLANE1_DIG_PCS_XF_TX_OVRD_IN` register, and line 95285 only introduces the next `RAWLANE3_DIG_PCS_XF_RX_ADAPT_FOM` register.

## State and Persistence Behavior

The header itself has no memory, persistence, locking, allocation, or side effects. It is persistent source data for register definitions. The state represented by these macros lives in hardware registers:

- PCS TX/RX request, reset, ACK, rate, width, pstate, loopback, and data-enable state.
- PMA/PCS handshake state, MPLL lane/supervisor state, and RTUNE acknowledgements.
- FSM monitor state such as command-ready, state index, wait count, ALU flags, memory address, and calibration flags.
- Sticky or latched IRQ status/clear/mask bits, depending on the underlying register behavior.
- RX adaptation measurements and calibration outputs such as FOM, EQ settings, IQ phase offset, VCO/ref load, and phase-2 calibration fields.

Any persistence, latching, clear-on-write behavior, or sequencing requirements are hardware-defined and must be enforced by the driver code that reads/writes these registers. The masks should not be treated as proof that a reserved field can be written safely.

## Dependencies

Direct dependencies are preprocessor-level:

- Include guard `_dpcs_4_2_0_SH_MASK_HEADER` is defined earlier in the same file.
- The matching address definitions are in `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_0_offset.h`.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn31/dcn31_resource.c` includes both `dpcs_4_2_0_offset.h` and this `dpcs_4_2_0_sh_mask.h`, then includes `reg_helper.h`, which is the normal AMD display register-helper layer.
- Neighboring generated DPCS versions, such as `dpcs_4_2_2_sh_mask.h` and `dpcs_4_2_3_sh_mask.h`, contain comparable definitions and are useful compatibility references, but they are distinct ASIC/IP register contracts.

This chunk does not include other headers and does not depend on C library, kernel APIs, or Ceph-specific code despite being located under the larger `ceph-client` source mirror.

## Integration Points

The main integration point is the AMD DCN 3.1 display resource stack. `dcn31_resource.c` includes this header for DPCS 4.2.0 register field constants. Downstream code can use these constants with generated register lists and helper macros to:

- Program lane TX/RX PCS and PMA override behavior during link bring-up, power transitions, retraining, or diagnostics.
- Observe and clear lane IRQs for RX/TX request/reset/rate/pstate/adaptation events.
- Configure or inspect fast calibration/adaptation paths for RX AFE/DFE/VCO/ref-level/IQ and TX DCC/supervisor calibration.
- Gate observability/debug paths such as OCLA and FSM monitor registers.
- Support automated test equipment paths through `ATE_*` override registers.

The specific rawlane macros in this chunk were only found in the generated headers during text search, not in direct C references elsewhere in the mirrored tree. That suggests they are part of a broad generated register surface where many fields are available to common helper code, debugging, or future ASIC-specific paths even if not explicitly used in the checked-in C sources.

## Risks and Edge Cases

- Register-field drift is the primary risk. If these generated masks do not match the DPCS 4.2.0 hardware spec or matching offset header, callers can silently write the wrong bits.
- Chunk boundaries are partial. Research or merge logic must not infer that line 92907 starts a complete register definition or that line 95285 contains the complete `RX_ADAPT_FOM` register.
- Many masks cover reserved fields, for example `RESERVED_15_*`. These are useful for generated completeness and readback decoding, but production code should avoid writing nonzero reserved bits unless the hardware spec requires it.
- Lane copy/paste errors are hard to detect manually because rawlane 1, rawlane 2, and rawlane 3 definitions are structurally repetitive. A lane prefix mismatch would compile cleanly but target the wrong register field family.
- All masks in this 4.2.0 chunk use 32-bit-looking `0x0000....L` constants for 16-bit fields. Neighboring DPCS versions may use shorter hex formatting for equivalent values; formatting differences should not be mistaken for semantic differences, but width/sign assumptions in helper macros should still be checked.
- Hardware side effects are not visible here. Fields named `*_CLR`, `*_OVRD_EN`, `RESET`, `REQ`, `ACK`, or calibration/adaptation bits may require strict sequencing, polling, debounce, or clear semantics in runtime code.

## Test Signals

Useful validation signals for this chunk are mostly compile-time and hardware/driver integration signals:

- Build coverage for AMD display code that includes `dcn31_resource.c` and this generated header.
- Static checks that every `*_MASK` has a corresponding `*__SHIFT` for non-heading fields in the same register group, except at chunk boundaries where the complete group may be outside this file slice.
- Generated-header consistency checks against `dpcs_4_2_0_offset.h`: every register prefix used here should have a matching address definition in the offset header for the same IP version.
- Cross-version diff checks against `dpcs_4_2_2_sh_mask.h` and `dpcs_4_2_3_sh_mask.h` to identify intended versus accidental field layout changes.
- Runtime display link tests on DCN 3.1/DPCS 4.2.0 hardware: link training, hotplug, rate changes, low-power transitions, RX adaptation, IRQ handling, and recovery from reset/request transitions.
- Debug readback tests that decode register values using these masks and confirm lane-specific fields behave independently across rawlane 1, rawlane 2, and rawlane 3.

## Open Questions for Merge Lane

- The final per-file synthesis should connect this chunk to neighboring chunks that define rawlane 0, the start of rawlane 1, the remainder of rawlane 3, and later rawlanes/register blocks.
- The merge lane should verify whether `DPCSSYS_CR4_RAWLANE3_DIG_PCS_XF_RX_ADAPT_FOM` is completed in the next chunk and avoid treating this boundary heading as a complete register group.
- If the repository contains generated register metadata outside the C headers, the merged report can compare this source against that generator output to assess whether the header is hand-edited or fully generated.
