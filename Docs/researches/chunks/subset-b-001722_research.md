# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_1_sh_mask.h lines 1-2496

## Scope And Purpose

This chunk is the opening 2,496 lines of AMD's generated DCN 3.0.1 register shift/mask header. It defines C preprocessor constants for hardware register fields: each exported field generally appears as a `__SHIFT` macro for the field bit position and a `_MASK` macro for the field bit mask. The matching register address metadata lives in `dcn_3_0_1_offset.h`; this file supplies the field layout used by AMD display register helper macros.

There are no executable functions, structs, enums, or local branches in this range. The API surface is the macro namespace itself. Runtime behavior appears only after display driver code includes this header and uses the constants through helpers such as `FD_SHIFT`, `FD_MASK`, `REG_SET_FIELD`, `REG_GET`, `REG_UPDATE`, `SRI`, or `SF`.

The covered range starts at the header guard and includes register-field definitions for Azalia/HDA controller and endpoint blocks, VGA compatibility/MMHUBBUB display blocks, a large DCCG clock-control section, DCCG DFS and DC performance monitor blocks, DMU display power-gating and performance monitor blocks, DMU miscellaneous control, and the beginning of the DMCU display microcontroller block. The chunk ends inside `DMCU_INTERRUPT_STATUS` mask definitions; later DMCU interrupt masks and the rest of the full 53,361-line header continue in following chunks.

## Register Blocks Covered

- `dce_dc_hda_azcontroller_azdec`: HDA/Azalia controller capability, version, stream payload, global reset/flush/control, wake/status, stream interrupt enable/status, wall-clock, stream synchronization, CORB/RIRB command/response ring buffers, immediate command/response registers, DMA position buffer address, and wall-clock alias fields.
- `dce_dc_hda_azendpoint_azdec` and `dce_dc_hda_azinputendpoint_azdec`: immediate command data/index fields for output and input endpoints. The stream0 through stream7 address blocks are present as comments in this slice but have no field macros here.
- `dce_dc_mmhubbub_vga_dispdec[72..76]` and `[948..986]`: legacy VGA memory page registers plus CRTC, sequencer, graphics, attribute, DAC, feature-control, misc-output, and status/readback fields.
- `dce_dc_mmhubbub_vga_dispdec`: VGA rendering, sequencer reset, mode control, aperture/surface address, HDP/cache control, per-display VGA control for D1 through D6, status/interrupt clear/status, main/test/QoS control, and VGA source selection.
- `dce_dc_dccg_dccg_dispdec`: display clock generation/control fields for PHY pixel-clock resync, DisplayPort DTO DBUF enables, reference-clock and clock-gating delay registers, downspread/GTC DTOs, DSC/DPP DTO parameters, display-clock ramping, global memory power request disable, DCCG performance monitor enables, clock-gate disable controls, timebase dividers, symbol/HDMI character clock enables, soft resets, audio DTOs, v-sync counter/latch/interrupt controls, forced symbol-clock disables, and PHY symbol-clock force controls.
- `dce_dc_dccg_dccg_dfs_dispdec`: `DENTIST_DISPCLK_CNTL` fields for DISPCLK/DPPCLK divider programming and change-done/toggle status.
- `dce_dc_dccg_dccg_dcperfmon0_dc_perfmon_dispdec` and `dcperfmon1`: repeated performance monitor register layouts for counter event selection, counted value type, counter state, run/count-off control, interrupt status/ack bits, counter value high/low readback, and selected read fields.
- `dce_dc_dmu_dc_pg_dispdec`: power-gating config/status for domains 0-7 and 16-18, plus interrupt status and interrupt control fields for domains 0-21. The status/control registers pack paired power-up and power-down event bits, masks, and clears.
- `dce_dc_dmu_dmu_dcperfmon_dc_perfmon_dispdec`: a third DC performance monitor block with the same counter/control/value pattern as perfmon0 and perfmon1, associated with DMU.
- `dce_dc_dmu_dmu_misc_dispdec`: pipe disable/DMCUB enable, DMU clock-gating status/control, DMCU ERAM/IRAM memory power controls, and forced deep-sleep allowance fields.
- `dce_dc_dmu_dmcu_dispdec`: beginning of DMCU control/status and memory access definitions, including microcontroller reset/enable/IRQ gating, firmware start/end/checksum address fields, ERAM/IRAM host access controls, ERAM/IRAM read/write data paths, internal interrupt status bits, static-screen interrupt status/clear fields, and the first part of `DMCU_INTERRUPT_STATUS`.

## Important APIs, Types, And Macros

The important exported contract is consistent:

- `<REGISTER>__<FIELD>__SHIFT` gives the field's starting bit.
- `<REGISTER>__<FIELD>_MASK` gives the field's mask in the register value.
- Comments such as `//DMCU_CTRL` and `// addressBlock: dce_dc_dmu_dmcu_dispdec` group generated definitions but are not C symbols.
- Register names in this chunk include uninstanced blocks such as `GLOBAL_CAPABILITIES`, `DCCG_AUDIO_DTO_SOURCE`, `DENTIST_DISPCLK_CNTL`, `DOMAIN0_PG_CONFIG`, and `DMCU_CTRL`, plus instance-style names such as `D1VGA_CONTROL` through `D6VGA_CONTROL`, `DC_PERFMON0_*` through `DC_PERFMON2_*`, and `PHYPLLA_*` through `PHYPLLD_*`.

This chunk does not define type-safe wrappers or validation logic. Consumers are expected to pass values through AMD's register accessor macros, which combine offset metadata from the companion offset header with these shifts and masks. Direct include evidence in this tree for the exact DCN 3.0.1 header includes `display/dmub/src/dmub_dcn301.c`, which includes both `dcn_3_0_1_offset.h` and `dcn_3_0_1_sh_mask.h` and relies on `FD_MASK`/`FD_SHIFT`-style register field binding.

## Control Flow

There is no local control flow in the header. The effective flow is compile-time and table-driven:

1. A DCN 3.0.1 display component includes `dcn_3_0_1_offset.h` and this `dcn_3_0_1_sh_mask.h`.
2. Register-list or field-list macros bind a logical register and field to an address, shift, and mask.
3. Runtime code calls AMD register helpers to read, update, or write MMIO registers.
4. The helper uses the generated mask/shift macros to isolate or pack the requested field.

Because these are raw hardware layout constants, this file does not decide sequencing for reset, power gating, display-clock programming, interrupt acknowledgement, or ring-buffer operation. That sequencing is owned by the display, DMUB/DMCU, audio, VGA, and power-management code that consumes the macros.

## State And Persistence Behavior

The header itself has no mutable state. It describes persistent and volatile state in hardware registers:

- Configuration state includes HDA ring buffer base addresses, DMA position buffer enable/address, VGA surface and mode controls, DCCG DTO phase/modulo values, clock-source selections, clock-gate disable bits, timebase divisors, perfmon event selection, power-gating force/gate requests, DMCU firmware address windows, and ERAM/IRAM access controls.
- Status state includes HDA flush/interrupt/status bits, wall-clock counters, VGA access/display-switch status, DCCG ramp-done and clock/error status, performance counter active/state/status fields, power-domain desired/current FSM state, DMU clock-on status, DMCU reset/wait/stop state, internal interrupt state, static-screen interrupt status, and DMCU interrupt occurrence bits.
- Event and interrupt state often has adjacent status and clear/ack fields, visible in names such as `*_INT_OCCURRED`, `*_INT_CLEAR`, `*_INT_STATUS`, `*_ACK`, and `*_EVENT_CLEAR`. Some clear fields share the same bit position and mask as the corresponding occurrence field.

Persistence across suspend/resume, GPU reset, display power gating, or modeset is not defined here. Driver code must restore or reprogram any hardware state that should survive those transitions.

## Dependencies And Integration Points

The direct dependency is the hardware register contract for DCN 3.0.1. This mask header must stay aligned with `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_1_offset.h`, which gives the addresses and base indices for the same symbolic registers.

The integration surface is AMD display and GPU register access code. `display/dmub/src/dmub_dcn301.c` is the visible direct include site for this exact generated header in the imported tree. Broader AMD display code follows the same generated-register pattern: register tables bind fields through `FD_MASK`/`FD_SHIFT` or `SF`, and runtime paths use `REG_GET`, `REG_UPDATE`, `REG_SET_FIELD`, or raw `RREG32`/`WREG32` sequences where appropriate.

Functional integration points represented by this chunk include:

- HDA/Azalia audio controller setup and interrupt handling through global, CORB/RIRB, immediate command, stream interrupt, and DMA position fields.
- VGA compatibility paths for legacy register aperture behavior, VGA memory mapping, CRTC/sequencer/graphics/DAC register access, VGA mode selection, and VGA-related interrupts.
- DCCG clock management for display, pixel, symbol, DP reference, DSC, DPP, audio DTO, and GTC/downspread clocks.
- Performance monitor setup and readback for display clock/DCCG/DMU monitoring.
- Display power-gating through DMU domain config/status and interrupt mask/clear fields.
- DMU/DMCU bring-up, firmware address programming, microcontroller memory access, static-screen and vertical blank interrupt signaling, and low-power clock/memory controls.

This path is under a Ceph-client source import, but the file content is AMD GPU display hardware metadata and is not related to Ceph filesystem logic.

## Risks And Edge Cases

The main risk is hardware-contract drift. A wrong shift or mask can silently modify the wrong MMIO bits, which can break display clocks, audio command rings, VGA legacy behavior, power-gating transitions, DMCU firmware control, or interrupt acknowledgement.

Several fields are replicated across instances or domains. `D1VGA_CONTROL` through `D6VGA_CONTROL`, `PHYPLL[A-D]`, `SYMCLK[A-D]`, `DC_PERFMON[0-2]`, and `DOMAIN*` power-gating registers have repeated layouts where a generation mistake for one prefix can create pipe-specific or domain-specific failures that are hard to diagnose.

Interrupt and clear semantics require care. This chunk contains many fields where status, occurrence, clear, mask, and ack bits are adjacent or share bit positions. Confusing a status mask with a clear mask can cause stuck interrupts, lost events, or accidental acknowledgement of unrelated power/DMCU/static-screen events.

Clock and power fields are sequencing-sensitive. DCCG gate-disable, soft-reset, DTO, clock-source, and DENTIST divider fields need to be programmed in the order expected by clock-manager and firmware code. DMU power-domain force/gate requests and status polling must respect hardware state transitions.

Address and buffer fields need alignment and width discipline. CORB/RIRB and DMA position lower base address fields mask low unimplemented bits, VGA surface/base fields are width-limited, DMCU ERAM/IRAM address fields have small ranges, and many counter or selector fields truncate overwide values rather than validating them.

This is only the first chunk of the file. It ends in the middle of `DMCU_INTERRUPT_STATUS`, so merge/reconciliation must use later chunks for the rest of the DMCU interrupt, DMCUB, display interrupt, destination-routing, and subsequent register blocks.

## Test Signals

Build-time validation is the first signal. Any removed, renamed, or malformed macro used by DCN 3.0.1 display/DMUB code should surface as compilation failures around generated register structures, `FD_MASK`, `FD_SHIFT`, `REG_FIELD`, `REG_GET`, `REG_UPDATE`, or `REG_SET_FIELD` expansions.

Static validation should compare this generated header against the authoritative AMD register database and against the companion `dcn_3_0_1_offset.h`. Repeated layouts should be checked for expected consistency across VGA display instances, PHY/SYMCLK instances, perfmon instances, and DMU power domains.

Runtime signals on DCN 3.0.1-class hardware include successful DMUB/DMCU initialization, stable display clock programming, valid audio/HDA command response behavior, working VGA legacy access where exercised, clean modeset/suspend/resume transitions, power-domain up/down interrupts clearing correctly, and absence of display clock, underflow, or interrupt storm symptoms.

Focused diagnostics include reading DCCG current/timebase/perfmon counters, checking DENTIST divider change-done toggles, verifying DMCU reset/status and ERAM/IRAM host access paths, testing static-screen/vblank/DCPG interrupt status-clear behavior, and confirming ring-buffer base/size programming for HDA command and response paths.
