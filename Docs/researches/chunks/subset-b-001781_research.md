# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_3_sh_mask.h lines 1-2407

## Purpose

This chunk is the opening slice of a generated AMD DCN 3.0.3 shift/mask register header. It contains no executable C logic; it publishes preprocessor constants that describe bit positions and bit masks for hardware fields in DCN display-controller MMIO registers. Consumers combine these `__SHIFT` and `_MASK` macros with the matching DCN 3.0.3 offset header and AMDGPU register access helpers to read, write, and update individual fields without hard-coding bit arithmetic at call sites.

The requested range covers lines 1-2407 of a 35,366-line file and contains 2,175 `#define` lines. It starts with the MIT license, AMD copyright, include guard, and then generated field definitions for early DCN 3.0.3 blocks: legacy VGA/MMHUBBUB decode, DCCG display clock generation, DFS/Dentist display-clock dividers, two DC perfmon blocks, DMU miscellaneous control, and the beginning of DMCU microcontroller control/interrupt plumbing. The slice ends inside `DMCU_INTERRUPT_TO_UC_XIRQ_IRQ_SEL_CONT2`, so later chunks are required for the rest of DMCU and subsequent DCN blocks.

Although the repository path is under a local `ceph-client` source mirror, this file is AMDGPU display hardware metadata, not Ceph or distributed filesystem logic.

## Important APIs, Types, And Macros

There are no functions, structs, enums, global variables, includes, locks, or allocator paths in this range. The public interface is the generated macro namespace:

- `<REGISTER>__<FIELD>__SHIFT`: bit index used to shift a field value into or out of the register.
- `<REGISTER>__<FIELD>_MASK`: bit mask for preserving, clearing, or extracting a field.
- `// addressBlock: ...`: generated grouping metadata from AMD's register database; it is useful for humans and generation tooling but is not compiled.

Major macro groups visible in this chunk:

- VGA/MMHUBBUB legacy decode: `VGA_MEM_WRITE_PAGE_ADDR`, `VGA_MEM_READ_PAGE_ADDR`, `VGA_RENDER_CONTROL`, `VGA_SEQUENCER_RESET_CONTROL`, `VGA_MODE_CONTROL`, VGA memory base/surface-address fields, `VGA_HDP_CONTROL`, `VGA_CACHE_CONTROL`, `D1VGA_CONTROL` through `D6VGA_CONTROL`, VGA status/interrupt/status-clear fields, legacy CRTC/attribute/sequencer/DAC/graphics index-data fields, and `VGA_SOURCE_SELECT`.
- DCCG clock generation: PHY PLL pixel-clock resync fields for PHY A/B, `DP_DTO_DBUF_EN`, DP/refclk clock-gating turn-on/off delays, `REFCLK_CNTL`, display/DS/GTC DTO phase and modulo fields, `DCE_VERSION`, `MILLISECOND_TIME_BASE_DIV`, `MICROSECOND_TIME_BASE_DIV`, `DISPCLK_FREQ_CHANGE_CNTL`, `DC_MEM_GLOBAL_PWR_REQ_CNTL`, and `DCCG_DISP_CNTL_REG`.
- DCCG gating and soft reset: `DCCG_GATE_DISABLE_CNTL`, `DCCG_GATE_DISABLE_CNTL2`, `FORCE_SYMCLK_DISABLE`, `SYMCLK_CGTT_BLK_CTRL_REG`, `SYMCLKA_CLOCK_ENABLE`, `SYMCLKB_CLOCK_ENABLE`, `PHYASYMCLK_CLOCK_CNTL`, `PHYBSYMCLK_CLOCK_CNTL`, and `DCCG_SOFT_RESET`.
- Pixel, DPP, DSC, audio, and VSYNC timing: `OTG0_PIXEL_RATE_CNTL`, `OTG1_PIXEL_RATE_CNTL`, `DP_DTO0/1_PHASE`, `DP_DTO0/1_MODULO`, `OTG0/1_PHYPLL_PIXEL_RATE_CNTL`, `DPPCLK0/1_DTO_PARAM`, `DSCCLK_DTO_CTRL`, `DPPCLK_DTO_CTRL`, `DCCG_AUDIO_DTO_SOURCE`, `DCCG_AUDIO_DTO0/1_PHASE`, `DCCG_AUDIO_DTO0/1_MODULE`, `DCCG_VSYNC_OTG0` through `DCCG_VSYNC_OTG5` latch values, `DCCG_VSYNC_CNT_CTRL`, and `DCCG_VSYNC_CNT_INT_CTRL`.
- DFS/Dentist divider: `DENTIST_DISPCLK_CNTL` fields for display and DPP clock divider programming, change toggles, done toggles, and change-done status.
- DC perfmon 0 and 1: repeated `DC_PERFMON0_*` and `DC_PERFMON1_*` fields for counter event selection, counted-value selection, increment mode, hardware stop/control selectors, active state, perfmon state, run-enable start/stop selection, interrupt status/ack, counter high/low values, and read selectors.
- DMU miscellaneous: `CC_DC_PIPE_DIS`, `DMU_CLK_CNTL`, `DMU_MEM_PWR_CNTL`, `DMCU_SMU_INTERRUPT_CNTL`, `SMU_INTERRUPT_CONTROL`, and `DMU_MISC_ALLOW_DS_FORCE`.
- DMCU control and firmware/RAM access: `DMCU_CTRL`, `DMCU_STATUS`, firmware start/end/ISR/checksum fields, `DMCU_RAM_ACCESS_CTRL`, ERAM/IRAM read/write address/data fields, `DMCU_EVENT_TRIGGER`, `DMCU_UC_INTERNAL_INT_STATUS`, `DC_DMCU_SCRATCH`, firmware checksum sample-byte selection, and microcontroller clock-gating delays.
- DMCU interrupt routing and communication: static-screen, ABM, MCP/SCP, vblank, OTG range timing, generic, VSYNC-counter, DPCS TX, perfmon, and DPRX/AUX interrupt status/clear fields; host/UC enable masks; UC IRQ/XIRQ selection fields; ABM interrupt counters; and master/slave communication command/data/control byte fields.

## Control Flow

This header has no runtime control flow. It contributes compile-time constants to the AMDGPU/DCN register access path:

1. DCN 3.0.3 display code includes this shift/mask header with the matching offset header for the same ASIC revision.
2. Block-specific register tables and macros bind symbolic register names to offsets plus field descriptors.
3. Runtime display code uses helpers such as read-modify-write field macros, `RREG32`, `WREG32`, and SOC15/DC register wrappers to update individual bitfields.
4. Hardware side effects occur only when those consumers write MMIO registers; this header only defines the field layout that makes those writes target the intended bits.

The macros do not encode sequencing. Clock changes, DTO programming, soft resets, firmware RAM access, mailbox handshakes, interrupt clear/ack, perfmon start/stop, static-screen handling, and DPRX/AUX event routing must still be ordered by the driver code that uses these constants.

## State And Persistence Behavior

The file itself stores no software state and persists no data. It describes hardware state that lives in DCN MMIO registers:

- VGA state controls legacy aperture paging, render behavior, cache mode, VGA source selection, per-pipe VGA enablement, status, and interrupts.
- DCCG state controls pixel clock source selection, DP DTO enablement, DPP/DSC/audio DTO phase and modulo values, display/ref/symbol clock gating, soft resets, display clock frequency-ramp state, VSYNC counting, and latch interrupt state.
- DFS/Dentist state stores display and DPP clock divider requests plus toggle/done status used to synchronize frequency changes.
- Perfmon state stores event selection, counter activity, interrupt enables/status/ack, counted values, and high/low counter reads for two display performance-monitor blocks.
- DMU/DMCU state controls pipe disablement, DMCUB enablement, DMU clock and memory power behavior, microcontroller reset/enable/wait/stop status, firmware address/checksum fields, host-visible ERAM/IRAM access, scratch registers, and master/slave command channels.
- DMCU interrupt state includes many write-one-to-clear style status/clear aliases where the same bit position is exposed as both `*_OCCURRED` and `*_CLEAR`. It also controls whether events route to host, UC, IRQ, or XIRQ paths.
- DPRX/AUX fields expose receiver/link/AUX/I2C/message timeout and error events to the DMCU interrupt fabric.

Persistence is hardware-defined. Register contents usually survive until a modeset, power transition, suspend/resume, GPU reset, firmware reset, or explicit driver write changes them. This header does not preserve reserved bits by itself; consumers must use the masks with read-modify-write helpers where unrelated bits or write-one-to-clear fields are present.

## Dependencies And Integration Points

This chunk depends on AMD's generated DCN 3.0.3 register database and must remain synchronized with:

- The matching `dcn_3_0_3_offset.h` register offsets and base-index constants.
- AMDGPU display register helper macros that token-paste register and field names into `__SHIFT` and `_MASK` symbols.
- DCCG resource code that programs pixel rates, DTOs, clock gating, clock frequency changes, soft resets, GTC/VSYNC counters, audio DTOs, and symbol clocks.
- DMU/DMCU and firmware-facing code that resets/enables the microcontroller, writes firmware/RAM access windows, exchanges master/slave command data, routes interrupts, and handles scratch or checksum registers.
- Display interrupt handling paths for VGA, DMCU, perfmon, vblank, static-screen, ABM, DPRX/AUX, VSYNC-counter, and timing-update events.
- Diagnostics and validation paths using perfmon counters, latch values, interrupt status, and error counters to verify display behavior.

The integration style is purely symbolic and preprocessor-driven. A wrong field shift, wrong mask, missing macro, or mismatch with the offset header can either fail compilation in register-table code or, more dangerously, compile cleanly while causing read-modify-write operations to alter the wrong hardware bits.

## Risks And Edge Cases

- Generated-header drift is the primary risk. These constants are untyped integer macros, so stale or cross-ASIC values can corrupt unrelated hardware fields without type-system help.
- Shift/mask mismatches are especially risky in read-modify-write helpers because a correct register offset with an incorrect mask can preserve the wrong bits, clear reserved bits, or write a value into the wrong field.
- Interrupt registers contain paired `*_OCCURRED` and `*_CLEAR` names on the same bit positions. Treating clear bits as normal status bits, or writing a full register value instead of a masked write-one-to-clear operation, can lose interrupts.
- DCCG clock, DTO, gating, and soft-reset fields are timing-sensitive. Incorrect field values can cause blank displays, pixel-rate errors, underflow, clock-domain hangs, audio drift, or low-power transition failures.
- DFS/Dentist divider toggles and done bits require correct sequencing. Wrong masks can leave display or DPP clock changes apparently stuck or race the driver into using an unfinished frequency transition.
- DMCU firmware/RAM access fields are stateful and sequencing-sensitive. Misprogramming reset/enable bits, RAM auto-increment, firmware start/end/checksum fields, or command channels can break firmware boot, command delivery, or resume.
- DMCU interrupt routing spans host, UC, IRQ, and XIRQ masks. Off-by-one routing in vblank, static-screen, ABM, perfmon, DPRX, or AUX events can produce missing wakeups, interrupt storms, or firmware waits that only reproduce under specific display topologies.
- Instance-patterned fields such as OTG0/1, DPP0-7, HUBP0-7, DSC0-5, WB0-2, PHY A-G, and vblank1-6 are vulnerable to copy/paste or generation mistakes that affect only multi-display, writeback, DSC, or specific-link configurations.
- The chunk boundary is artificial and stops mid-`DMCU_INTERRUPT_TO_UC_XIRQ_IRQ_SEL_CONT2`; the final per-file report must merge later chunks before making complete claims about DMCU coverage.

## Test Signals

Useful validation signals for this chunk are generated-header consistency plus hardware-facing behavior:

- Build AMDGPU/DC with DCN 3.0.3 support enabled; missing or renamed field macros should fail in register-table initializers or field-update macros.
- Mechanically compare this header against AMD's authoritative DCN 3.0.3 register database and the matching offset header to confirm register/field names, shifts, and masks align.
- Check that paired fields have coherent masks and shifts, especially repeated instance families and write-one-to-clear interrupt aliases.
- Exercise display modesets, pixel-clock changes, DP link bring-up, audio DTO programming, vblank handling, static-screen/ABM events, suspend/resume, and low-power transitions while watching for blank display, underflow, clock-change timeout, or firmware timeout logs.
- Validate perfmon programming for DC perfmon 0/1 and DMCU-routed perfmon interrupts, including interrupt status and ack behavior.
- Test DMCU communication and firmware-facing paths that use master/slave command registers, scratch registers, firmware checksum fields, ERAM/IRAM access, and interrupt routing.
- Exercise DPRX/AUX/I2C and link-error event paths where available, because the tail of this chunk defines the DMCU masks and XIRQ/IRQ selectors for those events.

## Cross-Chunk Notes

This chunk starts at line 1, so no earlier chunk context is needed for the include guard or initial register groups. Later chunks continue the DMCU interrupt selector family and cover the rest of the generated DCN 3.0.3 shift/mask namespace. The final merged per-file research document should treat this report as the early-register-block summary and combine it with later chunk reports before drawing whole-file conclusions.
