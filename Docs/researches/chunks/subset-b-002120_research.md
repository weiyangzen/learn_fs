# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_6_0_sh_mask.h lines 4813-7453

## Purpose

This chunk is a generated AMD DCN 3.6.0 register field shift/mask header segment. It does not implement executable logic; it defines `#define` constants used by the AMD display driver register helper layer to pack, unpack, update, and read individual hardware register fields safely. The chunk contributes 2,086 shift/mask macros for 422 register names spanning DMCUB communication tail registers, display writeback (DWB), writeback color processing, display/DC perf monitors, MCIF/MMHUBBUB writeback memory plumbing, HDA/Azalia audio controller registers, and DCHUBBUB arbitration/SDPIF controls.

The naming convention is uniform:

- `<REGISTER>__<FIELD>__SHIFT` gives the bit offset for the field.
- `<REGISTER>__<FIELD>_MASK` gives the field mask in the 32-bit MMIO register.

The generated constants are paired with offset headers and consumed through AMD display macros such as `REG_UPDATE`, `REG_UPDATE_2`, `REG_GET`, `REG_SET`, `REG_READ`, and register list macros that initialize per-IP `shift` and `mask` tables.

## Major Register Groups

### DMCUB tail fields

The first part continues DMCUB definitions from the previous chunk. It includes general-purpose interrupt mailbox registers `DMCUB_GPINT_DATAIN0` through `DMCUB_GPINT_DATAIN6`, `DMCUB_GPINT_DATAOUT`, `DMCUB_UNDEFINED_ADDRESS_FAULT_ADDR`, low-power wake enable, memory power control, timer, processor ID, soft reset, region space selection, and scratch registers `DMCUB_SCRATCH19` through `DMCUB_SCRATCH23`.

These fields are full-width mailbox/scratch values or small control bits. Consumers in `display/dmub/src` read/write `DMCUB_GPINT_*`, scratch, reset, timer, and fault fields when booting DMUB firmware, sending commands, collecting debug state, or handling DMCUB faults.

### DWB top and frame capture

The `dce_dc_wb0_dispdec_dwb_top_dispdec` block defines display writeback enable, clock gating, memory power, frame capture, crop window, CRC, output format/denorm, backpressure, overflow, host-read throttle, and soft reset fields. Important registers include:

- `DWB_ENABLE_CLK_CTRL`: enables DWB, disables selected DWB clock gates, selects test clocks, and controls fine-grain clock-gating replacement.
- `DWB_MEM_PWR_CTRL`: controls output FIFO and OGAM LUT memory power force/disable/state bits.
- `FC_MODE_CTRL`, `FC_FLOW_CTRL`, `FC_WINDOW_START`, `FC_WINDOW_SIZE`, `FC_SOURCE_SIZE`: configure frame capture enable/rate, cropping, stereo eye selection, new-content signaling, first-pixel delay, and source/window dimensions.
- `DWB_UPDATE_CTRL`: supplies update lock and pending state for coherent DWB programming.
- `DWB_CRC_*`: controls DWB CRC collection, masks RGBA channels, and exposes CRC signature values.
- `DWB_OUT_CTRL`: selects output format, denormalization mode, and output min/max pixel values.
- `DWB_OVERFLOW_STATUS` and `DWB_OVERFLOW_COUNTER`: expose overflow flag/status/ack/mask/type and overflow coordinates.

The DWB driver uses these fields in `display/dc/dwb/dcn30/dcn30_dwb.c`. For example, `dwb3_enable()` sets `DWB_ENABLE_CLK_CTRL.DWB_ENABLE`, programs `FC_*`, color-processing, and `DWB_OUT_CTRL`, then enables `FC_MODE_CTRL.FC_FRAME_CAPTURE_EN`. `dwb3_update()` and `dwb3_set_fc_enable()` use `DWB_UPDATE_CTRL.DWB_UPDATE_LOCK` around multi-register updates.

### DWB color processing and OGAM

The `dce_dc_wb0_dispdec_dwbcp_dispdec` block defines writeback color pipeline fields:

- `DWB_HDR_MULT_COEF` for HDR multiplier coefficient programming.
- `DWB_GAMUT_REMAP_MODE`, `DWB_GAMUT_REMAP_COEF_FORMAT`, and A/B remap coefficient registers for 3x4 color matrix programming.
- `DWB_OGAM_CONTROL`, LUT index/data/control fields, and two banks of OGAM PWL region definitions (`RAMA` and `RAMB`).

The OGAM blocks define start/end base and slope values per channel plus 34 exp regions encoded as LUT offsets and segment counts. These constants back the DWB output gamma path; register-list macros in `dcn30_dwb.h` map them into `struct dcn30_dwbc_registers`, `struct dcn30_dwbc_shift`, and `struct dcn30_dwbc_mask`.

### DC perf monitor blocks

The chunk contains three nearly identical perfmon address blocks:

- `DC_PERFMON3_*` for DWB/writeback.
- `DC_PERFMON4_*` for MMHUBBUB.
- `DC_PERFMON5_*` for HDA/Azalia.

Each block defines per-counter selection/control fields, counter state fields, perfmon state/report count/control, interrupt status/ack bits, current value high/low fields, and read selector fields. These are diagnostic/performance collection registers rather than normal display programming flow. Incorrect masks would mainly break telemetry, profiling, or interrupt-based counter collection.

### MCIF_WB and MMHUBBUB writeback memory

The `dce_dc_mmhubbub_mcif_wb0_dispdec` block defines writeback buffer manager and memory-interface fields:

- `MCIF_WB_BUFMGR_SW_CONTROL` and `MCIF_WB_BUFMGR_STATUS`: enable, software interrupt enable/ack/status, overrun interrupt, lock, current/next buffer, buffer tag, line counters, and address-fence enable.
- `MCIF_WB_BUF_1_STATUS` through `MCIF_WB_BUF_4_STATUS` plus `STATUS2`: active, locked, overflow, disable/mode, buffer tag, next buffer, current line, new content, color depth, TMZ, overrun, and stereo eye flag per buffer.
- Buffer base address registers for Y and chroma planes, including high address registers; luma/chroma sizes; per-buffer resolution; pitch; VMID/security; p-state timing; arbitration; and VCE control.

The adjacent `dce_dc_mmhubbub_mmhubbub_dispdec` block adds MMHUBBUB-level watermarks, warmup, clock/power/reset, outstanding counters, DMU error status, WBIF unit ID, and VMID warmup controls. These fields integrate DWB buffer ownership with the MMHUBBUB memory path and SoC/display clock/power management.

### HDA/Azalia audio

The HDA section spans controller, root codec, miscellaneous, stream, endpoint, and input endpoint address blocks:

- Controller fields cover clock gating, DTO phase/module, SOCCLK deep sleep exit, underflow filler sample, data/BDL/CORB/RIRB/DP DMA snoop and isochronous settings, payload capabilities, output arbiter latency hiding, input/output CRC engines, and audio memory power control/status.
- Root codec fields expose vendor/device/revision IDs, channel count, resync FIFO, function group type, supported rates/formats/power states, power state control, reset, subsystem ID response, converter synchronization, DC audio port connectivity, input port connectivity, and GTC group offsets.
- `AZ_CLOCK_CNTL` and `AZ_MEM_GLOBAL_PWR_REQ_CNTL` control Azalia clock selection/gating and global memory power requests.
- `AZF0STREAM0` through `AZF0STREAM15` provide indexed stream register access through `AZALIA_STREAM_REG_INDEX`, `AZALIA_STREAM_REG_WRITE_EN`, and `AZALIA_STREAM_REG_DATA`.
- `AZF0ENDPOINT0` through `AZF0ENDPOINT7` and `AZF0INPUTENDPOINT0` through `AZF0INPUTENDPOINT7` provide indexed codec endpoint data windows.

These masks bridge DC display audio support to the HDA/Azalia MMIO layout. The fields are especially sensitive to indexed access protocols: the index register selects an internal stream/endpoint register and the data register supplies or returns the 32-bit value.

### DCHUBBUB arbitration, timing, and SDPIF

The `dce_dc_dchubbubl_hubbub_dispdec` block defines memory arbitration and timing controls:

- `DCHUBBUB_ARB_DF_REQ_OUTSTAND`, `DCHUBBUB_ARB_SAT_LEVEL`, `DCHUBBUB_ARB_QOS_FORCE`, and `DCHUBBUB_ARB_DRAM_STATE_CNTL` control outstanding request limits, saturation level, forced QoS, self-refresh, p-state allowance, C-state/deep-sleep policy, and hysteresis.
- `DCHUBBUB_ARB_USR_RETRAINING_CNTL` and watermark sets A-D define data urgency, USR retraining, ref cycles per trip to memory, self-refresh enter/exit including Z8, UCLK/FCLK p-state change, and fractional urgent bandwidth.
- `DCHUBBUB_ARB_HOSTVM_CNTL` contains host VM force disable/status/limit fields for PRQ, read FIFO, return FIFO, and stall behavior.
- `DCHUBBUB_ARB_WATERMARK_CHANGE_CNTL` handles watermark-change requests, interrupt disable/enable/status/clear, urgent watermark selection, pending state, and timing status.
- `DCHUBBUB_ARB_MALL_CNTL` tracks MALL use and prefetch completion.
- Timer, surface checker address/in-use registers, VTG controls, soft reset, clock control, DCFCLK gating/delays, latency measurement, vline snapshot, ROB overflow status/clear, timeout detection/interrupts, and `FMON_CTRL` complete the block.

The block ends by entering `dce_dc_dchubbubl_hubbub_sdpif_dispdec` and beginning `DCHUBBUB_SDPIF_CFG0`, with only the first four field definitions present in this chunk: no outstanding request, port status, data response status, and response status. The following chunk continues the remaining SDPIF fields.

HUBBUB code uses these fields for watermark programming, clock and power decisions, timeout/error diagnostics, and SDPIF ownership. For example, `hubbub2_program_watermarks()` writes watermark and outstanding-request registers; `hubbub2_get_dchub_ref_freq()` reads `DCHUBBUB_GLOBAL_TIMER_CNTL`; `hubbub2_read_state()` captures watermark and DRAM-state control; `hubbub32_set_sdp_control()` writes `DCHUBBUB_SDPIF_CFG0.SDPIF_PORT_CONTROL`.

## APIs, Types, and Integration Points

This header provides preprocessor constants rather than C APIs. Its integration contract is with generated and hand-written display register plumbing:

- Offset headers such as `dcn_3_6_0_offset.h` provide register addresses/base indices; this file provides field shifts/masks.
- Register list macros in IP-specific headers, such as `DWBC_COMMON_REG_LIST_DCN30()` and `DWBC_COMMON_MASK_SH_LIST_DCN30()`, bind register names and fields into typed register/shift/mask structs.
- Driver code accesses fields through the register helper macros. The helpers use each field's shift and mask pair to read-modify-write only the intended bits.
- DMUB, DWB, HUBBUB/MMHUBBUB, perfmon, and HDA/Azalia code are the primary consumers for this chunk.

There are no functions, structs, dynamic allocations, reference counts, locks, or direct control-flow branches in this chunk itself. Control flow is external: higher-level DC code decides when to enable DWB, program color, update watermarks, read perf counters, or manipulate audio streams, and this header supplies the bit layout needed for those operations.

## State and Persistence Behavior

The state represented by these macros is persistent hardware MMIO state, not kernel memory state. Writes persist in the display/audio hardware register file until changed by the driver, reset by hardware, or affected by power management. Several groups have explicit state/ack/current conventions:

- DWB update state uses `DWB_UPDATE_LOCK` and `DWB_UPDATE_PENDING` so multiple DWB fields can be staged and applied coherently.
- DWB has current-state fields such as `FC_FRAME_CAPTURE_EN_CURRENT`, `DWB_GAMUT_REMAP_MODE_CURRENT`, and OGAM current selectors.
- Buffer manager and MCIF fields track active buffers, current/next buffer numbers, buffer tags, current line, overrun flags, TMZ state, and software/VCE locks.
- Interrupt/status fields frequently pair status bits with ack/clear bits, such as DWB overflow, MCIF writeback SW interrupt, perfmon interrupts, Azalia CRC completion, DMU error clear, DCHUBBUB timeout clear, and watermark-change interrupt clear.
- Memory/clock power fields expose force, disable, mode select, and state/status bits for DMCUB, DWB, MMHUBBUB/WBIF, and Azalia memories.

Because the file only defines masks, it has no persistence logic itself. Correct persistence behavior depends on consumers respecting hardware sequencing: lock before multi-field DWB updates, acknowledge status bits only when intended, avoid lowering watermarks unless safe, and account for indexed stream/endpoint register windows in Azalia.

## Dependencies

The direct dependency is the generated DCN 3.6.0 register naming scheme. The constants must match the corresponding hardware spec and the matching offset header. At compile time, consumers depend on:

- `reg_helper.h` and display register helper macros.
- IP-specific register structs and mask/shift structs for DWB, HUBBUB, DMUB, and audio blocks.
- Matching generation of register names across resource headers and ASIC-specific initialization tables.

The file is not self-validating. A field name typo, mask width mismatch, or shift/mask mismatch will compile if no consumer references it, but referenced mismatches can silently corrupt adjacent hardware fields.

## Risks and Failure Modes

- Bitfield drift against hardware is the main risk. A wrong shift or mask can write the wrong MMIO bits, causing display capture failure, audio malfunction, power-management instability, memory-request starvation, or interrupts that cannot be cleared.
- Generated header and offset-header mismatch can target the right field layout at the wrong address, or the right address with the wrong field layout.
- Partial chunk boundaries matter for generated documentation: this chunk begins mid-DMCUB block and ends mid-`DCHUBBUB_SDPIF_CFG0`. Final merged research should reconcile those edges with neighboring chunks.
- DWB update locking mistakes in consumers can expose partially programmed capture/color state to hardware.
- Watermark, p-state, C-state, and DCFCLK fields are performance and correctness sensitive; bad programming can cause underflow/overflow, missed self-refresh opportunities, or visible glitches.
- Indexed Azalia stream/endpoint access is protocol-sensitive. Incorrect index/write-enable/data field masks can read or write the wrong internal audio register.
- Status/ack/clear bits are side-effectful. Treating them like ordinary fields can lose diagnostic evidence or clear pending interrupts unexpectedly.

## Test Signals

Useful validation signals for changes touching this header or its consumers include:

- Build coverage for AMDGPU display code with DC enabled, ensuring all generated register/field references resolve.
- DWB enable/update/disable tests or runtime traces showing `DWB_ENABLE`, `FC_FRAME_CAPTURE_EN`, crop/source size, output format, and OGAM programming behave as expected.
- DWB CRC and overflow diagnostics: CRC values should update when enabled, and overflow flags/counters should clear and report consistently.
- Watermark programming traces from HUBBUB paths, including A-D watermark sets, global timer reference divider, `DCHUBBUB_ARB_WATERMARK_CHANGE_CNTL`, and timeout/ROB overflow status.
- Suspend/resume and power-management tests covering DMCUB, DWB, MMHUBBUB/WBIF, DCFCLK, and Azalia memory/clock power fields.
- Audio playback/HDMI/DP audio tests covering Azalia stream indexed registers, payload capabilities, DMA snoop/isochronous controls, and CRC/status fields.
- Perfmon smoke tests confirming counters can be configured, run, read, interrupt/ack, and reset without corrupting unrelated bits.
