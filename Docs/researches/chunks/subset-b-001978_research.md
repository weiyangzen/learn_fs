# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_2_0_sh_mask.h lines 119861-122338

## Scope

This chunk is a generated AMD DCN 3.2.0 shift/mask header slice for C20 PHY CR1 lane digital registers. It contains only C preprocessor constants: each register field has a `__SHIFT` macro and, usually in the same commented register block, a corresponding `_MASK` macro. The covered range starts in the middle of `C20_PHY_CR1_RAWLANEX_DIG_TX_IRQ_CTL_TX_REQ_IRQ`, runs through TX/RX lane-control, PCS/FW handshake, IRQ, FSM, and always-on calibration/adaptation fields, and ends at the first field of `C20_PHY_CR1_RAWLANEAONX_DIG_RX_ADAPT_DONE_BANK_1`; the rest of that last register's masks are in the following chunk.

## Purpose

The header maps hardware bit layouts for DCN 3.2.0 display PHY lane 1. Consumers pair these field definitions with matching register offsets from `dcn_3_2_0_offset.h` and AMD display register-helper macros to read, write, mask, clear, or preserve individual hardware fields without hard-coding bit positions in C logic.

This chunk specifically describes:

- `RAWLANEX_DIG_TX_IRQ_CTL_*` and `RAWLANEX_DIG_RX_IRQ_CTL_*` interrupt status, mask, enable, and clear fields for TX/RX lane events.
- `RAWLANEX_DIG_TX_CTL_*` and `RAWLANEX_DIG_RX_CTL_*` control/status fields for lane rate, width, power, clock, termination, adaptation, margining, CDR, IQ, phase, and rate-IRQ acknowledgment.
- `RAWLANEX_DIG_TX_PMA_XF_*`, `RAWLANEX_DIG_RX_PCS_XF_*`, `RAWLANEX_DIG_RX_FW_XF_*`, and `RAWLANEX_DIG_RX_PMA_XF_*` cross-interface override/handshake fields between firmware, PCS, PMA, and lane state machines.
- `RAWLANEX_DIG_FSM_*` state-machine override, monitor, scratch, lock, fast-path, and skip-calibration flags.
- `RAWLANEAONX_DIG_TX_*` and `RAWLANEAONX_DIG_RX_*` always-on calibration, DCC, IQ, adaptation, and banked measurement fields.

## Important Macros And Field Groups

The TX IRQ/control section covers single-bit status/clear registers such as `TX_REQ_IRQ_CLR`, `RX2TX_PAR_LB_EN_IRQ`, `RX2TX_PAR_LB_DIS_IRQ`, `RTUNE_IRQ`, `TX_TERM_CTRL_IRQ`, and `LANE_XCVR_MODE_IRQ`, plus `TX_CTL_FSM_CTL`, whose fields enable TX lane rate, width, MPLLB select, misc, termination, DCC control/bypass, and calibration-done interrupts. Adjacent TX control fields select clock source (`TX_CLK_SEL`), expose continuous offset-cancel status, acknowledge rate IRQs, publish 10-bit termination code, report firmware power-up done, and enable MPLLA/MPLLB resistor calibration.

The TX PMA transfer section provides override-value and override-enable pairs for MPLLA/MPLLB lane enables, RX-to-TX parallel loopback enable, TX request/reset, and supervisor state; it also exposes PMA acknowledgments and lane retune request/acknowledge bits. These are the low-level knobs used when firmware or debug logic needs to force PMA-facing lane states rather than letting the normal state machine drive them.

The RX PCS/FW transfer section defines override inputs for reset/request, P-state, low-power detect, data enable, invert, CDR SSC enable, adaptation request/progress, margin IQ/VDAC, margin status, recalibration force/skip, termination control, rate/width/VCO frequency, DCC/DFE/EQ controls, and RX2TX parallel loopback. It also includes readback/status fields for ACK, electrical idle, adapt done, link good, power state, margining, termination, and programmed lane parameters. Context configuration registers (`RX_PCS_XF_CNTX_CFG_*`) encode adaptation/margining/frequency-context behavior, including FOM, cycle counts, control masks, data width/rate, MPLL select, REFCLK config, PCS divider, VCO frequency, CDR mode, and margin IQ error thresholds.

The RX IRQ section groups mask and enable flags for RX request, rate, P-state, adaptation request/disable, reset, termination, and receiver margining events. It then provides individual one-bit status and clear registers for those same events. Clear registers use `_CLR`-named fields and should be treated as write-to-clear hardware semantics by consumers, even though the header itself only describes masks.

The RX control section publishes lane termination code, continuous offset-cancel/adaptation status, adaptation mode/select, PPM drift plus validity bit, CDR detector state, PMA misc controls (`RX_CDR_TRACK_EN`, DFE tap1 adaptation override, delta-IQ and margin-IQ scale disable), adaptation FOM/readback values, phase-adjust/IQ read/write values, margin deltas and status/error, and `RX_CTL_FSM_CTL` interrupt enables for rate, width, VCO frequency, misc, termination, DCC control/bypass, DFE bypass, EQ, and calibration completion.

The lane FSM section exposes debug/control registers: jump address/enable/start/override, jump bank, memory breakpoints, current memory address, state monitor flags, firmware configuration stage, twelve 16-bit scratch registers, CR register/memory locks, and many one-bit fast/skip flags. The skip flags cover TX DCC rate/startup/continuous/range calibration and RX AFE, DFE, IQ, phase, DCC, signal detect, VGEN, half/full-rate, error, bypass, VGA slicer, buffer, adaptation reload, DFE coarse/fine adaptation, CTLE, ATT, and margining operations. These fields are high risk because setting them changes PHY bring-up/calibration coverage rather than just reporting state.

The always-on TX section includes firmware state registers (`TX_FW_STATES_0/1`), an additional memory breakpoint, SRAM recording controls and counters, CCA loop/wait counters, startup/continuous algorithm controls, TX fast flags, HP protection and lane transceiver mode override inputs, initial power-up done, TX override input, per-bank MPLLA/MPLLB DCC full/half/range fields for banks 0-3, per-bank MPLLA/MPLLB calibration-done bits, aggregate calibration-done status, selected bank, and current DCC code/diff/common-mode readbacks.

The always-on RX section begins a large calibration/adaptation region. It includes startup calibration skip controls, startup adaptation skip controls for banks 0 and 1, continuous algorithm skip controls, RX fast flags, VGEN and signal-detect calibration readbacks, many VDAC/IDAC offsets for reference, DFE, CTLE, VGA, slicer, buffer, phase, data, bypass, and error paths, IQ calibration limits/reset/adjust, per-bank DCC/IQ/cal-done values for banks 0-3, aggregate DCC/IQ/cal-done readbacks, IQ controls, adaptation IQ limits and error slicer mode, and banked adaptation results for banks 0 and 1 (`ATT`, `VGA`, `CTLE`, `DFE_TAP1`-`DFE_TAP5`, DFE tap1 offsets, IQ, reference error, and adapt-done). The final `RX_ADAPT_DONE_BANK_1` block is incomplete in this chunk and continues after line 122338.

## Control Flow

There is no executable control flow in this file. Runtime flow is imposed by consumers:

1. DCN32 code includes `dcn_3_2_0_offset.h` and `dcn_3_2_0_sh_mask.h`.
2. Register helper macros compose a register address, field mask, and shift value.
3. Driver code reads or updates the backing MMIO register.
4. Hardware/firmware state machines observe control bits or update status bits asynchronously.

For this chunk, the implicit hardware flows are TX/RX lane power-up, request/acknowledge handshakes, interrupt assertion and clearing, receiver margining, RX adaptation, DCC/IQ calibration, and FSM debug/override paths. The header does not enforce ordering; sequencing must be supplied by the PHY bring-up, link-training, diagnostic, or firmware code that uses these fields.

## State And Persistence Behavior

All state described here lives in hardware registers, not in kernel heap, files, or persistent storage. Values may be volatile status bits, sticky interrupt bits, write-to-clear bits, writable configuration bits, firmware scratch/state registers, or calibration result banks.

Important state categories:

- IRQ status and clear fields are transient or sticky hardware event state; `_CLR` fields should not be treated like ordinary latched configuration.
- Override-enable fields persist in the register until firmware/driver clears them, and can force PMA/PCS/FW paths away from normal lane state-machine ownership.
- FSM scratch, breakpoint, jump, and lock fields are diagnostic/control state in the PHY micro-sequencer interface.
- Calibration and adaptation result banks persist as current hardware result registers until recalibration, bank selection, reset, or power transition changes them.
- Reserved masks show bits that callers must preserve during read-modify-write operations.

## Dependencies

This header depends on the generated register database staying consistent with:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_2_0_offset.h`, which provides the corresponding `ixC20_PHY_CR1_*` register offsets.
- AMD display register helper macros (`REG_GET`, `REG_SET`, `REG_UPDATE`, and related generated table macros) that expect `regFIELD`, `FIELD__SHIFT`, and `FIELD_MASK` naming to line up.
- DCN32 translation units that include this generated pair, including `display/dmub/src/dmub_dcn32.c`, `amdgpu/gmc_v11_0.c`, `display/dc/irq/dcn32/irq_service_dcn32.c`, `display/dc/resource/dcn32/dcn32_resource.c`, `display/dc/gpio/dcn32/hw_translate_dcn32.c`, `display/dc/gpio/dcn32/hw_factory_dcn32.c`, and `display/dc/clk_mgr/dcn32/dcn32_clk_mgr.c`.
- Sibling generated headers such as `include/asic_reg/dpcs/dpcs_4_2_3_sh_mask.h`, which contain closely matching C20 PHY layouts for DPCS and are useful for cross-checking generation drift but should not be substituted blindly.

## Integration Points

This chunk is source-tree-aligned with DCN 3.2.0 ASIC metadata. It is not a public C API and defines no types or functions. Integration happens through generated names consumed by DCN32 register tables and low-level register access helpers. Because direct `rg` checks in the C sources show the exact C20 PHY field names are not commonly referenced outside generated headers, most use is likely indirect or available for firmware/debug paths rather than hand-written call sites in normal display code.

The most important integration boundary is name consistency: each `C20_PHY_CR1_*` field macro must match the register name and field spelling expected by any generated table entry or helper expression. A rename, missing `_MASK`, wrong bit width, or copied value from a different CR instance can compile cleanly if unused directly, but fail when a board, firmware path, or debug feature touches that lane.

## Risks

- Reserved bits are large in many registers. Drivers must use masks and read-modify-write helpers that preserve reserved fields rather than writing whole 16-bit constants casually.
- `_CLR` registers are likely write-to-clear event controls. Treating them as persistent control bits can drop or repeatedly clear interrupts.
- Skip/fast calibration fields can make the PHY appear to bring up faster while bypassing required calibration, causing marginal links, display instability, or failures only on certain boards, rates, lanes, or temperatures.
- Override-enable bits can leave PMA/PCS/FW paths forced after diagnostics, blocking normal firmware ownership.
- Banked DCC/IQ/adaptation fields must be read with the correct bank context. Mixing bank 0/1/2/3 results or assuming the aggregate readback matches a selected bank can corrupt diagnostics.
- This chunk ends mid-register for `RX_ADAPT_DONE_BANK_1`; reconciliation with the next chunk is required before producing a complete per-file account of that block.
- Similar macros exist for CR0, CR2, CR3, CR4, and DPCS families. Copying field layouts across instances or ASIC revisions risks subtle bit-position drift.

## Test Signals

Useful validation signals for changes touching this generated range:

- Build DCN32-enabled AMDGPU/display configurations that include `dcn_3_2_0_offset.h` and `dcn_3_2_0_sh_mask.h`, catching missing symbols or name drift.
- Compare this range against AMD's authoritative register database and sibling generated headers for C20 PHY CR1 to ensure every `__SHIFT` has the correct `_MASK` and reserved mask.
- Exercise display link bring-up across lane rates and widths, watching for RX/TX lane IRQs, rate acknowledgments, calibration-done status, CDR lock behavior, and stable link training.
- Run hotplug, suspend/resume, and display mode-set tests that force PHY power transitions and recalibration.
- If firmware diagnostics expose these registers, verify that override bits are cleared after tests, interrupt clear bits only clear intended events, and calibration/adaptation banks report coherent values.
- For margining or signal-integrity workflows, validate RX margin IRQ/status/error fields, IQ/VDAC deltas, adaptation FOM, DFE tap values, and banked adapt-done bits against hardware traces.
