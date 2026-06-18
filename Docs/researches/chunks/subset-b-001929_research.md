# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_2_0_sh_mask.h lines 1-2373

## Purpose

This chunk is the opening portion of AMD DCN 3.2.0 generated register bitfield metadata. It defines preprocessor constants for register field shifts and masks, using the pattern `REGISTER__FIELD__SHIFT` and `REGISTER__FIELD_MASK`. The values are not executable logic; they are compile-time inputs to the AMD display driver's register access macros so C code can read, write, and update individual hardware fields without hand-coded bit positions.

The covered range spans the header guard, the MIT-style AMD copyright block, all of the initial DCCG display clock generator fields, and the beginning of the DMU/RBBMIF display interrupt routing fields. The source file itself is much larger than this chunk; line 2373 stops in the middle of the `OTG2_INTERRUPT_DEST` group after the first mask definition, so later chunks must reconcile the remainder of that register and subsequent address blocks.

## Major Register Areas

The first address block is `dcn_dc_dccg_dccg_dfs_dispdec`, containing `DENTIST_DISPCLK_CNTL`. It defines divider, change-mode, change-toggle, done-toggle, and completion bits for display clock and DPP clock changes. Driver code that programs clock changes depends on these masks matching the silicon layout because mis-shifted divider values can produce invalid clock ratios or incorrect completion polling.

Most of lines 50-999 are `dcn_dc_dccg_dccg_dispdec`, the DCCG block. It covers:

- PHY PLL pixel clock resync controls for PHY A through E: resync enable, deep-color DTO status/control, and pixel clock enable.
- DP, DTBCLK, DPPCLK, DSCCLK, HDMI stream clock, symbol clock, and pixel-rate DTO controls: phase, modulo, enable, double-buffer enable, and source selection fields.
- Clock gating and clock-turn-on/off controls: `DCCG_GATE_DISABLE_CNTL*`, `*_CGTT_BLK_CTRL_REG`, `FORCE_SYMCLK_DISABLE`, `DCCG_GLOBAL_FGCG_REP_CNTL`, and per-symbol-clock force-enable fields.
- Timing bases and counters: microsecond/millisecond time-base dividers, GTC DTO/current registers, DCCG DS DTO and calibration fields, VSync latch values for OTG0-OTG5, and VSync counter interrupt controls.
- Display pixel-rate programming: `OTG0_PIXEL_RATE_CNTL` through `OTG3_PIXEL_RATE_CNTL`, paired DP DTO phase/modulo registers, PHYPLL pixel-rate source fields, and pixel add/drop/error status bits.
- Audio clock DTO programming: `DCCG_AUDIO_DTO_SOURCE`, audio DTO0/1 phase/module, and audio DTBCLK DTO phase/modulo.
- Reset and diagnostics: `DCCG_SOFT_RESET`, `DCCG_CAC_STATUS*`, `DCCG_TEST_CLK_SEL`, `DCE_VERSION`, `DC_MEM_GLOBAL_PWR_REQ_CNTL`, and `DMCUBCLK_CNTL`.

Starting at line 1002, the chunk enters `dcn_dc_dmu_rbbmif_dispdec`. It defines RBBMIF timeout controls/status (`RBBMIF_TIMEOUT`, `RBBMIF_STATUS`, `RBBMIF_STATUS_2`, `RBBMIF_INT_STATUS`, `RBBMIF_TIMEOUT_DIS`, `RBBMIF_TIMEOUT_DIS_2`, and `RBBMIF_STATUS_FLAG`), GPU timer read/start-position fields, a long chain of display interrupt status continuation registers, and the initial interrupt destination routing registers.

The interrupt chain in this chunk maps hardware events for OPTC underflow, OTG timing events, DIG fast training/video-stream-disable, HPD/RX/AUX/I2C, RBBMIF timeout, MCIF/writeback overflow, AUX GTC sync lock/error, DCCG VSync latch, MPCC stall, HUBBUB faults, DCPG power up/down, HUBP vblank/vline/timeout/flip/flip-away, DCIO DPCS errors, Azalia audio endpoint state changes, OTG V-update/V-startup/V-ready/GSL/DRR events, DSC underflow/core errors, DMCUB mailbox/timer/general-data/fault events, DPIA, DMCUB whitelist violation, and MMHUBBUB warmup. The destination registers then route selected interrupt sources to interrupt handlers for DCCG, DMU, DCPG, MMHUBBUB, writeback, DCHUB, MPC, OPTC, and OTG0-OTG2.

## APIs, Types, and Functions

This chunk does not define functions, structs, enums, or exported symbols. Its "API" is its macro namespace. Consumers include generated AMD display register structures and access helpers that conventionally pair register address headers with `_sh_mask` headers. The important contract is:

- Each `__SHIFT` macro gives the least-significant bit position for a field.
- Each `_MASK` macro gives the full bit mask in register position.
- Fields with full-register masks such as `0xFFFFFFFFL` are used for direct whole-register DTO phase, modulo, counter, status, or address fields.
- Repeated register families encode hardware instance number in the macro name, such as `OTG0_*` through `OTG3_*`, `DPPCLK0_*` through `DPPCLK3_*`, `DCCG_VSYNC_OTG0_*` through `OTG5`, `HUBP0` through `HUBP7`, and `DOMAIN0` through `DOMAIN21` where present.

The macros are typically consumed by register programming helpers that build values with `field_value << SHIFT`, mask with `_MASK`, and preserve unrelated bits through read-modify-write. Interrupt handling paths use these masks to decode status registers and to configure interrupt routing/destination registers.

## Control Flow and State

There is no runtime control flow inside this header. Runtime behavior emerges when the display driver includes these constants and performs MMIO register accesses. The control-flow-sensitive areas are:

- Clock programming sequences: DENTIST/DCCG DTO fields are written, enable bits are toggled, and status/done bits are polled by driver code.
- Interrupt dispatch: `DISP_INTERRUPT_STATUS` through `DISP_INTERRUPT_STATUS_CONTINUE25` form a continuation chain using the high `*_CONTINUE*` bit at bit 31. Interrupt service code can inspect the base status and follow continuation status registers when the continuation bit is set.
- Timeout/error handling: RBBMIF status and interrupt fields expose timeout address, operation, read/write status, ack, mask, invalid access type/address, FIFO state, and client timeout disable/status bits.
- Event routing: `*_INTERRUPT_DEST` groups determine whether events route to the display interrupt handler path expected by the driver or firmware integration.

The state represented by this chunk is hardware state, not kernel-owned persistence. Writes persist in memory-mapped device registers until changed by the driver, firmware, reset, power-gating transition, or hardware side effects. Status fields may be latched, sticky, write-one-to-clear, read-only, or directly writable depending on the underlying register semantics; this header only records bit positions and masks, not access policy.

## Dependencies and Integration Points

This file depends only on the C preprocessor and include guard `_dcn_3_2_0_SH_MASK_HEADER`. It is tightly coupled to the matching DCN 3.2.0 register address header and to display driver macros in AMDGPU DC that expect the generated naming convention. Integration points include:

- DCCG clock management for DISPCLK, DPPCLK, DPREFCLK, DTBCLK, DSCCLK, HDMISTREAMCLK, HDMICHARCLK, symbol clocks, PHY PLL pixel clocks, GTC, and audio DTOs.
- OTG timing and pixel-rate programming for pipes/streams, including DTO selection, add/drop pixel correction, and FIFO error reporting.
- DMU/DMCUB integration through DMCUB clock and interrupt destination/status bits.
- RBBMIF timeout detection and masking for display microcontroller/register bus access.
- Linux DRM interrupt handling through display interrupt status, continuation, and destination registers.
- Power and memory-management hooks through DCPG domain power interrupts, DC memory global power request control, HUBBUB/HUBP timeout/fault status, and MMHUBBUB warmup interrupt bits.
- Display I/O integration through HPD, AUX, I2C/DDC, DIG link events, DCIO DPCS errors, DPIA, DSC, writeback, and Azalia audio endpoint interrupts.

## Risks

The central risk is silent hardware misprogramming if any generated shift or mask does not match the silicon register specification. A one-bit error can corrupt unrelated fields during read-modify-write, poll the wrong done/status bit, leave clocks gated, route interrupts incorrectly, or hide hardware errors.

Repeated macro families make copy/paste or generator-template mistakes high impact. For example, per-OTG, per-HUBP, per-DIG, and per-DCPG fields often share layouts but not always identical bit positions. Treating all instances as mechanically identical can be wrong, especially where this chunk shows asymmetric coverage such as OPTC5/6 underflow in `CONTINUE4`, HUBP0-2 timeout in `CONTINUE13-15`, HUBP3-7 timeout grouped in `CONTINUE16`, and OTG0 events appearing in destination registers while status naming often starts at OTG1.

Interrupt continuation bits at bit 31 are also risky. If code fails to follow the continuation chain, events in later registers can be missed. If code assumes continuation registers are fully populated, sparse continuation registers such as `CONTINUE7`, `CONTINUE8`, and `CONTINUE12` can lead to confusing diagnostics.

The chunk boundary is a documentation risk: `OTG2_INTERRUPT_DEST` is incomplete in this assigned range. Any final merged research for the whole file should avoid concluding the OTG interrupt destination family from this chunk alone.

## Test Signals

Useful validation for changes touching consumers of these macros includes:

- Build coverage for AMDGPU/DCN 3.2 paths with warnings treated seriously, because macro renames or missing fields fail at compile time.
- Display bring-up on DCN 3.2 hardware: link training, HPD detection, AUX/I2C/DDC reads, HDMI/DP stream enable, and modeset success exercise the clock, DTO, and interrupt fields.
- Clock programming tests: verify DISPCLK/DPPCLK changes complete, DTO phase/modulo programming produces expected pixel clocks, and no DCCG FIFO error or unexpected add/drop pixel counters appear.
- Interrupt tests: hotplug, vblank, page flip, underflow injection/observation, AUX completion, DMCUB mailbox, DSC error, writeback overflow, and DCPG power transition paths should map to the expected status and destination bits.
- Suspend/resume and power-gating tests: confirm DCPG, HUBP/HUBBUB, DMCUB, and clock-gating fields restore correctly after reset or power state changes.
- Register trace comparison against vendor register specifications or known-good driver traces, especially for read-modify-write masks and fields with overlapping clear/status semantics such as `DCCG_VSYNC_CNT_INT_CTRL`.
