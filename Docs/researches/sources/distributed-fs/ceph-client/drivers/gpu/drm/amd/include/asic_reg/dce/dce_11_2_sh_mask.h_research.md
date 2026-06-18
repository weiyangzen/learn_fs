# Research: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dce/dce_11_2_sh_mask.h

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-001524`: lines 1-4038, `Docs/researches/chunks/subset-b-001524_research.md`
- `subset-b-001525`: lines 4039-7906, `Docs/researches/chunks/subset-b-001525_research.md`
- `subset-b-001526`: lines 7907-11514, `Docs/researches/chunks/subset-b-001526_research.md`
- `subset-b-001527`: lines 11515-15026, `Docs/researches/chunks/subset-b-001527_research.md`
- `subset-b-001528`: lines 15027-18695, `Docs/researches/chunks/subset-b-001528_research.md`

## Chunk Research

### subset-b-001524: lines 1-4038

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dce/dce_11_2_sh_mask.h lines 1-4038

## Purpose

This chunk is the first generated register field mask/shift segment for AMD DCE 11.2 display hardware. It contains no executable code; it defines C preprocessor constants that describe bit masks and bit shifts for MMIO register fields. Driver code includes this header together with `dce_11_2_d.h`: the `_d.h` header supplies register addresses such as `mmCRTC_MASTER_UPDATE_MODE`, while this `_sh_mask.h` header supplies field extraction and insertion metadata such as `CRTC_MASTER_UPDATE_MODE__MASTER_UPDATE_MODE_MASK` and `CRTC_MASTER_UPDATE_MODE__MASTER_UPDATE_MODE__SHIFT`.

The assigned range covers the file prologue, include guard, and the first 4,013 `#define` lines. It defines 2,006 mask constants and 2,006 matching shift constants across 584 register names. The range begins with display pipe power-gating and DCPG interrupt fields, moves through BL/ABM, CRTC timing/control/status, DAC, performance counters, DCCG/display-clock controls, DMIF/MCIF/DCI memory interface controls, DCIO/UNIPHY/link and panel/backlight controls, and ends inside the `DC_GPIO_DDC2_MASK` field group after `DC_GPIO_DDC2CLK_PD_EN`.

This is hardware-contract data, not an algorithm. Its value is that the display, power, and clock-manager code can use common field helper macros (`set_reg_field_value`, `get_reg_field_value`, `REG_SET`, `REG_UPDATE`, mask-list initializers, and powerplay field macros) without hard-coding bit positions at every call site.

## Important APIs, Types, And Functions

This chunk declares no functions, structs, typedefs, or enums. The important exported API surface is the naming convention and the generated constants:

- `REGISTER__FIELD_MASK`: a constant with the target field bits already positioned in the 32-bit register word.
- `REGISTER__FIELD__SHIFT`: the corresponding low-bit position used to shift an unpositioned value into or out of the field.
- Full-register data fields use `0xffffffff` masks and shift `0`, for example debug data, CRC result, DTO phase/modulo, and reserved macro-control registers.
- Repeated per-pipe/per-link families keep stable field names under distinct register names, for example `PIPE0_PG_STATUS` through `PIPE5_PG_STATUS`, `CRTC0_PIXEL_RATE_CNTL` through `CRTC5_PIXEL_RATE_CNTL`, `PHYPLLA_PIXCLK_RESYNC_CNTL` through `PHYPLLF_PIXCLK_RESYNC_CNTL`, and `UNIPHYA_LINK_CNTL` through `UNIPHYLPB_LINK_CNTL`.
- The header guard is `DCE_11_2_SH_MASK_H`.

Consumers found in this tree include:

- `drivers/gpu/drm/amd/display/dc/clk_mgr/dce112/dce112_clk_mgr.c`, where `CLK_COMMON_MASK_SH_LIST_DCE_COMMON_BASE(__SHIFT)` and `_MASK` populate clock-manager shift/mask tables from these symbols.
- `drivers/gpu/drm/amd/display/dc/dce112/dce112_compressor.c`, where low-power tiling and compression setup uses field helpers with masks from this header and register addresses from `dce_11_2_d.h`.
- `drivers/gpu/drm/amd/display/dc/hwss/dce112/dce112_hwseq.c`, where `DVMM_PTE_REQ` fields are read and written during display power-gating/PTE initialization.
- `drivers/gpu/drm/amd/display/dc/resource/dce112/dce112_resource.c`, which assembles DCE 11.2 resource objects and register tables.
- `drivers/gpu/drm/amd/pm/powerplay/smumgr/vegam_smumgr.c`, where powerplay/SMU code has access to DCE 11.2 display fields alongside SMU/GMC/OSS/GFX register definitions.

## Covered Register Groups

The first group describes display pipe power-gating:

- `PIPE0_PG_CONFIG` through `PIPE5_PG_CONFIG` expose `PIPE*_POWER_FORCEON`.
- `PIPE0_PG_ENABLE` through `PIPE5_PG_ENABLE` expose `PIPE*_POWER_GATE`.
- `PIPE0_PG_STATUS` through `PIPE5_PG_STATUS` expose PGFSM read data, debug power status, desired/requested power state, and PGFSM power status.

The DCPG and display power-control block follows:

- `DCPG_INTERRUPT_STATUS`, `DCPG_INTERRUPT_CONTROL`, and `DCPG_INTERRUPT_CONTROL2` cover power-up/power-down interrupt status, masks, and clears for DCFE0-5, DCFEV0/1, and DSI.
- `DC_IP_REQUEST_CNTL`, `DC_PGFSM_CONFIG_REG`, `DC_PGFSM_WRITE_REG`, and `DC_PGCNTL_STATUS_REG` expose IP request enable, PGFSM access registers, SW request busy/force status, IP request ignore status, and ECO debug bits.
- `DCPG_TEST_DEBUG_INDEX` and `DCPG_TEST_DEBUG_DATA` are index/data debug accessors.

The BL/ABM segment describes backlight PWM and adaptive backlight management:

- `BL1_PWM_*` fields hold ambient, user, target/current ABM, final/minimum duty-cycle levels, ABM enable/source behavior, sample-rate counters, and group-2 lock/update controls.
- `DC_ABM1_*` fields configure ABM enable/source, input color-space coefficients, ACE slopes/offsets/thresholds, high/low-gain sample settings, histogram/luma result readback, overscan pixel values, and ABM register locks.
- `ABM_TEST_DEBUG_INDEX` and `ABM_TEST_DEBUG_DATA` provide ABM debug index/data access.

The CRTC segment is the largest early block and describes timing generator state:

- Horizontal and vertical timing fields cover totals, blanking windows, sync A/B windows, sync polarity/output enable, vertical-total min/max/control, vertical-total/nominal-vsync interrupts, and DTM test status.
- Trigger and synchronization controls include `CRTC_TRIGA_CNTL`, `CRTC_TRIGB_CNTL`, manual trigger bits, force-count-now controls, flow control, stereo force/status/control, snapshot controls, start-line controls, and GSL gap/window/control fields.
- `CRTC_CONTROL`, `CRTC_BLANK_CONTROL`, `CRTC_INTERLACE_CONTROL`, `CRTC_STATUS`, `CRTC_STATUS_POSITION`, frame counters, update locks, double-buffer controls, master update controls, and static-screen controls expose the main runtime state of the timing generator.
- Test and validation fields include test-pattern controls, pixel data readback, CRC window setup and CRC data readback for CRC0/CRC1, external timing sync controls and interrupts, and CRTC debug index/data access.

The DAC, performance, and DCCG portions describe legacy output and clocking:

- `DAC_*` fields cover DAC enable, source selection, CRC, sync tristate/stereosync, autodetect controls/status/interrupts, forced output/data, powerdown, comparator behavior, FIFO status, and debug index/data.
- `PERFCOUNTER_*` and `PERFMON_*` fields expose counter enables, source selections, state, thresholds, high/low data, interrupt controls, and debug access.
- `REFCLK_CNTL`, `DPREFCLK_CNTL`, `DCE_VERSION`, AVSYNC counter registers, DCCG GTC/DS DTO fields, DMCU/SMU interrupt controls, DAC/DVO clock enables, DCCG clock-gate disable controls, CGTT turn-on/off delays, pixel-clock resync controls, time-base dividers, display-clock ramp controls, global memory power request disable, and DCCG performance monitor enables are all covered before the per-CRTC DTO block.
- Per-CRTC pixel-rate controls (`CRTC0_PIXEL_RATE_CNTL` through `CRTC5_PIXEL_RATE_CNTL`), DisplayPort DTO phase/modulo registers, and PHYPLL pixel-rate controls are defined in repeated groups.
- Soft-reset, SYMCLK enable, audio DTO source/phase/module, DCCG test debug, test clock selection, CPLL/PLL reserved macro controls, and `DENTIST_DISPCLK_CNTL` fields support display clock generation and diagnostic paths.

The DMIF, MCIF, DCI, and DVMM segment describes memory/display fabric behavior:

- `DMIF_CONTROL`, `DMIF_STATUS`, `DMIFV_STATUS`, arbitration controls, pipe arbitration controls, VMID selection, urgency overrides, address-calculation, max-request, and debug fields describe display memory interface arbitration and status.
- `DVMM_REG_RD_STATUS`, `DVMM_REG_RD_DATA`, `DVMM_PTE_REQ`, `DVMM_CNTL`, fault status/address, and `DVMM_PTE_PGMEM_*` fields describe display VM/PTE request behavior, fault reporting, and PTE program-memory power state.
- `LOW_POWER_TILING_CONTROL`, `MCIF_CONTROL`, write-combine control, MCIF VMID/memory-control, pipe-disable fields, memory-controller NACK status, RBBMIF timeout/status/disable, and DCI memory power status/control fields cover memory routing, low-power tiling, timeout handling, and power-state observability.
- `DCI_CLK_CNTL`, `DCI_CLK_RAMP_CNTL`, `DCI_SOFT_RESET`, `DCI_MISC`, and DCI debug/test fields control DCI clock gating, resets, writeback urgency, and debug selection.
- `PIPE0_DMIF_BUFFER_CONTROL` through `PIPE5_DMIF_BUFFER_CONTROL` expose per-pipe buffer allocation and completion status.

The DCIO, UNIPHY, panel, timer, and GPIO segment covers display link IO setup:

- `DC_GENERICA`, `DC_GENERICB`, `DC_PAD_EXTERN_SIG`, `DC_REF_CLK_CNTL`, and `DC_GPIO_DEBUG` expose generic clock/signal routing and debug-loopback controls.
- `UNIPHYA_LINK_CNTL` through `UNIPHYLPB_LINK_CNTL` cover link pixel-valid reset, channel inversion, lane stagger, HPD link-enable masking, and pixel-frequency-change controls. Channel crossbar groups map output channels for the same links.
- `UNIPHY_IMPCAL_*`, `AUXP_IMPCAL`, `AUXN_IMPCAL`, `DCIO_IMPCAL_CNTL*`, and `UNIPHY_IMPCAL_PSW_*` expose impedance calibration controls, status, calibration enable/range, and pull-up/pull-down settings.
- `DCIO_WRCMD_DELAY`, `DC_PINSTRAPS`, `DC_DVODATA_CONFIG`, `LVTMA_PWRSEQ_*`, `BL_PWM_*`, and `BL_PWM_GRP1_REG_LOCK` describe panel/power-sequence/backlight PWM timing and locking.
- `DCIO_GSL_*`, GPU timer start/read controls, DCIO clock/debug/soft-reset fields, external vsync controls, debug output, DPHY selection, DPCS TX/RX interrupts, semaphores, and DCIO debug registers cover display IO synchronization, diagnostics, and interrupt state.
- The chunk ends in the GPIO/DDC section after `DC_GPIO_DDC2_MASK__DC_GPIO_DDC2CLK_PD_EN__SHIFT`; the rest of `DC_GPIO_DDC2_MASK` and later GPIO groups are outside this chunk.

## Control Flow

There is no runtime control flow in this header. The only compile-time control is the include guard:

1. If `DCE_11_2_SH_MASK_H` is not defined, define it.
2. Expose thousands of field mask and shift macros.
3. The closing `#endif` is outside this chunk at the end of the complete file.

Runtime behavior appears in consumers. A typical consumer reads a 32-bit MMIO register, extracts a field with `get_reg_field_value(value, REGISTER, FIELD)`, or builds a modified value with `set_reg_field_value(value, new_value, REGISTER, FIELD)` before writing it back. Those helper macros depend on `REGISTER__FIELD_MASK` and `REGISTER__FIELD__SHIFT` having exact names and exact values.

The table-style consumers use the same constants indirectly. For example, DCE clock-manager code initializes `struct clk_mgr_shift` with the `__SHIFT` variants and `struct clk_mgr_mask` with the `_MASK` variants. That lets later clock code operate through register tables instead of spelling every bit position directly.

## State And Persistence Behavior

This file does not allocate memory, define static variables, persist data, or perform MMIO. Its "state" is compile-time metadata that becomes constants in object code after preprocessing and compilation.

Hardware state is affected only when consumers use these macros to read-modify-write DCE 11.2 registers. Those writes can change persistent-until-reset hardware state such as power-gating enables, interrupt masks/clear bits, display timing generator control, clock-gate settings, memory-interface power controls, link PHY controls, backlight PWM duty/period, and GPIO/DDC/AUX pad settings.

Several fields in this chunk are status or readback-only from the software perspective, such as `*_STATUS`, `*_OCCURRED`, CRC data, pixel readback, PGFSM power state, memory power state, and debug result fields. Others are write-trigger or clear bits, such as interrupt clear fields, reset bits, force-update bits, and manual-trigger controls. The header itself does not encode access permissions, so access semantics must come from hardware documentation and the consuming driver code.

## Dependencies

This header depends only on the C preprocessor. It is generated as part of the ASIC register header set and must stay synchronized with the DCE 11.2 hardware register address header:

- `dce/dce_11_2_d.h` supplies the `mm...` register offsets that pair with these `REGISTER__FIELD_*` macros.
- Display Core helpers in `dm_services.h`, register table macros in DCE clock/resource code, and powerplay field access macros depend on the exact `REGISTER__FIELD_MASK` and `REGISTER__FIELD__SHIFT` naming scheme.
- Related ASIC block headers, such as GMC, SMU, OSS, BIF, and GFX register headers, are included alongside this one in consumers when display code interacts with memory compression, SMU power management, or firmware-controlled clock/power paths.
- The generated DCE register families for other versions (`dce_8_0_sh_mask.h`, `dce_10_0_sh_mask.h`, `dce_11_0_sh_mask.h`) provide parallel definitions. DCE 11.2 consumers rely on this version matching the DCE 11.2 address map and field layout, not merely on compatible names.

## Integration Points

The primary integration point is AMD Display Core support for DCE 11.2 GPUs. `dce112_*` modules include this header to build register, mask, and shift tables for:

- Display clock management and DP reference clock handling.
- Frame-buffer compression and low-power tiling setup.
- Hardware sequencing, display power-gating, and display VM/PTE programming.
- Resource construction for DCE 11.2 display pipes, timing generators, links, and support blocks.

The powerplay/SMU integration point is `vegam_smumgr.c`, which includes DCE 11.2 display fields alongside SMU and memory-controller fields. This allows power-management code to coordinate display-related state with firmware, clock, and voltage behavior.

The generated constants also integrate with common debug and test infrastructure. The many `*_TEST_DEBUG_INDEX`, `*_TEST_DEBUG_DATA`, `*_DEBUG*`, CRC, performance counter, semaphore, and interrupt-control fields are the symbolic bridge between register dump code, diagnostics, and real hardware bit positions.

## Risks And Edge Cases

- This file is a hardware ABI. A wrong mask or shift silently misprograms hardware even though the C code still compiles.
- The mask/shift pairs must remain synchronized. A correct mask with a stale shift, or vice versa, corrupts field extraction and insertion.
- Some names intentionally contain doubled words such as `*_MASK_MASK` for fields whose hardware field name ends in `MASK`. Scripts or manual refactors that try to normalize these names can break consumers.
- Repeated families are high-risk for copy/generation drift. A single wrong pipe/link suffix in a `PIPE*`, `CRTC*`, `PHYPLL*`, `SYMCLK*`, `UNIPHY*`, `DMIF*`, or GPIO/DDC group can route updates to the wrong display instance.
- Write-one-to-clear, interrupt clear, reset, force, and lock fields are mixed with status fields. Consumers must understand register semantics before writing a value built from these masks.
- Full-register `0xffffffff` masks are valid in debug/data/reserved registers. Automated validation should not assume every field is narrower than 32 bits.
- This chunk ends in the middle of a logical GPIO/DDC register group. The following chunk must be consulted for the remainder of `DC_GPIO_DDC2_MASK` and subsequent DDC/GPIO definitions before making per-register conclusions.
- The closing include-guard `#endif` is outside this chunk. That is expected because this is only chunk 1 of 5 for the complete header.
- Because the header is included by both display and power-management code, any accidental global macro rename or value change can have a broad build and runtime blast radius.

## Test Signals

Useful validation is mostly build-time, static, and hardware bring-up oriented:

- Compile all DCE 11.2 display and Vegam powerplay users with this header and `dce_11_2_d.h`; missing or renamed macros should fail compilation in field helper/table initializers.
- Run static checks that every field has exactly one `_MASK` define and one `__SHIFT` define, except the header guard. This chunk has 2,006 mask/shift pairs.
- Mechanically verify that each mask is consistent with its shift and field width, including legal full-register masks.
- Compare generated DCE 11.2 masks/shifts against the authoritative register database or AMD-generated source; do not hand-edit values without regenerating or proving the delta.
- Exercise display bring-up, mode set, power-gating enable/disable, suspend/resume, and clock changes on DCE 11.2 hardware.
- Exercise frame-buffer compression and low-power tiling paths, since compressor code uses fields from this chunk such as `LOW_POWER_TILING_CONTROL`.
- Validate CRTC timing, vertical interrupts, CRC capture, test pattern, stereo/snapshot/GSL, and static-screen behavior through display tests and register readback.
- Validate DP/DAC/link IO behavior, including UNIPHY link setup, pixel clock DTO/resync, HPD/DDC/AUX GPIO behavior, panel power sequencing, and backlight PWM programming.
- Check interrupt clear/mask behavior for DCPG, CRTC, DAC autodetect, external timing sync, SMU/DC, DPCS TX/RX, and static-screen events.
- Use register dump comparisons to confirm that field helper macros set only the intended bits when programming representative registers from every major group in this chunk.

### subset-b-001525: lines 4039-7906

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dce/dce_11_2_sh_mask.h lines 4039-7906

## Scope And Purpose

This chunk is a generated-style register shift/mask header segment for AMDGPU DCE 11.2 display hardware. It contains only C preprocessor constants, with paired `*_MASK` and `*__SHIFT` macros that describe bitfields inside display-engine MMIO registers. The chunk starts in the `DC_GPIO_DDC2_*` definitions and ends at `DMCU_INTERRUPT_STATUS__DCPG_IHC_DCFE0_POWER_UP_INT_OCCURRED__SHIFT`; earlier GPIO and display-control definitions, plus later DMCU interrupt/status fields, are outside this work item.

There are no functions, structs, enums, or executable branches here. The public contract is the macro namespace consumed by AMDGPU display, power-management, and firmware-loading code. Consumers combine these field constants with the sibling DCE 11.2 address header (`dce_11_2_d.h`) and register helpers such as `REG_SET_FIELD`, `RREG32`, and `WREG32` to read, compose, update, or poll hardware register values without embedding raw bit positions in driver code.

## Important APIs, Types, And Macro Families

The chunk exposes several large register families:

- GPIO and display connector pads: `DC_GPIO_DDC2` through `DC_GPIO_DDC6`, `DC_GPIO_DDCVGA`, `DC_GPIO_SYNCA`, `DC_GPIO_GENLK`, `DC_GPIO_HPD`, `DC_GPIO_PWRSEQ`, `DC_GPIO_I2CPAD`, `DC_GPIO_I2S_SPDIF`, `DC_GPIO_RECEIVER_EN0/1`, `DC_GPIO_AUX_CTRL_*`, `DC_GPIO_HPD_CTRL_*`, and `DC_GPIO_TX12_EN` describe DDC/AUX, VGA DDC, sync, genlock/swaplock, hotplug detect, backlight/power sequencing, I2C, audio pad, receiver-enable, slew/spike/filter, pad strength, and transmit-enable bits.
- Reserved PHY/macros: `DAC_MACRO_CNTL_RESERVED*`, `UNIPHY_MACRO_CNTL_RESERVED*`, `DCRX_PHY_MACRO_CNTL_RESERVED*`, and `DPHY_MACRO_CNTL_RESERVED*` map full 32-bit reserved register words. These still matter because generated tables or low-level bring-up code may preserve, save/restore, or compare reserved hardware state.
- Graphics plane, cursor, LUT, color, and transformation blocks: `GRPH_*`, `CUR_*`, `DC_LUT_*`, `DEGAMMA_CONTROL`, `DENORM_CONTROL`, `INPUT_CSC_*`, `OUTPUT_CSC_*`, `GAMUT_REMAP_*`, `COMM_MATRIX*`, `PRESCALE_*`, `REGAMMA_*`, `ALPHA_CONTROL`, `KEY_*`, `OUT_CLAMP_*`, and `OUT_ROUND_CONTROL` describe scanout surface format/addressing, page flip state, cursor surfaces, LUT programming, color-space matrices, gamut remap, gamma/regamma ramps, alpha blending, color keying, clamp, denorm, and rounding controls.
- Display core diagnostics and synchronization: `DCP_CRC_*`, `DCP_DEBUG*`, `DCP_TEST_DEBUG_*`, `DCP_GSL_CONTROL`, `DCP_LB_DATA_GAP_BETWEEN_CHUNK`, `DCP_SPATIAL_DITHER_CNTL`, `DCP_RANDOM_SEEDS`, `GRPH_XDMA_CACHE_UNDERFLOW_*`, and `GRPH_SURFACE_COUNTER_*` provide CRC capture, debug selectors, global-swap-lock coordination, line-buffer spacing, dither setup, random seed control, XDMA underflow detection, and surface counters.
- Display virtual memory: `DVMM_PTE_CONTROL` covers single-PTE use, page width/height, minimum PTEs before flip, and PTE buffer modes for display memory translation.
- DIG/TMDS/HDMI/AFMT output blocks: `DIG_FE_CNTL`, `DIG_BE_CNTL`, `DIG_LANE_ENABLE`, `DIG_OUTPUT_CRC_*`, `DIG_TEST_PATTERN`, `DIG_FIFO_STATUS`, `DIG_DISPCLK_SWITCH_*`, `TMDS_*`, `HDMI_*`, `AFMT_*`, `PHY_AUX_CNTL`, and `DVO_*` define digital encoder source selection, front/back-end enablement, lane enablement, CRC/test-pattern generation, FIFO calibration, display-clock switch interrupts, TMDS control symbols and DC balancing, HDMI scrambling/deep color/infoframe/generic packet/ACR/VBI/audio controls, Audio Format packet storage, AUX PHY, and legacy DVO analog-reference fields.
- DMCU firmware and interrupt interface: `DMCU_CTRL`, `DMCU_STATUS`, `DMCU_PC_START_ADDR`, `DMCU_FW_*`, `DMCU_RAM_ACCESS_CTRL`, `DMCU_ERAM_*`, `DMCU_IRAM_*`, `DMCU_EVENT_TRIGGER`, `DMCU_UC_INTERNAL_INT_STATUS`, `DMCU_SS_INTERRUPT_CNTL_STATUS`, and the first part of `DMCU_INTERRUPT_STATUS` define the display microcontroller reset/enable state, firmware address/checksum fields, host access to ERAM/IRAM, software interrupt generation, internal uC interrupt status, static-screen interrupts, ABM-ready/update interrupts, MCP/SCP/uC interrupts, external software interrupt, register read timeout, and the first DCPG/IHC power event in this chunk.

The naming convention is consistent: `REGISTER__FIELD_MASK` gives the raw bit mask, while `REGISTER__FIELD__SHIFT` gives the right shift needed to decode or encode the field. Names ending in `_MASK_MASK` are intentional because the underlying field name itself ends in `MASK`.

## Control Flow And Data Flow

This header has no runtime control flow. It enables compile-time substitution in register access paths. A typical data flow is:

1. Driver code reads a register address from `dce_11_2_d.h` with `RREG32()`.
2. The raw value is decoded with this header's `*_MASK` and `*__SHIFT` constants, or updated with `REG_SET_FIELD()`.
3. The composed value is written back with `WREG32()` or used as a polling predicate.

The chunk implies several hardware protocols even though the protocol code lives elsewhere:

- DDC/AUX/HPD/GPIO code masks pad output, enables input receivers, selects AUX-vs-DDC pad mode, handles pull-down/pull-up and drive strength, then reads `*_Y` or receiver status fields for connector detection and I2C/AUX transactions.
- Graphics scanout setup composes `GRPH_CONTROL`, pitch, primary/secondary surface address, endian/crossbar, tiling, compression, viewport, update, and flip-control fields before arming a page flip.
- Color-management paths program LUT indexes/data, input/output CSC matrices, degamma, prescale, gamut-remap, regamma region descriptors, clamp, and rounding fields in a hardware-defined order.
- HDMI/AFMT paths fill AVI/audio/MPEG/generic infoframes, channel-status words, ISRC payload bytes, ACR values, deep-color/scrambling controls, and send/continuous-send bits around encoder enablement.
- DMCU loading paths assert or release reset, enable host access to ERAM/IRAM, write firmware and interrupt-vector data, set start/end/checksum registers, trigger software interrupts, and check status/interrupt bits.

## State And Persistence Behavior

The header itself stores no state. State lives in DCE hardware registers, display microcontroller RAM, firmware-programmed registers, and connector-facing pad circuitry.

Important state classes represented by this chunk include:

- Mutable connector/pad state: DDC/AUX mode, clock/data enables, receiver enables, hotplug receiver state, pad drive strength, slew/spike controls, HPD controls, power-sequence GPIOs, and backlight/digital-on pins.
- Scanout and flip state: graphics surface addresses, high address bits, format, tiling, compression pitch, viewport boundaries, pending primary/secondary stereo surfaces, update locks, flip rate, and current in-use surface addresses.
- Color pipeline state: LUT indexes and data, black/white offsets, CSC matrices, prescale values, degamma/regamma/gamut modes, regamma piecewise-linear regions, alpha/key/clamp controls, and output rounding.
- Diagnostics and interrupt state: DCP/DIG CRC enable/result/last/current values, debug index/data ports, XDMA underflow counters and interrupt mask/ack bits, surface counter min/max, HDMI error status, display-clock-switch allowed interrupt bits, and DMCU static-screen or power/event interrupt bits.
- DMCU firmware state: reset/enable bits, program-counter start address, firmware start/end/ISR/checksum fields, ERAM/IRAM access control and data windows, internal interrupt status, and uC-to-host event state.

Many registers are sticky, latched, write-one-to-clear, or sequenced by hardware. For example, interrupt status fields often pair `*_OCCURRED` and `*_CLEAR` names on the same bit, and underflow/HDMI/DIG status registers include separate status, mask, and ack fields. Incorrect constants can therefore leave stale interrupts, clear the wrong event, or make a polling path wait forever.

## Dependencies And Integration Points

This header integrates with:

- The sibling DCE 11.2 address definitions in `include/asic_reg/dce/dce_11_2_d.h`.
- Generic AMDGPU register helpers and field macros that expect the `REGISTER__FIELD_MASK` and `REGISTER__FIELD__SHIFT` naming scheme.
- DCE 11.2 display code under `drivers/gpu/drm/amd/display/dc/`, including `display/dc/dce112/dce112_compressor.c`, `display/dc/hwss/dce112/dce112_hwseq.c`, `display/dc/resource/dce112/dce112_resource.c`, and `display/dc/clk_mgr/dce112/dce112_clk_mgr.c`, which include this exact header.
- Power-management code such as `pm/powerplay/smumgr/vegam_smumgr.c`, which includes `dce_11_2_d.h` and this shift/mask header for DCE 11.2 register programming.
- Older AMDGPU DCE implementations (`dce_v6_0.c`, `dce_v8_0.c`, `dce_v10_0.c`) that use equivalent field names for AFMT, HDMI, GRPH, REGAMMA, and related display blocks. They are useful examples of how these macro families are consumed even when they target earlier DCE generations.
- Firmware and user-visible feature plumbing around DMCU/ABM/static-screen behavior. DMCU firmware IDs and ABM status are exposed through AMDGPU firmware query paths, coredump output, and display power-management policy, while the actual register programming uses DCE-specific fields like those defined here.

## Risks And Edge Cases

The highest risk is mismatch between this generated header and the DCE 11.2 register database. Since these constants are used in read-modify-write sequences, a one-bit error can mutate a neighboring field while appearing syntactically valid.

Specific risk areas in this chunk are:

- Connector GPIO and HPD fields: wrong DDC/AUX/HPD/power-sequence bits can break EDID reads, DisplayPort AUX transactions, hotplug detection, panel power sequencing, backlight enablement, or pad electrical characteristics.
- Surface and flip fields: incorrect `GRPH_*` masks can program bad scanout addresses, pitch, tiling, compression, endian/crossbar, stereo flip, or update-lock state, producing corruption, blank displays, hangs, or missed vblank/flip completion.
- Color and LUT fields: malformed CSC, LUT, regamma, gamut, clamp, or dither masks can silently change color output, HDR/SDR conversion, gamma ramps, or cursor blending.
- HDMI/AFMT packet fields: errors in deep-color, scrambling, ACR, audio channel status, infoframe, ISRC, generic packet, or VBI fields can produce link compatibility problems or missing audio/video metadata.
- Interrupt and status fields: several names map status, mask, ack, occurred, and clear semantics onto adjacent or identical bits. Treating a clear bit as a status bit, or vice versa, can lose interrupts or cause repeated interrupts.
- DMCU RAM and firmware fields: bad ERAM/IRAM address, byte-enable, checksum, reset, host-access, or interrupt bits can prevent DMCU firmware load, ABM, PSR/static-screen flows, or uC/host signaling from working.
- Reserved register ranges: the large `*_RESERVED*` families are easy to dismiss, but save/restore or generated power tables may rely on them. Writing reserved fields without the matching ASIC sequence can be unsafe.
- Chunk boundary risk: this document covers only lines 4039-7906. The chunk begins after earlier DCE 11.2 definitions and ends mid-`DMCU_INTERRUPT_STATUS`; conclusions about the full header require the remaining chunks.

## Test Signals

There are no standalone unit tests for this header. Practical validation is indirect:

- Build coverage for AMDGPU display and power-management objects that include `dce_11_2_sh_mask.h`; this catches missing or renamed macros but not incorrect numeric values.
- Register-database comparison against the authoritative DCE 11.2 generated header or ASIC documentation, especially for GPIO, GRPH, HDMI/AFMT, REGAMMA, and DMCU fields.
- Display bring-up on DCE 11.2 hardware: connector detection, EDID/DDC, DP AUX, HPD IRQs, panel power/backlight sequencing, mode set, vblank, page flip, cursor, and suspend/resume should work without timeouts.
- Plane and color tests: framebuffer formats, tiling/compression, stereo or synchronized flips where supported, gamma/degamma/regamma LUT programming, CSC/gamut remap, alpha/keying, and cursor blending should match expected output.
- HDMI/audio tests: deep color, scrambling, ACR/N values, audio channel map/status, AVI/audio/MPEG infoframes, generic packets, and audio playback should be validated on compatible sinks.
- Diagnostic tests: CRC capture, DCP/DIG test patterns, FIFO calibration/status, XDMA underflow counters/interrupts, display-clock-switch interrupt handling, and surface counters provide signals that masks and ack bits line up with hardware.
- DMCU/ABM/static-screen tests: firmware load, ERAM/IRAM read/write windows, uC reset/release, software interrupt delivery, static-screen interrupt clear/status behavior, ABM ready/update events, and DCPG/IHC power interrupts should be exercised where platform firmware supports them.

### subset-b-001526: lines 7907-11514

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dce/dce_11_2_sh_mask.h lines 7907-11514

Chunk: `subset-b-001526`
Covered source range: lines 7907-11514 of `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dce/dce_11_2_sh_mask.h`

## Purpose

This chunk is a generated AMD DCE 11.2 register field mask/shift header segment. It contains no executable C logic; its exported surface is 3,608 preprocessor definitions, forming 1,804 mask/shift constants for DCE 11.2 display-controller register fields.

The constants follow the generated AMD register-header convention:

- `<REGISTER>__<FIELD>_MASK` is the bit mask for a field inside a 32-bit register.
- `<REGISTER>__<FIELD>__SHIFT` is the corresponding right-shift count.

This chunk covers the tail of DMCU interrupt/status definitions, then DisplayPort stream encoder and AUX-channel fields, DVO output fields, framebuffer compression, formatter/output pixel-processing fields, line-buffer and scaler fields, MVP stereo/video-port fields, and the beginning of color-manager input CSC/prescale fields. The companion address header is `dce_11_2_d.h`; this file supplies field layouts for those register names.

## Important APIs, Types, And Macro Families

There are no functions, structs, typedefs, or enums in this chunk. The effective API is the macro set consumed by AMDGPU/DC register helpers such as `REG_READ`, `REG_WRITE`, `REG_UPDATE`, `REG_SET_FIELD`, `REG_GET_FIELD`, `set_reg_field_value`, `get_reg_field_value`, `RREG32`, and `WREG32`.

Important macro families in this range:

- `DMCU_INTERRUPT_STATUS`, `DMCU_INTERRUPT_STATUS_1`, `DMCU_INTERRUPT_TO_HOST_EN_MASK`, `DMCU_INTERRUPT_TO_UC_EN_MASK*`, and `DMCU_INTERRUPT_TO_UC_XIRQ_IRQ_SEL*`: DMCU interrupt occurrence, clear, host mask, microcontroller routing, and IRQ/XIRQ selection fields for DCFE power up/down, DCFEV power events, vblank, static screen, ABM, SCP/MCP, software, and generic DMCU events.
- `DC_DMCU_SCRATCH`, `DMCU_INT_CNT`, `DMCU_FW_CHECKSUM_SMPL_BYTE_POS`, `DMCU_UC_CLK_GATING_CNTL`, `MASTER_COMM_*`, and `SLAVE_COMM_*`: scratch, interrupt count, firmware checksum sampling, clock-gating, and host/DMCU mailbox fields.
- `DMCU_PERFMON_INTERRUPT_STATUS1..5`, `DMCU_PERFMON_INTERRUPT_TO_UC_EN_MASK1..5`, and `DMCU_PERFMON_INTERRUPT_TO_UC_XIRQ_IRQ_SEL1..5`: status, clear, routing, and IRQ selection fields for display pipe perfmon counters across DCFE, DCO, DCP, DMIF, MCIF, ABM, DCPG, and related display blocks.
- `DMCU_DPRX_INTERRUPT_STATUS1`, `DMCU_DPRX_INTERRUPT_TO_UC_EN_MASK1`, and `DMCU_DPRX_INTERRUPT_TO_UC_XIRQ_IRQ_SEL1`: DisplayPort receiver-event status and routing fields, including DPRX and DPHY interrupt groups.
- `DP_*`: DisplayPort stream encoder fields for link enable, pixel format, MSA colorimetry/misc/VBID/timing override, video stream control, steering FIFO, DPHY training/scrambling/PRBS/CRC/fast training, secondary data packets, audio M/N readback, MST MSE rate and slot-allocation tables, and DP debug/index/data windows.
- `AUX_*` and `DP_AUX_DEBUG_*`: DisplayPort AUX channel enable/reset, software transaction control/status/data, arbitration, interrupt control, low-speed data/status, DPHY TX/RX controls/status, GTC sync status/error fields, and debug register windows.
- `DVO_*`: DVO enable, source select, output control, CRC, FIFO error status/ack/mask, and debug fields for legacy or external digital-video-output paths.
- `FBC_*`: framebuffer-compression control, source selection, idle-force clear mask, start/stop delay, compression mode/control, indirect LUT entries, CSM region offsets, client region masks, debug CSR access, status, alpha controls, and test-debug fields.
- `FMT_*`: output formatter clamp, dynamic expansion, control, bit-depth truncation/dithering/FRC/randomization, CRC controls/results/masks, side-by-side stereo, YCbCr 4:2:0 hblank early start, and formatter debug/index/data fields.
- `LB_*` and `LBV_*`: line-buffer and virtual/chroma line-buffer data format, memory control/size, desktop height, vline/vblank counters/status, sync reset, black/keyer color controls, buffer levels/urgency/status, no-outstanding-request status, and debug fields.
- `MVP_*` and `DC_MVP_LB_CONTROL`: multi-view/video-port or stereo related controls for AFR flip mode/FIFO, flip-line insertion, line-buffer routing, control/status, in-band capabilities, black keyer, CRC, receive counters, and debug registers.
- `SCL_*`: scaler coefficient RAM selection/data, scaler mode/tap/boundary/replication/automatic ratio controls, horizontal and vertical filter controls/ratios/init values, round offsets, update/pending/taken/lock/coef-complete bits, sharpness, ALU disable, coefficient conflict status, viewport/overscan, mode-change detection, and debug windows.
- `SCLV_*`: virtual/chroma scaler equivalents, including separate luma/chroma horizontal and vertical ratios/init values, viewport and overscan registers for primary and chroma planes, bottom-field init values, update locking, and debug windows.
- `COL_MAN_*`, `INPUT_CSC_*`, and `PRESCALE_*`: start of the color-manager section for input CSC update locking, input CSC mode/type/conversion controls, A/B matrix coefficient registers, and prescale bias/scale for red and green. The blue prescale and output CSC definitions continue in the next chunk.

Generated names ending in a hardware field called `*_MASK` produce identifiers such as `DMCU_INTERRUPT_TO_HOST_EN_MASK__UC_INTERNAL_INT_MASK_MASK`. This is expected: the first `MASK` is part of the hardware register or field name, and the final `_MASK` is the generated mask suffix.

## Control Flow

This header has no runtime control flow. It contributes compile-time constants to consumers that perform register programming and polling.

Typical runtime usage is:

1. A DCE 11.2 component constructor builds a register table from `dce_11_2_d.h` addresses and this file's mask/shift constants.
2. The component reads a register through DC register helpers or AMDGPU MMIO helpers.
3. The caller clears or extracts a field with the `*_MASK` macro.
4. The caller shifts a new value with the matching `__SHIFT` macro or delegates that to `REG_UPDATE`/`set_reg_field_value`.
5. Hardware latches, reports, clears, or routes the state according to the register semantics.

Concrete consumers in this tree include:

- `display/dc/resource/dce112/dce112_resource.c`, which includes this header and builds DCE 11.2 register/mask tables for timing generators, stream encoders, hardware sequencer, memory inputs, transforms, OPPs, AUX, I2C, and clock sources.
- `display/dc/hwss/dce112/dce112_hwseq.c`, which includes this header for DCE 11.2 hardware sequencer register programming.
- `display/dc/dce112/dce112_compressor.c`, which programs `FBC_*` fields, including `FBC_CNTL`.
- `display/dc/clk_mgr/dce112/dce112_clk_mgr.c`, which uses the same DCE 11.2 register header family for clock-management programming.
- Shared DCE code such as `display/dc/dce/dce_dmcu.c`, `dce_aux.c`, `dce_stream_encoder.c`, `dce_transform.c`, `dce_opp.c`, and `dce110_opp_csc_v.c`, where these fields shape DMCU interrupt routing, AUX transactions, DP secondary packets/MST rates, scaler/line-buffer state, formatter bit depth, and input CSC programming.

The effective sequencing is controlled by hardware side effects. Examples include interrupt `*_CLEAR` bits, AUX transaction start/done/status bits, DMCU mailbox command/byte count fields, `SCL_UPDATE` pending/taken/lock/coef-complete bits, FBC enable and invalidation controls, FIFO error ack bits, CRC result/status fields, and color-manager update locks.

## State And Persistence Behavior

The header itself stores no mutable state and has no persistence. Its constants are compiled into display driver objects.

The registers represented by these fields are hardware state:

- DMCU interrupt status, clear, routing, mailbox, scratch, and clock-gating fields represent state shared between host driver code and the display microcontroller firmware. Status/clear bits are transient and may be write-one-to-clear or otherwise edge-sensitive.
- DP stream encoder, DPHY, secondary packet, MST, and MSA fields persist as link/stream configuration until the encoder is reprogrammed, disabled, reset, power-gated, or restored after suspend/resume.
- AUX fields represent transaction state. `AUX_SW_DONE`, reply byte counts, timeout/invalid-receive bits, HPD-disconnect status, DPHY status, and GTC sync status are transient observations used by AUX/DDC flows.
- FBC fields persist compressed-framebuffer configuration, CSM offsets, client masks, debug CSR indices/data, and compression enable/status until the compressor is disabled or the display/GPU is reset.
- FMT, LB/LBV, SCL/SCLV, viewport, overscan, input CSC, and prescale fields persist as part of the active scanout pipeline and affect displayed pixels until a modeset, plane update, color update, or reset changes them.
- Debug and test-index/data fields can alter what internal state is observed or written through indexed debug windows; those fields should be treated as hardware diagnostics, not general persistent driver state.

## Dependencies And Integration Points

Direct dependencies are the C preprocessor and AMDGPU/DC register helper conventions. The semantic companion is:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dce/dce_11_2_d.h`

Primary include/use sites in this source tree include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dce112/dce112_resource.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dce112/dce112_hwseq.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce112/dce112_compressor.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dce112/dce112_clk_mgr.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/smumgr/vegam_smumgr.c`

The macro families integrate with several shared DCE/DC subsystems:

- DMCU and link encoder code uses interrupt-routing fields to route static-screen, vblank, power-gating, and other display events to firmware.
- AUX code uses `AUX_CONTROL`, `AUX_SW_CONTROL`, `AUX_SW_STATUS`, `AUX_SW_DATA`, and DPHY status fields to run DP AUX/I2C-over-AUX transactions and classify timeout, HPD-disconnect, and invalid-reply failures.
- Stream encoder code uses `DP_SEC_CNTL`, `DP_MSE_RATE_CNTL`, MSA/MST, and DP DPHY fields for infoframes, DP audio packet flow, MST slot/rate programming, link training, and stream enablement.
- Compressor code uses `FBC_*` fields for DCE 11.2 framebuffer compression power-up, enable/disable, LPT support, compressed surface programming, and invalidation triggers.
- Transform/scaler code uses `LB_*`, `SCL_*`, `SCLV_*`, viewport, overscan, and update fields for scaling ratios, coefficient RAM programming, line-buffer format, update locking, and virtual/chroma plane support.
- OPP/color code uses `FMT_*`, `COL_MAN_*`, `INPUT_CSC_*`, and `PRESCALE_*` fields for output bit depth, dithering/truncation, CRC, input color-space conversion, and prescale programming.

## Risks And Edge Cases

The main risk is silent hardware misprogramming. These are untyped numeric constants; the compiler cannot verify that a mask belongs to the register being updated, that the matching shift is used, or that the value fits within the field width.

This assigned range has two chunk-boundary artifacts:

- It starts at `DMCU_INTERRUPT_STATUS__DCPG_IHC_DCFE0_POWER_UP_INT_CLEAR_MASK`; the matching preceding occurrence fields and earlier DMCU interrupt fields are in the previous chunk.
- It ends at `PRESCALE_VALUES_G__PRESCALE_BIAS_G__SHIFT`; the matching green scale field and the blue/output CSC fields continue in the next chunk.

Interrupt fields require careful semantics. Many `*_OCCURRED`, `*_CLEAR`, `*_MASK`, and `*_TO_UC_EN` fields share the same bit position for status and clear behavior. Treating clear bits as ordinary persistent state can lose interrupts, and misrouting DMCU/UC interrupts can break DMCU-assisted power, ABM/backlight, static-screen, vblank, or perfmon workflows.

DP and AUX fields are protocol-visible. Bad link, training, MSA, MST, secondary packet, or audio M/N values can cause blank displays, link-training failures, wrong colorimetry, broken audio, MST allocation errors, or compliance failures. AUX transaction fields are also timing-sensitive; incorrect done/reset/status handling can turn EDID reads and DPCD transactions into intermittent failures.

FBC fields affect memory layout and display fetch/compression behavior. Incorrect compression enable/source selection, CSM offsets, LPT settings, client masks, or invalidation triggers can corrupt scanout, cause stale frames, increase memory traffic, or interact badly with suspend/resume.

SCL/SCLV, LB/LBV, viewport, overscan, FMT, input CSC, and prescale fields directly affect the visible image. Wrong ratios, init values, coefficient RAM selection, update locking, line-buffer pixel format, color matrices, bit-depth controls, or clamp/dither settings can produce scaling artifacts, color shifts, underflow, tearing, or partial updates.

Generated `*_MASK_MASK` names are easy to mishandle in scripts. Pairing checks and documentation tools must separate the hardware field name from the generated suffix to avoid false positives.

## Test Signals

Useful validation signals are a mix of generated-header consistency, build coverage, and hardware behavior:

- Build coverage for AMDGPU configurations that include DCE 11.2 display support, PowerPlay VegaM paths, and shared DCE/DC components that consume generated register tables.
- Header consistency checks that pair every `*_MASK` with its corresponding `__SHIFT`, while accounting for the two chunk-boundary artifacts and hardware fields that naturally end in `_MASK`.
- DCE 11.2 display bring-up on Polaris/VegaM-class hardware, including modeset, page flip, vblank, suspend/resume, hotplug, and GPU reset recovery.
- DP link-training and stream tests covering MSA colorimetry/misc fields, secondary packets, DP audio, MST slot/rate programming, DPHY CRC/debug status, and fast-training paths.
- AUX/DDC tests across all AUX engines, including EDID reads, DPCD reads/writes, HPD disconnect during AUX, timeout handling, reset sequencing, and GTC sync status behavior.
- DMCU-assisted feature tests for static-screen interrupts, vblank routing, display power-gating events, mailbox communication, firmware interrupt masks, perfmon interrupts, and DMCU clock gating.
- FBC enable/disable, compressed-surface address/pitch programming, LPT enable/disable, invalidation trigger, suspend/resume, and visual corruption checks.
- Scaler and line-buffer tests for luma/chroma scaling, interlaced/bottom-field init, coefficient RAM update, viewport/overscan changes, virtual scaler paths, underflow/status, and update-lock sequencing.
- Formatter/color tests for truncation, spatial/temporal dithering, CRC capture, 4:2:0 timing, input CSC matrices, prescale bias/scale, and visible color correctness.

## Chunk Boundary Notes

This report covers only lines 7907-11514. Earlier chunks contain the start of the DMCU interrupt definitions and other DCE 11.2 field families. Later chunks continue the color-manager prescale/output CSC section and the remaining register field definitions. The final per-file report should merge those adjacent reports before drawing file-wide conclusions.

### subset-b-001527: lines 11515-15026

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dce/dce_11_2_sh_mask.h lines 11515-15026

## Scope And Purpose

This chunk is a generated AMD DCE 11.2 register shift/mask header section. It contains only C preprocessor constants of the form `REGISTER__FIELD_MASK` and `REGISTER__FIELD__SHIFT`; there are no functions, structs, enums, storage objects, or executable branches in the mapped range.

The range starts at the tail of `PRESCALE_VALUES_G` and ends after the first macro of `AZALIA_F2_CODEC_INPUT_PIN_CONTROL_MULTICHANNEL7_ENABLE`, so both boundary register groups are partial and need adjacent chunk context for complete per-register documentation. Within those boundaries, the chunk defines bitfield constants for display color management, gamma correction, FIFO error reporting, unpinned graphics plane programming, legacy VGA indexed register compatibility, display pipe arbitration and stutter controls, and a large Azalia/HD Audio controller and codec endpoint block used for HDMI/DisplayPort audio.

## Important APIs, Types, And Macro Families

The public interface is the macro namespace itself. Consumers combine the masks and shifts with register addresses from the sibling DCE 11.2 address header and helper APIs such as `REG_SET_FIELD()`, `REG_GET_FIELD()`, `set_reg_field_value()`, `get_reg_field_value()`, `RREG32()`, `WREG32()`, `dm_read_reg()`, and `dm_write_reg()`.

Important macro families in this chunk include:

- Color management output and denormalization: `PRESCALE_VALUES_G/B`, `COL_MAN_OUTPUT_CSC_CONTROL`, `OUTPUT_CSC_C11_C12_A` through `OUTPUT_CSC_C33_C34_B`, `DENORM_CLAMP_CONTROL`, `DENORM_CLAMP_RANGE_R_CR/G_Y/B_CB`, and `COL_MAN_FP_CONVERTED_FIELD` define prescale bias/scale, output color-space conversion matrix coefficients for A/B banks, clamp mode, per-channel clamp min/max, and converted floating-point field access.
- Gamma correction: `GAMMA_CORR_CONTROL`, `GAMMA_CORR_LUT_INDEX`, `GAMMA_CORR_LUT_DATA`, `GAMMA_CORR_LUT_WRITE_EN_MASK`, and `GAMMA_CORR_CNTLA_*` / `GAMMA_CORR_CNTLB_*` define gamma LUT access and piecewise exponential-region layout for two banks. The region registers pack LUT offsets and segment counts for regions 0 through 15.
- FIFO and input-gamma status: `PACK_FIFO_ERROR` and `OUTPUT_FIFO_ERROR` expose underflow/overflow occurred and acknowledgement fields. `INPUT_GAMMA_LUT_AUTOFILL`, `INPUT_GAMMA_LUT_RW_INDEX`, `INPUT_GAMMA_LUT_SEQ_COLOR`, `INPUT_GAMMA_LUT_PWL_DATA`, `INPUT_GAMMA_LUT_30_COLOR`, `COL_MAN_INPUT_GAMMA_CONTROL1/2`, and `INPUT_GAMMA_BW_OFFSETS_*` define input gamma LUT loading, autofill, mode, exponent/region controls, and black/white offsets.
- Unpinned graphics plane: `UNP_GRPH_ENABLE`, `UNP_GRPH_CONTROL`, `UNP_GRPH_CONTROL_C`, `UNP_GRPH_CONTROL_EXP`, `UNP_GRPH_SWAP_CNTL`, luma/chroma primary and secondary surface address registers, high-address registers, bottom-field addresses, pitch, x/y offsets, start/end coordinates, `UNP_GRPH_UPDATE`, in-use address readbacks, `UNP_DVMM_PTE_CONTROL`, interrupt status/control, stereosync flip, flip control, CRC, line-buffer gap, rotation, debug, and test debug registers describe a graphics/video scanout path with separate luma/chroma programming and synchronized update behavior.
- Legacy VGA register compatibility: `GENMO_*`, `GENENB`, `GENFC_*`, `GENS*`, DAC palette registers, `SEQ*`, `CRT*`, `GRA*`, `ATTR*`, `VGA_RENDER_CONTROL`, `VGA_SOURCE_SELECT`, `VGA_SEQUENCER_RESET_CONTROL`, `VGA_MODE_CONTROL`, `VGA_SURFACE_PITCH_SELECT`, VGA memory/base/dispbuf address fields, `VGA_HDP_CONTROL`, `VGA_CACHE_CONTROL`, `D1VGA_CONTROL` through `D6VGA_CONTROL`, and VGA status, interrupt, clear, main-control, test, debug, and page-address fields map legacy VGA state into modern display hardware.
- DAC and display pipe gateway controls: `BPHYC_DAC_MACRO_CNTL` and `BPHYC_DAC_AUTO_CALIB_CONTROL` define analog DAC macro and calibration fields. `DPG_PIPE_ARBITRATION_CONTROL1/2`, `DPG_WATERMARK_MASK_CONTROL`, `DPG_PIPE_URGENCY_CONTROL`, `DPG_PIPE_DPM_CONTROL`, `DPG_PIPE_STUTTER_CONTROL`, `DPG_PIPE_NB_PSTATE_CHANGE_CONTROL`, `DPG_PIPE_STUTTER_CONTROL_NONLPTCH`, and debug/test registers define display pipe arbitration, watermarks, urgency, DPM, memory stutter, NB p-state changes, and repeater/check preprocessor controls.
- Virtual or per-viewport display pipe gateway controls: `DPGV0_*` and `DPGV1_*` mirror the DPG arbitration, watermark, urgency, DPM, stutter, NB p-state, repeater, hardware debug, and check preprocessor fields for two related DPGV instances.
- Azalia immediate command and codec identity: `AZROOT_IMMEDIATE_COMMAND_OUTPUT_INTERFACE_*`, `AZENDPOINT_IMMEDIATE_COMMAND_OUTPUT_INTERFACE_*`, `AZENDPOINT_IMMEDIATE_COMMAND_INPUT_INTERFACE_*`, and `IMMEDIATE_COMMAND_*` fields define HDA immediate command input/output index/data/status. `AZALIA_F2_CODEC_ROOT_PARAMETER_*`, `AZALIA_F2_CODEC_FUNCTION_*`, `AZALIA_F0_CODEC_ROOT_PARAMETER_*`, and `AZALIA_F0_CODEC_FUNCTION_*` define root/function vendor, revision, subordinate node, group type, supported rates, formats, power states, reset, subsystem ID, and converter synchronization.
- Azalia global controller, DMA, CORB/RIRB, and stream descriptors: `GLOBAL_CAPABILITIES`, version, payload capability, `GLOBAL_CONTROL`, wake/status registers, `INTERRUPT_CONTROL`, `INTERRUPT_STATUS`, `WALL_CLOCK_COUNTER`, `STREAM_SYNCHRONIZATION`, CORB/RIRB base pointers, read/write pointers, control/status/size, DMA position base, and output stream descriptor control/status/format/BDL/LPIB fields describe the HDA controller command/response rings and audio DMA stream machinery.
- Azalia output converter and pin widgets: `AZALIA_F2_CODEC_CONVERTER_*`, `AZALIA_F2_CODEC_PIN_*`, `AZALIA_F0_CODEC_CONVERTER_*`, `AZALIA_F0_CODEC_PIN_*`, audio descriptor registers, sink description registers, channel/speaker allocation, multichannel enable/mute/channel ID, lipsync, HBR, sink info, hot-plug control, unsolicited response force, channel-status override, LPIB snapshots, format-changed state, wireless display identification, remote keepalive, and audio enable/format interrupt status describe HDMI/DP audio presentation and ELD-like sink metadata paths.
- Azalia input converter and input pin widgets: `AZALIA_F0_CODEC_INPUT_CONVERTER_*`, `AZALIA_F0_CODEC_INPUT_PIN_*`, `AZALIA_F2_CODEC_INPUT_CONVERTER_*`, and `AZALIA_F2_CODEC_INPUT_PIN_*` define input converter capabilities, format, channel stream ID, digital converter status, input pin capabilities, unsolicited responses, pin sense, widget controls, multichannel input mapping, HBR, channel allocation, input status, infoframe, LPIB, and timer snapshots. The chunk ends before all fields for `AZALIA_F2_CODEC_INPUT_PIN_CONTROL_MULTICHANNEL7_ENABLE` are present.
- Azalia debug, clock, CRC, and memory power: `AZALIA_CONTROLLER_CLOCK_GATING`, `AZALIA_AUDIO_DTO`, `AZALIA_SCLK_CONTROL`, underflow filler samples, data/BDL/CORB/RIRB DMA controls, cyclic buffer sync, output/input payload capability, stream arbiter control, controller debug, `AZALIA_MEM_PWR_CTRL`, `AZALIA_MEM_PWR_STATUS`, `DCI_PG_DEBUG_CONFIG`, input/output CRC control/result/channel registers, latency counters, stream index/data/debug, and test debug registers provide low-level diagnostics, clocking, DMA control, and power-state observability.

## Control Flow And Data Flow

This header chunk has no runtime control flow. Its data flow is compile-time substitution into register access code. A caller reads or builds a 32-bit MMIO value, inserts a field by masking and shifting, writes it to a DCE 11.2 register address, and later reads status fields with the inverse mask/shift operation.

The implied hardware flows are:

- Color and gamma programming flows write prescale, CSC, denormal clamp, gamma LUT index/data, and gamma region fields as part of display pipe color setup. A/B coefficient and gamma banks suggest double-buffered or alternate-bank programming where software can prepare one bank while another is active, depending on the surrounding display block sequencing.
- FIFO error flows read occurred bits and write acknowledgement bits for pack and output FIFO underflow/overflow handling. These fields are diagnostic and recovery points for display underflow or packing faults.
- UNP graphics flows program format, tiling, stereo, surface addresses, chroma/luma addresses, pitch, offsets, and rectangle coordinates, then use update-lock, pending, flip, stereosync, and interrupt fields to commit scanout changes coherently.
- VGA flows expose legacy indexed VGA registers and modern routing controls. Driver code can select source pipes, enable/disable VGA memory, control sequencer reset, map aperture page addresses, and observe/clear VGA access and interrupt status.
- DPG and DPGV flows set arbitration, urgency watermarks, DPM, stutter, and p-state change controls for display memory access. The legacy Vegam powerplay code reads `DPG_PIPE_STUTTER_CONTROL.STUTTER_ENABLE` when deciding whether an MCLK level can enable stutter mode.
- Azalia/HDA flows configure global controller capabilities and control, command output and response input rings, immediate command transactions, stream descriptor DMA, codec converter/pin capabilities, channel allocation, HBR and multichannel modes, sink metadata, LPIB snapshots, infoframe status, unsolicited responses, clocking, CRC, latency counters, and memory power states.

## State And Persistence Behavior

The header stores no software state. The mutable and persistent state lives in DCE 11.2 MMIO registers, codec widget register files, HDA DMA rings, display pipe shadow/update registers, and hardware status latches.

State classes represented in the chunk include:

- Persistent display programming: output CSC matrices, prescale values, denormal clamp ranges, gamma LUT entries/regions, UNP surface addresses, pitch, offsets, format/tile settings, DPG watermarks, and stutter/DPM controls remain effective until rewritten, reset, or power-gated.
- Shadowed or synchronized update state: `UNP_GRPH_UPDATE`, flip control, stereosync flip, surface-in-use readbacks, and related pending/lock/enable fields participate in safe display updates and expose which programmed address is currently active.
- Latched error and interrupt state: pack/output FIFO error occurred/ack fields, UNP graphics interrupt status/control, VGA status/interrupt/clear registers, HDA interrupt control/status, audio enable/disable/format-changed interrupt status, unsolicited response fields, input activity/status fields, CRC results, and hot-plug controls represent event state that software must acknowledge or clear with the correct semantics.
- DMA and ring state: CORB/RIRB lower and upper base addresses, read/write pointers, sizes, controls, response interrupt count, DMA position buffer base, output stream descriptor BDL/LPIB/CBL/LVI/FIFO/format fields, and cyclic buffer snapshots describe persistent HDA controller state shared between the GPU display/audio block and the host audio driver path.
- Hardware-derived observability: LPIB timer snapshots, wall clock, GTC delta counters, CRC channel/result registers, stream latency counters, memory power status, controller debug, VGA/debug data, DPG/DPGV status, and input infoframe fields are readback and diagnostic state rather than configuration-only data.

Wrong masks or shifts can persist in hardware until a later mode set, audio reconfiguration, suspend/resume, or GPU reset reprograms the affected block. That is especially risky for scanout addresses, color coefficients, watermarks, stutter controls, CORB/RIRB pointers, stream descriptor DMA, and interrupt acknowledgement fields.

## Dependencies And Integration Points

This chunk depends on the rest of the generated DCE 11.2 register headers, especially `dce_11_2_d.h` for register addresses and adjacent portions of `dce_11_2_sh_mask.h` for complete register groups at the chunk boundaries. It also relies on the AMDGPU/DC register helper idiom where field names are expanded into `REGISTER__FIELD_MASK` and `REGISTER__FIELD__SHIFT`.

Observed local include and use points for the DCE 11.2 header family include:

- `drivers/gpu/drm/amd/display/dc/dce112/dce112_compressor.c`, which includes `dce_11_2_sh_mask.h` with DCE and GMC address/mask headers for DCE112 framebuffer compression and display memory interface programming.
- `drivers/gpu/drm/amd/display/dc/hwss/dce112/dce112_hwseq.c`, which includes the header for DCE112 hardware sequencing and register field access.
- `drivers/gpu/drm/amd/display/dc/clk_mgr/dce112/dce112_clk_mgr.c` and `drivers/gpu/drm/amd/display/dc/resource/dce112/dce112_resource.c`, which include the header while constructing DCE112 clock and resource objects.
- `drivers/gpu/drm/amd/pm/powerplay/smumgr/vegam_smumgr.c`, which includes `dce_11_2_sh_mask.h` and reads `DPG_PIPE_STUTTER_CONTROL.STUTTER_ENABLE` through `PHM_READ_FIELD()` when populating memory DPM levels.

Broader integration surfaces are:

- DRM/KMS mode setting and DC resource construction for display pipe color, scanout, update, and interrupt behavior.
- AMDGPU power management and SMU table construction for display watermark, stutter, and memory clock decisions.
- HDMI/DisplayPort audio through the GPU's Azalia/HDA controller, including codec widget capabilities, stream DMA, ELD/sink metadata, channel allocation, HBR, unsolicited responses, and LPIB position reporting.
- Legacy VGA handoff, VGA memory aperture control, and VGA-compatible display routing.
- Hardware bring-up, debugfs-style diagnostics, ASIC validation, and failure triage paths that read CRC, FIFO, latency, memory power, debug, and interrupt fields.

## Risks And Edge Cases

The main risk is numeric drift between this generated header and the authoritative DCE 11.2 register database. The C compiler can catch a missing macro but cannot prove that a mask or shift targets the intended hardware bits.

Specific risks in this chunk are:

- Partial chunk boundaries: line 11515 starts after the first `PRESCALE_VALUES_G` fields, and line 15026 contains only the first `AZALIA_F2_CODEC_INPUT_PIN_CONTROL_MULTICHANNEL7_ENABLE` macro. Full conclusions for those registers require adjacent chunks.
- Repeated A/B, F0/F2, input/output, luma/chroma, DPG/DPGV0/DPGV1, D1-D6, and multichannel0-7 layouts are copy-sensitive. A one-field offset error can silently program the wrong color bank, audio function, pin widget, channel ID, or display pipe.
- Fields named `MASK_MASK`, `INT_MASK`, `STATUS`, `CLEAR`, `ACK`, `ENABLE`, and `FORCE` have different write/read semantics. Confusing status, mask, clear, acknowledgement, and enable fields can drop interrupts, leave sticky status uncleared, or create repeated interrupt delivery.
- UNP surface-address and update fields are scanout critical. Wrong high/low address masks, chroma/luma address fields, pitch, tiling, or update-lock bits can produce corrupted frames, stale flips, page faults, or display underflow.
- DPG stutter, watermark, urgency, and NB p-state fields affect memory bandwidth and power behavior. Bad constants can cause underflow, visible corruption, or overly conservative power-management decisions.
- VGA compatibility fields are globally sensitive because they affect boot console handoff, VGA memory apertures, indexed register access, sequencer reset behavior, and pipe routing.
- Azalia/HDA DMA and command-ring fields are host-interface critical. Incorrect CORB/RIRB/stream descriptor, BDL, LPIB, interrupt, or format fields can break HDMI/DP audio, corrupt command/response flow, misreport playback position, or trigger audio underruns.
- Audio sink and infoframe fields encode externally visible capabilities and channel layout. Wrong masks can advertise invalid channel allocations, HBR capability, speaker allocation, pin configuration, or sink metadata to the audio stack.

## Test Signals

There are no unit tests for this header alone. Useful validation signals are build coverage, generated-header comparison, and hardware integration tests:

- Build AMDGPU/DC configurations that include DCE112 and Vegam powerplay paths. This catches missing or renamed macros and helper expansion failures.
- Compare lines 11515-15026 against the authoritative AMD DCE 11.2 register source or an upstream generated copy, paying special attention to repeated Azalia widget groups, DPG/DPGV mirrors, VGA indexed registers, and the partial boundary registers.
- Exercise DCE112 mode setting with color-management changes: output CSC, denormal clamp, gamma LUT programming, and input gamma modes should produce expected visual output and register readback.
- Exercise plane flips and UNP-style scanout paths where available, including luma/chroma surfaces, pitch/offsets, rotation, CRC, flip interrupts, and surface-in-use readbacks.
- Run display memory pressure, stutter, and MCLK/p-state transition tests while checking DPG watermark, urgency, stutter, and underflow indicators.
- Validate legacy VGA handoff or VGA-compatible paths by checking VGA memory disable/source selection, indexed VGA access, sequencer reset behavior, and VGA status/interrupt clear behavior.
- Exercise HDMI/DisplayPort audio: hotplug, EDID/ELD-like sink metadata, channel allocation, HBR, multichannel mappings, stream start/stop, suspend/resume, LPIB position reporting, CORB/RIRB command response, and interrupt delivery.
- Use CRC, FIFO error, Azalia latency, memory power, debug index/data, and stream debug registers as diagnostic signals during ASIC bring-up or regression testing.

### subset-b-001528: lines 15027-18695

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dce/dce_11_2_sh_mask.h lines 15027-18695

## Scope And Purpose

This chunk is the final generated-style section of the AMD DCE 11.2 register shift/mask header. It contains C preprocessor constants only: each hardware register field is exposed as a `REGISTER__FIELD_MASK` constant and a matching `REGISTER__FIELD__SHIFT` constant. There are no functions, structs, enums, storage definitions, or executable branches in this range.

The range starts at the shift for `AZALIA_F2_CODEC_INPUT_PIN_CONTROL_MULTICHANNEL7_ENABLE__MULTICHANNEL7_ENABLE`; its matching mask is immediately before the assigned range. It then covers the tail of Azalia HDMI/DP audio input-pin status, display blender and writeback/capture blocks, DCFE/DCFEV power and flush control, HPD and display interrupt status, DCO clock/power/reset control, display I2C/DDC engines, video blender and CRTCV timing/CRC, XDMA scanout transport, display PHY lane/PLL controls, PPLL controls, DPCSTX transmitter controls, and the closing `#endif` for `DCE_11_2_SH_MASK_H`.

The purpose is to let DCE 11.2 display, power, and firmware-facing code compose or extract fields in MMIO registers using symbolic masks instead of hard-coded bit positions. These macros are normally paired with register address definitions from `dce_11_2_d.h`, enumerated legal values from `dce_11_2_enum.h`, and AMDGPU/DC register helpers such as `REG_SET_FIELD`, `REG_UPDATE`, `REG_GET`, `set_reg_field_value`, `RREG32`, and `WREG32`.

## Important APIs, Types, And Macro Families

The public API surface is the macro namespace itself. Important families in this assigned range are:

- `AZALIA_F2_CODEC_INPUT_PIN_CONTROL_*`: final input-pin audio controls for multichannel channel 7, channel allocation, input activity/layout, unsolicited response enables, infoframe validity and payload bits, IEC/channel-status low/high words, LPIB snapshot locking, and LPIB/timer snapshots. These support HDMI/DP audio status and stream-position reporting.
- `BLND_*` and `BLNDV_*`: main and video blender controls for global gain/alpha, stereo mode/polarity, feedthrough, multiplied alpha, PTI/new-pixel modes, update pending/taken/lock bits, underflow interrupt occurred/ack/mask/pipe index, vertical update locks across DCP/CUR/SCL/BLND blocks, update-pending status, and indexed debug access.
- `WB_*` and `CNV_*`: writeback enable, clock-gating and memory-power controls, writeback soft reset and warm-up mode, capture/conversion mode, crop window, source size, capture update locks, CSC matrix coefficients, round offsets, clamps, CRC test controls/results, input pipe/source selection, and debug data.
- `DCFE_*` and `DCFEV_*`: display front-end clock gating, soft-reset, debug selection, memory power-control/status, flush controls, DMIFV clock/memory/debug controls, and miscellaneous state for normal and video front-end paths.
- `DC_HPD_*`: hotplug interrupt status/control, HPD signal control, fast-training controls, and toggle filter timing.
- `DISP_INTERRUPT_STATUS*`: base and continuation status registers covering a large display interrupt fan-in. The continuation registers encode line/vblank, page-flip, underflow, AUX/I2C, DMCU, DCO, DCFE, WB, HPD-like, and other display-block interrupt occurred bits across multiple pipes and subblocks.
- `DCO_*`, `FMT_MEMORY*_CONTROL`, `DPDBG_*`, `DCE_VCE_CONTROL`, and `DIG_SOFT_RESET*`: display controller output memory power/status, clock control, power management, soft reset, stereosync, HDMI RX status timing, PSP/generic interrupt handshakes, formatter memory controls, DisplayPort debug, and DIG reset controls.
- `DC_I2C_*` and `GENERIC_I2C_*`: DDC and generic I2C engine control, arbitration, interrupt control, software status, per-DDC hardware status/speed/setup for DDC1-6 and VGA DDC, transaction descriptors, data ports, EDID detect, read-request interrupt state, pin selection, and pin debug.
- `CRTCV_*`: video timing generator fields for horizontal/vertical totals, blanking, sync, enable/control flags, start-line behavior, overscan/black colors, CRC control/window/result registers, and indexed test debug.
- `XDMA_*`: XDMA display-transport and peer/cross-adapter scanout controls, including PCIe/memory client config, local tiling, interrupts, clock/memory power, interface status, power gating, master/slave control/status, local and remote surface addresses, pitch/dimensions, urgent controls, NACK status, GSL/vsync checks, pipe controls, read commands, cache config, performance measurement, read/write latency, flip pending, channel controls, and debug windows.
- PHY lane controls: `CMD_BUS_TX_CONTROL_LANE*`, `MARGIN_DEEMPH_LANE*`, `CMD_BUS_GLOBAL_FOR_TX_LANE*`, `TX_DISP_RFU*_LANE*`, `COMMON_*`, and `COMP_EN_CTL` describe per-lane command bus enable/reset/calibration, transmit pre/de-emphasis margins, reserved lane words, common lane power management/resets, common transmitter control, TMDP/zcal, and impedance/compensation calibration.
- Display PLL controls: `FREQ_CTRL*`, `BW_CTRL_*`, `CAL_CTRL`, `LOOP_CTRL`, `VREG_CFG`, `OBSERVE*`, `DFT_OUT`, `PLL_WRAP_CNTRL*`, and the `PPLL_*` mirrors describe fractional/integer frequency control words, denominators, reference/VCO/pre/post dividers, spread-spectrum enable, bandwidth coefficients, calibration controls, loop behavior, regulator settings, observation/debug muxes, update locking/pending/ready flags, reference clock routing, clock-out selectors, DFT/analog spares, and status/debug readback.
- `DPCSTX_*`: DisplayPort/clocked serial transmitter reset, symbol clock gating/enables, lane FIFO and link-mode controls, TX PLL update request/pending, CBUS delays/reset, register/TX FIFO error status and clear/mask fields, indexed PLL update/data windows, indexed register/data windows, debug muxing, and test debug data.

Generated field names ending in `MASK` produce identifiers such as `DPCSTX_REG_ERROR_STATUS__DPCS_REG_FIFO_ERROR_MASK_MASK`; the doubled suffix is intentional and means "mask for the hardware field named `..._MASK`."

## Control Flow And Data Flow

This header has no runtime control flow. Its data flow is compile-time macro expansion into register access code. A typical consumer selects an MMIO address from `dce_11_2_d.h`, combines it with an instance offset where needed, clears a field using `*_MASK`, inserts or extracts a value with `__SHIFT`, and reads or writes the register through DC/AMDGPU helpers.

The implied hardware flows are:

- Audio status code reads or writes Azalia input-pin fields to represent channel allocation, layout/activity, infoframe validity, channel status words, and LPIB snapshots.
- Blender/writeback/capture paths program update locks, alpha/stereo/crop/CSC/clamp fields, then observe update pending/taken, underflow, and CRC/debug fields.
- DCFE/DCFEV and DCO sequencing code gates clocks, asserts/deasserts soft reset, manages memory power state, flushes front-end FIFOs, and checks status fields.
- HPD, display interrupt, DCO PSP/generic, I2C, and read-request interrupt fields feed interrupt handlers or polling loops that must distinguish status, mask, clear, ack, and routing semantics.
- I2C/DDC consumers configure bus speed/setup/transaction/data registers, arbitrate ownership, then poll status or interrupt bits for DONE/NACK/timeout/error conditions.
- CRTCV timing and CRC fields are programmed as part of video timing, test-pattern, validation, and display CRC capture sequences.
- XDMA master/slave fields configure local and remote surfaces, dimensions, urgent thresholds, channel start, and cache/client behavior for display data movement, then expose NACK, latency, flip, and performance status.
- PHY, PLL, and DPCSTX fields are part of low-level link bring-up: lane reset/power/calibration, clock divider/frequency programming, PLL update handshakes, symbol-clock enabling, FIFO start, and debug/error reporting.

## State And Persistence Behavior

The header stores no mutable state. Persistent state lives in DCE 11.2 hardware registers and in firmware-visible or driver-visible state machines that those registers control.

State represented by this chunk includes:

- Durable configuration until reprogram/reset: blender alpha/stereo behavior, writeback/capture crop and CSC, DCFE/DCO clock and memory-power controls, HPD filters, I2C speed/setup, CRTCV timing/CRC window configuration, XDMA surfaces and urgent thresholds, PHY lane settings, PLL dividers/calibration settings, and DPCSTX transmitter modes.
- Shadowed or synchronized update state: `BLND_UPDATE`, `BLNDV_UPDATE`, `CNV_UPDATE`, vertical update locks, register-update status bits, TX PLL update pending/request, and PPLL update lock/point/pending/ready fields. These are intended to make multi-register display changes visible at controlled hardware update points.
- Latched or transient status: audio input activity and LPIB snapshots, underflow occurred bits, display interrupt continuation bits, HPD status, DCO PSP/generic interrupt status, I2C software/hardware status, read-request interrupts, CRTCV CRC results, XDMA NACK/latency/flip/performance status, PHY/DPCSTX FIFO error status, PLL lock/ready/status, and compensation calibration done.
- Diagnostic and validation state: indexed debug registers across BLND, CNV, DCO, XDMA, CRTCV, DPCSTX, DFT/observe outputs, FMT memory controls, DP debug interrupts, and PHY reserved/RFU words.

Wrong constants can persist in active hardware until a modeset, reset, suspend/resume restore, or explicit reprogramming path fixes them. PLL, PHY, DPCSTX, and XDMA mistakes can blank a link or corrupt scanout. Interrupt mask/clear mistakes can drop events or cause repeated interrupts. Update-lock mistakes can leave stale or partially-applied display state.

## Dependencies And Integration Points

Direct companion headers are:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dce/dce_11_2_d.h`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dce/dce_11_2_enum.h`

Direct include sites in this repository include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dce112/dce112_resource.c`, which builds DCE 11.2 register, shift, and mask tables such as `MI_DCE11_2_MASK_SH_LIST(__SHIFT)` and `MI_DCE11_2_MASK_SH_LIST(_MASK)`.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce112/dce112_compressor.c`, which pairs DCE 11.2 display addresses/masks with GMC 8.1 masks for framebuffer compression and tiling-related programming.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dce112/dce112_hwseq.c`, which uses DCE 11.2 register tables for hardware sequencing.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dce112/dce112_clk_mgr.c`, which constructs clock-manager register/mask/shift tables and programs display clocks through BIOS/DMCU flows.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/smumgr/vegam_smumgr.c`, which includes DCE 11.2 headers alongside SMU/GMC/BIF/GFX headers for Vegam power-management and firmware control paths.

Functional integration surfaces include DRM/DC modeset and pipe programming, display clock and power gating, HPD and display interrupt handling, HDMI/DP audio status, DDC/EDID I2C transactions, video timing/CRC validation, writeback/capture, cross-adapter/XDMA scanout, display PHY and PLL programming, DisplayPort transmitter control, firmware and SMU coordination, and hardware bring-up diagnostics.

## Risks And Edge Cases

The primary risk is silent hardware misprogramming. These are untyped constants, so the compiler cannot prove that a mask belongs to the register being accessed, that a matching shift is used, or that a value fits within the field width.

Specific risks in this chunk:

- The first register group is partial: line 15027 includes `MULTICHANNEL7_ENABLE__SHIFT`, but the matching `MULTICHANNEL7_ENABLE_MASK` is in the previous chunk.
- The assigned range includes the final `#endif`; file-level reconciliation should treat it as the header guard close, not a register definition.
- There are many repeated pipe/lane/register families: `DISP_INTERRUPT_STATUS_CONTINUE*`, DDC1-6, lane0-3 PHY controls, TX RFU words, `FMT_MEMORY0-5`, `DCO_SCRATCH0-7`, BLND versus BLNDV, and normal DCFE versus DCFEV. Copy/paste or generated-table drift can affect only one instance and be hard to spot.
- Status/mask/ack/clear naming is dense. Fields with `*_MASK_MASK`, `*_INT_MASK`, `*_CLEAR`, `*_ACK`, `*_OCCURRED`, `*_PENDING`, and `*_TAKEN` have different semantics; treating a clear or ack bit as ordinary configuration can lose events.
- Update-lock fields must align with hardware timing. Bad BLND/CNV/PPLL/DPCSTX update masks can cause partially-applied display state, PLL update stalls, or link bring-up failures.
- PLL/PHY/DPCSTX fields are ASIC- and board-sensitive. Incorrect dividers, calibration bits, lane resets, CBUS delays, FIFO start timing, or symbol-clock gates can produce unstable links, no display output, or hard-to-debug compliance failures.
- I2C/DDC fields are protocol-visible. Bad transaction lengths, speed/setup, arbitration, or status interpretation can break EDID reads, AUX/I2C-over-DDC-like access, or hotplug handling.
- XDMA fields bridge display, memory, and PCIe-like paths. Wrong remote/local addresses, pitch/dimension, urgent thresholds, NACK handling, or channel start bits can corrupt scanout, hang a data path, or produce cross-GPU display failures.
- Reserved/RFU lane and common display fields are addressable but not self-documenting. They should be treated as generated hardware documentation, not as safe-to-write policy.

## Test Signals

There are no meaningful unit tests for this header alone. Useful validation comes from generated-header checks, build coverage, and hardware integration:

- Build configurations that include DCE 11.2 DC, DCE112 resource/hwseq/compressor/clock-manager code, Vegam SMU paths, and register-helper macros.
- Run a generated-header consistency check pairing each `REGISTER__FIELD_MASK` with `REGISTER__FIELD__SHIFT`, allowing the known chunk-boundary partial `AZALIA_F2_CODEC_INPUT_PIN_CONTROL_MULTICHANNEL7_ENABLE` field and ignoring the final header guard.
- Cross-check register names in this range against `dce_11_2_d.h` and legal encodings in `dce_11_2_enum.h`.
- Exercise DCE 11.2 modesets, multi-pipe display, page flips, writeback/capture, video-plane paths, suspend/resume, and power-gating transitions while monitoring DCFE/DCO/BLND/CNV update and underflow status.
- Validate HPD, DDC/EDID, generic I2C, display interrupt, and read-request interrupt behavior with connect/disconnect, NACK, timeout, and interrupt-clear scenarios.
- Validate HDMI/DP audio channel allocation, channel-status, infoframe validity, HBR/multichannel behavior, and LPIB snapshot reporting where the hardware exposes the Azalia input-pin path.
- Use display CRC and CRTCV CRC windows to detect timing, capture, blending, and color-conversion mistakes.
- Test XDMA master/slave paths where available with local and remote scanout, latency/perf counters, NACK injection or observation, flip-pending behavior, and urgent threshold stress.
- Validate PHY/PLL/DPCSTX programming through DP/HDMI link bring-up, link training, hotplug, suspend/resume, symbol-clock gating, FIFO error counters, PLL ready/update pending readback, and compliance/debug patterns.
