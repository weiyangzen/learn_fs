# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_2_1_0_sh_mask.h lines 1-2452

## Purpose

This chunk is the opening portion of the generated DCN 2.1.0 shift/mask header used by the AMD display driver. It does not implement executable logic; it publishes C preprocessor constants that describe bit positions (`__SHIFT`) and bit masks (`_MASK`) for memory-mapped display hardware registers.

The covered range starts at the include guard and covers the first hardware address blocks in the header:

- MMHUBBUB VGA/display-decode fields for legacy VGA page addresses, render/mode control, VGA status, VGA interrupts, and per-display VGA routing.
- DCCG display clock generator fields for PHY pixel clock resynchronization, DP DTOs, reference clocks, clock-gating controls, DISPCLK/DPPCLK/DSCCLK DTO programming, audio DTOs, VSYNC counters, and test clock selection.
- DFS/Dentist display-clock divider fields for DISPCLK and DPPCLK frequency changes.
- DC performance monitor register fields for perfmon instances 0, 1, and 2.
- PLL macro reserved register masks.
- DMU/RBBMIF timeout/status fields, display power-gating domain fields, DMU clock/memory-power controls, and the beginning of DMCU control, firmware memory access, event, and interrupt masks.

The chunk ends at line 2452 inside the `DMCU_INTERRUPT_TO_UC_EN_MASK` register description, after the `DCPG_IHC_DOMAIN4_POWER_UP_INT_TO_UC_EN` shift field. The remaining fields for that register and the rest of the header are outside this chunk.

## Important APIs, Types, And Functions

There are no functions, structs, enums, or runtime APIs defined in this chunk. The important interface is the generated macro namespace:

- `REGISTER__FIELD__SHIFT`: bit offset for a field within a 32-bit MMIO register.
- `REGISTER__FIELD_MASK`: mask for the same field, already positioned in the register word.
- Include guard `_dcn_2_1_0_SH_MASK_HEADER`.

Typical consumers combine these macros with register-access helper layers such as `REG_GET`, `REG_UPDATE`, `REG_UPDATE_N`, `FD_MASK`, and `FD_SHIFT`. The paired offset header `dcn_2_1_0_offset.h` provides register addresses, while this file provides the bit layout needed to encode/decode fields at those addresses.

High-value register groups in this chunk include:

- VGA compatibility: `VGA_RENDER_CONTROL`, `VGA_SEQUENCER_RESET_CONTROL`, `VGA_MODE_CONTROL`, `VGA_HDP_CONTROL`, `VGA_CACHE_CONTROL`, `D1VGA_CONTROL` through `D6VGA_CONTROL`, `VGA_STATUS`, `VGA_INTERRUPT_CONTROL`, and `VGA_SOURCE_SELECT`.
- DCCG clocking: `PHYPLL[A-E]_PIXCLK_RESYNC_CNTL`, `DP_DTO_DBUF_EN`, `REFCLK_CNTL`, `DPREFCLK_CNTL`, `DCCG_DS_*`, `DCCG_GTC_*`, `DISPCLK_FREQ_CHANGE_CNTL`, `DCCG_GATE_DISABLE_CNTL`, `DCCG_GATE_DISABLE_CNTL2`, `DPPCLK_DTO_CTRL`, `DSCCLK_DTO_CTRL`, and `DCCG_AUDIO_DTO_*`.
- Pixel-rate DTOs: `OTG0_PIXEL_RATE_CNTL` through `OTG3_PIXEL_RATE_CNTL`, `DP_DTO0_PHASE/MODULO` through `DP_DTO3_PHASE/MODULO`, and `OTG[0-3]_PHYPLL_PIXEL_RATE_CNTL`.
- Clock divider control: `DENTIST_DISPCLK_CNTL`.
- Performance counters: `DC_PERFMON0_*`, `DC_PERFMON1_*`, and `DC_PERFMON2_*`.
- Power and management: `DOMAIN[0-7,16-18]_PG_CONFIG/STATUS`, `DCPG_INTERRUPT_STATUS`, `DCPG_INTERRUPT_STATUS_2`, `DCPG_INTERRUPT_CONTROL_[1-3]`, `DC_IP_REQUEST_CNTL`, `DMU_CLK_CNTL`, `DMU_MEM_PWR_CNTL`, `SMU_INTERRUPT_CONTROL`, and `DMU_MISC_ALLOW_DS_FORCE`.
- DMCU firmware/microcontroller access: `DMCU_CTRL`, `DMCU_STATUS`, firmware start/end/checksum registers, ERAM/IRAM access control/data registers, `DMCU_EVENT_TRIGGER`, `DMCU_UC_INTERNAL_INT_STATUS`, static-screen interrupt fields, and DMCU interrupt status/enable masks.

## Control Flow

This header has no control flow. At compile time, it expands into constants used by DCN 2.1 display code. Runtime control flow appears in the consuming modules when they:

1. Select a register address from `dcn_2_1_0_offset.h`.
2. Select a field mask and shift from this header.
3. Read, write, or poll the MMIO register through AMD display register helpers.

The implied hardware flows represented by the fields are state-machine oriented:

- VGA fields drive legacy display-memory mapping, sequencer reset behavior, per-pipe VGA enablement, status reporting, and interrupt clearing.
- DCCG fields configure display clock sources, pixel clock resync, fractional DTO phase/modulo values, audio DTO selection, VSYNC counter latching, clock gating, soft resets, and test clock routing.
- Dentist fields coordinate divider writes and change/done toggles for DISPCLK/DPPCLK changes.
- Perfmon fields select events, configure counter modes, start/stop conditions, interrupt reporting, and readback paths.
- Power-gating and DMCU interrupt fields expose request/status/clear/mask bits for display power domains and microcontroller-visible display events.

## State And Persistence Behavior

The header itself has no software state and performs no persistence. The state described by the constants lives in hardware registers. Writes made by consumers persist in the GPU display block until reset, power-gate transition, firmware action, or another driver write changes the same register.

Several field families are explicitly stateful at hardware level:

- `*_ENABLE`, `*_GATE_DISABLE`, `*_SOFT_RESET`, `*_POWER_FORCEON`, and `*_POWER_GATE` fields control persistent enable, gating, reset, and power-domain request state.
- `*_STATUS`, `*_CHG_DONE`, `*_DONETOG`, `*_INT_OCCURRED`, and `*_INT_STATUS` fields expose hardware state or latched events.
- Interrupt clear fields often share the same bit positions and masks as the corresponding occurred/status fields, for example in `DCCG_VSYNC_CNT_INT_CTRL`, `DMCU_SS_INTERRUPT_CNTL_STATUS`, and `DMCU_INTERRUPT_STATUS`.
- DTO phase/modulo and divider fields represent programmed clock ratios used continuously by display timing paths.
- DMCU ERAM/IRAM access fields describe host-visible windows into DMCU memory. Auto-increment and host-access-enable bits affect subsequent firmware memory transfers.

Because all masks are raw constants, the type and width semantics come from the consuming register helpers. Most masks are 32-bit values with an `L` suffix, and full-width fields use `0xFFFFFFFFL`.

## Dependencies

This chunk depends on the generated AMD display register naming scheme and the matching offset header for DCN 2.1. Consumers include:

- `display/dc/resource/dcn21/dcn21_resource.c`, which includes this header with `dcn_2_1_0_offset.h` and builds register tables through macros such as `SR`, `SRI`, and `SRIR`.
- `display/dmub/src/dmub_dcn21.c`, which includes this header to populate DMUB common register field masks and shifts through `FD_MASK` and `FD_SHIFT`.
- DCN 2.1 GPIO, IRQ service, and hardware translation code, which include this header for SoC-specific field layouts.
- Shared display modules such as clock manager, DCCG, audio, DMCU, and perfmon code paths that consume the generated field names through per-generation register structures.

The file must stay synchronized with:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_2_1_0_offset.h` for register addresses and base indices.
- DCN 2.1 resource and register-list macros that expect these exact field names.
- Hardware documentation for Renoir/DCN 2.1 display registers.

## Integration Points

The integration boundary is compile-time rather than call-time. DCN 2.1 driver components include this header to specialize generic display code for the DCN 2.1 register layout.

Practical integration examples visible in the tree include:

- `dmub_dcn21.c` maps DMCUB/DMUB common fields to masks and shifts. DMCU/DMCUB interrupt and memory-control fields in this chunk are part of that bridge between host driver and display microcontroller firmware.
- `dcn21_resource.c` uses this header while constructing hardware object register tables for the DCN 2.1 resource pool.
- Clock management code references `DENTIST_DISPCLK_CNTL` fields to read, update, and wait for DISPCLK/DPPCLK divider changes.
- DCE/DCN audio code uses `DCCG_AUDIO_DTO_SOURCE`, `DCCG_AUDIO_DTO0_PHASE/MODULE`, and `DCCG_AUDIO_DTO1_PHASE/MODULE` fields when programming audio clock DTOs.
- DMCU code uses `DMCU_INTERRUPT_TO_UC_EN_MASK`, `DMCU_INTERRUPT_STATUS`, and related fields to enable static-screen, ABM/backlight, vblank, and internal microcontroller interrupt paths.

The final per-file research should stitch this chunk with later chunks because many logical register blocks continue beyond line 2452, especially the DMCU interrupt-to-UC mask register and subsequent DCN display blocks.

## Risks And Edge Cases

- This is generated hardware-description code. A one-bit mask or shift error can misprogram display hardware while still compiling cleanly.
- Field names are part of a macro ABI used by generation-specific register tables. Renaming or removing macros can break consumers that build field tables with token-pasting macros.
- Several interrupt clear fields intentionally share bit positions and masks with occurred/status fields. Mechanical deduplication could remove meaningful aliases and break source readability or register-helper use.
- Full-width masks such as `0xFFFFFFFFL` and high-bit masks such as `0x80000000L` rely on consumers treating values as 32-bit register fields. Refactors should avoid sign-extension surprises when moving these constants through wider signed types.
- The chunk ends in the middle of `DMCU_INTERRUPT_TO_UC_EN_MASK`; any analysis of that register must include the next chunk before drawing completeness conclusions.
- Repeated per-instance blocks, such as `OTG0`-`OTG3`, `DPPCLK0`-`DPPCLK3`, `SYMCLK[A-E]`, and perfmon instances 0-2, are prone to generator or copy drift. Consumers often assume instance layouts are symmetric.
- Power-gating and clock-gating fields are order-sensitive at runtime. Incorrect masks can leave clocks forced on, gate clocks needed by active display paths, or misreport power-domain transitions.
- DMCU ERAM/IRAM host-access fields can affect firmware load/readback flows. Wrong masks may corrupt firmware upload, stall DMCU register reads, or prevent timeout interrupts from being enabled or cleared.

## Test Signals

Useful validation signals for this chunk are mostly compile-time, register-table, and hardware bring-up checks:

- The AMD display driver should compile with DCN 2.1 enabled, with no missing field macros in resource, GPIO, IRQ, DMUB, DMCU, audio, DCCG, and clock-manager code.
- Generated register tables should contain the expected masks and shifts for `DENTIST_DISPCLK_CNTL`, `DCCG_AUDIO_DTO_SOURCE`, `DPPCLK_DTO_CTRL`, `DMCU_INTERRUPT_STATUS`, and `DMCU_INTERRUPT_TO_UC_EN_MASK`.
- Display bring-up on DCN 2.1 hardware should successfully program DISPCLK/DPPCLK and observe `DENTIST_*_CHG_DONE` fields during clock changes.
- DP/HDMI audio tests should validate DTO source, module, and phase programming through the `DCCG_AUDIO_DTO*` fields.
- Hotplug, vblank, static-screen, ABM/backlight, and DMCU internal interrupt tests should exercise the corresponding status, mask, and clear fields.
- Runtime power-management tests should enter and leave display power-gated states while checking domain desired-state and PGFSM status fields.
- Register dump tooling can compare repeated instance masks for OTG, DPPCLK, DSCCLK, SYMCLK, and perfmon blocks to detect unexpected asymmetry.
- Static checks can verify that every `__SHIFT`/`_MASK` pair is internally consistent, for example mask width starts at the declared shift and repeated aliases intentionally share the same bit positions.
