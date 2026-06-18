# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_2_0_sh_mask.h lines 178125-180623

## Purpose

This chunk is generated AMD DCN 3.2 register field metadata. It contains no executable C logic; it publishes preprocessor constants for bit shifts and bit masks used to read or update fields inside C20 PHY CR3 RAWLANEAON display PHY registers. Consumers combine these macros with the matching register offsets from `dcn_3_2_0_offset.h` and the AMDGPU display register helpers to program PHY calibration, adaptation, lane control, signal detection, and status fields.

The range is a large mid-file slice of `dcn_3_2_0_sh_mask.h`. It starts inside the RAWLANEAON0 RX DCC calibration-bank definitions, covers the rest of RAWLANEAON0 RX calibration/adaptation/control fields, covers a broad RAWLANEAON1 TX and RX field set, and then enters RAWLANEAON2 TX plus the start of RAWLANEAON2 RX startup-calibration control. The requested range contains 2,499 lines, 430 register-comment blocks, and 2,069 `#define` lines: 1,035 `__SHIFT` definitions and 1,034 `_MASK` definitions. The one-count difference is due to the chunk starting in the middle of a register block.

Although the path is under a local `ceph-client` source mirror, this header is AMDGPU display hardware metadata. It does not implement Ceph or distributed filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, global variables, includes, allocation paths, or locking primitives in this chunk. The public interface is the generated macro namespace:

- `C20_PHY_CR3_RAWLANEAON<n>_<register>__<field>__SHIFT`: bit position for a field inside a 16-bit PHY register.
- `C20_PHY_CR3_RAWLANEAON<n>_<register>__<field>_MASK`: bit mask for the same field.
- `RESERVED_*` field macros: generated masks/shifts for unused or reserved bits that should usually be preserved by read-modify-write helpers.

The major field families are:

- RAWLANEAON0 RX DCC and IQ calibration fields: `RX_DCC_*_BANK_1` through `BANK_3`, `RX_CAL_BANK_SEL`, `RX_DCC_*_CODE`, `RX_IQ_CAL`, `RX_CAL_DONE`, `RX_IQ_CTL_*`, and IQ limit/range fields.
- RAWLANEAON0 RX adaptation fields: ATT, VGA, CTLE, DFE TAP1 through TAP5, DFE tap1 offset quadrants (`DEH`, `DEL`, `DOH`, `DOL`, `EEH`, `EEL`, `EOH`, `EOL`), valid bits, IQ adaptation, reference-error, and adapt-done fields for banks 0 and 1.
- RAWLANEAON0 RX/TX interaction and signal fields: TX equalization direction polarity, TX pre/main/post thresholds, 29 generic `RX_ADPT_CTL_*` full-word controls, CDR detector/recovery controls, RX override inputs/outputs, PMA override outputs, RX input state, and RX signal-detect output state.
- RAWLANEAON1 TX state and control fields: firmware state registers, memory breakpoint, SRAM recovery controls, CCA counters, startup/continuous algorithm skip bits, fast flags, high-power protection, transceiver mode, power-up done, TX disable override, MPLLA/MPLLB DCC bank values, TX calibration done bits, TX DCC code fields, TX calibration-bank select, and TX disable input.
- RAWLANEAON1 RX startup/calibration/adaptation fields: startup calibration skip controls, startup adaptation skip controls, continuous algorithm skip controls, fast RX flags, VGEN/signal-detect/AFE/reference/DFE VDAC and IDAC offsets, RX IQ calibration ranges and reset/adjust values, RX DCC banked calibration values, current RX DCC code fields, IQ controls, adaptation bank values, RX/TX equalization thresholds, generic adaptation control words, CDR/signal-detect controls, and RX input/output state.
- RAWLANEAON2 TX fields: the same broad TX state, SRAM recovery, startup/continuous DCC controls, fast flags, protection/mode, MPLLA/MPLLB DCC bank values, calibration-done status, DCC code fields, calibration-bank select, and TX disable input.
- RAWLANEAON2 RX startup-calibration fields: the chunk includes all `RX_STARTUP_CAL_ALGO_CTL_0` field shifts/masks and starts `RX_STARTUP_CAL_ALGO_CTL_1` before the requested range ends.

Common bit layouts repeat heavily. Many DCC and IQ calibration registers split 16 bits into low-byte `CM_VAL` or half-rate fields and high-byte `DIFF_VAL` or full-rate fields (`0x00FFL` and `0xFF00L`). Bank-select registers use 2-bit selectors, DCC range fields use 4-bit full/half values, calibration-done fields use single-bit done flags, DFE tap offsets use 6-bit fields, and several control/status registers are full 16-bit `VAL` fields.

## Control Flow

This header has no runtime control flow. Runtime code supplies all sequencing:

1. DCN 3.2 display code includes `dcn_3_2_0_offset.h` and `dcn_3_2_0_sh_mask.h`.
2. Register table macros paste hardware block/register names into matching offset and field-mask symbols.
3. Driver helper macros such as `REG_READ`, `REG_WRITE`, `REG_UPDATE`, `REG_SET`, `REG_GET`, and related wait/poll helpers use these constants to isolate fields without corrupting neighboring bits.
4. Hardware sequencing code, firmware handoff paths, or diagnostics decide when to poll done bits, select calibration/adaptation banks, update override-enable/value pairs, or program skip/fast-mode bits.

The macros do not encode ordering. Correct use still depends on external PHY bring-up and link-training code sequencing clocks, resets, power state, firmware ownership, DCC/IQ/AFE/DFE calibration, adaptation bank selection, signal-detect filtering, CDR recovery, and suspend/resume restore.

## State And Persistence Behavior

The chunk stores no software state and persists nothing to disk. It describes MMIO-backed display PHY state. The represented hardware state includes:

- RX DCC calibration data for full-rate and half-rate operation across data, bypass, and phase paths, with multiple recalibration banks and current-code views.
- RX IQ, VGEN, reference, AFE, CTLE, VGA, DFE, and signal-detect calibration offsets and done/status bits.
- RX adaptation results for ATT, VGA, CTLE, DFE taps, DFE tap1 offsets, IQ, reference error, and adapt-done state across adaptation banks.
- TX DCC calibration values and status for MPLLA/MPLLB and current TX DCC code values.
- Control and override state for TX/RX startup algorithms, continuous algorithms, fast paths, high-power protection, lane transceiver mode, disable/termination/signal-detect/VREF controls, and CDR recovery.
- Debug or recovery state such as TX firmware states, TX memory breakpoint, and TX SRAM recovery registers.

Persistence is hardware-defined. Configuration fields generally retain values until rewritten, reset, power-gated, or restored during resume. Done/status bits may be read-only, sticky, self-clearing, firmware-owned, or valid only after a calibration/adaptation sequence. Override registers typically pair a desired value bit with an override-enable bit; writing only one side can leave hardware in an unintended mixed software/hardware-controlled state. This generated header does not distinguish read-only, write-one-to-clear, volatile, or firmware-owned semantics.

## Dependencies And Integration Points

This chunk depends on AMD's generated DCN 3.2 register database and must match:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_2_0_offset.h`, which provides the matching `ixC20_PHY_CR3_*` register offsets.
- Other generated DCN 3.2 headers for the same ASIC revision, especially base/address metadata consumed by the AMDGPU display register helpers.
- The display PHY programming model for C20 PHY CR3 RAWLANEAON lane registers. The field names imply PLL DCC, RX DCC, IQ, AFE, CTLE, VGA, DFE, CDR, signal-detect, and TX/RX lane control contracts that are enforced by hardware and firmware, not by this header.

Direct include sites for the matching DCN 3.2 generated headers in this tree include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn32.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn32/irq_service_dcn32.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn32/hw_translate_dcn32.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn32/hw_factory_dcn32.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn32/dcn32_clk_mgr.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn32/dcn32_resource.c`

The RAWLANEAON macros are lower-level PHY field definitions. Many callers do not reference the literal names directly; they flow through generated register table macros, indirect PHY accessors, DMUB firmware interfaces, or token-pasted register helpers. The matching offset header exposes nearby `ixC20_PHY_CR3_*` PHY addresses, and this mask header supplies the field-level contract for preserving adjacent bits during updates.

## Risks And Edge Cases

- Generated bitfield drift is the central risk. A wrong shift or mask compiles cleanly but can program the wrong field in a hardware PHY register, causing link bring-up, calibration, or resume failures that may appear only on specific connectors or link rates.
- The chunk starts mid-register. Lines 178125-178126 are masks for `RAWLANEAON0_DIG_RX_DCC_FULL_DATA_BANK_1`; the corresponding comment and shifts are in the previous chunk. File-level conclusions about that register must merge adjacent chunks.
- The chunk ends mid-register-family. It includes `RAWLANEAON2_DIG_RX_STARTUP_CAL_ALGO_CTL_0` completely and starts `RAWLANEAON2_DIG_RX_STARTUP_CAL_ALGO_CTL_1`; the remaining masks and later RAWLANEAON2 RX definitions are outside this range.
- Repeated lane families are copy-sensitive. RAWLANEAON0, RAWLANEAON1, and RAWLANEAON2 contain many structurally identical fields, but a single instance typo can affect only one PHY lane or connector path.
- Reserved-bit masks are present but do not enforce preservation. Callers must use read-modify-write helpers correctly and avoid writing full literal values that clobber reserved or firmware-owned bits.
- Calibration and adaptation fields are sequencing-sensitive. Updating DCC/IQ/DFE/AFE fields while a lane is active, clock-gated, firmware-owned, or in the wrong bank can produce unstable links or ignored writes.
- Override fields have paired enable/value semantics. Setting override values without the matching enable bit, or leaving override enables asserted after diagnostics, can force stale RX/TX state.
- Status and done bits may be volatile or sticky. Poll loops need correct timeouts and must not infer success from a stale bank or a previous calibration run.
- Several field names use similar concepts across TX and RX (`DCC`, `CAL_DONE`, `FAST_FLAGS`, `IN_0`, `OVRD_IN_0`). Token-paste or manual macro mistakes can cross TX/RX namespaces while still compiling.

## Test Signals

Useful validation is mostly generated-header consistency plus hardware behavior:

- Build AMDGPU/DC with DCN 3.2 enabled; missing or renamed macros should fail in DCN 3.2 resource, IRQ, GPIO, clock-manager, and DMUB translation units that include this header.
- Mechanically verify that every complete register-comment block in lines 178125-180623 has matching `__SHIFT` and `_MASK` definitions for the same field names. The only expected mismatch in this chunk is the artificial start inside `RAWLANEAON0_DIG_RX_DCC_FULL_DATA_BANK_1`.
- Diff the RAWLANEAON0/1/2 repeated register families against AMD's authoritative DCN 3.2 register database and against nearby generated headers such as `dpcs_4_2_3_sh_mask.h` where the C20 PHY layout is expected to align.
- Exercise DCN 3.2 systems with connectors that use the affected PHY lanes: cold boot, hotplug, link training, link-rate and lane-count changes, display blank/unblank, suspend/resume, and runtime power transitions.
- Validate RX calibration/adaptation paths by watching for DCC/IQ/calibration done bits, stable CDR recovery, signal-detect transitions, and absence of repeated training failures or PHY timeouts.
- Validate TX calibration paths by checking MPLLA/MPLLB DCC calibration completion, TX disable/mode behavior, and successful DP/HDMI link bring-up after power transitions.
- Test high-bandwidth and marginal-link scenarios where CTLE/VGA/DFE adaptation matters; failures may surface as intermittent link loss, CRC errors, underflow, visual corruption, or fallback to lower link rates.
- Run register-dump or debugfs diagnostics before and after modeset/resume to confirm reserved bits are preserved and override-enable bits are not left asserted unexpectedly.
- Monitor kernel logs and display diagnostics for AUX/link-training errors, HPD instability, PHY calibration timeouts, CDR lock failures, signal-detect flapping, and resume-only display failures.

## Cross-Chunk Notes

The previous chunk owns the beginning of RAWLANEAON0 TX fields and the first part of RAWLANEAON0 RX calibration bank 1. Later chunks continue RAWLANEAON2 RX startup/adaptation/calibration definitions and the remaining C20 PHY CR3 RAWLANEAON/X generated field namespace. The final per-file research document should merge those adjacent chunks before making complete claims about every RAWLANEAON lane, every RX startup-control register, or the full `dcn_3_2_0_sh_mask.h` hardware map.
