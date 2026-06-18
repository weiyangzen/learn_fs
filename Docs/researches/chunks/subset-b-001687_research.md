# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_0_sh_mask.h lines 1-2452

## Scope

This chunk covers the opening 2,452 lines of the generated DCN 3.0.0 register shift/mask header. It defines preprocessor constants for register fields only; there are no C functions, structs, enums, or executable control paths in this slice. The paired offset header, `dcn_3_0_0_offset.h`, provides register addresses, while this file provides `<REGISTER>__<FIELD>__SHIFT` and `<REGISTER>__<FIELD>_MASK` constants used by AMD display register helper macros.

The slice contains roughly 2,170 `#define` entries plus the MIT SPDX line and header guard. The file continues after this chunk, so this report is intentionally partial and should be merged with later chunks for whole-file conclusions.

## Purpose

The purpose of this header slice is to encode the bit layout of DCN 3.0 display hardware registers in a form that driver code can consume safely through generated field access helpers. Instead of scattering literal shifts and masks across display, DMUB, IRQ, clock, and power-management code, the AMD driver includes this header and uses macros such as `FD_MASK(reg, field)`, `FD_SHIFT(reg, field)`, `REG_GET`, `REG_SET`, and `REG_UPDATE` to read, compose, and update memory-mapped register fields.

This chunk covers these major hardware areas:

- Legacy VGA/MMHUB display decode fields.
- DCCG clock generation, resync, DTO, pixel-rate, gating, reset, VSYNC-count, audio DTO, and perfmon fields.
- DCCG DFS `DENTIST_DISPCLK_CNTL` display-clock divider control.
- DC perfmon blocks 0 and 1 under DCCG.
- RBBMIF timeout/status/interrupt fields.
- DMU display power-gating domains and power transition interrupts.
- DMU perfmon block 2.
- DMU miscellaneous clock, memory power, SMU interrupt, and pipe disable fields.
- The start of DMCU microcontroller control, RAM access, firmware address/checksum, event, and interrupt status fields.

## Important APIs, Types, And Constants

There are no callable APIs or exported data objects. The exported interface is a generated macro namespace:

- `REGISTER__FIELD__SHIFT`: bit position for a hardware field.
- `REGISTER__FIELD_MASK`: bit mask for the same field.
- Register section comments such as `//VGA_RENDER_CONTROL` and `//DCCG_GATE_DISABLE_CNTL` group related field constants.
- Address-block comments such as `// addressBlock: dce_dc_dccg_dccg_dispdec` identify the IP block that owns the following registers.

Important field groups in this chunk include:

- VGA control and status: `VGA_MEM_WRITE_PAGE_ADDR`, `VGA_MEM_READ_PAGE_ADDR`, `VGA_RENDER_CONTROL`, `VGA_SEQUENCER_RESET_CONTROL`, `VGA_MODE_CONTROL`, `VGA_HDP_CONTROL`, `VGA_CACHE_CONTROL`, `D1VGA_CONTROL` through `D6VGA_CONTROL`, VGA interrupt status/clear/control, VGA indexed CRTC/SEQ/GRPH/DAC registers, and `VGA_SOURCE_SELECT`.
- Pixel clock and DTO controls: `PHYPLL[A-F]_PIXCLK_RESYNC_CNTL`, `DP_DTO_DBUF_EN`, `DSCCLK[0-5]_DTO_PARAM`, `DPPCLK[0-5]_DTO_PARAM`, `DP_DTO[0-5]_PHASE`, `DP_DTO[0-5]_MODULO`, `OTG[0-5]_PIXEL_RATE_CNTL`, and `OTG[0-5]_PHYPLL_PIXEL_RATE_CNTL`.
- DCCG timing and gating: `REFCLK_CNTL`, `DPREFCLK_CNTL`, `DISPCLK_FREQ_CHANGE_CNTL`, `DCCG_GATE_DISABLE_CNTL`, `DCCG_GATE_DISABLE_CNTL2`, `DCCG_SOFT_RESET`, `DCCG_DISP_CNTL_REG`, `DCCG_DS_*`, `DCCG_GTC_*`, `MILLISECOND_TIME_BASE_DIV`, and `MICROSECOND_TIME_BASE_DIV`.
- Perfmon layout: `DCCG_PERFMON_CNTL`, `DCCG_PERFMON_CNTL2`, `DC_PERFMON0_*`, `DC_PERFMON1_*`, and `DC_PERFMON2_*` define event selection, counter state, run/stop control, interrupt status/ack, and counter readback fields.
- Power management and interrupts: `DOMAIN0_PG_CONFIG` through `DOMAIN21_PG_STATUS` for selected domains, `DCPG_INTERRUPT_STATUS`, `DCPG_INTERRUPT_STATUS_2`, and `DCPG_INTERRUPT_CONTROL_[1-3]`.
- DMU/DMCU fields: `CC_DC_PIPE_DIS`, `DMU_CLK_CNTL`, `DMU_MEM_PWR_CNTL`, `DMCU_CTRL`, `DMCU_STATUS`, firmware address/checksum registers, ERAM/IRAM read-write controls, `DMCU_EVENT_TRIGGER`, `DMCU_UC_INTERNAL_INT_STATUS`, `DMCU_SS_INTERRUPT_CNTL_STATUS`, and the start of `DMCU_INTERRUPT_STATUS`.

## Control Flow

This chunk has no runtime control flow. Its effects are compile-time only:

1. The compiler preprocesses this header into C translation units that include it.
2. Driver register helper macros concatenate register and field names to resolve these `SHIFT` and `MASK` constants.
3. Runtime code performs the actual register reads/writes through helper macros and MMIO accessors in consumer files.

The visible ordering still matters for human and generator maintenance: the file is grouped by hardware address block and register, and each register generally lists all shifts first followed by all masks. Reordering does not usually affect C compilation, but it can make generated diffs harder to review and can hide mismatches between shift/mask pairs.

## State And Persistence Behavior

The header stores no software state and persists no data. It describes persistent hardware register state owned by the GPU display IP:

- VGA fields control compatibility display modes, VGA memory apertures, cache behavior, sequencer reset behavior, and legacy VGA interrupts.
- DCCG fields control clock selection, enablement, fractional divider/DTO settings, pixel-rate paths, clock gating, soft reset, and status counters. Incorrect values can persist in hardware until reset or until overwritten by the driver.
- Perfmon fields configure hardware counters and interrupt/ack behavior. Counter low/high fields expose sampled hardware state.
- DCPG/DMU fields describe display power-domain force-on/gate requests, desired power states, power FSM status, and power transition interrupt mask/clear bits.
- DMCU fields expose microcontroller reset/enable/status, firmware address metadata, RAM access, and interrupt sources.

Many interrupt status and clear fields intentionally share bit positions and masks, for example DMCU and DCCG VSYNC interrupt status/clear definitions. Consumers must understand whether a field is read-only status, write-one-to-clear, mask, or control based on the register programming model, not from the macro name alone.

## Dependencies And Integration Points

This header depends on generated naming compatibility with AMD's display register infrastructure. It is normally included together with:

- `sienna_cichlid_ip_offset.h` for base segment information.
- `dcn/dcn_3_0_0_offset.h` for register offsets.
- `dmub_reg.h`, `dm_services.h`, and DC register helper macros that build field metadata from `FD_MASK` and `FD_SHIFT`.

Observed direct consumers include:

- `drivers/gpu/drm/amd/display/dmub/src/dmub_dcn30.c`, which includes this header to populate `dmub_srv_dcn30_regs` common field arrays using `FD_MASK(reg, field)` and `FD_SHIFT(reg, field)`.
- `drivers/gpu/drm/amd/display/dmub/src/dmub_dcn302.c`, which reuses DCN 3.0 masks for closely related DMUB support.
- `drivers/gpu/drm/amd/display/dc/irq/dcn30/irq_service_dcn30.c` and `irq/dcn302/irq_service_dcn302.c`, which include the DCN 3.0 offset and mask headers for IRQ-source register programming.
- Older amdgpu display/VGA paths such as `amdgpu/cik.c`, `amdgpu/vi.c`, `amdgpu/si.c`, `amdgpu/gmc_v6_0.c`, and `amdgpu/dce_v6_0.c` use shared VGA mask names including `VGA_RENDER_CONTROL__VGA_VSTATUS_CNTL_MASK`.

The file also integrates indirectly with DCN 3.0 clock, power, DMU, DMCU, perfmon, and debug code wherever generated register field tables are compiled from the macros in this header.

## Risks And Edge Cases

- A wrong bit mask or shift silently corrupts MMIO field access. The compiler will not detect a semantically wrong numeric value if the macro name exists.
- Missing or renamed fields can break generated register tables at compile time through unresolved macro concatenations.
- Cross-ASIC reuse is risky. Nearby DCN versions define similar names with different field sets, for example newer `OTG*_PIXEL_RATE_CNTL` layouts add status/source fields not present in this DCN 3.0.0 chunk.
- Some fields use the same bit for status and clear semantics. Accidentally using a clear macro in a read/modify/write path can acknowledge an interrupt unexpectedly.
- Large full-register masks such as `0xFFFFFFFFL` for DTO phase/modulo and counter readback require width-safe handling in callers.
- The legacy VGA block shares names with non-DCN amdgpu paths. A generated change here can affect code outside the immediate DC display tree.
- Power-gating and clock-gating fields can cause display hangs, blanking, or firmware communication failures if field definitions diverge from the hardware specification.
- This chunk ends in the middle of DMCU interrupt definitions. Whole-file analysis must reconcile the continuation before drawing final conclusions about DMCU interrupt coverage.

## Test Signals

Useful validation signals for this header are mostly build-time and hardware-integration oriented:

- Compile coverage for DCN 3.0/3.0.2 display and DMUB code, especially files that include `dcn_3_0_0_sh_mask.h`.
- Macro expansion checks for representative consumers using `FD_MASK`, `FD_SHIFT`, `REG_GET`, `REG_SET`, and `REG_UPDATE`.
- Display bring-up on DCN 3.0 ASICs with modeset, hotplug, vblank, page flip, and DMUB firmware loading paths active.
- Clock programming tests covering DP DTOs, OTG pixel-rate controls, DPP/DSC DTOs, DISPCLK/DPPCLK changes, and PHYPLL pixel clock resync.
- Interrupt tests for vblank/vupdate, DMCUB outbox, power-domain transitions, DCCG VSYNC counter latches, and DMCU events.
- Power-management tests for display power gating, clock gating, static-screen interrupts, suspend/resume, and runtime display idle/deep-sleep behavior.
- Perf/debug tests that configure `DC_PERFMON0`, `DC_PERFMON1`, and `DC_PERFMON2`, verify counter activity, and acknowledge counter interrupts.

## Open Cross-Chunk Questions

- Later chunks must finish the DMCU interrupt and any remaining DCN register groups to determine whether this file is a complete generated mask set for every DCN 3.0.0 register block.
- Whole-file reconciliation should compare this header against `dcn_3_0_0_offset.h` to detect registers with offsets but missing field definitions, or fields without matching register offsets.
- If the repository has generated-header provenance scripts, the final report should identify the generator/source specification, because hand-editing this file would be high risk.
