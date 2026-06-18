# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_2_0_sh_mask.h lines 2374-4913

## Scope

This chunk is a generated AMD DCN 3.2.0 register-field shift/mask header slice. It contains C preprocessor constants only: `_SHIFT` macros for hardware bit positions, `_MASK` macros for raw register masks, register grouping comments, and address-block comments. There are no C functions, structs, enums, local variables, branches, loops, allocations, locks, or file-backed persistence in this range.

The requested range covers 2,540 source lines and 2,142 `#define` lines. It begins in the middle of `OTG2_INTERRUPT_DEST`, where only the tail mask definitions are visible, then covers complete interrupt destination families for `OTG3`, `OTG4`, `OTG5`, DIG/DIO/DCIO/HPD/audio/AUX/DSC/HPO interrupt routing, DMU and display power-gating controls, a large DMCUB MMIO/control region, Display Writeback top and color-processing fields, legacy VGA register-field definitions, MMHUBBUB VGA interface fields, MCIF writeback buffer-management fields, and the start of MMHUBBUB warmup control. It ends inside `MMHUBBUB_WARMUP_CONTROL_STATUS`, after its shift definitions and before its mask definitions, so neighboring chunks are required for complete file-level coverage.

Although the repository path is under a `ceph-client` source mirror, this file is AMDGPU display-controller hardware metadata, not Ceph filesystem code.

## Purpose

The purpose of this header range is to provide the DCN 3.2.0 bit-layout ABI used by AMDGPU Display Core, DCN hardware sequencing, IRQ service code, DMUB/DMCUB access paths, display writeback code, legacy VGA paths, and MMHUBBUB/MCIF programming. Matching offset headers supply register addresses; this file supplies the field positions and masks that generated register tables and register-helper macros use to pack MMIO writes, perform read/modify/write updates, decode status reads, and acknowledge hardware events.

The major hardware surfaces represented here are:

- Interrupt destination selection for OTG timing generators, digital outputs, I2C/DDC/HPD, DIO/DCIO, audio, AUX, DSC, and HPO events.
- DMU clock control, SMU/DMCUB interrupt routing, display power-gating domain configuration/status, and DCPG interrupt status/control.
- DMCUB memory-region windows, code-window mappings, interrupts, external interrupt metadata, fault reporting, security/memory controls, inbox/outbox rings, timers, scratch registers, general-purpose interrupt data, low-sleep wake control, memory power control, and processor/control status.
- Display Writeback (`DWB`) top-level clock, memory power, frame capture flow control, CRC, output control, overflow tracking, host-read control, soft reset, color remap, output gamma LUT control, and output gamma RAM A/B region parameters.
- Legacy VGA registers for page addressing, rendering, sequencer reset, mode/surface memory controls, per-pipe VGA enables, status/interrupt fields, indexed CRTC/SEQ/GRPH/ATTR/DAC legacy access, and source selection.
- MMHUBBUB VGA interface control and outstanding counters.
- MCIF writeback buffer manager controls/status, buffer pitch/address/resolution/security/VMID/QOS/watermark/pstate fields, VCE lock/interrupt controls, and per-buffer status/overrun/TMZ/new-content metadata.
- MMHUBBUB warmup QOS/AWID fields and the beginning of warmup enable/status/ack controls.

This is generated data rather than executable logic, but it is not low-risk data. A single incorrect shift or mask can compile successfully while causing runtime MMIO writes to touch the wrong field, corrupting display interrupt routing, firmware communication, writeback capture, VGA fallback behavior, memory-interface arbitration, security/VMID selection, or power-management state.

## Important APIs, Types, And Macros

This range exports the standard generated AMD register-field naming convention:

- `<REGISTER>__<FIELD>__SHIFT` gives the field's least-significant bit index.
- `<REGISTER>__<FIELD>_MASK` gives the field mask in register-positioned form.
- `//<REGISTER>` comments group the following definitions by register.
- `// addressBlock: ...` comments mark hardware address blocks that the generated offset header mirrors.

There are no callable APIs or C types in this chunk. The important definition families are the register namespaces below.

## Interrupt Destination And Display Power Control

The chunk starts at the end of `OTG2_INTERRUPT_DEST` mask definitions, then defines equivalent complete destination layouts for `OTG3_INTERRUPT_DEST`, `OTG4_INTERRUPT_DEST`, and `OTG5_INTERRUPT_DEST`. These fields route events such as CPU shadow-surface, DRR timing, vupdate, snapshot, force-count-now, force-vsync-next-line, OTG trigger A/B, GSL-vsync-gap, vertical interrupt 0/1/2, set-vtotal-min occurrence, vstartup, vready, nominal-vsync, vupdate-no-lock, and DRR-vtotal-reach interrupt destinations.

Other interrupt destination families include:

- `DIG_INTERRUPT_DEST` for DIGA-DIGH stream-disable and fast-training-complete events.
- `I2C_DDC_HPD_INTERRUPT_DEST` for software I2C done, DDC1-DDC6/DDCVGA hardware done, DDC read-request events, and HPD1-HPD6/high/low/rx events.
- `DIO_INTERRUPT_DEST` and `DCIO_INTERRUPT_DEST` for GPIO pad, genmux, DDC, AUX, DP stream, DP link training, and USB4 DPIA events.
- `HPD_INTERRUPT_DEST` for high/low/rx events across HPD1-HPD6.
- `AZ_INTERRUPT_DEST` for audio endpoint response, dummy, stream 0-7, and codec events.
- `AUX_INTERRUPT_DEST` for AUX SW/HW done and AUX timeout events across AUX1-AUX6 plus DDCVGA.
- `DSC_INTERRUPT_DEST` for DSC0-DSC3 rate-buffer and rate-control-buffer overflow/underflow events.
- `HPO_INTERRUPT_DEST` currently exposing the HPO-to-LT interrupt destination bit.

The DMU and display power-gating area then defines:

- `CC_DC_PIPE_DIS` for pipe disable bitfields.
- `DMU_CLK_CNTL` for DMU clock enable, clock-on, clock-gate-disable, and soft reset.
- `DMCUB_SMU_INTERRUPT_CNTL` and `SMU_INTERRUPT_CONTROL` for DMCUB-to-SMU and SMU-to-DMU interrupt selection/acknowledge.
- `DMU_MISC_ALLOW_DS_FORCE` for forcing deep-sleep allowance.
- `DOMAIN0`, `DOMAIN1`, `DOMAIN2`, `DOMAIN3`, `DOMAIN16`, `DOMAIN17`, `DOMAIN18`, and `DOMAIN19` power-gating config/status registers with domain power force, power-gate-enable, and power status fields.
- `DCPG_INTERRUPT_STATUS`, `DCPG_INTERRUPT_STATUS_2`, `DCPG_INTERRUPT_CONTROL_1`, and `DCPG_INTERRUPT_CONTROL_3` for domain power-up/power-down interrupt status, type, enable, and ack fields.
- `DC_IP_REQUEST_CNTL` for IP request clear behavior.

These fields are used by interrupt service and power-management code, not by normal arithmetic in this header. Correctness depends on preserving event routing, enable/status/ack separation, and instance-to-domain naming.

## DMCUB Register Fields

The `dcn_dc_dmu_dmcub_dispdec` address block is the largest coherent region in this chunk. It defines the register fields that software uses to configure and communicate with the Display Microcontroller Unit block:

- `DMCUB_REGION{0,1,2,4,5,6,7}_OFFSET`, `_OFFSET_HIGH`, and `_TOP_ADDRESS` define base offsets, high offsets, top addresses, and enable bits for DMCUB memory regions. Region 3 is represented separately as code-window subregions.
- `DMCUB_REGION3_CW{0..7}_BASE_ADDRESS`, `_TOP_ADDRESS`, `_OFFSET`, and `_OFFSET_HIGH` define eight region-3 code-window mappings, including per-window enable bits.
- `DMCUB_INTERRUPT_ENABLE`, `DMCUB_INTERRUPT_ACK`, `DMCUB_INTERRUPT_STATUS`, and `DMCUB_INTERRUPT_TYPE` define timer, inbox/outbox ready/done, GPINT0-6, GPINT_IH, undefined-address fault, instruction-fetch fault, and data-write fault fields.
- `DMCUB_EXT_INTERRUPT_STATUS`, `DMCUB_EXT_INTERRUPT_CTXID`, and `DMCUB_EXT_INTERRUPT_ACK` expose external interrupt count, ID, context ID, and acknowledge bits.
- `DMCUB_INST_FETCH_FAULT_ADDR`, `DMCUB_DATA_WRITE_FAULT_ADDR`, and `DMCUB_UNDEFINED_ADDRESS_FAULT_ADDR` expose faulting addresses.
- `DMCUB_SEC_CNTL` controls memory security level, memory unit ID, secure reset, data-fault interrupt disable, auto/security reset status, and fault-clear bits.
- `DMCUB_MEM_CNTL` defines memory read/write QOS fields.
- `DMCUB_INBOX0/1_*` and `DMCUB_OUTBOX0/1_*` define base address, size, write pointer, and read pointer fields for firmware communication rings.
- `DMCUB_TIMER_TRIGGER0`, `DMCUB_TIMER_TRIGGER1`, `DMCUB_TIMER_WINDOW`, and `DMCUB_TIMER_CURRENT` define timer trigger/window/current fields.
- `DMCUB_SCRATCH0` through `DMCUB_SCRATCH23` expose firmware/software scratch registers.
- `DMCUB_CNTL` and `DMCUB_CNTL2` define enable, traceport enable, soft reset, reset status, CWB path selection, traceport reservation, stall detection, and soft-reset interrupt disable fields.
- `DMCUB_GPINT_DATAIN0` through `DMCUB_GPINT_DATAIN6` and `DMCUB_GPINT_DATAOUT` carry general-purpose interrupt payloads.
- `DMCUB_LS_WAKE_INT_ENABLE`, `DMCUB_MEM_PWR_CNTL`, `DMCUB_PROC_ID`, and `DMCUB_REGION3_TMR_AXI_SPACE` define low-sleep wake interrupt enable, memory power/force/status fields, processor ID, and AXI space selection.

These definitions are a hardware/firmware contract. The runtime code must know which fields are configuration, volatile readback, write-one-to-clear acknowledgements, or reset triggers; this generated header only supplies bit positions and masks.

## Display Writeback And Color Processing

The `dcn_dc_wb0_dispdec_dwb_top_dispdec` block defines top-level display writeback controls:

- `DWB_ENABLE_CLK_CTRL` and `DWB_MEM_PWR_CTRL` cover clocks, clock gating, clock-on readback, memory power force/disable/state, and default low-power state.
- `FC_MODE_CTRL`, `FC_FLOW_CTRL`, `FC_WINDOW_START`, `FC_WINDOW_SIZE`, and `FC_SOURCE_SIZE` define frame-capture mode, source select, input/output format, alpha insertion, gamut remap enable, keyer enable, CSC selection, flow control, capture window, and source dimensions.
- `DWB_UPDATE_CTRL` controls update timing and update-pending status.
- `DWB_CRC_CTRL`, `DWB_CRC_MASK_R_G`, `DWB_CRC_MASK_B_A`, `DWB_CRC_VAL_R_G`, and `DWB_CRC_VAL_B_A` define writeback CRC selection, continuous/enable behavior, masks, and readback values.
- `DWB_OUT_CTRL` controls output depth, output format, compression, clamping, and allocation.
- `DWB_MMHUBBUB_BACKPRESSURE_CNT_EN`, `DWB_MMHUBBUB_BACKPRESSURE_CNT`, `DWB_HOST_READ_CONTROL`, `DWB_OVERFLOW_STATUS`, `DWB_OVERFLOW_COUNTER`, and `DWB_SOFT_RESET` define backpressure counting, host-read disable, overflow status/ack/clear, overflow counter, and soft reset fields.

The `dcn_dc_wb0_dispdec_dwbcp_dispdec` block then defines DWB color-processing fields:

- `DWB_HDR_MULT_COEF` defines the HDR multiplier coefficient.
- `DWB_GAMUT_REMAP_MODE`, `DWB_GAMUT_REMAP_COEF_FORMAT`, and `DWB_GAMUT_REMAPA/B_*` define gamut-remap mode, coefficient format, and two sets of 3x4-style remap coefficients.
- `DWB_OGAM_CONTROL`, `DWB_OGAM_LUT_INDEX`, `DWB_OGAM_LUT_DATA`, and `DWB_OGAM_LUT_CONTROL` define output gamma mode, direct/selectable RAM behavior, LUT index/data access, read/write color mask, test-status selection, and disconnect controls.
- `DWB_OGAM_RAMA_*` and `DWB_OGAM_RAMB_*` define start/end/base/slope/offset controls for blue, green, and red channels plus region metadata for paired exponential regions 0-33 in RAM A and RAM B.

The OGAM region definitions are highly repetitive and dense: each paired region register carries two LUT-offset fields and two segment-count fields. Generated consistency is important because a syntactically valid field with a wrong channel, RAM bank, region number, shift, or mask would affect writeback color conversion and validation rather than failing at compile time.

## Legacy VGA And VGA Interface Fields

The chunk defines a large set of legacy VGA-compatible register fields:

- `VGA_MEM_WRITE_PAGE_ADDR`, `VGA_MEM_READ_PAGE_ADDR`, `VGA_MEMORY_BASE_ADDRESS`, `VGA_MEMORY_BASE_ADDRESS_HIGH`, `VGA_DISPBUF1_SURFACE_ADDR`, and `VGA_DISPBUF2_SURFACE_ADDR` define page/base/surface addressing fields.
- `VGA_RENDER_CONTROL`, `VGA_SEQUENCER_RESET_CONTROL`, `VGA_MODE_CONTROL`, `VGA_SURFACE_PITCH_SELECT`, `VGA_HDP_CONTROL`, and `VGA_CACHE_CONTROL` define blink/render behavior, sequencer-reset blanking per display, VGA address/count/memory enable and timing select controls, pitch selection, HDP flush/idle behavior, and cache/debug controls.
- `D1VGA_CONTROL` through `D6VGA_CONTROL` define per-pipe VGA mode, timing select, sync polarity, overscan color enable, and overscan color fields.
- `VGA_STATUS`, `VGA_INTERRUPT_CONTROL`, `VGA_STATUS_CLEAR`, `VGA_INTERRUPT_STATUS`, `VGA_MAIN_CONTROL`, `VGA_TEST_CONTROL`, and `VGA_QOS_CTRL` expose mode/status, interrupt enable/type/ack, clear bits, main-clock/reset/test controls, and QOS.
- Legacy indexed/register data definitions include `CRTC8_IDX`, `CRTC8_DATA`, `SEQ8_IDX`, `SEQ8_DATA`, `GRPH8_IDX`, `GRPH8_DATA`, `ATTRX`, `ATTRDW`, `ATTRDR`, `DAC_MASK`, `DAC_R_INDEX`, `DAC_W_INDEX`, `DAC_DATA`, `GENFC_WT/RD`, `GENMO_WT/RD`, `GENS0`, `GENS1`, and `GENENB`, with duplicated `_1` aliases for some index/data/status/control fields.
- `VGA_SOURCE_SELECT` selects the VGA source.

The `dcn_dc_mmhubbub_vgaif_dispdec` address block follows with `MCIF_CONTROL`, `MCIF_WRITE_COMBINE_CONTROL`, and outstanding-counter registers for MMHUBBUB VGA interface phases. These fields connect legacy VGA memory access behavior to the display memory hub.

## MCIF Writeback Buffer Management

The `dcn_dc_mmhubbub_mcif_wb0_dispdec` block defines the memory-client interface used by display writeback:

- `MCIF_WB_BUFMGR_SW_CONTROL` controls enablement, buffer programming, swap modes, buffer stride selection, field selection, overflow/interrupt acknowledgements, frame-buffer control, and buffer-disable behavior.
- `MCIF_WB_BUFMGR_STATUS` exposes software/VCE lock state, buffer-manager state, active buffer, overflow, and frame counters.
- `MCIF_WB_BUF_PITCH` defines luma/chroma pitch fields.
- `MCIF_WB_BUF_{1..4}_STATUS` defines active, software-locked, VCE-locked, overflow, disable, mode, buffer tag, next buffer, and current line fields for each of four buffers.
- `MCIF_WB_BUF_{1..4}_STATUS2` defines new-content, color-depth, TMZ black-pixel/TMZ, luma/chroma overrun, and eye-flag fields.
- `MCIF_WB_BUF_{1..4}_ADDR_Y`, `_ADDR_C`, `_ADDR_Y_HIGH`, and `_ADDR_C_HIGH` define low and high address fields for luma and chroma planes.
- `MCIF_WB_BUF_{1..4}_RESOLUTION` defines per-buffer width and height fields.
- `MCIF_WB_ARBITRATION_CONTROL`, `MCIF_WB_SCLK_CHANGE`, `MCIF_WB_NB_PSTATE_CONTROL`, `MCIF_WB_NB_PSTATE_LATENCY_WATERMARK`, `MCIF_WB_WATERMARK`, `MULTI_LEVEL_QOS_CTRL`, and `MCIF_WB_MIN_TTO` define arbitration slice, time-per-pixel, clock/pstate force controls, watermark values/masks/types, max scaled time-to-urgent, and minimum time-to-urgent.
- `MCIF_WB_TEST_DEBUG_INDEX` and `MCIF_WB_TEST_DEBUG_DATA` provide indexed debug access.
- `MCIF_WB_BUFMGR_VCE_CONTROL` defines VCE lock ignore, VCE interrupt enable/ack, VCE slice interrupt enable, VCE lock, and slice size.
- `MCIF_WB_CLOCK_GATER_CONTROL`, `MCIF_WB_SELF_REFRESH_CONTROL`, `MCIF_WB_SECURITY_LEVEL`, `MCIF_WB_BUF_LUMA_SIZE`, `MCIF_WB_BUF_CHROMA_SIZE`, `MCIF_WB_VMID_CONTROL`, and `MCIF_WB_PSTATE_CHANGE_DURATION_VBI` define clock gating, per-frame self-refresh, security level/space, buffer sizes, VMID selection, and UCLK/FCLK pstate-change duration during VBI.

Many of these fields are stateful hardware controls or volatile status. Buffer address, high-address, resolution, pitch, security, and VMID fields directly influence where display writeback writes memory. Status2 fields expose overrun and TMZ/security indicators that are useful as test and diagnostic signals.

## Control Flow

There is no executable control flow in this header. Runtime flow is supplied by AMDGPU display code that includes the matching generated `dcn_3_2_0_offset.h` and this `dcn_3_2_0_sh_mask.h` file, then expands generated token-pasting macros into register tables.

Typical runtime usage is:

1. DCN 3.2 resource, IRQ, DMUB/DMCUB, GPIO, writeback, or hardware-sequencer code selects a hardware block instance and a generated register offset.
2. Register list macros or `SF`/`SR`/`SRI`-style generated macros bind the offset with one or more `_SHIFT`/`_MASK` symbols from this file.
3. Register helpers such as `REG_SET`, `REG_UPDATE`, `REG_GET`, `REG_WRITE`, and wait/poll helpers use the mask/shift pair to write packed values, preserve unrelated bits, decode status, or acknowledge events.
4. The hardware block latches the written values, reports status, raises interrupts, clears latched bits, performs firmware communication, captures writeback frames, accesses memory, or changes power/clock/reset state according to the block-specific sequencing rules.

This header does not encode sequencing constraints, access width, reset values, volatile behavior, write-one-to-clear semantics, double-buffer timing, or inter-register ordering. Those rules live in the hardware specification and in the display driver code that consumes these macros.

## State And Persistence Behavior

No software state is stored by this file. It describes MMIO-backed hardware state whose lifetime is controlled by display hardware, display firmware, modesets, resets, power-gating, suspend/resume, hotplug, writeback jobs, and runtime display operations.

Persistent or latched configuration fields in this chunk include interrupt destinations and types/enables, DMU/DMCUB clock/reset/security/memory-region configuration, DMCUB inbox/outbox base/size/pointers, display power-gating domain force/enables, DWB flow/color/gamut/OGAM/LUT/window/output controls, VGA mode/address/cache/HDP controls, MCIF writeback buffer addresses/pitch/resolution/security/VMID/arbitration/QOS/watermark settings, and MMHUBBUB warmup QOS/AWID/enable controls.

Volatile readback or status fields include interrupt status bits, power domain status, clock-on and reset-status bits, DMCUB fault/status/timer/scratch/GPINT values, DWB CRC values/backpressure/overflow counters, VGA status/interrupt status, MCIF outstanding counters, writeback buffer active/locked/overflow/current-line/new-content/TMZ/overrun/eye flags, pstate/watermark-related readback, and MMHUBBUB warmup interrupt/status fields.

Side-effecting write fields include interrupt acknowledgements, clear bits, soft resets, secure reset and fault clears, DMCUB external interrupt ack, DCPG power-up/power-down acks, DWB overflow clear/ack and soft reset, VGA status/interrupt clears, buffer-manager overflow and VCE interrupt ack, and warmup SW interrupt ack. Treating these fields as ordinary booleans can lose latched events, clear diagnostics, force resets, or desynchronize hardware/firmware handshakes.

## Dependencies And Integration Points

This chunk depends on the matching generated offset header:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_2_0_offset.h`

That companion file supplies register addresses and base indices; this header supplies the field layout. The two files must stay generated from the same DCN 3.2.0 register database. Runtime integration is normally through generated register-list and mask/shift-list macros in AMDGPU Display Core rather than direct hand-written references to every symbol.

Important source-tree integration points include:

- DCN 3.2 resource construction, which builds per-block register/shift/mask tables for display hardware instances.
- IRQ service code that enables, routes, types, reads, and acknowledges OTG/DIG/I2C/HPD/AUX/DSC/HPO/SMU/DCPG/DMCUB events.
- DMUB/DMCUB service code that configures firmware-visible regions, inbox/outbox rings, GPINT payloads, interrupts, scratch registers, timers, faults, security, and memory power.
- Hardware sequencing and power-management code that manages DMU clocks, display power-gating domains, deep-sleep forcing, resets, and DMCUB memory/power state.
- Display writeback code that programs DWB capture windows, source/output formats, CRC, color remap, OGAM LUTs, MCIF buffer addresses, security/VMID, watermarks, pstate controls, overflow handling, and VCE lock coordination.
- Legacy VGA paths and early/fallback display initialization code that uses VGA memory, render, status, interrupt, indexed-register, and source-select fields.
- Diagnostics and validation paths that rely on CRC results, overflow counters, fault addresses, debug-index/data registers, scratch registers, current-line/status fields, and outstanding counters.

Because the file contains only preprocessor constants, missing or renamed symbols tend to fail at build time. Incorrect numeric values, swapped instance prefixes, or wrong masks usually compile cleanly and only appear as hardware misbehavior.

## Risks And Edge Cases

- Bitfield drift from the authoritative DCN 3.2.0 register database is the main risk. Wrong masks or shifts can silently corrupt MMIO programming.
- The chunk boundaries are artificial. The first visible register, `OTG2_INTERRUPT_DEST`, is partial and contains only tail masks here. The final visible register, `MMHUBBUB_WARMUP_CONTROL_STATUS`, is also partial and lacks its masks in this chunk.
- Interrupt destination fields are repetitive across OTG3-5 and across HPD/AUX/DDC/DIG instances. Copy-generation or instance-prefix errors may route interrupts to the wrong destination without causing compile errors.
- Status, enable, type, and ack fields appear in similar register families. Confusing them can miss interrupts, repeatedly handle stale interrupts, or clear events before software observes them.
- DMCUB region, code-window, inbox/outbox, and GPINT fields are firmware interface contracts. Incorrect addresses, sizes, pointers, or interrupt bits can break host/firmware communication, fault handling, or secure memory isolation.
- Security and fault-control fields such as DMCUB security level, DMCUB fault clear, MCIF writeback security level/space, TMZ status, VMID, and buffer addresses have security and memory-corruption implications if masks drift.
- Power, clock, reset, and memory-power fields are sequencing-sensitive. Wrong masks can leave hardware clock-gated, stuck in reset, powered off, or reporting stale status after suspend/resume or runtime power transitions.
- DWB color-processing fields are dense and channel/bank/region-specific. Errors in gamut remap coefficients, LUT index/data controls, OGAM RAM A/B region offsets, segment counts, slopes, bases, or offsets may produce subtle color corruption in writeback output.
- MCIF writeback buffer fields control memory write targets and capture scheduling. Address, pitch, resolution, buffer-status, watermark, pstate, and arbitration mistakes can cause overflows, underruns, corrupted captured frames, or writes to the wrong memory region.
- Legacy VGA registers have compatibility-sensitive semantics. Changes can affect boot display, fallback paths, VGA console handoff, or systems relying on legacy indexed register behavior.
- Generated field names that include the word `MASK` may legitimately produce names ending in `_MASK_MASK`; scripts should not normalize or de-duplicate generated names by hand.

## Test Signals

Useful validation signals for this chunk include:

- Build AMDGPU Display Core with DCN 3.2.0 support enabled. Missing, malformed, or renamed macros should fail in DCN 3.2 resource, IRQ, DMUB/DMCUB, GPIO, writeback, or hardware-sequencer code that expands generated register tables.
- Mechanically compare this line range against a regenerated `dcn_3_2_0_sh_mask.h` or the authoritative DCN 3.2.0 register database, preserving the partial beginning and partial ending register families.
- Run generated-header consistency checks for each complete register in this range: every intended field should have matching `_SHIFT` and `_MASK`, masks should be 32-bit register-positioned values, fields should not overlap unexpectedly, and repeated instance layouts should match where the hardware spec says they are identical.
- Exercise interrupt enable/type/status/ack paths for OTG3-5 vertical/vupdate/vready/vstartup/DRR events, DIG stream-disable/training events, HPD/DDC/AUX events, DSC events, HPO events, SMU/DMCUB events, and DCPG power events.
- Validate DMCUB boot and communication: region programming, inbox/outbox ring setup, GPINT payloads, scratch register exchange, timer interrupts, external interrupt ack, undefined-address/fetch/write fault reporting, and secure reset/fault-clear paths.
- Test display power-management cycles, including runtime power gating, suspend/resume, hotplug after resume, deep-sleep forcing, and clock/reset status readback.
- Exercise display writeback capture paths with multiple formats, window sizes, color depths, gamut remap/OGAM enabled and disabled, CRC capture, overflow handling, host-read control, and soft reset.
- Validate MCIF writeback with four-buffer rotation, luma/chroma addresses including high-address bits, pitch/resolution changes, VMID/security/TMZ settings, VCE locks, pstate/watermark changes, and overrun/overflow status handling.
- Exercise legacy VGA paths where supported: boot console handoff, VGA mode enable/disable, indexed CRTC/SEQ/GRPH/ATTR/DAC access, interrupt/status clear behavior, and VGA memory base/page programming.
- Use runtime register dumps before and after modeset, writeback, interrupt, suspend/resume, and fault-injection tests to confirm packed writes affect only intended bits and status decoding matches hardware behavior.

## Cross-Chunk Notes

The previous chunk owns the beginning of `OTG2_INTERRUPT_DEST`; this chunk only sees the tail mask definitions for that register. The next chunk owns the masks and any remaining fields for `MMHUBBUB_WARMUP_CONTROL_STATUS`. The final merged report for `dcn_3_2_0_sh_mask.h` should reconcile those boundaries and should not treat this chunk alone as complete coverage for either boundary register.
