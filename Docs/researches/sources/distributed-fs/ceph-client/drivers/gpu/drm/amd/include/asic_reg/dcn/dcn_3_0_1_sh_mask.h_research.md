# Research: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_1_sh_mask.h

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-001722`: lines 1-2496, `Docs/researches/chunks/subset-b-001722_research.md`
- `subset-b-001723`: lines 2497-4770, `Docs/researches/chunks/subset-b-001723_research.md`
- `subset-b-001724`: lines 4771-7223, `Docs/researches/chunks/subset-b-001724_research.md`
- `subset-b-001725`: lines 7224-9864, `Docs/researches/chunks/subset-b-001725_research.md`
- `subset-b-001726`: lines 9865-12377, `Docs/researches/chunks/subset-b-001726_research.md`
- `subset-b-001727`: lines 12378-14892, `Docs/researches/chunks/subset-b-001727_research.md`
- `subset-b-001728`: lines 14893-17407, `Docs/researches/chunks/subset-b-001728_research.md`
- `subset-b-001729`: lines 17408-19930, `Docs/researches/chunks/subset-b-001729_research.md`
- `subset-b-001730`: lines 19931-22460, `Docs/researches/chunks/subset-b-001730_research.md`
- `subset-b-001731`: lines 22461-24958, `Docs/researches/chunks/subset-b-001731_research.md`
- `subset-b-001732`: lines 24959-27395, `Docs/researches/chunks/subset-b-001732_research.md`
- `subset-b-001733`: lines 27396-29755, `Docs/researches/chunks/subset-b-001733_research.md`
- `subset-b-001734`: lines 29756-32176, `Docs/researches/chunks/subset-b-001734_research.md`
- `subset-b-001735`: lines 32177-34584, `Docs/researches/chunks/subset-b-001735_research.md`
- `subset-b-001736`: lines 34585-36968, `Docs/researches/chunks/subset-b-001736_research.md`
- `subset-b-001737`: lines 36969-39480, `Docs/researches/chunks/subset-b-001737_research.md`
- `subset-b-001738`: lines 39481-42015, `Docs/researches/chunks/subset-b-001738_research.md`
- `subset-b-001739`: lines 42016-44533, `Docs/researches/chunks/subset-b-001739_research.md`
- `subset-b-001740`: lines 44534-47180, `Docs/researches/chunks/subset-b-001740_research.md`
- `subset-b-001741`: lines 47181-49549, `Docs/researches/chunks/subset-b-001741_research.md`
- `subset-b-001742`: lines 49550-51891, `Docs/researches/chunks/subset-b-001742_research.md`
- `subset-b-001743`: lines 51892-53361, `Docs/researches/chunks/subset-b-001743_research.md`

## Chunk Research

### subset-b-001722: lines 1-2496

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

### subset-b-001723: lines 2497-4770

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_1_sh_mask.h lines 2497-4770

## Scope And Purpose

This chunk is a generated AMD DCN 3.0.1 register shift/mask header section. It exports C preprocessor constants that describe bit positions (`__SHIFT`) and bit masks (`_MASK`) for display microcontroller, interrupt-routing, display interrupt decoder, and GPU timer registers. The companion offset header provides register addresses; this file provides the bitfield layout used by AMD display register helpers.

The requested range starts in the middle of `DMCU_INTERRUPT_STATUS`, after its field shifts and early masks were emitted in the previous chunk. It then covers DMCU interrupt status, host/UC enable masks, XIRQ routing, firmware scratch and mailbox registers, performance-monitor interrupt status/routing, DisplayPort receiver interrupt status/routing, continued DMCU interrupt status/routing, and the beginning of the `dce_dc_dmu_ihc_dispdec` address block. The display interrupt decoder portion covers `DC_GPU_TIMER_*`, `DISP_INTERRUPT_STATUS`, and `DISP_INTERRUPT_STATUS_CONTINUE` through `CONTINUE22`, then ends inside `DC_GPU_TIMER_START_POSITION_FLIP_AWAY`.

There are no functions, structs, runtime branches, or algorithms in this chunk. Its purpose is to keep hardware field metadata available at compile time for register-list macros and memory-mapped register accessors.

## Register Blocks Covered

The DMCU section includes the tail of `DMCU_INTERRUPT_STATUS`, full `DMCU_INTERRUPT_STATUS_1`, interrupt masks to host and microcontroller, and XIRQ selector registers. These fields describe ABM ready/update interrupts, static-screen interrupts, power-domain power-up/down events, vblank events, OTG range timing updates, generic DMCU interrupts, internal UC faults, and register-read timeout events.

The DMCU control and mailbox area includes `DC_DMCU_SCRATCH`, `DMCU_INT_CNT`, `DMCU_FW_CHECKSUM_SMPL_BYTE_POS`, `DMCU_UC_CLK_GATING_CNTL`, `MASTER_COMM_*`, and `SLAVE_COMM_*`. These registers expose scratch storage, interrupt counters, firmware checksum byte sampling, DMCU clock-gating delays, and byte-addressed command/data mailboxes with interrupt flags between host/master and DMCU/slave paths.

The performance-monitor groups include `DMCU_PERFMON_INTERRUPT_STATUS1` through `STATUS5`, matching `DMCU_PERFMON_INTERRUPT_TO_UC_EN_MASK1` through `MASK5`, and matching `DMCU_PERFMON_INTERRUPT_TO_UC_XIRQ_IRQ_SEL1` through `SEL5`. They define status, enable, and XIRQ routing for MPC, hubp, dpp, opp, otg, dsc, audio, dccg, dio, dchubbub, dchvm, dchubbubmem, dmub, dmcub, azalia, and other display performance/event sources.

The DisplayPort receiver groups include `DMCU_DPRX_INTERRUPT_STATUS1`, `DMCU_DPRX_INTERRUPT_TO_UC_EN_MASK1`, and `DMCU_DPRX_INTERRUPT_TO_UC_XIRQ_IRQ_SEL1`. These define hotplug, AUX, DPRX, training, stream, FEC, MST, SDP, and link-event status/routing fields for multiple DP-related channels.

The continued DMCU interrupt groups include `DMCU_INTERRUPT_STATUS_CONTINUE`, `DMCU_INTERRUPT_TO_UC_EN_MASK_CONTINUE`, `DMCU_INTERRUPT_TO_UC_XIRQ_IRQ_SEL_CONTINUE`, `DMCU_INT_CNT_CONTINUE`, `DMCU_INTERRUPT_TO_UC_XIRQ_IRQ_SEL_CONT2`, `DMCU_INTERRUPT_STATUS_2`, `DMCU_INTERRUPT_TO_UC_EN_MASK_2`, `DMCU_INT_CNT_CONT2`, and `DMCU_INT_CNT_CONT3`. These extend the base interrupt namespace for additional domain power events, vertical events, ABM events, and later DCN interrupt sources.

The `dce_dc_dmu_ihc_dispdec` address block begins at line 3831. It includes GPU timer start-position fields for vupdate, vstartup, vready, flip, vupdate-no-lock, and the beginning of flip-away. It also includes `DC_GPU_TIMER_READ` and `DC_GPU_TIMER_READ_CNTL` for selecting and reading timer-related positions.

The display interrupt decoder status chain covers `DISP_INTERRUPT_STATUS` and `DISP_INTERRUPT_STATUS_CONTINUE` through `CONTINUE22`. These packed status words expose interrupt presence for OPTC/OTG timing, HPD and HPD RX, AUX completion, DP fast-training and stream-disable events, DIO/DP encoder events, I2C/DDC events, ABM events, DCPG domain power events, OTG vstartup/vready/vupdate-no-lock, GSL/vsync-gap, DRR v-total-reach, underflow, and continue-link bits into the next status word.

## Important APIs, Types, And Macros

The exported API is the generated macro naming contract:

- `<REGISTER>__<FIELD>__SHIFT` gives the bit offset for packing or extracting a hardware field.
- `<REGISTER>__<FIELD>_MASK` gives the 32-bit mask for that field in the register value.
- Status and clear fields often intentionally share the same bit position and mask, such as `*_OCCURRED` and `*_CLEAR`.
- Enable-mask and XIRQ-selector registers mirror status register field names so firmware-facing routing can be derived from the same interrupt source vocabulary.
- Register comments such as `//DMCU_DPRX_INTERRUPT_STATUS1` and address-block comments such as `// addressBlock: dce_dc_dmu_ihc_dispdec` are generated delimiters for human orientation.

The chunk is consumed indirectly through AMD register helper macros such as `FD_MASK`, `FD_SHIFT`, `REG_FIELD`, `REG_GET`, `REG_SET`, and `REG_UPDATE`. `display/dmub/src/dmub_dcn301.c` includes both `dcn_3_0_1_offset.h` and this header, then builds `dmub_srv_dcn301_regs` by expanding `DMUB_COMMON_REGS()`, `DMCUB_INTERNAL_REGS()`, and `DMUB_COMMON_FIELDS()` into register offsets, masks, and shifts. Older DMCU/ABM/link-encoder paths also use the same style of mailbox and DMCU field definitions through shared DCE/DCN register-list macros.

The display interrupt fields integrate with AMD interrupt source ID headers. For example, `include/ivsrcid/dcn/irqsrcs_dcn_1_0.h` maps several `DISP_INTERRUPT_STATUS_CONTINUE22` fields to source IDs for DCPG domain power events, ABM0 ready/update events, OTG vupdate-no-lock interrupts, and DRR v-total-reach interrupts.

## Control Flow And State Behavior

This header has no direct control flow. Runtime behavior appears when display or DMUB code expands register-list macros and uses the generated masks and shifts to perform memory-mapped register reads and writes.

The DMCU interrupt status registers are event/state latches. Fields named `*_OCCURRED`, `*_INT`, or `*_INTERRUPT` report pending hardware events, while paired `*_CLEAR` fields acknowledge or clear those events. Enable-mask registers persistently control whether sources are routed to host or microcontroller firmware. XIRQ selector fields persistently select which microcontroller interrupt input receives a given event.

The mailbox registers represent persistent command/data state until overwritten by host, firmware, or reset. `MASTER_COMM_DATA_REG*`, `MASTER_COMM_CMD_REG`, and `MASTER_COMM_CNTL_REG` hold host-to-DMCU command bytes and the master interrupt bit. `SLAVE_COMM_DATA_REG*`, `SLAVE_COMM_CMD_REG`, and `SLAVE_COMM_CNTL_REG` hold DMCU-to-host response bytes, a slave interrupt bit, and a message-in-progress indicator.

The performance-monitor and DPRX fields are event routing and observation state. Status bits reflect hardware events from display subsystems; enable masks and XIRQ selectors determine whether those events are delivered to microcontroller firmware and on which interrupt line.

The display interrupt decoder status words form a continuation chain. The high bit in several `DISP_INTERRUPT_STATUS_CONTINUE*` registers points to the next status register, so interrupt service logic must walk or decode the correct continuation level before interpreting an event bit. The timer start-position registers are packed per-display fields, commonly six or eight 3-bit fields at 4-bit spacing, holding hardware-selected start positions for vupdate, vstartup, vready, flip, vupdate-no-lock, and flip-away events.

## Dependencies And Integration Points

This file depends on the DCN 3.0.1 hardware register database and must remain aligned with `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_1_offset.h`, which supplies the matching register offsets. A shift/mask without the matching offset, or an offset whose fields drift from this file, breaks register access silently.

The direct DCN 3.0.1 include site found in this tree is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn301.c`. That file builds the DMUB service register table using offsets from `dcn_3_0_1_offset.h` and masks/shifts from this header.

The DMCU mailbox fields integrate with shared display-core DMCU and ABM abstractions, including `display/dc/dce/dce_dmcu.h` and `display/dc/dce/dce_abm.h`, where register lists include `MASTER_COMM_DATA_REG1`, `MASTER_COMM_CMD_REG`, `MASTER_COMM_CNTL_REG`, `DMCU_INTERRUPT_TO_UC_EN_MASK`, and related fields. These abstractions use the byte-field masks for firmware commands and interrupt signaling.

The display interrupt decoder fields integrate with the IRQ source ID definitions under `include/ivsrcid/dcn/`. The field names in this chunk are the status-bit side of the mapping between raw display interrupt status words and logical DC interrupt sources.

Power and timing integration is broad. DCPG domain power-up/down bits are consumed by power-management and interrupt paths; OTG vstartup, vready, vupdate-no-lock, GSL, and DRR bits feed timing-sensitive display update logic; HPD/AUX/I2C/DP bits feed connector detection, link management, EDID/DDC transactions, and DisplayPort training/stream event handling.

## Risks And Edge Cases

The highest risk is generated metadata drift. A wrong mask or shift in this file can cause the driver to read a false interrupt source, clear the wrong latched event, route an interrupt to the wrong firmware line, or write mailbox bytes into the wrong positions.

Clear/status aliasing is easy to misuse. Many interrupt fields have identical masks for `*_OCCURRED` and `*_CLEAR`; callers must know whether a register read observes state and whether a write acknowledges it. Treating a clear mask as ordinary configuration can drop pending events.

Continuation status words require exact bit interpretation. A missing or wrong `*_CONTINUE*` bit can stop interrupt decoding before later status words, while an incorrect event bit can report the wrong logical source ID. This is especially relevant around `DISP_INTERRUPT_STATUS_CONTINUE21` and `CONTINUE22`, where DDC, DP, DCPG, ABM, OTG, and DRR events are packed together.

Mailbox fields are byte-packed. Command/data registers use four 8-bit lanes per 32-bit register, so callers must avoid truncation and must preserve unrelated bytes when updating a single field. Interrupt bits in `MASTER_COMM_CNTL_REG` and `SLAVE_COMM_CNTL_REG` are separate from the data payload and should be sequenced after payload writes.

Packed timer start-position fields are narrow. Most per-display timer position fields use 3-bit masks at 4-bit spacing. Overwide values are truncated by masks, and incorrect per-display indexing can shift a timer configuration to another pipe.

The chunk boundaries are partial. The first lines only complete masks for `DMCU_INTERRUPT_STATUS`; the paired shifts are immediately before the requested range. The final lines only start `DC_GPU_TIMER_START_POSITION_FLIP_AWAY`; remaining masks continue in the next chunk. Merge/reconciliation should not treat either boundary register as fully owned by this document alone.

## Test Signals

Build-time signals include successful compilation of DCN 3.0.1 DMUB code that includes this header, especially expansion of `FD_MASK` and `FD_SHIFT` in `dmub_dcn301.c`. Missing or renamed generated macros should surface as compile errors in register table initialization or in shared DMCU/ABM register-list code.

Static validation should compare this chunk against the generated hardware register database and against `dcn_3_0_1_offset.h` for register-name alignment. Cross-generation comparisons with nearby DCN headers can also catch accidental field omissions, but differences must be checked against DCN 3.0.1 hardware rather than normalized away.

Runtime validation requires DCN 3.0.1-class hardware. High-signal checks include DMUB firmware boot and command exchange, ABM mailbox commands completing, DMCU/DMUB interrupts arriving and clearing correctly, HPD/AUX/DDC events working during connector hotplug and EDID reads, and DP link training/stream-disable events being routed to the expected interrupt sources.

Display timing tests should exercise vblank, vstartup, vready, vupdate-no-lock, DRR v-total-reach, GSL/vsync-gap, and underflow interrupt paths across multiple pipes. Useful failure signals include lost interrupts, interrupt storms, stale status bits after clear, incorrect source IDs, stuck mailbox message-in-progress state, unstable variable-refresh behavior, or unexpected display underflow during modeset and page-flip workloads.

### subset-b-001724: lines 4771-7223

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_1_sh_mask.h lines 4771-7223

## Scope

This chunk is a generated AMD DCN 3.0.1 register shift/mask header slice. It contains only preprocessor constants; there are no C functions, structs, enums, variables, allocation paths, locks, or executable branches. The exported API is the generated field namespace:

- `<REGISTER>__<FIELD>__SHIFT`
- `<REGISTER>__<FIELD>_MASK`

The requested range contains 2,157 `#define` entries across 246 register names. It starts at the tail of `DC_GPU_TIMER_START_POSITION_FLIP_AWAY`, covers display interrupt status and interrupt destination routing, DMCUB/RBBMIF/DMU register fields, MCIF writeback and MMHUBBUB fields, perfmon blocks, and HDA/Azalia stream fields, then ends mid-register in `DC_PERFMON4_PERFCOUNTER_STATE`. Because both boundaries are artificial chunk boundaries, whole-file reconciliation must merge adjacent chunks before making complete claims about either boundary register.

Although this file lives below a local `ceph-client` source mirror, the content is AMDGPU display hardware metadata, not distributed filesystem logic.

## Purpose

The purpose of this chunk is to publish exact bit positions and masks for DCN 3.0.1 display-controller MMIO register fields. Runtime AMDGPU display code combines these constants with matching register offsets from `dcn_3_0_1_offset.h` and register helper macros such as `REG_READ`, `REG_WRITE`, `REG_GET`, `REG_SET`, and `REG_UPDATE`.

Major hardware areas represented here are:

- Display interrupt status continuation registers `DISP_INTERRUPT_STATUS_CONTINUE23` through `DISP_INTERRUPT_STATUS_CONTINUE25`, including DCPG power interrupts, DSC underflow/core/perfmon interrupts, DMCUB mailbox/timer/data/fault interrupts, HPO and MMHUBBUB interrupts, and ABM histogram/luma/backlight interrupts for ABM2 through ABM5.
- Interrupt destination routing registers for display blocks: `DCCG`, `DMU`, `DCPG`, `MMHUBBUB`, `WB`, `DCHUB`, DCHUB and DPP perf counters, `MPC`, `OPP`, `OPTC`, per-OTG instances 0 through 5, `DIG`, `I2C_DDC_HPD`, `DIO`, `DCIO`, `HPD`, `AZ`, `AUX`, and `DSC`.
- DMCUB and DMU interface control: RBBMIF security, timeout, status, timeout-disable, interrupt status, DMCUB memory regions and cache-window regions, interrupt enable/ack/status/type, extended interrupt status/context/ack, fault-address capture, security/reset controls, memory QoS/read/write spaces, mailbox base/size/read/write pointers, timers, scratch registers, GPINT data, light-sleep wake, memory power, timer current value, and processor ID.
- MCIF writeback and MMHUBBUB: writeback buffer manager control/status, four buffer slots with luma/chroma addresses, status, tags, locks, overrun/TMZ fields, pitch, resolution, sizes, arbitration, VCE handoff controls, NB pstate/self-refresh/QoS/watermark controls, VMID, warmup configuration, VGAIF latency and outstanding counters, memory power, clock gating, soft reset, and DMU interface error status.
- DC perfmon instances 3 and 4: counter control, counted-value type, hardware stop/count-off selection, counter state selection, perfmon state/report count, interrupt status/ack, current value high/low, and read selectors.
- HDA/Azalia stream indirection for streams 0 through 7 plus Azalia clock gating/test-clock fields.

## Important API Surface

This chunk's important API is the generated macro set consumed by register table builders and field access helpers. Representative high-risk or high-integration fields include:

- `DMCUB_REGION*_OFFSET`, `DMCUB_REGION*_OFFSET_HIGH`, and `DMCUB_REGION*_TOP_ADDRESS` fields for DMCUB firmware memory window programming. `*_TOP_ADDRESS` registers pack the top address with an enable bit at bit 31.
- `DMCUB_REGION3_CW*_BASE_ADDRESS`, `DMCUB_REGION3_CW*_TOP_ADDRESS`, `DMCUB_REGION3_CW*_OFFSET`, and `*_OFFSET_HIGH` for DMCUB cache-window setup used by firmware boot, inbox/outbox, trace, and other firmware-visible memory regions.
- `DMCUB_INTERRUPT_ENABLE`, `DMCUB_INTERRUPT_ACK`, `DMCUB_INTERRUPT_STATUS`, and `DMCUB_INTERRUPT_TYPE` fields for timer, inbox, outbox, GPINT, and undefined-address-fault interrupt control.
- `DMCUB_INBOX0_*`, `DMCUB_INBOX1_*`, `DMCUB_OUTBOX0_*`, and `DMCUB_OUTBOX1_*` fields for firmware command/event ring base addresses, sizes, and read/write pointers.
- `DMCUB_SEC_CNTL`, `DMCUB_CNTL`, `DMCUB_MEM_CNTL`, `DMCUB_MEM_PWR_CNTL`, and `DMCUB_SCRATCH0` through `DMCUB_SCRATCH15` for boot/reset/security, memory access policy, firmware state exchange, and debug.
- `MCIF_WB_BUFMGR_SW_CONTROL`, `MCIF_WB_BUFMGR_STATUS`, `MCIF_WB_BUF_*_STATUS`, `MCIF_WB_BUF_*_STATUS2`, `MCIF_WB_BUF_*_ADDR_[YC]`, `*_HIGH`, `MCIF_WB_BUF_*_RESOLUTION`, `MCIF_WB_VMID_CONTROL`, and `MCIF_WB_MIN_TTO` for display writeback buffer management.
- `MMHUBBUB_WARMUP_*`, `MMHUBBUB_MEM_PWR_*`, `MMHUBBUB_CLOCK_CNTL`, `MMHUBBUB_SOFT_RESET`, and `DMU_IF_ERR_STATUS` for memory hub warmup, memory power, clock/reset, and interface error handling.
- `DC_PERFMON3_*` and `DC_PERFMON4_*` fields for display performance counter programming and interrupt/status handling.
- `AZF0STREAM<n>_AZALIA_STREAM_INDEX` and `AZF0STREAM<n>_AZALIA_STREAM_DATA` for indexed HDA stream register access.

The field constants are untyped numeric constants. Correctness depends on exact token names because AMD display code pastes register and field tokens into generated `__SHIFT` and `_MASK` macro names.

## Control Flow

There is no local runtime control flow. The runtime sequence is supplied by AMDGPU display code:

1. DCN 3.0.1 code includes `dcn_3_0_1_offset.h` and this `dcn_3_0_1_sh_mask.h`.
2. Resource, IRQ, DMUB, DWB/MMHUBBUB, audio, and link code build register and field tables with token-pasting macros.
3. Register helpers use the generated `__SHIFT` and `_MASK` values to read, write, update, set, poll, or acknowledge hardware fields.

Direct integration examples in this tree include `display/dmub/src/dmub_dcn301.c`, which includes this exact header and builds `dmub_srv_dcn301_regs` from `DMUB_COMMON_REGS()`, `DMCUB_INTERNAL_REGS()`, and `DMUB_COMMON_FIELDS()`. `display/dc/resource/dcn301/dcn301_resource.c` also includes this header and uses DCN301 register-list and mask-list macros for display resources, audio, AUX/HPD, link encoders, panel control, DPP, OPP, and related DC objects.

The macros do not encode ordering requirements. Callers must still sequence DMCUB reset and memory-window setup, mailbox pointer initialization, interrupt clear/enable, writeback buffer locking, MMHUBBUB clock/power/reset changes, Azalia stream indexed writes, and perfmon start/stop/ack handling according to hardware rules.

## State And Persistence

This header stores no software state and persists nothing on its own. It describes MMIO-backed hardware state:

- DMCUB firmware state includes memory window mappings, cache-window enablement, secure reset state, mailbox ring locations and pointers, scratch registers used for boot/status/options, timers, GPINT data, interrupt status/ack/type bits, and fault address captures.
- Interrupt destination and status fields control how display block events are routed and observed by the interrupt handler.
- MCIF writeback state includes buffer slot ownership, active/next buffer selection, line counters, locks, overflow/overrun indicators, luma/chroma addresses, resolution, pitch, TMZ/security-related flags, VMID, arbitration, and pstate/watermark behavior.
- MMHUBBUB state includes warmup DMA address/range/VMID/QoS, memory and clock power controls, soft resets, outstanding counters, VGAIF controls, and DMU interface error bits.
- Perfmon state includes selected events, run/stop controls, counter states, current values, and sticky interrupt status/ack fields.
- Azalia stream state is accessed through per-stream index/data windows and audio clock gating controls.

Persistence is hardware-defined. Configuration fields normally remain until reprogrammed, power-gated, reset, or restored after suspend/resume. Status, fault, interrupt, ack, and counter fields may be sticky, read-only, write-one-to-clear, self-clearing, or timing-sensitive; this generated header does not distinguish those semantics.

## Dependencies And Integration Points

This chunk depends on:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_1_offset.h` for matching DCN 3.0.1 register offsets and base indexes.
- `vangogh_ip_offset.h` and DCN base-segment definitions used by DCN301 code to turn offsets into absolute MMIO addresses.
- AMD display register helper infrastructure (`reg_helper.h`, `dmub_reg.h`, and block-specific register-list macros) that expects the generated shift/mask naming convention.

Important integration paths:

- `display/dmub/src/dmub_dcn301.c`: exact include site for this header; constructs DMUB register offset, mask, and shift tables for `DMUB_ASIC_DCN301`.
- `display/dmub/src/dmub_srv.c`: selects `dmub_srv_dcn301_regs` for DCN301 ASICs.
- `display/amdgpu_dm/amdgpu_dm.c`: maps the relevant display ASIC to `DMUB_ASIC_DCN301`.
- `display/dc/resource/dcn301/dcn301_resource.c`: exact include site for DCN301 display resource construction and many field-table initializers.
- `display/dc/dcn10/dcn10_dwb.h`, `display/dc/dcn30/dcn30_dwb.h`, and `display/dc/dcn30/dcn30_mmhubbub.h`: consume MCIF writeback and MMHUBBUB-style field names represented in this range.
- `display/dc/irq/*/irq_service_*.c`: related IRQ service code consumes generated interrupt enable/status/ack/destination fields for display and DMCUB events.
- `display/dc/dce/dce_audio*` and DCN audio register-list code: consume Azalia/HDA index/data and clock-control fields for display audio.

## Risks And Edge Cases

- A wrong mask or shift compiles cleanly but can update the wrong bit in a live MMIO register. The highest-risk fields are reset, memory-window enable, mailbox pointer, interrupt ack, writeback buffer lock/status, pstate/watermark, and fault-clear fields.
- DMCUB boot is sensitive to address-window programming. Incorrect offset-high, top-address, enable, or secure-reset fields can prevent firmware boot, map the wrong memory, corrupt inbox/outbox traffic, or leave DMUB in reset.
- Mailbox pointers and interrupt fields are producer/consumer state. Bad masks in inbox/outbox read/write pointers or ready/done/GPINT ack bits can cause command hangs, lost notifications, or interrupt storms.
- Writeback buffer fields are repeated for four slots and for luma/chroma planes. Instance-like copy drift can affect only one buffer slot, one plane, or TMZ/overrun handling under capture/writeback workloads.
- Status and ack bits often share registers. Generic read-modify-write updates around `*_STATUS`, `*_ACK`, `*_INT_STATUS`, and `*_CLEAR` fields can accidentally clear sticky diagnostics or fail to clear an interrupt if the mask semantics are wrong.
- Power, clock, and reset fields interact with low-power transitions. Incorrect `MMHUBBUB_*`, `DMCUB_MEM_PWR_*`, or `AZ_CLOCK_CNTL` masks can produce suspend/resume failures, ignored writes while a block is gated, or stale state after reset.
- Perfmon fields are multiplexed and packed. Counter select, value high/low, interrupt status, and ack field drift may produce misleading diagnostics rather than obvious functional failures.
- The chunk ends before all `DC_PERFMON4_PERFCOUNTER_STATE` masks are visible, so this work item should not be used as the only source for the complete DC perfmon4 register-family description.

## Test Signals

Useful validation signals for this chunk are:

- Build AMDGPU display with DCN301/Van Gogh support enabled. Missing or renamed macros should fail in DMUB DCN301 register-table construction, DCN301 resource construction, DWB/MMHUBBUB code, audio code, or IRQ tables.
- Mechanically verify the generated naming contract in lines 4771-7223: each intended field has a `__SHIFT` and matching `_MASK`, repeated register families preserve expected bit positions, and boundary registers are reconciled with adjacent chunks.
- Diff against AMD's authoritative DCN 3.0.1 register database and nearby generated headers such as `dcn_3_0_0_sh_mask.h` where DCN 3.0 and DCN 3.0.1 are expected to align.
- Runtime DMUB tests: firmware boot, reset/reload, secure backdoor load, region/window setup, cached inbox/outbox use, GPINT handling, outbox interrupts, scratch/status readback, fault capture, and suspend/resume.
- Runtime display interrupt tests: hotplug, AUX/DDC, vblank/vupdate, DMCUB outbox ready/done, DSC underflow/core/perfmon, ABM2-5 events, and interrupt ack/reenable paths.
- Writeback tests: enable/disable DWB, exercise all buffer slots, luma/chroma addresses, pitch/resolution programming, software locks, overrun/overflow detection, VMID/TMZ cases, and pstate/watermark transitions.
- MMHUBBUB and low-power tests: warmup address programming, outstanding counter sanity, memory power state convergence, clock-gating/reset paths, and suspend/resume without stuck DMU interface errors.
- Audio tests: HDMI/DP audio stream setup across Azalia stream instances, indexed stream register access, audio clock gating, and audio recovery after modeset or power transition.
- Perfmon tests: select events, start/stop counters, read high/low values, trigger counter interrupts, and verify ack/status behavior for perfmon3 and the adjacent perfmon4 family after merged coverage is available.

## Chunk Notes

This is generated register metadata, not functional logic. The main research value is identifying which hardware surfaces the constants expose and where bad constants would have the largest blast radius: DMCUB boot/mailbox/control, interrupt routing and acknowledgement, MCIF writeback buffer ownership, MMHUBBUB power/warmup behavior, audio stream indirection, and display performance counters.

### subset-b-001725: lines 7224-9864

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_1_sh_mask.h lines 7224-9864

## Scope And Purpose

This chunk is a generated AMD DCN 3.0.1 register shift/mask table. It contains C preprocessor constants that describe bit positions (`__SHIFT`) and bit masks (`_MASK`) for display-engine, audio, memory-hub, VM, HUBP, cursor, and performance-monitor registers. It does not define executable functions, structs, or runtime branches; its value is the compile-time register-field contract consumed by AMD display driver register helpers.

The requested range starts in the tail of the `DC_PERFMON4` block, covers the Azalia/HDA controller and codec-index windows, the main `DCHUBBUB` fabric and VM-request blocks, the `DC_PERFMON5` block, 16 DCN VM contexts, the first HUBP pipe's `HUBP0`/`HUBPREQ0`/`HUBPRET0` register fields, the first cursor block, and ends inside the `DC_PERFMON6` block. The companion offset header (`dcn_3_0_1_offset.h`) supplies register addresses; this file supplies how callers pack and extract the fields inside those 32-bit MMIO registers.

Within lines 7224-9864 there are 2,057 `#define` entries. The dominant prefixes are `DCHUBBUB`, `HUBPREQ0`, `DCN_VM_CONTEXT*`, `DC_PERFMON*`, `AZALIA`, `HUBP0`, `HUBPRET0`, and `CURSOR0_0`. The source is hardware-register metadata, so the practical research surface is the register grouping and the driver integration points that consume the generated names.

## Important APIs, Types, And Macros

The exported API is the naming convention:

- `<register>__<field>__SHIFT` gives the field's bit offset.
- `<register>__<field>_MASK` gives the already-shifted mask for that field.
- Address-block comments such as `// addressBlock: dce_dc_dcbubp0_dispdec_hubpreq_dispdec` identify replicated hardware blocks.
- Register comments such as `//HUBPREQ0_DCSURF_FLIP_CONTROL` delimit groups but are not consumed by C code.

These constants are used by AMD display macros such as `SF`, `HUBP_SF`, `HWS_SF`, `DMUB_SF`, `REG_SET`, `REG_UPDATE`, `REG_GET`, and `REG_READ`. For example, `display/dc/hubp/dcn10/dcn10_hubp.h` builds `HUBP_MASK_SH_LIST_*` entries from names such as `HUBP0_DCSURF_ADDR_CONFIG__NUM_PIPES_MASK`, `HUBPREQ0_DCSURF_FLIP_CONTROL__SURFACE_FLIP_PENDING_MASK`, and `HUBPRET0_HUBPRET_READ_LINE_STATUS__PIPE_READ_VBLANK_MASK`. `display/dc/dce/dce_audio.h` consumes the Azalia endpoint index/data field names, while `display/dc/dcn20/dcn20_vmid.h` consumes the `DCN_VM_CONTEXT0_*` field names as the canonical mask/shift shape for all VM context instances.

`display/dmub/src/dmub_dcn301.c` directly includes `dcn_3_0_1_offset.h` and this `dcn_3_0_1_sh_mask.h`, then materializes DMUB field masks and shifts through `FD_MASK` and `FD_SHIFT`. This makes the chunk relevant not only to kernel display core code but also to the display microcontroller service register abstraction for DCN 3.0.1.

## Register Blocks Covered

`DC_PERFMON4` is a partial tail at the start of the chunk. It includes fields for performance-monitor state, report count, count-off interrupt control/status/acknowledge, clock enable, run-enable start/stop selection, per-counter interrupt status and acknowledge bits, high/low counter value readback, and counter read selection.

`AZF0ENDPOINT0` through `AZF0ENDPOINT7` each expose an indexed Azalia codec endpoint register pair: `AZALIA_F0_CODEC_ENDPOINT_INDEX` selects a codec endpoint register index and `AZALIA_F0_CODEC_ENDPOINT_DATA` carries the data. Each instance has the same `AZALIA_ENDPOINT_REG_INDEX` and `AZALIA_ENDPOINT_REG_DATA` fields.

`AZALIA_CONTROLLER`, root, stream, and input endpoint blocks cover the display audio controller. The controller section includes clock gating, audio DTO phase/module, SOC clock/deep-sleep exit controls, DMA non-snoop and isochronous policy for data/BDL/RIRB/CORB paths, cyclic-buffer position/sync, global and stream payload capabilities, input/output stream arbiter controls, CRC controls/results, and memory power control/status. The root section exposes vendor/device/revision IDs, channel count, resync FIFO control, function parameter capabilities, power/reset controls, subsystem response fields, converter synchronization, audio port connectivity, GTC offsets, and registerized port connectivity. Stream windows `AZF0STREAM8` through `AZF0STREAM15` provide indexed stream register access; input endpoints `AZF0INPUTENDPOINT0` through `AZF0INPUTENDPOINT7` mirror the index/data access model for codec input endpoint registers.

`DCHUBBUB_SDPIF`, `DCHUBBUB_RET_PATH`, and main `DCHUBBUB` blocks describe the display hub fabric. The SDPIF and VM-address fields include physical request selection, forced IO status, framebuffer location, AGP bounds/base, local HBM address bounds and lock control, SDPIF memory power state, and SDPIF configuration. The return path section defines DCC configuration for surfaces 0 through 7, return-path memory power control/status, and CRC capture controls/results. The main hubbub section covers outstanding request limits, saturation/QoS force, DRAM state control, A/B/C/D watermarks for urgency, memory-trip, self-refresh enter/exit, DRAM clock-change behavior, watermark change control, timeout enable/detection/interrupt status, global timer control, surface-check addresses, VTG controls, soft reset, clock control, DCFCLK control, performance measurement, status, debug-index/data, fractional urgent bandwidth, host-VM controls, and FMON controls.

`DC_PERFMON5` is the DCHUBBUB perfmon instance. It has the standard DC perfmon shape: event select, counted-value select/type, increment and hardware-control mode, run-enable mode, count-off selection and start-disable, restart, interrupt enable/status/acknowledge, active status, per-counter state selection for counters 0 through 7, global monitor state/report count, clock enable, run-enable start/stop selectors, and low/high counter value readback.

`DCN_VM_CONTEXT0` through `DCN_VM_CONTEXT15` provide per-VMID display VM programming. Each context has page-table depth/block-size control, page-table base address high/low, logical start address high/low, and logical end address high/low. The chunk also includes default fault address high/low, VM fault control, fault status with context/client/read/write/walker/fault-type fields, and fault address high/low.

`HUBP0` covers the first hub pipe's surface format and request-size programming. It includes surface pixel format/alpha/rotation/h-mirror and DCC/tiling metadata, address configuration (`NUM_PIPES`, `NUM_BANKS`, `PIPE_INTERLEAVE`, `NUM_SE`, `NUM_RB_PER_SE`, `MAX_COMPRESSED_FRAGS`), tiling configuration (`SW_MODE`, `META_LINEAR`, `PIPE_ALIGNED`), primary/secondary viewport start/dimension for luma and chroma, request-size configuration for data/meta/DPTE chunks and swath heights, HUBP control/status bits such as blank enable, TTU disable, underflow status/clear, no-outstanding-requests, VTG select, disable, and in-blank, plus HUBP clock and measurement controls.

`HUBPREQ0` defines the first pipe's memory-request programming surface. It contains pitch and meta pitch for luma/chroma; VMID selection; primary/secondary data and metadata surface addresses for luma/chroma; TMZ and DCC enable/metadata fields in surface control; flip-control bits for flip type, stereo sync, pending state, update lock, earliest-in-use tracking, and flip interrupt status/clear/mask; expansion modes for DRQ/PRQ/MRQ/CRQ; TTU QoS watermarks and global/surface/cursor TTU controls; DMDATA VM control; VM aperture and L1 TLB controls; blank offsets; destination/scaler dimensions; prefetch, vblank, flip, nominal, and per-line delivery parameters; cursor delivery settings; reference-to-pixel frequency ratio; destination Y delta request limit; and HUBPREQ memory power state.

`HUBPRET0` describes the return/read side of the first hub pipe. It includes DET buffer base addresses, crossbar source selection for color components, stereo and first-line pairing fields, memory power control/status, read-line control/line registers, interrupt status/clear/mask/type fields for read line and read line compare events, and read-line value/status flags that distinguish vblank/inside/outside state for two programmable read lines.

`CURSOR0_0` describes cursor plane 0 for pipe 0. It includes cursor enable, magnification, mode, TMZ, pitch, rotation/mirroring bypass, lines per chunk, perfmon latency measurement controls, surface address high/low, size, position, hot spot, stereo offsets, destination X offset, cursor memory power control/status, and DMDATA address/control/QoS/status/software data fields. The DMDATA fields program auxiliary display metadata delivery, including update/repeat/mode/size, QoS level/deadline delta, done/underflow/clear status, and software-supplied data.

`DC_PERFMON6` begins at the end of the chunk. The requested range includes its counter control, counter-control2, per-counter state register, and the start of global perfmon control. The later `DC_PERFMON6` value and auxiliary registers continue after line 9864 and are owned by the next chunk.

## Control Flow And State Behavior

There is no direct control flow in this header. The effective flow is compile-time expansion: a driver-specific register list chooses an instance and register name, the offset header resolves its MMIO address, and this mask header resolves the fields used by helper macros to read, update, or write the register. At runtime the display driver writes memory-mapped registers in hardware-defined sequences for modesets, flips, cursor updates, audio setup, VM context setup, power management, and diagnostics.

The state described here persists in hardware registers until changed by the driver, DMUB firmware, reset logic, power-management logic, or the hardware block itself. Configuration state includes audio DTO values, DMA coherency/isochronous policy, hubbub watermarks, VM page-table bounds, surface addresses, tiling metadata, viewport geometry, TTU/prefetch parameters, cursor addresses, and memory-power force/disables. Live status includes flip pending/in-use addresses, underflow flags, no-outstanding-request state, memory power states, timeout status, fault status, read-line status, counter activity, CRC results, and perfmon values.

Some fields use event or acknowledge semantics rather than plain storage. Names containing `*_STATUS`, `*_INT_STATUS`, `*_INT_ACK`, `*_CLEAR`, `*_UNDERFLOW_CLEAR`, `*_FAULT_CLEAR`, and `*_EVENT_CLEAR` indicate fields that can be set by hardware and cleared or acknowledged by software. Confusing a status mask with a clear/ack mask can alter interrupt behavior or hide the evidence needed for diagnosing display faults.

Several groups are timing-sensitive. HUBPREQ prefetch, vblank, flip, nominal, TTU, and per-line-delivery registers are programmed relative to scanout timing and watermarks. HUBPRET read-line interrupts are line-position based. Cursor position/hotspot and DMDATA delivery must align with active planes and VM configuration. Audio DTO and cyclic-buffer fields affect stream rate and buffer-position reporting. VM fault and aperture state must be established before display memory requests are allowed to consume GPU virtual addresses.

## Dependencies And Integration Points

The chunk depends on the generated DCN 3.0.1 register database. It must stay aligned with `dcn_3_0_1_offset.h`; a mask with a stale offset can write a correct field layout into the wrong register, and a correct offset with a stale mask can corrupt neighboring fields. It also depends on the local display register-helper macros that concatenate register and field names exactly as generated here.

Audio integration is through `display/dc/dce/dce_audio.h` and `display/dc/dce/dce_audio.c`. The audio code uses `SRI(AZALIA_F0_CODEC_ENDPOINT_INDEX, AZF0ENDPOINT, id)` and the corresponding `AZALIA_ENDPOINT_REG_INDEX`/`AZALIA_ENDPOINT_REG_DATA` masks to implement indirect codec register access. Higher-level audio functions use the indexed Azalia register path for HBR, lipsync, hot-plug control, speaker/channel descriptors, sink info, power states, and stream format capability programming.

HUBP integration is through the hub pipe register lists in `display/dc/hubp/dcn10/dcn10_hubp.h` and later ASIC-specific variants. The mask list maps many fields from this chunk into `struct dcn_hubp*` shift/mask tables. Runtime hubp code then programs surface format, tiling, pitch, addresses, flip control, viewport, request sizes, DCC/TMZ state, VM/TLB settings, TTU/deadline parameters, blanking, underflow handling, cursor, and read-line behavior.

DCHUBBUB integration is through resource initialization, including `display/dc/resource/dcn30/dcn30_resource.c`, which builds `hubbub_reg`, `hubbub_shift`, and `hubbub_mask` from `HUBBUB_REG_LIST_DCN30` and `HUBBUB_MASK_SH_LIST_DCN30`. This connects the chunk to bandwidth/watermark programming, self-refresh and DRAM clock-change gating, timeout detection, hubbub CRC/debug state, soft reset, clock control, host-VM controls, and fabric monitoring.

VM integration is through `display/dc/dcn20/dcn20_vmid.h`, which uses the `DCN_VM_CONTEXT0_*` masks and shifts as the field-template for all VM contexts. The context instances in this chunk provide the per-VMID page table base/start/end state used by display memory requests, while default/fault registers expose fault recovery and debugging information.

DMUB integration is explicit in `display/dmub/src/dmub_dcn301.c`, which includes this header and emits DMUB service field arrays via `FD_MASK` and `FD_SHIFT`. Cursor state is also mirrored in DMUB command structures (`display/dmub/inc/dmub_cmd.h`) with fields matching names such as `CURSOR0_0_CURSOR_SURFACE_ADDRESS`, `CURSOR0_0_CURSOR_SIZE__CURSOR_WIDTH`, and `HUBPREQ0_CURSOR_SETTINGS__CURSOR0_DST_Y_OFFSET`.

## Risks And Edge Cases

The main risk is generated metadata drift. A wrong shift or mask can silently pack values into the wrong bit positions, which is especially dangerous for MMIO because failures may appear as display corruption, underflow, missed interrupts, lost audio, VM faults, or power-management instability rather than as compile errors.

Partial-block ownership is important for reconciliation. This chunk starts after the beginning of `DC_PERFMON4` and ends before the completion of `DC_PERFMON6`; any final per-file report should describe those perfmon blocks as spanning neighboring chunks. In contrast, most Azalia endpoint/index windows, `DC_PERFMON5`, the VM context array, and the pipe-0 HUBP/HUBPREQ/HUBPRET/cursor fields are materially represented here.

Instance replication is another source of mistakes. Azalia endpoint and input endpoint blocks repeat 0 through 7, streams repeat 8 through 15, VM contexts repeat 0 through 15, and HUBP-style fields are normally repeated for multiple pipes even though this chunk covers pipe 0. A generation error in one instance can be missed if only instance 0 is exercised; a driver assuming all instances are identical can also be wrong when later chunks or ASIC variants add or remove fields.

Status and clear fields are adjacent in several registers. Examples include HUBP underflow status/clear, HUBPREQ flip interrupt status/clear, HUBPRET read-line interrupt status/clear/mask/type, perfmon interrupt status/ack, DMDATA underflow/clear, timeout interrupt status/ack, and VM fault status/control. Incorrect use can either leave interrupts storming or clear diagnostic state before it is captured.

Address and VM fields are width-sensitive. Surface addresses are split into low/high fields, VM context start/end fields are split into high/low logical page-number pieces, and aperture or local-memory bounds are represented in multiple registers. Callers must preserve alignment, high-bit placement, and context selection; truncation or stale high halves can redirect scanout requests to the wrong memory.

Timing and bandwidth fields are mode-dependent. Hubbub watermarks, TTU controls, prefetch/vblank/flip/nominal parameters, per-line delivery, and DRAM/self-refresh clock-change controls must match the active mode set, memory clock behavior, DCC use, cursor use, and multi-plane composition. Bad values can cause underflow only under specific refresh rates, plane formats, scaling ratios, or power states.

Audio fields combine indexed codec access with DMA and DTO state. Incorrect endpoint indices, stream index/data handling, DTO phase/module, non-snoop/isochronous policy, cyclic-buffer sync, or HDA memory-power controls can manifest as silent audio, drift, buffer-position errors, or codec enumeration problems.

## Test Signals

Build-time signals are missing-symbol or initializer errors in AMD display modules that consume generated masks and shifts. High-signal failures would mention `SF`, `HUBP_SF`, `HWS_SF`, `DMUB_SF`, `FD_MASK`, `FD_SHIFT`, `REG_FIELD`, or a missing `*_MASK`/`__SHIFT` identifier from this chunk.

Runtime display validation should include modeset and page-flip tests on DCN 3.0.1-class hardware, with attention to HUBP0 scanout, DCC/TMZ surfaces, luma/chroma planes, scaling, viewport changes, cursor enable/move/resize, and flip interrupt delivery. Useful symptoms are absence of HUBP underflow, no stuck surface flip pending bit, correct in-use and earliest-in-use addresses, advancing frame/line state, and no unexpected timeout interrupts.

Memory/VM validation should exercise VMID setup across multiple contexts, GPU virtual-address scanout, fault injection or bad-address handling where available, and register dumps of fault context/client/read/write/walker fields. Correct behavior includes valid page-table bounds, no false VM faults during normal scanout, and clear fault status after expected recovery paths.

Bandwidth and power-management validation should cover memory clock changes, self-refresh entry/exit, low-power memory states, watermark set changes, and high-bandwidth multi-plane modes. Signals include stable display during pstate transitions, no DCHUBBUB timeout interrupt, expected memory power status, and no underflow when cursor/DMDATA and chroma planes are active.

Audio validation should cover HDMI/DP audio enumeration, supported sample rates and formats, HBR/lipsync/speaker allocation programming, stream start/stop, cyclic-buffer position reporting, and suspend/resume or display hotplug. Failures in the Azalia masks commonly show up as lost codec endpoint access, wrong stream descriptors, or unstable audio timing.

Perfmon and diagnostic validation should include reading `DC_PERFMON4/5/6` counters, checking counter interrupt/ack behavior, using DCHUBBUB CRC capture where supported, and verifying HUBPRET read-line interrupt/status behavior at programmed lines. Because these are generated register masks, the strongest regression signal is a combination of hardware register-database diffing, compile coverage for all generated field names, and smoke tests that touch the audio, hubbub, VM, HUBP, cursor, and perfmon paths represented by the chunk.

### subset-b-001726: lines 9865-12377

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_1_sh_mask.h lines 9865-12377

## Purpose

This chunk is generated AMD DCN 3.0.1 register field metadata. It contains no executable C logic; it publishes `#define` constants for field shifts and field masks used to compose or extract MMIO register fields for Vangogh/DCN301 display hardware.

The requested range starts in the tail of the `DC_PERFMON6` block, then covers replicated HUBP pipeline metadata for display pipe instances 1 and 2, and begins the same metadata for instance 3. The covered blocks include:

- `DC_PERFMON6`, `DC_PERFMON7`, and `DC_PERFMON8` performance monitor controls, counter state, counter readback, interrupt status, and counter-offset interrupt fields.
- `HUBP1`, `HUBP2`, and `HUBP3` surface, viewport, request-size, hub-pipe control, clock, debug, VM page-size, and performance-measurement fields.
- `HUBPREQ1`, `HUBPREQ2`, and most of `HUBPREQ3` request-side surface address, pitch, VMID, DCC/TMZ, flip, interrupt, in-use-address, TTU/QoS, VM/TLB, prefetch, vblank, flip, nominal delivery, cursor delivery, and memory-power fields.
- `HUBPRET1` and `HUBPRET2` return-side DET buffer, crossbar, memory-power, read-line, vblank/read-line interrupt, and read-line status fields.
- `CURSOR0_1` and `CURSOR0_2` cursor surface, size, position, hot spot, stereo, memory power, display metadata, software metadata, QoS, and underflow/status fields.

Although the repository path is under a local `ceph-client` mirror, this file is AMDGPU display-driver hardware metadata. It is unrelated to Ceph protocol or distributed filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, includes, allocations, or locks in this chunk. The public interface is the generated macro namespace:

- `<REGISTER>__<FIELD>__SHIFT`: bit offset of a named field within a 32-bit hardware register.
- `<REGISTER>__<FIELD>_MASK`: bit mask for the same named field.

The shift/mask pairs are intended to match the register offsets in `dcn_3_0_1_offset.h`. Runtime code uses token-pasting helper macros to bind field names into typed register tables. In `dcn301_resource.c`, `HUBP_MASK_SH_LIST_DCN30(__SHIFT)` and `HUBP_MASK_SH_LIST_DCN30(_MASK)` populate `struct dcn_hubp2_shift` and `struct dcn_hubp2_mask` for all HUBP instances. In DMUB code, `FD_SHIFT(reg, field)` and `FD_MASK(reg, field)` from `dmub_reg.h` expand directly to these symbols.

Notable field groups in this range:

- Surface geometry and memory layout: `SURFACE_PIXEL_FORMAT`, `ROTATION_ANGLE`, mirror/alpha enable, tiling `SW_MODE`, `DIM_TYPE`, `META_LINEAR`, pipe alignment, primary/secondary viewport starts and dimensions, and luma/chroma request-size fields such as swath height, chunk size, meta chunk size, DPTE group size, and VM group size.
- HUBP runtime control: blanking, disable, VTG select, vready, timeout status/clear/interrupt enable, underflow status/clear, outstanding-request status, TTU disable/mode, clock enable/gating/status, VMPG size, debug, and DCFCLK/DPPCLK measurement-window controls.
- Surface addressing and protection: primary/secondary luma and chroma base addresses, high address halves with VMID bits, meta-surface addresses, `PRIMARY_SURFACE_TMZ`, `SECONDARY_SURFACE_TMZ`, DCC enable, and DCC independent-block fields.
- Flip and interrupt handling: update lock, flip type, vupdate skip count, pending status, stereo-sync fields, GSL enable/mask, triple buffering, pending minimum time, flip/flip-away interrupt mask/type/clear/occurred/status fields, and current/earliest in-use address snapshots.
- TTU, QoS, VM, and delivery timing: expansion modes for data/chroma/meta/page requests, low/high QoS watermarks, global TTU controls, fixed QoS and ramp disable fields for surface and cursor traffic, DMDATA VM fault/underflow/late/done status, system aperture, L1 TLB control, blank offsets, destination timing, prefetch ratios, vblank/flip/nominal PTE/meta/VM request timing, per-line delivery, and ref-frequency-to-pixel-frequency fields.
- Return and cursor blocks: HUBPRET DET base/crossbar, memory-power force/disable/status, read-line windows and vblank/read-line interrupts; cursor enable/mode/TMZ/pitch/position/size/hotspot/stereo, CROB memory power, DMDATA address/control/QoS/status/software-data fields.

## Control Flow

This header has no runtime control flow. Runtime sequencing is supplied by the display driver:

1. DCN301 resource and DMUB code include `dcn_3_0_1_offset.h` and this matching `dcn_3_0_1_sh_mask.h`.
2. Resource table macros paste register names and instance IDs into symbols such as `HUBP2_DCSURF_SURFACE_CONFIG__SURFACE_PIXEL_FORMAT_MASK` or `HUBPREQ1_DCSURF_FLIP_CONTROL__SURFACE_FLIP_PENDING__SHIFT`.
3. Driver code stores the resulting shifts and masks in block-specific tables and later uses helpers such as `REG_SET`, `REG_UPDATE`, `REG_GET`, `REG_SET_N`, and `REG_UPDATE_N` to update individual hardware fields.
4. Higher-level display paths sequence the writes around modesets, plane updates, flips, cursor updates, memory-power transitions, VM/TLB programming, QoS/watermark programming, and interrupt handling.

The macros do not encode required ordering. For example, the presence of fields for surface addresses, DCC/TMZ, update locks, flip pending status, and interrupt clear bits does not itself enforce the ordering needed to avoid tearing, underflow, stale metadata, or missed interrupts.

## State And Persistence Behavior

The chunk stores no software state and persists nothing. It describes hardware state in memory-mapped display registers.

State represented by these fields includes:

- Per-HUBP plane configuration: pixel format, rotation, mirroring, alpha plane enablement, tiling, viewport geometry, request sizes, VTG binding, blank/disable state, clock state, underflow/timeout status, and debug/measurement windows.
- Per-HUBPREQ fetch/request state: primary/secondary luma/chroma and metadata addresses, VMIDs, VM system aperture, L1 TLB mode, DCC/TMZ controls, flip state, in-use address reporting, TTU/QoS parameters, prefetch/vblank/flip/nominal timing, and request memory-power state.
- Per-HUBPRET return state: DET buffer allocation, component crossbar routing, internal memory power, read-line windows, read-line snapshots, vblank state, and read-line interrupt state.
- Per-cursor state for cursor 0 on pipes 1 and 2: cursor enable/mode, address, size, position, hot spot, stereo offset, TMZ, CROB memory power, DMDATA addressing/control/QoS/status, and software-injected DMDATA.
- Perfmon state: selected performance counters, start/stop controls, high/low counter readback, current counter value, interrupt status/ack bits, and counter offset behavior.

Persistence is hardware-defined. Configuration fields generally retain their programmed value until modeset reprogramming, plane disable, power gating, suspend/resume, or ASIC reset. Status, interrupt, counter, clear, ack, underflow, timeout, pending, and power-status fields may be read-only, sticky, self-clearing, write-one-to-clear, or update only at display timing boundaries. This generated header does not distinguish those semantics; consuming code and hardware documentation must.

## Dependencies And Integration Points

This chunk must stay synchronized with:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_1_offset.h`, which provides the matching `mm...` register offsets and `_BASE_IDX` constants.
- DCN301 base-address definitions from `vangogh_ip_offset.h`, consumed through `BASE(mm..._BASE_IDX)`.
- DCN shared register-list macros from the AMD display stack, especially the HUBP/HUBPREQ/HUBPRET/CURSOR lists used by DCN 3.0 and reused by DCN301.

Direct include sites in this tree are:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn301/dcn301_resource.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn301.c`

`dcn301_resource.c` constructs `hubp_regs[]`, `hubp_shift`, and `hubp_mask` tables through `HUBP_REG_LIST_DCN30(id)` and `HUBP_MASK_SH_LIST_DCN30(...)`; those tables drive plane, cursor, VM, flip, watermark, underflow, and power-management code in the DC display core. `dmub_dcn301.c` includes this header so DMUB register helpers can derive field masks and shifts through `FD_MASK` and `FD_SHIFT` when programming common DMUB-facing DCN301 registers.

The repeated instance names matter. Instance 1 and 2 blocks are complete in this range; instance 3 starts at `HUBP3` and reaches `HUBPREQ3_REF_FREQ_TO_PIX_FREQ` at the final requested line, so later chunks are required for the rest of pipe 3.

## Risks And Edge Cases

- Generated mask drift is high impact. A wrong shift or mask can compile cleanly but silently update the wrong bits in a display register.
- Register-offset and mask headers are a pair. If `dcn_3_0_1_offset.h` and this header come from different generator revisions, the driver may address the intended register while applying fields from a different layout.
- Repeated pipe instances are copy-sensitive. `HUBP1`, `HUBP2`, and `HUBP3` are structurally similar, but an instance-specific typo can affect only one plane or only multi-display configurations that allocate that pipe.
- Bitfield width errors can corrupt neighboring controls. Examples in this range include packed address-high plus VMID fields, DCC/TMZ control bits, flip interrupt mask/type/clear/status fields, QoS levels, and underflow/timeout clear bits.
- Clear/ack/status fields are side-effect-sensitive. Misusing perfmon interrupt ack, flip clear, DMDATA underflow clear, HUBP underflow clear, timeout clear, or HUBPRET interrupt clear bits can lose diagnostic state or leave interrupts stuck.
- Plane update timing is fragile. Incorrect update-lock, flip-pending, in-use-address, triple-buffering, GSL, prefetch, vblank, flip, nominal, or per-line-delivery fields can cause tearing, black frames, missed flips, underflow, or failures that appear only at high bandwidth.
- VM, DCC, TMZ, and meta-surface fields cross security and memory-management boundaries. Incorrect masks can fetch from the wrong VMID, mark protected memory incorrectly, break DCC metadata reads, or cause page-table/request faults.
- Power fields may be ignored or harmful when clocks/resets are not in the expected state. The memory-power and clock-control fields require sequencing by higher-level power-management code.
- Chunk boundaries are artificial. The range begins after the start of `DC_PERFMON6_PERFMON_CNTL` and ends at the declaration comment for `HUBPREQ3_REF_FREQ_TO_PIX_FREQ`; adjacent chunks are needed for full-file completeness.

## Test Signals

Useful validation combines generated-header checks with display hardware behavior:

- Build AMDGPU/DC with DCN301 support enabled. Missing or renamed field macros should fail in `dcn301_resource.c`, DMUB register table construction, and shared HUBP/HUBPREQ/HUBPRET/CURSOR register-list users.
- Mechanically verify that each `__SHIFT` macro in lines 9865-12377 has a matching `_MASK` macro for the same `<REGISTER>__<FIELD>` where the source defines both, and diff the chunk against AMD's authoritative DCN 3.0.1 generated register database.
- Cross-check this mask chunk against `dcn_3_0_1_offset.h` to ensure every register represented here has a matching offset/base-index definition.
- Exercise plane allocation across pipes 1, 2, and 3 with multi-monitor modesets, plane enable/disable, scaling, rotation, mirroring, alpha, luma/chroma formats, DCC-enabled surfaces, and protected/TMZ surfaces.
- Run flip and vblank tests that cover immediate and synchronized flips, update locks, stereo/GSL fields, triple buffering, flip interrupts, flip-away interrupts, and in-use-address reporting.
- Stress memory and timing paths with high-resolution/high-refresh modes, cursor movement, DMDATA updates, VM faults, page-table pressure, DCC metadata traffic, prefetch/watermark changes, and suspend/resume.
- Monitor kernel logs, debugfs counters, and display diagnostics for HUBP underflow, timeout, DMDATA underflow/late/fault, stuck flip pending, missed vblank/read-line interrupts, cursor corruption, blank frames, perfmon interrupt issues, and resume failures.

## Cross-Chunk Notes

The previous chunk owns the beginning of `DC_PERFMON6_PERFMON_CNTL` and earlier DCN301 register-field metadata. Later chunks continue after `HUBPREQ3_REF_FREQ_TO_PIX_FREQ` and are needed to complete the pipe 3 HUBPREQ/HUBPRET/CURSOR/perfmon material and the rest of `dcn_3_0_1_sh_mask.h`. The final per-file research document should merge adjacent chunks before making whole-file claims about all HUBP instances or all DCN301 display register fields.

### subset-b-001727: lines 12378-14892

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_1_sh_mask.h lines 12378-14892

## Purpose

This chunk is generated AMD DCN 3.0.1 register field metadata. It contains no executable C logic; it publishes preprocessor constants for bit shifts and masks used when AMDGPU display code reads or updates MMIO registers with helper macros such as `REG_UPDATE`, `REG_SET`, `REG_GET`, `HUBP_SF`, and `TF_SF`.

The requested range contains 2,115 `#define` lines covering 374 register names. It starts in the tail of the `HUBPREQ3` request block, then covers the full `HUBPRET3` return/control block, `CURSOR0_3` cursor and DMDATA registers, `DC_PERFMON9`, and the beginning of the DPP0 pipe: `DPP_TOP0`, `CNVC_CFG0`, `CNVC_CUR0`, `DSCL0`, `CM0`, and the first `DC_PERFMON10` control/state fields. The boundaries are artificial: the first visible macro is paired with a `HUBPREQ3_REF_FREQ_TO_PIX_FREQ` comment from the previous line context, and the final line stops inside `DC_PERFMON10_PERFCOUNTER_STATE`.

Although the path sits under a local `ceph-client` source mirror, this file is AMDGPU display-controller hardware metadata, not Ceph or distributed filesystem code.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, includes, allocation paths, or locks in this range. The interface is the generated macro naming convention:

- `<REGISTER>__<FIELD>__SHIFT`: low-bit position for a hardware field.
- `<REGISTER>__<FIELD>_MASK`: field bitmask for a 32-bit MMIO register value.
- Block comments such as `// addressBlock: dce_dc_dpp0_dispdec_cm_dispdec`: generated register-database grouping hints.

Major macro families in this slice:

- `HUBPREQ3_*`: tail fields for HUBP request-side timing and memory power state, including `REF_FREQ_TO_PIX_FREQ`, DRQ limits, DPTE/MPTE/META/PDE memory power force/disable/status, and VM/PTE/meta chunk timing for vblank and flip paths.
- `HUBPRET3_*`: return-side DET buffer base and component crossbar control, DET/DMROB/PIXCDC memory power control/status, read-line interval/window/status registers, and vblank/read-line interrupt mask/type/clear/status fields.
- `CURSOR0_3_*`: cursor enable, magnification, mode, TMZ, pitch, size, position, hot spot, stereo control, destination offset, cursor memory power, surface address high/low pieces, and display metadata (`DMDATA`) address/control/QoS/status/software-data fields.
- `DC_PERFMON9_*`: HUBP-local performance counter control, counter state selection, global perfmon enable/reset/state, interrupt/mask/clear controls, manual trigger, overflow/counter status, and high/low counter value registers.
- `DPP_TOP0_*`: DPP top-level control, soft reset, CRC values/control, and host-read control.
- `CNVC_CFG0_*` and `CNVC_CUR0_*`: converter pixel format, format control, floating-point bias/scale, color keying, alpha LUT/pre-dealpha/pre-realpha, pre-CSC matrix and coefficient format, pre-degamma, and cursor color/scale-bias fields for DPP-side cursor handling.
- `DSCL0_*`: scaler coefficient RAM access, scaler mode/taps/2-tap controls, manual replicate, horizontal/vertical/chroma scale ratio and init fields, black color, update/autocal, overscan, OTG blanking windows, recout/MPC sizing, line-buffer format/memory/v-counter, DSCL memory power/status, and output-buffer control/memory power.
- `CM0_*`: color-management control, post-CSC and gamut-remap matrices, bias/HDR multiplier/dealpha/coefficient format, gamut-correction and blend-gamma LUT controls plus RAM A/B region tables, shaper LUT and RAM A/B region tables, color-management memory power/status, 3D LUT mode/index/data/read-write/output normalization/output offset-scale, and CM test-debug index/data fields.
- `DC_PERFMON10_*`: start of DPP-local performance counter control, counter control 2, and partial counter state field definitions.

## Control Flow

This header has no runtime control flow. Runtime sequencing is supplied by the DCN driver:

1. DCN 3.0.1 resource or DMUB code includes `dcn_3_0_1_offset.h` and this matching `dcn_3_0_1_sh_mask.h`.
2. Resource construction macros paste instance IDs into register names and pair offsets with field masks. In `dcn301_resource.c`, `hubp_regs(0..3)` uses `HUBP_REG_LIST_DCN30(id)`, while `hubp_shift` and `hubp_mask` are initialized with `HUBP_MASK_SH_LIST_DCN30(__SHIFT)` and `HUBP_MASK_SH_LIST_DCN30(_MASK)`.
3. The same file constructs DPP instances from `dpp_regs[inst]`, `tf_shift`, and `tf_mask`; DPP field lists in shared `dcn10`/`dcn20`/`dcn3` headers reference many `CNVC_CFG0`, `DSCL0`, and `CM0` masks from this chunk.
4. Runtime code then calls typed block methods such as HUBP cursor/DMDATA updates, DPP scaler programming, color-transform setup, LUT programming, CRC/perfmon reads, and power-management routines. Those methods use the generated shift/mask constants through register helpers.

The macros do not express ordering. Consumers must still sequence clock and power enablement, memory-power requests, cursor surface programming, DMDATA update toggles, scaler coefficient loads, double-buffered update points, color-LUT programming, interrupt clear/ack, and performance-counter start/stop behavior.

## State And Persistence Behavior

This chunk stores no software state and persists nothing by itself. It describes bit layouts for MMIO-backed display hardware state:

- HUBP request/return state: memory power force/disable/status for request-side page-table/meta memories, DET/DMROB/PIXCDC power state, request timing for vblank/flip, read-line windows, vblank/read-line interrupt state, and DET/crossbar configuration.
- Cursor and DMDATA state: cursor enable/mode/size/position/address, cursor memory power, trusted-memory-zone bit, cursor stereo controls, metadata address/control/QoS/status, and software-fed metadata data.
- DPP conversion/scaling/color state: input pixel format, dealpha/realpha, color keying, pre/post CSC matrices, gamut remap, scaler taps/ratios/init phases, line-buffer and output-buffer memory power, gamma/blend-gamma/shaper LUT RAM programming, 3D LUT control/data/output scaling, and debug selectors.
- Perfmon state: selected events, counted value type, run/interrupt/overflow controls, manual trigger, active/started flags, and low/high counter values.

Persistence is hardware-defined. Configuration fields generally remain until modeset, fast update, power gating, suspend/resume, or ASIC reset. Status, interrupt, clear, debug, power-state, and counter fields can be read-only, sticky, self-clearing, write-one-to-clear, or dependent on block clocks. This header only exposes bit positions; the consuming block code is responsible for preserving unrelated bits and respecting side effects.

## Dependencies And Integration Points

This chunk depends on AMD's generated DCN 3.0.1 register database and must stay synchronized with:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_1_offset.h`, which supplies the matching `mm...` register offsets and base-index constants.
- Shared DCN block headers that consume the generated symbols, including `dc/hubp/dcn30/dcn30_hubp.h`, `dc/hubp/dcn20/dcn20_hubp.h`, and `dc/dpp/dcn10/dcn10_dpp.h`.
- DCN301 resource construction in `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn301/dcn301_resource.c`, which includes this header and builds `hubp_shift`, `hubp_mask`, `tf_shift`, and `tf_mask` tables.
- DCN301 DMUB support in `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn301.c`, which includes the same offset/mask pair for firmware-facing register definitions.

The primary integration pattern is token-pasting. Shared block macros use instance-zero field names such as `CM0_CM_GAMUT_REMAP_CONTROL` or `DSCL0_SCL_MODE` for masks, while register lists use per-instance offsets such as `HUBPREQ3` or `CURSOR0_3` for concrete pipes. For DPP masks, instance-zero field layouts are shared across DPP instances; for HUBP instance 3, this chunk provides the concrete generated names that correspond to the fourth HUBP pipe's request, return, cursor, and perfmon registers.

## Risks And Edge Cases

- Mask/shift drift is the central risk. These constants are untyped preprocessor values, so a wrong shift or mask can compile and then silently modify the wrong bits in a hardware register.
- Generated instance naming is easy to misuse. `HUBPREQ3`, `HUBPRET3`, and `CURSOR0_3` are pipe-instance-specific names, while many DPP field lists intentionally use `CM0`, `DSCL0`, and `CNVC_CFG0` as canonical layouts. Treating those naming schemes as interchangeable can break only one pipe or only nonzero DPP instances.
- The chunk starts and ends mid-context. Adjacent chunks are required for complete `HUBPREQ3_REF_FREQ_TO_PIX_FREQ` context and for the remainder of `DC_PERFMON10_PERFCOUNTER_STATE` and later DPP perfmon fields.
- Power-control fields are sequencing-sensitive. Forcing or disabling DPTE/MPTE/META/PDE, DET, line-buffer, output-buffer, gamma, shaper, or 3D LUT memories at the wrong time can cause display corruption, underflow, stuck status bits, or ignored writes.
- Cursor and DMDATA paths have update semantics. Incorrect `DMDATA_UPDATED`, software update, repeat, size, address-high, QoS, or done-status fields can break HDR/static metadata updates, cursor-only updates, or low-latency metadata delivery.
- Scaler and color fields are visually high impact. Incorrect tap counts, init phases, ratios, CSC coefficients, gamma region offsets, shaper regions, or 3D LUT controls can produce blank output, bad colors, banding, clipping, scaling artifacts, CRC mismatches, or failures limited to specific formats.
- Perfmon and debug fields can perturb diagnostics. Bad event selection, counter control, interrupt clear, or debug write-enable masks can hide performance regressions or create interrupt/status noise.

## Test Signals

Useful validation is mostly generated-header consistency plus hardware behavior:

- Build AMDGPU/DC with DCN301 support enabled; missing or renamed macros should fail in `dcn301_resource.c`, DPP/HUBP register-table construction, and DMUB DCN301 register setup.
- Mechanically verify that every field in lines 12378-14892 has one `__SHIFT` and one `_MASK` macro where the generated schema expects a pair, and that masks align with the declared shifts without overlapping unrelated fields.
- Diff this chunk against AMD's authoritative DCN 3.0.1 register database and nearby generated headers such as `dcn_3_0_0_sh_mask.h` or later DCN 3.x headers where the hardware layout is expected to match.
- Exercise four-pipe configurations so HUBP instance 3 is active: multi-display modesets, cursor movement, cursor-only plane updates, DMDATA/HDR metadata updates, flip/vblank timing, read-line interrupts, and suspend/resume.
- Validate DPP0 image-processing behavior with format conversion, color keying, dealpha/realpha, pre/post CSC, gamut remap, degamma/gamma/blend-gamma, shaper, 3D LUT, scaling up/down, chroma scaling, overscan, and CRC capture.
- Stress power-management transitions: idle display, memory power gating/ungating, cursor updates during idle optimization, fast updates, full modesets, hotplug, and resume from low-power states.
- Use perfmon/debug paths to confirm counters start/stop, overflow/interrupt status behaves correctly, and selected events produce plausible values.
- Watch kernel logs and display diagnostics for underflow, VM/DMDATA faults, stuck interrupts, cursor corruption, metadata loss, color errors, scaler artifacts, CRC mismatch, and resume-only failures.

## Cross-Chunk Notes

Previous chunks own the earlier portions of `HUBPREQ3` and the rest of the generated DCN 3.0.1 mask namespace before line 12378. Later chunks continue `DC_PERFMON10_PERFCOUNTER_STATE` and the remaining DPP/perfmon field definitions. The final per-file research document should merge adjacent chunks before making complete claims about all HUBP3 request fields, all DPP0 color/scaler fields, or all DCN301 perfmon registers.

### subset-b-001728: lines 14893-17407

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_1_sh_mask.h lines 14893-17407

## Scope And Purpose

This chunk is a generated AMD DCN 3.0.1 register shift/mask header segment. It contains 2,115 preprocessor definitions: 1,052 `__SHIFT` constants and 1,063 `_MASK` constants for display pipe processor (`DPP`) register fields. There are no executable functions, types, global variables, runtime branches, or filesystem behavior in this source range.

The purpose of the chunk is to provide compile-time bitfield metadata for AMDGPU Display Core register helpers. The matching offset header, `dcn_3_0_1_offset.h`, supplies register addresses such as `mmDPP_TOP1_DPP_CONTROL`; this header supplies field layout constants such as `DPP_TOP1_DPP_CONTROL__DPP_CLOCK_ENABLE__SHIFT` and `DPP_TOP1_DPP_CONTROL__DPP_CLOCK_ENABLE_MASK`.

The slice starts in the tail of `DC_PERFMON10`, covers the complete DPP1 top, converter, cursor-converter, scaler, color-management, and `DC_PERFMON11` blocks, then enters DPP2 top and converter configuration before ending at the `CNVC_CFG2_PRE_DEGAM` marker. The final per-file report should merge adjacent chunks before treating `DC_PERFMON10` or DPP2 converter coverage as complete.

Although this file is under a `ceph-client` source mirror, this chunk is AMD GPU display register metadata. It does not implement Ceph, distributed filesystem logic, storage persistence, or network protocol behavior.

## Register Blocks Covered

The preamble finishes `DC_PERFMON10` with performance monitor control, run-enable start/stop selection, current-value interrupt status/ack bits, high/low counter readback, and read-select fields. The earlier counter-control and counter-state definitions for instance 10 begin before this chunk.

`dce_dc_dpp1_dispdec_dpp_top_dispdec` covers `DPP_TOP1_*` control, soft reset, CRC readback/control, and host read-rate control. These fields gate DPP clocks, request soft resets for CNVC/DSCL/CM/OBUF sub-blocks, configure CRC capture format/source/mask/stereo/interlace behavior, and expose CRC R/G/B/A result halves.

`dce_dc_dpp1_dispdec_cnvc_cfg_dispdec` covers `CNVC_CFG1_*` pixel converter configuration. It includes surface pixel format and alpha-plane enable, format expansion and channel crossbar controls, floating-point conversion bias/scale values, color keyer thresholds, alpha LUT, pre-dealpha, pre-CSC mode and coefficient matrices for banks A/B, coefficient format, pre-degamma mode/select, and pre-realpha.

`dce_dc_dpp1_dispdec_cnvc_cur_dispdec` covers `CNVC_CUR1_CURSOR0_*` cursor converter fields: cursor enable/mode/expansion, FP16 enable, color registers, and cursor floating-point scale/bias.

`dce_dc_dpp1_dispdec_dscl_dispdec` covers `DSCL1_*` scaler and line-buffer fields. It includes scaler coefficient RAM selection/data, scaler mode, tap counts, two-tap sharpness controls, manual replication, horizontal/vertical luma/chroma scale ratios and initial phases, black color, update/autocal controls, overscan, OTG blank windows, recout and MPC dimensions, line-buffer data format and memory layout, live vertical counter, DSCL memory power status/control, OBUF control, and OBUF memory power control.

`dce_dc_dpp1_dispdec_cm_dispdec` is the largest block in this chunk. It covers `CM1_*` color-management control, post-CSC matrices, gamut remap matrices, bias registers, GAMCOR and BLNDGAM programmable transfer functions with RAM A/B region metadata, HDR multiplier, dealpha, coefficient format, shaper LUT/RAM region programming, memory power controls and status, 3D LUT index/data/read-write controls and output normalization/offset, plus test debug index/data registers.

`dce_dc_dpp1_dispdec_dpp_dcperfmon_dc_perfmon_dispdec` covers full `DC_PERFMON11` counter control, selection, state, global perfmon control, interrupt, and readback registers for DPP1 diagnostics.

`dce_dc_dpp2_dispdec_dpp_top_dispdec` mirrors the DPP top fields for instance 2. `dce_dc_dpp2_dispdec_cnvc_cfg_dispdec` begins the DPP2 converter configuration block and is covered through `CNVC_CFG2_CNVC_COEF_FORMAT`; the final line is only the comment for `CNVC_CFG2_PRE_DEGAM`, with its field definitions continuing after this chunk.

## Important APIs, Types, And Macros

The exported API is the generated macro naming contract:

- `<REGISTER>__<FIELD>__SHIFT` gives the low bit position for a hardware field.
- `<REGISTER>__<FIELD>_MASK` gives the already-positioned 32-bit mask for that field.
- Instance prefixes in this chunk include `DPP_TOP1`, `CNVC_CFG1`, `CNVC_CUR1`, `DSCL1`, `CM1`, `DC_PERFMON10`, `DC_PERFMON11`, `DPP_TOP2`, and `CNVC_CFG2`.
- Address-block and register comments are documentation delimiters only; C code consumes the `#define` symbols.
- Names such as `CM1_CM_SHAPER_LUT_WRITE_EN_MASK__CM_SHAPER_LUT_WRITE_EN_MASK_MASK` are expected generated names where the hardware field itself includes `MASK`.

The main local consumer pattern is in the DCN 3.0 DPP register lists. `display/dc/resource/dcn301/dcn301_resource.c` builds `dpp_regs[]`, `tf_shift`, and `tf_mask` through `DPP_REG_LIST_DCN30(id)` and `DPP_REG_LIST_SH_MASK_DCN30(__SHIFT/_MASK)`. `display/dc/dpp/dcn30/dcn30_dpp.h` maps logical DPP registers to instance-prefixed symbols with `SRI(...)` and field metadata with `TF_SF(...)`/`TF2_SF(...)`; those lists include the converter, cursor converter, scaler, color management, memory-power, and DPP control fields represented in this chunk.

Runtime code reaches these constants through register helpers such as `REG_SET`, `REG_UPDATE`, `REG_GET`, `REG_READ`, and `REG_WAIT`, plus transfer-function helpers that copy field shifts and masks into color-management programming structures.

## Functional Areas

Pixel conversion fields in `CNVC_CFG1` and the start of `CNVC_CFG2` describe how scanout surface data is interpreted before scaling and color management. Important field groups include pixel format, alpha-plane enable, 16-bit conversion, alpha enable, converter bypass and MSB alignment, positive clamping, RGB crossbar selection, FP bias/scale, color-key thresholds, 2-bit alpha LUT, pre-dealpha/pre-realpha, pre-CSC bank selection/current-state readback, pre-CSC coefficient matrices, and pre-degamma mode/select.

Cursor converter fields provide the DPP-local cursor conversion layer. They control cursor mode, expansion, enable, floating-point conversion enable, two cursor colors, and FP scale/bias. These fields integrate with cursor attribute programming in DPP code, while broader cursor fetch/address controls live in other cursor blocks and chunks.

Scaler fields in `DSCL1` drive the digital scaler and line buffer. Coefficient RAM fields select tap pairs, filter phase, filter type, and even/odd tap coefficients. Mode/tap/2-tap fields select scaler mode, luma/chroma coefficient RAM behavior, tap counts, boundary behavior, and 2-tap sharpening. Ratio/init fields program luma/chroma horizontal and vertical scale ratios and initial phases, including bottom-field values for interlaced paths. Output geometry fields define recout start/size, MPC size, overscan, and OTG blank reference windows.

Color-management fields in `CM1` describe the DPP color pipeline around post-CSC, gamut remap, programmable gamma correction (`GAMCOR`), blend gamma (`BLNDGAM`), shaper LUT, 3D LUT, HDR multiply, coefficient format, and dealpha. GAMCOR, BLNDGAM, and SHAPER use RAM A/B banks with LUT index/data windows plus many region start/end/base/slope/offset fields. The driver can program an inactive bank, switch selection, and read current mode/select state through adjacent control fields.

Power and clock fields include DPP top clock-enable/gating-disables, per-sub-block soft reset, DSCL/OBUF memory power force/disable/status fields, and CM memory power controls/status for GAMCOR, BLNDGAM, SHAPER, and 3D LUT memory. These are used by DPP initialization, power optimization, and suspend/resume paths.

Diagnostic fields include DPP CRC control/readback, host read-rate control, CM test debug index/data, and DC performance monitors. The perfmon registers expose event and increment selection, counted value selection, run-enable state, per-counter state selection, overflow/threshold interrupt controls, current-value interrupt status/ack bits, and high/low counter readback.

## Control Flow

This header has no local control flow. The effective flow is compile-time symbol expansion:

1. DCN 3.0.1 sources include `dcn_3_0_1_offset.h` and `dcn_3_0_1_sh_mask.h`.
2. Register-list macros select a DPP instance and paste names such as `CM1_CM_GAMCOR_CONTROL` or `DSCL1_SCL_MODE` into address tables.
3. Field-list macros paste instance-0 field names into shared shift/mask tables because replicated DPP instances have the same field layout.
4. Runtime DPP, color-management, cursor, scaler, and power code writes or reads fields through common MMIO helpers.

The runtime sequencing is external to this header. Typical flows set surface pixel format, converter/pre-CSC state, scaler geometry and coefficients, color-management LUTs/matrices, cursor conversion state, and memory-power controls during modeset, plane update, color update, cursor update, or power transition.

## State And Persistence Behavior

The file itself stores no state. Its macros describe memory-mapped DCN hardware state that persists while the display controller block remains powered and until driver, firmware, reset, or hardware logic changes it.

Persistent configuration state represented here includes converter format and alpha settings, color keyer bounds, pre-CSC/post-CSC/gamut matrices, scale ratios and coefficients, recout/MPC geometry, LUT region metadata, 3D LUT normalization and offsets, clock gating overrides, soft reset controls, and memory power force/disable settings.

Live or latched status state includes `*_CURRENT` mode/select fields, DSCL line-buffer and memory-power status, vertical counter readback, CRC result registers, perfmon counter values, perfmon interrupt status bits, and per-counter state fields. Fields named `*_ACK`, `*_STATUS`, `*_PENDING`, `*_CURRENT`, `*_STATE`, or `*_READ_*` should not be treated as ordinary writable configuration just because this header exposes their bit layout.

Several field groups have implicit double-buffering or bank-selection behavior. GAMCOR, BLNDGAM, SHAPER, pre-CSC, post-CSC, and gamut-remap bank A/B fields must be coordinated with mode/select/current fields so a partially programmed LUT or matrix is not made active. Memory power fields must be sequenced with use of the corresponding LUT RAMs; forcing memory off while a block is active can produce visible color errors or hangs waiting for status.

## Dependencies And Integration Points

This chunk depends on the DCN 3.0.1 register contract and must match `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_1_offset.h`. Offset and mask headers must evolve together; a correct mask paired with a wrong address is still an incorrect MMIO operation.

Observed include and integration points include:

- `display/dmub/src/dmub_dcn301.c`, which includes both DCN 3.0.1 offset and shift/mask headers for DMUB register access.
- `display/dc/resource/dcn301/dcn301_resource.c`, which instantiates DPP register, shift, and mask tables using DCN30 DPP macros.
- `display/dc/dpp/dcn30/dcn30_dpp.h`, which names the DPP registers and fields covered here in `DPP_REG_LIST_DCN30_COMMON`, `DPP_REG_LIST_DCN30`, and `DPP_REG_LIST_SH_MASK_DCN30_COMMON`.
- `display/dc/dpp/dcn30/dcn30_dpp.c`, which programs pre-degamma, format control, surface pixel format, cursor conversion, DSCL memory power, and snapshots DPP/DSCL state.
- `display/dc/dpp/dcn30/dcn30_dpp_cm.c`, which programs GAMCOR LUT RAMs, gamut-remap matrices, transfer-function region descriptors, memory power, and related current-state fields.

The hardware integration points are the DPP pipeline stages: CNVC input conversion, CNVC cursor conversion, DSCL scaling/line buffering, CM color processing, DPP top-level clock/reset/CRC, and per-DPP performance monitoring.

## Risks And Edge Cases

Wrong shifts or masks compile cleanly but can silently corrupt display programming. High-risk fields include color matrices and LUT region descriptors, bank-select/current fields, memory-power force/disable bits, scaler ratios/initial phases, coefficient RAM selection/data, soft reset bits, CRC controls, and perfmon interrupt acknowledge fields.

Chunk boundaries split logical blocks. `DC_PERFMON10` is only a tail in this range, and `CNVC_CFG2_PRE_DEGAM` begins at the last line with no field definitions in the chunk. A final report should not claim complete DPP2 converter coverage from this file range alone.

Replicated instance names are easy to mix. DPP1 is complete here, DPP2 is partial, and shared field-mask tables often use instance-0 field names because field layouts are replicated. Manually substituting prefixes can break either address selection or field-table initialization.

Status and acknowledge bits are adjacent in perfmon and CRC-related registers. Confusing `*_STATUS`, `*_ACK`, `*_INT_EN`, `*_INT_TYPE`, or readback fields can leave interrupts stuck, clear diagnostic state unexpectedly, or report stale counter values.

Color pipeline fields require bank and memory sequencing. Programming `GAMCOR`, `BLNDGAM`, `SHAPER`, or 3D LUT data while the wrong bank is selected, while memory is powered down, or while current-mode readbacks are ignored can cause partial transfer functions to become visible.

Scaler fields are mode-sensitive and packed into limited-width fixed-point fields. Overwide or unvalidated mode-derived values for ratios, initial phases, blank windows, recout sizes, MPC sizes, or tap counts will be masked and can produce unintended scaling, clipping, underflow, or display corruption that only appears for particular formats or resolutions.

Generated names with full-width masks such as `0xFFFFFFFFL` should stay within existing 32-bit register helper paths. Ad hoc signed arithmetic or width changes around these constants can introduce subtle packing bugs.

## Test Signals

Build-time signals include successful compilation of DCN301 Display Core and DMUB sources that include `dcn_3_0_1_sh_mask.h`. Missing, renamed, or mismatched symbols should surface around `DPP_REG_LIST_DCN30`, `DPP_REG_LIST_SH_MASK_DCN30`, `TF_SF`, `TF2_SF`, `REG_SET`, `REG_UPDATE`, or `REG_GET` expansions.

Static generated-header validation should check that each intended field has both shift and mask constants, masks align with shifts and widths, replicated DPP instance layouts are consistent where the hardware spec says they should be, and all registers in this chunk have matching addresses in `dcn_3_0_1_offset.h`.

Runtime validation should exercise modesets and plane updates on DCN 3.0.1-class hardware across DPP instances, including different pixel formats, alpha-plane enablement, cursor conversion, color keying, scaling up/down, chroma formats, overscan/recout changes, and MPC sizing.

Color-management tests should cover pre-CSC/post-CSC/gamut-remap programming, GAMCOR and BLNDGAM RAM A/B updates, shaper LUT updates, 3D LUT programming, HDR multiplier behavior, bank switching, current-mode readbacks, and suspend/resume with LUT memory power transitions.

Diagnostic tests should cover DPP CRC capture and readback, CM debug index/data reads, perfmon counter setup/readback/interrupt acknowledgement, DSCL vertical counter readback, memory power status convergence, and absence of underflow, blanking, or visible color/scaling artifacts after repeated modesets and color updates.

## Chunk Notes

This is generated register metadata rather than algorithmic code. The main research value for the merge lane is the hardware coverage map: DPP1 converter, cursor conversion, scaler, color-management/LUT, memory-power, CRC, and perfmon field definitions, plus the beginning of DPP2 top/CNVC metadata. The merge lane should combine this with neighboring chunks before describing complete file-level coverage for `dcn_3_0_1_sh_mask.h`.

### subset-b-001729: lines 17408-19930

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_1_sh_mask.h lines 17408-19930

## Purpose

This chunk is generated AMD DCN 3.0.1 display-controller register field metadata. It contains no executable C logic; it publishes preprocessor constants for bit shifts and masks used to pack and unpack fields in DCN 3.0.1 MMIO registers. Consumers include this header with `dcn_3_0_1_offset.h` so register-table code can combine an address macro with the matching `__SHIFT` and `_MASK` constants.

The requested range starts at the tail of the DPP2 converter config block, covers DPP2 cursor, scaler, color-management, and DC perfmon field definitions, then starts the corresponding DPP3 top, converter, cursor, scaler, and color-management field definitions. The range is intentionally a chunk of a much larger generated header; the final line stops inside the DPP3 `CM3_CM_POST_CSC_B_C11_C12` register definition.

Although this source tree is under a local `ceph-client` mirror, this file is AMDGPU display-driver hardware metadata. It does not implement Ceph or distributed filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, includes, allocation paths, or locks in this range. The interface is the generated macro namespace:

- `<REGISTER>__<FIELD>__SHIFT`: the least-significant bit position for a register field.
- `<REGISTER>__<FIELD>_MASK`: the 32-bit field mask before shifting or extraction.

Major field families in this chunk:

- `CNVC_CFG2_PRE_DEGAM` and `CNVC_CFG2_PRE_REALPHA`: the end of DPP2 converter pre-degamma and realpha controls.
- `CNVC_CUR2_CURSOR0_*`: DPP2 cursor enable/mode, expansion, pixel inversion, ROM enable, alpha modulation, update-pending status, palette colors, and floating-point cursor scale/bias.
- `DSCL2_*`: DPP2 scaler coefficient RAM selection/data, scaler mode, tap counts, 2-tap sharpness/hardcoded coefficient controls, manual replication, horizontal/vertical scale ratios and initial phases for luma and chroma, black color, update-pending status, autocalibration, overscan, OTG blanking snapshots, recout/MPC sizes, line-buffer format/partition/counters, scaler memory power, output-buffer control, and output-buffer memory power.
- `CM2_*`: DPP2 color management fields for bypass/update state, post-CSC matrices, gamut remap matrices, bias, gamma correction (`GAMCOR`), blending gamma (`BLNDGAM`), HDR multiplier, memory power/status, dealpha, coefficient format, shaper LUTs, 3D LUT controls/data/output normalization, and test/debug access.
- `DC_PERFMON12_*`: DPP2 perfmon counter control, counter state, run/stop selection, count-off interrupts, counter interrupt status/ack bits, and high/low count-value reads.
- `DPP_TOP3_*`: DPP3 DPP top-level clock enables/gates, soft reset controls for CNVC/DSCL/CM/OBUF, CRC value/control fields, and host-read rate control.
- `CNVC_CFG3_*` and `CNVC_CUR3_*`: DPP3 converter surface format, alpha-plane enable, format expansion/conversion/bypass/crossbar, float conversion bias/scale, color keyer, alpha LUT, pre-dealpha, pre-CSC matrices, pre-degamma, realpha, and cursor fields.
- `DSCL3_*`: DPP3 scaler and output-buffer fields mirroring the DPP2 DSCL structure.
- `CM3_CM_CONTROL`, `CM3_CM_POST_CSC_CONTROL`, and the visible `CM3_CM_POST_CSC_*` registers: the beginning of DPP3 color-management bypass/update and post-CSC field definitions.

The repeated `RAMA` and `RAMB` blocks under `CM2_CM_GAMCOR`, `CM2_CM_BLNDGAM`, and `CM2_CM_SHAPER` describe double-buffered LUT programming metadata. Each RAM bank has start, slope, base, end, offset, and region-pair fields. Region macros cover pairs `0_1` through `32_33`, with LUT offsets and segment-count fields packed into one register per pair.

## Control Flow

This header has no runtime control flow. Runtime sequencing is supplied by AMDGPU display code:

1. DCN 3.0.1 resource and DMUB code include `dcn/dcn_3_0_1_offset.h` and this `dcn/dcn_3_0_1_sh_mask.h`.
2. Register-table macros build per-block register, shift, and mask tables. In `dcn301_resource.c`, `DPP_REG_LIST_DCN30(id)` builds DPP register addresses while `DPP_REG_LIST_SH_MASK_DCN30(__SHIFT)` and `DPP_REG_LIST_SH_MASK_DCN30(_MASK)` initialize DPP field metadata.
3. DMUB support in `dmub_dcn301.c` uses `FD_MASK(reg, field)` and `FD_SHIFT(reg, field)` to populate firmware-facing register field tables.
4. Hardware code later uses these tables through register helpers such as field update/extract macros to program converter, cursor, scaler, color-management, LUT, perfmon, clock/reset, CRC, and debug registers.

The macros do not encode ordering requirements. Consumers still have to sequence DPP clock enable, soft reset, scaler coefficient loading, double-buffered LUT RAM selection, color-pipeline updates, perfmon start/stop/ack handling, and modeset or power-management transitions correctly.

## State And Persistence Behavior

This chunk stores no software state and persists nothing. It describes bit layouts for MMIO-backed hardware state.

The represented hardware state includes:

- DPP2 and DPP3 pixel-converter state for input format, alpha behavior, pre-CSC, pre-degamma, channel crossbar, color keying, and cursor composition.
- DPP2 and DPP3 scaler state for coefficient RAM contents, scaler modes, phase/ratio values, line-buffer sizing, overscan/recout geometry, memory power, and output-buffer behavior.
- DPP2 color-management state for post-CSC, gamut remap, gamma correction, blending gamma, shaper LUTs, 3D LUTs, coefficient formats, HDR multiplier, debug access, and RAM bank selection.
- DPP2 perfmon counter state, including event selection, counter modes, count-off interrupt status/ack bits, and high/low count reads.
- DPP3 top-level DPP clock-gating, reset, CRC, and host-read controls.

Persistence is hardware-defined. Configuration registers generally retain values until a modeset, pipe disable, power gating, suspend/resume, ASIC reset, or driver reprogramming. Status, update-pending, interrupt, ack, memory-power-state, debug, CRC, and counter fields may be read-only, sticky, self-clearing, or write-one-to-clear depending on the register semantics. This generated header only names bit positions and masks; it does not distinguish those behavior classes.

## Dependencies And Integration Points

This chunk depends on AMD's generated DCN 3.0.1 register database and must match the companion offset header:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_1_offset.h`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn301/dcn301_resource.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn301.c`

Important consumers are the DCN 3.0 display-pipe code paths reused by DCN 3.0.1:

- DPP/CNVC/CUR/DSCL/CM programming through `dcn30/dcn30_dpp.*` and transform/color-management helpers.
- Resource construction in `dcn301_resource.c`, which instantiates four DPP register tables (`dpp_regs(0)` through `dpp_regs(3)`) and their shared shift/mask tables from the generated macros.
- DMUB register service initialization in `dmub_dcn301.c`, where generated field masks and shifts are exported into firmware-service register descriptors.

The integration pattern is token-pasted field construction. Higher-level macros refer to logical `(reg, field)` pairs and expand to names such as `DSCL2_SCL_MODE__DSCL_MODE_MASK`, `CNVC_CFG3_FORMAT_CONTROL__CNVC_BYPASS__SHIFT`, or `CM2_CM_3DLUT_READ_WRITE_CONTROL__CM_3DLUT_RAM_SEL_MASK`. A typo in either the generated name or the table macro normally becomes a compile error, but a wrong numeric mask or shift can compile and corrupt runtime register programming.

## Risks And Edge Cases

- Numeric field drift is the central risk. These are untyped constants; a wrong shift or mask can compile cleanly while updating or reading the wrong bits in a live display register.
- The register namespaces are highly repetitive. DPP2 and DPP3 fields are structurally similar, and DPP2 color-management RAMA/RAMB bank definitions repeat across `GAMCOR`, `BLNDGAM`, and `SHAPER`. Copy-generation errors can affect only one pipe, one RAM bank, one color channel, or one LUT region pair.
- Chunk boundaries are artificial. The first visible macros are the tail of `CNVC_CFG2_PRE_DEGAM`, and the final visible register is incomplete for DPP3 color management. Adjacent chunks are required for whole-file claims.
- Double-buffered LUT fields are sequencing-sensitive. Wrong RAM select/current/read-select/write-enable fields can program an inactive bank, read the wrong bank, or expose partially updated gamma/shaper/3D-LUT state.
- Scaler ratio/init/tap and coefficient-RAM fields are precision-sensitive. Bad masks can cause underflow, cropped/shifted output, chroma misalignment, bad sharpness, or artifacts that only appear on scaled, interlaced, chroma-subsampled, or multi-plane formats.
- Power and reset fields are high risk. Incorrect DPP clock-gate, soft-reset, DSCL memory-power, OBUF memory-power, or CM memory-power fields can make later register writes ineffective or stall a pipe.
- Status and ack fields must be handled with the correct semantics by consumers. Perfmon interrupt ACK/status, update-pending, memory-power-state, CRC one-shot pending, and test/debug fields can be read-only, sticky, or write-one-to-clear.
- Generated headers are ASIC-specific. Values that match nearby DCN 3.x headers may still differ for DCN 3.0.1; broad refactors should not substitute a sibling header's field data without checking the authoritative register source.

## Test Signals

Useful validation is mostly generated-header consistency plus hardware/display behavior:

- Build AMDGPU display code with DCN 3.0.1 support enabled; missing or renamed field macros should fail in DPP, resource, and DMUB register-table construction.
- Mechanically compare this chunk with the authoritative DCN 3.0.1 register database and verify that each visible `__SHIFT` has the intended matching `_MASK` width and position.
- Validate DPP2 and DPP3 pipe bring-up on DCN 3.0.1 hardware: modeset, plane enable/disable, cursor enable/disable, format changes, alpha/color-keying, scaling, chroma formats, and suspend/resume.
- Exercise color-management paths: pre-CSC/post-CSC, gamut remap, gamma correction, blending gamma, shaper LUT, 3D LUT, HDR multiplier, coefficient-format selection, and banked LUT update/readback flows.
- Exercise scaler-specific cases: non-integer scaling, luma/chroma scaling, vertical bottom-field init, overscan, line-buffer partitioning, OBUF control, and memory-power transitions.
- Exercise DPP CRC and DC perfmon: CRC one-shot/continuous capture, perfmon event selection, counter start/stop, count-value reads, interrupt status, and interrupt ACK handling.
- Watch kernel logs and display diagnostics for blank or stuck pipes, underflow, cursor corruption, color/gamma errors, scaler artifacts, CRC mismatches, perfmon counters that do not advance, stuck update-pending bits, memory-power timeouts, and suspend/resume failures.

## Cross-Chunk Notes

Earlier chunks own the beginning of the DPP2 CNVC config register family and the rest of the DCN 3.0.1 shift/mask namespace before line 17408. Later chunks continue DPP3 color-management definitions after `CM3_CM_POST_CSC_B_C11_C12` and cover the remaining register field metadata. The final per-file research document should merge adjacent chunks before making complete claims about all DPP instances, all color-management LUT banks, or the full `dcn_3_0_1_sh_mask.h` generated header.

### subset-b-001730: lines 19931-22460

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_1_sh_mask.h lines 19931-22460

## Scope And Purpose

This chunk is a generated AMD DCN 3.0.1 register shift/mask table. It contains C preprocessor constants that describe bit positions (`__SHIFT`) and masks (`_MASK`) for memory-mapped display hardware registers. The companion offset header supplies register addresses; this header supplies field layout metadata consumed by AMD display register helpers.

The requested range starts inside the `dce_dc_dpp3_dispdec_cm_dispdec` color-management address block, beginning after the first `CM3_CM_POST_CSC_B_C11_C12` line and continuing through the rest of the DPP3 color pipeline registers. It then covers the `DC_PERFMON13` performance-monitor address block and the OPP formatter, display-pattern-generator, output buffer, output-pipe, and output-pipe CRC blocks for OPP instances 0, 1, and 2. The range ends inside instance 3 after `DPG3_DPG_COLOUR_G_Y`, so the later DPG3, OPPBUF3, OPP_PIPE3, and CRC3 fields continue in the next chunk.

There are no executable functions, structs, or runtime branches in this chunk. The exported surface is a dense set of 2,115 macro definitions. The highest-density region is `CM3`, which contributes most of the macros because programmable piecewise-linear LUT RAM A/B region tables are expanded into per-field definitions.

## Register Blocks Covered

The first portion completes DPP3 color-management (`CM3`) fields. It covers post-CSC bank B coefficients, gamut-remap control and coefficients for primary and bank B coefficient sets, bias registers, gamma-correction control and LUT access, gamma-correction RAM A/B region descriptors, blend-gamma control and LUT access, blend-gamma RAM A/B region descriptors, HDR multiplier, CM memory power control and status, dealpha control, coefficient format selection, shaper LUT control and RAM A/B region descriptors, additional CM memory power controls, 3D LUT mode/index/data/read-write/output normalization fields, and CM test/debug index/data registers.

The `dce_dc_dpp3_dispdec_dpp_dcperfmon_dc_perfmon_dispdec` block covers `DC_PERFMON13`. It provides field layouts for performance-counter control, counter-window and event selection, trigger selection and trigger masks, performance-monitor enable and clear state, counter-state readback, thresholding, and low/high counter-value readback registers.

The `FMT0` through `FMT3` blocks cover OPP formatter fields. Each formatter instance includes RGB component clamps, dynamic expansion enable/mode, pixel encoding, subsampling mode and order, CbCr bit-reduction bypass, double-buffer update-pending status, bit-depth truncation, spatial dithering, temporal dithering, random seed registers, clamp enable/color format, side-by-side stereo active width, 4:2:0 formatter memory power controls, and 4:2:2 left-edge extra-pixel count.

The `DPG0` through partial `DPG3` blocks cover display pattern generators. Instances 0, 1, and 2 are complete in this slice and include enable/mode/dynamic-range/bit-depth/resolution controls, ramp controls, active dimensions, two packed colors per RGB/YCbCr component register, offset/segment width, and double-buffer pending status. Instance 3 begins at line 22426 and is covered only through `DPG3_DPG_COLOUR_G_Y`; `DPG3_DPG_COLOUR_B_CB`, offset/segment, and status fields continue after the requested range.

The `OPPBUF0` through `OPPBUF2` blocks cover output-buffer fields. They define active width, display segmentation, overlap pixels, pixel repetition, double-buffer pending status, 3D vertical-active space sizes, dummy RGB data, and padded-pixel count.

The `OPP_PIPE0` through `OPP_PIPE2` blocks define output-pipe clock and bypass fields: clock enable, clock-on status, and digital bypass enable.

The `OPP_PIPE_CRC0` through `OPP_PIPE_CRC2` blocks define output-pipe CRC capture controls, mask, and result registers. They include CRC enable, continuous mode, stereo and interlace modes, pixel/source selection, one-shot pending status, a 16-bit mask, and packed A/R/G/B/C result fields.

## Important APIs, Types, And Macros

The important API is the generated macro naming contract:

- `<register>__<field>__SHIFT` gives the bit offset for packing or extracting a hardware field.
- `<register>__<field>_MASK` gives the field mask in the 32-bit register value.
- Register comments such as `//CM3_CM_GAMCOR_CONTROL` and address-block comments such as `// addressBlock: dce_dc_opp_fmt0_dispdec` delimit generated register groups but are not themselves C APIs.
- Instance prefixes in this chunk include `CM3`, `DC_PERFMON13`, `FMT0` through `FMT3`, `DPG0` through `DPG3`, `OPPBUF0` through `OPPBUF2`, `OPP_PIPE0` through `OPP_PIPE2`, and `OPP_PIPE_CRC0` through `OPP_PIPE_CRC2`.

These macros are consumed indirectly through AMD display register-list helpers such as `SF`, `SRI`, `TF_SF`, `OPP_SF`, `REG_READ`, `REG_GET`, `REG_SET`, and `REG_UPDATE`. For DCN 3.0.1, `display/dc/resource/dcn301/dcn301_resource.c` includes this header, builds `dpp_regs[]` with `DPP_REG_LIST_DCN30(id)`, initializes `tf_shift` and `tf_mask` with `DPP_REG_LIST_SH_MASK_DCN30(__SHIFT/_MASK)`, builds `opp_regs[]` with `OPP_REG_LIST_DCN30(id)`, and initializes `opp_shift` and `opp_mask` with `OPP_MASK_SH_LIST_DCN20(__SHIFT/_MASK)`.

The DPP color fields are used by DCN DPP code paths such as `dcn10_dpp_cm.c`, `dcn20_dpp.c`, and `dcn30_dpp.c`. Those modules program or read gamut remap, post-CSC, gamma correction, blend gamma, shaper LUT, and 3D LUT state through the generic register tables whose field layouts come from this header. The OPP formatter and pattern-generator fields are wired through `dcn10_opp.h` and `dcn20_opp.h`, where `OPP_MASK_SH_LIST_DCN20` references `FMT0_*`, `DPG0_*`, and `OPPBUF0_*` field names as the canonical mask/shift source for every OPP instance.

## Functional Field Groups

Post-CSC and gamut-remap fields provide matrix-style color transforms. The chunk includes the tail of `CM3_CM_POST_CSC_B_*` and full `CM3_CM_GAMUT_REMAP_*` and `CM3_CM_GAMUT_REMAP_B_*` coefficient sets. Coefficients are packed as 16-bit halves in paired registers such as C11/C12 and C33/C34, while control registers expose selected and current modes. The banked forms allow drivers to program an alternate coefficient set and switch modes around frame-synchronized update points.

Gamma-correction and blend-gamma fields expose programmable PWL LUTs. `CM3_CM_GAMCOR_*` and `CM3_CM_BLNDGAM_*` include mode/select/current bits, LUT index/data/control registers, per-channel start/end slope/base/offset fields, and RAM A/B region tables from region 0 through 33. The region table fields pair LUT offsets with segment counts, while separate endpoint fields describe start and end behavior per color channel. Blend gamma mirrors this structure for the later blend/output gamma stage.

The shaper and 3D LUT fields support the DCN color pipeline used for HDR and wide-gamut workflows. The shaper block includes per-channel offsets/scales, LUT access fields, write-enable and RAM-select controls, and RAM A/B region tables. The 3D LUT block includes mode/current status, index, data, 30-bit data path fields, read/write control, output normalization factor, and per-channel output offsets. These fields integrate with the color capability flags in the DCN 3.0.1 resource setup, where post-CSC, gamma correction, hardware 3D LUT, and output gamma RAM are advertised.

Memory-power and debug fields include `CM3_CM_MEM_PWR_CTRL`, `CM3_CM_MEM_PWR_STATUS`, `CM3_CM_MEM_PWR_CTRL2`, `CM3_CM_MEM_PWR_STATUS2`, `CM3_CM_TEST_DEBUG_INDEX`, and `CM3_CM_TEST_DEBUG_DATA`. They describe force/disable/mode/state fields for CM memories and indexed debug read/write access.

`DC_PERFMON13` fields describe hardware performance counter configuration. Control fields select counter enables, clear actions, counter modes, clock enable, event selection, threshold enable, windowing, and trigger selection. State and value registers expose current counter status and low/high counter values. These registers are diagnostic and profiling surfaces rather than display-mode programming knobs.

Formatter (`FMTx`) fields control final stream formatting before link/pipe output. They include clamp bounds, dynamic expansion, pixel encoding, 4:2:0/4:2:2 controls, truncation and dither mode/depth/seed fields, temporal dither reset/offset/FRC selectors, memory power state for 4:2:0 mapping memory, and double-buffer update-pending status. These fields are used when programming output bit depth, YCbCr packing, dithering, and clamp behavior.

Display pattern generator (`DPGx`) fields generate test patterns in the OPP path. Control fields select enable, pattern mode, dynamic range, bit depth, horizontal/vertical resolution, and field polarity. Dimensions, color, ramp, and segment fields describe the generated pattern geometry and colors. Status exposes double-buffer pending state.

OPP buffer and pipe fields describe output buffering and clock/bypass state. `OPPBUFx` active width, segmentation, overlap, pixel repetition, 3D parameters, dummy data, and padded-pixel count support segmented output and stereo/3D formatting. `OPP_PIPEx` clock enable/on and digital bypass bits control the pipe-level output path.

OPP pipe CRC fields support validation and diagnostics. CRC controls enable one-shot or continuous capture, select stereo/interlace behavior, choose pixel/source selection, and report one-shot pending state. Result registers return packed 16-bit component CRC values.

## Control Flow And State Behavior

This file has no direct control flow. Runtime behavior is created by macro expansion in display-core register helpers. DCN 3.0.1 resource initialization binds register addresses from the offset header and field masks/shifts from this header into per-block register, shift, and mask structs. Later DPP and OPP code calls generic helpers such as `REG_SET`, `REG_UPDATE`, and `REG_GET`; those helpers use the bound shift/mask fields to modify memory-mapped registers.

The hardware state described here persists in display-controller registers until driver code, firmware, reset logic, power-management logic, or hardware event logic changes it. Matrix coefficient registers, LUT region descriptors, formatter settings, pattern generator parameters, OPP buffer settings, and pipe clock controls are configuration state. Current-mode fields, memory-power state fields, double-buffer pending bits, clock-on bits, CRC pending bits, performance counter state, and counter readback fields are live hardware status.

Several field groups are explicitly banked or double-buffered. CM gamma, blend-gamma, and shaper RAM A/B fields allow programming one RAM bank while another is active. Mode/current fields indicate requested versus active color-pipeline state. FMT, DPG, and OPPBUF pending bits indicate delayed register updates. Programming code must account for frame-synchronized updates, RAM bank ownership, and pending-state completion rather than assuming an immediate visible change.

LUT access registers are stateful index/data windows. `*_LUT_INDEX`, `*_LUT_DATA`, `*_LUT_CONTROL`, `*_3DLUT_INDEX`, and `*_3DLUT_DATA*` operations depend on the current index and selected channel/RAM bank. Incorrect ordering can write valid values to the wrong component, bank, or LUT entry.

## Dependencies And Integration Points

This header must stay aligned with `dcn_3_0_1_offset.h`, which provides the addresses for the same generated register names. A mask/shift macro without the matching address macro, or vice versa, breaks the generated resource tables or silently misprograms hardware if names are mismatched.

The direct DCN 3.0.1 include sites found for this header are `display/dc/resource/dcn301/dcn301_resource.c` and `display/dmub/src/dmub_dcn301.c`. The resource file is the key integration point for this chunk because it instantiates DPP and OPP register tables for four pipes and binds the field metadata through `tf_shift`, `tf_mask`, `opp_shift`, and `opp_mask`.

The DPP fields integrate with `display/dc/dpp/dcn30/dcn30_dpp.c`, `display/dc/dpp/dcn20/dcn20_dpp.c`, and older shared DPP color-management helpers. Examples include state reads for `CM_GAMCOR_CONTROL`, `CM_SHAPER_CONTROL`, `CM_3DLUT_MODE`, and `CM_BLNDGAM_CONTROL`; post-CSC programming through `CM_POST_CSC_CONTROL` and coefficient registers; blend-gamma LUT programming through `CM_BLNDGAM_LUT_*`; and region descriptor programming through `CM_BLNDGAM_RAMA_*` masks.

The OPP fields integrate with shared OPP definitions in `display/dc/opp/dcn10/dcn10_opp.h` and `display/dc/opp/dcn20/dcn20_opp.h`. Those headers define the canonical OPP field lists for formatter dithering, clamp, dynamic expansion, 4:2:0 memory power, OPP buffer segmentation, pattern-generator setup, and output-pipe clock state. DCN 3.0.1 uses the DCN 3.0 OPP register list while still relying on the DCN 2.0-era mask list for the common fields present in this chunk.

The performance-monitor fields are generated register metadata for the DPP3 performance monitor. This tree has fewer visible high-level consumers for `DC_PERFMON13` than for DPP and OPP color/output fields, so the likely users are diagnostic/debug paths, register dumps, firmware interactions, or future perf-counter instrumentation that accesses the generated register names through the same register-helper layer.

## Risks And Edge Cases

The primary risk is drift between the generated header, the offset header, and the hardware register specification. A single bad mask or shift can target the wrong bits in a memory-mapped register, causing wrong colors, broken HDR/3D LUT behavior, incorrect dithering, missing pattern-generator output, bad CRC results, stuck power states, or unreliable diagnostics.

The chunk begins and ends at partial block boundaries. It starts after the first fields for `CM3_CM_POST_CSC_B_C11_C12`, and it ends before the DPG3 block is complete. Merge/reconciliation must combine adjacent chunks before drawing per-file conclusions about complete DPP3 or OPP3 coverage.

Banked color LUT programming is sensitive to RAM selection and current-mode state. Confusing RAM A and RAM B fields, or switching mode before a bank is fully programmed, can create transient or persistent color corruption. The same caution applies to `*_CURRENT` fields: they are readback/status indicators, not always the same as the requested mode fields.

Packed coefficient and color fields are truncation-sensitive. Many matrix and color registers pack two 16-bit fields into one 32-bit register, while LUT and offset fields use 18- or 19-bit masks. Callers must clamp and pack values through the generated masks rather than assuming natural C integer widths map directly to hardware fields.

Formatter and output-buffer updates are timing-sensitive. Dither, truncation, pixel encoding, subsampling, segmentation, overlap, and active-width settings must match stream timing and link encoding. Incorrect values can manifest as color banding, chroma ordering errors, edge artifacts, or update-pending bits that do not clear as expected.

CRC and perfmon fields are diagnostic but still stateful. CRC one-shot pending, continuous capture, source selection, and mask fields can produce misleading test results if not reset between captures. Performance-counter clear/enable/window/trigger fields can similarly produce stale or partial values if programmed out of order.

Memory power fields need care around low-power transitions. Forcing, disabling, or changing default low-power modes for CM or FMT memories while the corresponding LUT or formatter path is active can cause subtle failures that only appear during blanking, resume, mode changes, or multi-pipe configurations.

## Test Signals

Build-time tests should catch missing or renamed macros through failures in `dcn301_resource.c`, DPP mask/shift initialization, and OPP mask/shift initialization. High-signal errors include missing `CM3_*`, `FMT0_*`, `DPG0_*`, `OPPBUF0_*`, or `OPP_PIPE0_*` identifiers referenced through `SF`, `TF_SF`, `OPP_SF`, `DPP_REG_LIST_SH_MASK_DCN30`, or `OPP_MASK_SH_LIST_DCN20`.

Runtime display validation should exercise DCN 3.0.1 hardware across all four DPP/OPP instances. Useful signals include successful modesets, stable scanout, correct color output with post-CSC and gamut-remap changes, correct gamma/blend-gamma/shaper/3D-LUT behavior, and no stuck double-buffer pending or memory-power state during mode changes and suspend/resume.

Color-management tests should cover RAM A/B LUT programming, current-mode readback, HDR multiplier behavior, 3D LUT 30-bit paths, and state dumps from `dcn30_dpp.c` paths. Visual or CRC-based comparisons are useful because many failures are silent register misprogramming rather than crashes.

OPP tests should cover truncation, spatial and temporal dithering, RGB and YCbCr pixel encodings, 4:2:0 and 4:2:2 formatting, clamp ranges, active width and segmentation, pixel repetition, and side-by-side stereo parameters where supported.

Diagnostic tests should validate DPG-generated patterns, OPP pipe CRC capture in one-shot and continuous modes, and performance-counter clear/enable/readback sequencing. Because the file is generated metadata, the strongest regression signal is a combination of hardware-register database cross-checks, compile coverage of every generated field list, and hardware smoke tests that touch each display pipe instance represented by the chunk.

### subset-b-001731: lines 22461-24958

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_1_sh_mask.h lines 22461-24958

## Scope And Purpose

This chunk is a generated AMD DCN 3.0.1 register shift/mask table. It exports C preprocessor constants for bit positions (`__SHIFT`) and bit masks (`_MASK`) used by AMD display register helpers when accessing memory-mapped display controller registers. The matching `dcn_3_0_1_offset.h` header supplies register addresses; this file supplies field layout.

The requested range starts in the tail of the `dce_dc_opp_dpg3_dispdec` block, covers the OPP buffer/pipe CRC/top-control registers for OPP instance 3, covers DSC forward routing registers for `DSCRM0` through `DSCRM2`, covers the `DC_PERFMON14` performance monitor block, covers all four `ODM0` through `ODM3` OPTC input blocks, covers full OTG timing-generator layouts for `OTG0` and `OTG1`, and ends inside the beginning of the `OTG2` timing-generator block at `OTG2_OTG_INTERRUPT_CONTROL`.

There are no functions, structs, or runtime branches in this chunk. Its purpose is to keep generated field metadata available to macro-based driver code such as `REG_SET`, `REG_UPDATE`, `REG_GET`, `REG_WAIT`, `SRI`, `SF`, `FD_MASK`, and `FD_SHIFT`.

## Register Blocks Covered

The range begins with the final fields of `DPG3`, including test-pattern colors, segment offset/width, and `DPG_DOUBLE_BUFFER_PENDING` status. The preceding chunk owns most of the `DPG3` block.

`dce_dc_opp_oppbuf3_dispdec` contributes OPP buffer control fields for active width, display segmentation, overlap pixels, pixel repetition, double-buffer pending state, 3D active-space dummy data, and padded segment pixels.

`dce_dc_opp_opp_pipe3_dispdec` contributes `OPP_PIPE3_OPP_PIPE_CONTROL`, with clock enable/on status and digital bypass enable. `dce_dc_opp_opp_pipe_crc3_dispdec` contributes OPP pipe CRC enable/control, CRC mask, and A/R/G/B/C result fields. `dce_dc_opp_opp_top_dispdec` contributes top-level OPP clock gating/test clock status and ABM backlight PWM selection.

`DSCRM0`, `DSCRM1`, and `DSCRM2` each expose the same `DSCRM_DSC_FORWARD_CONFIG` field layout: forward enable, OPP pipe source, double-buffer update pending, and forward-enable status.

`DC_PERFMON14` defines fields for event selection, counter control, counted value type, counter state selection, perfmon state, count-off interrupt state/acknowledge, counter interrupt status/acknowledge, captured value high/low words, and read-select fields.

`ODM0` through `ODM3` each define OPTC input control fields for soft reset, underflow interrupt/status/clear, current underflow state, double-buffer pending, input and output segment counts, per-segment source select, data format, DSC mode, DSC bytes per pixel, segment and DSC slice widths, input clock gate/enable/on status, memory selection, and spare register storage.

`OTG0` and `OTG1` are fully represented. Each has 716 `#define` entries covering scanout timing, sync and blanking, variable refresh, trigger controls, flow control, stereo/interlace, status counters, snapshots, interrupts, update locks, blank colors, vertical interrupts, CRC windows/results, global sync lock, update-window programming, DRR controls, DTO constants, request controls, DSC start position, pipe update status, and spare registers.

`OTG2` begins in this chunk and is covered from `OTG2_OTG_H_TOTAL` through `OTG2_OTG_INTERRUPT_CONTROL`. Later `OTG2` update-lock, double-buffer, master, CRC/global-control, DRR, DTO, DSC, pipe-status, and spare fields continue in the next chunk.

## Important APIs, Types, And Macros

The exported API is the generated macro naming contract:

- `<register>__<field>__SHIFT` gives the field's low bit position.
- `<register>__<field>_MASK` gives the field's masked bit range in a 32-bit register value.
- Instance prefixes in this chunk include `DPG3`, `OPPBUF3`, `OPP_PIPE3`, `OPP_PIPE_CRC3`, `OPP_TOP`, `DSCRM0` through `DSCRM2`, `DC_PERFMON14`, `ODM0` through `ODM3`, and `OTG0` through the first part of `OTG2`.
- Address-block comments identify hardware register blocks but are not compiled.

The main consumers are generated-style AMD display register lists. `display/dc/resource/dcn30/dcn30_resource.c` includes DCN 3.0 register-list structures and populates `optc_regs`, `optc_shift`, `optc_mask`, `dsc_shift`, and `dsc_mask` using macros that expand into the shift/mask symbols from this header. `display/dc/optc/dcn30/dcn30_optc.h` maps the OTG and ODM fields in this chunk through `OPTC_COMMON_REG_LIST_DCN3_0(inst)` and `OPTC_COMMON_MASK_SH_LIST_DCN30(mask_sh)`. `display/dmub/src/dmub_dcn301.c` directly includes `dcn_3_0_1_offset.h` and this header to populate DMUB register masks and shifts via `FD_MASK` and `FD_SHIFT`.

DSC routing is tied to `display/dc/dsc/dcn20/dcn20_dsc.h` and `display/dc/dsc/dcn20/dcn20_dsc.c`. That code uses `DSC_REG_LIST_DCN20(id)` and `DSC_REG_LIST_SH_MASK_DCN20(...)` for `DSCRM_DSC_FORWARD_CONFIG`, then runtime operations such as `dsc2_disconnect()` and `dsc2_wait_disconnect_pending_clear()` update `DSCRM_DSC_FORWARD_EN` and wait on `DSCRM_DSC_DOUBLE_BUFFER_REG_UPDATE_PENDING`.

## Functional Field Groups

OPP and DPG fields in this range configure late-pipe output behavior. DPG fields describe display-pattern generator colors, segment geometry, and double-buffer status. OPPBUF fields describe segmented output-buffer width, overlap, pixel repetition, 3D dummy data, and pending state. OPP pipe and pipe CRC fields expose clock/bypass control plus CRC enable modes, stereo/interlace CRC selection, one-shot pending state, CRC mask, and channel result readback.

DSCRM fields control whether a DSC stream is forwarded and which OPP pipe receives it. Their pending/status bits are synchronization points between DSC programming and OPP/OPTC routing.

`DC_PERFMON14` fields implement a display performance monitor endpoint. Counter control selects events, counted-value types, increment modes, hardware start/stop/count-off sources, restart and interrupt behavior, and readback selectors. The perfmon control fields expose monitor state, report count, count-off interrupt enable/status/ack, clock enable, run-enable start/stop selectors, counter interrupt status/ack fields, and high/low counter data.

ODM fields configure how OPTC input data is split, combined, formatted, clocked, and monitored. Source-select fields encode the number of input/output segments and the source for up to four segments. Width and bytes-per-pixel fields carry DSC-related layout, while input global control exposes underflow and double-buffer status used during ODM combine/bypass transitions.

OTG timing fields describe scanout geometry and timing. `OTG_H_TOTAL`, `OTG_H_BLANK_START_END`, `OTG_H_SYNC_A`, `OTG_H_SYNC_A_CNTL`, `OTG_H_TIMING_CNTL`, `OTG_V_TOTAL`, `OTG_V_TOTAL_MIN/MAX/MID`, `OTG_V_BLANK_START_END`, `OTG_V_SYNC_A`, and `OTG_V_SYNC_A_CNTL` hold horizontal/vertical totals, blanking windows, sync windows, polarity, mode, and divider behavior.

OTG event, trigger, and flow-control fields include vtotal and nominal-vsync interrupt status, `OTG_TRIGA/B_CNTL`, manual trigger registers, force-count-now controls, and flow-control source/polarity/granularity fields. These allow hardware-triggered timing events, manual trigger injection, delayed edge detection, and scanout-aligned control points.

OTG state and scanout readback fields include master enable, stereo force/control/status, interlace control/status, pixel data readback, vblank/hblank/active/sync status, horizontal and vertical counters, frame/VF/HV counters, count reset, vertical-sync force controls, and snapshot status/control/position/frame registers.

OTG update, global sync, DRR, CRC, and diagnostic fields include update locks, double-buffer pending bits, master update mode/lock, global sync status, GSL control/window fields, vupdate keepout, global control windows, manual flow control, DRR timing status/reach/change/trigger/control, DTO phase/modulo constants, DSC start position, pipe update status, vertical interrupt slots, CRC control, CRC windows, CRC data results, and CRC signature masks.

## Control Flow And State Behavior

This header has no direct control flow. The effective control flow is compile-time macro expansion: a resource file selects a DCN generation, instantiates per-block register tables with `SRI(...)`, and initializes shift/mask tables with `SF(...)`. Runtime code then passes logical register and field names to register helpers, which use these constants to pack or extract values.

The hardware state represented here is persistent memory-mapped register state. Configuration fields such as timing totals, ODM source selection, DSC forwarding, blank colors, CRC windows, DRR trigger windows, GSL windows, DTO constants, and update-lock settings remain active until driver writes, hardware reset, power transitions, or firmware actions change them.

Many status fields are live hardware state rather than stored configuration: clock-on bits, underflow current/status, CRC results, frame and scanout counters, blank/sync status, input trigger status, pending update bits, current stereo/interlace state, and perfmon active/counter status. Fields named `*_CLEAR`, `*_ACK`, `*_EVENT_CLEAR`, or interrupt acknowledge fields imply write-to-clear or acknowledge-style semantics in the hardware programming model.

Several register groups are frame-phase sensitive. OTG timing, vertical interrupts, vstartup/vupdate/vready, global update lock, GSL windows, vupdate keepout, DRR trigger windows, and double-buffer pending state must be programmed relative to scanout boundaries. DSCRM disconnect waits and ODM underflow/double-buffer state are also synchronization points when reconfiguring DSC/ODM paths.

## Dependencies And Integration Points

This file depends on the DCN 3.0.1 hardware register database and must stay aligned with `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_1_offset.h`. Register names in this shift/mask file must match address macros in the offset file and generated register-list entries in display core code.

Important integration points include:

- `display/dmub/src/dmub_dcn301.c`, which includes this header directly for DMUB register field masks/shifts.
- `display/dc/resource/dcn30/dcn30_resource.c`, whose `optc_regs[]`, `optc_shift`, `optc_mask`, `dsc_shift`, and `dsc_mask` tables rely on the OTG, ODM, and DSCRM field definitions.
- `display/dc/optc/dcn30/dcn30_optc.h`, which declares DCN 3.0 OPTC register and mask lists for OTG/ODM timing, CRC, DRR, GSL, DSC start-position, pipe-update-status, and ODM programming.
- `display/dc/dsc/dcn20/dcn20_dsc.*`, which uses `DSCRM_DSC_FORWARD_CONFIG` fields to connect, disconnect, and wait for DSC forwarding state.
- IRQ and diagnostics paths that consume OTG status, interrupt, CRC, frame counter, and global sync fields through common register helpers rather than spelling every generated macro directly.

## Risks And Edge Cases

The primary risk is drift between this generated mask header, the companion offset header, and the hardware register specification. A wrong mask or shift silently packs values into the wrong bits, which can produce display timing corruption, missed interrupts, invalid CRC capture, incorrect DSC routing, ODM underflow handling failures, or stuck update locks.

Instance replication is high risk. `ODM0` through `ODM3` and `OTG0` through `OTG2` use repeated layouts, but this chunk only contains full layouts for `OTG0` and `OTG1`; `OTG2` is split across chunk boundaries. Review or merge tooling should not infer that the `OTG2` block is complete from this document alone.

Interrupt/status fields are densely packed next to clear and ack bits. Confusing `*_INT_STATUS` with `*_INT_ACK`, `*_CLEAR`, or `*_MSK` can either fail to acknowledge an interrupt or clear an event unexpectedly. This applies to OPP pipe CRC one-shot state, perfmon counter interrupts, ODM underflow status/clear, OTG vertical interrupts, snapshot/trigger interrupts, vtotal/nominal-vsync events, DRR timing events, and global sync events.

Timing fields are width-limited and often packed as low/high halves. Mode-derived horizontal and vertical totals, blanking intervals, sync windows, CRC windows, GSL windows, DRR windows, and DSC/ODM widths must be clamped before packing. Overwide values are truncated by masks and can move timing points to unintended coordinates.

Double-buffer and update-lock fields can create frame-dependent failures. Incorrect sequencing around `OPTC_DOUBLE_BUFFER_PENDING`, `OTG_UPDATE_PENDING`, `OTG_DRR_TIMING_DBUF_UPDATE_PENDING`, `DSCRM_DSC_DOUBLE_BUFFER_REG_UPDATE_PENDING`, global update locks, and vupdate keepout can make updates apply on the wrong frame or appear stuck.

## Test Signals

Build-time failures involving missing `*_SHIFT` or `*_MASK` symbols in `SF`, `SRI`, `FD_MASK`, `FD_SHIFT`, `REG_FIELD`, `REG_GET`, `REG_SET`, `REG_UPDATE`, or `REG_WAIT` expansions are strong signals that this generated metadata no longer matches its consumers.

Runtime validation should include DCN 3.0.1 hardware modesets on OTG instances 0, 1, and 2, including standard timing changes, vblank/vupdate interrupt delivery, frame counter advancement, CRC readback, and no stuck pipe-update or double-buffer pending state.

ODM and DSC coverage should exercise bypass and combine configurations, DSC forwarding connect/disconnect, high-bandwidth modes requiring ODM segmentation, and underflow clear/status handling. Useful signals are correct segment source selection, expected DSC slice/bytes-per-pixel programming, no unexpected ODM underflow interrupts, and `DSCRM_DSC_DOUBLE_BUFFER_REG_UPDATE_PENDING` clearing after disconnect.

DRR and synchronization coverage should exercise variable refresh, DRR trigger windows, vtotal min/max/mid changes, GSL participation, global update locks, and vupdate keepout. Perfmon coverage should verify event selection, counter start/stop, interrupt/ack behavior, and high/low readback consistency.

Because this chunk is generated register metadata rather than algorithmic code, the strongest regression tests are hardware-register-database diffs, successful AMDGPU display builds, and targeted modeset/CRC/ODM/DSC/DRR smoke tests on DCN 3.0.1-class hardware.

### subset-b-001732: lines 24959-27395

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_1_sh_mask.h lines 24959-27395

## Scope And Purpose

This chunk is part of AMDGPU's generated DCN 3.0.1 shift/mask header. It contains C preprocessor constants only: there are no functions, structs, enums, storage objects, loops, branches, or local runtime policy. The exported interface is a set of `REGISTER__FIELD__SHIFT` and `REGISTER__FIELD_MASK` macros that describe bit positions and already-positioned masks for memory-mapped display-controller registers.

The requested range starts at the tail of the `OTG2` output timing generator block, contains the full `dce_dc_optc_otg3_dispdec` block, then moves through OPTC miscellaneous registers, an OPTC performance-monitor block, DIO I2C/DDC registers, DIO miscellaneous clock/power/reset registers, HPD blocks 0 through 3, and ends after the first fields of `DC_PERFMON16_PERFCOUNTER_CNTL2`.

The file's practical purpose is to let DCN 3.0.1 display code use common register helpers such as `REG_GET`, `REG_SET`, `REG_UPDATE`, `SF`, `SRI`, `LE_SF`, `I2C_SF`, and related register-list macros while this generated header supplies the ASIC-specific field layout. The companion `dcn_3_0_1_offset.h` supplies the matching register addresses and base indices.

Although this repository path is under `sources/distributed-fs/ceph-client`, this source is AMD display hardware metadata. It has no Ceph, filesystem, distributed-storage, or network protocol behavior.

## Register Blocks Covered

The first section completes the `OTG2` timing generator slice from `OTG2_OTG_UPDATE_LOCK` through `OTG2_OTG_SPARE_REGISTER`. It covers double-buffer update state, master enable, blank color, vertical interrupt slots, CRC controls/windows/results, static-screen detection, stereo/3D controls, global sync lock, vstartup/vupdate/vready positions, global sync status, DRR timing status and control, DTO constants, DSC start position, pipe update status, and spare state. The earlier `OTG2` timing fields live in the previous chunk.

`dce_dc_optc_otg3_dispdec` is fully represented. `OTG3` starts at `OTG3_OTG_H_TOTAL` and runs through `OTG3_OTG_SPARE_REGISTER`. It mirrors the per-timing-generator layout used by other OTG instances: horizontal and vertical timing, vtotal min/max/mid control, trigger A/B controls, forced count and flow control, stereo/interlace, live status/counters, snapshots, interrupt routing, update locks, CRC, static-screen detection, GSL, DRR, DSC, pipe update status, and spare register fields.

`dce_dc_optc_optc_misc_dispdec` covers OPTC-wide routing, clocks, and ODM memory power:

- `DWB_SOURCE_SELECT` selects OTG sources for DWB0, DWB1, and DWB2.
- `GSL_SOURCE_SELECT` selects ready sources for GSL0-2 and timing sync.
- `OPTC_CLOCK_CONTROL` exposes OPTC display-clock gating, clock-on status, and test clock selection.
- `ODM_MEM_PWR_CTRL`, `ODM_MEM_PWR_CTRL2`, `ODM_MEM_PWR_CTRL3`, and `ODM_MEM_PWR_STATUS` describe force/disable/status fields for ODM memories 0-11 and unassigned/vblank memory power modes.
- `OPTC_MISC_SPARE_REGISTER` exports an 8-bit spare field.

`dce_dc_optc_optc_dcperfmon_dc_perfmon_dispdec` covers performance monitor 15. It defines counter control, counted-value type, hardware stop and count-off selection, per-counter states, perfmon state/report-count control, count-off interrupt enable/status/ack/type, clock enable, run-enable start/stop selectors, comparison value high/low fields, and readback high/low registers.

`dce_dc_dio_dout_i2c_dispdec` covers the display I2C/DDC engine. It includes global I2C control and arbitration, interrupt status/ack/masks for software and DDC hardware engines, software status, DDC1-DDC4 hardware status, DDC1-DDC4 speed/setup, four queued transaction descriptors, the indexed data register, EDID detect control, and DDC read-request interrupt fields.

`dce_dc_dio_dio_misc_dispdec` covers DIO scratch registers, DIO memory power status/control, DIO clock gating/status, DIO power management, DIG soft reset controls, HDMI RX status timer, and generic interrupt message/clear fields.

`dce_dc_dio_hpd0_dispdec` through `dce_dc_dio_hpd3_dispdec` define the first four hot-plug-detect blocks. Each HPD instance has the same layout: interrupt/sense status, interrupt control/ack/polarity/enable, connection and RX interrupt debounce timers, fast-train delays/enables, and connect/disconnect toggle filter delays.

The final lines start `dce_dc_dio_dio_dcperfmon_dc_perfmon_dispdec` by defining `DC_PERFMON16_PERFCOUNTER_CNTL` and the beginning of `DC_PERFMON16_PERFCOUNTER_CNTL2`. The rest of performance monitor 16 continues in the next chunk.

## Important APIs, Types, And Macros

There are no callable APIs in this chunk. The important exported surface is the macro naming contract:

- `<REGISTER>__<FIELD>__SHIFT` gives the low bit position of a hardware register field.
- `<REGISTER>__<FIELD>_MASK` gives the field mask already shifted into its register position.
- Register-heading comments such as `//OTG3_OTG_CRC_CNTL` group fields by hardware register name.
- Address-block comments such as `// addressBlock: dce_dc_dio_hpd0_dispdec` identify generated hardware blocks and replicated instances.

The most important OTG2/OTG3 macro families are timing and scanout fields (`OTG_H_TOTAL`, `OTG_H_BLANK_START_END`, `OTG_V_TOTAL`, `OTG_V_BLANK_START_END`, `OTG_STATUS_POSITION`), frame-phase update fields (`OTG_UPDATE_LOCK`, `OTG_DOUBLE_BUFFER_CONTROL`, `OTG_MASTER_UPDATE_MODE`, `OTG_MASTER_UPDATE_LOCK`), GSL fields (`OTG_GLOBAL_SYNC_STATUS`, `OTG_GSL_CONTROL`, `OTG_GSL_WINDOW_X/Y`), DRR fields (`OTG_DRR_TIMING_INT_STATUS`, `OTG_DRR_V_TOTAL_*`, `OTG_DRR_CONTROL`), vertical interrupt controls, and CRC controls/windows/results.

The important OPTC misc fields are the source selectors and ODM memory power controls. `DWB_SOURCE_SELECT` and `GSL_SOURCE_SELECT` feed display writeback and global sync lock routing. `ODM_MEM_PWR_CTRL*` and `ODM_MEM_PWR_STATUS` provide compact repeated fields for memory power force, disable, mode, and state.

The important I2C/DDC fields are `DC_I2C_GO`, soft/send/status reset bits, DDC select, transaction count, arbitration request/done bits for software and DMCU users, software completion/error status bits, DDC hardware status/read-request bits, DDC speed/setup timing fields, per-transaction read/write/start/stop/count fields, and indexed data/index-write fields.

The important HPD fields are `DC_HPD_INT_STATUS`, `DC_HPD_SENSE`, `DC_HPD_SENSE_DELAYED`, `DC_HPD_RX_INT_STATUS`, interrupt ack/polarity/enable fields, connection/RX timers, fast-train delay/enables, and toggle filter delays. These are replicated for HPD0, HPD1, HPD2, and HPD3.

## Control Flow

This header has no local control flow. Runtime control flow is created by consumers that include `dcn_3_0_1_offset.h` and this shift/mask header, then build register tables and issue MMIO register operations through AMD display helpers.

A typical use pattern is:

1. DCN 3.0.1 resource or DMUB code includes the generated offset and mask headers.
2. Register-list macros paste logical register names into offset, mask, and shift identifiers.
3. Driver modules call helpers such as `REG_GET`, `REG_SET`, `REG_UPDATE`, or instance-aware variants.
4. Those helpers use these constants to isolate or pack the requested field in a 32-bit hardware register value.

For OTG and OPTC fields, the runtime sequencing lives in the timing generator, hardware sequencer, IRQ, writeback, and global-sync-lock paths. For I2C/DDC, sequencing lives in the DCE/DC I2C hardware engine: callers program transaction descriptors, load or drain the indexed data register, assert `DC_I2C_GO`, then poll or handle software/hardware completion and error bits. For HPD, IRQ and GPIO paths read sense/status fields and write ack or enable fields around hotplug events.

The chunk does not encode whether a field is read-only, write-one-to-clear, self-clearing, sticky, clock-gated, or safe only in a particular display phase. Those semantics come from the hardware specification and higher-level AMD display code.

## State And Persistence Behavior

The file itself stores no state and persists nothing. It describes hardware register state whose lifetime is controlled by display-controller hardware, the AMD display driver, DMUB/DMCU firmware, clock and power management, hotplug events, modesets, suspend/resume, and GPU reset.

OTG configuration state includes timing totals, blank/sync intervals, trigger controls, blank colors, CRC windows, vertical interrupt line positions, update-lock settings, GSL windows, DRR ranges, DTO constants, DSC start position, and static-screen settings. OTG live state includes current blank/sync/active status, counters, frame counts, snapshot readbacks, global sync and DRR event status, CRC results, pending double-buffer updates, and pipe update pending/locked indicators.

OPTC misc state includes display writeback and GSL source routing, clock gating/status, and ODM memory power force/disable/mode/state fields. Bad values can persist until corrected by a later hardware-sequencer pass, power transition, or reset.

I2C/DDC state spans command setup, ownership/arbitration, queued transaction descriptors, indexed data-buffer position and write direction, software and hardware status bits, EDID-detect state, and interrupt status/ack/mask fields. Some bits are command latches, some are live status, and some are event acknowledgements.

DIO and HPD state includes scratch registers, memory and clock power controls, DIG soft reset bits, HDMI RX timer control, generic interrupt message/clear fields, HPD debounce/filter timers, HPD sense status, and HPD interrupt enable/ack/polarity. HPD sense and delayed sense are live connector signals, while debounce timers and interrupt enables are configuration state.

Performance monitor state includes selected events, counted value type, start/stop/count-off controls, active state, comparison values, interrupt status/ack, and counter readbacks. Performance monitor values are diagnostic/runtime counters rather than persistent software data.

## Dependencies And Integration Points

The direct companion is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_1_offset.h`, which defines matching register addresses and base indices. Examples in this range include `mmOTG2_OTG_UPDATE_LOCK`, `mmOTG3_OTG_H_TOTAL`, `mmDWB_SOURCE_SELECT`, `mmGSL_SOURCE_SELECT`, `mmOPTC_CLOCK_CONTROL`, `mmODM_MEM_PWR_CTRL*`, `mmDC_PERFMON15_*`, `mmDC_I2C_CONTROL`, `mmDIO_MEM_PWR_STATUS`, `mmHPD0_DC_HPD_INT_STATUS`, and `mmDC_PERFMON16_PERFCOUNTER_CNTL`.

Visible include sites for the DCN 3.0.1 generated headers are `display/dc/resource/dcn301/dcn301_resource.c` and `display/dmub/src/dmub_dcn301.c`. Those files build the DCN 3.0.1 resource and DMUB register surfaces from generated offsets and masks.

The OTG and OPTC portions integrate with shared DCN timing-generator code. `display/dc/optc/dcn30/dcn30_optc.h` defines common DCN 3.0 OPTC register and shift/mask lists that include `GSL_SOURCE_SELECT`, `DWB_SOURCE_SELECT`, many `OTG_*` timing/status/CRC/DRR/GSL fields, and the pipe update status fields represented in this chunk. `display/dc/optc/dcn20/dcn20_optc.c` uses `GSL_SOURCE_SELECT` and `DWB_SOURCE_SELECT` at runtime to select GSL-ready sources and writeback sources.

The I2C/DDC fields integrate with `display/dc/dce/dce_i2c_hw.c`, `display/dc/dce/dce_i2c_hw.h`, `display/dc/gpio/ddc_regs.h`, and `display/dc/gpio/hw_ddc.c`. These paths define the register/mask structures and perform DDC transactions for EDID and link detection by programming `DC_I2C_CONTROL`, `DC_I2C_ARBITRATION`, `DC_I2C_SW_STATUS`, `DC_I2C_TRANSACTION*`, `DC_I2C_DATA`, DDC setup/speed, and EDID-detect fields.

The HPD fields integrate with display IRQ and GPIO handling. `display/dc/irq/irq_service.c` contains generic HPD sense/polarity handling around `HPD0_DC_HPD_INT_STATUS` and `HPD0_DC_HPD_INT_CONTROL`, while link encoder headers use HPD control/sense fields to enable hotplug detection and read connector state. Cross-generation link encoder code also uses `DIO_CLK_CNTL` fields for display, reference, symbol, and HDCP clock gating, matching the DIO clock families present here.

The ODM memory power mode fields integrate with DC hardware sequencer paths. For example, DCN hardware sequencer code programs `ODM_MEM_PWR_CTRL3` fields such as `ODM_MEM_UNASSIGNED_PWR_MODE` and `ODM_MEM_VBLANK_PWR_MODE` during display initialization or power policy setup.

## Risks And Edge Cases

The primary risk is silent hardware misprogramming. A wrong shift or mask can still compile, but read/modify/write helpers will touch the wrong bits, truncate field values, leave stale bits behind, or decode live status incorrectly.

Chunk boundaries matter. The range starts in the middle of the `OTG2` block after earlier timing fields and ends in the middle of the `DC_PERFMON16` block. Whole-file reconciliation must merge this slice with adjacent chunks before describing complete OTG2 or DC_PERFMON16 coverage.

OTG timing fields are phase-sensitive. Incorrect masks for update locks, double-buffer pending bits, vertical interrupt positions, GSL windows, vstartup/vupdate/vready positions, DRR trigger windows, or DSC start position can cause missed updates, stuck update locks, unstable variable refresh, broken vblank/vupdate IRQs, visible timing glitches, or CRC/readback mismatches.

Repeated instance layouts are easy to review incorrectly. OTG2 and OTG3 share many field names under different prefixes, and HPD0-HPD3 are structurally identical. A generation or copy error in one instance can affect only one display pipe or connector and escape broad smoke tests.

I2C/DDC fields mix command, ownership, status, interrupt, and indexed data access in a compact register set. Confusing `ACK`, `MASK`, `INT`, `REQ`, `DONE`, `GO`, `ABORT`, or `INDEX_WRITE` fields can hang DDC transfers, corrupt the transaction buffer, leave the engine owned by the wrong client, or make EDID/hotplug detection unreliable.

HPD fields are event-sensitive. Bad debounce/filter timers can create missed or bouncing hotplug events. Wrong polarity or ack masks can invert connector state, leave interrupts asserted, or suppress RX interrupt handling used by DisplayPort sideband and link-maintenance paths.

Clock, reset, and memory power fields have broad blast radius. Incorrect DIO/OPTC clock gating or DIG reset masks can shut off active display paths or prevent link training. Wrong ODM/DIO memory power force/disable values can create failures that appear only during vblank power transitions, multi-stream ODM use, or low-power state changes.

Performance monitor registers are diagnostic but still stateful. Incorrect counter selection, count-off, interrupt ack, or read-select fields can produce misleading performance data or unexpected perfmon interrupts.

## Test Signals

Build-time signals are direct: missing or stale macros used by DCN 3.0.1 resource, DMUB, OPTC, I2C/DDC, GPIO, IRQ, or hardware-sequencer register lists should fail compilation around `SF`, `SRI`, `REG_FIELD`, `REG_GET`, `REG_SET`, `REG_UPDATE`, `LE_SF`, `I2C_SF`, or generated `*_MASK`/`__SHIFT` identifiers.

Generated-register validation should cross-check every mask in this line range against the matching `dcn_3_0_1_offset.h` register names and against the ASIC register database. Cross-generation diffs against nearby DCN headers are useful, but expected ASIC deltas must be reviewed rather than normalized away.

Runtime display signals include successful modesets on pipes using OTG2 and OTG3, stable vblank/vupdate IRQ delivery, no stuck global/update locks, correct DRR behavior, correct DSC start placement where DSC is active, advancing frame and HV counters, and CRC capture values that match expected scanout content.

I2C/DDC and HPD tests are high value for this chunk: EDID reads over DDC1-DDC4, hotplug connect/disconnect storms, delayed HPD sense validation, DisplayPort RX interrupt handling, suspend/resume with monitors connected, and link detection on each exposed connector. Regression symptoms include missing EDID, NACK/timeout loops, stuck software I2C status, repeated HPD interrupts, or connectors that never report present.

DIO/OPTC power and clock tests should cover blanking transitions, multi-display ODM paths, display writeback routing, GSL synchronization, link training, runtime power management, and resume from low-power states. Performance monitor validation can read counters before/after selected display activity and confirm interrupt ack/status bits behave as expected.

Because this is generated register metadata rather than algorithmic code, the strongest tests combine build coverage, generated-header consistency checks, register-state dumps on DCN 3.0.1 hardware, and hardware smoke tests that exercise the affected display pipes, DDC engines, HPD blocks, and power-management states.

## Cross-Chunk Notes

This is chunk 11 of `dcn_3_0_1_sh_mask.h`. The previous chunk owns the earlier `OTG2` registers, including timing and trigger fields before `OTG2_OTG_UPDATE_LOCK`. The next chunk continues after the partial `DC_PERFMON16_PERFCOUNTER_CNTL2` definitions and should be consulted for the full DIO perfmon 16 layout and later generated blocks.

### subset-b-001733: lines 27396-29755

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_1_sh_mask.h lines 27396-29755

## Scope And Purpose

This chunk is a generated AMD DCN 3.0.1 register shift/mask table for display I/O hardware. It contains C preprocessor constants that describe bit positions (`__SHIFT`) and bit masks (`_MASK`) for DC display performance monitoring, DisplayPort AUX controllers, Video Packet Generator (VPG), Audio Formatter (AFMT), Display Metadata Engine (DME), and the first part of digital stream encoder (`DIG0`) HDMI/TMDS registers.

There are no executable functions, structs, or runtime branches in this slice. The exported surface is compile-time field metadata used by AMD display register helper macros. The companion `dcn_3_0_1_offset.h` header provides register addresses such as `mmDP_AUX0_AUX_CONTROL`, `mmVPG0_VPG_GENERIC_PACKET_DATA`, `mmAFMT0_AFMT_VBI_PACKET_CONTROL`, `mmDME0_DME_CONTROL`, and `mmDIG0_HDMI_CONTROL`; this header supplies the matching bit layout, for example `DP_AUX0_AUX_CONTROL__AUX_RESET__SHIFT` and `DP_AUX0_AUX_CONTROL__AUX_RESET_MASK`.

The requested range contains 2,360 source lines with 2,175 `#define` entries, 8 address-block comments, and 161 register delimiter comments. It starts in the tail of `DC_PERFMON16_PERFCOUNTER_CNTL2`, covers complete `DP_AUX0` through `DP_AUX3` AUX field blocks, covers `VPG0`, `AFMT0`, and `DME0`, and ends inside `DIG0_TMDS_DCBALANCER_CONTROL` after the first three shift definitions. The surrounding lines before and after this chunk own the rest of those two partial edge registers.

## Register Blocks Covered

`DC_PERFMON16` is present as a tail from the previous address block. The chunk begins with three masks for `DC_PERFMON16_PERFCOUNTER_CNTL2`, then covers `PERFCOUNTER_STATE`, `PERFMON_CNTL`, `PERFMON_CNTL2`, `PERFMON_CVALUE_INT_MISC`, `PERFMON_CVALUE_LOW`, `PERFMON_HI`, and `PERFMON_LOW`. These fields describe performance-counter state selection, report counts, count-off interrupt enable/status/acknowledge bits, selected readback halves, and low/high counter value storage.

`DP_AUX0`, `DP_AUX1`, `DP_AUX2`, and `DP_AUX3` are replicated under `dce_dc_dio_dp_aux[0-3]_dispdec`. Each instance exposes the same AUX controller register layout: enable/reset, low-speed read, HPD selection, impedance calibration request, test/deglitch control, software transaction control, register arbitration between software and DMCU, interrupt status/ack/mask fields, software and low-speed status/data FIFOs, DPHY TX/RX configuration and status, GTC sync control/status/error tracking, and PHY wake control.

`VPG0` under `dce_dc_dio_dig0_vpg_vpg_dispdec` covers generic packet access and data staging, frame-update and immediate-update controls for generic packets 0 through 14, generic packet conflict status/clear, memory power control, ISRC packet access/data, and MPEG info packet words. This is the packet-generation side used to stage secondary data packets before sending them through the stream encoder.

`AFMT0` under `dce_dc_dio_dig0_afmt_afmt_dispdec` covers audio and infoframe formatting registers. The fields include VBI packet control, HDMI audio packet rate limits, audio infoframe words, IEC 60958 channel status words, audio CRC control/result, ramp controls, AFMT status, audio sample send/control, infoframe update, interrupt status, audio source select, and AFMT memory power.

`DME0` under `dce_dc_dio_dig0_dme_dme_dispdec` covers metadata engine enablement, HUBP requestor selection, stream type, double-buffer pending/taken/clear/disable state, transmission-missed status/clear, and memory power controls. It integrates the display metadata path with the stream encoder and DP/HDMI metadata transmission registers.

`DIG0` under `dce_dc_dio_dig0_dispdec` begins the digital stream encoder block. This range includes front-end source selection, output CRC controls/results, test/random/clock pattern registers, FIFO status, HDMI metadata packet control, HDMI deep color/scramble/keepout/error control, HDMI status and audio/ACR/VBI/infoframe controls, generic HDMI packet controls 0 through 10 for packets 0 through 14, HDMI double-buffer control, ACR constants/status for 32/44.1/48 kHz audio families, AFMT clock control, back-end enable and mode/HPD/source selection, TMDS sync/control character fields, TMDS feedback/stereosync/sync pattern fields, and the start of TMDS DC balancer control.

## Important APIs, Types, And Macros

The important contract is the generated macro naming scheme:

- `<instance>_<register>__<field>__SHIFT` gives the bit offset used when packing or extracting a register field.
- `<instance>_<register>__<field>_MASK` gives the 32-bit field mask.
- Address-block comments identify replicated hardware instances, while register comments delimit groups for generated readability.
- Instance prefixes in this chunk include `DC_PERFMON16`, `DP_AUX0` through `DP_AUX3`, `VPG0`, `AFMT0`, `DME0`, and `DIG0`.

These constants are consumed through AMD display register macros such as `AUX_SF`, `SE_SF`, `SRI`, `REG_FIELD`, `REG_READ`, `REG_WRITE`, `REG_UPDATE`, `REG_SET`, and `REG_WAIT`. `display/dc/dce/dce_aux.h` uses `DP_AUX0_*` field names as the base mask/shift list for all AUX instances. `display/dc/dcn30/dcn30_vpg.h` uses `VPG0_*` fields for generic-packet data/index/update/conflict state. `display/dc/dcn30/dcn30_afmt.h` uses `AFMT0_*` fields for audio source, audio channel layout, IEC 60958 channel status, sample-send, and memory-power control. `display/dc/dio/dcn30/dcn30_dio_stream_encoder.h` uses `DIG0_*`, `DME0_*`, and related `DP0_*` fields to build the DCN 3.0 stream encoder register and mask lists.

The direct DCN 3.0.1 include site found in this tree is `display/dmub/src/dmub_dcn301.c`, which includes this header with the matching offset header. Other DCN display modules use the same generated macro families through versioned resource and stream-encoder setup.

## Functional Field Groups

AUX transaction fields describe a software-driven DisplayPort AUX channel. `AUX_CONTROL` enables and resets the controller, selects HPD input, controls low-speed read, and exposes reset completion. `AUX_SW_CONTROL`, `AUX_SW_DATA`, and `AUX_SW_STATUS` stage request bytes, transaction length, auto-increment behavior, reply data, reply byte count, done/error/timeout state, and the software transaction go bit. `AUX_INTERRUPT_CONTROL` provides done/error interrupt status, acknowledge, and mask bits. `AUX_ARB_CONTROL` arbitrates access between software and DMCU users, with request, pending, done, and status fields. DPHY and GTC sync registers cover physical signaling thresholds/timing, invalid/timeout handling, receive state, wake detection, and global-time-code sync lock/error status.

VPG fields stage generic secondary data packets. The access-control/data pair selects byte indexes and writes four packet bytes at a time. Frame-update and immediate-update registers independently schedule generic packet slots 0 through 14. Status fields report generic-packet conflicts and provide a clear bit, while memory-power fields allow force/light-sleep style power management around the VPG packet RAM.

AFMT fields program HDMI/DP audio packet formatting. They control VBI/audio packet placement, maximum packets per line, audio channel enables and layouts, 60958 channel-status values, audio-source selection, audio-sample sending, CRC testing, audio infoframe updates, and AFMT RAM power behavior. Status and interrupt bits report packet/audio formatter conditions.

DME fields program metadata insertion. They select a HUBP requestor, enable metadata engine operation, choose stream type, manage double-buffer handshakes, clear taken/missed state, and control DME memory power. These fields are timing-sensitive because metadata payloads need to be accepted by the stream pipeline before the intended frame or packet interval.

DIG/HDMI/TMDS fields program the stream encoder. `DIG_FE_CNTL` selects the OTG/source input and stereo/bypass options. `HDMI_CONTROL`, `HDMI_STATUS`, and related packet controls handle scrambling, deep color, keepout, packet generator versioning, HDMI error ack/mask/status, VBI/infoframe/audio packet send behavior, and ACR enable/source selection. Generic packet controls provide continuous send, one-shot send, immediate send, pending, enable double-buffer pending, and line-number fields for slots 0 through 14. TMDS fields select packing phase, control-character output, sync character patterns, CTL bits, feedback delay, stereosync control selection, and DC balancer behavior.

Performance monitor fields define counter state and readback plumbing for the display performance monitor. They expose selected counter states, count-off interrupt controls, report count, low/high counter value readback, and interrupt/status/ack bits for individual performance counters.

## Control Flow And State Behavior

This header has no direct control flow. Runtime behavior appears when the display driver expands register-list and mask-list macros for a selected hardware instance. The offset header supplies the memory-mapped register address, this header supplies the mask/shift constants, and helper macros perform read-modify-write, polling, or direct writes.

Hardware state described here persists in display controller registers until changed by driver writes, firmware/DMCU/DMUB activity, reset, power gating, or hardware event logic. Configuration fields include AUX timing/control, VPG packet RAM indexes and update bits, AFMT audio/infoframe setup, DME metadata mode, DIG source selection, HDMI/TMDS mode controls, packet scheduling, and memory-power controls. Live status fields include AUX done/error/timeout/reply status, reset-done bits, FIFO status, GTC sync lock/error state, VPG conflict state, AFMT status/interrupt state, DME double-buffer and missed-transmission state, HDMI error/status state, generic-packet pending bits, and performance-counter values.

Several fields have acknowledge, clear, or double-buffer semantics. Examples include `*_ACK`, `*_CLR`, `*_CLEAR`, `*_DB_PENDING`, `*_DB_TAKEN`, `*_DB_TAKEN_CLR`, `*_IMMEDIATE_SEND_PENDING`, and `*_EN_DB_PENDING`. Callers must distinguish status from write-to-clear or handshake bits, because a wrong mask can either fail to clear a condition or clear/take state unexpectedly.

## Dependencies And Integration Points

The chunk depends on the DCN 3.0.1 hardware register database and must remain aligned with `dcn_3_0_1_offset.h`, where the corresponding `mm*` address and base-index macros are defined. It also depends on the generated AMD display naming convention that lets a single `DP_AUX0_*`, `VPG0_*`, `AFMT0_*`, `DME0_*`, or `DIG0_*` field list seed per-instance register tables.

The AUX definitions integrate with `display/dc/dce/dce_aux.c` and `display/dc/dce/dce_aux.h`. Those paths reset AUX, poll `AUX_RESET_DONE`, program software request length/data, trigger `AUX_SW_GO`, wait for `AUX_SW_DONE`, read reply bytes and error state, and acknowledge `AUX_SW_DONE_ACK`.

The VPG and AFMT definitions integrate with DCN 3.0 packet/audio helpers in `display/dc/dcn30/dcn30_vpg.*` and `display/dc/dcn30/dcn30_afmt.*`. These modules stage infoframe/generic-packet bytes, request frame or immediate updates, configure HDMI audio channel/layout/channel-status data, and control audio mute/sample sending.

The DME and DIG definitions integrate with `display/dc/dio/dcn30/dcn30_dio_stream_encoder.*` and related stream-encoder construction. The register list includes HDMI generic packet controls 0 through 10, HDMI audio/ACR/infoframe controls, `DME_CONTROL`, HDMI metadata packet control, front-end source selection, FIFO status, and clock/test pattern registers. These fields are used during stream enable, modeset, infoframe/metadata updates, audio setup, and DP/HDMI packet programming.

## Risks And Edge Cases

The primary risk is mismatch between this generated mask header, the companion offset header, and real DCN 3.0.1 hardware. A bad shift or mask silently targets the wrong bitfield in memory-mapped display registers, which can break AUX transactions, corrupt HDMI infoframes, disable audio packets, leave metadata double buffers stuck, misroute DIG sources, or cause spurious/missed interrupts.

The replicated AUX blocks are easy to drift. `DP_AUX0` through `DP_AUX3` should remain structurally identical except for instance prefix and offsets. A generation error in one instance could affect only one connector path and might only reproduce with a display attached to that AUX channel.

Partial-block boundaries matter for chunk reconciliation. `DC_PERFMON16_PERFCOUNTER_CNTL2` begins before this range, and `DIG0_TMDS_DCBALANCER_CONTROL` continues after line 29755. Any final merged research should avoid treating those two registers as fully owned by this chunk alone.

Handshake and clear bits are high risk. AUX `GO`/`DONE`/`ACK`, arbitration request/done bits, VPG conflict clear, DME double-buffer taken/pending/clear, HDMI error ack/mask, HDMI double-buffer state, and generic packet pending bits are adjacent to configuration fields. Confusing status masks with acknowledge masks can create lost completion signals or stale pending state.

Packet and audio fields are width-sensitive. Generic packet line numbers are packed 16-bit values, packet byte lanes are packed in 8-bit fields, ACR N/CTS values have fixed field widths, and many update controls are one-bit slot selectors. Callers must clamp or validate values before packing; overwide values will be truncated by these masks.

Power-management fields can hide state. VPG, AFMT, and DME memory power controls interact with packet RAM or metadata state. Programming packet data while RAM is gated, or failing to restore state after power transitions, can manifest as missing infoframes, stale audio metadata, or missed HDR/metadata packets.

## Test Signals

Build-time signals include compilation failures for missing `DP_AUXx_*`, `VPG0_*`, `AFMT0_*`, `DME0_*`, or `DIG0_*` macros used by `AUX_SF`, `SE_SF`, `SRI`, `REG_FIELD`, `REG_UPDATE`, and related AMD display helpers. These are strong indicators that generated headers and consumer field lists are out of sync.

Runtime AUX signals include successful EDID/DPCD reads, stable hotplug detection across all AUX-backed connectors, no AUX timeout storms, correct `AUX_RESET_DONE` polling behavior, and successful reply byte counts for DP link training and I2C-over-AUX transactions.

Runtime packet/audio/metadata signals include correct HDMI/DP infoframes, HDR or vendor metadata arriving on the sink, audio playback with expected channel layout and sample status, correct ACR/N/CTS behavior for 32/44.1/48 kHz families, no stale generic-packet pending bits after updates, and no VPG conflict or DME missed-transmission status after mode changes.

Stream-encoder signals include successful HDMI modesets with deep color and scrambling where required, correct DIG source routing, stable TMDS output, expected FIFO status, no HDMI error interrupts left uncleared, and clean behavior when enabling/disabling double-buffered HDMI packet updates.

Because this file is generated register metadata rather than algorithmic code, the best regression coverage combines hardware register-database diffing, build coverage for every DCN 3.0.1 display path, and hardware smoke tests that exercise every AUX instance, packet slot, audio formatter path, metadata engine path, and HDMI/TMDS stream-encoder mode represented by this chunk.

### subset-b-001734: lines 29756-32176

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_1_sh_mask.h lines 29756-32176

## Scope

This chunk is a generated AMD DCN 3.0.1 ASIC register bitfield header segment. It contains preprocessor constants only: for each hardware register field, one `__SHIFT` macro gives the bit offset and one `_MASK` macro gives the bit mask. The chunk spans 2,421 source lines and includes 1,083 shift/mask pairs. It starts in the tail of the `DIG0` TMDS/DIG block and ends in the middle of the `DP1_DP_ALPM_CNTL` field list, so the file-level merge must reconcile this chunk with neighboring chunks for complete register coverage.

## Purpose

The purpose of this header segment is to expose symbolic bit positions for DCN display I/O MMIO programming. Driver code elsewhere can build, mask, read, or update register fields without open-coded numeric constants. The covered register groups are display encoder front/back end (`DIG0` tail and `DIG1`), DisplayPort stream/link/PHY/secondary-data registers (`DP0` and `DP1`), video packet generator registers (`VPG1`), audio formatter registers (`AFMT1`), and metadata engine registers (`DME1`).

The chunk is data-like source rather than executable logic. Its correctness depends on exact alignment with AMD hardware register specifications and with companion register-address headers for the same ASIC/IP version.

## Address Blocks And Register Surface

Visible address blocks:

- `dce_dc_dio_dp0_dispdec`: full `DP0` DisplayPort mask set from link control through GSP enable double-buffer status.
- `dce_dc_dio_dig1_vpg_vpg_dispdec`: `VPG1` generic packet, MPEG/ISRC data, update, status, and memory-power masks.
- `dce_dc_dio_dig1_afmt_afmt_dispdec`: `AFMT1` HDMI/DP audio formatter packet, IEC 60958 channel status, CRC, ramp-test, status, source, and memory-power masks.
- `dce_dc_dio_dig1_dme_dme_dispdec`: `DME1` metadata engine control and memory-power masks.
- `dce_dc_dio_dig1_dispdec`: `DIG1` encoder, HDMI packet/control, ACR, AFMT clock, TMDS, lane, and force-disable masks.
- `dce_dc_dio_dp1_dispdec`: `DP1` DisplayPort masks, mirroring most of `DP0`, through the partial `DP1_DP_ALPM_CNTL` section at this chunk boundary.

The chunk also includes the final `DIG0` definitions for TMDS DC balancer, sync DC-balance characters, DIG version, lane enables, and force-disable state.

## Important Macros And Register Families

`DIG0_*` and `DIG1_*` define digital encoder controls. Important fields include source selection, stereosync routing, start gating, digital bypass, input pixel selection, Dolby Vision enable/missed metadata indication, symbol-clock status, TMDS pixel/color format, output CRC control/result, FIFO status, HDMI metadata packet enable/line/missed state, HDMI scrambling/deep-color/error state, ACR packet fields, generic packet controls, double-buffer state, backend mode/HPD selection, lane enables, and force-disable controls.

`DP0_*` and `DP1_*` define DisplayPort link and stream controls. They cover link training completion/status, embedded-panel mode, pixel encoding/component depth/combine mode, MSA colorimetry/misc/timing/VBID fields, lane count, video stream enable/status/deferred disable/keepout, steer FIFO overflow and transfer-unit overflow status, M/N timing values, framing, HBR2 eye pattern, video interrupts, DPHY control/training/symbol/8b10b/PRBS/scrambler/CRC/MST CRC/fast-training fields, secondary packet enables and line references, audio M/N and readbacks, timestamp, packet control, MST stream allocation table (`MSE_SAT*`) programming/status, MSO secondary stream enables, DSC mode/slice width/bytes-per-pixel, metadata transmission, generic secondary packet (`GSP8`-`GSP11` for `DP0`), double-buffer control, and ALPM sleep/standby request state.

`VPG1_*` defines the video packet generator surface for generic packet access/data, GSP frame-update and immediate-update triggers for packets 0 through 14 plus Dolby Vision and HDR10 control points, generic packet pending/status, memory power state, ISRC packet access/data, and MPEG info payload bytes.

`AFMT1_*` defines audio formatter fields: VBI packet control, audio sample packet layout and HBR/flat-line/override controls, HDMI audio infoframe byte fields, IEC 60958 channel status words, audio CRC source/channel/count/result, ramp test counters, audio enable/HBR/FIFO-overflow/status-change flags, sample-send/test/channel-swap/update/ack fields, infoframe source/update controls, audio source select, and memory power.

`DME1_*` defines metadata engine control, including HUBP requestor ID, engine enable, stream type, double-buffer pending/taken/clear/disable state, and DME memory power state/default low-power state.

## Control Flow And Runtime Behavior

There is no C control flow in this chunk. Runtime behavior is indirect: display driver code includes this header and uses these macros with register-access helpers, usually through generated `*_SHIFT`/`*_MASK` tables or macros, to program MMIO registers.

The hardware-oriented flows represented by the bitfields are:

- Display enable sequencing: `DIG*_DIG_FE_CNTL`, `DIG*_DIG_BE_CNTL`, `DIG*_DIG_BE_EN_CNTL`, `DIG*_DIG_LANE_ENABLE`, and `DIG*_FORCE_DIG_DISABLE` expose source routing, encoder start, backend enable, lane clocking, and forced disable.
- DisplayPort stream setup: `DP*_DP_PIXEL_FORMAT`, `DP*_DP_CONFIG`, `DP*_DP_VID_TIMING`, `DP*_DP_VID_M`, `DP*_DP_VID_N`, MSA timing registers, and stream control macros provide the register fields needed before enabling a DP stream.
- Link training and PHY verification: `DP*_DP_LINK_CNTL`, DPHY training, fast training, PRBS, HBR2 pattern, CRC, and MST CRC masks expose training state, test pattern selection, and validation signals.
- Secondary packet delivery: `DP*_DP_SEC_CNTL*`, `DP*_DP_SEC_FRAMING*`, `DP*_DP_SEC_PACKET_CNTL`, `VPG1_*`, `AFMT1_*`, and `DIG1_HDMI_GENERIC_PACKET_CONTROL*` define packet enable, send, pending, active, missed-deadline, line-number, and double-buffer bits for audio/video metadata packets.
- MST/MSO allocation: `DP*_DP_MSE_*`, `DP*_DP_MSO_CNTL*`, and `DP*_DP_MSE_SAT*_STATUS` provide slot allocation, update, timing, and status bitfields.
- Power and low-power flows: `VPG1_VPG_MEM_PWR`, `AFMT1_AFMT_MEM_PWR`, `DME1_DME_MEMORY_CONTROL`, and `DP*_DP_ALPM_CNTL` expose memory power and DP main-link sleep/standby request/status fields.

## State And Persistence

The macros themselves hold no mutable state and introduce no storage. They describe persistent hardware state in memory-mapped display registers. Writes through these fields can affect persistent device state until the register is changed again, the display block is reset, or the GPU resumes/reinitializes.

Several field groups represent latched or handshake state:

- Double-buffer state: `*_DB_PENDING`, `*_DB_TAKEN`, `*_DB_TAKEN_CLR`, `*_DB_LOCK`, `*_DB_DISABLE`, and `*_VUPDATE_DB_*` fields indicate pending/taken updates and require correct clear/lock sequencing.
- Interrupt/status acknowledgement: `DP*_DP_VID_INTERRUPT_CNTL`, `DIG1_HDMI_CONTROL`, `DIG1_HDMI_STATUS`, `DIG1_HDMI_DB_CONTROL`, `AFMT1_AFMT_AUDIO_PACKET_CONTROL`, and DPHY fast-training/CRC status fields include flags and ack bits that must be handled according to write-one-to-clear or hardware-specific semantics in the register spec.
- Packet send state: GSP, HDMI generic, metadata, and secondary packet send/pending/active/deadline-missed fields model hardware packet schedulers and can reflect transient per-frame activity.
- Power state fields: `*_MEM_PWR_STATE`, `*_MEM_PWR_FORCE`, `*_MEM_PWR_DIS`, and ALPM pending bits expose hardware power-management state; stale or incorrect writes can block low-power entry or wake paths.

## Dependencies And Integration Points

This chunk depends on companion generated headers that define register addresses, base indices, and aggregate field lists for DCN 3.0.1. The naming convention matches AMDGPU display code patterns where register access macros combine a register symbol with `__FIELD__SHIFT` and `__FIELD_MASK` constants.

Likely integration points include:

- AMDGPU DC resource, link encoder, stream encoder, HDMI, DP, MST, DSC, audio, metadata, and power-management code that includes DCN ASIC register headers.
- Register helper macros/functions that read-modify-write fields by applying `MASK` and `SHIFT` constants.
- ASIC-version dispatch tables that choose the DCN 3.0.1 register layout for compatible GPUs.
- Diagnostics and self-test paths that use CRC, PRBS, FIFO error, packet status, fast-training status, and HDMI/AFMT overflow/error fields.

Because this is an include header, compile-time consumers are sensitive to exact macro names. Any rename, missing field, or changed mask silently redirects or breaks low-level hardware programming at all call sites that reference it.

## Risks And Edge Cases

- Generated-header drift is the main risk. A wrong bit mask or shift can corrupt unrelated fields in the same 32-bit register, causing display blanking, audio packet failure, DSC/MST misconfiguration, or power-management regressions.
- Repeated instance blocks (`DP0` vs `DP1`, `DIG0` vs `DIG1`) are mostly parallel but not byte-for-byte identical in this chunk. For example, `DP1_DP_VID_TIMING` in this slice lacks the visible `DP_VID_M_N_GEN_EN` field that appears for `DP0`, and `DP1_DP_ALPM_CNTL` is cut off at the chunk boundary. Merge/review must avoid assuming all instances are identical.
- Fields ending in `_MASK_MASK` are legitimate generated names for fields whose logical name includes `MASK`; tooling that splits on `_MASK` naively can misparse `DP*_DP_VID_INTERRUPT_CNTL__DP_VID_STREAM_DISABLE_MASK_MASK`, `DP*_DP_DPHY_CRC_CNTL__DPHY_CRC_MASK_MASK`, and similar definitions.
- Many packet-control groups use dense repeated fields for generic packet indexes. Off-by-one mistakes in generated constants or table consumers could route metadata/audio packets to the wrong slot or line.
- Status/ack fields and double-buffer clear fields have hardware-specific write semantics not represented in this header. Consumers must not infer safe write values from the masks alone.
- The chunk begins after the start of a `DIG0` register group and ends before the full `DP1_DP_ALPM_CNTL` mask list, so file-level research must include adjacent chunks before drawing whole-file completeness conclusions.

## Test Signals

Useful validation signals for this chunk are mostly build-time and hardware/display regression signals:

- Compile coverage for AMDGPU DCN 3.0.1 paths catches missing or renamed macros used by driver code.
- Generated-header consistency checks can compare each `__SHIFT` field with a matching `_MASK` field, verify masks fit within 32 bits, and verify that repeated instance families retain expected parity where the hardware spec requires it.
- Display bring-up tests should exercise DP0 and DP1 link training, stream enable/disable, mode changes, MST slot allocation, MSO, DSC, HDMI deep-color/scrambling, audio packet output, metadata packets, and ALPM transitions.
- Runtime diagnostics should watch FIFO overflow, steer/TU overflow, HDMI audio/VBI packet errors, AFMT FIFO overflow, DPHY CRC validity, MST CRC phase errors, fast-training completion, GSP deadline-missed flags, and double-buffer pending/taken bits.
- Suspend/resume and power-gating tests should verify `VPG1`, `AFMT1`, `DME1`, and DP ALPM memory/power fields are restored or reprogrammed correctly.

## Open Questions For Merge Lane

- Confirm adjacent chunks include the full opening context for `DIG0_TMDS_DCBALANCER_CONTROL` and the remaining `DP1_DP_ALPM_CNTL` mask definitions.
- Compare the DCN 3.0.1 generated masks with the matching address header and any `*_DEFAULT` or field-list headers to identify whether differences between `DP0` and `DP1` are intentional hardware differences or chunk-boundary artifacts.
- Identify actual consumers of the `DIG1`, `DP0`, `DP1`, `VPG1`, `AFMT1`, and `DME1` macros in the AMDGPU display driver before the final per-file report describes concrete call sites.

### subset-b-001735: lines 32177-34584

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_1_sh_mask.h lines 32177-34584

## Scope And Purpose

This chunk is part of AMD's generated DCN 3.0.1 register field mask header. It contains C preprocessor constants for hardware bit positions (`__SHIFT`) and bit masks (`_MASK`) rather than executable driver code. The covered range starts at the tail of `DP1_DP_ALPM_CNTL`, finishes late DisplayPort secondary-packet fields for `DP1`, covers complete `DIG2` VPG/AFMT/DME/DIG and `DP2` DIO blocks, then begins the `DIG3` VPG/AFMT/DME/DIG block and ends inside `DIG3_HDMI_GENERIC_PACKET_CONTROL0`.

In driver terms, this header is the field-layout half of the DCN 3.0.1 MMIO contract. The matching offset header supplies register addresses; this file supplies the per-field masks and shifts used by AMD display register helpers to pack and extract values. The hardware areas represented here drive DisplayPort stream/link setup, secondary-data-packet scheduling, multi-stream allocation, HDMI packet and audio formatting, generic packet RAM access, metadata transport, DIO/DIG enablement, TMDS test/control patterns, CRC/readback diagnostics, and memory power state for VPG/AFMT/DME engines.

There are no functions, structs, local variables, or runtime branches in this chunk. Its value is the stable macro naming contract that lets common DC display code target repeated hardware instances by prefix, such as `VPG2_`, `AFMT2_`, `DIG2_`, `DP2_`, `VPG3_`, `AFMT3_`, `DME3_`, and `DIG3_`.

## Register Blocks Covered

The first lines complete the end of a previous `DP1` block, including `DP1_DP_ALPM_CNTL` masks and `DP1_DP_GSP8_CNTL` through `DP1_DP_GSP11_CNTL`. These generic secondary-packet controls expose MSO packet enables, packet send triggers, send-in-idle/send-any-line behavior, pending/active/deadline-missed status, and line-number placement. `DP1_DP_GSP_EN_DB_STATUS` adds per-GSP double-buffer pending bits for GSP0 through GSP11.

`dce_dc_dio_dig2_vpg_vpg_dispdec` covers the Video Packet Generator instance 2. It defines indexed packet RAM access (`VPG2_VPG_GENERIC_PACKET_ACCESS_CTRL`, `VPG2_VPG_GENERIC_PACKET_DATA`), frame-synchronized and immediate update controls for generic packet slots 0 through 14, generic lock/conflict status, VPG memory power state, ISRC indexed data, and MPEG infoframe payload/update fields.

`dce_dc_dio_dig2_afmt_afmt_dispdec` covers Audio Formatter instance 2. It includes HDMI audio packet pacing, audio layout/channel/stream-id controls, HDMI audio infoframe words, IEC 60958 channel-status fields, audio CRC controls/results, ramp/test-pattern controls, audio FIFO/status bits, audio sample-send and overflow/change acknowledgements, audio infoframe update source, audio-source select, and AFMT memory power controls.

`dce_dc_dio_dig2_dme_dme_dispdec` covers Display Metadata Engine instance 2. Its fields identify the HUBP metadata requestor, enable the metadata engine, select stream type, expose metadata double-buffer pending/taken/clear/disable state, and control DME memory power/default low-power state.

`dce_dc_dio_dig2_dispdec` covers Digital Encoder instance 2. It starts with DIG front-end selection and output CRC/test-pattern/FIFO fields, then defines HDMI metadata, HDMI control/status, audio delay, ACR, VBI, infoframe, generic-packet scheduling and line-placement, HDMI DB control, ACR programmed/status values for 32/44.1/48 kHz families, AFMT clock enable/status, DIG back-end mode/HPD/source routing, TMDS control patterns, lane enablement, DIG version, and forced disable.

`dce_dc_dio_dp2_dispdec` covers DisplayPort instance 2. This is the largest block in the chunk and includes link status/configuration, pixel format, MSA colorimetry/misc/timing, video stream enable/status, steer FIFO overflow handling, DPHY training/scrambler/FEC/CRC/fast-training controls, secondary packet and audio M/N controls, MST MSE rate and slot allocation tables/status, MSO, DSC, ALPM, secondary metadata transmission, DB control, GSP8 through GSP11 controls, and GSP enable double-buffer status.

The range then begins the next repeated DIO instance. `VPG3`, `AFMT3`, and `DME3` mirror the VPG/AFMT/DME2 layouts for instance 3. The final `DIG3` section covers front-end, output CRC, test pattern, FIFO, HDMI metadata/control/status, ACR/VBI/infoframe controls, and starts `DIG3_HDMI_GENERIC_PACKET_CONTROL0` through the mask for `HDMI_GENERIC4_SEND`. The rest of the DIG3 generic-packet block continues in the next chunk.

## Important APIs, Types, And Macros

The exported surface is entirely macro based:

- `<instance>_<register>__<field>__SHIFT` gives the field's low bit position in a 32-bit MMIO register.
- `<instance>_<register>__<field>_MASK` gives the already-shifted field mask.
- Register comments, for example `//DP2_DP_SEC_CNTL`, delimit logical register groups for humans and generated diff review.
- Address-block comments, for example `// addressBlock: dce_dc_dio_dp2_dispdec`, identify the replicated hardware block that owns the following register names.

Consumers normally reach these constants indirectly through AMD display register helpers such as `SRI`, `SF`, `SE_SF`, `REG_FIELD`, `REG_GET`, `REG_SET`, and `REG_UPDATE`. The repeated prefixes in this chunk are intentionally compatible with common register-list macros in the display tree. For example, VPG code uses fields such as `VPG_GENERIC_PACKET_ACCESS_CTRL`, `VPG_GENERIC_PACKET_DATA`, `VPG_GSP_FRAME_UPDATE_CTRL`, `VPG_GSP_IMMEDIATE_UPDATE_CTRL`, and `VPG_MEM_PWR`; AFMT code uses `AFMT_AUDIO_PACKET_CONTROL`, `AFMT_AUDIO_PACKET_CONTROL2`, `AFMT_60958_*`, `AFMT_AUDIO_SRC_CONTROL`, and `AFMT_MEM_PWR`; DP/DIG encoder code uses the corresponding `DP_*`, `HDMI_*`, `DIG_*`, and `TMDS_*` fields.

No C type is defined here. The implicit type model is 32-bit register words, with callers responsible for shifting, masking, and clamping values before MMIO access.

## Functional Areas

Generic and secondary packet programming is represented in three forms. VPG registers provide indexed packet payload RAM and update triggers for generic packet slots 0-14. HDMI generic-packet registers schedule packet send/continuous modes, line references, update-lock bypass, immediate-send requests, line numbers, and DB-pending status. DP secondary-packet registers schedule ASP/ATP/AIP/ACM/GSP/ISRC/MPG packets, line numbers, send triggers, send-active/send-in-idle status, and deadline-missed reporting.

DisplayPort link and stream fields cover link-training completion/status, embedded-panel mode, UDI lane count, pixel encoding/component depth, MSA misc/colorimetry/timing, video stream enable/deferred disable/status, VBID/enhanced framing, DPHY scrambler and bypass selection, FEC enable/ready/active status, training pattern selection, 8b/10b reset, PRBS/scrambler controls, CRC enable/result/MST slot selection, and fast-training state/interrupt acknowledgement.

DP MST/MSO/DSC support appears through `DP2_DP_MSE_*`, `DP2_DP_MSO_*`, and `DP2_DP_DSC_*` fields. The MSE fields configure rate X/Y, slot allocation table entries for sources 0-5, update-pending state, link timing, misc controls, and SAT readback/status. MSO fields control secondary-link count/selection and pixel/stream width behavior. DSC fields control DSC enable/mode and bytes-per-pixel metadata.

HDMI and TMDS fields cover metadata packet line scheduling, AVMUTE/general-control packets, HDMI scrambling, clock-channel rate, deep color, error acknowledgement/masking, ACR send/source/auto-send/N-multiple, null/GC/ISRC VBI packet controls, audio and MPEG infoframe send/continuous/line fields, TMDS control characters, sync character patterns, DC balancer controls, and lane/clock enables.

Audio formatter fields cover audio channel enablement, DP audio stream ID, HDMI audio packet count limits, audio layout override/select, 60958 channel-status words and per-channel numbers, audio sample send and double-buffer enable, FIFO overflow/change acknowledgements, channel swap, audio test/ramp generation, CRC capture, and memory power state.

Metadata and memory-power fields include DME requestor/engine/stream-type and metadata DB state, `VPG*_VPG_MEM_PWR`, `AFMT*_AFMT_MEM_PWR`, and `DME*_DME_MEMORY_CONTROL`. These let the display driver or power-management paths force, disable, or observe low-power state for packet/audio/metadata RAMs.

Diagnostics and status fields include output CRC control/results, DPHY CRC results, FIFO level/error/calibration status, HDMI audio/VBI packet errors, metadata missed bits, GSP send pending/active/deadline flags, MSE SAT status, DP link and video stream status, and DIG clock/frontend/backend enable status.

## Control Flow And State Behavior

This header has no local control flow. Runtime behavior is created when DCN 3.0.1 display modules include this generated mask header, bind these fields to register addresses from the companion offset header, and invoke register-helper macros. A typical path constructs an instance-specific register table, then calls `REG_UPDATE` or `REG_GET` against logical field names; macro expansion selects the concrete `DP2_`, `DIG2_`, `VPG3_`, or similar mask and shift.

The state described by these fields lives in hardware registers, not in this file. Configuration fields persist in the display engine until rewritten or reset, including packet payload bytes, line numbers, link/framing options, audio formatter settings, ACR N/CTS values, MST slot allocations, and memory-power controls. Status fields are live hardware observations, including pending DB updates, send-active flags, FIFO level/error state, CRC results, link/stream state, and power-state readbacks. Event/interrupt-style fields are indicated by names such as `*_ACK`, `*_CLR`, `*_PENDING`, `*_MISSED`, `*_ERROR_INT`, and `*_MASK`; callers must follow the hardware write-to-clear or acknowledge semantics.

Many packet controls are double-buffered or synchronized to frame/update boundaries. VPG frame-update, VPG immediate-update, HDMI DB, DP DB, MSE rate/SAT update, metadata DB, and GSP enable DB fields represent pending/taken state. Incorrect sequencing can leave new packet data pending for the wrong frame, collide with a lock, miss a packet deadline, or expose stale metadata/audio information on the link.

## Dependencies And Integration Points

This chunk depends on the DCN 3.0.1 hardware register database and must stay aligned with `dcn_3_0_1_offset.h`, which supplies the MMIO addresses for the same register names. The file is included directly by the DCN 3.0.1 DMUB implementation (`display/dmub/src/dmub_dcn301.c`) and is part of the broader generated-register include set consumed by DCN 3.0.1 display code.

Important integration points are the DIO encoder/link/audio/packet subsystems under `drivers/gpu/drm/amd/display`. VPG register-list code maps the generic packet access/data/update/memory-power fields used here. AFMT register-list code maps the audio info, 60958, audio packet, source-select, and memory-power fields. DIG/DP encoder paths use these masks to program HDMI, TMDS, DisplayPort, DSC, MST/MSO, secondary-packet, link-training, and CRC registers.

Higher-level display workflows that depend on these definitions include link enable/disable, DisplayPort link training and fast training, HDMI mode setup, audio enablement and channel-status programming, infoframe and HDR/static metadata packet transmission, DP MST allocation, DSC transport setup, low-power memory gating, debug CRC collection, and interrupt/error acknowledgement for FIFO/link/packet conditions.

Although the repository path is under `sources/distributed-fs/ceph-client`, this file is imported Linux AMD GPU display driver code and is not Ceph filesystem logic.

## Risks And Edge Cases

The primary risk is generated-register drift. A one-bit error in a `_MASK` or `__SHIFT` value can make otherwise correct driver code write adjacent hardware fields, fail to acknowledge status, or read misleading diagnostics. This is especially risky in tightly packed registers such as HDMI generic-packet controls, VPG update bitmaps, DP secondary-packet controls, MSE slot allocation tables, and AFMT 60958 channel-status words.

The chunk boundaries are partial. It starts after the beginning of `DP1_DP_ALPM_CNTL` and ends partway through `DIG3_HDMI_GENERIC_PACKET_CONTROL0`; final per-file reconciliation must combine adjacent chunks before claiming complete `DP1` or `DIG3` coverage.

Instance replication can hide defects. The `VPG2` and `VPG3`, `AFMT2` and `AFMT3`, and `DME2` and `DME3` groups are structurally mirrored, while `DIG2` and `DP2` are complete enough to exercise large independent hardware paths. A generation error in only one instance may show up as a pipe-specific failure rather than an obvious compile problem.

Packet timing fields are mode- and frame-phase-sensitive. Bad line numbers, line-reference bits, immediate-send triggers, update-lock-disable bits, or DB disable/pending controls can cause packets to be sent on the wrong line, never sent, sent during idle unexpectedly, or missed under deadline pressure.

Status and acknowledge fields are easy to misuse. Confusing `*_PENDING`, `*_TAKEN`, `*_TAKEN_CLR`, `*_ACK`, `*_MASK`, and error-status masks can leave interrupts stuck, clear evidence before it is sampled, or allow packet/FIFO/link errors to go unreported.

Value-width truncation is another risk. Many fields are small packed quantities: 6-bit MST slots, 8-bit payload bytes and infoframe fields, 16-bit line positions, 20-bit ACR N/CTS values, and 24-bit audio/video M/N values. Callers must validate values before packing because this header only masks; it does not enforce semantic ranges.

## Test Signals

Build-time coverage is the first signal. DCN 3.0.1 display and DMUB objects that include `dcn_3_0_1_sh_mask.h` should compile without missing `DP2_*`, `DIG2_*`, `VPG*_*`, `AFMT*_*`, or `DME*_*` field identifiers in register tables and helper macros.

Static validation should compare this generated header against AMD's authoritative register database and adjacent DCN generations for expected replicated layouts. High-signal checks include matching `VPG2`/`VPG3` and `AFMT2`/`AFMT3` field shapes, verifying `DP2` secondary-packet and MSE/MSO/DSC masks, and confirming the companion offset header has corresponding register addresses.

Runtime validation should exercise DCN 3.0.1 hardware paths that use instance 2 and 3 DIO blocks: HDMI modes with infoframes, metadata packets, AVMUTE, ACR, deep-color/scrambling, and TMDS patterns; DP modes with link training, FEC/scrambler settings, MSA programming, secondary packets, MST slot allocation, MSO, DSC, and ALPM; and audio enablement with channel layout, channel status, sample-send, and FIFO overflow handling.

Diagnostic signals include output CRC and DPHY CRC readback, FIFO status staying clear of level errors, GSP/HDMI/DP packet pending bits draining after updates, no deadline-missed flags during metadata/infoframe transmission, correct MSE SAT status after MST allocation, and memory-power state readbacks matching low-power entry/exit requests.

### subset-b-001736: lines 34585-36968

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_1_sh_mask.h lines 34585-36968

## Scope

This chunk is a generated AMDGPU DCN 3.0.1 register shift/mask header slice. It contains only preprocessor constants of the form `<REGISTER>__<FIELD>__SHIFT` and `<REGISTER>__<FIELD>_MASK`, plus generated register/address-block comments. There are no C functions, structs, enums, storage objects, or executable branches in this range.

The range starts mid-register in the `DIG3_HDMI_GENERIC_PACKET_CONTROL0` mask list and ends inside the `DC_GPIO_RXEN` shift list. Complete interpretation of both boundary registers requires adjacent chunks. Inside those boundaries, this slice covers:

- `DIG3` HDMI/audio/video packet and TMDS fields.
- The `dce_dc_dio_dp3_dispdec` address block for DisplayPort link `DP3`.
- The `dce_dc_dcio_dcio_dispdec` address block for DCIO, UNIPHY, panel power sequencing, and backlight PWM fields.
- The beginning of the `dce_dc_dcio_dcio_chip_dispdec` chip GPIO address block, including generic GPIO, DDC/AUX, genlock/swaplock, HPD, panel power GPIO, pad strength, AUX/HPD electrical controls, and the start of RX-enable fields.

Across lines 34585-36968, the chunk contains 2,384 source lines, 199 register/address-block comments, 1,090 `__SHIFT` defines, and 1,247 `_MASK` defines.

## Purpose

The purpose of this header region is to encode the DCN 3.0.1 hardware bit layout used by AMD display code when programming one display output path and shared DCIO/GPIO infrastructure. The companion `dcn_3_0_1_offset.h` header supplies register addresses and base indices; this file supplies the field positions and masks consumed by register helper macros such as `FD_MASK`, `FD_SHIFT`, `REG_GET`, `REG_SET`, and `REG_UPDATE`.

At a subsystem level, the slice describes:

- HDMI generic packet scheduling, immediate-send state, ACR values for 32/44/48 kHz audio families, audio formatter clock control, digital backend selection, TMDS lane/control-character behavior, and HDMI double-buffer control for `DIG3`.
- DisplayPort stream programming for `DP3`, including link status, pixel format, MSA colorimetry/misc fields, stream enable/status, FIFO overflow flags, DPHY scrambler/training/CRC controls, secondary-data/audio packet controls, MST/MSE slot allocation, DSC, ALPM, and GSP packet transmission state.
- DCIO clock/reference selection, UNIPHY link and channel crossbar control for PHYs A-D, write-command delays, pin straps, panel power sequence and backlight PWM control for panel instances 0 and 1, genlock/swaplock pads, and soft-reset bits for UNIPHY/DSYNC/DCRXPHY/ZCAL paths.
- GPIO pad ownership and state for generic, DDC, DDCVGA, genlock, HPD, and panel power sequence pins, plus pad strength and AUX/HPD electrical tuning fields.

This is part of the generated hardware contract. Driver code should not hard-code these bit positions in implementation files; it should consume the generated names so register tables and ASIC-specific code remain aligned with the register database.

## Important APIs, Types, And Macros

There are no callable APIs or local types in this chunk. The exported interface is the macro namespace itself:

- `<REGISTER>__<FIELD>__SHIFT`: bit offset for a field.
- `<REGISTER>__<FIELD>_MASK`: 32-bit mask for the same field.
- Comments such as `//DP3_DP_SEC_CNTL` and `//DC_GPIO_DDC1_MASK` group fields by hardware register.
- Address-block comments such as `// addressBlock: dce_dc_dio_dp3_dispdec` identify generated register blocks.

Important register families in this chunk include:

- HDMI/DIG3 packet and TMDS fields: `DIG3_HDMI_GENERIC_PACKET_CONTROL5/6/1..10`, `DIG3_HDMI_GC`, `DIG3_HDMI_DB_CONTROL`, `DIG3_HDMI_ACR_*`, `DIG3_AFMT_CNTL`, `DIG3_DIG_BE_CNTL`, `DIG3_DIG_BE_EN_CNTL`, `DIG3_TMDS_*`, `DIG3_DIG_LANE_ENABLE`, and `DIG3_FORCE_DIG_DISABLE`.
- DP3 link and stream fields: `DP3_DP_LINK_CNTL`, `DP3_DP_PIXEL_FORMAT`, `DP3_DP_CONFIG`, `DP3_DP_VID_STREAM_CNTL`, `DP3_DP_STEER_FIFO`, `DP3_DP_VID_TIMING`, `DP3_DP_VID_N`, `DP3_DP_VID_M`, `DP3_DP_LINK_FRAMING_CNTL`, `DP3_DP_VID_MSA_VBID`, and `DP3_DP_VID_INTERRUPT_CNTL`.
- DP3 physical/link-test fields: `DP3_DP_DPHY_CNTL`, `DP3_DP_DPHY_TRAINING_PATTERN_SEL`, `DP3_DP_DPHY_SYM0/1/2`, `DP3_DP_DPHY_8B10B_CNTL`, `DP3_DP_DPHY_PRBS_CNTL`, `DP3_DP_DPHY_SCRAM_CNTL`, CRC control/result/status registers, fast training registers, and HBR2 pattern control.
- DP3 secondary-stream, audio, MST, and DSC fields: `DP3_DP_SEC_CNTL*`, `DP3_DP_SEC_FRAMING*`, `DP3_DP_SEC_AUD_*`, `DP3_DP_SEC_PACKET_CNTL`, `DP3_DP_MSE_*`, `DP3_DP_MSA_TIMING_PARAM*`, `DP3_DP_MSO_CNTL*`, `DP3_DP_DSC_CNTL`, `DP3_DP_DSC_BYTES_PER_PIXEL`, `DP3_DP_SEC_METADATA_TRANSMISSION`, `DP3_DP_ALPM_CNTL`, `DP3_DP_GSP8_CNTL` through `DP3_DP_GSP11_CNTL`, and `DP3_DP_GSP_EN_DB_STATUS`.
- DCIO and PHY fields: `DC_GENERICA`, `DC_GENERICB`, `DCIO_CLOCK_CNTL`, `DC_REF_CLK_CNTL`, `UNIPHYA/B/C/D_LINK_CNTL`, `UNIPHYA/B/C/D_CHANNEL_XBAR_CNTL`, `DCIO_WRCMD_DELAY`, `DC_PINSTRAPS`, `DCIO_GSL_GENLK_PAD_CNTL`, `DCIO_GSL_SWAPLOCK_PAD_CNTL`, and `DCIO_SOFT_RESET`.
- Panel and backlight fields: `PANEL_PWRSEQ0_*`, `BL_PWM0_*`, `PANEL_PWRSEQ1_*`, and `BL_PWM1_*`, including power target/state, timing delays, reference dividers, PWM period/duty/fractional enable, group lock, update-pending, frame-start update, and readback controls.
- GPIO fields: `DC_GPIO_GENERIC_*`, `DC_GPIO_DDC1_*` through `DC_GPIO_DDC4_*`, `DC_GPIO_DDCVGA_*`, `DC_GPIO_GENLK_*`, `DC_GPIO_HPD_*`, `DC_GPIO_PWRSEQ0_*`, `DC_GPIO_PWRSEQ1_*`, `DC_GPIO_PAD_STRENGTH_1/2`, `PHY_AUX_CNTL`, `DC_GPIO_TX12_EN`, `DC_GPIO_AUX_CTRL_0/1/2`, and the start of `DC_GPIO_RXEN`.

The generated pattern is mostly all shifts first followed by all masks for each register. Fields with names ending in `_MASK` as part of the hardware field name, for example `DP_STEER_OVERFLOW_MASK`, produce generated symbols with `_MASK_MASK`; those are expected and should not be simplified manually.

## Control Flow

This chunk has no runtime control flow. Its practical flow is compile-time macro expansion:

1. DCN 3.0.1 implementation files include `dcn/dcn_3_0_1_offset.h` and `dcn/dcn_3_0_1_sh_mask.h`.
2. Register-table macros concatenate register and field names to resolve the shift/mask constants in this file.
3. Runtime code uses the resolved constants to compose MMIO writes, extract MMIO read fields, or populate ASIC-specific register tables.
4. Hardware sequencing, ordering, waits, acknowledgements, and side effects are implemented in display, GPIO, DIO, panel, audio, and DMUB code; this header only supplies bit placement.

Observed direct include points for the DCN 3.0.1 offset/mask pair are:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn301/dcn301_resource.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn301.c`

The `dcn301_resource.c` file then wires the generated constants into resource objects for link encoders, stream encoders, audio, panel control, GPIO/I2C/AUX, clocks, DCCG, hubbub, DSC, DWB, and DMUB-facing infrastructure.

## State And Persistence Behavior

The header itself stores no software state and persists no data. It describes hardware register state owned by the GPU display block:

- HDMI/DIG state includes generic packet send/continuous/immediate-send/pending controls, generic packet line numbers, AVMUTE/default phase/packing phase, ACR CTS/N fields and status, audio formatter clock enable/on state, DIG backend source/mode/HPD selection, TMDS control character and DC-balance settings, lane enable state, and double-buffer pending/taken/lock/disable flags.
- DP3 state includes link-training completion/status, embedded panel mode, pixel encoding/depth, stream enable/status/deferred disable, M/N timing values, link framing, video interrupt status/ack/mask, FIFO/TU overflow flags, DPHY FEC/scrambler/bypass/test state, training pattern selection, PRBS/CRC/test symbol fields, fast training controls, secondary-data/audio packet enables, MST allocation slots, DSC enable and bytes-per-pixel programming, ALPM requests, and GSP packet send/pending/deadline state.
- DCIO/UNIPHY state includes reference/output clock selection, UNIPHY power-frequency-change and pixel-valid reset state, lane invert/crossbar/link-enable programming, HPD-gated link enable behavior, lane stagger delay, write-command delay knobs, pin strap readback, and soft-reset bits for PHY/display-sync blocks.
- Panel/backlight state includes panel power sequence enable/target/state/done flags, DIGON/SYNCEN/BLON control and override bits, power-up/power-down delays, PWM reference divider, PWM period and active fractional count, PWM enable, and group lock/update-pending state.
- GPIO state includes software mask/enable/output/readback fields, pull-down or power-down controls, AUX pad mode/polarity, DDC line strength, HPD delayed/raw sense and receive fields, panel power GPIO fields, pad drive strength, AUX/HPD slew/spike filter/bias/receiver/comparator tuning, and TX12/RXEN routing.

Persistence is hardware-defined. Many control fields remain effective until a modeset, link reconfiguration, backlight update, GPIO ownership change, power-gating transition, suspend/resume path, or ASIC reset reprograms them. Status and pending fields can change asynchronously with link training, secondary packet sends, hotplug activity, panel power sequencing, or hardware double-buffer updates. The generated masks do not encode read-only, write-one-to-clear, or side-effect semantics, so callers must follow the hardware programming model.

## Dependencies And Integration Points

This chunk depends on generated register metadata staying synchronized across files:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_1_offset.h` pairs with this header by providing register offsets and base-index constants.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn301/dcn301_resource.c` includes the pair and uses resource macros such as `SR`, `SRI`, `SRII`, and field macros to populate DCN301 register, shift, and mask tables.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn301.c` includes the pair and builds DMUB common register field masks/shifts with `FD_MASK` and `FD_SHIFT`.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dcn301/dcn301_panel_cntl.h` maps panel/backlight fields from this chunk into `struct dcn301_panel_cntl_shift` and `struct dcn301_panel_cntl_mask`.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dcn301/dcn301_panel_cntl.c` consumes those fields for panel power/backlight initialization, status checks, backlight level reads, and stored level handling.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dio/dcn301/dcn301_dio_link_encoder.c` constructs DCN301 link encoders for UNIPHY transmitters A-G; the UNIPHY and DIG/DP fields in this chunk are part of the register namespace used by related DIO/link encoder paths.
- GPIO service, hardware factory, and translate layers in `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/` consume the same generic register model for DDC, HPD, generic GPIO, and genlock/swaplock ownership and translation.
- Audio and stream encoder paths rely on the DIG/HDMI/DP secondary-packet and ACR field definitions when HDMI/DP audio and info packets are programmed through DCN resource tables.

The direct contract is preprocessor name stability. A missing or renamed define usually fails at build time when a register table expands. A numerically wrong shift or mask can compile cleanly and cause bad MMIO behavior at runtime.

## Risks And Edge Cases

- The chunk starts after the shifts and early masks for `DIG3_HDMI_GENERIC_PACKET_CONTROL0`. Whole-file reconciliation must not treat this chunk alone as the complete definition for that register.
- The chunk ends before the `DC_GPIO_RXEN` masks and before later GPIO chip fields. Adjacent chunks are required for a complete RX-enable and chip GPIO view.
- Several field names naturally include `MASK`, which produces symbols such as `DP_STEER_OVERFLOW_MASK_MASK` and `DCIO_GENLK_CLK_GSL_MASK_MASK`. These are generated names, not typographical duplicates.
- Wrong HDMI generic packet, ACR, or double-buffer masks can produce silent audio/infoframe failures, stale metadata transmission, missed immediate sends, or incorrect CTS/N programming.
- DP3 contains many status, pending, ack, interrupt, CRC, training, FEC, MST, DSC, ALPM, and GSP fields. Treating these as ordinary read/write control bits can cause interrupt storms, missed acknowledgements, link training instability, or secondary-packet timing failures.
- DP MSE/MST allocation and MSO fields pack slot, timing, and stream data into narrow bit ranges. Numeric drift can affect only MST, DSC, or multi-stream cases, making failures topology-dependent.
- UNIPHY link and channel crossbar fields are repeated for PHYs A-D. Copy/generator drift in one instance can make failures connector-specific while other ports still work.
- Soft-reset masks for UNIPHY, DSYNC, DCRXPHY, and ZCAL are side-effect-sensitive. Incorrect or stale bit positions can reset the wrong hardware block or leave a block held in reset.
- Panel power sequence and PWM fields directly affect embedded panel power, backlight timing, and brightness. Bad masks can cause black panels, flicker, incorrect brightness readback, or unsafe sequencing around DIGON/BLON/SYNCEN.
- GPIO DDC/AUX/HPD fields are shared with connector detection and I2C/AUX transactions. Incorrect ownership, pull-down, pad mode, polarity, or receive-enable masks can break EDID reads, HPD detection, DP AUX communication, or wake/hotplug routing.
- AUX/HPD electrical tuning fields (`FALLSLEWSEL`, spike filter, bias/current/resistance/comparator/slew settings) should be changed only according to hardware guidance; the header cannot express board-specific signal-integrity constraints.
- Cross-ASIC reuse is risky. Many names resemble DCN 3.0.0 or DCN 3.0.2 headers, but DCN301-specific field layout should be treated as authoritative for Vangogh/DCN301.

## Test Signals

Useful validation signals for this generated-header chunk are build-time macro expansion plus hardware behavior on DCN301-class systems:

- Build AMDGPU display code with DCN301 enabled so `dcn301_resource.c`, `dmub_dcn301.c`, panel control, DIO, GPIO, audio, and DMUB register tables expand this header successfully.
- Compare this range against the register generator output and `dcn_3_0_1_offset.h` to ensure every register used by the resource tables has matching offset, shift, and mask definitions.
- Exercise HDMI output on the `DIG3` path, including generic info packets, AVMUTE, audio formatter clocking, ACR status, and packet double-buffer updates.
- Exercise DisplayPort link bring-up on the `DP3` path across SST, MST if supported, DSC, secondary-data packet transmission, audio, link retraining, suspend/resume, and hotplug/unplug cycles.
- Run DP link-training diagnostics that cover DPHY training pattern, FEC readiness/active status, scrambler state, CRC readback, PRBS/test-symbol paths, and fast-training status.
- Validate MST/MSE allocation and MSO/DSC paths with multi-stream or compressed modes, watching for slot allocation errors, deadline-missed GSP status, and MSA/VBID anomalies.
- Test embedded panel power sequencing and backlight control through brightness changes, DPMS off/on, boot splash handoff, suspend/resume, and backlight readback. Watch `PANEL_PWRSEQ*_STATE`, `BL_PWM*_GRP1_REG_UPDATE_PENDING`, and PWM enable/period/duty behavior.
- Exercise HPD, DDC, AUX, and GPIO paths across all available connectors: EDID reads, HPD IRQs, HPD RX sense, DP AUX transactions, DDCVGA if present, genlock/swaplock pins if supported, and generic GPIO ownership transitions.
- Check reset and recovery paths that touch `DCIO_SOFT_RESET`, UNIPHY link state, panel power sequencing, and GPIO receive-enable state after GPU reset or display core reinitialization.

## Cross-Chunk Notes

This chunk is a middle slice of a large generated mask header. The final per-file report should merge it with adjacent chunks to describe the full `DIG3`, `DP3`, DCIO, and GPIO chip field maps. In particular, adjacent chunks are needed for the beginning of `DIG3_HDMI_GENERIC_PACKET_CONTROL0` and the rest of `DC_GPIO_RXEN`.

### subset-b-001737: lines 36969-39480

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_1_sh_mask.h lines 36969-39480

## Purpose

This chunk is generated AMD DCN 3.0.1 register field metadata. It contains no executable C code; it publishes C preprocessor constants that name bit positions (`__SHIFT`) and bit masks (`_MASK`) for DCN display-controller MMIO registers. Driver code combines these macros with the matching `dcn_3_0_1_offset.h` register offsets through AMD display helper macros such as `REG_SET`, `REG_UPDATE`, `REG_GET`, `SRI`, `SR`, and block-specific field-list macros.

The requested range starts in the tail of `DC_GPIO_RXEN`, then covers GPIO pull-up and AUX/DDC pad controls, three complete UNIPHY reserved macro-control address blocks, DSC compressor instances 0 through 2, DSC-local perfmon blocks 17 through 19, the first display writeback top/perfmon/control-processing registers, and ends inside the `DWB_GAMUT_REMAPA_C11_C12` field definitions. The slice has 2,101 `#define` lines, with 1,043 shift definitions and 1,058 mask definitions.

Although the path is under a local `ceph-client` source mirror, the content is AMDGPU display-driver hardware metadata. It does not implement Ceph or distributed filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, global variables, includes, locks, allocations, or persistence APIs in this chunk. The public interface is the macro namespace:

- `<REGISTER>__<FIELD>__SHIFT`: the least-significant bit position for a field in a 32-bit MMIO register.
- `<REGISTER>__<FIELD>_MASK`: the bit mask used to isolate or update that field.
- Address-block comments such as `dce_dc_dsc0_dispdec_dscc_dispdec`: generator breadcrumbs that group registers by display hardware block.

Major macro families in this slice:

- `DC_GPIO_RXEN`, `DC_GPIO_PULLUPEN`, `DC_GPIO_AUX_CTRL_3`, `DC_GPIO_AUX_CTRL_4`, `DC_GPIO_AUX_CTRL_5`, and `AUXI2C_PAD_ALL_PWR_OK`: GPIO receiver enables, pull-ups, AUX termination/swap/hysteresis, AUX drive tuning, DDC I2C mode and voltage-domain controls, and AUX/I2C pad power-good bits for PHYs 1 through 6.
- `DCIO_UNIPHY[1-3]_UNIPHY_MACRO_CNTL_RESERVED[0-47]`: repeated full-register reserved fields, each exposing a shift of zero and a 32-bit mask. These preserve symbolic access to reserved UNIPHY macro-control apertures for generated register tables and debug paths.
- `DSC_TOP[0-2]`: DSC clock enable, display-clock gate-disable, DSCCLK gate-disable, debug enable, and test-clock mux fields.
- `DSCCIF[0-2]`: DSC client-interface underflow recovery/status/interrupt, input pixel format, bits per component, double-buffer update pending, picture width, and picture height fields.
- `DSCC[0-2]`: DSC compressor configuration, status, interrupt/status/enable fields, PPS payload fields (`DSCC_PPS_CONFIG0` through `DSCC_PPS_CONFIG22`), memory power control, squared-error and max-absolute-error counters, rate-buffer/fullness counters, and test debug bus rotation.
- `DC_PERFMON17`, `DC_PERFMON18`, `DC_PERFMON19`, and `DC_PERFMON20`: event selection, counted-value selection, increment/run modes, counter active/interrupt state, perfmon report count, count-off interrupt control, high/low counter-value access, and per-counter interrupt status/ack fields.
- `DWB_*` and `FC_*`: display writeback enable/clock controls, memory power controls, frame-capture mode/rate/crop/stereo/current-enable state, window/source geometry, update lock/pending state, CRC controls and values, output format range controls, MMHUBBUB backpressure counters, host-read throttling, overflow status/counters, soft reset, debug select, HDR multiplier, gamut-remap mode, coefficient format, and the first two gamut-remap matrix coefficients.

## Control Flow

This header has no runtime control flow. Runtime sequencing lives in the display driver:

1. DCN 3.0.1 resource and DMUB code include `dcn_3_0_1_offset.h` with this matching `dcn_3_0_1_sh_mask.h`.
2. Resource code builds register and field tables by token-pasting instance IDs into names such as `DSCC2_DSCC_PPS_CONFIG22__RANGE_MAX_QP14_MASK` or `DWB_ENABLE_CLK_CTRL__DWB_ENABLE__SHIFT`.
3. Block code uses those tables through register helpers to program DSC, DWB, GPIO/AUX/DDC, perfmon, and related display hardware.
4. Hardware then observes the programmed fields during modeset, link bring-up, DSC enablement, writeback capture, interrupt handling, debug capture, and suspend/resume restoration.

The macros do not encode ordering. Consumers must still enable clocks before touching gated blocks, program DSC PPS fields before enabling compressed streams, honor double-buffer/update-pending behavior, clear or acknowledge sticky interrupt/status fields correctly, and avoid writes to reserved or read-only hardware fields.

## State And Persistence Behavior

The chunk stores no software state. It describes MMIO-backed GPU state:

- GPIO/AUX/DDC pad state controls receiver enablement, pull-ups, AUX termination and polarity, pad drive/hysteresis, DDC I2C modes, voltage-domain enables, and power-good reporting.
- UNIPHY reserved macro-control fields represent opaque hardware state. The generated masks allow symbolic full-register access but do not document safe values.
- DSC state includes clock/debug gates, input format and dimensions, slice count and dimensions, DSC PPS parameters, rate-control thresholds, QP ranges, memory-power state, underflow/overflow interrupt state, fullness counters, and visual-error counters.
- Perfmon state includes selected events, per-counter states, run/start/stop gates, interrupt status/ack bits, and 48-bit-style high/low counter value exposure.
- DWB state includes capture enable/rate/window/source geometry, CRC mask/value state, output-format limits, overflow state and interrupt policy, soft reset, debug muxing, HDR coefficient, and color-remap matrix state.

Persistence is hardware-defined. Configuration fields generally last until modeset reprogramming, block reset, power gating, suspend/resume, or ASIC reset. Status, counter, interrupt, ack, and update-pending fields may be read-only, sticky, write-one-to-clear, self-clearing, or timing-sensitive. This generated header only provides bit encodings; semantic access rules come from the hardware spec and the consuming AMD display code.

## Dependencies And Integration Points

This chunk depends on AMD's generated DCN 3.0.1 register database and must stay synchronized with:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_1_offset.h`, which provides the corresponding register offsets.
- Shared AMD display register helper infrastructure that expands `REG_*`, `SR`, `SRI`, `DSC_SF`, `SF_DWB2`, and related macros into offset plus field-mask operations.
- Adjacent chunks of the same header, because this range starts in the middle of `DC_GPIO_RXEN` and ends inside the DWB color-processing block.

Direct include sites in this tree are:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn301/dcn301_resource.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn301.c`

Important shared consumers include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dsc/dcn20/dcn20_dsc.h` and `.c`, which use `DSC_SF`, `REG_SET`, `REG_UPDATE`, and `REG_GET` field tables for DSC clocking, PPS programming, DSCCIF input configuration, and status.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dwb/dcn30/dcn30_dwb.h`, `.c`, and `dcn30_dwb_cm.c`, which use DWB field definitions for capture control, CRC, output formatting, gamut remap, and color matrix programming.
- GPIO/DCIO/AUX/DDC handling code in the DCN family, which relies on matching GPIO and pad-control field names when mapping logical pins and AUX/DDC channels to hardware.

## Risks And Edge Cases

- Shift/mask drift is the central risk. These are untyped integer macros, so incorrect masks or positions can compile cleanly while updating the wrong bits in live display hardware.
- The repeated DSC instance families are copy-sensitive. `DSCC0`, `DSCC1`, and `DSCC2` are structurally similar, but an instance-specific typo can break only one pipe or only high-bandwidth modes requiring DSC on that instance.
- `DCIO_UNIPHY*_RESERVED*` full-register masks are risky by nature. The header exposes them as 32-bit fields, but the safe write semantics of reserved registers are not documented here.
- Interrupt/status fields in `DSCC*_DSCC_INTERRUPT_CONTROL_STATUS`, perfmon status/ack registers, and `DWB_OVERFLOW_STATUS` may be sticky or write-one-to-clear. Generic read-modify-write code can accidentally clear or preserve stale status if it does not follow hardware semantics.
- DSC PPS fields are dense and format-sensitive. Bad values or masks for bits-per-pixel, slice geometry, rate-control thresholds, QP ranges, offsets, and native 4:2:0/4:2:2 flags can cause visual corruption, link failures, or modeset-only regressions.
- DWB frame-capture and color-processing fields interact with source timing and buffer readback. Incorrect capture-rate/window/source/gamut-remap masks can produce cropped output, stale frames, wrong color, CRC mismatch, or overflow.
- Power and clock fields for DSC, DWB, and memory blocks are sequencing-sensitive. Writes may be ignored, harmful, or lost if the block is gated, reset, or transitioning power state.
- Chunk boundaries are artificial. The beginning lacks the earlier `DC_GPIO_RXEN` field definitions, and the end stops before the rest of the DWB color-processing matrix fields.

## Test Signals

Useful validation is mostly generated-header consistency plus display hardware behavior:

- Build AMDGPU/DC with DCN 3.0.1 support enabled; missing or renamed macros should fail in `dcn301_resource.c`, `dmub_dcn301.c`, DSC register-table construction, DWB register-table construction, and GPIO/DCIO code paths.
- Mechanically verify every `__SHIFT` field in lines 36969-39480 has a compatible `_MASK` in the same register family, accounting for the intentionally partial `DC_GPIO_RXEN` and final `DWB_GAMUT_REMAPA_C11_C12` boundaries.
- Diff this slice against AMD's authoritative generated DCN 3.0.1 register database and nearby generation targets such as DCN 3.0.0, DCN 3.2.0, and DPCS headers where fields are expected to match.
- Exercise AUX/DDC and GPIO paths: hotplug, EDID reads, DisplayPort AUX DPCD transactions, I2C-over-AUX, pull-up behavior, pad power-good reporting, and suspend/resume.
- Exercise DSC on capable displays across all available DSC instances: high-bandwidth modes, different bits-per-component/pixel formats, native 4:2:0/4:2:2 paths, DSC enable/disable during modeset, and visual integrity under rate-buffer stress.
- Watch DSC interrupt/status and error counters for underflow, overflow, rate-buffer fullness, squared-error, and max-absolute-error anomalies.
- Use perfmon debug workflows to verify selected DC perfmon events count, report, interrupt, acknowledge, and read high/low values correctly.
- Exercise DWB capture paths: enable/disable capture, crop/window/source-size programming, stereo eye selection, CRC generation, output format limits, overflow interrupt handling, color remap, HDR multiplier, and host-read throttling.
- Monitor kernel logs and display diagnostics for AUX timeouts, hotplug storms, link-training failures, DSC corruption, stuck interrupts, DWB overflow, CRC mismatches, blanking, and resume failures.

## Cross-Chunk Notes

Previous chunks own the beginning of the DC GPIO and RX-enable definitions. Later chunks continue the DWB color-processing block after `DWB_GAMUT_REMAPA_C11_C12` and cover the rest of the DCN 3.0.1 field-mask namespace. The final per-file research document should merge adjacent chunks before making complete claims about all DCN 3.0.1 GPIO, DSC, perfmon, or DWB fields.

### subset-b-001738: lines 39481-42015

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_1_sh_mask.h lines 39481-42015

## Scope

This chunk covers a generated DCN 3.0.1 register shift/mask header slice. It contains only preprocessor constants and register grouping comments; there are no C functions, structs, enums, or executable statements in this range.

The slice begins inside the `dce_dc_wb0_dispdec_dwbcp_dispdec` writeback color block, continues through `dce_dc_dchvm_hvm_dispdec`, covers the main MPC/MPCC0-3 compositor register fields, then defines most of the MPCC OGAM0, OGAM1, and OGAM2 color pipeline register fields. It ends at the start of the MPCC OGAM3 LUT-control block, so the final MPCC OGAM3 transfer-function and gamut-remap coverage is intentionally left to the next chunk.

## Purpose

The purpose of this header region is to publish the bit layouts for DCN 3.0.1 display writeback, hardware virtualization/memory-control, MPC composition, and per-MPCC output-gamma programming registers. Driver code combines these `__SHIFT` and `_MASK` constants with register offsets from `dcn_3_0_1_offset.h` and AMD display register helpers to program MMIO fields symbolically instead of hard-coding bit positions.

At a subsystem level, this chunk supports:

- DWB color output programming, including gamut remap matrices, output gamma mode selection, OGAM LUT host access, and dual RAM A/B piecewise-linear region tables for red, green, and blue.
- DCHVM control and status fields for host virtual memory style display access, clock gating, memory-selection, RIOMMU control/status, and debug/test windows.
- MPCC0 through MPCC3 composition setup: source selection, OPP routing, blend/alpha/background controls, update-lock selection, memory power control, and status reporting.
- MPCC OGAM0 through OGAM2 full transfer-function programming and double-buffered gamut-remap matrix selection.
- The beginning of MPCC OGAM3 control and LUT host access fields.

This file is a generated hardware contract. Its macro names and numeric masks are consumed through macro concatenation in register tables, so both spelling and bit values are part of the build-time and runtime ABI between generated ASIC headers and display code.

## Important APIs, Types, And Constants

There are no callable APIs or local C types in this chunk. The exported interface is the macro namespace:

- `<REGISTER>__<FIELD>__SHIFT`: bit offset for a field in a register.
- `<REGISTER>__<FIELD>_MASK`: bit mask for that field.
- Comments such as `//DWB_OGAM_CONTROL` and `//MPCC2_MPCC_CONTROL` group fields by hardware register.
- Address-block comments identify generated hardware blocks, including `dce_dc_wb0_dispdec_dwbcp_dispdec`, `dce_dc_dchvm_hvm_dispdec`, `dce_dc_mpc_mpcc<n>_dispdec`, and `dce_dc_mpc_mpcc_ogam<n>_dispdec`.

The main register families in this chunk are:

- `DWB_GAMUT_REMAPA_*` and `DWB_GAMUT_REMAPB_*`: two banks of 3x4-ish color remap coefficients, two signed/fixed-point coefficients per 32-bit register with low/high 16-bit fields.
- `DWB_OGAM_CONTROL`, `DWB_OGAM_LUT_INDEX`, `DWB_OGAM_LUT_DATA`, and `DWB_OGAM_LUT_CONTROL`: mode/current-mode, RAM select/current-select, PWL disable, LUT index/data, per-color write mask, read color select, debug read, host RAM select, and config-mode fields for the DWB output-gamma LUT.
- `DWB_OGAM_RAMA_*` and `DWB_OGAM_RAMB_*`: dual RAM A/B transfer-function programming fields. Each RAM has per-channel start, start-base, start-slope, end-base, end/slope, offset, and region descriptors for regions 0-33. Region-pair registers pack LUT offset and segment-count fields for two adjacent regions.
- `DCHVM_CTRL0`, `DCHVM_CTRL1`, `DCHVM_CLK_CTRL`, `DCHVM_MEM_CTRL`, `DCHVM_RIOMMU_CTRL0`, `DCHVM_RIOMMU_STAT0`, `DCHVM_DEBUG_CTRL0`, `DCHVM_TEST_DEBUG_INDEX`, and `DCHVM_TEST_DEBUG_DATA`: control, clock-gating, memory, RIOMMU, status, and debug/test access fields for the display HVM block.
- `MPCC<n>_MPCC_TOP_SEL`, `BOT_SEL`, `OPP_ID`, `CONTROL`, `SM_CONTROL`, `UPDATE_LOCK_SEL`, gain/background registers, `MEM_PWR_CTRL`, and `STATUS`: repeated MPCC compositor field sets for instances 0-3.
- `MPCC_OGAM<n>_MPCC_OGAM_CONTROL`, `LUT_INDEX`, `LUT_DATA`, and `LUT_CONTROL`: per-MPCC OGAM mode/current-mode, RAM select/current-select, PWL disable, host LUT selection, color write mask, read color select, and config mode.
- `MPCC_OGAM<n>_MPCC_OGAM_RAMA_*` and `RAMB_*`: per-MPCC dual transfer-function RAM descriptors matching the DWB OGAM shape.
- `MPCC_OGAM<n>_MPCC_GAMUT_REMAP_COEF_FORMAT`, `MPCC_GAMUT_REMAP_MODE`, and `MPC_GAMUT_REMAP_*_{A,B}`: per-MPCC gamut-remap coefficient format, active/current mode, and two banks of remap coefficients.

The repeated blocks are mechanically consistent but not identical at the chunk boundaries: DWB starts mid-gamut-remap block, MPCC OGAM0-2 are complete in this range, and MPCC OGAM3 is partial.

## Control Flow

This chunk has no runtime control flow. Its effective flow is compile-time expansion into display register access code:

1. DCN 3.0.1 resource and DMUB code include `dcn/dcn_3_0_1_offset.h` and `dcn/dcn_3_0_1_sh_mask.h`.
2. Register-list macros such as `SRII(...)` bind offsets for indexed register instances, while field macros such as `SF(register, field, mask_sh)` bind shift and mask values.
3. Runtime helpers such as `REG_GET`, `REG_SET`, `REG_UPDATE`, and `REG_WAIT` use the precomputed register offsets plus these shift/mask values to access MMIO fields.
4. Higher-level color and composition code, especially DCN3 MPC code, programs OGAM RAMs, selects active LUT RAM A/B, writes LUT data, updates MPCC blend state, and reads status/current-state fields.

The ordering within the header is still semantically useful. Each register section lists shifts first and masks second. Indexed blocks are ordered by hardware instance, and dual RAM A/B programming registers use the same field layout so shared color helper code can reuse one field table.

## State And Persistence Behavior

The header itself stores no software state and persists no data. It describes hardware state in the GPU display engine:

- DWB OGAM and gamut-remap state controls writeback color conversion. Programmed LUT RAMs, remap matrices, and current-select fields persist in hardware until overwritten or reset.
- MPCC composition state controls which top/bottom surfaces feed each compositor, how alpha and blending behave, which OPP receives the output, gain/background values, and update-lock behavior.
- MPCC memory power fields determine whether MPCC and OGAM memories are forced on, disabled, in low-power mode, or reporting a powered state. These fields directly affect whether later LUT writes can succeed.
- MPCC OGAM state includes the active mode, currently selected RAM, host-write target RAM, LUT index/data, per-color write mask, PWL region tables, and two banks of gamut-remap matrices.
- DCHVM state covers enable/control bits, clock-gating policy, memory selection, RIOMMU control/status, and debug-indexed data access.

The persistence boundary is hardware-defined. Values can survive normal software object lifetimes but are generally reset by display engine reset, ASIC reset, power transitions, or explicit reprogramming during modeset, color-management, writeback, or resume paths. Some fields are status/current mirrors rather than direct controls; the generated shift/mask names do not encode read-only versus writable access.

## Dependencies And Integration Points

This chunk depends on the generated DCN 3.0.1 register model remaining synchronized across files:

- `dcn_3_0_1_offset.h` supplies the register addresses paired with these fields.
- `dcn_3_0_1_sh_mask.h` supplies field placement for AMD display register helpers.
- `dcn301_resource.c` and `dmub_dcn301.c` include this header and the offset header for DCN 3.0.1 hardware setup.
- DCN3 MPC code consumes the MPCC and MPCC OGAM fields through `dcn30_mpc.h` register lists and `dcn30_mpc.c` helpers. For example, it reads `MPCC_OGAM_MODE_CURRENT`/`MPCC_OGAM_SELECT_CURRENT`, powers OGAM memory through `MPCC_MEM_PWR_CTRL`, configures `MPCC_OGAM_LUT_CONTROL`, writes `MPCC_OGAM_LUT_INDEX`/`DATA`, and fills RAM A/B transfer-function register descriptors.
- Display color management integrates conceptually through transfer-function programming, gamut remap, LUT RAM selection, and PWL region setup.
- Display writeback integrates through DWB OGAM and DWB gamut-remap fields, while MPC composition integrates through MPCC mux/blend/gain/background/status fields.

The primary integration contract is preprocessor naming. A missing or renamed macro usually fails at compile time when an `SF`/`REG_*` macro expands. A wrong numeric shift or mask can compile cleanly and only surface as incorrect MMIO programming on DCN 3.0.1 hardware.

## Risks And Edge Cases

- The chunk starts and ends mid-generated structure. Whole-file reconciliation must merge adjacent chunks before judging DWB or MPCC OGAM3 completeness.
- The DWB and MPCC OGAM RAM A/B fields are highly repetitive. A generator drift in one channel, RAM bank, or region-pair mask can silently corrupt only a narrow part of the transfer function.
- Several fields pack two 16-bit coefficient or region values into one register. Incorrect masks or shifts can cross-write adjacent coefficients, especially gamut-remap Cxx pairs and region-pair `LUT_OFFSET`/`NUM_SEGMENTS` fields.
- Mode/current-mode and select/current-select fields are separate. Confusing control fields with current-status fields can make color-management code believe a RAM switch happened before hardware reports it.
- Memory power fields in `MPCC<n>_MPCC_MEM_PWR_CTRL` affect LUT accessibility. Wrong `MPCC_OGAM_MEM_PWR_DIS`, `FORCE`, `LOW_PWR_MODE`, or `STATE` masks can cause LUT writes to be dropped, hang waiting for power state, or keep memory unnecessarily powered.
- `DCHVM_*` and `RIOMMU_*` fields are low-level display memory-path controls/status. Misprogramming them can affect address translation, debug visibility, or clock gating rather than producing a local color-only failure.
- The MPCC compositor fields are repeated per instance 0-3. A single instance-specific macro typo can produce failures only for a particular pipe/plane topology.
- Full-width and high-bit masks require unsigned handling. Status fields, coefficient fields, and packed fixed-point values should not be treated as signed integers merely because the macros use `L` suffixes.
- Cross-generation reuse is risky. Nearby DCN 3.x headers have similar names but not guaranteed identical bit positions, field coverage, or instance counts.

## Test Signals

Useful validation signals for this header are build-time, generator-comparison, and hardware-integration oriented:

- Compile DCN 3.0.1 display and DMUB code with the normal AMDGPU build to catch missing field names in `SF`, `REG_GET`, `REG_SET`, `REG_UPDATE`, and `REG_WAIT` expansions.
- Compare this slice against the matching `dcn_3_0_1_offset.h` and generator source to confirm every register with fields has a matching offset and every indexed MPCC/OGAM instance is consistently generated.
- Exercise modesets with multiple planes to validate MPCC0-3 source selection, OPP routing, alpha/blend modes, update locking, gains, backgrounds, and status reads.
- Run color-management tests that program MPCC OGAM RAM A and RAM B, switch between RAMs, verify `MPCC_OGAM_MODE_CURRENT`/`SELECT_CURRENT`, and compare output against expected transfer functions.
- Test gamut remap matrix programming for both A and B banks, including coefficient-format changes and mode/current-mode transitions.
- Exercise DWB/writeback paths with color transforms enabled to verify DWB OGAM LUT, gamut remap, and HDR multiplier behavior.
- Run suspend/resume, display reset, and power-management tests to catch stale MPCC memory-power or OGAM RAM state and to verify LUT writes still work after reinitialization.
- Include hardware debug or register-dump checks for DCHVM clock/memory/RIOMMU status fields when enabling display memory virtualization paths.

## Open Cross-Chunk Questions

- The final per-file report should merge this with the previous DWB chunk and the following MPCC OGAM3 chunk before summarizing completeness.
- Reconciliation should verify that DCN 3.0.1 actually exposes four MPCC instances and at least four MPCC OGAM blocks in the generated offset header, not just in this shift/mask range.
- If generator provenance is tracked elsewhere in the repository, the final report should identify it, because manual edits to these repetitive field constants would be unusually high risk.

### subset-b-001739: lines 42016-44533

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_1_sh_mask.h lines 42016-44533

## Scope

This chunk covers a generated DCN 3.0.1 shift/mask header slice for AMD display hardware registers. It contains only preprocessor constants and generated grouping comments; there are no C functions, structs, enums, or executable statements in this range.

The slice begins inside the `MPCC_OGAM3` output-gamma register family and then covers these address blocks:

- `dce_dc_mpc_mpc_cfg_dispdec`
- `dce_dc_mpc_mpc_ocsc_dispdec`
- `dce_dc_mpc_mpc_rmu_dispdec`
- `dce_dc_mpc_mpc_dcperfmon_dc_perfmon_dispdec`
- `dce_dc_opp_abm0_dispdec`
- `dce_dc_opp_abm1_dispdec`

The chunk ends partway through the `ABM1_DC_ABM1_HG_MISC_CTRL` register, so final per-file reconciliation should merge it with the next chunk for the complete ABM1 block.

## Purpose

This region is part of the generated hardware ABI used by AMDGPU Display Core to program DCN 3.0.1 display-pipeline blocks. Each exported macro gives either the bit shift or bit mask for a named hardware register field. Runtime display code does not call into this file directly; instead, register helper macros such as `SF`, `ABM_SF`, `REG_SET`, `REG_UPDATE`, `REG_GET`, and related DC register-table builders concatenate register and field names to resolve these constants at compile time.

At a hardware level, this chunk describes:

- MPCC output-gamma RAM A/B region layout and gamut remap fields for MPCC/OGAM instance 3.
- MPC global configuration fields for clocks, soft reset, CRC capture, pending-update status, vupdate locks, and DWB muxing.
- MPC output path muxing, flow control, denormalization clamps, output color-space-conversion coefficient format, and per-output CSC matrices for outputs 0-3.
- MPC RMU routing, memory power controls, shaper LUT programming, shaper RAM A/B region descriptors, and 3D LUT programming for RMU instances 0 and 1.
- DC perfmon instance 21 counter control, state, interrupt, and readback fields.
- ABM0 and the beginning of ABM1 backlight/PWM, adaptive backlight, histogram, luma-statistics, sample-rate, and register-lock fields.

The main value of this file is keeping implementation code symbolic. Driver code can request fields like `MPC_OUT0_MUX__MPC_OUT_FLOW_CONTROL_COUNT_MASK` or `ABM0_DC_ABM1_HGLS_REG_READ_PROGRESS__ABM1_HG_REG_READ_MISSED_FRAME_CLEAR_MASK` without duplicating fragile numeric bit layouts.

## Important APIs, Types, And Constants

There are no callable APIs or local types. The exported interface is the macro namespace:

- `<REGISTER>__<FIELD>__SHIFT`: numeric bit offset for a field.
- `<REGISTER>__<FIELD>_MASK`: bit mask for the same field.
- Register comments such as `//MPC_CRC_CTRL` and address-block comments such as `// addressBlock: dce_dc_mpc_mpc_rmu_dispdec` preserve the generated register grouping.

Important macro families in this chunk are:

- `MPCC_OGAM3_MPCC_OGAM_RAMA_*` and `MPCC_OGAM3_MPCC_OGAM_RAMB_*`: output-gamma RAM A/B start, start slope, start base, end, offset, and region descriptor fields. Region registers pair two regions per register, with LUT offset fields and segment-count fields for regions 0-33.
- `MPCC_OGAM3_MPCC_GAMUT_REMAP_*` and `MPCC_OGAM3_MPC_GAMUT_REMAP_C*`: gamut-remap coefficient format, mode/current mode, and double-buffered A/B coefficient fields for a 3x4 style matrix.
- `MPC_CLOCK_CONTROL`, `MPC_SOFT_RESET`, `MPC_CRC_CTRL`, `MPC_CRC_SEL_CONTROL`, and `MPC_CRC_RESULT_*`: MPC clock/test-clock controls, resets for MPCC/SFR/SFT/global MPC blocks, CRC enable/update/source selection, CRC input selection, and CRC readback result fields.
- `MPC_DPP_PENDING_STATUS` and `MPC_PENDING_STATUS_MISC`: pending update status bits for DPP surface/config/cursor updates, OPP config updates, MPCC config updates, and DWB config updates.
- `ADR_CFG_CUR_VUPDATE_LOCK_SET<n>`, `ADR_CFG_VUPDATE_LOCK_SET<n>`, `ADR_VUPDATE_LOCK_SET<n>`, `CFG_VUPDATE_LOCK_SET<n>`, and `CUR_VUPDATE_LOCK_SET<n>`: per-pipe vupdate lock request bits for coordinated address, config, and cursor updates.
- `MPC_DWB0_MUX`: DWB mux selection and readback/status fields.
- `MPC_OUT<n>_MUX`, `MPC_OUT<n>_DENORM_*`, and `MPC_OUT<n>_CSC_*`: output mux selection, rate/flow-control error and control bits, denormalization min/max clamp fields, CSC mode/current mode, coefficient format, and A/B double-buffered CSC matrix coefficients for outputs 0-3.
- `MPC_RMU_CONTROL` and `MPC_RMU_MEM_PWR_CTRL`: RMU mux selections/status and force/disable/state fields for RMU0/RMU1 shaper and 3D LUT memories.
- `MPC_RMU<n>_SHAPER_*`: shaper LUT mode/current mode, per-channel offsets/scales, LUT index/data/write controls, RAM A/B start/end descriptors, and RAM A/B region descriptors for RMU instances 0 and 1.
- `MPC_RMU<n>_3DLUT_*`: 3D LUT mode, size, current mode, index, 16-bit paired data, 30-bit data, read/write controls, output normalization factor, and per-channel output offset/scale fields.
- `DC_PERFMON21_*`: counter event selection, counted-value type, hardware start/stop selection, per-counter state, perfmon state/report count, counter-off interrupt controls, interrupt status/ack fields, high/low counter value readback, and read selector fields.
- `ABM0_BL1_PWM_*` and `ABM1_BL1_PWM_*`: ambient/user/target/current ABM levels, final/minimum PWM duty cycle, ABM enable policy, backlight update sample rate, and grouped register lock/update bits.
- `ABM0_DC_ABM1_*` and early `ABM1_DC_ABM1_*`: adaptive backlight controls, input CSC coefficient selection, HGLS register-read progress/missed-frame clear fields, histogram controls, luma-statistics readbacks, sample-rate controls, histogram bin shift/index masks, histogram results, and backlight master lock.

## Control Flow

This chunk has no runtime control flow. Its effective flow is compile-time macro expansion:

1. ASIC-specific DCN 3.0.1 resource or block code includes the generated offset and shift/mask headers.
2. Register-list macros such as `SF(...)` and `ABM_SF(...)` expand a symbolic register and field pair into `.mask` and `.shift` table entries.
3. Runtime helpers use those generated tables to compose MMIO values, perform read/modify/write operations, poll status bits, or decode readback fields.
4. Hardware sequencing is implemented elsewhere, but it relies on these masks being correct for fields that must be programmed in a specific order, such as LUT index/data/write-enable sequences, double-buffered mode updates, register locks, and status/ack bits.

The ordering inside the chunk is generated and hardware-oriented. Most register comments are followed by all field `__SHIFT` defines and then all corresponding `_MASK` defines. Repeated instances are ordered numerically, such as MPC outputs 0-3 and RMU instances 0-1.

## State And Persistence Behavior

The header itself stores no software state and persists no data. It describes hardware state that lives in DCN display registers:

- MPCC OGAM state includes output-gamma LUT selection/configuration, RAM A/B region layout, offsets, slopes, bases, and gamut-remap coefficient banks.
- MPC configuration state includes clock-gating/test-clock controls, soft reset bits, CRC capture state, CRC source selection, pending-update status, vupdate locks, and DWB mux routing.
- MPC output state includes OPP/MPCC muxing, flow-control and overflow/error acknowledgement bits, denormalization clamps, output CSC modes, active/current CSC bank selection, and matrix coefficients.
- RMU state includes mux routing, memory power-force/disable bits, memory power-state readbacks, shaper LUT contents, shaper region descriptors, 3D LUT mode/size/current mode, LUT memory contents, and output normalization/offset/scale fields.
- DC perfmon21 state includes event/counter configuration, counter active/state bits, interrupt enables/status/ack bits, and readback latch/select values.
- ABM state includes backlight target/current/final PWM levels, ABM enable policy, update sample rates, grouped update locks, histogram/luma-statistics controls and results, missed-frame indicators, and master locks.

Persistence is hardware-defined. Most programmed fields remain active until another MMIO write, a block reset, display reset, or ASIC reset. Status and readback fields can change asynchronously with frame timing, histogram collection, CRC capture, perfmon counting, or backlight processing. This header does not encode access permissions, volatility, locking requirements, or write-one-to-clear semantics; consumers must follow the relevant DC block programming model.

## Dependencies And Integration Points

This chunk depends on the generated DCN register model staying synchronized across companion headers and block code:

- The matching `dcn_3_0_1_offset.h` provides register offsets that pair with these field definitions.
- AMD Display Core register helpers consume these macros through generated tables in block headers, especially MPC code such as `drivers/gpu/drm/amd/display/dc/mpc/dcn30/dcn30_mpc.h`.
- ABM tables in `drivers/gpu/drm/amd/display/dc/dce/dce_abm.h` consume the `ABM0_DC_ABM1_*` and `ABM0_BL1_PWM_*` field names through `ABM_SF(...)` lists.
- Resource files for DCN generations list shared MPC registers such as `MPC_CRC_CTRL`; this header supplies field placement for DCN 3.0.1-specific builds.
- Color management paths depend on the MPCC OGAM, gamut-remap, output CSC, shaper, and 3D LUT fields to upload curves and matrices.
- Diagnostics and validation paths depend on MPC CRC and DC perfmon masks to select sources, enable counters, acknowledge interrupts, and read results.
- Backlight and panel power/brightness paths depend on the ABM/PWM fields for target levels, update cadence, luma statistics, histogram readback, and lock sequencing.

The direct interface is the preprocessor name contract. If a macro is missing or renamed, users generally fail at compile time. If a numeric mask or shift is wrong, code can still compile and perform incorrect MMIO writes, which is a higher-risk failure mode.

## Risks And Edge Cases

- The chunk starts inside `MPCC_OGAM3_MPCC_OGAM_LUT_CONTROL` and ends inside `ABM1_DC_ABM1_HG_MISC_CTRL`. Per-file reconciliation must merge neighboring chunks before making completeness claims about either register family.
- The register families are highly repetitive. Generator drift in one MPCC/RMU RAM region, one MPC output, or one ABM instance can be hard to notice in review while affecting only a specific pipeline or output.
- Many color fields are double-buffered or banked (`A`/`B`, current-mode fields, LUT RAM selectors). A mask drift can cause updates to land in the wrong bank or report the wrong active bank, producing color-management failures that are hard to attribute to the generated header.
- Full-register and high-bit masks, such as histogram results, perfmon values, 30-bit LUT data, lock bits, interrupt acks, and master locks, require unsigned-width-safe handling by callers.
- Some fields are read-only status, some are control bits, and some are write-one-to-clear acknowledgements. The shift/mask header does not distinguish them, so caller misuse is possible even when the macro values are numerically correct.
- Reset and memory-power fields are sensitive. Incorrect `MPC_SOFT_RESET` or `MPC_RMU_MEM_PWR_CTRL` masks could leave MPC, RMU shaper, or 3D LUT memories disabled, reset, or powered unexpectedly.
- Pending-update and vupdate-lock masks participate in frame-synchronized programming. Wrong masks can create update races, stuck pending states, or missed cursor/address/config commits.
- Flow-control error acknowledgement bits in `MPC_OUT<n>_MUX` are adjacent to selection and rate-control fields. Incorrect read/modify/write composition could accidentally clear errors or alter output routing.
- DC perfmon interrupt status and ack fields share one register family. Bad masks can lose performance-counter interrupts or acknowledge the wrong counter.
- ABM HGLS missed-frame clear bits are high-bit fields in a register that also reports in-progress and missed-frame status. Wrong masks can leave stale missed-frame state or clear the wrong channel's state.
- Cross-ASIC reuse is risky. Similar field names exist in neighboring DCN headers, but this file is specifically for DCN 3.0.1 and should not be assumed identical to DCN 3.0.0, DCN 3.1, or later ASICs.

## Test Signals

Useful validation is mostly build-time, register-table, and hardware-integration oriented:

- Compile AMDGPU Display Core for DCN 3.0.1 with warning coverage enabled to catch missing field names in `SF`, `ABM_SF`, `REG_*`, and resource-table expansions.
- Preprocess or build MPC and ABM users that reference `MPC_OUT0_MUX`, `MPC_RMU0_3DLUT_*`, `MPCC_OGAM0/3_*`, `ABM0_DC_ABM1_*`, and related field names.
- Compare this header against the matching offset header and the upstream register-generation source to ensure every register field has a matching offset and that the generated masks are in the expected bit positions.
- Exercise color-management paths on DCN 3.0.1 hardware: output gamma LUT upload/readback, gamut remap, output CSC programming, shaper LUT upload, and 3D LUT upload, including bank-switch/current-mode validation.
- Run display CRC tests through the DRM debug/CRC paths to validate `MPC_CRC_CTRL`, source selection, update locking, one-shot/continuous capture, and result registers.
- Exercise multi-pipe updates with surface, cursor, and config commits, checking pending-status and vupdate-lock behavior across pipes 0-3.
- Validate DWB routing if supported by the platform, including mux status readback.
- Run perfmon smoke tests for DC perfmon21: event selection, counter enable, state reporting, interrupt status/ack, and high/low value readback.
- Exercise ABM/backlight behavior on panels that support it: user level, target/current ABM level, final duty cycle, sample-rate programming, register-lock updates, luma statistics, histogram result reads, missed-frame clear paths, suspend/resume, and display reset.

## Open Cross-Chunk Questions

- The final per-file report should merge adjacent chunks to represent the full `MPCC_OGAM3` and `ABM1` register families.
- Whole-file reconciliation should verify whether DCN 3.0.1 intentionally exposes only the RMU fields shown here for both instances or whether additional RMU controls live in adjacent chunks.
- If generation provenance is available, the final report should identify the source register database or import path because hand-editing these numeric masks would be unusually high risk.

### subset-b-001740: lines 44534-47180

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_1_sh_mask.h lines 44534-47180

## Purpose

This chunk is generated AMD DCN 3.0.1 register field metadata. It contains no executable C logic; it publishes preprocessor constants for field shifts and bit masks used when AMDGPU display code reads, writes, or updates individual fields inside DCN 3.0.1 MMIO and indexed registers.

The requested range starts in the middle of the `ABM1_DC_ABM1_HG_MISC_CTRL` field list, then covers the tail of ABM1 luma/histogram/backlight masks, complete ABM2 and ABM3 ambient-backlight-management field masks, legacy VGA sequencer/CRTC/graphics/attribute indexed register masks, and a large Azalia/HD-audio register-mask area for output codecs, descriptors, sink info, CRC counters, input codecs, root-function registers, stream latency counters, and the beginning of `AZF0ENDPOINT0` endpoint-0 fields.

Although this path is under a local `ceph-client` source mirror, the file is AMDGPU display-driver hardware metadata. It does not implement Ceph or distributed filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, includes, allocation paths, or locks in this range. The API is the generated macro namespace:

- `<REGISTER>__<FIELD>__SHIFT`: bit position for a field.
- `<REGISTER>__<FIELD>_MASK`: mask for the same field.

The chunk contains 2,065 `#define` lines: 1,033 shift macros and 1,032 mask macros. The off-by-one is expected from the artificial chunk boundary: line 44534 begins after the first `ABM1_DC_ABM1_HG_MISC_CTRL` shift in the prior chunk, while this range still includes all visible masks for that register.

Major macro families in this slice:

- `ABM1`, `ABM2`, `ABM3`: adaptive backlight management, PWM/ambient/user/target/current/final/minimum duty-cycle levels, ABM enable/bypass, IPS color-space coefficient selection, histogram/luma-statistics read-progress and missed-frame bits, histogram bin controls, luma min/max/pixel-count thresholds, sample-rate controls, 24 histogram result registers, and master/double-buffer lock fields.
- `SEQxx`, `CRTxx`, `GRAxx`, `ATTRxx`: legacy VGA sequencer, CRTC, graphics-controller, and attribute-controller indexed fields for reset, plane maps, font selection, timing totals, blank/sync positions, cursor, pitch, address mode, graphics write/read modes, palettes, overscan, panning, and color-select controls.
- `AZALIA_F2_CODEC_CONVERTER_*`: HD-audio output-converter format, channel/stream IDs, IEC 60958 digital-converter status/control bits, stripe control, keepalive, ramp rate, GTC presentation-time embedding, audio widget capabilities, supported sizes/rates, and stream formats.
- `AZALIA_F2_CODEC_PIN_*`: output pin widget control, unsolicited responses, pin sense and presence detect, default configuration words, speaker/channel allocation, downmix data, audio descriptors, multichannel enables, lipsync, HBR, sink-info index/data, LPIB snapshot/status, coding type, format-changed notification, wireless-display identification, remote keepalive, association/status fields, and IEC 60958 channel-status overrides.
- `AUDIO_DESCRIPTOR0` through `AUDIO_DESCRIPTOR13` and `SINK_DESCRIPTION0` through `SINK_DESCRIPTION17`: ELD/EDID-like audio descriptor and sink-description payload fields.
- `AZALIA_INPUT_CRC*` and `AZALIA_CRC*`: per-channel CRC result fields for input and controller CRC paths.
- `AZALIA_F2_CODEC_INPUT_*`: input converter and input pin equivalents for format, stream/channel ID, digital-converter bits, widget capabilities, pin sense/default config, channel allocation, multichannel enable/mute, HBR, LPIB, input status, infoframe, and channel-status words.
- `AZALIA_F2_CODEC_ROOT_*` and `AZALIA_F2_CODEC_FUNCTION_*`: root/function vendor, revision, subordinate-node count, power state, subsystem ID, converter synchronization, reset, group type, supported formats, and power-state capability fields.
- `AZF0STREAM0` through `AZF0STREAM15`: repeated stream FIFO-size, latency counter control, worst-case latency, cumulative latency, and cumulative request-count fields.
- `AZF0ENDPOINT0_*`: endpoint-0 output converter and pin fields, including widget capabilities, converter format, stream/channel ID, digital converter flags, stream-format/rate capabilities, stripe and ramp controls, GTC counters, pin capabilities, unsolicited response, pin sense, widget output enable, channel/speaker/downmix allocation, and audio descriptor fields 0 through 7.

## Control Flow

This header has no runtime control flow. Runtime sequencing is supplied by AMDGPU display and DMUB code:

1. DCN 3.0.1 code includes `dcn_3_0_1_offset.h` and this `dcn_3_0_1_sh_mask.h` together.
2. Register-table macros build register offsets from the offset header and field metadata from this mask header.
3. Access helpers such as `REG_SET`, `REG_UPDATE`, `REG_GET`, `FD_MASK`, `FD_SHIFT`, and DMUB `REG_OFFSET`/field-table construction use the generated shift/mask values to isolate fields without hard-coding bit positions in handwritten driver code.
4. Higher-level display, audio, backlight, and firmware paths decide the actual order: modeset, backlight update, histogram sampling, audio stream setup, sink capability reporting, interrupt/unsolicited-response handling, CRC capture, suspend/resume, and reset.

The macros themselves do not express whether a field is read-only, sticky, self-clearing, write-one-to-clear, double-buffered, or safe to modify while a block is active. Those behaviors are hardware contract details that must be honored by the consuming driver code.

## State And Persistence Behavior

This chunk stores no software state and persists nothing to disk. It describes bit-level layout for hardware-backed state:

- ABM/PWM registers hold ambient light level, user level, computed ABM target/current/final duty cycle, minimum duty cycle, sample-rate counters, histogram configuration, luma statistics, histogram results, and double-buffer/master-lock state.
- Legacy VGA indexed registers describe emulation/compatibility state for sequencer, CRTC timing, graphics plane, palette, cursor, and attribute behavior.
- Azalia codec and endpoint registers hold audio format, sample rate, channel count, channel-status bits, stream/channel IDs, pin presence/configuration, speaker/channel allocation, ELD-style descriptors, sink strings, LPIB/timestamp snapshots, keepalive, HBR, infoframe, and unsolicited-response state.
- CRC and latency/counter registers expose hardware counters and diagnostic state for audio/input streams.

Persistence is hardware-defined. Configuration fields may survive until a modeset, audio reconfiguration, power gating, suspend/resume, function reset, or ASIC reset. Status/counter/clear/ack fields may be transient, sticky, or side-effect-sensitive. This generated header intentionally does not encode those policy differences.

## Dependencies And Integration Points

This chunk depends on AMD's generated DCN 3.0.1 register database and must match:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_1_offset.h` for the corresponding register offsets.
- AMD register-access helpers that derive `FD_MASK(reg, field)` and `FD_SHIFT(reg, field)` from names in this file.
- Related generated enum metadata such as `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/soc21_enum.h`, which names many Azalia field values for converter format, digital-converter flags, audio descriptors, channel allocation, multichannel mute/enable, and power states.

The directly observed include site in this tree is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn301.c`, which includes both `dcn_3_0_1_offset.h` and `dcn_3_0_1_sh_mask.h` and builds `dmub_srv_dcn301_regs` with `REG_OFFSET`, `FD_MASK`, and `FD_SHIFT`. Other DCN display code uses the same generated-header style for register programming, even when a particular macro in this chunk is only consumed through generated tables or firmware-facing register lists.

Integration points by hardware area:

- ABM/backlight programming paths use the ABM fields when enabling/disabling adaptive backlight processing, selecting histogram/luma sampling behavior, reading statistics/results, and committing PWM or ABM updates at frame boundaries.
- Display bring-up, VGA compatibility, or early/legacy paths can use the `SEQ`, `CRT`, `GRA`, and `ATTR` field masks to program indexed VGA state without open-coded bit shifts.
- Display audio paths use the Azalia converter/pin/root/stream fields for HDMI/DP audio format negotiation, stream ID routing, ELD/sink data exposure, HBR/multichannel enablement, channel-status overrides, pin presence/unsolicited response handling, and latency/CRC diagnostics.
- DMUB uses the generated field tables to let firmware-facing code manipulate DCN 3.0.1 registers with consistent offsets, masks, and shifts.

## Risks And Edge Cases

- Generated macro drift is the primary risk. A wrong shift or mask compiles cleanly but can write the wrong bits in hardware, producing silent backlight, display, or audio failures.
- The chunk starts and ends inside larger register families. The first visible ABM register is incomplete because its earlier shifts are in the prior chunk; the final `AZF0ENDPOINT0_AZALIA_F0_CODEC_PIN_CONTROL_AUDIO_DESCRIPTOR7` register continues at the next chunk boundary.
- ABM registers are timing-sensitive. Misusing lock, update-pending, frame-start, readback, missed-frame-clear, or sample-rate fields can cause stale luma statistics, missed histogram reads, flickering backlight, or brightness jumps.
- VGA indexed registers are compact 8-bit legacy fields. Mask/shift mistakes can affect unrelated timing, plane, cursor, or palette bits and may only show up in firmware console, boot graphics, or compatibility modes.
- Azalia fields are externally visible through HDMI/DP audio behavior. Incorrect format, channel count, sample-rate, descriptor, channel-allocation, speaker-allocation, ELD, stream-ID, or channel-status masks can cause missing audio, wrong channel layout, receiver incompatibility, HBR failures, or format-change storms.
- Status, CRC, latency, LPIB, unsolicited-response, and format-change fields may be clear-on-write or sticky. Treating them like normal configuration bits can lose diagnostics or leave interrupts asserted.
- Repeated `AZF0STREAM0` through `AZF0STREAM15` blocks are copy-sensitive. Instance-specific mistakes may only occur under high stream counts, multi-display audio, or unusual firmware routing.

## Test Signals

Useful validation is a mix of generated-header consistency and hardware behavior:

- Build AMDGPU/DCN 3.0.1 and DMUB support; missing or renamed macros should fail in register-table construction, especially in `dmub_dcn301.c`.
- Mechanically verify that every complete field in lines 44534-47180 has matching `__SHIFT` and `_MASK` macros, allowing for the known range-boundary exception at the initial `ABM1_DC_ABM1_HG_MISC_CTRL` tail.
- Diff this chunk against AMD's authoritative DCN 3.0.1 register database and adjacent DCN headers where the same ABM, VGA, and Azalia blocks are expected to be identical or intentionally changed.
- Exercise ABM/backlight on supported panels: enable/disable ABM, vary ambient/user brightness levels, check smooth duty-cycle transitions, read luma/histogram results, and test suspend/resume and modeset boundaries.
- Exercise display audio over HDMI and DP: stereo and multichannel PCM, HBR/compressed formats where supported, sample-rate changes, channel allocation, hotplug, receiver ELD parsing, silent-stream/keepalive behavior, and format-change notifications.
- Use enough active streams/endpoints to stress `AZF0STREAM0` through `AZF0STREAM15` latency and request counters, plus CRC/status paths.
- Watch kernel logs and display/audio diagnostics for missed-frame ABM reads, stuck update-pending bits, backlight flicker, VGA console corruption, audio enable/disable interrupt storms, pin-sense mismatch, LPIB/timestamp anomalies, CRC mismatches, and resume regressions.

## Cross-Chunk Notes

Adjacent chunks are required for full-file claims. The prior chunk owns the beginning of `ABM1_DC_ABM1_HG_MISC_CTRL` and earlier ABM1 fields. The next chunk continues `AZF0ENDPOINT0_AZALIA_F0_CODEC_PIN_CONTROL_AUDIO_DESCRIPTOR7` and the rest of the DCN 3.0.1 shift/mask namespace. The final per-file research document should merge those boundaries before making complete statements about all ABM instances or all Azalia endpoint fields.

### subset-b-001741: lines 47181-49549

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_1_sh_mask.h lines 47181-49549

## Scope

This chunk is a generated AMD DCN 3.0.1 register shift/mask header slice for Azalia HD-audio endpoint indirect registers. It contains preprocessor constants only; there are no functions, structs, enums, variables, allocation paths, locks, or executable branches.

The requested range starts in the tail of `AZF0ENDPOINT0_AZALIA_F0_CODEC_PIN_CONTROL_AUDIO_DESCRIPTOR7`, covers the rest of endpoint 0 pin-control/audio-status fields, covers complete endpoint 1 through endpoint 3 converter and pin-control field blocks, and enters endpoint 4 through `AZF0ENDPOINT4_AZALIA_F0_CODEC_PIN_CONTROL_MULTICHANNEL_MODE` before stopping at the comment for `AZF0ENDPOINT4_AZALIA_F0_PIN_CONTROL_CODEC_CS_OVERRIDE_0`. The visible address-block markers are `azf0endpoint1_endpointind`, `azf0endpoint2_endpointind`, `azf0endpoint3_endpointind`, and `azf0endpoint4_endpointind`.

The slice has 2,049 `#define` lines: 1,023 `__SHIFT` constants and 1,038 `_MASK` constants. The imbalance is caused by chunk boundaries and field-family details: the first lines are only the mask tail for endpoint 0 audio descriptor 7, and some descriptors include additional fields such as the stereo-frequency bitfield.

Although this source path is under a `ceph-client` mirror, the content is AMDGPU display-driver hardware metadata. It does not implement distributed filesystem behavior.

## Purpose

The purpose of this chunk is to map symbolic DCN 3.0.1 Azalia endpoint register fields to exact bit positions and bit masks. AMD display code uses these constants with generated register helper macros to program HDMI/DisplayPort audio codec state without hard-coding bit arithmetic.

Major hardware surfaces represented here are:

- Per-endpoint converter capabilities and controls: audio-widget capabilities, converter format, channel/stream ID, digital converter state, stream formats, supported size/rates, stripe control, ramp rate, GTC embedding, and GTC counter delta/min/max fields.
- Per-endpoint pin capabilities and controls: pin widget capabilities, pin capabilities, unsolicited response setup, pin sense, widget control, channel speaker allocation, audio descriptors 0 through 13, multichannel enables, lipsync response, HBR response, sink information, hot-plug/audio enable control, unsolicited response force, default pin configuration, codec channel-status overrides, association info, digital output status, LPIB snapshot/timer fields, coding type, format-changed status, wireless display identification, remote keepalive, and audio enable/disable/format-change interrupt status.
- Endpoint repetition for `AZF0ENDPOINT1`, `AZF0ENDPOINT2`, and `AZF0ENDPOINT3`, plus a partial `AZF0ENDPOINT4` block. Endpoint 0 is partial in this range because earlier endpoint 0 converter and early pin-control descriptors live in the previous chunk.

## Important APIs, Types, And Macros

The exported API is the generated field macro namespace:

- `<REGISTER>__<FIELD>__SHIFT`
- `<REGISTER>__<FIELD>_MASK`

There are no C-callable APIs or types. The important field groups are the register families exposed through those macro names:

- `AZALIA_F0_CODEC_CONVERTER_*` fields provide converter-side audio format, stream/channel binding, digital converter enables, supported stream format/rate descriptors, stripe control, ramp rate, and GTC timestamp/counter programming.
- `AZALIA_F0_CODEC_PIN_PARAMETER_*` and `AZALIA_F0_CODEC_PIN_CONTROL_*` fields provide pin widget/pin capabilities, pin sense, unsolicited response control, widget enable/control bits, speaker allocation, and per-format audio descriptor fields.
- `AUDIO_DESCRIPTOR*` fields pack `MAX_CHANNELS`, `SUPPORTED_FREQUENCIES`, optional `SUPPORTED_FREQUENCIES_STEREO`, and `DESCRIPTOR_BYTE_2`. Runtime audio code writes these from EDID/audio mode data for HDMI and DP sinks.
- `MULTICHANNEL_ENABLE`, `MULTICHANNEL_ENABLE2`, and `MULTICHANNEL_MODE` expose enable, mute, and channel-ID routing for paired and odd multichannel lanes.
- `RESPONSE_LIPSYNC` exposes `VIDEO_LIPSYNC` and `AUDIO_LIPSYNC`; `RESPONSE_HBR` exposes `HBR_CAPABLE` and `HBR_ENABLE`.
- `SINK_INFO0` through `SINK_INFO8` encode manufacturer/product IDs, sink-description length, port IDs, and up to 18 display-name bytes.
- `HOT_PLUG_CONTROL` contains `CLOCK_GATING_DISABLE`, `CLOCK_ON_STATE`, and `AUDIO_ENABLED`, which are used around audio endpoint enable/disable and configuration writes.
- `UNSOLICITED_RESPONSE_FORCE`, `RESPONSE_CONFIGURATION_DEFAULT`, `PIN_CONTROL_CODEC_CS_OVERRIDE_*`, `DIGITAL_OUTPUT_STATUS`, `LPIB*`, `CODING_TYPE`, `FORMAT_CHANGED`, `WIRELESS_DISPLAY_IDENTIFICATION`, `REMOTE_KEEPALIVE`, and `AUDIO_*_INT_STATUS` provide status, override, timer, stream-position, and interrupt/status field metadata.

These constants are normally consumed indirectly through helpers such as `set_reg_field_value`, `get_reg_field_value`, `AZ_REG_READ`, `AZ_REG_WRITE`, `REG_SET`, `REG_UPDATE`, and register-list macros that token-paste register and field names into the generated `__SHIFT`/`_MASK` symbols.

## Control Flow

This header has no local runtime control flow. Runtime sequencing is supplied by AMDGPU display audio code:

1. DCN 3.0.1 resource and DMUB code include `dcn_3_0_1_offset.h` together with `dcn_3_0_1_sh_mask.h`.
2. Audio register tables bind endpoint register offsets with these field shifts/masks.
3. Audio setup code selects an Azalia endpoint, reads or writes endpoint data through the generated access macros, and uses `set_reg_field_value`/`get_reg_field_value` to pack or extract individual fields.
4. HDMI/DP audio configuration writes speaker allocation, ACP AI support, audio descriptor entries, HBR capability, lipsync values, sink manufacturer/product IDs, sink port IDs, display-name bytes, hot-plug/audio-enable state, and status/interrupt fields in the order required by the audio block and display link state.

The macros do not encode sequencing rules. Callers must still gate clocks correctly, select the intended endpoint, apply signal-specific HDMI versus DP behavior, respect sink capabilities, and handle sticky status/interrupt bits according to the hardware specification.

## State And Persistence Behavior

The chunk stores no software state. It describes MMIO-backed hardware state in Azalia endpoint registers:

- Converter state persists the active stream format, stream/channel ID, digital converter configuration, stripe/ramp settings, and GTC timing/counter fields.
- Pin state persists reported sink capabilities, pin sense, widget control, channel/speaker allocation, audio format descriptors, HBR and lipsync response values, sink identity strings, multichannel routing, and default configuration response data.
- Hot-plug/audio enable fields control whether the audio endpoint is exposed and whether clock gating is temporarily disabled during programming.
- LPIB and timer snapshot fields expose stream-position/timing state; audio enable/disable/format-change fields expose status and interrupt state.

Persistence is hardware-defined. Configuration fields generally remain until audio reconfiguration, modeset, endpoint reset, power gating, suspend/resume, or GPU reset. Status, interrupt, snapshot, force, and keepalive fields may be read-only, sticky, write-one-to-clear, self-clearing, or side-effect-sensitive; this generated header only supplies bit positions and masks, not access semantics.

## Dependencies And Integration Points

This chunk depends on the matching DCN 3.0.1 register offset header:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_1_offset.h`

Direct DCN 3.0.1 include sites in this tree include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn301/dcn301_resource.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn301.c`

The audio behavior represented by these field names is implemented in the shared DCE/DC audio path, especially `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce/dce_audio.c`. That code reads and writes many fields present in this chunk, including `RESPONSE_HBR`, `RESPONSE_LIPSYNC`, `HOT_PLUG_CONTROL`, `CHANNEL_SPEAKER`, `AUDIO_DESCRIPTOR*`, and `SINK_INFO*`. It programs these values from `struct audio_info`, `struct audio_crtc_info`, DP link information, sink EDID data, and the active signal type.

Integration is also cross-generation. Azalia audio field names are repeated across DCE/DCN generated headers, so generic audio code can target multiple ASIC generations through per-generation register tables. The offset header and shift/mask header must be paired for the same ASIC; a DCN 3.0.1 mask used with a different offset table can compile while programming incorrect bits.

## Risks And Edge Cases

- Incorrect shifts or masks silently corrupt MMIO bitfields. High-risk fields include `HOT_PLUG_CONTROL`, audio descriptor packing, HBR capability/enable, lipsync values, sink info strings, multichannel routing, LPIB snapshot controls, and interrupt status/clear fields.
- Endpoint repetition is copy-sensitive. `AZF0ENDPOINT1`, `AZF0ENDPOINT2`, `AZF0ENDPOINT3`, and partial `AZF0ENDPOINT4` are structurally similar; an instance-specific mismatch may affect only one physical audio endpoint or one connector topology.
- The chunk boundaries are artificial. Endpoint 0 begins before this range, and endpoint 4 continues after it. The final per-file report must merge adjacent chunks before making complete claims about all Azalia endpoints.
- Audio descriptors are packed and indexed by format. A bad `MAX_CHANNELS`, `SUPPORTED_FREQUENCIES`, `SUPPORTED_FREQUENCIES_STEREO`, or `DESCRIPTOR_BYTE_2` mask can make a sink expose the wrong LPCM or compressed-audio modes to the OS audio stack.
- Hot-plug and clock-gating fields are sequencing-sensitive. Runtime code temporarily disables clock gating while programming endpoint data; wrong masks can cause writes to be ignored, audio to remain disabled, or low-power state transitions to become unreliable.
- Sink-info string fields are byte-packed across several registers. Wrong masks or shifts can corrupt monitor-name reporting or overwrite adjacent bytes.
- Interrupt/status fields can be sticky or write-one-to-clear. Generic read-modify-write helpers must use exact masks or they can lose audio enable/disable/format-change events.

## Test Signals

Useful validation signals for this chunk are:

- Build AMDGPU display code with DCN 3.0.1 enabled, especially `dcn301_resource.c`, `dmub_dcn301.c`, and shared DCE audio code, to catch missing or renamed generated field macros.
- Static consistency checks that every full register family in this range has expected `__SHIFT` and `_MASK` pairs and that repeated endpoint 1 through endpoint 3 families remain structurally consistent where the hardware specification expects repetition.
- Diff against AMD's authoritative DCN 3.0.1 register database and neighboring generated headers such as DCN 3.0.0 or later DCN 3.x variants, reviewing intentional ASIC differences.
- HDMI and DisplayPort audio runtime tests across multiple connectors/endpoints: audio enable/disable, hotplug, EDID-driven sink capability programming, LPCM and compressed formats, 192 kHz/8-channel HBR checks, channel-count changes, and DP MST audio paths.
- Validate sink metadata exposed to the OS: manufacturer/product IDs, port IDs, display-name length, and all 18 display-name bytes from `SINK_INFO4` through `SINK_INFO8`.
- Exercise suspend/resume, display modesets, connector unplug/replug, clock/power gating, and audio format changes while watching for missing audio devices, stale capabilities, audio dropouts, stuck interrupts, bad lipsync/HBR state, and kernel display/audio logs.

## Cross-Chunk Notes

Previous chunks own the beginning of the endpoint 0 Azalia block, including converter fields and early pin-control fields before the descriptor 7 tail visible here. Later chunks own the remainder of endpoint 4 after `AZF0ENDPOINT4_AZALIA_F0_PIN_CONTROL_CODEC_CS_OVERRIDE_0` and any subsequent Azalia/register families. The merge lane should combine adjacent chunks before presenting complete endpoint coverage for `dcn_3_0_1_sh_mask.h`.

### subset-b-001742: lines 49550-51891

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_1_sh_mask.h lines 49550-51891

## Scope

This chunk covers 2,342 lines from the generated DCN 3.0.1 shift/mask header. It contains only C preprocessor constants and register grouping comments; there are no functions, structs, enums, storage objects, or executable statements in this slice.

The chunk is part of the AMD display Azalia function 0 register field map. It starts in the middle of the `AZF0ENDPOINT4` output endpoint block, covers complete `AZF0ENDPOINT5`, `AZF0ENDPOINT6`, and `AZF0ENDPOINT7` output endpoint blocks, then transitions to input endpoint blocks. It includes complete `AZF0INPUTENDPOINT0` and `AZF0INPUTENDPOINT1` blocks and ends at the first field of `AZF0INPUTENDPOINT2_AZALIA_F0_CODEC_INPUT_PIN_PARAMETER_AUDIO_WIDGET_CAPABILITIES`. The section contains 2,037 `#define` entries, split almost evenly between `__SHIFT` and `_MASK` definitions, across 288 grouped register names.

## Purpose

The purpose of this header region is to describe bit positions and masks for DCN 3.0.1 display-audio hardware registers. These generated constants let AMDGPU display code address HD-audio/Azalia codec-style converter and pin fields by symbolic name instead of embedding raw bit arithmetic in implementation files.

For output endpoints, the chunk describes:

- Converter capabilities, stream format fields, stream/channel routing, digital converter flags, stream-format support, size/rate capabilities, stripe/ramp/GTC controls, and GTC counter deltas.
- Pin widget capabilities and pin controls for channel/speaker mapping, audio descriptors, multichannel routing, lipsync, HBR, sink information, hot-plug state, forced unsolicited responses, default configuration, IEC 60958 channel-status overrides, LPIB snapshots, coding type, format-change status, wireless display identification, remote keepalive, audio enable state, and audio enable/disable/format-change interrupt status.

For input endpoints, the chunk describes:

- Input converter capabilities, format selection, stream/channel IDs, digital converter flags, supported stream formats, and supported audio size/rate fields.
- Input pin capabilities and controls for unsolicited responses, input pin sense, widget input enable, multichannel routing, HBR, channel allocation, hot-plug audio state, forced unsolicited responses, default configuration, LPIB snapshots, input status, and audio infoframe fields.

This is a hardware contract file. Its value is not algorithmic behavior but precise, stable naming and numeric field layout consumed by register helper macros elsewhere in the AMD display stack.

## Important APIs, Types, And Constants

There are no callable APIs or types in this chunk. The exported interface is the macro naming scheme:

- `AZF0ENDPOINT<n>_<REGISTER>__<FIELD>__SHIFT` gives a field bit offset for an output endpoint register.
- `AZF0ENDPOINT<n>_<REGISTER>__<FIELD>_MASK` gives the corresponding field mask.
- `AZF0INPUTENDPOINT<n>_<REGISTER>__<FIELD>__SHIFT` and `_MASK` provide the same contract for input endpoint registers.
- Comments such as `// addressBlock: azf0endpoint5_endpointind` and `//AZF0ENDPOINT5_AZALIA_F0_CODEC_CONVERTER_CONTROL_CONVERTER_FORMAT` group generated constants by hardware block and register.

The output endpoint blocks in this chunk follow a repeated register family:

- `AZALIA_F0_CODEC_CONVERTER_PARAMETER_AUDIO_WIDGET_CAPABILITIES` exposes channel, amplifier, format override, stripe, processing, unsolicited response, connection-list, digital, power-control, LR-swap, delay, and type capability fields.
- `AZALIA_F0_CODEC_CONVERTER_CONTROL_CONVERTER_FORMAT` maps the audio stream format fields: number of channels, bits per sample, sample base divisor, sample base multiple, sample base rate, and stream type.
- `AZALIA_F0_CODEC_CONVERTER_CONTROL_CHANNEL_STREAM_ID` maps channel ID and stream ID fields.
- `AZALIA_F0_CODEC_CONVERTER_CONTROL_DIGITAL_CONVERTER` covers digital converter enable/status bits such as `DIGEN`, validity/config/preemphasis/copy/non-audio/professional flags, category code, and `KEEPALIVE`.
- `AZALIA_F0_CODEC_CONVERTER_PARAMETER_STREAM_FORMATS` and `SUPPORTED_SIZE_RATES` expose format, sample-rate, and bit-depth capability masks.
- `AZALIA_F0_CODEC_CONVERTER_STRIPE_CONTROL`, `CONTROL_RAMP_RATE`, `CONTROL_GTC_EMBEDDING`, and `GTC_COUNTER_DELTA*` describe converter timing and packing controls.
- `AZALIA_F0_CODEC_PIN_PARAMETER_AUDIO_WIDGET_CAPABILITIES` and `PIN_PARAMETER_CAPABILITIES` describe pin-side widget and pin capabilities, including HDMI/DP, presence-detect, trigger, EAPD, VREF, input/output, and balanced I/O flags.
- `AZALIA_F0_CODEC_PIN_CONTROL_CHANNEL_SPEAKER`, `AUDIO_DESCRIPTOR0` through `AUDIO_DESCRIPTOR13`, `MULTICHANNEL_ENABLE`, and `MULTICHANNEL_ENABLE2` describe audio channel mapping, SAD-like descriptor data, and per-channel enable/mute/channel-ID slots.
- `AZALIA_F0_CODEC_PIN_CONTROL_RESPONSE_LIPSYNC`, `RESPONSE_HBR`, and `SINK_INFO0` through `SINK_INFO8` expose sink latency, high-bit-rate audio, manufacturer/product/port, string, connection, and converter-identification fields.
- `AZALIA_F0_PIN_CONTROL_CODEC_CS_OVERRIDE_0` through `_8` define IEC 60958 channel-status override fields for mode, source number, clock accuracy, word length, sampling frequency, original sampling frequency, CGMS-A, MPEG surround, and channel numbers 0-7.
- `AZALIA_F0_AUDIO_ENABLE_STATUS`, `AUDIO_ENABLED_INT_STATUS`, `AUDIO_DISABLED_INT_STATUS`, and `AUDIO_FORMAT_CHANGED_INT_STATUS` provide audio state and interrupt flag/mask/type field definitions.

The input endpoint blocks use a smaller but related register family:

- `AZALIA_F0_CODEC_INPUT_CONVERTER_PARAMETER_AUDIO_WIDGET_CAPABILITIES`, `INPUT_CONVERTER_CONTROL_CONVERTER_FORMAT`, `INPUT_CONVERTER_CONTROL_CHANNEL_STREAM_ID`, `INPUT_CONVERTER_CONTROL_DIGITAL_CONVERTER`, `INPUT_CONVERTER_PARAMETER_STREAM_FORMATS`, and `INPUT_CONVERTER_PARAMETER_SUPPORTED_SIZE_RATES` mirror the converter-side output endpoint fields with input endpoint naming.
- `AZALIA_F0_CODEC_INPUT_PIN_PARAMETER_AUDIO_WIDGET_CAPABILITIES` and `INPUT_PIN_PARAMETER_CAPABILITIES` describe input pin widget and pin capabilities.
- `INPUT_PIN_CONTROL_UNSOLICITED_RESPONSE`, `RESPONSE_INPUT_PIN_SENSE`, `WIDGET_CONTROL`, `MULTICHANNEL_ENABLE`, `MULTICHANNEL_ENABLE2`, `RESPONSE_HBR`, `CHANNEL_ALLOCATION`, `HOT_PLUG_CONTROL`, `UNSOLICITED_RESPONSE_FORCE`, `RESPONSE_CONFIGURATION_DEFAULT`, `LPIB*`, `INPUT_STATUS_CONTROL`, and `INFOFRAME` cover input-side status, routing, default configuration, snapshot, and infoframe state.

## Control Flow

This chunk has no runtime control flow. Its effective flow is compile-time macro resolution:

1. A DCN 3.0.1 source file includes this header together with the matching register-offset header.
2. AMD display register helpers concatenate a register token and field token to resolve a `__SHIFT` or `_MASK` constant.
3. Runtime code uses the resolved constants in MMIO read/modify/write sequences or register-table initialization.

The ordering still carries generated-structure meaning. The chunk starts with the remaining output endpoint 4 pin/audio status fields, then enumerates complete output endpoints 5-7 in ascending endpoint order. It then starts the input endpoint register space, with complete input endpoints 0-1 and the beginning of input endpoint 2. Within each register group, shift definitions generally precede mask definitions for the same fields.

## State And Persistence Behavior

The header itself stores no state and persists no data. It describes hardware state in the GPU display audio block:

- Converter control fields represent programmed audio stream shape, stream/channel association, IEC/digital converter flags, keepalive, stripe/ramp behavior, and GTC embedding/counter relationships.
- Capability fields represent hardware-advertised audio widget, pin, stream format, and sample size/rate support. These are typically read-oriented even though the header only encodes bit placement, not access permissions.
- Output pin control fields represent HDMI/DP-style audio presentation state: speaker/channel mapping, audio descriptors, lipsync, HBR enablement, sink identity data, sink connection data, hot-plug audio enable state, and remote keepalive.
- IEC 60958 channel-status override fields can change transmitted channel-status metadata such as sampling frequency, word length, source number, clock accuracy, CGMS-A, and channel numbers.
- LPIB and timer snapshot fields represent hardware position/timing state, with snapshot lock and cyclic-buffer wrap count fields.
- Interrupt status fields represent audio enabled, disabled, and format-changed flag/mask/type state.
- Input pin fields represent input activity, channel layout, infoframe contents, input pin sense, unsolicited response setup, and multichannel channel-slot routing.

Persistence is hardware-defined. A write to a writable control field may survive until the next driver update, audio/display block reset, or ASIC reset. Read-only status and capability fields can be masked by the same helpers as writable fields, so callers must rely on the hardware programming model rather than this header to decide legal access direction.

## Dependencies And Integration Points

This chunk depends on the generated DCN 3.0.1 register set staying synchronized across related files:

- The matching DCN 3.0.1 offset header supplies register addresses for the register names whose fields are defined here.
- AMD display register helper macros such as `REG_GET`, `REG_SET`, `REG_UPDATE`, `FD_MASK`, and `FD_SHIFT` consume the `__SHIFT` and `_MASK` suffix conventions.
- Generated enum/value headers and hardware specs provide semantic values for fields such as stream format, widget type, pin configuration, channel allocation, and IEC channel-status fields.
- DRM display audio and ALSA-facing HDMI/DisplayPort audio paths integrate with these definitions when programming or reading GPU display audio endpoints.

The most important integration point is the preprocessor name contract. Missing or renamed macros usually fail at compile time, but wrong numeric masks or shifts can compile cleanly and produce incorrect MMIO accesses. The repeated endpoint shape also implies that generator consistency matters across endpoint instances.

## Risks And Edge Cases

- The chunk starts mid-output-endpoint 4 and ends mid-input-endpoint 2. Final per-file reconciliation must merge adjacent chunks before making whole-endpoint completeness claims.
- The output endpoint blocks are mechanically repetitive. A single endpoint-specific generator drift can be difficult to spot because most lines differ only by endpoint number.
- Shift/mask mismatches are high risk: a bad high-bit field such as `AUDIO_ENABLED`, `PRESENCE_DETECT`, or `INFOFRAME_VALID` would not necessarily be caught by compilation.
- Several full-register masks use `0xFFFFFFFFL`, including association info, LPIB, timer snapshots, stream formats, and GTC deltas. Callers need unsigned-width-safe handling.
- Capability/status fields and control fields share the same macro style. This header does not prevent software from attempting writes to read-only fields.
- `UNSOLICITED_RESPONSE_FORCE` fields can synthesize events. Accidental writes to the force bit could create misleading hotplug or audio notifications.
- Multichannel enable registers pack enable, mute, and channel-ID fields for four channel slots per register. Incorrect masks can cross into adjacent channel slot fields.
- IEC channel-status override fields include paired override-enable bits for some metadata. Programming a value without the matching enable bit, or using the wrong endpoint's override field, can silently leave transmitted metadata unchanged.
- Cross-generation reuse is risky. DCN 3.0.0 and DCN 3.0.1 have similar Azalia names, but consumers should include the ASIC-specific header that matches the register offsets used for the target hardware.

## Test Signals

Useful validation signals are mostly build-time and hardware-integration oriented:

- Compile the DCN 3.0.1 AMD display code that includes this header to catch missing macro names in register-helper expansions.
- Preprocess representative users of `FD_MASK`, `FD_SHIFT`, `REG_GET`, `REG_SET`, and `REG_UPDATE` for Azalia output/input endpoint fields to verify the expected macros resolve.
- Compare this header against the generated offset header and the register database to ensure every endpoint register has matching field definitions and that no endpoint block is truncated.
- Exercise HDMI and DisplayPort audio enumeration on DCN 3.0.1 hardware, checking advertised pin/widget capabilities, SAD/audio descriptor data, stream format/rate support, sink info, and channel allocation.
- Test audio enable/disable, format-change, and hotplug paths while watching the audio enable status and interrupt status fields.
- Exercise stereo, multichannel, and HBR audio modes to validate multichannel enable/mute/channel-ID fields, HBR capability/enable bits, and IEC channel-status overrides.
- Test suspend/resume and display reset paths to confirm converter, pin, hotplug, LPIB snapshot, infoframe, and interrupt state is restored or re-read correctly.
- For input endpoints, validate input activity, infoframe-valid, channel-layout, input pin sense, and unsolicited-response behavior if the hardware path exposes those features.

## Open Cross-Chunk Questions

- The later merge lane should combine this with the previous chunk to present endpoint 4 as a complete output endpoint block.
- The later merge lane should combine this with the next chunk to present `AZF0INPUTENDPOINT2` as a complete input endpoint block.
- Whole-file analysis should verify whether all expected output and input endpoint counts for DCN 3.0.1 are present and whether generated field layouts match the authoritative AMD register source.

### subset-b-001743: lines 51892-53361

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_1_sh_mask.h lines 51892-53361

## Purpose

This chunk is generated AMD DCN 3.0.1 register field metadata for Azalia HD-audio input endpoints. It contains no executable C logic; it publishes preprocessor constants that describe bit positions (`__SHIFT`) and bitmasks (`_MASK`) for indirect Azalia codec input-converter and input-pin registers.

The requested range covers the tail of `AZF0INPUTENDPOINT2` and complete repeated layouts for `AZF0INPUTENDPOINT3` through `AZF0INPUTENDPOINT7`. These are per-endpoint input-side HDA codec register definitions under generated address blocks such as `azf0inputendpoint3_inputendpointind`. The chunk ends the header with `#endif`, so later content does not continue after this range. Although the repository path is under a local `ceph-client` source mirror, this file is AMDGPU display/audio hardware metadata, not Ceph filesystem code.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, locks, allocation paths, or include directives in this range. The interface is the generated macro namespace:

- `<REGISTER>__<FIELD>__SHIFT`: low-bit position for a field in a 32-bit register value.
- `<REGISTER>__<FIELD>_MASK`: field mask for extracting or updating that field.
- `//AZF0INPUTENDPOINT*_...` comments: generated register grouping markers.
- `// addressBlock: azf0inputendpoint*_inputendpointind`: generated indirect-register block markers.

The range contains 1,321 `#define` lines: 161 for the end of `AZF0INPUTENDPOINT2`, then 232 each for endpoints 3, 4, 5, 6, and 7. Endpoint 2 starts mid-register in this chunk: its `INPUT_PIN_PARAMETER_AUDIO_WIDGET_CAPABILITIES__AUDIO_CHANNEL_CAPABILITIES__SHIFT` and earlier input-converter definitions are owned by the previous chunk, while this range includes the rest of that pin block and all following endpoint-2 pin-control registers.

Major register groups:

- `*_AZALIA_F0_CODEC_INPUT_CONVERTER_PARAMETER_AUDIO_WIDGET_CAPABILITIES`: input converter widget capability fields such as channel capability, amplifier presence, format override, stripe, processing-widget, unsolicited-response capability, digital flag, power control, LR swap, delay, and widget type.
- `*_AZALIA_F0_CODEC_INPUT_CONVERTER_CONTROL_CONVERTER_FORMAT`: stream format fields for channel count, bits per sample, sample-base divisor/multiple/rate, and stream type.
- `*_AZALIA_F0_CODEC_INPUT_CONVERTER_CONTROL_CHANNEL_STREAM_ID`: channel and stream-id assignment fields.
- `*_AZALIA_F0_CODEC_INPUT_CONVERTER_CONTROL_DIGITAL_CONVERTER`: digital converter control/status bits such as `DIGEN`, validity/config/pre-emphasis/copy/non-audio/professional/level flags, channel-status category code, and keepalive.
- `*_AZALIA_F0_CODEC_INPUT_CONVERTER_PARAMETER_STREAM_FORMATS` and `*_SUPPORTED_SIZE_RATES`: advertised stream-format, sample-rate, and bit-depth capability masks.
- `*_AZALIA_F0_CODEC_INPUT_PIN_PARAMETER_AUDIO_WIDGET_CAPABILITIES` and `*_PARAMETER_CAPABILITIES`: input pin widget and pin capability fields, including impedance sense, trigger requirement, jack-detection capability, output/input capability, HDMI/DP indicators, VREF control, EAPD capability, and related widget flags.
- `*_AZALIA_F0_CODEC_INPUT_PIN_CONTROL_UNSOLICITED_RESPONSE`: unsolicited-response tag and enable fields.
- `*_AZALIA_F0_CODEC_INPUT_PIN_CONTROL_RESPONSE_INPUT_PIN_SENSE`: impedance-sense value and presence-detect bit.
- `*_AZALIA_F0_CODEC_INPUT_PIN_CONTROL_WIDGET_CONTROL`: input-enable control.
- `*_AZALIA_F0_CODEC_INPUT_PIN_CONTROL_MULTICHANNEL_ENABLE` and `*_MULTICHANNEL_ENABLE2`: per-channel enable, mute, and channel-id fields for multichannel slots 0-7.
- `*_AZALIA_F0_CODEC_INPUT_PIN_CONTROL_RESPONSE_HBR`: high-bit-rate capable/enable flags.
- `*_AZALIA_F0_CODEC_INPUT_PIN_CONTROL_CHANNEL_ALLOCATION`: HDMI/DP channel allocation byte.
- `*_AZALIA_F0_CODEC_INPUT_PIN_CONTROL_HOT_PLUG_CONTROL`: clock-gating disable, clock-on state, and audio-enabled fields.
- `*_AZALIA_F0_CODEC_INPUT_PIN_CONTROL_UNSOLICITED_RESPONSE_FORCE`: forced unsolicited-response payload and trigger bit.
- `*_AZALIA_F0_CODEC_INPUT_PIN_CONTROL_RESPONSE_CONFIGURATION_DEFAULT`: HDA default-configuration fields such as sequence, association, misc, color, connection type, default device, location, and port connectivity.
- `*_AZALIA_F0_CODEC_INPUT_PIN_CONTROL_LPIB*`: link-position-in-buffer snapshot lock, wrap count, LPIB value, and timer snapshot.
- `*_AZALIA_F0_CODEC_INPUT_PIN_CONTROL_INPUT_STATUS_CONTROL`: input activity, channel layout, and unsolicited-response enables for activity and channel-layout/channel-status infoframe changes.
- `*_AZALIA_F0_CODEC_INPUT_PIN_CONTROL_INFOFRAME`: audio infoframe channel count, channel allocation, infoframe byte 5, and valid bit.

## Control Flow

This header has no runtime control flow. Runtime behavior is supplied by the AMD display/audio driver:

1. DCN301 resource and DMUB code include `dcn_3_0_1_offset.h` and this matching `dcn_3_0_1_sh_mask.h`.
2. `dcn301_resource.c` builds Azalia audio objects with `audio_regs(0..6)`, `DCE120_AUD_COMMON_MASK_SH_LIST(__SHIFT)`, and `DCE120_AUD_COMMON_MASK_SH_LIST(_MASK)`.
3. `dce_audio.c` programs Azalia endpoint registers indirectly: it writes an index into `AZALIA_F0_CODEC_ENDPOINT_INDEX` and reads/writes payload through `AZALIA_F0_CODEC_ENDPOINT_DATA`.
4. Generic audio setup code configures supported formats, rates, DTO clocks, packetization, and AFMT/stream-encoder state around those endpoint accessors.

The input-endpoint-specific symbols in this chunk are generated metadata for indirect endpoint register payload layouts. In this tree, direct display audio code primarily uses the generic endpoint index/data masks and output/audio-function fields; `rg` did not find direct references to `AZF0INPUTENDPOINT[2-7]_AZALIA_F0_CODEC_INPUT_*` outside generated register headers. That means this chunk is an ABI-style hardware description that can be used by future diagnostics, firmware-facing code, or HDA input-endpoint paths even when not actively consumed by the current DCN301 display path.

## State And Persistence Behavior

The file stores no software state and persists nothing by itself. It describes hardware-visible fields for Azalia input endpoint state:

- Converter format state: channel count, sample size, sample-rate base/divider/multiple, stream type, stream ID, and channel ID.
- Digital converter state: enablement, channel status attributes, non-audio/professional/copy flags, category code, validity, and keepalive behavior.
- Advertised capability state: supported stream formats, sample rates, bit depths, widget capabilities, pin capabilities, HDMI/DP identity, jack-detection/presence capability, VREF and EAPD support.
- Pin-control state: input enable, multichannel enable/mute/channel mapping, HBR enable, channel allocation, hot-plug audio enablement, unsolicited-response enable/force, default configuration, LPIB snapshots, input activity, channel layout, and infoframe validity.

Persistence and side effects are hardware-defined. Configuration fields typically remain until driver reprogramming, codec reset, power transition, suspend/resume, or ASIC reset. Status-like fields such as presence detect, LPIB snapshots, activity, infoframe validity, and hot-plug/audio state can change asynchronously with hardware events. Force/clear/update-style fields may be self-clearing or side-effectful even though the header only exposes masks.

## Dependencies And Integration Points

This chunk must stay synchronized with:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_1_offset.h`, which supplies the matching `mmAZF0INPUTENDPOINT*_AZALIA_F0_CODEC_INPUT_ENDPOINT_INDEX/DATA` MMIO offsets and `ixAZF0INPUTENDPOINT*_...` indirect register indexes.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn301/dcn301_resource.c`, which includes this generated header and constructs DCN301 audio register, shift, and mask tables.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn301.c`, which includes the same generated offset/mask pair for DMUB register definitions.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce/dce_audio.h` and `dce_audio.c`, which define the generic Azalia endpoint access model and audio-object interface.
- HDA/Azalia and HDMI/DP audio concepts represented elsewhere in the driver: EDID SAD parsing, audio component ELD delivery, AFMT packet programming, stream-encoder audio setup, and DTO clock programming.

The key integration contract is indirect register addressing. Endpoint-specific `ixAZF0INPUTENDPOINT*` indexes select logical HDA codec registers, while the generated `__SHIFT`/`_MASK` constants describe the fields inside the value transferred through endpoint data registers. Any consumer must pair the correct endpoint instance, indirect index, and field layout.

## Risks And Edge Cases

- Mask/shift drift is the central risk. These constants are untyped macros; a wrong mask can compile cleanly and corrupt the wrong bit in an audio endpoint register.
- The repeated endpoint layouts invite copy/paste or generator errors. Endpoints 3-7 should have identical field layouts, while endpoint 2 is split across chunk boundaries. A mismatch may affect only one audio input endpoint and escape ordinary display-output tests.
- Indirect register access requires correct endpoint selection and serialized index/data operations. Mixing endpoint index registers or racing index/data writes can read or update the wrong logical register.
- Input endpoint support may be dormant in this tree. Because the DCN301 display path does not directly reference these `INPUTENDPOINT` macros, compile coverage alone may not detect stale or incorrect generated definitions.
- HDA semantic fields have side effects. Unsolicited-response force/enable, hot-plug audio enable, HBR enable, LPIB snapshot lock, activity UR enables, and infoframe-valid fields can create interrupt noise, stale status, missed presence changes, or broken audio capture/loopback behavior if programmed incorrectly.
- Format and channel mapping fields are user-visible. Bad sample-size/rate/channel fields, channel allocation, multichannel mutes, or channel IDs can cause silent channels, swapped channels, unsupported-format advertisement, or HBR playback/capture failures.
- Capability fields influence policy decisions. Incorrect HDMI/DP, input/output capable, jack-detection, VREF, EAPD, supported-size/rate, or widget-type masks could cause the driver or firmware to expose nonexistent functionality or hide supported functionality.

## Test Signals

Useful validation is a mix of generated-header consistency and hardware/audio behavior:

- Build AMDGPU/DC with DCN301 support enabled; generated include drift should surface in resource construction, DMUB register compilation, and shared audio definitions that consume this header.
- Mechanically verify every field in this range has the expected `__SHIFT` and `_MASK` pair, and that each mask aligns with its shift and width.
- Compare endpoint 3, 4, 5, 6, and 7 field layouts for exact consistency, then compare endpoint 2 against adjacent chunks to ensure the split register is complete after merge.
- Cross-check `dcn_3_0_1_sh_mask.h` against `dcn_3_0_1_offset.h`: every `AZF0INPUTENDPOINT*_...` field group should have a matching `ixAZF0INPUTENDPOINT*_...` indirect index where the generated register database expects one.
- Diff these definitions against nearby AMD generated headers such as other `dcn_3_*_sh_mask.h` files when the Azalia input endpoint layout is expected to match.
- On hardware or emulator paths that exercise input endpoints, test converter format programming, stream/channel IDs, digital converter enable/keepalive, supported-rate reporting, HBR enablement, multichannel enable/mute/channel IDs, channel allocation, LPIB snapshot reads, and input infoframe validity.
- Exercise hotplug, suspend/resume, codec reset, runtime power transitions, and repeated unsolicited-response paths while monitoring kernel logs for HDA/Azalia errors, missed presence changes, stuck activity/status bits, or interrupt storms.
- For user-visible audio validation, check channel mapping, sample rates and bit depths, HDMI/DP HBR behavior, ELD/EDID-derived mode exposure, and audio continuity across modesets and fast updates.

## Cross-Chunk Notes

The previous chunk owns the beginning of `AZF0INPUTENDPOINT2`, including its input-converter blocks and the first field of `INPUT_PIN_PARAMETER_AUDIO_WIDGET_CAPABILITIES`. This chunk completes endpoint 2's pin-side definitions, contains complete endpoint 3-7 input converter and input pin layouts, and closes `dcn_3_0_1_sh_mask.h`. The final per-file research document should merge this with adjacent chunks before making complete claims about all Azalia function, output endpoint, or input endpoint definitions in the generated DCN 3.0.1 mask header.
