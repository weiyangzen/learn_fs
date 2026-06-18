# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gmc/gmc_8_1_sh_mask.h lines 14960-15682

## Scope And Purpose

This chunk is the final portion of the `gmc_8_1_sh_mask.h` generated-style ASIC register mask header. It contains preprocessor constants only: each hardware register field is exposed as a `<REGISTER>__<FIELD>_MASK` and matching `<REGISTER>__<FIELD>__SHIFT` definition. There are no functions, structs, enums, storage objects, or executable branches in this line range.

The span covers three related register-contract areas for GMC 8.1-era AMD GPUs:

- Memory-controller sequencer and data-loopback controls: `MC_SEQ_DLL_STBY`, `MC_SEQ_DLL_STBY_LP`, and the `MC_DLB_*` register family.
- Memory-controller arbitration policy fields: `MC_ARB_HARSH_*` and `MC_ARB_GRUB_PRIORITY*` read/write priority registers.
- MCIF writeback buffer-manager fields: `MCIF_WB_BUFMGR_*`, `MCIF_WB_BUF_*`, `MCIF_WB_ARBITRATION_CONTROL`, `MCIF_WB_URGENCY_WATERMARK`, test/debug, VCE control, and VMID control registers.

The purpose is to give AMDGPU and display/power-management code symbolic bit layouts for register programming. The companion address header, `gmc_8_1_d.h`, defines the `mm*` register offsets; this mask header defines how to pack or decode values at those offsets.

## Important APIs, Types, And Constants

There are no callable APIs or C types in this chunk. The public interface is the macro namespace.

`MC_SEQ_DLL_STBY` and `MC_SEQ_DLL_STBY_LP` define bitfields for DLL standby behavior. The normal and low-power variants share fields for enable, forced/explicit VCTRL ADC and master-standby values, entry/standby delays, CKE pulse/extension timing, and exit delay. Power-management code maps `mmMC_SEQ_DLL_STBY` to `mmMC_SEQ_DLL_STBY_LP` and copies normal register values into the LP register when building memory-clock tables.

`MC_DLB_*` defines the data-loopback/test block:

- `MC_DLB_MISCCTRL0`, `MISCCTRL1`, and `MISCCTRL2` select user-defined data, PRBS run length, PRBS error limits, PRBS modes, stop behavior, clock stop, sweep delay, gray-code mode, PHY/AC checker selection, and status selection.
- `MC_DLB_CONFIG0` and `CONFIG1` hold per-channel configuration enable bits, auto enable, mask/pointer selection, and full-width configuration data.
- `MC_DLB_SETUP`, `SETUPSWEEP`, `SETUPFIFO`, and `WRITE_MASK` control DLB enablement, FIFO/status/config/PRBS enablement, PRBS resets, QDR mode, checked data-bit selection, memory-bit selection, RX/TX low-power enablement, DLL sweep setup, FIFO reset/sync/strobe settings, and bit/channel write masks.
- `MC_DLB_STATUS` and `MC_DLB_STATUS_MISC0` through `MISC7` expose sticky errors, lock state, sweep completion, and full-width status data words.

`MC_ARB_HARSH_*` defines memory-arbiter "harsh" policy fields for read and write traffic. The register families are structured in parallel for RD and WR:

- `MC_ARB_HARSH_EN_{RD,WR}` has 8-bit enable groups for transaction-priority, bandwidth-priority, fixed-priority, and stall-priority handling.
- `MC_ARB_HARSH_TX_HI*` and `TX_LO*` define high and low transaction thresholds for groups 0-7.
- `MC_ARB_HARSH_BWPERIOD*`, `BWCNT*`, and `SAT*` define packed 8-bit group values for bandwidth accounting periods, bandwidth counters, and saturation thresholds.
- `MC_ARB_HARSH_CTL_{RD,WR}` provides global policy controls: `FORCE_HIGHEST`, round-robin harsh mode, bank-age-only mode, legacy harsh mode, bandwidth-counter catch-up, stall mode, force-stall bitfield, and performance-monitor selection.

`MC_ARB_GRUB_PRIORITY1_*` and `MC_ARB_GRUB_PRIORITY2_*` define packed 2-bit client priority fields for read and write arbitration. The read registers cover clients such as `CB0`, `CBCMASK0`, `CBFMASK0`, `DB0`, `DBHTILE0`, `DBSTEN0`, `TC0`, `ACPG`, `ACPO`, `DMIF`, `MCIF`, `RLC`, `SDMA1`, `SMU`, `VCE0`, `VCE1`, `XDMAM`, `SDMA0`, `HDP`, `UMC`, `UVD`, `SEM`, `SAMMSP`, `VP8`, `ISP`, and reserved slots. The write-side registers are similar but include write-specific clients and ordering such as `CBIMMED0`, `SH`, `XDMA`, `XDP`, `IH`, and `VIN0`.

`MCIF_WB_*` defines the writeback path into memory:

- `MCIF_WB_BUFMGR_SW_CONTROL` controls buffer-manager enablement, dual-size requests, software interrupt enable/ack/slice interrupt enable, software lock bits, and producer VMID.
- `MCIF_WB_BUFMGR_STATUS` reports VCE/software interrupt status, current/next buffer, dual-size status, buffer tag, and current left-line position. `MCIF_WB_BUFMGR_CUR_LINE_R` reports the right-line position.
- `MCIF_WB_BUF_PITCH` packs luma and chroma pitches.
- `MCIF_WB_BUF_[1-4]_STATUS` and `STATUS2` repeat the same field layout for four buffers: active, software-locked, VCE-locked, overflow, disable, mode, buffer tag, next buffer, field, current line left/right, long-line error, short-line error, frame-length error, new-content flag, and color-depth flag.
- `MCIF_WB_ARBITRATION_CONTROL` selects client arbitration slice and time-per-pixel scheduling.
- `MCIF_WB_URGENCY_WATERMARK` packs two client urgency watermarks.
- `MCIF_WB_TEST_DEBUG_INDEX` and `MCIF_WB_TEST_DEBUG_DATA` expose an indexed test/debug path with write enable and full-width debug data.
- `MCIF_WB_BUF_[1-4]_ADDR_{Y,C}` and matching `_OFFSET` registers define luma/chroma base addresses and 18-bit offsets for the four writeback buffers.
- `MCIF_WB_BUFMGR_VCE_CONTROL` controls VCE lock-ignore, VCE interrupts/acks/slice interrupts, VCE lock bits, and slice size.
- `MCIF_WB_HVVMID_CONTROL` defines default VMID and allowed-VMID mask fields. The macro name `MCIF_WB_HVVMID_CONTROL__MCIF_WB_ALLOWED_VMID_MASK_MASK` is mechanically generated and includes the duplicated `MASK` token in the field name; consumers must use the exact generated spelling.

## Control Flow And State Behavior

This header chunk has no local runtime control flow. Its effects are compile-time substitution of constants into consumers that read, modify, or write MMIO registers.

Runtime state lives in GPU hardware registers:

- The DLL standby fields configure memory sequencer timing and low-power behavior. Power-management code for Island/Tonga/CI-era paths uses the address pair `mmMC_SEQ_DLL_STBY` and `mmMC_SEQ_DLL_STBY_LP` when constructing low-power memory register tables, so values can be mirrored from normal to low-power register banks.
- The `MC_DLB_*` registers configure and observe memory data-loopback or PRBS diagnostics. Enable, reset, checker selection, run length, and stop-on-error fields drive hardware test state; status and misc status fields expose sticky errors, lock status, sweep completion, and diagnostic data.
- The arbiter registers configure memory-controller scheduling policy. The "harsh" fields set group thresholds and enable different priority algorithms; the GRUB priority fields assign packed client priorities for read and write traffic. These values affect arbitration behavior inside hardware rather than storing software-owned state.
- The MCIF writeback registers describe buffer manager configuration and observable buffer state. Active/locked/error/new-content bits are hardware status signals; address, offset, pitch, urgency, arbitration, interrupt, lock, and VMID fields are programmed configuration state.

Persistence is therefore hardware-dependent. Values survive until reset, power-gating, mode changes, firmware/driver reinitialization, or explicit register writes. The header does not cache values, serialize access, restore state, or enforce read-modify-write discipline.

## Dependencies And Integration Points

This file is part of the AMDGPU ASIC register vocabulary under `drivers/gpu/drm/amd/include/asic_reg/gmc/`. It depends on conventional inclusion by driver code that also includes register-address headers:

- `gmc_8_1_d.h` defines the matching offsets: `mmMC_SEQ_DLL_STBY` at `0xd8e`, `mmMC_SEQ_DLL_STBY_LP` at `0xd8f`, `mmMC_DLB_*` at `0xd90` through `0xda1`, `mmMC_ARB_HARSH_*` at `0xdc0` through `0xdd7`, `mmMC_ARB_GRUB_PRIORITY*` at `0xdd8` through `0xddb`, and `mmMCIF_WB_*` starting at `0x5e78`.
- `gmc_8_1_d.h` also defines instance-specific aliases for MCIF writeback, such as `mmMCIF_WB0_*`, `mmMCIF_WB1_*`, and `mmMCIF_WB2_*`, with the same field layout described by this mask chunk.
- Power-management SMU manager code for related GCN 1.2 ASICs maps `mmMC_SEQ_DLL_STBY` to `mmMC_SEQ_DLL_STBY_LP` and writes the LP register from the normal register value when preparing memory tables.
- Display writeback code in newer DC/DCN paths uses analogous `MCIF_WB_*` register lists and masks for MCIF writeback programming. This GMC 8.1 chunk supplies the pre-DCN/GCN-era field layout for the same conceptual block.
- The mask names are intended to be used with AMDGPU register helpers such as raw MMIO reads/writes or table-driven register programming, usually in the form `(value << FIELD__SHIFT) & FIELD_MASK` or `(reg & FIELD_MASK) >> FIELD__SHIFT`.

The header is not useful by itself: every meaningful use needs a register address, an MMIO accessor, and an ASIC path that actually exposes the corresponding register block.

## Risks And Edge Cases

- The constants are a hardware ABI. A wrong mask or shift can write reserved bits, leave a target field unchanged, select an unintended arbiter policy, corrupt writeback buffer addressing, or misdecode status/errors.
- Many fields are packed 8-bit or 2-bit repeated groups. Off-by-one shifts in group registers are especially risky because they silently configure the wrong client/group while preserving a plausible-looking value.
- Several fields use full-width `0xffffffff` masks. Call sites should keep values in unsigned 32-bit types and avoid signed promotion surprises when composing or printing register values.
- MCIF writeback address fields are full 32-bit lows plus 18-bit offsets in this chunk. Consumers must combine these with the correct address granularity and any high-address registers supplied elsewhere for the target ASIC; using the wrong generation's layout can point writeback at the wrong memory.
- Buffer-manager lock and interrupt-ack fields are stateful hardware controls. Read-modify-write operations must preserve unrelated bits, and interrupt ack fields should be written according to the hardware's write-one/write-zero semantics rather than treated as ordinary sticky software state.
- `MC_DLB_*` PRBS, FIFO reset, DLL sweep, and stop-clock fields are diagnostic/control-path registers. Accidentally touching them during normal memory operation could disrupt memory-controller behavior or hide memory-training failures.
- Arbiter policy registers can affect display, DMA, video, shader, and host clients at once. A regression may appear as performance jitter, underruns, GPU hangs, or starvation rather than an immediate register-access failure.
- The generated name `MCIF_WB_HVVMID_CONTROL__MCIF_WB_ALLOWED_VMID_MASK_MASK` looks like a typo but is the macro exported by this header. Renaming it for style would break consumers that expect the generated symbol.
- This chunk ends with `#endif /* GMC_8_1_SH_MASK_H */`. Any regeneration or merge must preserve the guard close or every includer of the header will fail to compile.

## Test And Validation Signals

There are no direct unit tests for this macro-only chunk. Useful validation is mostly compile-time and hardware/integration-oriented:

- Build coverage for AMDGPU configurations that include `gmc_8_1_sh_mask.h`, especially power-management paths that reference `MC_SEQ_DLL_STBY`/`MC_SEQ_DLL_STBY_LP` and display or writeback paths that reference `MCIF_WB_*`.
- Static mask/shift consistency checks: single-bit masks should match their shift, contiguous multi-bit masks should shift down to dense fields, full-width fields should have shift zero, and repeated groups should occupy non-overlapping ranges.
- Register-table smoke tests on supported GMC 8.1 hardware: low-power memory table construction should mirror `MC_SEQ_DLL_STBY` into `MC_SEQ_DLL_STBY_LP` without clobbering adjacent LP registers.
- MCIF writeback validation: enable writeback, program buffer addresses/pitches/VMID/watermarks, then check buffer status, new-content, current-line, overflow, long-line, short-line, and frame-length status fields during capture.
- Arbitration validation: compare register dumps before and after any performance or QoS tuning path and confirm only intended `MC_ARB_HARSH_*` and `MC_ARB_GRUB_PRIORITY*` fields changed.
- Diagnostic-only validation for DLB fields: PRBS loopback/sweep tests should report lock and sweep-done status, preserve status-misc readability, and respect stop-on-error/error-limit controls.
- Cross-generation diffing against adjacent `gmc_8_2_sh_mask.h` can catch accidental edits in shared MCIF writeback layouts while still allowing real ASIC-generation differences.

## Chunk Notes For Merge Lane

This is a terminal chunk of a larger generated GMC 8.1 register mask header. Whole-file research should treat it as the mask/shift definition section for memory-controller standby/test/arbitration and MCIF writeback buffer-manager registers, not as standalone logic. The paired address definitions in `gmc_8_1_d.h` and the AMDGPU MMIO helpers are required to explain runtime behavior.
