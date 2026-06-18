# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_2_0_0_sh_mask.h lines 4769-7154

## Purpose

This chunk is part of AMDGPU's generated DCN 2.0 register field mask header. It contains no executable C logic; it publishes compile-time `REGISTER__FIELD__SHIFT` and `REGISTER__FIELD_MASK` constants for display hardware registers. Driver code combines these field constants with the matching register-address definitions from `dcn_2_0_0_offset.h` and the DC register helper macros.

The assigned range covers three related regions of the DCN 2.0 display register map:

- The tail of display interrupt status and GPU timer-position registers, including `DISP_INTERRUPT_STATUS_CONTINUE22`, timer start positions for vready, flip, no-lock v-update, and flip-away events, plus `DISP_INTERRUPT_STATUS_CONTINUE23` and `DISP_INTERRUPT_STATUS_CONTINUE24`.
- Interrupt destination registers for many display sub-blocks: DCCG, DMU/DMCUB/DMCU, DCPG, MMHUBBUB, WB/WBSCL, DCHUB/HUBP, DPP, MPC, OPP, OPTC/OTG, DIG, I2C/DDC/HPD, DIO, DCIO, HPD, AZ audio, AUX, and DSC.
- The beginning of writeback and memory-hubbub field definitions: WB0 converter, WB scaler, WB perfmon, MCIF writeback instances 0 and 1, WBIF0, VGA split, MMHUBBUB memory power, and the first fields of `MMHUBBUB_CLOCK_CNTL`.

Although this repository path is under a local `ceph-client` source tree, this header chunk is AMD display-driver hardware metadata. It has no Ceph filesystem protocol behavior, distributed filesystem state, or storage persistence.

## Important APIs, Types, And Macros

There are no functions, structs, enums, or variables in this chunk. The macro namespace is the API surface.

Each field appears as a pair:

- `REGISTER__FIELD__SHIFT` gives the low bit position.
- `REGISTER__FIELD_MASK` gives the already-positioned bit mask.

The interrupt status groups expose live/sticky event bits. `DISP_INTERRUPT_STATUS_CONTINUE22` covers DCPG domain 8-15 power up/down events, ABM0 ready/backlight update events, OTG0-OTG5 v-update-no-lock events, and the continuation bit into `DISP_INTERRUPT_STATUS_CONTINUE23`. `DISP_INTERRUPT_STATUS_CONTINUE23` covers DCPG domain 16-21 power events, DSC0-DSC5 input-underflow and core-error events, and continuation into `DISP_INTERRUPT_STATUS_CONTINUE24`. `DISP_INTERRUPT_STATUS_CONTINUE24` covers DSC perfmon counter interrupts and DMCUB timer, inbox, outbox, general-data, and undefined-address-fault events.

The `DC_GPU_TIMER_START_POSITION_*` registers pack per-pipe timer trigger positions. `VREADY` and `V_UPDATE_NO_LOCK` expose D1-D6 fields; `FLIP` and `FLIP_AWAY` expose D1-D8 fields. These fields are small packed selectors used by display interrupt/timer logic around scanout and page-flip timing.

The interrupt destination groups define routing selectors for display interrupt sources. They include:

- `DCCG_INTERRUPT_DEST`, `DMU_INTERRUPT_DEST`, `DCPG_INTERRUPT_DEST`, and `DCPG_INTERRUPT_DEST2` for clock-generator, display microcontroller, and display clock/power-gating interrupts.
- `MMHUBBUB_INTERRUPT_DEST`, `WB_INTERRUPT_DEST`, `DCHUB_INTERRUPT_DEST`, `DCHUB_PERFCOUNTER_INTERRUPT_DEST`, and `DCHUB_INTERRUPT_DEST2` for memory-hubbub, writeback, HUBP vblank/vline/VM-context, perfmon, flip, flip-away, and VM-fault routing.
- `DPP_PERFCOUNTER_INTERRUPT_DEST`, `MPC_INTERRUPT_DEST`, `OPP_INTERRUPT_DEST`, `OPTC_INTERRUPT_DEST`, and `OTG0_INTERRUPT_DEST` through `OTG5_INTERRUPT_DEST` for pixel pipe, composition, output, timing-generator, and underflow/range/vupdate/snapshot events.
- `DIG_INTERRUPT_DEST`, `I2C_DDC_HPD_INTERRUPT_DEST`, `DIO_INTERRUPT_DEST`, `DCIO_INTERRUPT_DEST`, `HPD_INTERRUPT_DEST`, `AZ_INTERRUPT_DEST`, `AUX_INTERRUPT_DEST`, and `DSC_INTERRUPT_DEST` for display I/O, hotplug, AUX, audio, and DSC interrupt routing.

The WB0 converter block under `dce_dc_wb0_dispdec_cnv_dispdec` includes `WB_ENABLE`, `WB_EC_CONFIG`, `CNV_MODE`, source/window size and start registers, update control, test CRC registers, debug controls, soft reset, and warm-up controls. These fields describe writeback capture enablement, format/conversion setup, source and output geometry, update latching, diagnostics, and reset behavior.

The WBSCL block under `dce_dc_wb0_dispdec_wbscl_dispdec` includes coefficient RAM select/data, scaler mode, tap control, destination size, horizontal and vertical filter scale ratios and initial phases, round offsets, overflow/conflict status, test CRCs, backpressure counters, clamp ranges, outside-pixel strategy, and debug access. These constants support the writeback scaler pipeline.

The WB perfmon block `DC_PERFMON3_*` exposes counter control, counter state, perfmon control, and current/high/low counter values for writeback performance monitoring.

The MCIF writeback blocks `MCIF_WB0_*` and `MCIF_WB1_*` expose memory-interface writeback control. Important families include software buffer-manager control and status, current line, pitch, four luma/chroma buffer status and address registers, address offsets, high address bits, resolution fields, VCE buffer-manager lock/interrupt/slice controls, SCLK/NB-pstate watermark controls, client watermark, clock gating override, warm-up pitch, self-refresh behavior, multi-level QoS, luma/chroma sizes, and test-debug access. `MCIF_WB0_MCIF_WB_SECURITY_LEVEL` is present for instance 0 in this range.

The final MMHUBBUB block begins with `WBIF0_MISC_CTRL`, `WBIF0_SMU_WM_CONTROL`, `WBIF0_PHASE0_OUTSTANDING_COUNTER`, `WBIF0_PHASE1_OUTSTANDING_COUNTER`, `VGA_SRC_SPLIT_CNTL`, `MMHUBBUB_MEM_PWR_STATUS`, `MMHUBBUB_MEM_PWR_CNTL`, and the first `MMHUBBUB_CLOCK_CNTL` shift fields through `DISPCLK_G_WBIF0_GATE_DIS`. These fields cover writeback interface timeout/deep-sleep controls, SMU watermark-change handshaking, outstanding request counters, legacy VGA split selection, memory power status/control for VGA and MCIF DWB0 memories, and MMHUBBUB/VGA/WBIF clock-gate controls.

## Control Flow

This header range has no runtime control flow. It is preprocessor data consumed by DCN 2.0 display code.

A typical consumer flow is:

1. Include `dcn_2_0_0_offset.h` for register addresses and `dcn_2_0_0_sh_mask.h` for field layouts.
2. Bind fields into a block-specific register descriptor with macros such as `SF(reg, field, mask_sh)` or `FD(reg__field)`.
3. Use display register helpers such as `REG_SET`, `REG_UPDATE`, `REG_GET`, or SOC15-specific wrappers to read, modify, and write packed fields.
4. Let hardware interpret the programmed value as interrupt routing, interrupt status, writeback/scaler configuration, memory-interface buffer state, power-management policy, or debug/perfmon setup.

The control-sensitive behaviors represented here include interrupt routing to the correct interrupt handler, acknowledging or inspecting display status events, selecting GPU timer positions for scanout events, enabling/disabling writeback, latching writeback converter/scaler updates, programming buffer addresses and sizes, responding to writeback backpressure or overrun, coordinating p-state and self-refresh watermarks, and disabling/enabling MMHUBBUB/VGA/WBIF clock gates.

## State And Persistence Behavior

The file stores no software state and has no persistence mechanism. It describes state held in DCN 2.0 display hardware registers.

The represented hardware state includes:

- Interrupt state: live or sticky status bits for DCPG, DSC, DMCUB, ABM, OTG, HUBP, WBSCL, WB, AUX, HPD, DIG, AZ, and other display sub-block events.
- Interrupt routing state: destination bits that determine which interrupt path receives events from each display block.
- Timer-position state: compact per-pipe trigger positions for vready, flip, v-update-no-lock, and flip-away handling.
- Writeback pipeline state: enable, conversion mode, input/output geometry, update latches, scaler coefficients, scaling ratios, clamp ranges, CRC/debug controls, soft reset, and warm-up setup.
- MCIF writeback state: buffer-manager enable/locks/interrupts, buffer pitch/address/offset/high bits, four-buffer status, resolution, QoS/watermarks, p-state handling, self-refresh behavior, security level, and memory client clock gating.
- MMHUBBUB state: writeback interface handshake/status, VGA split, memory power status/control, and clock-gate control.

Persistence is hardware-defined. Some fields are programmed configuration that remains until reset or reprogramming; some are status/readback fields; some are interrupt status bits that may be sticky or write-one-to-clear; and some are handshake or acknowledge bits that can be self-clearing. Values can be changed by the display driver, DMCUB/firmware, BIOS initialization, hotplug/modeset paths, power-gating, suspend/resume, or ASIC reset. This generated header does not encode access type, reset value, volatile behavior, or sequencing constraints.

## Dependencies And Integration Points

This chunk depends on the generated DCN 2.0 register header set. The companion address definitions live in `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_2_0_0_offset.h`; this file supplies only the field layout inside those addresses.

Direct include points for `dcn_2_0_0_sh_mask.h` found in this tree include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn20.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn20/irq_service_dcn20.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gmc_v10_0.c`

The writeback and MMHUBBUB fields are integrated through DCN 2.0 display-resource descriptors. For example, `display/dc/mmhubbub/dcn20/dcn20_mmhubbub.h` maps `MCIF_WB0_MCIF_WB_BUFMGR_SW_CONTROL` fields such as `MCIF_WB_BUFMGR_ENABLE`, software interrupt enable/ack bits, lock bits, VMID, and address-fence enable into the `dcn20_mmhubbub` register/mask structures. Older or shared writeback declarations such as `display/dc/dcn10/dcn10_dwb.h` use the same MCIF WB field names where the hardware layout is compatible.

The interrupt fields integrate with `display/dc/irq/dcn20/irq_service_dcn20.c`, which builds IRQ source tables for DCN 2.0 display events. The destination/status masks in this chunk are part of the low-level contract that lets IRQ service code route, enable, clear, or inspect display interrupt sources.

The DMCUB-related interrupt fields integrate with DMUB firmware communication in `display/dmub/src/dmub_dcn20.c`. The `DISP_INTERRUPT_STATUS_CONTINUE24` and `DMU_INTERRUPT_DEST` fields describe the hardware event surface for DMCUB timers, inbox/outbox readiness/completion, general data, and undefined-address faults.

## Risks And Edge Cases

The main risk is silent hardware misprogramming. A wrong shift or mask can compile successfully while changing the wrong bit, failing to update the intended field, corrupting an adjacent field during read-modify-write, or routing an interrupt to the wrong destination.

Interrupt fields are sensitive because routing/status mistakes can cause missed vblank, vline, HPD, AUX, underflow, DSC, DMCUB mailbox, VM-fault, or writeback events. Symptoms can include lost hotplug notifications, stuck DMUB communication, unacknowledged interrupts, interrupt storms, missed page-flip completion, incorrect underflow reporting, or broken display diagnostics.

Writeback and scaler fields are sensitive to geometry and buffer programming. Incorrect masks for `CNV_WINDOW_*`, `CNV_SOURCE_SIZE`, WBSCL scale ratios/phases, clamp/outside-pixel strategy, MCIF buffer addresses, pitch, offsets, high address bits, luma/chroma sizes, or resolution fields can produce corrupt captures, out-of-bounds memory writes, wrong color/chroma layout, bad CRC diagnostics, or hangs in the writeback path.

MCIF and MMHUBBUB power/performance fields affect memory traffic and display power management. Bad watermarks, p-state controls, self-refresh bits, QoS settings, clock-gate overrides, memory power controls, or SMU watermark handshakes can lead to writeback underrun/overrun, backpressure, missed watermark updates, higher power use, or display instability around suspend/resume and clock changes.

The repeated instance layout is a maintenance risk. `MCIF_WB0_*` and `MCIF_WB1_*` are nearly mirrored, but not identical in this range because `MCIF_WB0_MCIF_WB_SECURITY_LEVEL` appears while the analogous WB1 security-level register is not present before the next instance's luma/chroma size fields. Copying constants across instances without checking the generated source can introduce subtle instance-specific bugs.

The chunk boundaries are artificial. It starts inside the `DISP_INTERRUPT_STATUS_CONTINUE22` macro group, after earlier shift fields for that register, and ends before the remaining `MMHUBBUB_CLOCK_CNTL` shift and mask fields. The final per-file merge should treat these as chunk boundaries, not as source omissions.

## Test Signals

Useful validation is mostly compile-time plus display hardware behavior:

- AMDGPU builds for DCN 2.0 paths should compile all generated field names referenced by IRQ, DMUB, MMHUBBUB, writeback, and GMC/DC integration code.
- Generated-register validation should compare every `*_MASK` and `*__SHIFT` pair in this range against AMD's DCN 2.0 register database and the matching addresses in `dcn_2_0_0_offset.h`.
- IRQ tests should exercise vblank/vline, page-flip, flip-away, HPD, AUX, DMCUB inbox/outbox, DSC, underflow, writeback, and VM-fault events and verify that status bits, destination routing, and clear/ack behavior match expectations.
- DMUB mailbox tests should confirm timer and inbox/outbox ready/done interrupts are delivered and cleared correctly.
- Writeback tests should enable WB0 capture across representative pixel formats, source/window sizes, scaling ratios, luma/chroma layouts, and four-buffer rotations, then compare captured frames or CRCs.
- Stress tests should combine writeback with modesets, page flips, hotplug, MST, suspend/resume, runtime power management, and clock/p-state changes to expose bad MCIF watermarks, self-refresh controls, or MMHUBBUB clock/memory power fields.
- Perfmon and debug tests should verify WB/DC perfmon counters, scaler conflict/overflow status, test CRC registers, and MCIF debug-index/data access.

Regression symptoms from bad constants include blank or flickering display, missed page-flip completion, interrupt storms, stuck DMUB mailbox traffic, lost HPD/AUX notifications, false underflow or DSC errors, corrupt writeback frames, GPU memory faults from bad capture addresses, writeback hangs, failed suspend/resume, and unexpected clock or power-management behavior.

## Cross-Chunk Notes

Earlier chunks of `dcn_2_0_0_sh_mask.h` define the start of `DISP_INTERRUPT_STATUS_CONTINUE22` and the earlier DCN 2.0 display register field families. Later chunks complete `MMHUBBUB_CLOCK_CNTL` and continue through the remaining DCN 2.0 generated register mask definitions. The final per-file report should describe the whole header as a generated hardware layout contract rather than as algorithmic driver code.
