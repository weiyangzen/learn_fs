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
