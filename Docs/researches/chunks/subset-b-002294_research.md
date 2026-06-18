# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_0_sh_mask.h lines 14321-16696

## Purpose

This chunk is generated AMD DPCS 4.2.0 register field metadata for DCN 3.1-era display link encoders. It contains no executable C logic; it publishes preprocessor constants that describe bit positions (`__SHIFT`) and bit masks (`_MASK`) for DPCS raw-lane registers. Runtime code combines these field constants with matching register offsets from `dpcs_4_2_0_offset.h` and AMD register helper macros to read, update, and program display PHY/link-encoder state.

The requested range covers 2,376 source lines and 2,113 `#define` lines. It begins at the tail of RAWLANE0 PCS ATE TX override fields, covers most RAWLANE1 and RAWLANE2 digital PCS/FSM/IRQ/PMA/TX/RX control field maps, and ends inside early RAWLANE3 PCS RX override fields. Although the repository path is under a `ceph-client` source mirror, this file is AMDGPU display-driver hardware metadata, not Ceph or distributed filesystem code.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, includes, allocation paths, locks, or direct I/O operations in this chunk. The exposed interface is the macro namespace:

- `DPCSSYS_CR0_RAWLANE<n>_<block>_<register>__<field>__SHIFT`: bit offset for a field within a 16-bit DPCS register.
- `DPCSSYS_CR0_RAWLANE<n>_<block>_<register>__<field>_MASK`: mask for the same field.

Major register families in this slice:

- `DIG_PCS_XF_*`: PCS transmit/receive override and status fields for `PSTATE`, `LPD`, `WIDTH`, `RATE`, `MPLLB_SEL`, `MPLL_EN`, master MPLL state, reset/request handshakes, detect-RX request/result, TX/RX data enables, async TX, beacon, serial/parallel loopback, `ACK`, `EN_CTL`, and RX-valid override. It also defines RX adaptation fields, CDR/VCO/ref load values, LOS thresholds, equalizer controls (`EQ_ATT_LVL`, `EQ_VGA*`, `EQ_CTLE_*`, `EQ_DFE_TAP1`), RX adaptation acknowledgements/FOM, TX precursor/main/post cursor direction fields, lane numbering, and ATE override fields.
- `DIG_FSM_*`: raw-lane finite-state-machine override and monitor fields, including FSM jump address/start/override/break controls, current state, command-ready and ALU/wait/mask status bits, fast calibration/adaptation flags, common-calibration status for MPLL/RCAL, DCC flags/status, OCLA enables, TX EQ update status, IQ phase offset, and CR register/memory lock bits.
- `DIG_IRQ_CTL_*`: interrupt status, clear, and mask fields for RX reset/request/rate/pstate/adaptation, lane transceiver mode, phase-2 calibration, lane RX-to-TX loopback, DCC on-demand, TX reset, and TX request.
- `DIG_PMA_XF_*`: PMA-side lane/MPLL/supervisor override fields, TX/RX request and reset overrides, beacon/async/clock-sync/data-enable overrides, lane loopback, RTUNE request/ack, MPHY PWM/async/termination controls, and RX adaptation phase-adjust output.
- `DIG_TX_CTL_*` and `DIG_RX_CTL_*`: lane-local TX/RX control knobs such as TX FSM wait/allow-RXDET fields, TX clock enable/select, async beacon wait time, DCC continuous status, OCLA/UPCS enables, RX FSM enable, rate-change-in-P1, LOS mask count, RX data-enable override count, internal reference tracking count, and continuous off-cancel/adaptation status.

The chunk is dominated by RAWLANE1 and RAWLANE2: each has 1,085 visible lines in the assigned slice. RAWLANE0 contributes only the end of a preceding block and small PCS ATE/RX/TX override groups; RAWLANE3 starts near the end and is incomplete in this chunk.

## Control Flow

This header has no runtime control flow. The effective runtime path is generated-macro expansion:

1. `dcn31_resource.c` includes `dpcs/dpcs_4_2_0_offset.h` and this `dpcs_4_2_0_sh_mask.h`.
2. DCN31 resource macros build link encoder register tables with `DPCS_DCN31_REG_LIST(id)`.
3. The same file initializes `le_shift` and `le_mask` with `DPCS_DCN31_MASK_SH_LIST(__SHIFT)` and `DPCS_DCN31_MASK_SH_LIST(_MASK)`.
4. DC link encoder code later uses those tables with AMD register helpers to compose read-modify-write operations for DPCS registers.

The macros themselves do not encode sequencing. Correct behavior depends on caller-side ordering for lane reset/request handshakes, power-state changes, MPLL selection/enabling, link training, RX detection, adaptation/calibration, interrupt clear/mask operations, and PMA/PCS override enablement.

## State And Persistence Behavior

This chunk stores no software state and persists nothing by itself. It describes hardware-backed DPCS register fields. The represented hardware state includes:

- PCS/PMA control state for each raw lane: TX/RX request, reset, acknowledgement, power state, width, rate, MPLL selection, data enable, async/beacon mode, and loopback.
- RX adaptation and calibration state: AFE/DFE adaptation enablement, adaptation requests and continuous modes, off-cancel continuous mode, LOS/LFPS thresholding, VCO/reference load values, equalizer gains/taps, IQ phase offsets, and fast calibration bypass/status flags.
- FSM/debug state: FSM command and jump override, command-ready/status bits, CR locks, OCLA enables, DCC status, common-calibration init/done, and TX EQ update status.
- Interrupt state: sticky or latched status bits, write/clear bits, and masks for RX/TX events and lane-specific calibration or loopback events.
- PMA interface state: PMA lane/MPLL/supervisor overrides, TX/RX PMA data enables, PWM/MPHY controls, RTUNE, async drive controls, and RX adaptation phase-adjust mapping.

Retention and side effects are hardware-defined. Configuration fields usually persist until reprogrammed, lane power-gated, reset, or ASIC reset. Status, clear, IRQ, calibration, and handshake fields may be read-only, sticky, self-clearing, write-one-to-clear, or timing-sensitive; this header only names bit positions and masks, so consuming code must know the register semantics.

## Dependencies And Integration Points

This chunk must stay synchronized with:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_0_offset.h`, which provides matching `ixDPCSSYS_CR0_RAWLANE...` register offsets.
- DCN31 resource and link-encoder code, especially `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn31/dcn31_resource.c`, which includes this header and expands `DPCS_DCN31_REG_LIST`, `DPCS_DCN31_MASK_SH_LIST(__SHIFT)`, and `DPCS_DCN31_MASK_SH_LIST(_MASK)`.
- Generic AMDGPU/DC register helper infrastructure such as `reg_helper.h`, which turns register tables plus shift/mask tables into typed-looking register operations.
- Adjacent generated DPCS/DCN register headers for related ASIC revisions (`dpcs_4_2_2`, `dpcs_4_2_3`, and `dcn_4_1_0`) whose repeated field maps show this is a generated hardware ABI, not hand-authored logic.

There were no direct C references to individual field macros in the quick source search outside generated headers; the normal integration path is token-pasted macro-list expansion into link encoder register, shift, and mask tables.

## Risks And Edge Cases

- Shift/mask drift is the central risk. A wrong constant compiles cleanly but can update the wrong DPCS bit, corrupting lane power state, link rate/width, reset/request handshakes, MPLL selection, or interrupt masking.
- The chunk has artificial boundaries. RAWLANE0 and RAWLANE3 are partial here; complete per-file conclusions require adjacent chunk reports.
- Repeated raw-lane blocks are copy-sensitive. RAWLANE1 and RAWLANE2 are structurally similar, but lane-number, offset, and instance-selection mistakes can fail only on specific physical links or multi-display configurations.
- Many fields are override-enable/value pairs. Setting an override value without the matching enable bit, or leaving an override enabled after training/test flows, can produce hard-to-debug link failures.
- IRQ fields are side-effect-sensitive. Confusing status, mask, and clear fields can create stuck interrupts, missed lane events, or repeated hotplug/link-training recovery.
- Calibration/adaptation fields interact with analog timing. Incorrect fast-calibration, DCC, VCO, RX EQ, LOS, or IQ phase masks can produce rate-specific or cable-specific failures rather than immediate build-time errors.
- Reserved masks are present throughout the chunk. Read-modify-write paths must preserve reserved bits unless the hardware programming guide says otherwise.

## Test Signals

Useful validation is mostly generated-header consistency plus hardware behavior:

- Build AMDGPU/DC with DCN31 support enabled; `dcn31_resource.c` should compile while expanding `DPCS_DCN31_REG_LIST` and `DPCS_DCN31_MASK_SH_LIST` against this header.
- Mechanically verify every visible field in this line range has a coherent `__SHIFT`/`_MASK` pair, and that masks match the advertised bit width and shift.
- Compare RAWLANE1 and RAWLANE2 field layouts in this chunk against each other and against `dpcs_4_2_0_offset.h` lane offsets; expected repeated blocks should remain aligned.
- Diff the generated fields against AMD's authoritative DPCS 4.2.0 register database or neighboring generated headers where hardware compatibility is expected.
- Exercise DisplayPort/HDMI link bring-up across all DCN31 link encoder instances, especially displays mapped to RAWLANE1 and RAWLANE2.
- Test link-rate and lane-width changes, suspend/resume, hotplug, RX detect, training failure/retry, low-power transitions, and MST or multi-monitor configurations.
- Use debug logging and hardware status reads to watch for stuck `ACK`, reset/request mismatches, DCC/adaptation failures, unexpected IRQ storms, LOS false positives, and link instability after modesets.

## Cross-Chunk Notes

Earlier chunks own the beginning of RAWLANE0 and RAWLANE1 register definitions before line 14321. Later chunks continue RAWLANE3 after line 16696 and likely cover the rest of its PCS/FSM/IRQ/PMA/TX/RX controls. The final merged per-file document should combine all chunks before making whole-file claims about complete raw-lane coverage or every DPCS 4.2.0 field family.
