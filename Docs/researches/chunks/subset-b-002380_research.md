# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_2_sh_mask.h lines 102492-103633

## Scope And Purpose

This chunk covers the tail of AMDGPU's generated DPCS 4.2.2 shift/mask header. It is hardware register metadata, not executable logic: every `*_SHIFT` macro names a bit position and every `*_MASK` macro names the corresponding bit mask for fields in DPCS, raw lane, FSM, IRQ, PMA, TX/RX control, ATE, and RDPCSPIPE registers.

The covered range begins in the lane analog RX ATB measurement definitions, then moves through raw common memory data registers and a dense block of `DPCSSYS_CR4_RAWLANEX_DIG_*` register fields. The largest portion describes raw lane PCS/PMA TX and RX override inputs, PCS-visible inputs/outputs, adaptation controls, equalizer and termination controls, finite-state-machine status and fast-calibration flags, IRQ status/clear/mask fields, and TX/RX control helper registers. The chunk ends with a hand-annotated RDPCSPIPE PHY control exception for two RDPCSPIPE instances and the file's closing `#endif`.

This header is paired with `dpcs_4_2_2_offset.h`, which gives the register addresses such as `ixDPCSSYS_CR4_RAWLANEX_DIG_PCS_XF_TX_OVRD_IN` at `0xe000`, `ixDPCSSYS_CR4_RAWLANEX_DIG_FSM_FAST_FLAGS` at `0xe038`, `ixDPCSSYS_CR4_RAWLANEX_DIG_PCS_XF_TX_OVRD_IN_2` at `0xe0c8`, and `regRDPCSPIPE0_RDPCSPIPE_PHY_CNTL6` / `regRDPCSPIPE1_RDPCSPIPE_PHY_CNTL6`. The macros in this chunk let display and PHY code compose field writes and decode field reads without hard-coding bit arithmetic at each call site.

## Important APIs, Types, And Macros

There are no C functions, structs, enums, or runtime APIs in this slice. The effective API is the generated macro namespace consumed by AMD display register helpers such as `REG_GET`, `REG_UPDATE`, `FN`, `SF`, and `LE_SF`-style register-field tables.

The macro naming convention is consistent:

- `REGISTER__FIELD__SHIFT` gives the field's least-significant bit.
- `REGISTER__FIELD_MASK` gives the unshifted field mask in the register word.
- `RESERVED_*`, `NC*`, and `RESERVED_REG_*` macros document reserved or unused regions that callers should preserve unless a hardware sequence explicitly says otherwise.

Key register families in this chunk include:

- Analog/test fields: `DPCSSYS_CR4_LANEX_ANA_RX_ATB_MEAS3`, `MEAS4`, `ATB_FRC`, and `RX_RESERVED1` cover ATB measurement selection, calibration reference forcing, and reserved lane analog bits.
- Raw memory windows: `DPCSSYS_CR4_RAWMEM_DIG_ROM_CMN0_B0_R0` and `DPCSSYS_CR4_RAWMEM_DIG_RAM_CMN0_B0_R0` expose 16-bit `DATA` fields for common ROM/RAM access.
- Raw PCS TX controls: `DPCSSYS_CR4_RAWLANEX_DIG_PCS_XF_TX_OVRD_IN`, `_IN_1`, `_IN_2`, `TX_PCS_IN`, `TX_OVRD_OUT`, and `TX_PCS_OUT` describe TX reset/request, power state, low-power disable, width, rate, MPLL selection/enables, master MPLL override, async data/enables, detect-RX request, vboost, iboost, beacon, loopback, data enable, ACK, and detection-result fields.
- Raw PCS RX controls: `RX_OVRD_IN`, `_IN_1` through `_IN_3`, `RX_PCS_IN` through `_IN_4`, `RX_OVRD_OUT`, `RX_PCS_OUT`, `RX_OVRD_OUT_1`, and `RX_OVRD_OUT_2` describe rate/width/pstate/lpd overrides, adaptation AFE/DFE controls, loopback, RX data enable, LOS threshold and LFPS overrides, VCO/ref load overrides, equalizer values, reset/request/ACK, clock enable, and RX-valid override.
- Adaptation and equalization status: `RX_ADAPT_ACK`, `RX_ADAPT_FOM`, `RX_TXPRE_DIR`, `RX_TXMAIN_DIR`, `RX_TXPOST_DIR`, `RX_EQ_DELTA_IQ_OVRD_IN`, `RX_EQ_OVRD_IN_1`, `RX_EQ_OVRD_IN_2`, and `RX_PH2_CAL` expose adaptation handshakes, figure of merit, direction hints, EQ/CTLE/DFE override values, and phase-2 calibration request/ack bits.
- ATE and loop controls: `PCS_XF_ATE_OVRD_IN`, `PCS_XF_ATE_RX_OVRD_IN*`, `PCS_XF_ATE_TX_OVRD_IN*`, and `PCS_XF_MASTER_MPLL_LOOP` provide manufacturing/test override equivalents for normal RX/TX paths plus MPLLA/MPLLB loop enables.
- Raw FSM controls/status: `FSM_FSM_OVRD_CTL`, `FSM_MEM_ADDR_MON`, `FSM_STATUS_MON`, many `FSM_FAST_*` bits, `FSM_FAST_FLAGS`, `FSM_CR_LOCK`, `FSM_TX_DCC_FLAGS`, `FSM_TX_DCC_STATUS`, `FSM_OCLA`, `FSM_TX_EQ_UPDATE_FLAG`, `FSM_CMNCAL_*_STATUS`, and `FSM_RX_IQ_PHASE_OFFSET` expose state-machine jump/command/debug controls, fast calibration/adaptation bypasses, common calibration state, lock controls, and observability controls.
- IRQ controls: `IRQ_CTL_*` registers define RX/TX reset/request/rate/pstate/adaptation/phase-calibration/loopback/DCC interrupt status, clear, and mask fields. Most individual status and clear registers are one-bit flags with upper bits reserved; `IRQ_MASK` and `IRQ_MASK_2` aggregate mask bits.
- Raw PMA controls: `PMA_XF_LANE_*`, `SUP_*`, `TX_*`, `RX_*`, `MPHY_*`, `RX_ADAPT_OVRD_OUT`, and `LANE_RTUNE_CTL` fields cover MPLL lane enables, override enables, PMA-visible TX/RX reset/request/data/clock controls, superblock controls, RTUNE, and MPHY override handoff.
- TX/RX control helper registers: `TX_CTL_TX_FSM_CTL`, `TX_CTL_TX_CLK_CTL`, `TX_CTL_TX_DCC_CONT_STATUS`, `TX_CTL_OCLA`, `TX_CTL_UPCS_OCLA`, `RX_CTL_RX_FSM_CTL`, `RX_CTL_RX_LOS_MASK_CTL`, `RX_CTL_RX_DATA_EN_OVRD_CTL`, `RX_CTL_OFFCAN_CONT_STATUS`, `RX_CTL_ADAPT_CONT_STATUS`, and `RX_CTL_UPCS_OCLA` expose coarse FSM, clock, data-enable, LOS, continuous calibration/adaptation, and OCLA debug controls.
- RDPCSPIPE tail: `RDPCSPIPE0_RDPCSPIPE_PHY_CNTL6` and `RDPCSPIPE1_RDPCSPIPE_PHY_CNTL6` define `RDPCS_PHY_DPALT_DP4`, `RDPCS_PHY_DPALT_DISABLE`, and `RDPCS_PHY_DPALT_DISABLE_ACK` fields at bits 16-18.

The RDPCSPIPE fields are visibly integrated by `drivers/gpu/drm/amd/display/dc/dio/dcn31/dcn31_dio_link_encoder.h`, where `DPCS_DCN31_MASK_SH_LIST(mask_sh)` includes `LE_SF(RDPCSPIPE0_RDPCSPIPE_PHY_CNTL6, RDPCS_PHY_DPALT_DP4, mask_sh)`, `RDPCS_PHY_DPALT_DISABLE`, and `RDPCS_PHY_DPALT_DISABLE_ACK`.

## Control Flow And Runtime Use

This file has no runtime control flow. Its only control behavior is preprocessor expansion during compilation.

Typical use is indirect:

1. A DCN/DPCS implementation includes the relevant offset and shift/mask headers for the ASIC generation.
2. Register-list macros bind register addresses from `dpcs_4_2_2_offset.h` with field masks and shifts from this header.
3. Register helper macros turn a symbolic field access into masked read/modify/write operations, using the `*_MASK` and `*_SHIFT` constants to place or extract values.
4. The hardware register write or read is performed through AMD display's register access layer.

For the raw `DPCSSYS_CR4_RAWLANEX_DIG_*` register families, the likely runtime sequences are low-level PHY bring-up, link training, manufacturing test, diagnostics, and recovery flows that force or observe TX/RX requests, power state, width/rate, MPLL state, PMA/PCS handshakes, adaptation, calibration, interrupts, and loopback. The chunk itself does not enforce the ordering of those sequences; it only exposes the bit layout used by the implementation code and firmware-facing paths.

The RDPCSPIPE tail is more directly connected to DisplayPort alternate-mode handling. The DCN31 link encoder field list includes these mask/shift definitions so code can set `RDPCS_PHY_DPALT_DISABLE`, detect `RDPCS_PHY_DPALT_DISABLE_ACK`, and mark `RDPCS_PHY_DPALT_DP4` when controlling DP alternate-mode PHY behavior.

## State And Persistence Behavior

The macros do not allocate memory, store state, perform I/O, or persist anything by themselves. Their state impact occurs only when consumers use them to access memory-mapped hardware registers.

Hardware state affected through these fields is persistent at the register level until overwritten, reset, power-gated, or changed by the PHY microcontroller/state machines. In particular, override-enable fields can force TX/RX reset, request, data-enable, loopback, MPLL, termination, equalizer, adaptation, and PMA handoff values away from autonomous hardware control. IRQ clear fields are write-sensitive hardware controls: writing the wrong bit can acknowledge an interrupt event rather than merely update software bookkeeping.

Most masks in this slice are 16-bit hardware-field masks expressed as 32-bit-looking constants with an `L` suffix, often `0x0000....L`. Consumers should still treat them as register-field masks rather than generic 32-bit software flags. Reserved masks define bits that should generally be preserved across read/modify/write cycles.

## Dependencies And Integration Points

This chunk depends on the generated AMD register-header convention. Address macros come from `dpcs_4_2_2_offset.h`, while this file supplies field placement. The display code's register helper layer supplies the functions and macros that actually combine addresses, masks, shifts, and values.

Important integration points include:

- AMD Display Core register helper infrastructure under `drivers/gpu/drm/amd/display/dc/inc/reg_helper.h`, which defines the common `REG_GET*` and `REG_UPDATE*` style operations used throughout DC.
- ASIC-specific register lists and field lists in display modules, especially DCN/DPCS link encoder code. The observed DCN31 link encoder uses the RDPCSPIPE fields from this chunk through `DPCS_DCN31_MASK_SH_LIST`.
- Matching DPCS generations, such as `dpcs_4_2_0_sh_mask.h` and `dpcs_4_2_3_sh_mask.h`, which carry similar field definitions. Differences in literal formatting and availability between generations are compatibility signals, not cleanup opportunities.
- Hardware/firmware link-training, PHY, ATE, and diagnostics paths that need raw lane PCS/PMA control or observation.

The final per-file report should reconcile this tail with earlier chunks of the same header because some register families begin before line 102492 and this slice starts mid-register at `DPCSSYS_CR4_LANEX_ANA_RX_ATB_MEAS3`.

## Risks And Edge Cases

Generated shift/mask headers are hardware ABI. A one-bit error in a mask or shift can redirect a write to another hardware field, leaving display link training, PHY power sequencing, calibration, interrupts, or DP alternate-mode handling broken in ways that may be ASIC-, board-, or monitor-specific.

Reserved fields are a particular risk. Many registers include high-bit reserved masks such as `RESERVED_15_1`, `RESERVED_15_2`, `RESERVED_15_6`, or `RESERVED_15_8`. Register writes should use helpers that preserve unrelated fields unless the hardware programming guide explicitly requires a full-register write.

Override-enable fields are operationally dangerous if left asserted. The chunk exposes many `*_OVRD_EN`, `*_OVRD_VAL`, ATE override, and PMA/PCS override controls. A debug or recovery path that enables one of these bits and fails to restore autonomous control can pin reset/request/data-enable, force an unsupported rate/width/pstate, disrupt calibration, or hide a real PHY handshake failure.

Interrupt clear registers are easy to misuse because they are represented as ordinary field masks. `IRQ_CTL_*_CLR` writes should be audited for write-one-to-clear semantics and for avoiding accidental clears of concurrent hardware events.

The RDPCSPIPE block contains an explicit source comment: `TODO: verify this still applies to DCN315` and `Hack. RDPCSPIPE only has 2 instances.` The adjacent offset header also aliases `regRDPCSPIPE2_RDPCSPIPE_PHY_CNTL6` to the same address as instance 0. Any future ASIC or DCN315-related work should verify instance count, address aliasing, and field validity before copying these definitions into new generation headers.

This chunk also differs from nearby generation headers in literal formatting. For example, DPCS 4.2.3 contains equivalent-looking field masks with shorter 16-bit-style literals such as `0x0003L`, while this 4.2.2 header often uses `0x00000003L`. That difference should not be normalized manually unless the generator or style contract is intentionally changed.

Because the raw-lane register space spans many subsystems, normal display hotplug testing may not exercise ATE, OCLA, IRQ clear, FSM override, PMA handoff, and fast-calibration fields. Regressions can survive compile and basic boot tests unless validation includes targeted PHY/debug flows.

## Test Signals

Build validation should compile every DCN/DPCS configuration that includes `dpcs_4_2_2_sh_mask.h` and related offset headers. A broken macro name, missing field, or duplicate conflicting definition should surface as compile failures in register-list users.

Static consistency checks should compare every field's mask against its shift and expected width. For one-bit fields, `MASK == 1 << SHIFT`; for multi-bit fields, the contiguous mask width should match the field's documented range. These checks are especially valuable for dense registers such as `PCS_XF_TX_OVRD_IN`, `PCS_XF_RX_PCS_IN`, `FSM_STATUS_MON`, `FSM_FAST_FLAGS`, `IRQ_CTL_IRQ_MASK`, and ATE override registers.

Header-pair validation should verify that every register in this chunk has a matching address macro in `dpcs_4_2_2_offset.h` when it is an indexed `DPCSSYS_CR4_*` register, and that RDPCSPIPE fields match the available `regRDPCSPIPE*_RDPCSPIPE_PHY_CNTL6` address macros.

Hardware or simulator tests should exercise link bring-up, DP alternate-mode disable/ack handling, lane rate/width/pstate changes, reset/request handshakes, MPLL selection, RX adaptation, LOS threshold behavior, TX/RX data enable, loopback controls, and IRQ mask/status/clear flows on the relevant ASIC generation.

Debug and manufacturing test coverage should include ATE override paths, OCLA enable fields, FSM override/status observation, PMA override handoff, and continuous adaptation/calibration status. These fields are less likely to be covered by normal display modeset tests but are prominent in this chunk.

Regression tests should include read/modify/write preservation of reserved bits and paired enable/value behavior for override controls. For DPALT-specific behavior, tests should confirm that setting `RDPCS_PHY_DPALT_DISABLE` produces the expected `RDPCS_PHY_DPALT_DISABLE_ACK` transition on the intended RDPCSPIPE instance and does not accidentally target an aliased or nonexistent pipe.
