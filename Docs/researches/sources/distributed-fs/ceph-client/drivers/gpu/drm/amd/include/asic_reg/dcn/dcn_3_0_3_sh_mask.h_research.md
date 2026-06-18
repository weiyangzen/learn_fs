# Research: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_3_sh_mask.h

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-001781`: lines 1-2407, `Docs/researches/chunks/subset-b-001781_research.md`
- `subset-b-001782`: lines 2408-4719, `Docs/researches/chunks/subset-b-001782_research.md`
- `subset-b-001783`: lines 4720-7368, `Docs/researches/chunks/subset-b-001783_research.md`
- `subset-b-001784`: lines 7369-9903, `Docs/researches/chunks/subset-b-001784_research.md`
- `subset-b-001785`: lines 9904-12415, `Docs/researches/chunks/subset-b-001785_research.md`
- `subset-b-001786`: lines 12416-14925, `Docs/researches/chunks/subset-b-001786_research.md`
- `subset-b-001787`: lines 14926-17341, `Docs/researches/chunks/subset-b-001787_research.md`
- `subset-b-001788`: lines 17342-19736, `Docs/researches/chunks/subset-b-001788_research.md`
- `subset-b-001789`: lines 19737-22116, `Docs/researches/chunks/subset-b-001789_research.md`
- `subset-b-001790`: lines 22117-24606, `Docs/researches/chunks/subset-b-001790_research.md`
- `subset-b-001791`: lines 24607-27132, `Docs/researches/chunks/subset-b-001791_research.md`
- `subset-b-001792`: lines 27133-29716, `Docs/researches/chunks/subset-b-001792_research.md`
- `subset-b-001793`: lines 29717-32085, `Docs/researches/chunks/subset-b-001793_research.md`
- `subset-b-001794`: lines 32086-34399, `Docs/researches/chunks/subset-b-001794_research.md`
- `subset-b-001795`: lines 34400-35366, `Docs/researches/chunks/subset-b-001795_research.md`

## Chunk Research

### subset-b-001781: lines 1-2407

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

### subset-b-001782: lines 2408-4719

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_3_sh_mask.h lines 2408-4719

## Scope And Purpose

This chunk is generated AMD DCN 3.0.3 register field metadata. It contains no executable C logic; its API surface is preprocessor constants that describe field shifts and masks for 32-bit MMIO registers. The matching `dcn_3_0_3_offset.h` header provides register offsets, while this file provides the bit layout consumed by AMDGPU Display Core and DMUB register helper macros.

The requested range begins inside the `DMCU_INTERRUPT_TO_UC_XIRQ_IRQ_SEL_CONT2` register, covers DMCU-to-microcontroller interrupt status/enable fields for DPCS transmit interrupts, spans the `dce_dc_dmu_ihc_dispdec` block for GPU timer snapshots, display interrupt status continuation registers, and interrupt destination routing registers, then enters the `dce_dc_dmu_dmcub_dispdec` block for the beginning of DMCUB memory-window and interrupt-control definitions. It ends at the `//DMCUB_INTERRUPT_STATUS` marker; the actual DMCUB status field definitions are owned by the next chunk.

Although the repository path is under a `ceph-client` source mirror, this header is AMD GPU display hardware metadata, not Ceph filesystem logic.

## Important APIs, Types, And Macros

There are no functions, structs, enums, globals, locks, allocations, callbacks, or includes in this chunk. The relevant interface is the generated macro convention:

- `<REGISTER>__<FIELD>__SHIFT`: low bit position for a field.
- `<REGISTER>__<FIELD>_MASK`: raw bitmask for that field before shifting.
- `// addressBlock: ...`: generated hardware block grouping.
- `//<REGISTER>`: generated register grouping marker.

This slice contains 2,187 `#define` entries, mostly paired shift/mask definitions. The pair count is not perfectly symmetric because the range starts in the middle of one register and ends just before the following register's fields. There are two address blocks in scope:

- `dce_dc_dmu_ihc_dispdec`: display interrupt handler/controller metadata, GPU timer read/start-position fields, interrupt status continuation, and interrupt destination routing.
- `dce_dc_dmu_dmcub_dispdec`: the start of the DMCUB display microcontroller register metadata, especially address windows and interrupt enable/ack fields.

Major register families:

- `DMCU_INTERRUPT_STATUS_2` and `DMCU_INTERRUPT_TO_UC_EN_MASK_2`: latched/clearable DPCS TXA-TXG interrupt status bits and enable masks for routing those events to the DMCU microcontroller path.
- `DC_GPU_TIMER_START_POSITION_*`, `DC_GPU_TIMER_READ`, and `DC_GPU_TIMER_READ_CNTL`: per-display timing selector fields for V_UPDATE, VSTARTUP, VREADY, FLIP, V_UPDATE_NO_LOCK, FLIP_AWAY, VSYNC_NOM, and full-width timer readback.
- `DISP_INTERRUPT_STATUS` through `DISP_INTERRUPT_STATUS_CONTINUE25`: a dense interrupt-status cascade covering OTG/OPTC, DIG, AUX, HPD/HPDRX, I2C/DDC, ABM, DMCU, DCPG power events, DCHUB/HUBP, DPP, MPC/OPP, DSC, MCIF writeback, DMCUB mailbox/timer/fault events, MMHUBBUB warmup, and continuation bits that link one status register to the next.
- `DCCG_INTERRUPT_DEST`, `DMU_INTERRUPT_DEST*`, `DCPG_INTERRUPT_DEST*`, `MMHUBBUB_INTERRUPT_DEST`, `WB_INTERRUPT_DEST`, `DCHUB_INTERRUPT_DEST*`, `DCHUB_PERFCOUNTER_INTERRUPT_DEST`, `DPP_PERFCOUNTER_INTERRUPT_DEST`, `MPC_INTERRUPT_DEST`, `OPP_INTERRUPT_DEST`, `OPTC_INTERRUPT_DEST`, `OTG0_INTERRUPT_DEST` through `OTG5_INTERRUPT_DEST`, `DIG_INTERRUPT_DEST`, `I2C_DDC_HPD_INTERRUPT_DEST`, `DIO_INTERRUPT_DEST`, `DCIO_INTERRUPT_DEST`, `HPD_INTERRUPT_DEST`, `AZ_INTERRUPT_DEST`, `AUX_INTERRUPT_DEST`, and `DSC_INTERRUPT_DEST`: interrupt destination selector fields for the same display subblocks and events.
- `DMCUB_REGION0/1/2/4/5/6/7_OFFSET`, matching `_OFFSET_HIGH`, and matching `_TOP_ADDRESS`: 40-bit-style low/high offset pieces plus top-address and enable fields for DMCUB memory regions. Low offsets start at bit 8 with `0xFFFFFF00L`; high offsets use `0x0000FFFFL`; top addresses use `0x1FFFFFFFL` with enable at bit 31.
- `DMCUB_REGION3_CW0` through `DMCUB_REGION3_CW7`: per-code-window base, top, enable, offset, and offset-high definitions for the DMCUB region-3 code-window aperture.
- `DMCUB_INTERRUPT_ENABLE` and `DMCUB_INTERRUPT_ACK`: timer, inbox, outbox, GPINT0-2, and undefined-address-fault interrupt enable/acknowledge bits. These are the only DMCUB interrupt-control fields fully defined in this chunk.

## Control Flow

This header has no local control flow. Runtime flow is supplied by code that includes it:

1. DCN303 resource and IRQ code include `dcn_3_0_3_offset.h` and this matching mask header.
2. Register-table macros expand offsets from the offset header and masks/shifts from this header into per-ASIC tables.
3. AMDGPU Display Core and DMUB service code use helper macros such as `REG_READ`, `REG_WRITE`, `REG_SET`, `REG_UPDATE`, `REG_GET`, and IRQ table initializers to program or decode hardware registers.
4. Hardware interprets the encoded bits as timer selection, interrupt status, interrupt routing, DMCUB memory-window configuration, or DMCUB interrupt enable/ack state.

Direct consumers in this tree include `display/dc/resource/dcn303/dcn303_resource.c`, `display/dc/irq/dcn303/irq_service_dcn303.c`, and `display/dmub/src/dmub_dcn303.c`. The DMUB file constructs `dmub_srv_dcn303_regs` from `DMUB_COMMON_REGS()`, `DMCUB_INTERNAL_REGS()`, and `DMUB_COMMON_FIELDS()`, using `REG_OFFSET`, `FD_MASK`, and `FD_SHIFT` against this generated header. Shared DMUB definitions in nearby headers, such as the DCN31 register list, show the concrete DMCUB fields used by the service layer, including region code-window top/enable fields and `DMCUB_INTERRUPT_ENABLE`/`DMCUB_INTERRUPT_ACK`.

## State And Persistence Behavior

The header stores no software state and persists nothing by itself. It describes hardware state:

- Interrupt status fields are volatile or latched hardware events. Some fields use paired occurred/clear naming, and acknowledgement or clear writes may have side effects.
- Interrupt destination fields persist routing policy inside the display interrupt controller until reprogrammed, reset, or affected by power management.
- GPU timer selector/read fields expose display timing snapshots and timer readback state; timing values change as scanout and vertical events progress.
- DMCUB region fields persist firmware-visible memory window configuration: offsets, top addresses, enables, and code-window base/top mappings.
- DMCUB interrupt enable fields persist which DMCUB events can raise interrupts; ACK fields are write-side clear/ack controls for timer, inbox/outbox, GPINT, and undefined-address-fault events.

Power transitions, DMCUB reset, display core reset, ASIC reset, suspend/resume, and firmware boot sequencing can all change or require reprogramming of the described hardware state. The macros do not encode ordering constraints; callers must know when a register is safe to read, update, or acknowledge.

## Dependencies And Integration Points

This chunk must remain synchronized with:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_3_offset.h`, which supplies the matching register offsets for these field names.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn303/dcn303_resource.c`, which includes the header for DCN303 resource construction and register-table initialization.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn303/irq_service_dcn303.c`, which includes the header for DCN303 IRQ source mapping and register-backed IRQ entries.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn303.c`, which includes this header to build the DCN303 DMUB register, shift, and mask tables.
- Shared DMUB service code and headers that use common DMCUB register names for firmware boot, memory-window setup, inbox/outbox traffic, GPINT signaling, fault handling, and debug snapshots.
- Display subsystems represented by interrupt destination/status fields: OTG/OPTC, HUBP/DCHUB, DPP, MPC, OPP, DCCG, DCPG, DIO/DCIO, AUX/DDC/I2C, HPD/HPDRX, DSC, MCIF writeback, Azalia audio, ABM, DMCU, and DMCUB.

The integration contract is exact name/value parity. Register helpers generally combine a `REG_*` offset with a field name that resolves through these masks and shifts. Pairing a field from the wrong ASIC version, wrong register instance, or wrong companion offset header can compile in some macro contexts but update the wrong hardware bit.

## Risks And Edge Cases

- Generated mask/shift drift is the core risk. A one-bit error can silently corrupt interrupt routing, clear the wrong latched event, or misconfigure a DMCUB firmware memory aperture.
- This chunk starts and ends on chunk boundaries that split register groups. `DMCU_INTERRUPT_TO_UC_XIRQ_IRQ_SEL_CONT2` is missing its first TXA/TXB shift definitions in this document, and `DMCUB_INTERRUPT_STATUS` is only a marker here. The final per-file research must merge adjacent chunks before making complete claims for those registers.
- Interrupt status continuation registers are dense and repetitive. A bad continuation bit can hide later status registers; a bad per-event bit can misreport only one display pipe, endpoint, or subblock.
- ACK/clear fields are side-effectful. Treating `DMCUB_INTERRUPT_ACK` or DMCU clear masks like persistent configuration can drop evidence of pending events or suppress servicing.
- Destination fields affect system-level interrupt routing. Incorrect routing for HPD, AUX/DDC, vblank/vline, flip, DSC, DMCUB, DCPG, or writeback events can cause missed hotplug, display update stalls, interrupt storms, or events delivered to an unexpected handler.
- DMCUB region windows are security- and stability-sensitive. Wrong base/top/offset masks can point firmware execution or data windows at the wrong memory, trigger undefined-address/fetch/write faults, or break mailbox setup during boot.
- The DCN303 DMCUB interrupt set in this chunk exposes only GPINT0-2 and no `DMCUB_GPINT_IH_INT_EN` field seen on newer ASIC headers. Shared code must use the correct per-ASIC common field list.
- These are untyped C macros. The compiler will not prevent mixing a mask from one register with a shift from another when generic helper code is misused.

## Test Signals

Useful validation is mostly compile-time, generated-header consistency, and hardware smoke behavior:

- Build AMDGPU with DCN303 display support enabled; `dcn303_resource.c`, `irq_service_dcn303.c`, and `dmub_dcn303.c` should compile against the generated names.
- Mechanically verify every field in this range has the expected mask/shift pair, and that each mask aligns with its shift and width. Treat the first and last partial register groups as cross-chunk checks.
- Cross-check all registers in this range against `dcn_3_0_3_offset.h` so offset names and field names come from the same generated ASIC database.
- Compare repeated instance families: `OTG0`-`OTG5` destination layouts, DMCUB region 0/1/2/4/5/6/7 fields, and DMCUB region-3 `CW0`-`CW7` fields should be structurally consistent where the hardware instances are expected to match.
- Exercise IRQ paths for vblank/vstartup, vline, flip, HPD/HPDRX, AUX/DDC/I2C completion, DSC errors/underflow, writeback, DCPG power transitions, DMCU/DMCUB mailbox events, and DMCUB faults while checking for missed events or interrupt storms.
- Validate DMUB firmware boot and reset on DCN303 hardware: region windows should be programmed with correct offsets/top/enables, and DMCUB interrupt enable/ack should allow expected mailbox or trace events to be serviced.
- Run suspend/resume, display hotplug, modeset, fast update, PSR/ABM-related, and DMCUB reset paths to catch stale interrupt destination state or DMCUB window state after power transitions.
- For timer fields, inspect vblank counters, scanout position, and timing-related debug paths around modesets and vertical events to confirm GPU timer selectors and readback masks decode plausible values.

## Cross-Chunk Notes

The previous chunk owns the beginning of the DMCU interrupt-selector area, including earlier `DMCU_INTERRUPT_TO_UC_XIRQ_IRQ_SEL_CONT2` shift definitions. This chunk completes that selector's visible masks, covers the main display interrupt-status and destination-routing surface, and begins DMCUB region and interrupt-control metadata. The next chunk begins with the `DMCUB_INTERRUPT_STATUS` fields and continues DMCUB control/mailbox/fault definitions, so final per-file research should merge this document with adjacent chunks before summarizing the complete DCN 3.0.3 mask header.

### subset-b-001783: lines 4720-7368

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_3_sh_mask.h lines 4720-7368

## Purpose

This chunk is generated AMD DCN 3.0.3 register field metadata. It contains no executable C logic; it exposes C preprocessor constants naming bit positions (`__SHIFT`) and masks (`_MASK`) for 32-bit MMIO register fields used by the AMD display driver. Consumer code pairs these definitions with the matching `dcn_3_0_3_offset.h` register offsets and AMD register helpers such as `REG_SET`, `REG_UPDATE`, `REG_GET`, `SR`, `SRI`, and block-specific field-list macros.

The requested range starts in the middle of the DMCUB interrupt/status block, then covers DMCUB mailbox, scratch, security, timer, memory-power, and GPINT fields; MCIF writeback and MMHUBBUB fields; one DC perfmon instance; Azalia/HDA audio endpoint, controller, root, stream, and input endpoint fields; DCHUBBUB SDPIF, return-path, arbitration, watermark, CRC, timing, clock, reset, timeout, and FMON fields; another DC perfmon instance; DCN VM context/fault fields; and the first HUBP0 surface/viewport/request/control/clock/perf-measurement fields. The slice has 2,066 `#define` lines: 1,035 shift definitions and 1,031 mask definitions.

Although the source path is under a local `ceph-client` mirror, this file is AMDGPU display-controller hardware metadata. It does not implement Ceph or distributed filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, global variables, includes, locks, allocations, or persistence APIs in this chunk. The public interface is the generated macro namespace:

- `<REGISTER>__<FIELD>__SHIFT`: least-significant bit position of a hardware register field.
- `<REGISTER>__<FIELD>_MASK`: mask used to isolate or update that field.
- Address-block comments such as `dce_dc_mmhubbub_mcif_wb0_dispdec` and `dce_dc_dcbubp0_dispdec_hubp_dispdec`: generator breadcrumbs that group registers by display hardware block.

Major macro families in this slice:

- `DMCUB_*`: interrupt status/type, external interrupt status/context/ack, instruction/data fault addresses, security reset and fault-clear controls, memory QoS/space controls, inbox/outbox base/size/read/write pointers, timer triggers/window/current value, scratch registers 0-15, DMCUB control bits, GPINT data registers, undefined-address fault address, light-sleep wake interrupt enable, memory power control, and processor ID.
- `MCIF_WB_*`: display writeback buffer-manager software control/status, buffer pitch, per-buffer Y/C address low/high registers, per-buffer status/status2 and resolution, arbitration, SCLK/NB pstate/self-refresh controls, VCE buffer manager controls, clock gating, luma/chroma sizes, VMID, memory-power, and minimum time-to-output controls.
- `MMHUBBUB_*`, `WBIF0_*`, `MCIF_*`, and `VGA_SRC_SPLIT_CNTL`: writeback/hubbub warmup controls and base addresses, watermark and pstate-latency values, memory-power and clock/soft-reset controls, WBIF misc/phase counters, VGA/MCIF write-combine controls, DMU interface error status, client unit IDs, and warmup VMID controls.
- `DC_PERFMON3_*` and `DC_PERFMON4_*`: counter selection, increment mode, run mode, threshold/interrupt policy, counter state, perfmon start/stop/reporting, high/low counter reads, and counter-value interrupt status/ack fields for MMHUBBUB and DCHUBBUB perfmon blocks.
- `AZF0ENDPOINT[0-7]_*`, `AZF0INPUTENDPOINT[0-7]_*`, `AZF0STREAM[8-15]_*`, and `AZALIA_*`: indexed codec endpoint/stream registers, controller clock gating, audio DTO/control, SOCCLK, DMA, RIRB/CORB/BDL controls, payload capability and stream arbitration, CRC controls/results, memory-power state, root codec vendor/revision/channel/power/reset/sync controls, GTC group offsets, and audio port connectivity fields.
- `DCHUBBUB_SDPIF_*`, `VM_REQUEST_PHYSICAL`, and `DCHUBBUB_FORCE_IO_STATUS_*`: VM physical request policy, framebuffer/AGP/HBM address ranges, local HBM lock control, per-pipe security levels, SDPIF memory-power and config bits, and forced I/O status.
- `DCHUBBUB_RET_PATH_*`: return-path DCC configuration registers for multiple pipes, return-path memory-power control/status, and DCHUBBUB CRC select/mask/window/source and CRC result fields.
- `DCHUBBUB_ARB_*`, `SURFACE_CHECK*`, `VTG*`, `DCHUBBUB_*`, `DCFCLK_CNTL`, and `FMON_*`: arbitration outstanding request caps, saturation and QoS force values, DRAM state policy, A/B/C/D urgency and self-refresh/DRAM-clock-change watermarks, watermark change policy, global timer, surface-check addresses, VTG selection, hubbub soft reset and clock status, performance measurement windows, timeout detection/interrupts, fractional urgency bandwidth, and frequency-monitor controls.
- `DCN_VM_CONTEXT[0-15]_*`, `DCN_VM_DEFAULT_ADDR_*`, and `DCN_VM_FAULT_*`: VM page table base/start/end addresses, page-table depth and block size, default address/control fields, fault interrupt enable/clear/mode/status, fault address, and fault attribution fields.
- `HUBP0_*`: surface pixel format/rotation/mirroring/alpha, address and tiling configuration, primary/secondary viewport start/dimension for luma and chroma, request-size configuration, HUBP blank/disable/VTG/timeout/underflow controls, clock gating/status, VM page size, and DCFCLK/DPPCLK measurement-window controls.

## Control Flow

This header has no runtime control flow. Runtime sequencing is in the display driver:

1. DCN303 resource, IRQ, and DMUB service code include `dcn_3_0_3_offset.h` and this matching `dcn_3_0_3_sh_mask.h`.
2. Resource construction token-pastes register and field names into typed register, shift, and mask tables. Examples in this tree include `dcn303_resource.c` building `hubbub_shift`, `audio_shift`, `hubp_shift`, `mcif_wb30_shift`, and corresponding mask tables from block macros.
3. Block implementations operate through those tables with register-helper calls. DMUB code reads and writes DMCUB mailbox, interrupt, and fault fields; DCE audio code uses Azalia endpoint fields; HUBP/HUBBUB/MMHUBBUB code programs surface fetch, VM, arbitration, watermark, writeback, memory-power, and clocking state.
4. Hardware observes those MMIO fields during boot/display resource initialization, DMUB command exchange, modesets, page flips, audio stream setup, display writeback capture, memory watermark programming, VM context setup, fault handling, perf/debug capture, suspend/resume, and ASIC reset flows.

The macros do not encode ordering. Consumers must still sequence clocks and resets before programming gated blocks, update writeback buffers only when buffer fences/state allow it, program VM page-table fields coherently, acknowledge sticky interrupt/status fields correctly, and respect double-buffer or pending-update hardware semantics where applicable.

## State And Persistence Behavior

The chunk stores no software state. It describes MMIO-backed GPU state:

- DMCUB fields represent firmware-facing mailbox rings, timers, scratch state, GPINT data, interrupt status/type/ack state, fault addresses, security reset state, and microcontroller memory-power policy.
- MCIF writeback fields represent capture buffer addresses and dimensions, buffer-manager state, luma/chroma pitch and allocation size, VCE/writeback flow-control policy, self-refresh and pstate-change policy, clock gating, and VMID selection for writeback memory traffic.
- MMHUBBUB and DCHUBBUB fields represent display fabric warmup, memory power, clocking, resets, arbitration, watermarks, self-refresh and DRAM clock-change thresholds, urgency bandwidth, timeout detection, surface-check addresses, CRC collection, and debug/frequency/performance measurement state.
- Azalia/HDA fields represent audio codec endpoint/index/data windows, stream DMA/ring controls, audio DTO clocking, CRC/debug paths, root codec power/reset/channel capabilities, and output/input port connectivity.
- VM context fields represent display VM page table base/start/end ranges and page-table format for contexts 0 through 15, plus default address and fault attribution/status state.
- HUBP0 fields represent plane surface format, tiling/addressing, viewport geometry, fetch request sizing, blank/disable/underflow/timeout status, clock status, VM page sizing, and local perf-measurement controls.

Persistence is hardware-defined. Configuration fields generally last until display reprogramming, power gating, block reset, suspend/resume restoration, or full ASIC reset. Status, fault, interrupt, ack, counter, timeout, underflow, and update-pending fields may be sticky, read-only, write-one-to-clear, self-clearing, or timing-sensitive. This generated header only provides bit encodings; safe access rules come from the hardware spec and consuming AMD display code.

## Dependencies And Integration Points

This chunk depends on AMD's generated DCN 3.0.3 register database and must stay synchronized with:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_3_offset.h`, which provides the corresponding register offsets.
- AMD display register-helper infrastructure that expands `REG_*`, `SR`, `SRI`, `SRII`, `FD_MASK`, `FD_SHIFT`, `HUBP_MASK_SH_LIST_DCN30`, `HUBBUB_MASK_SH_LIST_DCN30`, `MCIF_WB_COMMON_MASK_SH_LIST_DCN30`, `AUD_COMMON_MASK_SH_LIST_BASE`, and similar macros into offset plus shift/mask operations.
- Adjacent chunks of this same header, because the requested slice starts after the beginning of `DMCUB_INTERRUPT_STATUS` and ends inside `HUBP0_HUBP_MEASURE_WIN_CTRL_DPPCLK`.

Direct DCN 3.0.3 include sites in this tree include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn303.c`, which builds `dmub_srv_dcn303_regs` from DMUB common and DMCUB register/field lists.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn303/dcn303_resource.c`, which builds resource-pool register, shift, and mask tables for HUBBUB, audio, HUBP, DWB/MCIF writeback, DSC, DIO, and related blocks.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn303/irq_service_dcn303.c`, which maps DCN303 interrupt sources to register fields.

Important shared consumers include:

- `display/dmub/src/dmub_reg.h` and DMUB service code for DMCUB mailbox, scratch, interrupt, and fault access.
- `display/dc/mmhubbub/dcn30`/`dcn32` style MMHUBBUB implementations for MCIF writeback buffer programming, warmup, watermarks, pstate latency, memory-power, and clock control.
- `display/dc/hubbub/dcn20`/`dcn30` style HUBBUB implementations for DCHUBBUB arbitration, watermarks, CRC, timeout, clock, and reset programming.
- `display/dc/hubp/dcn20`/`dcn30` style HUBP implementations for surface format, tiling, viewport, VM, request sizing, underflow, and clock state.
- `display/dc/dce/dce_audio.*` and stream-encoder audio paths for Azalia endpoint/root/controller state and audio stream setup.
- `display/dc/dcn20/dcn20_vmid.*` and related VM helper code for VM context page table programming.

## Risks And Edge Cases

- Shift/mask drift is the central risk. These macros are untyped integers, so an incorrect mask or bit position can compile cleanly while programming the wrong hardware bit.
- Chunk boundaries are artificial. The beginning lacks the earlier part of `DMCUB_INTERRUPT_STATUS`, and the end stops before the rest of `HUBP0_HUBP_MEASURE_WIN_CTRL_DPPCLK` and the following HUBPREQ0 block.
- DMCUB mailbox and interrupt fields are synchronization-sensitive. Wrong inbox/outbox pointer masks, ack/status handling, GPINT fields, or timer/fault bits can cause DMUB command hangs, missed firmware interrupts, or unrecoverable display-controller faults.
- MCIF writeback buffer address, high-address, pitch, size, and status fields are DMA-facing. Bad masks can target the wrong memory, corrupt capture output, violate VMID isolation, or leave buffer-manager state inconsistent.
- HDA/Azalia endpoint, stream, DMA, and power fields are index/data-window based. A wrong endpoint or stream field can affect only specific audio instances, making regressions appear as sink-specific or stream-number-specific audio failures.
- DCHUBBUB arbitration and watermark fields are timing-critical. Incorrect urgency, self-refresh, DRAM-clock-change, timeout, or fractional bandwidth masks can show up only under high-resolution, high-refresh, multi-plane, writeback, or memory-clock-transition workloads.
- VM context page-table fields are security- and correctness-sensitive. Incorrect base/start/end/depth/block-size masks can cause display VM faults, wrong physical address translation, or out-of-range memory access.
- Sticky status and write-one-to-clear fields in interrupt, fault, CRC, timeout, underflow, perfmon, and memory-power blocks can be mishandled by generic read-modify-write operations if the consumer does not follow hardware-specific access rules.
- HUBP surface, viewport, tiling, and request-size fields interact with DML calculations and plane state. Small mask errors can cause corruption, cropping, underflow, or only-mode-specific failures.
- Perfmon and FMON fields are debug/telemetry-facing but still mutable hardware state. Bad selection or ack fields can make diagnostics misleading and can hide real performance, clock, or timeout issues.

## Test Signals

Useful validation is a mix of generated-header consistency and hardware behavior:

- Build AMDGPU/DC with DCN303 support enabled; missing or renamed macros should fail in `dmub_dcn303.c`, `dcn303_resource.c`, `irq_service_dcn303.c`, HUBP/HUBBUB/MMHUBBUB/audio table construction, and DMUB register tables.
- Mechanically verify that every field in lines 4720-7368 has coherent `__SHIFT`/`_MASK` pairs, accounting for the intentionally partial start and end of the chunk.
- Diff this range against AMD's authoritative generated DCN 3.0.3 register database and nearby generated headers where fields are expected to match.
- Exercise DMUB firmware command paths: boot, inbox/outbox command submission, GPINT signaling, timer handling, interrupt ack/status behavior, scratch reads/writes, and fault reporting.
- Exercise display writeback: buffer allocation/address programming, luma/chroma pitch and size, buffer fences, buffer flip/status transitions, VMID use, pstate/self-refresh transitions, overflow/backpressure, and captured-frame correctness.
- Exercise HDA/HDMI/DP audio: endpoint enumeration, audio stream enable/disable, sample-rate/DTO behavior, DMA ring operation, suspend/resume, hotplug audio device appearance, and CRC/debug paths if available.
- Exercise HUBBUB/DCHUBBUB under stress: multi-plane and high-refresh modes, memory clock changes, self-refresh entry/exit, watermark changes, warmup paths, CRC capture, timeout interrupt handling, and forced I/O/debug status.
- Exercise VM setup and fault paths: valid page-table programming, invalid/fault injection where supported, default address behavior, context 0-15 table ranges, and fault address/status reporting.
- Exercise HUBP0 plane programming: varied pixel formats, rotation/mirroring/alpha plane paths, linear and tiled surfaces, chroma planes, viewport cropping, underflow detection, clock gating, and performance measurement windows.
- Monitor kernel logs, DC debug traces, perf counters, CRCs, captured frames, display corruption, audio dropouts, DMUB timeouts, VM faults, underflow/timeout interrupts, and suspend/resume failures.

## Cross-Chunk Notes

Earlier chunks own the start of the DMCUB interrupt/status definitions and prior DCN 3.0.3 register field families. Later chunks continue after `HUBP0_HUBP_MEASURE_WIN_CTRL_DPPCLK` into HUBPREQ0 and the remaining HUBP/display pipe register fields. The final per-file research document should merge adjacent chunks before making complete claims about all DMCUB, MCIF writeback, HDA audio, DCHUBBUB, VM, or HUBP coverage in `dcn_3_0_3_sh_mask.h`.

### subset-b-001784: lines 7369-9903

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_3_sh_mask.h lines 7369-9903

## Purpose

This chunk is generated C preprocessor metadata for DCN 3.0.3 display-register bitfields. It contains `_SHIFT` and `_MASK` definitions used by AMDGPU DC display code to pack, unpack, and update MMIO register fields without hard-coding bit positions at call sites. The covered range starts at the tail of `HUBP0_HUBP_MEASURE_WIN_CTRL_DPPCLK` masks, then covers HUBP/HUBPREQ/HUBPRET/CURSOR/perfmon definitions for display pipe 0 and pipe 1, and finally begins the DPP0 top, converter, scaler, and color-management register field map.

There are no functions, structs, or runtime algorithms in this slice. Its behavioral importance is indirect: every macro value becomes part of the hardware programming ABI between the DRM display driver and DCN 3.0.3 display blocks.

## Important APIs, Types, And Register Groups

- `HUBPREQ0_*` and `HUBPREQ1_*` describe hubp request-side surface programming. They include pitch, VMID, primary/secondary luma and chroma surface addresses, primary/secondary metadata addresses, TMZ and DCC surface-control bits, flip controls, flip interrupts, in-use/earliest-in-use address snapshots, request expansion modes, TTU/QoS timing, VM aperture and L1 TLB control, blank/prefetch/vblank/flip/nominal delivery timing, cursor delivery timing, and request memory power control/status.
- `HUBPRET0_*` and `HUBPRET1_*` describe hubp return-side programming. They cover DET buffer base/crossbar controls, DET/DMROB/PIXCDC memory power control and state, pipe read-line windows, vblank/read-line interrupts, read-line values, and read-line status flags.
- `CURSOR0_0_*` and `CURSOR0_1_*` define hardware cursor fetch and metadata fields for pipes 0 and 1. They include enable/mode/magnification/TMZ/snoop/system/pitch settings, cursor address low/high, size, position, hot spot, stereo offsets, destination offset, cursor memory power control/status, DMDATA address/control/QoS/status, and software DMDATA payload registers.
- `DC_PERFMON5_*` and `DC_PERFMON6_*` define per-pipe display performance monitor controls. They expose event selection, counted value selection, increment modes, hardware stop selection, counter state multiplexing for counters 0-7, perfmon state, report count, count-off interrupt control, clock enable, run-enable start/stop selectors, counter interrupt status/ack fields, and high/low readback fields.
- `HUBP1_*` at the pipe-1 hubp block mirrors earlier pipe-0 hubp definitions from outside this chunk for surface config, address/tiling config, primary/secondary viewport geometry, request sizing, hubp control/status, hubp clocks, VMPG config, and DCFCLK/DPPCLK measurement windows.
- `DPP_TOP0_*` starts the DPP0 display pipe processor top block, covering DPP clock/gating, soft resets for CNVC/DSCL/CM/OBUF, CRC readback/control, and host-read throttling.
- `CNVC_CFG0_*` defines the DPP0 converter configuration: surface pixel format, format expansion/conversion/alpha/bypass/crossbar controls, FP bias/scale values, color-key controls and RGBA thresholds, 2-bit alpha LUT, pre-dealpha, pre-CSC mode and coefficient pairs including B-bank coefficients, coefficient format, pre-degamma, and pre-realpha.
- `CNVC_CUR0_*` defines converter-side cursor controls, cursor palette colors, and cursor FP scale/bias.
- `DSCL0_*` defines scaler state: coefficient RAM selection/data, scaler modes, tap counts, 2-tap sharpening, manual replicate factors, horizontal/vertical scale ratios and initial phases for luma/chroma/top/bottom, black color, update pending, autocal, overscan, OTG blanking, recout/MPC sizing, line-buffer format and partitioning, scaler/line-buffer memory power state, and OBUF control/power.
- `CM0_*` begins DPP0 color management: CM bypass/update pending, post-CSC mode and coefficient matrices with B-bank values, gamut remap mode and coefficient matrices with B-bank values, output bias, gamma-correction controls, LUT index/data/control, and RAMA piecewise-linear gamma region setup.

All macros use the naming pattern `<register>__<field>__SHIFT` and `<register>__<field>_MASK`. They are consumed as constants by register helper macros in the AMD display stack, typically alongside register-address headers and generated register-list tables.

## Control Flow

The chunk has no C control flow. The effective control flow appears in callers that:

1. Choose a register for a DCN block instance, such as `HUBPREQ1_DCSURF_FLIP_CONTROL`.
2. Use the matching `_SHIFT` and `_MASK` definitions to construct field values.
3. Issue MMIO read/modify/write operations through AMDGPU/DC register helper macros.
4. Poll or inspect status fields such as flip pending, DMDATA done, memory power state, read-line status, underflow/timeout status, or perfmon interrupt status.

The field families imply several important programming sequences: surface update locks before address/format flips; programming VMID, surface addresses, pitches, metadata, DCC/TMZ, and timing before enabling fetch; clearing flip/read-line/vblank/DMDATA interrupt bits after handling; enabling DPP/CNVC/DSCL/CM clocks and releasing soft reset before DPP programming; and selecting scaler/gamma LUT indices before writing associated data.

## State And Persistence Behavior

The macros themselves are compile-time constants and have no persistence. The hardware registers they describe are persistent device state until changed by driver writes, reset, suspend/resume, display mode changes, or power gating.

Stateful hardware surfaces visible in this range include framebuffer base addresses and VMID selection, DCC/TMZ/security bits, flip pending/occurred/away status, read-line/vblank interrupt state, DMDATA done/underflow/fault/late state, memory power control and status for request buffers, DET/DMROB/PIXCDC/CROB/scaler/LUT/line-buffer/OBUF memories, perfmon counter state/readback values, DPP CRC values, scaler coefficient RAM, line-buffer partitioning, CM post-CSC/gamut/gamma LUT state, and RAMA gamma-region tables.

Several fields are status-or-ack style rather than ordinary configuration. Examples include `*_CLEAR`, `*_STATUS`, `*_INT_STATUS`, `*_ACK`, `*_UPDATE_PENDING`, `*_DONE`, and `*_CURRENT` fields. Callers must preserve the expected write-one-to-clear or read-only semantics from the hardware spec; the masks alone do not encode those access rules.

## Dependencies And Integration Points

This header depends on the wider generated ASIC register set for DCN 3.0.3. It is meaningful only with the corresponding address-definition headers, DC register-list structures, and helper macros that combine shifts/masks with MMIO access. Integration points are the AMDGPU DRM display manager and DCN resource/HUBP/DPP/HUBBUB programming code under the AMD display driver.

The pipe-indexed duplication is intentional. Pipe 0 uses `HUBPREQ0`, `HUBPRET0`, `CURSOR0_0`, and `DC_PERFMON5`; pipe 1 uses `HUBP1`, `HUBPREQ1`, `HUBPRET1`, `CURSOR0_1`, and `DC_PERFMON6`; DPP0 uses `DPP_TOP0`, `CNVC_CFG0`, `CNVC_CUR0`, `DSCL0`, and `CM0`. Higher-level code usually abstracts this duplication through per-instance register lists, but the generated macro names must remain exact for those lists to compile.

The bit widths encode hardware limits that callers must respect: 48-bit-style surface addresses split into 32-bit low and 16-bit high fields, 14-bit viewport/pitch dimensions in many places, 23-bit/27-bit timing and scale-ratio fields, 4-bit VMID/QoS fields, 9-bit cursor/gamma LUT indices, and paired 16-bit matrix coefficients in many color registers.

## Risks And Edge Cases

- Incorrect shift or mask constants can silently corrupt adjacent fields during read/modify/write operations. This is especially risky for packed registers with configuration, status, clear, and interrupt-enable bits in the same 32-bit word.
- The chunk contains security-sensitive memory attributes such as TMZ, system, snoop, and VM/TLB fields. Misprogramming these can expose protected buffers incorrectly or cause display fetch faults.
- Surface address, pitch, metadata, DCC, and flip-control fields are tightly coupled. A valid mask can still be used in an invalid sequence, causing underflow, stale frame display, wrong chroma plane fetch, or hangs around flip pending/in-use state.
- Many memory power controls have matching status fields, but the masks do not enforce sequencing or polling. Powering down DET, request, cursor, scaler, LUT, line-buffer, or OBUF memory while a pipe is active can cause data loss or underflow.
- Pipe 0 and pipe 1 definitions are near-duplicates; copy-generation drift between `HUBPREQ0` and `HUBPREQ1`, `HUBPRET0` and `HUBPRET1`, `CURSOR0_0` and `CURSOR0_1`, or `DC_PERFMON5` and `DC_PERFMON6` would be hard to catch by compile tests alone.
- DPP color/scaler fields use dense fixed-point encodings. Driver-side values must be range-checked before packing, because the masks will truncate oversized coefficients, phase values, scale ratios, LUT indices, and RAMA region counts.
- This chunk ends mid-register at `CM0_CM_GAMCOR_RAMA_REGION_14_15`; only the shift macros for region 14 LUT offset, region 14 segment count, and region 15 LUT offset are visible here. The matching region 15 segment shift and masks continue in the next chunk, so whole-file research must reconcile that boundary before treating the `REGION_14_15` definition as complete.

## Test Signals

- Build coverage: any renamed or malformed macro should break compilation in DCN 3.0.3 register-list or register-helper users.
- Register mask validation: generated-header comparison against the vendor register database can catch drift in shift/mask values, especially for duplicated pipe blocks.
- Runtime display tests: modeset, plane enable/disable, page flip, stereo flip, cursor movement/format changes, DCC/TMZ surfaces, suspend/resume, and multi-pipe configurations exercise the HUBP/HUBPREQ/HUBPRET/CURSOR portions.
- Fault and interrupt tests: induced VM faults, DMDATA underflow, vblank/read-line interrupt handling, flip interrupt/away interrupt handling, and HUBP timeout/underflow paths should observe and clear the status fields defined here.
- Perf/debug tests: DPP CRC readback, perfmon counter start/stop/count-off interrupts, HUBP DCFCLK/DPPCLK measurement windows, and host-read throttling verify the debug/performance monitor masks.
- Color and scaler tests: pre-CSC/post-CSC/gamut matrix programming, pre-degamma/gamma correction LUT programming, RAMA piecewise-linear regions, scaler coefficient RAM writes, luma/chroma scaling, overscan, line-buffer partitioning, and OBUF modes provide coverage for the DPP0/CNVC/DSCL/CM definitions.

### subset-b-001785: lines 9904-12415

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_3_sh_mask.h lines 9904-12415

## Scope

This chunk is a generated AMD DCN 3.0.3 ASIC register bitfield header segment. It contains preprocessor constants only: hardware register fields are represented by a `__SHIFT` macro for the bit offset and a `_MASK` macro for the field mask. The assigned range spans 2,512 source lines, with 2,113 `#define` entries, 1,055 shift definitions, 1,066 mask definitions, and 385 register/comment anchors.

The range starts in the middle of `CM0_CM_GAMCOR_RAMA_REGION_14_15` and ends on the `CM1_CM_GAMCOR_RAMB_REGION_32_33` comment before that register's fields. The merge lane must stitch adjacent chunks before treating either boundary group as complete.

## Purpose

The purpose of this header segment is to expose symbolic bit positions for DCN 3.0.3 display pipeline programming in the AMDGPU display driver. It is included with the matching DCN 3.0.3 offset header so register helper macros can construct MMIO read-modify-write operations without embedding raw bit constants in driver logic.

The covered register surface is concentrated on DPP pipe 0 color management, DPP0 performance monitoring, and the beginning of DPP pipe 1:

- tail of `CM0` gamma-correction RAM-A region programming.
- `CM0` gamma-correction RAM-B, blend-gamma RAM-A/RAM-B, shaper RAM-A/RAM-B, CM memory power, dealpha, coefficient format, 3D LUT, and debug fields.
- `DC_PERFMON7` DPP0 performance counter control, state, interrupt, and value readback fields.
- `DPP_TOP1`, `CNVC_CFG1`, `CNVC_CUR1`, `DSCL1`, and a large prefix of `CM1` display-pipe fields for DPP1.

This source is data-like rather than executable. Runtime behavior is indirect: the constants must match AMD's hardware register specification and the companion `dcn_3_0_3_offset.h` address definitions.

## Address Blocks And Register Surface

Visible address blocks and implied surfaces:

- The opening lines continue the `dce_dc_dpp0_dispdec_cm_dispdec` color-management block from the previous chunk. This range covers `CM0_CM_GAMCOR_*`, `CM0_CM_BLNDGAM_*`, `CM0_CM_HDR_MULT_COEF`, `CM0_CM_MEM_PWR_*`, `CM0_CM_DEALPHA`, `CM0_CM_COEF_FORMAT`, `CM0_CM_SHAPER_*`, `CM0_CM_3DLUT_*`, and CM test-debug fields.
- `dce_dc_dpp0_dispdec_dpp_dcperfmon_dc_perfmon_dispdec`: `DC_PERFMON7` performance counter selection, state, perfmon control, interrupt/status, and counter value low/high registers for DPP0.
- `dce_dc_dpp1_dispdec_dpp_top_dispdec`: `DPP_TOP1` clock, gating, reset, CRC, and host-read control fields.
- `dce_dc_dpp1_dispdec_cnvc_cfg_dispdec`: `CNVC_CFG1` source pixel format, format conversion, floating-point scale/bias, color keying, alpha, pre-dealpha, pre-CSC, coefficient format, pre-degamma, and pre-realpha fields.
- `dce_dc_dpp1_dispdec_cnvc_cur_dispdec`: `CNVC_CUR1` cursor enable/mode/color/floating-point scale-bias fields.
- `dce_dc_dpp1_dispdec_dscl_dispdec`: `DSCL1` scaler coefficient RAM, scaler mode/taps/ratios/inits, black color, update/autocal, overscan, blanking, recout/MPC dimensions, line-buffer memory, DSCL memory power, OBUF control, and OBUF memory power fields.
- `dce_dc_dpp1_dispdec_cm_dispdec`: starts `CM1` color-management controls and proceeds through post-CSC, gamut remap, bias, gamma-correction controls, gamma RAM-A/RAM-B region programming, and the start of the next blend-gamma section outside this chunk.

## Important Macros And Register Families

`CM0_CM_GAMCOR_RAMA_*` and `CM0_CM_GAMCOR_RAMB_*` define DPP0 gamma-correction piecewise-linear RAM programming. The range starts with the tail of RAM-A `REGION_14_15`, then continues RAM-A region descriptors through `REGION_32_33`. RAM-B includes per-channel start controls, start slope/base controls, end controls, offsets, and paired region descriptors from `REGION_0_1` through `REGION_32_33`. The repeated region registers pack two PWL regions per 32-bit register: LUT offsets use masks such as `0x000001FFL` and `0x01FF0000L`; segment counts use `0x00007000L` and `0x70000000L`.

`CM0_CM_BLNDGAM_*` mirrors the gamma-correction shape for blend gamma. It includes mode/select/current-state bits, LUT index/data/control, RAM-A and RAM-B start/end/offset/region descriptors, and the same two-regions-per-register encoding used by gamma correction. `CM_BLNDGAM_PWL_DISABLE`, color write masks, read color selection, host selection, and config mode are the key control fields.

`CM0_CM_SHAPER_*` defines DPP0 shaper LUT control and region programming. The shaper block includes offset/scale fields for R/G/B, indexed LUT access, a write-enable mask register, RAM-A/RAM-B start and end controls, and paired RAM region descriptors. Unlike the gamma/blend RAM-B end controls, shaper RAM-B end controls pack end and end-base fields rather than the end-slope split used by the other PWL blocks.

`CM0_CM_MEM_PWR_CTRL`, `CM0_CM_MEM_PWR_STATUS`, `CM0_CM_MEM_PWR_CTRL2`, and `CM0_CM_MEM_PWR_STATUS2` expose memory power control and state for gamma/blend, shaper, and HDR 3D LUT memories. These fields are force/disable/state bits, not standalone policy.

`CM0_CM_3DLUT_*` exposes DPP0 3D LUT programming: mode, size, current mode, index, 16-bit paired data, 30-bit data access, RAM selection, write-enable mask, read selection, output normalization, and RGB output offset/scale. `CM0_CM_TEST_DEBUG_INDEX` and `CM0_CM_TEST_DEBUG_DATA` provide indexed debug access.

`DC_PERFMON7_*` defines DPP0 performance-monitor controls. `PERFCOUNTER_CNTL` selects event, counted value, increment mode, hardware control source, run-enable mode, restart, interrupt, off-mask behavior, active state, and counter selector. `PERFCOUNTER_CNTL2` selects counted value type, hardware stop inputs, counter-off source, and counter-control selector. `PERFCOUNTER_STATE`, `PERFMON_CNTL`, `PERFMON_CNTL2`, `PERFMON_CVALUE_INT_MISC`, `PERFMON_CVALUE_LOW`, `PERFMON_HI`, and `PERFMON_LOW` cover per-counter state, report count, counter-off interrupt status/ack, clock enable, run start/stop source selection, and value readback.

`DPP_TOP1_*` defines top-level DPP1 controls: DPP clock enable, static/dynamic clock-gate disables, DSCL gate disable, DISPCLK/DPPCLK gating, test clock selection, soft-reset bits for CNVC/DSCL/CM/OBUF, CRC value registers, CRC enable/one-shot/status/source/pixel-format/cursor-format/mask fields, and host-read rate control.

`CNVC_CFG1_*` defines the DPP1 converter configuration path before scaling and color management. It covers surface pixel format, alpha-plane enable, expansion mode, 16-bit conversion, CNVC bypass/MSB alignment, positive clamps, update-pending status, RGB crossbar selection, floating-point bias/scale, color-keyer enable/alpha and RGB low/high thresholds, four-entry 2-bit alpha LUT, pre-dealpha, pre-CSC mode/current mode, primary and alternate pre-CSC matrices, coefficient format, pre-degamma mode/select, and pre-realpha.

`CNVC_CUR1_*` is the DPP1 cursor subset: cursor0 enable, expansion mode, pixel inversion, ROM enable, cursor mode, pixel-alpha modulation, update-pending status, two 24-bit cursor colors, and floating-point scale/bias.

`DSCL1_*` defines DPP1 scaler and line-buffer programming. Coefficient RAM fields select tap pair, phase, filter type, and even/odd tap data with enable bits. The scaler mode/tap/ratio/init fields configure luma/chroma scale ratios and initial phases, coefficient RAM bank/current/readback selection, chroma/alpha coefficient modes, two-tap sharp/hardcoded behavior, manual replicate factors, black color, update state, autocal pipe selection, overscan, OTG blanking, recout/MPC dimensions, line-buffer interleave/alpha, line-buffer partition counts, vertical counters, DSCL memory power, OBUF behavior, and OBUF memory power.

`CM1_CM_*` begins the DPP1 color-management block. This range includes global bypass/update-pending, post-CSC mode/current state and A/B 3x4 matrix fields, gamut-remap mode/current state and A/B 3x4 matrices, bias fields, gamma-correction mode/LUT/control, and most gamma RAM-A/RAM-B PWL region programming. The chunk ends before `CM1_CM_GAMCOR_RAMB_REGION_32_33` fields are listed, so the following chunk is needed for the complete RAM-B region table and subsequent blend/shaper/3D LUT CM1 fields.

## Control Flow And Runtime Behavior

There is no C control flow in this chunk. Runtime control flow is represented by hardware programming sequences that consume these bit masks through AMDGPU register helper macros.

The likely hardware flows represented here are:

- DPP0 color-management programming: driver code loads gamma correction, blend gamma, shaper, and 3D LUT state by programming mode/select fields, indexed LUT data registers, PWL region descriptors, and output normalization/offset registers.
- DPP0 performance monitoring: diagnostic or profiling code selects events and counter modes through `DC_PERFMON7_*`, enables clock/run conditions, handles counter-off/per-counter interrupts, and reads high/low counter values.
- DPP1 pipe bring-up and reset: `DPP_TOP1_DPP_CONTROL` and `DPP_TOP1_DPP_SOFT_RESET` enable the DPP clock, manage gating, and reset CNVC, DSCL, CM, and OBUF subblocks.
- DPP1 conversion and cursor setup: `CNVC_CFG1_*` and `CNVC_CUR1_*` select surface format, alpha/keying behavior, pre-CSC/pre-degamma transforms, cursor mode, and cursor colors.
- DPP1 scaling and viewport setup: `DSCL1_*` programs coefficient RAM, scale ratios, filter inits, taps, output sizes, overscan, line-buffer partitions, memory power, and output-buffer state.
- DPP1 color-management setup: `CM1_CM_*` fields in this chunk establish post-CSC, gamut remap, bias, gamma-correction control, and a partial gamma PWL RAM table.

## State And Persistence

The macros themselves hold no mutable state and allocate no storage. They describe fields in hardware MMIO registers. Writes through these fields persist in the display hardware until another write, block reset, GPU reset, suspend/resume restore, or mode-set reprogramming occurs.

Important state classes represented by this chunk:

- Double-buffer/current-state fields: `*_UPDATE_PENDING`, `*_MODE_CURRENT`, `*_SELECT_CURRENT`, `SCL_COEF_RAM_SELECT_CURRENT`, and `SCL_COEF_RAM_SELECT_RD` expose the difference between requested and currently latched hardware state.
- Indexed RAM state: `CM*_GAMCOR_LUT_INDEX`, `CM*_GAMCOR_LUT_DATA`, `CM*_BLNDGAM_LUT_INDEX`, `CM*_BLNDGAM_LUT_DATA`, `CM0_CM_SHAPER_LUT_*`, `CM0_CM_3DLUT_*`, and `DSCL1_SCL_COEF_RAM_*` are address/data style interfaces. The selected index, RAM bank, host/config mode, color write mask, and read selector are stateful context for subsequent accesses.
- Piecewise-linear curve descriptors: gamma, blend-gamma, and shaper RAM-A/RAM-B region registers persist LUT offsets and segment counts. These descriptors must match the indexed LUT data layout loaded elsewhere.
- Matrix and bias state: CNVC pre-CSC, CM post-CSC, CM gamut-remap, and bias fields persist color transform state and can affect every pixel through the pipe.
- Power state: CM, DSCL, line-buffer, and OBUF memory power fields can force, disable, or report subblock memory state. These interact with active scanout and power management rather than behaving as ordinary display parameters.
- Interrupt and diagnostic state: perfmon interrupt status/ack fields, CRC status/value fields, line-buffer counters, and CM debug registers expose hardware state that may be latched or write-one-to-clear depending on the underlying register semantics. The header does not encode those semantics.

## Dependencies And Integration Points

This chunk depends on companion generated DCN 3.0.3 headers for register addresses and base indices, especially `dcn_3_0_3_offset.h`. Consumers combine register names and field names through macros such as `FD_MASK`, `FD_SHIFT`, `REG_OFFSET`, `SF`, and `TF_SF` to populate per-block register tables and issue MMIO operations.

Concrete include points for `dcn_3_0_3_sh_mask.h` include:

- `drivers/gpu/drm/amd/display/dc/resource/dcn303/dcn303_resource.c`, where the DCN 3.0.3 resource layer includes the offset and mask headers while constructing display resources.
- `drivers/gpu/drm/amd/display/dmub/src/dmub_dcn303.c`, where DMUB register tables use `FD_MASK` and `FD_SHIFT` arrays derived from this header.
- `drivers/gpu/drm/amd/display/dc/irq/dcn303/irq_service_dcn303.c`, where interrupt service code includes the same register definitions.

Functional integration points include:

- DPP resource construction and DPP helper tables that bind generic DPP0/DPP1 field names to instance-specific register offsets and masks.
- Color-management code that programs transfer functions, gamma/blend-gamma PWL curves, shaper curves, post-CSC/gamut matrices, bias, HDR multiplier, and 3D LUT contents.
- Scaler code that programs DSCL coefficient RAM, taps, ratios, initial phases, recout/MPC dimensions, line-buffer partitioning, OBUF behavior, and overscan.
- Cursor and conversion paths that program CNVC format, alpha/keying, pre-dealpha/pre-realpha, pre-CSC, pre-degamma, and cursor registers.
- Diagnostics and profiling paths that use DPP CRC, DC perfmon, DSCL counters, and CM test-debug interfaces.
- Power-management and suspend/resume paths that restore DPP subblock memory power state and indexed LUT contents.

Because this is a generated public include within the AMDGPU display tree, compile-time consumers are sensitive to exact macro spelling. A missing or renamed macro can break builds, and an incorrect mask or shift can silently program the wrong hardware bits.

## Risks And Edge Cases

- Generated-header drift is the primary risk. A wrong shift or mask can corrupt neighboring fields in a 32-bit MMIO register, causing display blanking, bad color transforms, scaling artifacts, cursor defects, incorrect perfmon data, or power-management regressions.
- The range starts and ends mid-register-family. `CM0_CM_GAMCOR_RAMA_REGION_14_15` starts before line 9904, and `CM1_CM_GAMCOR_RAMB_REGION_32_33` fields are outside the range. File-level conclusions must merge adjacent chunks.
- Repeated PWL RAM region tables are easy to misgenerate. Gamma, blend-gamma, and shaper RAM A/B blocks use many near-identical `REGION_N_N+1` macros, so an off-by-two region, channel swap, RAM A/B swap, or missing final region would be hard to detect by inspection.
- Several field names include the word `MASK`, producing generated names such as `CM0_CM_SHAPER_LUT_WRITE_EN_MASK__CM_SHAPER_LUT_WRITE_EN_MASK_MASK` and `PERFCOUNTER_OFF_MASK_MASK`. Parsers that split naively on `_MASK` can misclassify these fields.
- Indexed RAM programming is order-sensitive. Losing the intended index, RAM select, 30-bit mode, read selector, color write mask, or host/config mode can corrupt LUT contents even if each bitfield constant is individually correct.
- Status, current-mode, update-pending, interrupt-status, and ack fields have hardware-specific semantics not represented by the macros. Callers must rely on the block programming sequence and hardware documentation, not just the mask constants.
- Memory-power fields can interact with active scanout. Forcing or disabling CM, DSCL, line-buffer, OBUF, shaper, gamma/blend, or HDR3DLUT memories at the wrong time can produce visual corruption, stale LUT data, underflow, or hangs.
- The constants are DCN 3.0.3-specific. Reusing them for nearby DCN revisions because names appear similar risks subtle register layout mismatches.

## Test Signals

Useful validation signals for this chunk are mostly compile-time, generated-header consistency, and hardware/display regression signals:

- AMDGPU DCN 3.0.3 compile coverage catches missing or renamed macros used by resource tables, DMUB register tables, IRQ code, DPP/DSCL/CM helpers, and perfmon helpers.
- Generated-header checks should verify that every complete field has both `__SHIFT` and `_MASK`, masks fit within 32 bits, repeated RAM-region families retain expected offsets and segment-count positions, and chunk boundaries are reconciled by adjacent chunks.
- Display mode-set tests should exercise DPP1 clock/reset, CNVC pixel formats, alpha/keying, cursor modes, DSCL scaling ratios/taps/coefficient RAM, recout/MPC sizing, line-buffer partitioning, and OBUF behavior.
- Color-management tests should cover DPP0 and DPP1 gamma correction, DPP0 blend gamma, DPP0 shaper LUTs, DPP0 3D LUT mode/data paths, post-CSC, gamut remap, bias, bypass/current-mode readbacks, and update-pending handshakes.
- Power tests should cover suspend/resume and runtime power transitions for CM gamma/blend/shaper/HDR3DLUT memories, DSCL LUT/LB banks, and OBUF memory.
- Diagnostic tests should compare DPP CRC output, `DC_PERFMON7` counter programming/readback, perfmon interrupt acknowledgement, DSCL vertical counters, and CM debug-index/data behavior against expected hardware results.

## Open Questions For Merge Lane

- Confirm the previous chunk contains the beginning of `CM0_CM_GAMCOR_RAMA_REGION_14_15` and the earlier `CM0` gamma-control fields needed to describe the complete gamma-correction block.
- Confirm the next chunk contains `CM1_CM_GAMCOR_RAMB_REGION_32_33` fields and the remainder of the `CM1` blend-gamma, shaper, memory-power, 3D LUT, and debug surface.
- Identify the exact DCN 3.0.3 DPP/DSCL/CM register table macros that consume the `CM0`, `DPP_TOP1`, `CNVC_CFG1`, `CNVC_CUR1`, `DSCL1`, `CM1`, and `DC_PERFMON7` fields before the final per-file report names call sites.

### subset-b-001786: lines 12416-14925

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_3_sh_mask.h lines 12416-14925

## Scope And Purpose

This chunk is a generated AMD DCN 3.0.3 shift/mask register header slice. It does not contain executable functions or C types; instead it defines preprocessor constants that describe bit positions (`__SHIFT`) and bit masks (`_MASK`) for memory-mapped display registers. The matching register addresses live in `dcn_3_0_3_offset.h`; this file supplies the field layout used by the AMD display core helpers to compose, update, read, and acknowledge hardware registers safely.

The slice starts at the end of the `CM1_CM_GAMCOR_RAMB_REGION_32_33` region table, covers most of the DPP1 color-management register fields, crosses several OPP/OPTC address blocks, and ends partway through `OTG0_OTG_GLOBAL_SYNC_STATUS`. In this range there are 2,125 `#define` entries and 349 register/comment markers. The register groups covered here are:

- `CM1_*` color-management fields for blend gamma, shaper, 3D LUT, HDR multiplier, memory power control/status, coefficient format, dealpha, and debug index/data.
- `DC_PERFMON8_*` and `DC_PERFMON9_*` display performance monitor counters and control/status fields.
- `FMT0_*` and `FMT1_*` output formatter fields for clamp, dynamic expansion, bit depth, spatial/temporal dithering, stereo, 4:2:0 memory mapping, and 4:2:2 output.
- `DPG0_*` and `DPG1_*` display pattern generator controls, dimensions, colors, offset, and status.
- `OPPBUF0_*`, `OPPBUF1_*`, `OPP_PIPE0_*`, `OPP_PIPE1_*`, `OPP_PIPE_CRC0_*`, `OPP_PIPE_CRC1_*`, `OPP_TOP_*`, `OPP_ABM_CONTROL`, and `DSCRM0/1_*` output-pixel-processor buffer, pipe, CRC, top clock, ABM, and DSC forwarding fields.
- `ODM0_*` and `ODM1_*` OPTC input fields for underflow, data source, format, bytes per pixel, width, clock, memory config, and spare registers.
- `OTG0_*` timing generator fields for horizontal/vertical timing, triggers, force-count, flow, stereo/3D, status snapshots, interrupts, update locking, blank color, vertical interrupts, CRC, static screen, GSL vsync gap, clock/reset, and vstartup/vupdate/vready/global-sync status.

## Important APIs, Types, And Macros

The public surface of this chunk is macro names. Each field appears as a pair such as `OTG0_OTG_H_TOTAL__OTG_H_TOTAL__SHIFT` and `OTG0_OTG_H_TOTAL__OTG_H_TOTAL_MASK`, or as similarly structured register/field pairs for CM, OPP, ODM, FMT, DPG, and perfmon blocks. AMD display code uses token-pasting helper macros to turn these constants into typed register tables:

- `FD_MASK(reg, field)` and `FD_SHIFT(reg, field)` in DMUB code expand against these definitions when constructing common DMUB register field tables for DCN303.
- `SF(reg, field, mask_sh)` and `OPP_SF(reg, field, mask_sh)` expand to either the shift or mask constant and populate per-block shift/mask structs.
- `REG_SET`, `REG_SET_N`, `REG_UPDATE`, `REG_UPDATE_N`, `REG_GET`, and `REG_READ` call sites in the display core depend on these shift/mask values when writing packed register fields.
- IRQ construction macros in `irq_service_dcn303.c`, especially `IRQ_REG_ENTRY`, paste block, instance, register, and field names to select enable, clear, and status bits.

There are no C structs declared in the header chunk, but it is consumed into structs elsewhere. In `dcn303_resource.c`, the DCN303 resource pool builds `dcn3_dpp_shift/mask`, `dcn20_opp_shift/mask`, `dcn_optc_shift/mask`, `dcn30_mpc_shift/mask`, and `dce_hwseq_shift/mask` instances from macros that ultimately resolve into this header. The same resource construction creates DPP, OPP, timing-generator, MPC, DSC, hubp, and hardware-sequencer objects with these field layouts.

## Register Areas Covered

The `CM1` section defines DPP1 color-management field layouts. The blend gamma (`CM_BLNDGAM`) block includes mode/select/current status, LUT index/data/control, RAM A/B PWL start/end/slope/base/offset values per RGB channel, and 34 region definitions for each RAM. Region registers pack two regions per 32-bit register, using low bits for one region's LUT offset and segment count and high bits for the next region. The shaper block has similar RAM A/B region tables plus per-channel offsets/scales and LUT write masks. The 3D LUT block defines mode, index, data, 30-bit data, read/write control, output normalization, and RGB output offsets. Memory power fields (`CM_MEM_PWR_CTRL`, `CM_MEM_PWR_STATUS`, `CM_MEM_PWR_CTRL2`, `CM_MEM_PWR_STATUS2`) expose force, disable, light/deep sleep, shutdown, and status bits for the color-management RAMs.

The `DC_PERFMON8` and `DC_PERFMON9` sections define event select, counted-value selection, increment/run control, active/status, counter selection, perfmon enable/reset/start mode, counter state, and high/low counter value fields. These are instrumentation surfaces rather than normal display programming paths, but a bad field definition can still break diagnostics or performance counter collection.

The `FMT0` and `FMT1` blocks describe output formatter state for two output pixel processors. They include per-component clamp min/max, dynamic expansion enable/mode, pixel encoding, subsampling mode/order, bit-depth truncation and dithering controls, random seeds, clamp format, side-by-side stereo, 4:2:0 memory power force, and 4:2:2 output control. `dcn10_opp.h` maps a subset of these fields into OPP masks/shifts used by OPP construction and programming.

The `DPG0` and `DPG1` blocks define display pattern generator enable/source, ramp parameters, dimensions, RGB/YCbCr color values, segment offsets, and status. `OPPBUF0/1` and `OPP_PIPE0/1` cover OPP buffer active width, pixel repetition, segmentation, overlap/padding, 3D active-space parameters, buffer control, and pipe clock enable. `OPP_PIPE_CRC0/1` define CRC enable/source/stereo controls, masks, and CRC result registers. These blocks are useful for output validation, diagnostics, and self-test style paths.

The `ODM0` and `ODM1` sections describe OPTC input and underflow state. The global-control register includes soft reset, underflow interrupt enable/type/status/clear/current, and double-buffer pending. Other registers define data source selection, data format, bytes per pixel, input width, input clock gate/on/enable, memory config, and spare data. These constants feed timing-generator and OPTC code when display data is split or merged across OPP/OTG paths.

The `OTG0` section is the largest in this chunk. It defines the timing generator's core timing fields (`OTG_H_TOTAL`, blank start/end, sync start/end/polarity, vtotal min/mid/max/control, vertical blank/sync), trigger A/B configuration, manual trigger bits, force-count status, flow control, stereo/3D control and status, pixel-data readback, scanout/frame counters, status-position fields, update locks, double-buffer control, blank color, vertical interrupt positions and clear/enable/status bits, CRC control/window/data/signature masks, static-screen detection/control, GSL vsync-gap status, clock gate/reset/busy bits, and the start of global-sync interrupt/status fields.

## Control Flow And Runtime Use

This file has no runtime control flow by itself. Its control-flow impact is indirect and compile-time: register helper macros embed these constants into code that performs runtime MMIO reads and writes.

For resource construction, `dcn303_resource.c` includes `dcn_3_0_3_sh_mask.h` and constructs block-specific shift/mask tables. `dcn303_dpp_create()` passes the DPP table into `dpp3_construct`; `dcn303_opp_create()` passes the OPP table into `dcn20_opp_construct`; `dcn303_timing_generator_create()` passes the OPTC/OTG table into `dcn30_timing_generator_init`; `dcn303_mpc_create()` passes the MPC shift/mask table into `dcn30_mpc_construct`; and `dcn303_hwseq_create()` stores HWSEQ shift/mask pointers. Once constructed, higher-level display operations call `REG_*` helpers through these objects, and the helpers use the shifts/masks from this header to place field values in the correct bits.

For interrupts, `irq_service_dcn303.c` includes the same header and creates `irq_source_info_dcn303`. The vblank and vupdate paths use `OTG_GLOBAL_SYNC_STATUS` fields such as `VSTARTUP_INT_EN`, `VSTARTUP_EVENT_CLEAR`, `VUPDATE_NO_LOCK_INT_EN`, and `VUPDATE_NO_LOCK_EVENT_CLEAR`; vline setup uses `OTG_VERTICAL_INTERRUPT0_CONTROL` fields such as interrupt enable and clear. If a mask in this chunk is wrong, an IRQ source may fail to enable, fail to acknowledge, or acknowledge a neighboring bit.

For CRC and diagnostics, OPTC code such as `optc2_configure_crc()` writes `OTG_CRC_CNTL2` fields for DSC and stream-combine modes, while later OPTC state dump paths read many `OTG_CRC*`, static-screen, global-sync, and status registers. The data path is therefore: display code selects a semantic field, helper macros combine the field's value with this header's mask/shift, then the register access layer writes or reads the packed MMIO word.

## State And Persistence Behavior

The header itself persists no state. The state described by this chunk lives in hardware registers and internal display RAMs:

- Color LUT, shaper, blend gamma, and 3D LUT fields configure persistent DPP color pipeline state until reprogrammed, reset, power-gated, or lost across suspend/resume.
- Memory power-control fields affect whether color-management RAMs are forced on, shut down, or placed into light/deep sleep; incorrect values can corrupt later LUT programming or waste power.
- OPP/FMT/DPG/CRC/ODM/OTG registers hold live display-pipe configuration. Many of these fields are double-buffered or have pending/current status bits so writes may not take effect until a timing boundary.
- Interrupt status and clear fields are edge-sensitive hardware state. Clear bits such as `*_EVENT_CLEAR`, `OTG_VERTICAL_INTERRUPT*_CLEAR`, and CRC pending/status bits should be treated as write-one-to-clear or hardware-defined side-effect fields according to the register spec.
- Counter, CRC, static-screen, snapshot, frame-count, and performance-monitor fields expose observed hardware state and can change asynchronously with scanout.

The persistence boundary is the GPU display hardware, not software storage. Kernel modeset, atomic commits, power management, DMUB firmware interaction, IRQ handlers, and debug/state-dump paths all rely on the field definitions remaining aligned with the ASIC specification.

## Dependencies And Integration Points

This chunk depends on the generated DCN303 offset header for register addresses and on Sienna Cichlid base-index definitions for segment selection. It is directly included by DCN303 DMUB setup, the DCN303 IRQ service, and `dcn303_resource.c`. Through resource construction it integrates with:

- DPP color pipeline code (`dpp3_construct`, DPP register-list macros, color-management and transfer-function programming).
- OPP/output formatting code (`dcn20_opp_construct`, formatter/dither/clamp/OPP buffer and OPP pipe controls).
- OPTC/timing-generator code (`dcn30_timing_generator_init`, vertical interrupts, timing programming, CRC, static screen, GSL, stereo/3D, and global sync).
- IRQ service code that maps DC IRQ source abstractions to register enable/ack/status bits.
- DMUB service register tables built from `DMUB_COMMON_FIELDS`.
- Debug and diagnostics paths that read CRC, static-screen, perfmon, status-position, frame-count, snapshot, and global-sync registers.

The field naming also matches generic macro tables shared across DCN generations. For example, OPP and OPTC helper headers use `FMT0_*`, `OPPBUF0_*`, `OTG0_*`, and `ODM0_*` field names as canonical instance-zero templates and then apply instance-specific register addresses separately. This makes spelling and bit layout compatibility important across the resource-construction layer.

## Risks And Edge Cases

The primary risk is silent hardware misprogramming. A bad shift or mask still compiles, but writes the wrong bits. For timing and interrupt fields this can produce blank displays, missed vblank/vline/vupdate IRQs, stuck update locks, incorrect vertical-total behavior, or scanout instability. For color-management fields it can produce wrong gamma, shaper, 3D LUT, HDR multiplier, or coefficient behavior, including subtle color corruption that is hard to trace back to a generated constant.

Packed region registers are especially error-prone. Blend-gamma and shaper region definitions store two region offsets/segment counts per word with repeated bit positions (`0x0`, `0xc`, `0x10`, `0x1c`) and masks (`0x000001FF`, `0x00007000`, `0x01FF0000`, `0x70000000`). Any off-by-one region name, copied mask, or skipped region can misalign a PWL LUT segment table while leaving neighboring regions apparently valid.

Status/control registers mix writable control bits with read-only/current/pending/status bits in the same word, such as `CM_BLNDGAM_CONTROL`, `ODM*_OPTC_INPUT_GLOBAL_CONTROL`, `OTG_STATUS`, `OTG_DOUBLE_BUFFER_CONTROL`, `OTG_CLOCK_CONTROL`, and `OTG_GLOBAL_SYNC_STATUS`. Read-modify-write helpers must use masks precisely so they do not clear or set unrelated status/clear bits.

Interrupt and clear fields have side effects. Misusing `OTG_GLOBAL_SYNC_STATUS` or `OTG_VERTICAL_INTERRUPT*_CONTROL` masks can cause event storms, lost acknowledgements, or stale interrupt status. CRC control also includes one-shot pending bits and multiple data-window/result fields, so register dump and CRC-configuration code must treat control, window, and result registers differently.

Generated header drift is another risk. This file is part of a DCN303-specific hardware ABI; manually editing constants or merging values from nearby DCN versions can compile because names are similar, but the hardware layout may differ. The safest maintenance path is regeneration from the authoritative ASIC register database plus comparison against adjacent generation headers and live hardware behavior.

## Test Signals

There are no unit tests for this header chunk alone. Useful validation signals come from build coverage, hardware bring-up, display functional tests, and diagnostics:

- Compile coverage for DCN303 display code should catch missing or misspelled macro names in `dcn303_resource.c`, `irq_service_dcn303.c`, DMUB setup, and shared OPP/OPTC/DPP macro tables.
- Kernel modeset and atomic-commit tests on DCN303 hardware should verify that DPP, OPP, ODM, and OTG objects construct successfully and can light displays across common resolutions, pixel encodings, refresh rates, stereo/3D disabled/enabled paths, and dynamic refresh behavior.
- IRQ tests or runtime traces should confirm vblank, vertical line, vupdate-no-lock, pflip, and HPD-related IRQ paths enable and acknowledge correctly. The strongest signals for this chunk are vblank/vline events using `OTG_GLOBAL_SYNC_STATUS` and `OTG_VERTICAL_INTERRUPT0_CONTROL`.
- Color pipeline tests should exercise blend gamma, shaper, 3D LUT, HDR multiplier, and LUT RAM A/B programming, then compare CRC or measured output for expected color transforms.
- CRC/debug paths should configure OTG and OPP CRC, read CRC result registers, validate CRC windows, and inspect static-screen/status/snapshot/perfmon dumps without unstable or impossible values.
- Power-management and suspend/resume testing should check CM memory power control/status, OTG clock control, double-buffer pending state, update locks, and reset behavior after display off/on cycles.

Because this is a hardware register-layout header, the most valuable regression signal is not a pure software assertion; it is successful DCN303 display operation with interrupts, color programming, CRC/debug reads, and power transitions all exercising the generated masks and shifts together.

### subset-b-001787: lines 14926-17341

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_3_sh_mask.h lines 14926-17341

## Scope

This chunk is a generated DCN 3.0.3 register-field mask slice from `dcn_3_0_3_sh_mask.h`. It contains preprocessor constants only: `_SHIFT` values for field bit positions, `_MASK` values for unshifted 32-bit register masks, and comment markers that name registers and hardware address blocks. There are no C functions, structs, enums, local variables, loops, branches, or runtime data structures in this range.

The slice starts in the tail of the `OTG0` timing-generator definitions, covers the full `dce_dc_optc_otg1_dispdec` `OTG1` register-field surface, then moves through OPTC miscellaneous and perfmon registers, DIO I2C/DDC, DIO scratch/power/clock/reset/generic-interrupt registers, HPD0/HPD1 hotplug detect registers, DIO perfmon registers, all of DP AUX0, and the beginning of DP AUX1 through its interrupt-control fields.

## Purpose And Hardware Surface

The purpose of this header range is to provide the bit layout ABI between AMDGPU Display Core code and DCN 3.0.3 display hardware. Companion offset headers provide register addresses; this mask header provides field positions and masks used by register helper macros to encode values, decode MMIO readbacks, and perform read/modify/write updates without hard-coding numeric bit positions in functional code.

Major hardware areas represented here:

- `OTG0` tail fields for global sync status, master update lock, global swap lock, vupdate keepout, global/manual flow control, dynamic refresh rate timing interrupts, DTO constants, DSC start position, pipe-update status, and spare state.
- `OTG1` timing generator fields for horizontal/vertical totals, blanking, sync, trigger A/B, force-count-now, flow control, stereo/interlace, status/counters, snapshots, interrupts, update locks, blank color, vertical interrupts, CRC windows/data, static screen detection, 3D structure, GSL vsync gap, clocks, vstartup/vupdate/vready, master/global update locks, DRR, DSC start position, pipe-update status, and spare state.
- OPTC miscellaneous muxing and power fields: display writeback source selection, GSL ready/timing source selection, OPTC clock control, ODM memory power controls/status, and OPTC spare register.
- `DC_PERFMON10` for OPTC perfmon counters and `DC_PERFMON11` for DIO perfmon counters, including event selection, counter state, run/stop control, counter-value interrupt status/ack, and low/high readback.
- DIO I2C/DDC registers for software I2C control/arbitration, interrupt control, software status, DDC1/DDC2 hardware status, DDC speed/setup, four transaction descriptors, indexed data, EDID detect control, and DDC read-request interrupts.
- DIO common registers for scratch words, light-sleep memory power state/control for I2C and DIG/DP links, DIO clock gating, power-management clock gating, DIG soft reset, additional clock controls, HDMI RX status timer control, and generic interrupt message/clear.
- HPD0 and HPD1 hotplug-detect fields for interrupt status/control, connection/RX interrupt timers, fast-train sequencing, and toggle filter delays.
- DP AUX0 register fields for AUX enable/reset, software AUX transactions, arbitration between software and DMCU users, interrupt status/ack/mask bits, software/link-service status, indexed SW/LS data windows, DPHY TX/RX controls/status, GTC sync control/error/status, and PHY wake request/acknowledge.
- DP AUX1 starts at the end of the chunk and includes AUX control, software-control, arbitration, and interrupt-control fields.

## Important Definitions

The exported interface is the generated macro naming convention:

- `<REGISTER>__<FIELD>__SHIFT` gives the field's low bit.
- `<REGISTER>__<FIELD>_MASK` gives the field's raw bitmask within the 32-bit register.
- `// addressBlock: ...` comments identify the hardware register aperture for following definitions.
- `//<REGISTER>` comments group field definitions by register.

Important field families in this chunk:

- Timing-generator fields use 15-bit-ish horizontal/vertical coordinate masks for totals, blanking, sync points, window start/end coordinates, snapshot positions, CRC windows, and DSC start positions. These are used when the display pipe programs scanout timing and validates live position/status.
- OTG update and lock fields include per-OTG update locks, master update locks, global update lock enables, vupdate keepout ranges, double-buffer pending bits, update-instantly controls, and GSL-controlled master update locking. These coordinate atomic timing updates with vblank/vupdate boundaries.
- DRR fields include vertical total min/max/mid controls, vtotal min event interrupt state, DRR timing-update and vtotal-reach status/clear/mask/type bits, vtotal reach ranges, vtotal change limits, trigger windows, average-frame selection, and last-used vtotal readback. These support variable refresh behavior.
- Trigger and flow-control fields cover TRIGA/TRIGB source selection, pipe selection, polarity, edge detection, frequency selection, delay, occurred/clear bits, manual trigger bits, force-count-now modes, and manual/global flow control selection.
- Stereo/interlace/3D fields expose current/next field, current eye, stereo sync output/selection, eye flag polarity, force-next-eye pending state, 3D structure enable/update mode, frame-count reset/pending/count, and DP-related stereo/field output disables.
- CRC fields include enable, dual-link mode, blank-only, continuous/one-shot pending bits, stereo/interlace modes, CRC selectors, two window sets for CRC0/CRC1, CRC data readbacks for CRC0-CRC3, and signature masks. These are display validation and diagnostics hooks.
- Interrupt fields are split into status, clear/ack, mask/enable, and type fields. Examples include OTG vertical interrupts, vstartup/vupdate/vready/global sync status, GSL vsync gap, HPD connect/RX events, I2C software/hardware completion, DDC read requests, AUX SW/LS/GTC events, and perfmon counter interrupts.
- Perfmon controls for `DC_PERFMON10` and `DC_PERFMON11` provide event selectors, counter-value selection, increment mode, run-enable mode, hardware stop controls, count-off selection, active state, perfmon state, report count, clock enable, run start/stop selectors, interrupt status/ack bits for counters 0-7, and low/high counter readout.
- I2C/DDC fields represent both software-driven I2C and hardware DDC/EDID detection. Transaction descriptors include read/write direction, stop-on-NACK, start/stop bits, and transfer count. The data register uses an index, data byte, read/write bit, and index-write bit.
- AUX fields distinguish software AUX, link-service AUX, GTC sync AUX, DPHY controls, data windows, arbitration, and wake flow. Status fields enumerate timeout, overflow, HPD disconnect, partial byte, non-AUX mode, invalid start/stop/sync/reply, NACK, reply byte count, and arbitration state.
- DIO and OPTC clock/power fields are single-bit or small enum controls for light sleep, clock gating, memory power force/disable/state, soft reset, power-management gating, and clock-on/busy status.

## Control Flow And State Behavior

There is no executable control flow in this header. Runtime behavior appears only when other AMDGPU Display Core code combines these constants with register addresses and helper macros. A typical usage pattern is:

1. Select the DCN 3.0.3 register address from a companion offset/header table.
2. Use this chunk's `_SHIFT` and `_MASK` macros to pack or unpack the desired field.
3. Perform an MMIO read, write, or read/modify/write through the display register abstraction.
4. Let hardware retain, consume, update, or clear the register-backed state according to the register semantics.

The state represented here is hardware state, not in-memory driver state:

- OTG timing, lock, DRR, stereo/interlace, CRC, blank color, snapshot, and global sync fields persist in timing-generator registers until reprogrammed, reset, or power-gated.
- Status and counter fields are volatile readbacks generated by display hardware, for example current scan position, frame counts, vblank/hsync/vsync state, pipe update pending state, perfmon values, I2C/AUX transaction state, and HPD sense state.
- ACK, clear, and reset fields are write paths that mutate hardware-latched events or state machines. They should not be treated as durable configuration bits.
- I2C/AUX transaction descriptors and data windows are shared hardware queues/register windows. Their state depends on arbitration, transaction completion, abort/timeout/NACK conditions, and ownership by software or DMCU/firmware clients.
- Clock, memory-power, and light-sleep controls influence whether related display subblocks are usable. Driver code must sequence these with register access and reset/power transitions.

The masks themselves do not enforce ordering. Correct code must still respect display hardware sequencing, such as holding update locks while changing double-buffered timing fields, clearing interrupt latches after service, waiting for reset-done or clock-on status, programming I2C/AUX transaction data before asserting go bits, and avoiding live timing/CRC/DRR changes at unsafe scan positions.

## Dependencies And Integration Points

This chunk integrates with:

- Companion DCN 3.0.3 register offset/address headers, especially the matching `dcn_3_0_3_offset.h` style generated headers.
- AMDGPU Display Core register access helpers that consume register-name, mask, and shift tables for `REG_GET`, `REG_SET`, `REG_UPDATE`, and related operations.
- OTG/OPTC timing code that programs scanout geometry, vblank/vsync timing, DRR, global swap lock, update locks, CRC capture, stereo/interlace, DSC start position, and pipe update synchronization.
- IRQ code for OTG vertical interrupts, vstartup/vupdate/vready, GSL gap, HPD, I2C/DDC completion, DDC read requests, AUX completion/error, and perfmon counter interrupts.
- AUX/DDC/I2C code that performs DisplayPort AUX and monitor EDID transactions, handles HPD disconnects and NACK/timeouts, and arbitrates AUX register ownership with firmware/DMCU.
- Hotplug-detect code using HPD0/HPD1 sense, RX interrupt, debounce/toggle filter, connection timers, and fast-train delay/enable fields.
- Clock and power-management paths that control DIO/OPTC/DIG clocks, soft resets, light sleep, memory power, HDMI RX status timers, and power-management gating.
- Debug, validation, and diagnostics tooling that reads OTG status/counters, CRC signatures, perfmon counters, DIO scratch registers, AUX/I2C status, and HPD sense/timer state.

The range depends on generated-name consistency across DCN 3.0.3 headers and driver tables. Because these are preprocessor macros, a stale field name is a compile-time failure only where referenced; a stale numeric mask or shift can compile cleanly and cause runtime hardware misprogramming.

## Risks And Maintenance Notes

- Numeric drift from the ASIC register specification is the primary risk. A wrong mask or shift can write the wrong bits in MMIO registers and corrupt timing, interrupt, power, AUX/DDC, or hotplug behavior.
- The chunk is highly repetitive across OTG0/OTG1, perfmon10/perfmon11, HPD0/HPD1, and AUX0/AUX1. Copying code between instances with the wrong prefix can target the wrong pipe, interrupt source, AUX channel, or hotplug block.
- Clear/ACK fields are side-effecting. Using them in generic read/modify/write paths without care can unintentionally drop pending interrupts, AUX/GTC errors, HPD events, perfmon events, or force-count/snapshot/DRR state.
- Update-lock and double-buffer fields are sequencing-sensitive. Misuse can cause partially applied timing changes, missed vupdate/vready events, visible glitches, or inconsistent pipe update status.
- DRR and vtotal fields interact with scanout timing and frame pacing. Incorrect min/max/mid/range/window programming can produce unstable variable-refresh behavior.
- I2C and AUX transaction fields include timeout, overflow, invalid symbol, NACK, HPD disconnect, and arbitration state. Ignoring these status bits can lead to stuck transactions, failed EDID reads, or DisplayPort link-management failures.
- DIO clock, reset, and light-sleep fields can make subsequent register reads/writes unreliable if toggled while dependent subblocks are active.
- Full-width fields such as DTO phase/modulo, scratch registers, perfmon low values, I2C data windows, and AUX data windows provide no type or range checking. Callers must validate widths, indices, ownership, and transaction lengths.
- The chunk ends partway through DP AUX1. Later chunks must complete AUX1 coverage; this document should not be treated as the full per-file register map.

## Test Signals

Useful validation signals for this chunk are mostly compile-time, generated-header consistency, and hardware/display smoke tests:

- Build AMDGPU with DCN 3.0.3 support and ensure all referenced generated macro names resolve.
- Run static/generated-header checks that every field has a matching `_SHIFT`/`_MASK` pair, masks fit in 32 bits, and fields do not overlap unexpectedly within each register.
- Exercise display modesetting on pipes using OTG1, including timing programming, vblank/vsync interrupts, update locks, double-buffered updates, and pipe-update status.
- Test DRR/VRR behavior and verify vtotal min/max/mid, DRR timing-update, vtotal-reach, and vupdate/vready signals behave as expected.
- Use display CRC diagnostics to enable CRC capture, configure windows/selectors, read CRC0-CRC3 data, and confirm one-shot/continuous pending bits clear correctly.
- Exercise hotplug on HPD0 and HPD1, including debounce/toggle filtering, RX interrupt handling, connection timers, fast-train delays, and interrupt acknowledgements.
- Run EDID/DDC tests over DDC1/DDC2 and software I2C paths, checking transaction counts, start/stop/stop-on-NACK behavior, completion interrupts, NACK/timeout/abort states, and EDID detect state.
- Run DisplayPort AUX tests over AUX0 and the initial AUX1 register set, including SW and LS transactions, AUX arbitration with firmware/DMCU, HPD disconnect handling, timeout/overflow/invalid-reply reporting, data-window indexing, and interrupt ACK/mask behavior.
- Validate DIO/OPTC power and clock transitions around suspend/resume, runtime power management, display blank/unblank, and DIG soft reset.
- Configure `DC_PERFMON10` and `DC_PERFMON11`, sample counter low/high values, trigger counter interrupts, and verify status/ack bits clear without losing counter state.

## Chunk-Specific Summary

Lines 14926-17341 define a dense DCN 3.0.3 register-field surface rather than executable code. The most important responsibilities in this slice are OTG0 tail and OTG1 timing-generator control, atomic update synchronization, DRR, CRC, HPD, I2C/DDC, AUX0 and partial AUX1 transaction handling, DIO/OPTC clock and memory-power controls, and display perfmon counters. Correctness is measured by exact generated mask/shift values, instance-correct macro use, and successful hardware behavior under modeset, interrupt, hotplug, AUX/DDC, power-management, CRC, DRR, and perfmon workloads.

### subset-b-001788: lines 17342-19736

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_3_sh_mask.h lines 17342-19736

## Purpose

This chunk is generated AMD DCN 3.0.3 register field metadata. It contains no executable C logic; it defines `#define` constants for field shifts and masks used by AMDGPU Display Core register helpers when packing and unpacking memory-mapped display-controller registers.

The selected range starts inside the `DP_AUX1_AUX_INTERRUPT_CONTROL` mask list, completes the remaining `DP_AUX1` software AUX/status/DPHY/GTC-sync/PHY-wake fields, then covers the display I/O stream-encoder-related blocks for DIG instance 0: `VPG0`, `AFMT0`, `DME0`, `DIG0`, and `DP0`. It then begins the mirrored DIG instance 1 blocks for `VPG1`, `AFMT1`, and the start of `DME1_DME_CONTROL`; line 19736 stops before the rest of `DME1` and `DIG1`.

Although the source tree is under a local `ceph-client` mirror, this file is AMDGPU display hardware metadata, not Ceph or distributed filesystem logic.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, includes, locks, allocations, or callbacks in this chunk. The public interface is the generated macro namespace:

- `<REGISTER>__<FIELD>__SHIFT`: bit offset for a field.
- `<REGISTER>__<FIELD>_MASK`: bit mask for the same field, usually with an `L` suffix.

Major macro families in this slice:

- `DP_AUX1_*`: software AUX transaction status and FIFO data access, link-service status/data, DPHY TX/RX timing and status, AUX interrupt bits, AUX GTC sync control/error/status/counter fields, and AUX PHY wake control.
- `VPG0_*` and `VPG1_*`: video packet generator access/data registers, generic stream packet frame-update and immediate-update controls for packet slots 0 through 11, generic packet status, memory power control, ISRC indexed data, and MPEG infoframe fields.
- `AFMT0_*` and `AFMT1_*`: audio formatter fields for HDMI audio packet limits, audio layout/channel/stream selection, audio infoframe bytes, IEC 60958 channel-status words, audio CRC control/result, audio ramp test controls, audio status, audio sample send/test/overflow acknowledgements, infoframe update control, audio source selection, and AFMT memory power state.
- `DME0_*` plus the beginning of `DME1_DME_CONTROL`: metadata engine requestor, enable, stream type, double-buffer pending/taken/clear/disable fields, and DME memory power control for instance 0.
- `DIG0_*`: front-end source and pixel selection, Dolby Vision flags, symbol clock status, HDMI/TMDS pixel encoding/color format, output CRC, test/random/clock patterns, FIFO underflow/overflow/depth status, HDMI metadata/audio/ACR/VBI/infoframe/generic-packet controls, HDMI guard-band/control-period/deep-color/status fields, TMDS control, TMDS data-balance and control-symbol generation, DIG version, lane enablement, and forced disable.
- `DP0_*`: DisplayPort link control, pixel format, MSA colorimetry/config/timing/misc/VBID fields, stream control, FIFO steering, VID M/N, link framing, DPHY control/training/symbol/8b10b/PRBS/scrambler/CRC/fast-training fields, secondary-data packet controls, DP audio M/N/timestamp fields, MST/MSE stream allocation table fields, MSO controls, DSC controls, double-buffer controls, ALPM, and generic stream packet slots 8 through 11.

The macros are normally consumed indirectly through token-pasting helpers such as `SF`, `SRI`, `SE_SF`, `HWS_SF`, and block lists like `DCN_AUX_MASK_SH_LIST`, `VPG_DCN3_REG_LIST`, `AFMT_DCN3_REG_LIST`, and `SE_DCN3_REG_LIST`.

## Control Flow

This header has no runtime control flow. Runtime sequencing comes from AMD Display Core:

1. `dcn303_resource.c` includes `dcn/dcn_3_0_3_offset.h` and this matching `dcn/dcn_3_0_3_sh_mask.h`.
2. Resource macros paste register and field tokens into generated constants, then initialize per-block register, shift, and mask tables.
3. DCN 3.0.3 constructors allocate display objects and pass those tables into component constructors such as `dcn30_dio_stream_encoder_construct()`, `vpg3_construct()`, `afmt3_construct()`, `dce110_aux_engine_construct()`, and `dcn10_dio_construct()`.
4. Modeset, hotplug, AUX/I2C, audio, HDMI, DP, MST, DSC, and infoframe paths use `REG_GET`, `REG_SET`, `REG_UPDATE`, and related helpers to access the hardware fields described here.

The macros do not encode sequencing. Callers must still order link training, stream setup, AUX transactions, infoframe updates, audio source selection, interrupt acknowledgement, double-buffer commits, memory power transitions, and suspend/resume restore correctly.

## State And Persistence Behavior

This chunk stores no software state and persists nothing on disk. It describes bit layouts for state held in GPU display hardware registers.

Important hardware state represented by the fields includes:

- AUX transaction state: software request completion, reply byte count, timeout/overflow/invalid-start/stop/sync errors, HPD disconnect indications, arbitration status, data byte/index access, and interrupt/ack/mask bits.
- AUX PHY/GTC state: TX/RX timing windows, symbol-period status, sync enable, lock acquisition/maintenance periods, error masks, offset/min/max counters, controller lock/error status, and PHY wake enable/delay parameters.
- VPG packet state: packet slot update modes, line numbers, send timing, generic packet readiness/collision status, and payload/index windows for generic, ISRC, and MPEG packets.
- AFMT/audio state: HDMI/DP audio stream ID, channel enable mask, layout override, audio infoframe bytes, IEC 60958 channel-status fields, CRC counters/results, test-ramp configuration, overflow and audio-enable status, and audio-source selection.
- DIG/HDMI/TMDS state: source selection, encoder start/bypass, test patterns, FIFO status, HDMI packet scheduling, ACR N/CTS programming and status, generic packet enable/update timing, guard-band and control-period settings, TMDS control-symbol generation, lane enablement, and forced disable.
- DP stream/link state: link rate/lane-count/enhanced framing, pixel encoding, MSA timing, training pattern and DPHY controls, scrambling/PRBS/CRC diagnostics, secondary packet and audio timing, MST allocation, MSO and DSC enablement, double-buffering, ALPM, and high-numbered generic stream packet controls.
- Metadata/DME state: metadata requestor selection, engine enable, stream type, double-buffer pending/taken state, disable flags, and memory power state.

Persistence is hardware-defined. Configuration bits generally remain until overwritten, reset, power-gated, or restored by driver resume paths. Status, interrupt, CRC, collision, timeout, double-buffer, and acknowledgement fields may be sticky, write-one-to-clear, read-only, self-clearing, or latch-on-read depending on the register. This generated mask file does not identify access type or side effects.

## Dependencies And Integration Points

The chunk depends on AMD's generated DCN 3.0.3 register database and must remain synchronized with `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_3_offset.h`, which provides matching register addresses and base-index constants.

The direct consumer in this tree is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn303/dcn303_resource.c`. That file includes this header and uses token-pasted shift/mask constants to build:

- `vpg_regs`, `vpg_shift`, and `vpg_mask` for `VPG0` and `VPG1` stream packet generators.
- `afmt_regs`, `afmt_shift`, and `afmt_mask` for `AFMT0` and `AFMT1` audio formatter blocks.
- `stream_enc_regs`, `se_shift`, and `se_mask` for `DIG0` and `DIG1` stream encoder register programming; this chunk contains the complete `DIG0` side and starts the instance-1 adjacent blocks.
- `aux_engine_regs`, `aux_shift`, and `aux_mask` for `DP_AUX0/1` AUX engines; this chunk contributes the `DP_AUX1` field definitions.
- `dio_regs`, `dio_shift`, and `dio_mask` for the DIO wrapper power-control integration, though this specific chunk is mostly stream/AUX rather than the DIO global power register.

Higher-level integration is through Display Core link encoder, stream encoder, VPG, AFMT, DME, AUX, and audio objects. These objects expose behavioral operations such as AUX transfers, DP/HDMI stream enablement, infoframe programming, MST allocation, DSC setup, and audio packet control while relying on this header only for bit positions.

## Risks And Edge Cases

- Mask/shift drift is the main risk. A wrong generated value still compiles but can silently program the wrong hardware bit.
- The range is artificially chunked. It starts after the beginning of `DP_AUX1_AUX_INTERRUPT_CONTROL` and ends in the middle of `DME1_DME_CONTROL`, so adjacent chunks are required for complete file-level reasoning.
- Instance symmetry is copy-sensitive. `VPG0/AFMT0/DME0/DIG0/DP0` and `VPG1/AFMT1/DME1/DIG1` have similar names but distinct register instances; a prefix mismatch can route packets, audio, AUX, or metadata to the wrong engine.
- AUX status and interrupt fields are side-effect-sensitive. Mishandling done/ack/mask, timeout, HPD-disconnect, or arbitration fields can hang DPCD/EDID reads, break hotplug handling, or hide link-service updates.
- Packet update fields are timing-sensitive. Generic, AVI/audio, ISRC, MPEG, DP secondary-data, and GSP update controls interact with frame boundaries and double buffering; bad masks can produce stale, torn, or missing infoframes.
- Audio formatter fields affect externally visible HDMI/DP audio behavior. Incorrect channel enables, layout, stream ID, IEC 60958 fields, HBR override, or audio-source selection can cause silence, wrong channel mapping, or bad sink capability behavior.
- DP link-training and diagnostic fields are hardware-critical. Mistakes in DPHY, scrambler, PRBS, CRC, MSA, MST allocation, MSO, DSC, or ALPM fields can cause link training failures, display blanking, intermittent corruption, or power-state regressions.
- Status and memory-power fields may be read-only or asynchronous. Treating state bits as ordinary writable configuration can race power gating, FIFO state transitions, or metadata double-buffer ownership.

## Test Signals

Useful validation signals for changes touching this generated data include:

- Build coverage for the DCN 3.0.3 AMDGPU display target; token-pasted users catch missing or renamed macros at compile time.
- Boot and modeset tests on DCN 3.0.3 hardware using both DIG0 and DIG1 paths, including HDMI and DP outputs.
- AUX/DPCD/EDID tests on the second AUX engine, especially timeout, HPD disconnect, arbitration, and retry paths.
- DP link-training coverage across lane counts/rates, enhanced framing, MST allocation, DSC, MSO, ALPM, and suspend/resume.
- HDMI validation for ACR, deep color, generic packets, AVI/audio infoframes, guard-band/control-period behavior, and TMDS output.
- Audio playback tests for stereo, multichannel, HBR, channel-status, stream ID, audio source selection, FIFO overflow acknowledgement, and audio CRC diagnostics.
- Infoframe and metadata checks that verify VPG/AFMT/DME packet updates occur on the intended frame boundaries and no generic packet collision/status bits remain stuck.
- Runtime power-management and display resume tests that confirm AFMT, VPG, DME, AUX, and DIG state is restored after power gating.

### subset-b-001789: lines 19737-22116

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_3_sh_mask.h lines 19737-22116

## Purpose

This chunk is generated AMD DCN 3.0.3 register field metadata. It contains no executable C code; it publishes `#define` constants for field shifts and masks used by AMDGPU display code when packing and unpacking DCN 3.0.3 MMIO register values.

The selected range spans 2,372 macro/comment lines. It starts at the tail of the `DME1_DME_CONTROL` mask block, covers `DME1_DME_MEMORY_CONTROL`, then moves through the first digital-output instance's DIO encoder blocks: `DIG1`, `DP1`, DCIO, LVTMA/backlight power sequencing, and GPIO/DDC/AUX/HPD pad controls. The chunk ends inside `DC_GPIO_RXEN`; later receive-enable masks for the remaining HPD and panel-control pins are in the next chunk.

Although this file is under a local `ceph-client` source mirror, this content is AMD Display Core hardware metadata, not Ceph or distributed filesystem logic.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, allocation sites, locks, or callbacks in this range. The public interface is the generated macro namespace:

- `<REGISTER>__<FIELD>__SHIFT`: bit position for a field within a 32-bit register value.
- `<REGISTER>__<FIELD>_MASK`: bit mask for the same field, usually written with an `L` suffix.

Major macro families in this slice:

- `DME1_DME_CONTROL` tail and `DME1_DME_MEMORY_CONTROL`: metadata double-buffer status/clear/disable bits and DME memory power force, disable, state, and default low-power-state fields.
- `DIG1_DIG_FE_CNTL`: digital front-end source selection, stereosync selection/gating, start bit, digital-bypass selection, pixel input selection, Dolby Vision enable/missed-metadata status, symbol-clock status, and TMDS pixel/color format.
- `DIG1_DIG_OUTPUT_CRC_*`, `DIG1_DIG_CLOCK_PATTERN`, `DIG1_DIG_TEST_PATTERN`, and `DIG1_DIG_RANDOM_PATTERN_SEED`: output CRC enable/link/data selection, CRC results, static/random test-pattern controls, clock pattern, and random-pattern seed behavior.
- `DIG1_DIG_FIFO_STATUS`: FIFO level error/ack, overwrite level, calibrated average/min/max levels, read clock source, calibration status, and forced recalculation/recompute bits.
- `DIG1_HDMI_*`: HDMI metadata packet control, core HDMI control/status, audio packet delay, ACR packet control, VBI packet control, audio/MPEG infoframe control, generic packet send/continuous/line-reference/update-lock controls for packets 0 through 14, immediate-send/pending bits, global control packet fields, double-buffer controls, programmed and status CTS/N values for 32 kHz, 44.1 kHz, and 48 kHz families, and AFMT audio clock enable/status.
- `DIG1_DIG_BE_*` and `DIG1_TMDS_*`: digital back-end enable/mode/source/HPD selection, dual-link and lane controls, TMDS control-character generation, sync-character patterns, data-balance controls, CTL bit generation, DIG type/version, lane enable, clock enable, and force-disable.
- `DP1_DP_*`: DisplayPort link count/rate/spread, pixel format, MSA colorimetry and timing fields, video stream enable/status, steering FIFO, VBID/MSA miscellaneous data, video N/M values, link framing, HBR2 eye-pattern control, interrupts, DPHY control/training/symbol/test/scramble/CRC/fast-training fields, secondary-data packet controls, audio N/M and readback, MSE/MST rate and slot allocation controls/status, MSO controls, DSC bytes-per-pixel, ALPM controls, metadata transmission, and generic SDP controls for GSP8 through GSP11.
- `DC_GENERICA`, `DC_GENERICB`, `DCIO_CLOCK_CNTL`, `DC_REF_CLK_CNTL`: generic DCIO GPIO-style pins, clock gating/enable/status, reference clock mux/divider/root-gate control, and spread-spectrum state.
- `UNIPHYA_*` and `UNIPHYB_*`: link control and channel crossbar fields for the first two display PHY blocks, including enable, mode, connection, calibration, powerdown, output-enable, and lane crossbar mappings.
- `DCIO_WRCMD_DELAY`, `DC_PINSTRAPS`, and `DCIO_SOFT_RESET`: write-command delay tuning, strap reporting for audio/backlight/spread-spectrum and panel/connection capabilities, and soft resets for DIO, DP AUX, DC GPIO, and audio-related logic.
- `LVTMA_PWRSEQ_*`, `BL_PWM_*`, and `BL_PWM_GRP1_REG_LOCK`: embedded-panel power sequencing, state/readback, reference divider, delay programming, backlight PWM enable/debug/fractional and period controls, and grouped PWM register locking.
- `DCIO_GSL_GENLK_PAD_CNTL` and `DCIO_GSL_SWAPLOCK_PAD_CNTL`: genlock/swaplock pad mux, polarity, mask, and receive fields.
- `DC_GPIO_*`: generic GPIO, DDC1, DDC2, DDCVGA, genlock, HPD, power-sequence, pad-strength, PHY AUX, TX12 enable, AUX/I2C/HPD electrical tuning, and receive-enable fields. The chunk ends after `DC_GPIO_RXEN` masks for `GENERICA` through `HPD3`.

These macros are normally consumed through token-pasting helpers such as `FD_MASK(reg, field)`, `FD_SHIFT(reg, field)`, `SF(reg, field, post_fix)`, or block-specific register-table macros, rather than by direct handwritten references to every generated name.

## Control Flow

This header chunk has no runtime control flow. Runtime sequencing is supplied by AMD Display Core and DMUB code:

1. DCN 3.0.3 users include the matching offset header and this shift/mask header.
2. Register helpers paste register and field tokens into names such as `DIG1_HDMI_CONTROL__HDMI_DEEP_COLOR_ENABLE_MASK` or `DP1_DP_SEC_CNTL__DP_SEC_STREAM_ENABLE__SHIFT`.
3. Static register/field tables and helper macros convert those constants into packed MMIO reads, writes, field updates, interrupt masks, and firmware-service register descriptors.
4. Modeset, link-training, audio, HPD, AUX/I2C, backlight, panel-power, and interrupt paths perform the actual ordering around the raw bitfields.

The direct DCN 3.0.3 include sites visible in this tree are `display/dmub/src/dmub_dcn303.c` and `display/dc/irq/dcn303/irq_service_dcn303.c`. `dmub_dcn303.c` uses the generated masks and shifts to populate `dmub_srv_dcn303_regs` common register fields through `FD_MASK` and `FD_SHIFT`. `irq_service_dcn303.c` uses the same generated register database with `SRI` and `IRQ_REG_ENTRY` style macros for interrupt enable, acknowledge, and status register descriptors. The broader DIO, stream encoder, AUX, GPIO, and audio flows are implemented in shared AMD Display Core components that expect these ASIC-specific definitions to match the offset file.

The selected macros do not encode sequencing. Consumers still must order link disable/enable, clock enablement, DIO/PHY reset, DP link training, HDMI packet setup, double-buffer update/clear, MST/MSO slot programming, panel power sequencing, AUX/DDC ownership, HPD interrupt acknowledgement, and suspend/resume restore correctly.

## State And Persistence Behavior

This chunk stores no software state and persists nothing by itself. It describes bit layouts for hardware state maintained by the GPU display controller.

Important hardware state represented by the fields includes:

- DME metadata and memory-power state: metadata double-buffer status/clear/disable bits plus DME memory force/disable/default low-power controls.
- Digital encoder state: selected source, start/disable status, front-end/back-end clock status, DIG mode, HPD selection, dual-link settings, lane enables, TMDS control-character patterns, DCBALANCER state, and test-pattern programming.
- HDMI transport state: AVMUTE/error status, deep color and scrambling controls, audio delay, ACR send/continuous/auto-send/source/N-multiple controls, infoframe and generic packet scheduling, immediate-send pending bits, double-buffer state, and programmed/readback ACR N/CTS values.
- DisplayPort transport state: link rate/count/spread, stream enable, MSA timing and colorimetry, VBID overrides, DPHY training/scrambling/CRC/test state, fast-training state/acknowledge, secondary-data packet enable/scheduling, audio N/M, MST/MSE allocation, MSO control, DSC bytes-per-pixel, ALPM requests/pending state, and generic SDP enable/pending/deadline status.
- DCIO/PHY state: clock and reference-clock selection/gating, UNIPHY link modes and lane crossbars, soft-reset bits, strap-derived capabilities, and write-delay tuning.
- Panel and backlight state: LVTMA power-sequence control/state, delay counters, reference divider, PWM enable/period/fractional controls, PWM debug and register locks.
- GPIO/DDC/AUX/HPD state: output masks, output values, output enables, sensed values, pad pull-up/pull-down/drive-strength/receive controls, AUX pad mode and polarity, genlock/swaplock pins, HPD electrical tuning, and generic RX enables.

Persistence is hardware-defined. Configuration bits generally remain until overwritten, reset, power-gated, or restored after suspend/resume. Status, pending, acknowledge, clear, lock, readback, calibration, CRC, and error fields may be read-only, sticky, write-one-to-clear, self-clearing, or latch-on-read depending on the register. This generated header gives only shifts and masks; it does not describe access type, reset values, or side effects.

## Dependencies And Integration Points

This chunk depends on AMD's generated DCN 3.0.3 register database and must remain synchronized with:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_3_offset.h`, which provides matching MMIO offsets and base-index constants.
- `sienna_cichlid_ip_offset.h` and DCN base-segment macros used to turn generated offsets into absolute register addresses.
- AMD Display Core register helper macros such as `REG_GET`, `REG_SET`, `REG_UPDATE`, `FD_MASK`, `FD_SHIFT`, `SF`, `SRI`, and block-specific register-list macros.
- DCN 3.0.3 DMUB register descriptors in `display/dmub/src/dmub_dcn303.c`.
- DCN 3.0.3 interrupt descriptors in `display/dc/irq/dcn303/irq_service_dcn303.c`.
- Shared DIO, DP/HDMI stream encoder, AUX/DDC, GPIO, HPD, backlight, and panel-power code paths that use the ASIC-specific offset and shift/mask headers to program hardware.

The chunk is source-tree aligned with DCN 3.0.3 hardware instance 1 naming. Similar macro families exist for other DIG/DP instances and other DCN ASIC generations, but the numeric masks in this file are only valid for the matching DCN 3.0.3 register layout.

## Risks And Edge Cases

- Mask/shift drift is the central risk. A wrong value still compiles but can silently write or read the wrong hardware bits.
- This chunk begins and ends inside larger generated blocks: it starts after the beginning of `DME1_DME_CONTROL` and stops inside `DC_GPIO_RXEN`. Adjacent chunks are required for complete file-level coverage.
- Repeated instance naming is copy-sensitive. `DIG1`/`DP1` fields look like other encoder instances, but a prefix mismatch can route programming to the wrong display output.
- HDMI and DP packet scheduling has pending, immediate-send, continuous-send, line-reference, deadline-missed, and double-buffer fields. Treating pending or clear bits as plain configuration can lose metadata packets, infoframes, or audio packets.
- DP link-training and DPHY fields are timing-sensitive. Incorrect training pattern, scramble, CRC, fast-training, or ALPM masks can cause link bring-up failures that only appear with specific panels, cables, rates, or power states.
- MST/MSE/MSO and DSC fields are bandwidth-sensitive. Bad slot allocation, rate X/Y, secondary-data enable, or bytes-per-pixel masks can produce black screens, corruption, audio loss, or multi-stream routing failures.
- GPIO/DDC/AUX/HPD fields mix output, enable, receive, pull, drive-strength, pad-mode, polarity, and electrical compensation controls. A bad mask can break EDID reads, AUX transactions, HPD detection, backlight control, or external genlock/swaplock.
- Power-sequence and PWM fields can affect embedded panels. Incorrect LVTMA sequencing, delay, PWM period, lock, or soft-reset handling can cause visible flicker, panel power timing violations, or backlight state loss across suspend/resume.
- Status/ack fields such as error, CRC, fast-training complete, secondary-packet pending, double-buffer taken, and interrupt acknowledgement may have clear-on-write semantics not visible in this header.

## Test Signals

Useful validation signals for changes touching this chunk or generated data around it include:

- Build coverage for DCN 3.0.3 AMDGPU display paths; token-pasting consumers catch missing or renamed macros at compile time.
- HDMI modeset tests covering deep color, scrambling, AVMUTE behavior, infoframes, generic metadata packets, Dolby Vision metadata, and audio ACR/N/CTS programming.
- DisplayPort link-training tests across link rates and lane counts, including DPHY training patterns, scrambling, CRC diagnostics, HBR2 eye pattern, fast training, ALPM, and link recovery.
- DP MST/MSO/DSC tests that verify stream allocation, MSE slot programming, secondary-data packets, VBID/MSA timing, and compressed stream bytes-per-pixel values.
- Audio playback over HDMI and DP, including sample-rate switching, infoframe generation, audio mute/unmute, N/M readback, and hotplug after modeset.
- AUX/DDC/HPD validation: EDID/DPCD reads, HPD and HPD RX interrupts, AUX polarity/pad mode behavior, GPIO receive states, and retry/error reporting.
- Embedded-panel tests: LVTMA panel power sequencing, backlight PWM enable/period/fractional behavior, register lock handling, suspend/resume, and runtime power-management recovery.
- Diagnostic register reads during failures: packet pending/deadline bits, double-buffer pending/taken bits, FIFO status, DP CRC results, DPHY training state, DC_PINSTRAPS, HPD status, AUX/DDC GPIO sense bits, and soft-reset status.

### subset-b-001790: lines 22117-24606

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_3_sh_mask.h lines 22117-24606

## Purpose

This chunk is generated AMD DCN 3.0.3 register field metadata. It contains no executable C logic; it publishes preprocessor constants for bit shifts and bit masks used to read, write, and update fields inside memory-mapped display-controller registers.

The requested range starts at the tail of `DC_GPIO_RXEN`, then covers `DC_GPIO_PULLUPEN`, AUX/DDC pad controls, DSC instance 0 and 1 field definitions, DSC-local performance monitor blocks, display writeback `DWB0` capture/color/gamma fields, MPCC instance 0 and 1 blending controls, and the beginning of `MPCC_OGAM0` output-gamma RAM field definitions. It is the companion style of header to a DCN offset header: consuming code combines register offsets from an `*_offset.h` file with the `__SHIFT` and `_MASK` constants here to safely pack and extract fields.

Although this source path is under a local `ceph-client` mirror, the content is AMDGPU display-driver hardware metadata. It is unrelated to Ceph filesystem protocol behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, includes, allocation paths, or locking primitives in this range. The public interface is the generated macro namespace:

- `<REGISTER>__<FIELD>__SHIFT`: bit position of a hardware register field.
- `<REGISTER>__<FIELD>_MASK`: bit mask for that same field.

Major macro families in this slice:

- `DC_GPIO_*`: GPIO input-enable tail, pull-up enable fields for generic GPIOs, sync pins, HPD pins, backlight/panel signals, plus AUX termination, DP/DN swap, hysteresis tuning, AUX drive/control, AUX voltage-output tuning, DDC pad I2C mode, 1.2 V enable, pad I2C control, and AUX/I2C PHY power-good status.
- `DSC_TOP0` and `DSC_TOP1`: DSC clock enable, clock-gating disables, debug enable, and test-clock mux fields.
- `DSCCIF0` and `DSCCIF1`: DSC client-interface configuration for underflow recovery/interrupt/status, input pixel format, bits per component, double-buffer update pending, picture width, and picture height.
- `DSCC0` and `DSCC1`: DSC compressor configuration, status, interrupt/status bits, picture parameter set fields, memory power control, squared-error and maximum-absolute-error counters, rate-buffer fullness counters, and debug-bus rotate fields.
- `DC_PERFMON12`, `DC_PERFMON13`, and `DC_PERFMON14`: local display perfmon counter control, counter source/type/mode selection, hardware start/stop/counter-off selection, counter state, report count, interrupt status/ack, high/low counter values, and read selectors.
- `DWB_*` and `FC_*`: display writeback enable/clock/memory power, frame capture enable/rate/crop/eye selection/new-content state, source/window geometry, update lock/pending, CRC control/masks/values, output format/denorm/min/max, MMHUBBUB backpressure counters, host-read control, overflow status/counters, and soft reset.
- `DWB_GAMUT_REMAP*` and `DWB_OGAM*`: writeback color-processing fields, including gamut-remap mode/format and two coefficient matrices, output gamma mode/select/current state, LUT index/data/control, and RAM A/B piecewise-linear region start/end/base/slope/offset/segment fields.
- `MPCC0` and `MPCC1`: MPC compositor control fields for top/bottom mux selection, OPP ID, alpha/blend/overlap flags, stereo/field controls, shared-mem controls, update lock selection, top/bottom gains, background color channels, memory power, and status/current mux values.
- `MPCC_OGAM0`: MPCC output-gamma mode/select/current state, LUT access fields, RAM A piecewise-linear region programming for regions 0 through 33, and the beginning of RAM B start/end field definitions through `MPCC_OGAM0_MPCC_OGAM_RAMB_END_CNTL2_R`.

The macros are intentionally untyped `#define` constants. Type safety, volatile MMIO access, field value range checks, and read-modify-write behavior are supplied by the AMD display register helper layers that include this file.

## Control Flow

This header has no runtime control flow. Runtime sequencing is provided by AMDGPU display code:

1. DCN 3.0.3 resource, GPIO, DSC, DWB, MPC, and DMUB paths include this shift/mask header with the matching offset header.
2. Register-list macros paste register and field names into helper macros such as `REG_UPDATE`, `REG_SET`, `REG_GET`, `REG_SET_2`, and block-specific `SRI`/`SR` register-table initializers.
3. Consumers use the `__SHIFT` and `_MASK` pairs to encode values into 32-bit MMIO writes or decode status/counter fields from 32-bit MMIO reads.
4. Driver control flow around those accesses handles clocks, power gating, double-buffer update locks, status polling, interrupt acknowledgement, modeset ordering, and suspend/resume restoration.

The macros themselves do not encode ordering. For example, DSC PPS fields must be programmed in the compressor's expected sequence, DWB gamma/LUT and gamut-remap fields must follow writeback pipeline update rules, and MPCC blending fields must be coordinated with MPC update locks and pipe topology.

## State And Persistence Behavior

The chunk stores no software state and persists nothing to disk. It describes hardware state held in DCN 3.0.3 display registers.

State represented by this chunk includes:

- Pad and GPIO configuration for pull-ups, HPD-related pins, panel/backlight-related pins, AUX termination/swap/tuning/control, DDC I2C behavior, voltage enables, and AUX/I2C PHY power-good reporting.
- DSC top/client/compressor state for clocking, input format, picture size, slice configuration, PPS payload programming, buffer thresholds, quantization parameter ranges, BPG offsets, memory low-power policy, interrupt/status bits, rate-buffer fullness, and compression error metrics.
- Perfmon state for DSC and writeback blocks, including event source selection, counter mode, active status, run start/stop selection, counter-off conditions, interrupt status/ack, and high/low counter values.
- DWB state for capture enable/rate/window/source geometry, CRC generation, output format, host readback, overflow tracking, MMHUBBUB backpressure accounting, memory power, soft reset, gamut remap, and output gamma RAM/LUT contents.
- MPCC and MPCC OGAM state for compositor routing, blend/alpha behavior, background color, update lock, memory power, active mux/status reporting, and output gamma piecewise-linear RAM contents.

Persistence is hardware-defined. Configuration fields usually survive until the block is reprogrammed, gated, reset, or the GPU enters a suspend/reset path. Status, interrupt, counter, update-pending, current-state, and power-state fields may be read-only, sticky, write-one-to-clear, self-clearing, or transient. This generated header does not indicate access type; consumers must rely on hardware programming guides and existing AMD display block code.

## Dependencies And Integration Points

This chunk depends on the generated DCN 3.0.3 register database and must match the companion register-offset namespace for the same ASIC generation:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_3_offset.h`
- sibling DCN shift/mask headers used for comparison or related ASIC variants, such as `dcn_3_0_0_sh_mask.h` and nearby DCN 3.x headers
- AMD display register helper macros that expect `__SHIFT` and `_MASK` names generated from register and field tokens

Likely integration points in the AMD display tree include:

- GPIO and link/pad code that programs `DC_GPIO_*`, AUX, DDC, HPD, panel-power, and backlight-related fields.
- DSC resource and encoder code that writes `DSC_TOP*`, `DSCCIF*`, and `DSCC*` fields when enabling DSC for high-bandwidth DisplayPort/eDP modes.
- IRQ/status code that reads and acknowledges DSCC underflow, overflow, and rate-control-buffer status bits.
- DWB/writeback code that configures frame capture, crop/source geometry, output format, CRC, overflow handling, host readback, color transforms, and writeback output gamma.
- MPC/MPCC code that sets MPCC source selection, OPP routing, alpha/blending controls, gains, background color, update locks, memory power, and MPCC OGAM LUT/RAM fields.
- Debug/perf paths that configure `DC_PERFMON12`, `DC_PERFMON13`, and `DC_PERFMON14` counters for DSC and writeback diagnostics.

The primary integration contract is name stability. A register helper can only build field operations if the generated register and field tokens match the offset header, register lists, and block-specific C code.

## Risks And Edge Cases

- Shift or mask drift is the main risk. These constants compile as ordinary numeric macros, so a wrong mask or shift can silently program the wrong bits in a real hardware register.
- Copy-family errors are easy in repeated generated blocks. `DSCC0` and `DSCC1`, `DC_PERFMON12` through `14`, `MPCC0` and `MPCC1`, and RAM A/B gamma region families are structurally similar but instance-specific.
- Some fields span nearly the whole register, such as 32-bit error counters or LUT data, while others are narrow single-bit controls. Incorrect field width can truncate values, leak neighboring fields, or break read-modify-write preservation.
- Status and interrupt fields require correct access semantics. Treating sticky or write-one-to-clear bits like ordinary writable configuration can lose diagnostics or leave interrupts asserted.
- DSC PPS fields are bandwidth and format critical. Bad masks for `BITS_PER_PIXEL`, slice geometry, RC model sizes, buffer thresholds, QP ranges, or BPG offsets can produce visual corruption, link failures, or failures only on DSC-enabled panels.
- DWB and OGAM LUT/RAM fields are stateful programming surfaces. Incorrect index/data/control or region start/end/slope/base masks can corrupt captured frames, CRC validation, color conversion, or gamma output.
- MPCC blend/routing fields affect pipe composition. A bad source selection, OPP ID, alpha mode, gain, or update lock field can cause blank planes, wrong z-order, stale updates, or pipe-specific artifacts.
- GPIO/AUX/DDC pad fields interact with external electrical behavior. Wrong pull-up, termination, voltage, swap, or I2C mode masks can cause hotplug, EDID, AUX, panel, or backlight issues that are board-specific.
- The chunk boundary is artificial. It starts after earlier `DC_GPIO_RXEN` shift definitions and stops inside `MPCC_OGAM0` RAM B definitions; the final file report must merge adjacent chunks before making whole-header claims.

## Test Signals

Useful validation combines generated-header consistency checks and hardware behavior:

- Build AMDGPU/DC with the DCN 3.0.3 paths enabled; missing or renamed field macros should fail where register tables and helper macros reference them.
- Mechanically verify that each visible `__SHIFT` macro in lines 22117-24606 has the expected matching `_MASK` macro for the same register/field, and that repeated instance blocks preserve intended symmetry between `DSCC0`/`DSCC1`, `MPCC0`/`MPCC1`, perfmon instances, and RAM A/B region families.
- Compare this chunk against AMD's authoritative generated DCN 3.0.3 register headers and adjacent DCN 3.x variants to detect accidental drift in bit positions or masks.
- Exercise hotplug, EDID/DDC reads, AUX DPCD transactions, panel power, backlight, suspend/resume, and low-power wake on boards using the affected GPIO/AUX/DDC pads.
- Enable DSC on capable DisplayPort/eDP panels across multiple formats, slice layouts, and bandwidth pressure points; monitor for visual corruption, link training failures, DSCC underflow/overflow/rate-control-buffer status, and error-counter changes.
- Exercise writeback/frame capture paths with crop windows, different source sizes, output formats, CRC capture, host readback, overflow/backpressure monitoring, gamut remap, and output gamma programming.
- Test compositor paths using MPCC instances 0 and 1 with plane blending, alpha, stereo/field settings, background color, update locks, memory power transitions, and output gamma programming.
- Use perfmon/debug paths to read DSC and DWB counter values and interrupt status/ack behavior, checking for stuck counters, invalid high/low reads, or unexpected active-state behavior.
- Watch kernel logs and display diagnostics for AUX timeouts, hotplug storms, DSC PPS failures, writeback overflow, CRC mismatches, stuck interrupts, color/gamma regressions, blank planes, and resume-only failures.

## Cross-Chunk Notes

Earlier chunks own the start of the GPIO and DCIO shift/mask namespace, including the beginning of `DC_GPIO_RXEN`. Later chunks continue `MPCC_OGAM0` RAM B fields and the rest of the DCN 3.0.3 shift/mask register map. This document is only the worker-produced research for `subset-b-001790`; the final per-file research document should merge it with all other chunks for `dcn_3_0_3_sh_mask.h`.

### subset-b-001791: lines 24607-27132

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_3_sh_mask.h lines 24607-27132

## Purpose

This chunk is generated AMD DCN 3.0.3 register field metadata. It contains no executable C logic; it publishes `#define` constants for register-field bit shifts and masks used by AMDGPU Display Core to pack and unpack MMIO register values.

The selected range starts in the middle of the `MPCC_OGAM0` output-gamma block, covers the full `MPCC_OGAM1` output-gamma block, then continues through MPC global configuration, output CSC/denorm programming, RMU shaper and 3D LUT registers, display performance monitor blocks, HPO top clocking, two ABM/backlight blocks, and the start of the HDA Azalia CORB/RIRB controller block. Although the file lives under a local `ceph-client` source mirror, this content is AMD GPU display-controller hardware metadata, not Ceph or distributed-filesystem code.

## Important APIs, Types, And Macros

There are no functions, structs, classes, enums, variables, callbacks, allocation sites, or locks in this line range. The public interface is the generated macro namespace:

- `<REGISTER>__<FIELD>__SHIFT`: field bit position within the register value.
- `<REGISTER>__<FIELD>_MASK`: field bit mask, normally with an `L` suffix.

Major macro families in this chunk:

- `MPCC_OGAM0_*`: tail of output gamma RAM B metadata for MPCC instance 0, including RGB offsets, 34 segmented-region descriptors, gamut-remap format/mode status, and coefficient banks A/B.
- `MPCC_OGAM1_*`: complete output gamma metadata for MPCC instance 1. It includes `MPCC_OGAM_CONTROL`, LUT index/data/control, RAM A and RAM B start/end/base/slope/offset fields for B/G/R, region pairs `0_1` through `32_33`, gamut-remap coefficient format/mode fields, and gamut-remap matrix coefficients `C11` through `C34` for banks A and B.
- `MPC_*` configuration: `MPC_CLOCK_CONTROL`, `MPC_SOFT_RESET`, CRC controls and results, performance event enable, bypass background color, host-read throttling, DPP/OPP/MPCC/DWB pending-status fields, vupdate lock sets for two pipes, and `MPC_DWB0_MUX`.
- `MPC_OUT0_*` and `MPC_OUT1_*`: output mux selection, rate/flow-control fields, denorm clamp min/max values, output CSC coefficient format, CSC mode/current status, and banks A/B of output CSC matrix coefficients.
- `MPC_RMU*`: RMU mux and memory power controls, shaper LUT control/data/write-enable, shaper offsets/scales, RAM A/B segmented-region descriptors, 3D LUT mode/index/data/read-write control, output normalization factor, and output offsets.
- `DC_PERFMON15_*` and `DC_PERFMON16_*`: display performance-counter selector, threshold, state, interrupt/status/ack, current value, and high/low result fields for MPC and HPO perfmon blocks.
- `HPO_TOP_CLOCK_CONTROL`: HPO display clock gate/test-clock fields.
- `ABM0_*` and `ABM1_*`: backlight/PWM levels, ABM enable and sample-rate controls, register locks, ACE offset/slope and thresholds, histogram/luma statistics controls and readback fields, sample-rate counters, histogram bin shift/index fields, histogram result registers 1 through 24, and master-lock fields.
- `CORB_*` and the first `RIRB_LOWER_BASE_ADDRESS` marker: HDA command output ring buffer write/read pointer, reset, control, memory-error status, and size/capability fields.

Consumers normally do not reference every generated name manually. They use token-pasting helpers such as `SF(register, field, __SHIFT)`, `SF(register, field, _MASK)`, `SR(register)`, and `SRII(register, block, instance)` to initialize per-block register, shift, and mask tables.

## Control Flow

This header has no runtime control flow. Runtime sequencing is supplied by AMD Display Core:

1. DCN 3.0.3 resource and hardware-block code include the matching offset and shift/mask headers.
2. Register-list macros paste register names into MMIO offset symbols, while field-list macros paste register and field names into this header's `__SHIFT` and `_MASK` symbols.
3. Constructors for MPC, ABM, audio, and related display blocks receive static register/shift/mask tables.
4. Modeset, color-management, backlight, perfmon, and display-audio paths call helpers such as `REG_SET`, `REG_UPDATE`, `REG_GET`, or indexed register accessors.
5. Those helpers use the masks and shifts in this chunk to read/modify/write only the intended hardware bits.

The macro values do not encode ordering. Consumers still must handle sequencing around clocks, power, soft reset, double-buffer/update locks, LUT bank selection, frame-start updates, histogram readback, interrupt clear/ack, and HDA DMA ring setup.

## State And Persistence Behavior

This chunk stores no software state and persists nothing itself. It describes hardware state in DCN 3.0.3 display registers.

Important state represented here includes:

- Color pipeline configuration: MPCC output gamma modes, LUT bank selection, RAM A/B segmented PWL regions, gamut remap matrices, output CSC matrices, denorm clamps, RMU shaper LUTs, and RMU 3D LUT contents.
- Composition and routing state: MPC output muxes, DWB muxing, DPP/OPP/MPCC/DWB pending status, rate/flow-control state, vupdate locks, and soft-reset bits.
- Power and clock state: MPC display-clock gates, RMU memory power controls, and HPO clock-control fields.
- Diagnostics: MPC CRC enable/source/result fields and perfmon counter configuration, states, current values, interrupts, and high/low readback values.
- Backlight and adaptive brightness state: PWM user/ambient/target/current/final/min duty values, ABM enable/bypass controls, ACE curves, luma statistics, histogram bins/results, sample-rate frame counters, missed-frame flags, and lock/update-pending flags.
- Audio controller state: HDA CORB pointers, reset/control bits, memory-error status, and CORB sizing/capability information.

Persistence is hardware-defined. Configuration fields generally remain until overwritten, reset, power-gated, or restored after suspend/resume. Status, pending, current-mode, current-mux, CRC, perfmon, histogram, missed-frame, memory-error, and interrupt-like fields may be read-only, sticky, write-one-to-clear, self-clearing, or latch-on-read depending on the register. This generated header only supplies bit positions; it does not express access type or side effects.

## Dependencies And Integration Points

This chunk must stay synchronized with:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_3_offset.h`, which supplies matching register offsets and base-index constants.
- AMD's generated DCN 3.0.3 register database.
- Display Core register-helper macros that consume these generated names through token pasting.

Relevant integration points in the inspected tree include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/mpc/dcn30/dcn30_mpc.h`, where `MPC_REG_LIST_DCN3_0`, `MPC_OUT_MUX_REG_LIST_DCN3_0`, `MPC_RMU_GLOBAL_REG_LIST_DCN3AG`, and `MPC_RMU_REG_LIST_DCN3AG` enumerate many `MPCC_OGAM`, `MPC_OUT`, and `MPC_RMU` registers covered by this chunk.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/mpc/dcn32/dcn32_mpc.h`, where `MPC_COMMON_MASK_SH_LIST_DCN32` and related field-list macros use `SF(...)` against several field names present here, including output CSC, denorm, MPCC output gamma, DWB mux, and flow-control fields.
- ABM/backlight hardware code and resource tables that use the `ABM0_*` and `ABM1_*` field masks for PWM, ACE, histogram, luma-stat, and lock/update programming.
- Display audio/HDA code that uses the Azalia CORB/RIRB masks together with the matching offsets to manage command and response DMA rings.

The generated constants are compile-time data for hardware access. They are not a standalone abstraction and are meaningful only with the matching register offsets, register-block tables, and access helpers.

## Risks And Edge Cases

- Mask/shift drift is the main risk. A wrong generated value can compile cleanly while writing or reading the wrong hardware bits.
- This chunk is artificially bounded. It starts after the beginning of `MPCC_OGAM0` and ends at the start of the `RIRB_LOWER_BASE_ADDRESS` block, so adjacent chunks are needed for complete file-level reasoning.
- The repeated RAM A/RAM B and RGB region tables are copy-sensitive. Prefix, instance, channel, bank, or region-number mistakes can affect only one color channel, one LUT bank, or one MPCC instance.
- Double-buffered and current-status fields are easy to misuse. `*_CURRENT`, update-pending, frame-start, lock, and ignore-master-lock fields require correct sequencing around vblank/frame-start updates.
- Color LUT and matrix fields are user-visible. Bad masks can produce wrong gamma, gamut remap, CSC, denorm clamp, HDR/SDR conversion, or 3D LUT behavior without causing an obvious kernel failure.
- Soft reset, clock gating, and memory-power fields can disrupt active display hardware if written outside the intended power-sequencing path.
- CRC and perfmon fields mix configuration, status, thresholds, interrupt status, and acknowledgement bits. Treating ack or sticky status masks as ordinary configuration can lose diagnostics or leave interrupts asserted.
- ABM histogram/luma fields include readback-in-progress, missed-frame, clear, and lock bits. Incorrect access ordering can sample inconsistent brightness statistics or miss frame-boundary updates.
- HDA CORB fields manage DMA ring state. Incorrect pointer, reset, enable, or memory-error handling can break display-audio command transport.

## Test Signals

Useful validation signals for changes touching this generated data include:

- AMDGPU/DC display build coverage for the DCN 3.0.3 target; token-pasting users catch missing or renamed generated macros at compile time.
- Modeset and color-management tests on matching hardware: output gamma, gamut remap, output CSC, denorm clamp, RMU shaper LUT, and 3D LUT programming should produce expected visual output.
- CRC/perfmon diagnostics: enabling MPC/HPO counters or CRC capture should yield stable, expected register readback and interrupt/ack behavior.
- Backlight and ABM tests: brightness changes, ambient/ABM level updates, ACE behavior, luma statistics, histogram bins, missed-frame flags, and lock/update-pending bits should behave across frame boundaries.
- Suspend/resume and runtime power-management tests covering LUTs, backlight state, RMU memory power, HPO/MPC clocking, and audio ring state restoration.
- Display-audio smoke tests on HDMI/DP sinks to verify HDA command transport still works when CORB/RIRB registers are initialized and reset.

### subset-b-001792: lines 27133-29716

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_3_sh_mask.h lines 27133-29716

## Scope

This chunk covers a generated AMD DCN 3.0.3 shift/mask header region. It contains C preprocessor constants only: register grouping comments plus `__SHIFT` and `_MASK` `#define` entries. There are no C functions, structs, enums, storage objects, or direct MMIO operations in this slice.

The range starts in the middle of the HDA/Azalia RIRB base-address definitions, covers HDA response-ring, immediate-command, DMA-position, wall-clock, legacy VGA indexed-register, Azalia F2 codec, descriptor, sink-info, CRC, input-codec, root-codec, stream-latency, and AZF0 endpoint 0 field definitions, then ends inside AZF0 endpoint 1 audio descriptor definitions. Adjacent chunks are needed for complete coverage of the opening RIRB lower-base register and the remainder of endpoint 1 plus later endpoints.

## Purpose

The purpose of this header region is to define bit positions and masks for DCN 3.0.3 display audio and legacy display-adapter register surfaces. AMD display and audio code uses these generated constants through register-helper macros so implementation files can address hardware fields symbolically instead of hard-coding bit shifts and masks.

The covered hardware areas are:

- HDA/Azalia controller response path: RIRB base address, write pointer, interrupt count, RIRB control/status/size, immediate command/response registers, DMA position buffer address, and wall-clock counter alias.
- Azalia endpoint immediate command data/index windows for output and input endpoints.
- Legacy VGA sequencer, CRTC, graphics-controller, and attribute-controller indexed register field layouts.
- Azalia F2 codec converter and pin widgets for output and input paths, including audio format, stream/channel mapping, digital converter state, GTC embedding, widget capabilities, pin capabilities, pin sense, speaker/channel allocation, audio descriptors, multichannel enable/mute/channel IDs, lipsync/HBR, channel-status overrides, LPIB snapshots, format-changed status, and remote keepalive.
- Endpoint descriptor and sink-info indexed blocks that expose HDMI/DP audio descriptors, ELD-like sink metadata, manufacturer/product IDs, port IDs, and sink description bytes.
- Azalia input and output CRC result banks for channels 0-7.
- Azalia F2 root codec function parameters and controls, including vendor/device ID, revision, subordinate-node count, power state, subsystem ID, converter synchronization, reset, group type, size/rate capabilities, stream formats, and power states.
- AZF0 stream 0-15 FIFO and latency counter fields.
- AZF0 endpoint 0 full converter/pin/audio-enable interrupt surface and the beginning of AZF0 endpoint 1.

This is a hardware contract file. The behavioral importance is that each mask and shift must match the DCN 3.0.3 register database and the matching offset header; the code that consumes it often compiles even if a numeric value is wrong, but it will then program or read the wrong hardware bits.

## Important APIs, Types, And Constants

There are no callable APIs or concrete types in this chunk. The exported interface is the generated macro naming contract:

- `<REGISTER>__<FIELD>__SHIFT` gives the field bit offset.
- `<REGISTER>__<FIELD>_MASK` gives the field mask.
- Address-block comments such as `// addressBlock: azendpoint_f2codecind` and register comments such as `//AZALIA_F2_CODEC_PIN_CONTROL_CHANNEL_ALLOCATION` preserve the hardware grouping used by register-table and indirect-register macros.

Important register families in this chunk include:

- `RIRB_*`, `RESPONSE_INTERRUPT_COUNT`, `IMMEDIATE_COMMAND_*`, `IMMEDIATE_RESPONSE_INPUT_INTERFACE`, `DMA_POSITION_*`, and `WALL_CLOCK_COUNTER_ALIAS`, which define HDA command/response transport fields. Notable fields include RIRB base-address alignment masks, write-pointer reset, response and overrun interrupt bits, RIRB DMA enable, immediate-command busy/result-valid status, and DMA-position buffer enable/address fields.
- `AZENDPOINT_IMMEDIATE_COMMAND_*` and `AZENDPOINT_IMMEDIATE_COMMAND_INPUT_*`, which define endpoint-local immediate command data/index windows with 32-bit data payloads and 17-bit index fields.
- `SEQ00` through `SEQ04`, `CRT00` through `CRT22`, `GRA00` through `GRA08`, and `ATTR00` through `ATTR14`, which define legacy VGA indexed register fields for resets, clocking, map enables, font selection, timing totals, blank/sync positions, cursor and display start, line compare, graphics read/write modes, chain/odd-even behavior, attribute palette entries, mode control, overscan, color plane enable, pixel panning, and color select.
- `AZALIA_F2_CODEC_CONVERTER_CONTROL_CONVERTER_FORMAT`, which packs number of channels, bits per sample, sample base divisor/multiple/rate, and stream type.
- `AZALIA_F2_CODEC_CONVERTER_CONTROL_CHANNEL_STREAM_ID`, which maps the codec channel ID and HDA stream ID.
- `AZALIA_F2_CODEC_CONVERTER_CONTROL_DIGITAL_CONVERTER`, `_2`, and `_3`, which define digital audio enable/status bits such as `DIGEN`, `V`, `VCFG`, `PRE`, `COPY`, `NON_AUDIO`, `PRO`, `L`, channel-status `CC`, and silent-stream `KEEPALIVE`.
- `AZALIA_F2_CODEC_CONVERTER_CONTROL_GTC_EMBEDDING` and the AZF0 endpoint GTC registers, which define presentation-time embedding enable, offset-changed, group selection, and GTC counter delta/min/max fields.
- `AZALIA_F2_CODEC_*_PARAMETER_AUDIO_WIDGET_CAPABILITIES`, `*_SUPPORTED_SIZE_RATES`, `*_STREAM_FORMATS`, and `*_PARAMETER_CAPABILITIES`, which expose codec/widget capability bitmaps such as format override, stripe, unsolicited response, connection list, digital, power control, LR swap, widget type, HDMI/DP pin capabilities, VREF, and EAPD.
- `AZALIA_F2_CODEC_PIN_CONTROL_*` and `AZALIA_F2_CODEC_INPUT_PIN_CONTROL_*`, which define pin widget control and response data: pin sense/presence, configuration default fields, speaker allocation, channel allocation, downmix info, audio descriptors, multichannel enables, HBR, LPIB snapshots, input status, infoframe, channel status, and format-changed reasons/responses.
- `AZALIA_F2_PIN_CONTROL_CODEC_CS_OVERRIDE_0` through `_8`, which define IEC 60958 channel-status override fields for mode, source number, clock accuracy, word length, sampling frequency, CGMS-A, and per-channel numbers.
- `AUDIO_DESCRIPTOR0` through `AUDIO_DESCRIPTOR13`, which pack EDID/CTA-style audio descriptor fields for maximum channels, format code, supported frequencies, descriptor byte 2, and stereo-frequency overrides.
- `AZALIA_INPUT_CRC0/1_CHANNEL<n>` and `AZALIA_CRC0/1_CHANNEL<n>`, which expose 32-bit CRC readback fields per audio channel.
- `AZF0STREAM<n>_AZALIA_FIFO_SIZE_CONTROL`, `LATENCY_COUNTER_CONTROL`, `WORSTCASE_LATENCY_COUNT`, `CUMULATIVE_LATENCY_COUNT`, and `CUMULATIVE_REQUEST_COUNT`, repeated for streams 0-15, which expose FIFO bounds, maximum latency support, counter reset, and 32-bit latency/request counters.
- `AZF0ENDPOINT0_AZALIA_F0_*` and `AZF0ENDPOINT1_AZALIA_F0_*`, which are endpoint-instance-prefixed versions of the converter and pin register surfaces. Endpoint 0 is covered through audio enable/status and interrupt-status registers; endpoint 1 is covered from converter/widget capability through audio descriptor 5 at the end of the chunk.

Related semantic values live outside this header. Generated enum headers such as `soc24_enum.h` and older ASIC enum headers define values for fields such as audio sample sizes/rates, stream type, digital converter bits, RIRB size/reset, HBR, downmix, and descriptor format codes. This file only defines bit placement.

## Control Flow

This chunk has no runtime control flow. Its effective control flow is compile-time macro expansion into register-helper and indirect-register operations:

1. DCN 3.0.3 display code includes `dcn_3_0_3_sh_mask.h` with the matching `dcn_3_0_3_offset.h`.
2. Resource and audio register-list macros bind generated register and field names into register, shift, and mask tables. In this tree, `dcn303_resource.c` includes this header and uses field-list entries such as `SF(AZF0ENDPOINT0_AZALIA_F0_CODEC_ENDPOINT_INDEX, AZALIA_ENDPOINT_REG_INDEX, mask_sh)` and `SF(AZF0ENDPOINT0_AZALIA_F0_CODEC_ENDPOINT_DATA, AZALIA_ENDPOINT_REG_DATA, mask_sh)`.
3. Runtime code in the display audio layer uses helper macros such as `REG_SET`, `REG_UPDATE`, `REG_READ`, `AZ_REG_READ`, and `AZ_REG_WRITE`.
4. The helper layer uses the generated shifts and masks to construct MMIO or indirect-register reads/writes for the selected Azalia controller, endpoint, stream, or indexed codec register.

The runtime consumers provide the real flow. Typical audio flows write an endpoint index, write or read the endpoint data register, update pin/sink/audio descriptor fields from display sink information, configure converter format and channel allocation, set HBR/lipsync/status bits, and enable or disable audio when a connector/stream changes. HDA command flows use RIRB/immediate-command fields to transport codec verbs and responses. Stream-latency consumers reset and read latency counters. This header only supplies field layout for those sequences.

## State And Persistence Behavior

The header itself stores no state and persists no data. It describes stateful hardware registers:

- RIRB base, write pointer, size, DMA-enable, interrupt-enable, and status fields persist HDA response-ring configuration until driver reprogramming, controller reset, power transition, or ASIC reset.
- Immediate-command busy/result-valid fields reflect transient command execution state. The command write payload, codec address, endpoint index, and endpoint data registers are used as short-lived command windows rather than durable software state.
- DMA position buffer base/enable and wall-clock alias fields participate in audio position reporting and timing. Bad base-address alignment or enable bits can break position reporting without necessarily breaking display output.
- Legacy VGA indexed registers persist adapter compatibility state such as timing, attribute palette, plane routing, cursor, and text/graphics mode controls. Modern DC paths may rarely touch these fields, but the masks remain part of the ASIC register contract.
- Codec converter and pin control fields persist audio format, stream/channel routing, digital converter state, HBR enable, channel allocation, speaker allocation, sink capabilities, sink info, and channel-status override values used by HDMI/DP audio presentation.
- Capability and parameter registers represent hardware-advertised state. This header does not encode read-only versus writable direction, so capability fields appear as ordinary masks.
- LPIB, LPIB timer, CRC, latency, cumulative request, and worst-case latency registers expose counters or snapshots whose values change as audio traffic flows.
- GTC embedding and counter-delta fields persist presentation-time embedding configuration and measurement state for audio/video timing correlation.
- Audio enable/status and enabled/disabled/format-changed interrupt status fields persist or latch endpoint audio state changes until acknowledged according to the hardware's interrupt semantics.

Persistence is hardware-defined. Writable control fields remain until later driver updates, endpoint reset, display/audio power-state transitions, or full ASIC reset. Status and counter fields can change asynchronously with hardware, audio DMA, hotplug, and codec-response activity.

## Dependencies And Integration Points

This chunk depends on several generated and handwritten AMD display/audio components staying synchronized:

- The matching `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_3_offset.h` supplies MMIO and indirect-register offsets for the register names described here.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn303/dcn303_resource.c` includes the DCN 3.0.3 offset and shift/mask headers and builds the audio register/field table used by the DC resource layer.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn303.c` includes the same DCN 3.0.3 generated headers for DMUB-side register access.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce/dce_audio.h` defines audio register structures and macros for endpoint index/data and Azalia fields; `dce_audio.c` uses `AZ_REG_READ`, `AZ_REG_WRITE`, `REG_SET`, and related helpers to program audio descriptors, channel allocation, HBR, lipsync, sink info, hotplug control, power capabilities, and endpoint register windows.
- Older non-DC display paths such as `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/dce_v6_0.c`, `dce_v8_0.c`, and `dce_v10_0.c` show the same Azalia endpoint-index/data programming model and direct use of Azalia field masks/shifts, which helps validate the intended semantics even when DCN 3.0.3 uses different generated names.
- Generated enum headers, including `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/soc24_enum.h` and earlier ASIC enum files, provide symbolic values for many fields in this chunk. This shift/mask header does not define those values.
- The Linux HDA/HDMI audio stack, DRM connector hotplug flow, EDID/ELD parsing, DC stream state, and DMUB/display power management indirectly depend on these fields being correct when enabling audio over HDMI or DisplayPort.

The main integration contract is preprocessor naming. If a register or field macro is missing or renamed, table construction generally fails at compile time. If a mask or shift is numerically wrong, the driver can compile and then silently program the wrong endpoint, audio descriptor, interrupt bit, or stream counter field.

## Risks And Edge Cases

- The line range starts after the `RIRB_LOWER_BASE_ADDRESS` register comment and ends inside endpoint 1 audio descriptors. The merge lane must combine adjacent chunks before making whole-file statements about HDA RIRB coverage or all AZF0 endpoint instances.
- HDA base-address fields intentionally reserve or mask low alignment bits. Treating the lower base as a full 32-bit address instead of using `RIRB_LOWER_BASE_ADDRESS_MASK` or `DMA_POSITION_LOWER_BASE_ADDRESS_MASK` can create unaligned DMA state.
- RIRB status and control bits are small and adjacent. A wrong overrun/response interrupt bit can cause lost codec responses, interrupt storms, or missed overrun diagnostics.
- Immediate-command status has separate busy and result-valid bits. Polling the wrong bit can read stale responses or issue overlapping codec verbs.
- Endpoint index masks differ by block: top-level immediate command index fields include 16-bit or 17-bit windows depending on path. Using the wrong indexed-register width can address the wrong codec or endpoint register.
- Legacy VGA register fields are byte-sized and heavily packed. Accidental reuse of these masks outside their indexed-register path can corrupt unrelated VGA state.
- F2 codec output and input register families share many field names but have different prefixes. Mixing output pin fields with input pin fields can compile if names are manually expanded elsewhere, but would program the wrong direction's widget.
- Audio descriptor registers repeat with nearly identical layouts. Descriptor 0 includes `SUPPORTED_FREQUENCIES_STEREO` in several endpoint-specific blocks while later descriptors may not; assuming one descriptor layout for all entries risks overwriting high bits.
- Multichannel enable registers use paired and per-channel variants (`MULTICHANNEL01_ENABLE`, `MULTICHANNEL23_ENABLE`, then `MULTICHANNEL1_ENABLE`, `MULTICHANNEL3_ENABLE`, and so on). Confusing the pair fields with single-channel fields can mute or map the wrong channels.
- IEC 60958 channel-status override fields are spread across nine small registers. A wrong mask can change copy/pro/audio/sample-rate signaling without obvious driver errors, causing sink compatibility or compliance problems.
- Sink-info and sink-description fields are plain 32-bit or byte-like data fields. Endianness and packing assumptions in higher-level ELD/EDID handling must match the register definitions.
- CRC and latency counters are readback/status surfaces. The shift/mask header does not mark them as read-only, so accidental write paths are not prevented by the macro interface.
- AZF0 stream latency blocks are repeated 16 times with instance numbers embedded in macro names. Copy/paste or generation mistakes are easy to miss because neighboring streams look identical.
- Endpoint 0 and endpoint 1 register names are nearly identical except for the instance prefix. Endpoint selection bugs can appear as audio only working on one connector or one encoder path.
- Cross-generation reuse is risky. DCN 3.0.0, 3.0.2, 3.0.3, and later DCN headers contain similar Azalia names, but the offset header and shift/mask header must match the target ASIC.

## Test Signals

Useful validation is mostly build-time and hardware-integration oriented:

- Compile the DCN 3.0.3 AMD display driver paths that include this header, especially `dcn303_resource.c` and `dmub_dcn303.c`, to catch missing or renamed `__SHIFT`/`_MASK` macros in register-field table expansion.
- Preprocess representative `dce_audio.c` and DCN 3.0.3 resource objects to confirm that Azalia endpoint index/data fields resolve to the expected generated constants.
- Compare this chunk against the matching DCN 3.0.3 register database and `dcn_3_0_3_offset.h` to verify field/register coverage, especially the repeated AZF0 stream 0-15 and endpoint 0/1 blocks.
- Exercise HDMI and DisplayPort audio enable/disable on DCN 3.0.3 hardware. Expected signals are correct audio enumeration, stable hotplug behavior, and correct audio-enabled/audio-disabled interrupt status.
- Test PCM formats across channel counts, sample rates, and bits per sample; failures can implicate converter format, channel/stream ID, descriptor, or supported size/rate masks.
- Exercise HBR/non-PCM audio and verify the HBR enable/capable fields, stream type, coding type, and audio descriptor signaling.
- Validate speaker allocation and channel allocation using sinks with stereo, multichannel LPCM, and compressed-format capabilities; watch for wrong speaker map or muted channels.
- Check ELD/sink-info programming by comparing driver-visible sink metadata and hardware register readback for manufacturer/product IDs, port IDs, sink description, and audio descriptors.
- Run suspend/resume and display power-transition tests with audio active, because endpoint state, RIRB/DMA-position state, and stream latency counters may be reset or stale across power changes.
- Use register readback or debug traces around `RIRB_STATUS`, `IMMEDIATE_COMMAND_STATUS`, `AZALIA_F2_CODEC_PIN_CONTROL_FORMAT_CHANGED`, endpoint audio interrupt-status fields, and AZF0 stream latency counters to verify that status bits move through the expected masks.
- On hardware or simulation that exposes CRC result registers, compare audio CRC channels before and after format/channel changes to detect wrong channel mapping or stale endpoint programming.

## Open Cross-Chunk Questions

- The later merge lane should combine this with the previous chunk to recover the full `RIRB_LOWER_BASE_ADDRESS` context and any earlier HDA/CORB/controller fields.
- The later merge lane should combine this with the next chunk to document complete `AZF0ENDPOINT1` coverage and the remaining endpoint instances expected for DCN 3.0.3.
- Whole-file analysis should verify that the endpoint and stream instance counts in this shift/mask header match the DCN 3.0.3 offset header and the DCN audio resource register-list macros.

### subset-b-001793: lines 29717-32085

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_3_sh_mask.h lines 29717-32085

## Scope

This chunk is a generated AMD DCN 3.0.3 shift/mask header slice. It contains only preprocessor constants and generated register grouping comments; there are no C functions, structs, enums, variables, includes, or executable statements in this range.

The slice starts inside the `AZF0ENDPOINT1_AZALIA_F0_CODEC_PIN_CONTROL_AUDIO_DESCRIPTOR5` register, covers the remainder of endpoint 1 pin/audio status fields, then covers complete `azf0endpoint2_endpointind`, `azf0endpoint3_endpointind`, and `azf0endpoint4_endpointind` blocks. It then enters `azf0endpoint5_endpointind` and ends after the masks for `AZF0ENDPOINT5_AZALIA_F0_CODEC_PIN_CONTROL_MULTICHANNEL_ENABLE2`. The requested range contains 2,049 `#define` lines for register field shifts and masks.

Although the repository path is under a local `ceph-client` source mirror, this file is AMDGPU Display Core hardware metadata for DCN display audio, not distributed filesystem logic.

## Purpose

This region publishes the bit layout for DCN 3.0.3 Azalia/HD-audio endpoint-indirect registers. Runtime display and audio code uses these macros with the matching offset/index definitions to program audio converter widgets and pin widgets behind display outputs. The generated names encode a register and field contract:

- `<REGISTER>__<FIELD>__SHIFT` gives the field bit offset.
- `<REGISTER>__<FIELD>_MASK` gives the field mask.
- Address block comments such as `// addressBlock: azf0endpoint2_endpointind` preserve the generated grouping for endpoint instances.

The main value is keeping audio register users symbolic. Code can construct register tables or compose values for fields such as converter format, stream/channel ID, speaker allocation, audio descriptors, hot-plug audio enablement, IEC 60958 channel-status overrides, LPIB snapshots, and audio interrupt status without embedding raw bit positions.

## Important APIs, Types, And Constants

There are no callable APIs or local types. The exported API is the macro namespace for `AZF0ENDPOINT<n>_AZALIA_F0_*` fields.

Important register families in this chunk:

- Endpoint 1 tail: audio descriptor 5 masks plus descriptors 6-13, multichannel controls, lipsync/HBR response fields, sink info, hot-plug control, unsolicited response forcing, default configuration response, IEC 60958 channel-status override fields, LPIB snapshot/readback fields, coding type, format-changed status, wireless display identification, remote keepalive, audio enable status, and enabled/disabled/format-changed interrupt status.
- Endpoints 2-4 complete blocks: converter widget capability parameters, converter format, channel/stream ID, digital converter controls, supported stream formats and rates, stripe/ramp/GTC embedding controls, GTC counter delta/min/max fields, pin widget capabilities, unsolicited response controls, pin-sense/widget-control fields, speaker/channel allocation, audio descriptors 0-13, multichannel controls, sink info, hot-plug audio controls, IEC 60958 override fields, LPIB state, format-change state, keepalive, and audio interrupt status.
- Endpoint 5 partial block: converter and pin capability/control fields through audio descriptors, multichannel enable, lipsync/HBR, sink info, hot-plug, unsolicited response force, default configuration response, and `MULTICHANNEL_ENABLE2`; the following endpoint 5 fields continue in the next chunk.

Notable field groups include:

- Audio descriptor fields: `MAX_CHANNELS`, `SUPPORTED_FREQUENCIES`, `DESCRIPTOR_BYTE_2`, and for descriptor 0 the stereo-frequency byte in adjacent context. These are the ELD/SAD-style capability payloads exposed through the codec pin.
- Converter format fields: channel count, sample rate/base/multiplier/divider, bits per sample, stream type, and digital converter flags such as validity, VCFG, pre-emphasis, copy protection, non-audio, professional mode, and digital converter enablement.
- Stream routing fields: `CHANNEL_ID`, `STREAM_ID`, stripe control, ramp rate, GTC embedding enable/status bits, and GTC counter delta values.
- Pin capability and response fields: presence detect, ELD valid, connection list, HDMI/DP support, HBR, unsolicited response enable/tag, pin sense, widget control, speaker allocation, lipsync, sink manufacturer/product IDs, port IDs, and sink description bytes.
- Multichannel fields: paired-channel `MULTICHANNEL01/23/45/67` controls and odd-channel `MULTICHANNEL1/3/5/7` controls, each with enable, mute, and channel ID fields.
- Status/interrupt fields: audio enable status, audio enabled/disabled interrupt enable/status/ack, audio format changed enable/status/ack, and format-change sticky/current fields.

## Control Flow

This header has no runtime control flow. Its effective control flow is compile-time macro expansion plus endpoint-indirect register access performed elsewhere:

1. DCN303 code includes `dcn_3_0_3_offset.h` and this shift/mask header.
2. Resource code builds audio and AFMT register tables. In `drivers/gpu/drm/amd/display/dc/resource/dcn303/dcn303_resource.c`, `DCE120_AUD_COMMON_MASK_SH_LIST(__SHIFT)` and `DCE120_AUD_COMMON_MASK_SH_LIST(_MASK)` populate `struct dce_audio_shift` and `struct dce_audio_mask`; `dcn303_create_audio()` then passes those tables to `dce_audio_create()`.
3. Runtime audio helpers use the register tables and field masks with `REG_SET`, `REG_UPDATE`, `REG_GET`, endpoint index/data writes, or equivalent helpers to program converter and pin-widget state.
4. Hardware sequencing, such as enabling audio after link setup, updating ELD/SAD-derived descriptors, configuring speaker allocation, acknowledging audio interrupts, and handling hotplug or format changes, is implemented in Display Core audio and stream encoder code. This chunk only supplies bit positions.

Direct DCN303 include sites in this tree include:

- `drivers/gpu/drm/amd/display/dc/resource/dcn303/dcn303_resource.c`
- `drivers/gpu/drm/amd/display/dc/irq/dcn303/irq_service_dcn303.c`
- `drivers/gpu/drm/amd/display/dmub/src/dmub_dcn303.c`

The broader Azalia field contract is also visible in older DCE audio code paths, which use the same style of `AZALIA_F0_CODEC_*` masks for HDMI/DP audio setup. Those older files are useful behavioral references, but this chunk is the DCN 3.0.3 generated variant.

## State And Persistence Behavior

The file stores no software state and persists nothing. It describes MMIO-backed hardware state for display audio endpoints:

- Converter state: stream format, stream/channel IDs, digital converter enable/status flags, supported stream formats and rates, ramp/stripe policy, and GTC embedding counters.
- Pin state: pin capabilities, pin sense, unsolicited response configuration, widget control, speaker allocation, audio descriptors, HBR/lipsync response, sink metadata, hot-plug audio enablement, and default configuration response.
- Multichannel state: per-channel enable, mute, and channel mapping for paired and odd-channel multichannel modes.
- IEC 60958/channel-status state: override mode, source number, clock accuracy, word length, sampling frequency, original sampling frequency, CGMS-A, copyright, additional format info, category code, generation level, and validity-bit override.
- Runtime status state: audio enabled/disabled and format-changed interrupt status/ack bits, current and sticky format-changed indications, LPIB snapshots, LPIB timer snapshots, and remote keepalive.

Persistence is hardware-defined. Programmed fields usually remain until another MMIO write, display audio teardown, modeset, suspend/resume, power gating, or ASIC reset. Status, interrupt, ack, snapshot, pin-sense, hotplug, keepalive, and format-change fields can be asynchronous, sticky, self-clearing, or write-one-to-clear depending on the register. This generated header does not encode access permissions or side effects; callers must follow the audio block programming model.

## Dependencies And Integration Points

This chunk must stay synchronized with:

- `dcn_3_0_3_offset.h`, which provides the matching register offsets and endpoint-indirect addresses.
- DCN303 base address data from `sienna_cichlid_ip_offset.h` and associated SOC/DCN register helper macros.
- Display Core audio tables in `dcn303_resource.c`, especially `audio_regs`, `audio_shift`, `audio_mask`, and `dcn303_create_audio()`.
- Shared DCE/DCN audio code that consumes `struct dce_audio_registers`, `struct dce_audio_shift`, and `struct dce_audio_mask` to configure HDMI/DP audio and codec endpoint state.
- Stream encoder and AFMT code paths that generate HDMI/DP audio packets and rely on endpoint audio state matching stream timing and sink capabilities.
- IRQ and hotplug flows that observe audio enabled/disabled, format-changed, HPD, and unsolicited-response behavior.
- DMUB register metadata generation for DCN303, which includes this header for shared field mask/shift definitions.

The direct contract is preprocessor name compatibility. Missing or renamed macros generally fail at build time when register tables expand. Incorrect numeric masks or shifts are more dangerous because the build can pass while the driver programs the wrong bits.

## Risks And Edge Cases

- The chunk boundaries are artificial. It starts after the shifts for endpoint 1 `AUDIO_DESCRIPTOR5` and ends before later endpoint 5 fields such as multichannel mode and IEC 60958 overrides. Whole-file reconciliation must merge adjacent chunks before claiming complete endpoint 1 or endpoint 5 coverage.
- Repetition across endpoints 1-5 is copy-sensitive. A single shifted bit or mask typo can affect only one display audio endpoint, making failures connector- or pipe-specific.
- Endpoint-indirect access is stateful. Consumers must write the correct endpoint index and then read/write endpoint data; a correct field mask still causes bad behavior if paired with the wrong endpoint instance or indirect register offset.
- Audio descriptor and speaker allocation fields are sink-capability sensitive. Bad masks can advertise invalid channel counts, unsupported sampling rates, wrong speaker layouts, or wrong compressed-audio support.
- Hot-plug and unsolicited-response fields interact with display detection. Wrong enable/tag/payload masks can cause missing audio device notifications, hotplug storms, or stale userspace audio devices.
- Interrupt status and ack fields are easy to misuse because enable, status, and acknowledge bits share related register families. Mask drift can lose audio-enabled/disabled or format-changed events, or acknowledge the wrong condition.
- High-bit fields such as `AUDIO_ENABLED` at bit 31 and full-width LPIB/timer snapshots require unsigned-width-safe composition by callers.
- IEC 60958 override bits control externally visible audio metadata. Incorrect masks can produce subtle receiver compatibility issues even when PCM playback appears to work.
- GTC embedding and counter-delta fields affect audio/video synchronization. Incorrect programming can manifest as drift, lipsync errors, or timing-dependent failures rather than immediate link failure.
- Similar Azalia field names exist in DCE and other DCN generation headers. Cross-generation reuse must not assume identical bit layouts without checking the generated header for the target ASIC.

## Test Signals

Useful validation is mostly build-time, generated-header consistency, and hardware audio behavior:

- Build AMDGPU Display Core with DCN303 enabled to catch missing `AZF0ENDPOINT*` field names in `SF(...)`, audio table, IRQ, and DMUB expansions.
- Mechanically compare this chunk against the matching DCN 3.0.3 register database and `dcn_3_0_3_offset.h` to ensure every field belongs to a defined endpoint-indirect register.
- Check repeated endpoint blocks for structural consistency: endpoints 2-4 should have matching field sets, while endpoint 1 and endpoint 5 differences should line up with adjacent chunk boundaries rather than generator drift.
- Exercise HDMI and DisplayPort audio on hardware using multiple endpoint instances: hotplug, audio device enumeration, EDID/ELD-derived descriptor programming, stereo and multichannel PCM, compressed formats, HBR-capable sinks, and speaker allocation changes.
- Test audio enable/disable across modesets, connector unplug/replug, DPMS, suspend/resume, and stream reallocation.
- Validate format-change behavior by switching sample rates, channel counts, and bit depths while monitoring kernel logs and userspace audio device state.
- Check interrupt paths for audio-enabled, audio-disabled, and format-changed status/ack behavior; watch for stuck interrupts or missed notifications.
- Validate lipsync/GTC-related behavior with A/V playback, especially after link-rate changes or resume.
- For register-level tests, read back endpoint-indirect registers after programming and verify that fields occupy the expected bits without modifying adjacent status or ack bits.

## Cross-Chunk Notes

Adjacent chunks are required for complete coverage of `AZF0ENDPOINT1_AZALIA_F0_CODEC_PIN_CONTROL_AUDIO_DESCRIPTOR5` and the remainder of `AZF0ENDPOINT5_AZALIA_F0_*`. The final per-file document should merge this report with neighboring chunks before summarizing all Azalia endpoint instances or the full `dcn_3_0_3_sh_mask.h` generated ABI.

### subset-b-001794: lines 32086-34399

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_3_sh_mask.h lines 32086-34399

## Scope

This chunk covers 2,314 lines from the generated DCN 3.0.3 shift/mask header. It contains only preprocessor constants and generated grouping comments; there are no C functions, structs, enums, storage definitions, branches, loops, or local algorithms in this range.

The range is part of the AMD display Azalia function 0 register field map. It starts inside `AZF0ENDPOINT5_AZALIA_F0_CODEC_PIN_CONTROL_MULTICHANNEL_ENABLE2`, covers the tail of output endpoint 5, then covers complete output endpoint 6 and output endpoint 7 blocks, complete input endpoint 0 through input endpoint 3 blocks, and the beginning of input endpoint 4. It ends inside `AZF0INPUTENDPOINT4_AZALIA_F0_CODEC_INPUT_CONVERTER_CONTROL_DIGITAL_CONVERTER`, after `NON_AUDIO_MASK`; later masks for that register and the rest of input endpoint 4 continue in the next chunk.

The chunk contains 2,032 `#define` entries: 1,013 `__SHIFT` definitions and 1,019 `_MASK` definitions. Generated register-group comments identify 23 endpoint-5 groups, 71 endpoint-6 groups, 71 endpoint-7 groups, 23 groups each for input endpoints 0 through 3, and 4 early input-endpoint-4 groups.

## Purpose

This header slice gives DCN 3.0.3 display-audio code symbolic bit positions and masks for Azalia/HD-audio-style converter and pin registers. Runtime code can combine these constants with the matching offset/index header and AMD display register helper macros to read, update, or decode hardware fields without hard-coded bit arithmetic.

For output endpoint 5, the range covers the remaining pin-control fields: multichannel slots, IEC 60958 channel-status override registers, association and digital-output status, LPIB snapshot data, coding type, format-change status/acknowledgement, wireless-display identification, remote keepalive, audio enable state, and audio enabled/disabled/format-change interrupt status.

For output endpoints 6 and 7, the range maps the full endpoint field surface: converter capabilities, converter format, stream/channel routing, digital converter state, stream format/rate/size support, stripe/ramp/GTC timing controls, pin capabilities, unsolicited responses, pin sense, widget control, channel speaker allocation, audio descriptors, multichannel routing, lipsync, HBR, sink information, hot-plug state, forced unsolicited responses, default pin configuration, IEC channel-status overrides, LPIB snapshots, coding type, format-change state, wireless-display identification, remote keepalive, audio enable status, and audio interrupt status.

For input endpoints 0 through 3, the range maps the full input endpoint pattern: input converter capabilities and format controls, input stream/channel IDs, digital converter flags, supported stream formats and sample sizes/rates, input pin capabilities, unsolicited response state, input pin sense, widget enable, multichannel routing, HBR capability/enablement, channel allocation, hot-plug audio state, forced unsolicited responses, pin default configuration, LPIB snapshots, input activity/status controls, and infoframe fields. Input endpoint 4 is only partially present through the beginning of its digital converter register.

## Important APIs, Types, And Constants

There are no callable APIs or C types in this chunk. The exported interface is the generated preprocessor naming contract:

- `AZF0ENDPOINT<n>_...__<FIELD>__SHIFT` gives a field bit offset for an output endpoint indexed register.
- `AZF0ENDPOINT<n>_...__<FIELD>_MASK` gives the corresponding output endpoint field mask.
- `AZF0INPUTENDPOINT<n>_...__<FIELD>__SHIFT` and `_MASK` provide the same contract for input endpoint indexed registers.
- Comments such as `// addressBlock: azf0endpoint6_endpointind` and `//AZF0INPUTENDPOINT3_AZALIA_F0_CODEC_INPUT_PIN_CONTROL_INFOFRAME` group constants by generated address block and logical register.

Important output endpoint register families in this chunk include:

- `AZALIA_F0_CODEC_CONVERTER_PARAMETER_AUDIO_WIDGET_CAPABILITIES`, exposing widget attributes such as channel capability, amplifier presence, format override, stripe, processing widget, unsolicited response support, connection list, digital, power control, LR swap, widget delay, and widget type.
- `AZALIA_F0_CODEC_CONVERTER_CONTROL_CONVERTER_FORMAT`, mapping number of channels, bits per sample, sample base divisor, sample base multiple, sample base rate, and stream type.
- `AZALIA_F0_CODEC_CONVERTER_CONTROL_CHANNEL_STREAM_ID`, mapping channel ID and stream ID.
- `AZALIA_F0_CODEC_CONVERTER_CONTROL_DIGITAL_CONVERTER`, mapping `DIGEN`, validity/config/preemphasis/copy/non-audio/professional flags, category code, and keepalive.
- `AZALIA_F0_CODEC_CONVERTER_PARAMETER_STREAM_FORMATS` and `SUPPORTED_SIZE_RATES`, exposing supported stream formats, audio rate capabilities, and bit-depth capabilities.
- `AZALIA_F0_CODEC_CONVERTER_STRIPE_CONTROL`, `CONTROL_RAMP_RATE`, `CONTROL_GTC_EMBEDDING`, and `GTC_COUNTER_DELTA*`, mapping striping, ramp rate, GTC embedding enable, and GTC counter delta values.
- `AZALIA_F0_CODEC_PIN_PARAMETER_AUDIO_WIDGET_CAPABILITIES` and `AZALIA_F0_CODEC_PIN_PARAMETER_CAPABILITIES`, defining pin widget and physical pin capability fields such as HDMI/DP, EAPD, VREF, input/output capability, presence-detect, trigger, balanced I/O, and headphone drive.
- `AZALIA_F0_CODEC_PIN_CONTROL_CHANNEL_SPEAKER`, `AUDIO_DESCRIPTOR0` through `AUDIO_DESCRIPTOR13`, `MULTICHANNEL_ENABLE`, `MULTICHANNEL_ENABLE2`, and `MULTICHANNEL_MODE`, covering speaker/channel allocation, short-audio-descriptor bytes, channel enable/mute/channel-ID slots, and multichannel mode.
- `AZALIA_F0_CODEC_PIN_CONTROL_RESPONSE_LIPSYNC`, `RESPONSE_HBR`, and `SINK_INFO0` through `SINK_INFO8`, covering audio/video latency, HBR capable/enable bits, sink manufacturer/product identity, port ID, sink description bytes, connection information, and converter ID.
- `AZALIA_F0_CODEC_PIN_CONTROL_HOT_PLUG_CONTROL`, `UNSOLICITED_RESPONSE_FORCE`, and `RESPONSE_CONFIGURATION_DEFAULT`, mapping hot-plug clock/audio state, forced unsolicited response payloads, and default pin-configuration fields.
- `AZALIA_F0_PIN_CONTROL_CODEC_CS_OVERRIDE_0` through `_8`, defining IEC 60958 channel-status override values and override-enable fields for mode, category code, source number, clock accuracy, word length, sampling frequency, original sampling frequency, CGMS-A, MPEG surround, and channel numbers.
- `AZALIA_F0_CODEC_PIN_CONTROL_LPIB_SNAPSHOT_CONTROL`, `LPIB`, and `LPIB_TIMER_SNAPSHOT`, defining audio position and timer snapshot fields.
- `AZALIA_F0_CODEC_PIN_CONTROL_FORMAT_CHANGED`, `AUDIO_ENABLE_STATUS`, `AUDIO_ENABLED_INT_STATUS`, `AUDIO_DISABLED_INT_STATUS`, and `AUDIO_FORMAT_CHANGED_INT_STATUS`, defining format-change flags/reasons/responses and audio enable/disable/change interrupt flag/mask/type fields.

Important input endpoint register families include:

- `AZALIA_F0_CODEC_INPUT_CONVERTER_PARAMETER_AUDIO_WIDGET_CAPABILITIES`, `INPUT_CONVERTER_CONTROL_CONVERTER_FORMAT`, `INPUT_CONVERTER_CONTROL_CHANNEL_STREAM_ID`, `INPUT_CONVERTER_CONTROL_DIGITAL_CONVERTER`, `INPUT_CONVERTER_PARAMETER_STREAM_FORMATS`, and `INPUT_CONVERTER_PARAMETER_SUPPORTED_SIZE_RATES`, mirroring converter-side audio format, routing, capability, and digital metadata fields for input paths.
- `AZALIA_F0_CODEC_INPUT_PIN_PARAMETER_AUDIO_WIDGET_CAPABILITIES` and `INPUT_PIN_PARAMETER_CAPABILITIES`, defining input pin capability bits.
- `INPUT_PIN_CONTROL_UNSOLICITED_RESPONSE`, `RESPONSE_INPUT_PIN_SENSE`, and `WIDGET_CONTROL`, defining unsolicited-response tagging/enabling, impedance/presence sense, and input widget enable.
- `INPUT_PIN_CONTROL_MULTICHANNEL_ENABLE` and `MULTICHANNEL_ENABLE2`, packing enable, mute, and 4-bit channel IDs for input multichannel slots 0 through 7.
- `INPUT_PIN_CONTROL_RESPONSE_HBR`, `CHANNEL_ALLOCATION`, `HOT_PLUG_CONTROL`, `UNSOLICITED_RESPONSE_FORCE`, `RESPONSE_CONFIGURATION_DEFAULT`, `LPIB*`, `INPUT_STATUS_CONTROL`, and `INFOFRAME`, defining HBR, channel allocation, hot-plug audio enable state, default configuration, position snapshots, input activity/channel layout, infoframe validity, and infoframe channel metadata.

## Control Flow

This chunk has no runtime control flow. Its effective flow is compile-time symbol resolution:

1. DCN 3.0.3 display code includes `dcn_3_0_3_sh_mask.h` with the matching DCN 3.0.3 offset header.
2. Register helper macros concatenate register and field tokens to resolve `__SHIFT` and `_MASK` symbols.
3. Runtime MMIO or indexed-register paths use the resolved constants to mask, shift, insert, or extract fields.

The declaration order mirrors the generated hardware address-block order. The range starts in endpoint 5 pin-control fields, enters `azf0endpoint6_endpointind`, then `azf0endpoint7_endpointind`, then `azf0inputendpoint0_inputendpointind` through `azf0inputendpoint4_inputendpointind`. Within most register groups, shift macros precede mask macros for the same fields.

## State And Persistence Behavior

The header itself stores no state and persists no data. It describes the layout of state held by DCN 3.0.3 display-audio hardware:

- Converter control fields represent programmed audio stream shape, channel/stream association, digital converter flags, keepalive behavior, stripe/ramp settings, and GTC timing relationships.
- Capability fields represent hardware-advertised widget, pin, stream-format, sample-rate, and sample-size support. This header does not encode whether a field is read-only, read/write, volatile, sticky, or write-one-to-clear.
- Output pin fields represent sink-facing HDMI/DisplayPort audio state: speaker and channel allocation, SAD/audio descriptor payloads, lipsync, HBR, sink identity, sink information, hot-plug audio state, format-change response, wireless-display identification, remote keepalive, and IEC channel-status overrides.
- LPIB and timer snapshot fields represent hardware audio position and timing snapshots, including snapshot lock and cyclic-buffer wrap count.
- Interrupt fields represent audio enabled, disabled, and format-changed flag/mask/type state.
- Input pin fields represent input activity, channel layout, infoframe validity/data, input pin sense, unsolicited-response behavior, and multichannel routing.

Persistence is hardware-defined. Writable fields may retain values until the driver reprograms them, the display/audio block is reset, suspend/resume state is restored, or the ASIC is reset. Status and capability fields can change asynchronously with hardware state, sink/source connection state, and display audio routing.

## Dependencies And Integration Points

This chunk depends on generated DCN 3.0.3 register files staying synchronized:

- `dcn_3_0_3_offset.h` supplies the matching indexed MMIO access registers and `ix...` register offsets. For example, it defines `mmAZF0ENDPOINT6_AZALIA_F0_CODEC_ENDPOINT_INDEX` at `0x03aa`, `ixAZF0ENDPOINT7_AZALIA_F0_CODEC_PIN_CONTROL_REMOTE_KEEPALIVE` at `0x006a`, and `ixAZF0INPUTENDPOINT4_AZALIA_F0_CODEC_INPUT_CONVERTER_PARAMETER_SUPPORTED_SIZE_RATES` at `0x0006`.
- AMD display register helper macros such as `REG_GET`, `REG_SET`, `REG_UPDATE`, `FD_MASK`, and `FD_SHIFT` rely on the exact `__SHIFT` and `_MASK` suffix convention used here.
- DCN audio, HDMI, DisplayPort, hotplug, interrupt, and power-management paths integrate with these constants when programming or reading display audio endpoints.
- Generated register databases are the source of truth for field semantics. This header captures numeric bit layout, not legal value ranges, write permissions, reset values, or sequencing rules.

The main integration contract is preprocessor naming. Missing or renamed fields usually fail at compile time, while wrong numeric masks or shifts can compile cleanly and cause incorrect MMIO field extraction or writes.

## Risks And Edge Cases

- The range starts and ends mid-register group. Endpoint 5 `MULTICHANNEL_ENABLE2` must be reconciled with the previous chunk, and input endpoint 4 `INPUT_CONVERTER_CONTROL_DIGITAL_CONVERTER` must be completed from the next chunk before making whole-group claims.
- The endpoint blocks are highly repetitive. A generator or manual merge error affecting only one endpoint number may be difficult to spot because most lines differ only by endpoint prefix.
- Shift/mask mismatches are high risk for fields such as `AUDIO_ENABLED`, `PRESENCE_DETECT`, `INFOFRAME_VALID`, `DOWN_MIX_INHIBIT`, `KEEPALIVE`, interrupt masks/types, and multichannel channel IDs.
- Several payload fields use `0xFFFFFFFFL`, including stream formats, GTC deltas, LPIB values, timer snapshots, association information, and sink information. Consumers should avoid signed-width assumptions when combining these masks with intermediate integer types.
- Capability, status, interrupt, and control fields share identical macro style. This file does not protect callers from writing read-only fields, clearing sticky status incorrectly, or confusing mask bits with value bits.
- `UNSOLICITED_RESPONSE_FORCE` fields can synthesize hardware notifications. Incorrect use can create misleading audio, hotplug, or pin events.
- Multichannel enable registers pack multiple enable, mute, and channel-ID fields into one 32-bit word. An incorrect mask or endpoint prefix can corrupt adjacent slots.
- IEC channel-status override registers contain both value and override-enable bits. Programming only value fields, or using the wrong endpoint's override fields, may silently leave transmitted channel-status metadata unchanged.
- Cross-generation reuse is risky. DCN 3.0.3 Azalia fields are similar to adjacent DCN/DCE generations, but code must include the offset and shift/mask headers that match the target ASIC.

## Test Signals

Useful validation signals are mostly build-time and hardware-integration oriented:

- Build the AMDGPU DCN 3.0.3 display code that includes this header to catch missing macro names in register-helper expansions.
- Preprocess representative users of `FD_MASK`, `FD_SHIFT`, `REG_GET`, `REG_SET`, and `REG_UPDATE` for Azalia fields to confirm the expected `AZF0ENDPOINT*` and `AZF0INPUTENDPOINT*` macros resolve.
- Compare this header against `dcn_3_0_3_offset.h` and the generator register database to ensure indexed endpoint registers have matching field definitions and that masks align with documented bit ranges.
- Exercise HDMI and DisplayPort audio enumeration on DCN 3.0.3 hardware, checking widget and pin capabilities, supported stream formats/rates/sizes, audio descriptors, sink information, HBR state, and channel allocation.
- Test audio enable/disable, format-change, hotplug, and unsolicited-response paths while observing `AUDIO_ENABLE_STATUS`, audio interrupt status fields, hot-plug `AUDIO_ENABLED`, and `FORMAT_CHANGED` fields.
- Exercise stereo, multichannel, and HBR audio modes to validate multichannel enable/mute/channel-ID packing, speaker/channel allocation, IEC channel-status override behavior, and converter stream/channel routing.
- Test suspend/resume and display reset paths to confirm converter, pin, sink info, hotplug, LPIB snapshot, infoframe, interrupt, and keepalive state is restored or re-read correctly.
- If input audio paths are exposed by the platform, validate input activity, channel layout, input pin sense, infoframe validity/data, channel allocation, and forced/ordinary unsolicited-response behavior.

## Open Cross-Chunk Questions

- The merge lane should combine this with the previous chunk to complete the beginning of `AZF0ENDPOINT5_AZALIA_F0_CODEC_PIN_CONTROL_MULTICHANNEL_ENABLE2`.
- The merge lane should combine this with the next chunk to finish `AZF0INPUTENDPOINT4_AZALIA_F0_CODEC_INPUT_CONVERTER_CONTROL_DIGITAL_CONVERTER` and the remainder of input endpoint 4.
- Whole-file analysis should verify the expected output/input endpoint count for DCN 3.0.3 and compare generated field layouts with the authoritative AMD register source.

### subset-b-001795: lines 34400-35366

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_3_sh_mask.h lines 34400-35366

## Scope

This chunk covers the final 967 lines of the generated DCN 3.0.3 shift/mask header. It contains only C preprocessor constants and generated grouping comments; there are no functions, structs, enums, storage objects, or executable statements in this slice.

The line range starts in the middle of the `AZF0INPUTENDPOINT4_AZALIA_F0_CODEC_INPUT_CONVERTER_CONTROL_DIGITAL_CONVERTER` mask list, continues through the rest of input endpoint 4, covers complete input endpoint 5, input endpoint 6, and input endpoint 7 register-field maps, and ends with the header's closing `#endif`. The range contains 868 `#define` entries: 432 `__SHIFT` definitions and 436 `_MASK` definitions. The mask count is larger because the range begins with the remaining four endpoint-4 digital-converter masks whose shift definitions are in the previous chunk.

This is the tail of the Azalia function 0 input-endpoint portion of the DCN 3.0.3 hardware register map. Endpoint 4 is partial in this chunk; endpoints 5, 6, and 7 are complete indexed input-endpoint blocks.

## Purpose

The purpose of this header region is to provide symbolic bit positions and masks for DCN 3.0.3 display-audio input endpoint registers. AMDGPU display code can include the header with the matching DCN 3.0.3 offset header and use register helper macros to extract or update fields without embedding raw bit positions.

The covered registers describe HD-audio/Azalia-style input converter and input pin state for display audio paths. They expose the register fields for converter widget capabilities, stream format selection, stream/channel IDs, digital converter control flags, advertised stream formats and sample size/rate support, input pin capabilities, unsolicited response controls, pin sense, widget input enablement, multichannel routing, high-bit-rate audio status, channel allocation, hot-plug audio status, forced unsolicited responses, default pin configuration, LPIB snapshots, input activity status, and audio infoframe data.

This file is a hardware contract. Its important behavior is the exact macro naming and numeric bit layout consumed by ASIC-specific DCN303 register code, not local algorithmic logic.

## Important APIs, Types, And Constants

There are no callable APIs or C types in this chunk. The exported interface is the preprocessor naming convention:

- `AZF0INPUTENDPOINT<n>_<REGISTER>__<FIELD>__SHIFT` gives the field bit offset for input endpoint `n`.
- `AZF0INPUTENDPOINT<n>_<REGISTER>__<FIELD>_MASK` gives the field bit mask for the same register field.
- Generated comments such as `// addressBlock: azf0inputendpoint5_inputendpointind` group constants by indexed input-endpoint register block.
- Generated comments such as `//AZF0INPUTENDPOINT7_AZALIA_F0_CODEC_INPUT_PIN_CONTROL_INFOFRAME` group field macros by logical register.

The partial endpoint 4 tail includes:

- The final `AZALIA_F0_CODEC_INPUT_CONVERTER_CONTROL_DIGITAL_CONVERTER` masks for `PRO`, `L`, `CC`, and `KEEPALIVE`.
- `INPUT_CONVERTER_PARAMETER_STREAM_FORMATS`, a full-width stream-format bitmap.
- `INPUT_CONVERTER_PARAMETER_SUPPORTED_SIZE_RATES`, with audio rate capability bits and audio bit-depth capability bits.
- `INPUT_PIN_PARAMETER_AUDIO_WIDGET_CAPABILITIES`, with fields for audio channel capability, amplifier presence, amplifier override, stripe, processing widget, unsolicited response capability, connection list, digital, power control, LR swap, widget delay, and type.
- `INPUT_PIN_PARAMETER_CAPABILITIES`, with impedance sense, trigger-required, jack-detection, headphone-drive, output/input capability, balanced I/O, HDMI, VREF control, EAPD, and DisplayPort capability fields.
- Input pin controls for unsolicited response tag/enable, input pin sense, widget input enable, multichannel enable and mute/channel IDs for slots 0-7, HBR capability/enable, channel allocation, hot-plug audio status, forced unsolicited-response payload/force bit, default configuration, LPIB snapshot control, LPIB position, LPIB timer snapshot, input activity/status, and infoframe data.

Input endpoints 5, 6, and 7 repeat the complete 23-register input-endpoint pattern:

- `AZALIA_F0_CODEC_INPUT_CONVERTER_PARAMETER_AUDIO_WIDGET_CAPABILITIES`
- `AZALIA_F0_CODEC_INPUT_CONVERTER_CONTROL_CONVERTER_FORMAT`
- `AZALIA_F0_CODEC_INPUT_CONVERTER_CONTROL_CHANNEL_STREAM_ID`
- `AZALIA_F0_CODEC_INPUT_CONVERTER_CONTROL_DIGITAL_CONVERTER`
- `AZALIA_F0_CODEC_INPUT_CONVERTER_PARAMETER_STREAM_FORMATS`
- `AZALIA_F0_CODEC_INPUT_CONVERTER_PARAMETER_SUPPORTED_SIZE_RATES`
- `AZALIA_F0_CODEC_INPUT_PIN_PARAMETER_AUDIO_WIDGET_CAPABILITIES`
- `AZALIA_F0_CODEC_INPUT_PIN_PARAMETER_CAPABILITIES`
- `AZALIA_F0_CODEC_INPUT_PIN_CONTROL_UNSOLICITED_RESPONSE`
- `AZALIA_F0_CODEC_INPUT_PIN_CONTROL_RESPONSE_INPUT_PIN_SENSE`
- `AZALIA_F0_CODEC_INPUT_PIN_CONTROL_WIDGET_CONTROL`
- `AZALIA_F0_CODEC_INPUT_PIN_CONTROL_MULTICHANNEL_ENABLE`
- `AZALIA_F0_CODEC_INPUT_PIN_CONTROL_MULTICHANNEL_ENABLE2`
- `AZALIA_F0_CODEC_INPUT_PIN_CONTROL_RESPONSE_HBR`
- `AZALIA_F0_CODEC_INPUT_PIN_CONTROL_CHANNEL_ALLOCATION`
- `AZALIA_F0_CODEC_INPUT_PIN_CONTROL_HOT_PLUG_CONTROL`
- `AZALIA_F0_CODEC_INPUT_PIN_CONTROL_UNSOLICITED_RESPONSE_FORCE`
- `AZALIA_F0_CODEC_INPUT_PIN_CONTROL_RESPONSE_CONFIGURATION_DEFAULT`
- `AZALIA_F0_CODEC_INPUT_PIN_CONTROL_LPIB_SNAPSHOT_CONTROL`
- `AZALIA_F0_CODEC_INPUT_PIN_CONTROL_LPIB`
- `AZALIA_F0_CODEC_INPUT_PIN_CONTROL_LPIB_TIMER_SNAPSHOT`
- `AZALIA_F0_CODEC_INPUT_PIN_CONTROL_INPUT_STATUS_CONTROL`
- `AZALIA_F0_CODEC_INPUT_PIN_CONTROL_INFOFRAME`

Important field families in the complete endpoint blocks include:

- Converter capability fields: channel capability, input/output amplifier presence, amplifier parameter override, format override, stripe, processing widget, unsolicited response capability, connection list, digital, power control, LR swap, widget delay, and widget type.
- Converter format fields: number of channels, bits per sample, sample base divisor, sample base multiple, sample base rate, and stream type.
- Channel/stream routing fields: 4-bit channel ID and 4-bit stream ID.
- Digital converter flags: `DIGEN`, validity, validity configuration, preemphasis, copy, non-audio, professional, level, category code, and keepalive.
- Capability bitmaps: full-width stream formats plus audio rate and bit-depth capability fields.
- Pin capability fields: impedance sense, trigger-required, jack-detection, headphone-drive, output/input capability, balanced I/O, HDMI, VREF control, EAPD, and DisplayPort.
- Unsolicited response fields: tag/enable plus forced unsolicited response payload and force bit.
- Pin sense fields: impedance sense value and high-bit presence detect.
- Multichannel routing fields: four packed slots per register, each with enable, mute, and channel-ID fields; the second register covers slots 4-7.
- HBR/channel/status fields: HBR capability/enable, 8-bit channel allocation, hot-plug clock gating state, clock-on state, and high-bit `AUDIO_ENABLED`.
- Default pin configuration fields: sequence, default association, misc, color, connection type, default device, location, and port connectivity.
- LPIB fields: snapshot lock, cyclic buffer wrap count, full-width LPIB, and full-width timer snapshot.
- Input status/infoframe fields: input activity, channel layout, unsolicited-response enables for activity and channel-layout/channel-status infoframe changes, channel count, channel allocation, infoframe byte 5, and high-bit infoframe valid.

## Control Flow

This chunk has no runtime control flow. Its effective flow is compile-time token resolution:

1. DCN303 display code includes `dcn_3_0_3_offset.h` and `dcn_3_0_3_sh_mask.h`.
2. Register helper macros concatenate register and field tokens to find the matching `__SHIFT` and `_MASK` constants.
3. Runtime MMIO or indexed-register code uses those constants to pack write values, update fields without disturbing neighboring bits, or extract status fields from hardware register reads.

The declaration order still reflects hardware organization. The chunk first finishes input endpoint 4, then enters `azf0inputendpoint5_inputendpointind`, `azf0inputendpoint6_inputendpointind`, and `azf0inputendpoint7_inputendpointind` in ascending endpoint order. Within each register group, generated shift definitions appear before mask definitions for the same fields.

## State And Persistence Behavior

The header itself stores no state and persists no data. It describes where state lives in DCN 3.0.3 Azalia input endpoint hardware registers.

Writable converter and pin-control fields can represent programmed audio input format, stream/channel association, digital converter behavior, channel allocation, multichannel routing, HBR enablement, hot-plug audio enablement, unsolicited-response setup, forced event generation, and LPIB snapshot lock state. Read-only or hardware-updated fields can represent capability bitmaps, widget/pin capability declarations, presence detect, input activity, channel layout, infoframe validity/data, position-buffer snapshots, timer snapshots, and hot-plug status. The header does not encode access type, reset value, write-one-to-clear behavior, or ordering rules; those remain hardware/manual and driver responsibilities.

Persistence is hardware-defined. Programmed control fields may survive until reprogramming, display/audio block reset, suspend/resume restore, or ASIC reset. Capability and status fields may change as the display audio topology, hot-plug state, input activity, or hardware power state changes.

## Dependencies And Integration Points

This chunk depends on the matching generated DCN 3.0.3 register offset file:

- `dcn_3_0_3_offset.h` defines the MMIO index/data register pairs for `AZF0INPUTENDPOINT4` through `AZF0INPUTENDPOINT7` and the indexed `ixAZF0INPUTENDPOINT<n>_...` offsets for each logical input converter and input pin register described here.
- The endpoint index/data pairs are in the `dce_dc_hda_azf0inputendpoint<n>_dispdec` address blocks, while the field macros in this chunk are in the corresponding `azf0inputendpoint<n>_inputendpointind` indexed blocks.
- The offset header and this shift/mask header must stay generated from the same register database. A field macro without a matching indexed register, or an indexed register without field macros, breaks the intended register-helper contract.

Direct include integration observed in the DCN303 tree:

- `drivers/gpu/drm/amd/display/dc/resource/dcn303/dcn303_resource.c` includes `dcn_3_0_3_offset.h` and `dcn_3_0_3_sh_mask.h` while constructing DCN303 resources. That file declares `num_audio = 2`, so not every endpoint exposed by the generated register database is necessarily used as a live audio instance on every product configuration.
- `drivers/gpu/drm/amd/display/dc/irq/dcn303/irq_service_dcn303.c` includes the same headers for DCN303 interrupt-service setup.
- `drivers/gpu/drm/amd/display/dmub/src/dmub_dcn303.c` includes the same headers and uses `FD_MASK` and `FD_SHIFT` style expansion for DMUB common register fields.

The broader AMD display register framework provides the main integration point. Helpers such as `REG_GET`, `REG_SET`, `REG_UPDATE`, `FD_MASK`, and `FD_SHIFT` rely on the exact suffix convention used here. Missing or renamed symbols generally fail at compile time; wrong numeric masks or shifts can compile cleanly and fail only as incorrect hardware programming or status interpretation.

## Risks And Edge Cases

- The chunk begins mid-register group. Endpoint 4's `DIGEN`, `V`, `VCFG`, `PRE`, `COPY`, and `NON_AUDIO` digital-converter shifts/masks are in the previous chunk, while this chunk starts at the remaining `PRO`, `L`, `CC`, and `KEEPALIVE` masks.
- This is the final chunk of the header and ends with the include guard close. Any merge-lane whole-file summary should avoid treating the trailing `#endif` as a register artifact.
- The endpoint blocks are highly repetitive. Copy/generator drift affecting only endpoint 5, 6, or 7 can be difficult to detect in review because most lines differ only by endpoint number.
- Shift/mask mismatches are high risk for fields at the edge of the word, especially `PRESENCE_DETECT`, `AUDIO_ENABLED`, and `INFOFRAME_VALID`, all of which use bit 31.
- Several full-width fields use `0xFFFFFFFFL`, including stream formats, LPIB, and timer snapshots. Consumers should avoid signed-width assumptions and should use the expected unsigned register-width types.
- Capability, status, and control registers share identical macro style. This header does not prevent writes to read-only capability/status fields or incorrect handling of clear-on-read/write-one-to-clear semantics if any apply in the hardware model.
- `UNSOLICITED_RESPONSE_FORCE` can synthesize an event payload. Incorrect writes could create misleading hot-plug, input activity, or pin-response notifications.
- Multichannel enable registers pack enable, mute, and 4-bit channel-ID fields for four slots per register. Bad masks or wrong endpoint prefixes can corrupt neighboring slot state while still producing valid C code.
- Endpoint count and hardware exposure are not the same concept. The generated register map exposes input endpoints 4-7 here, but DCN303 resource configuration may instantiate fewer usable audio resources.
- Cross-generation reuse is risky. DCN 3.0.3 names are close to DCN 3.0.2 and other DCN headers, but code must include offset and shift/mask files for the same ASIC generation.

## Test Signals

Useful validation signals are mostly build-time and hardware-integration oriented:

- Build the AMDGPU display code for a DCN303-enabled configuration to catch missing macro names in register helper expansions.
- Preprocess representative users of `FD_MASK`, `FD_SHIFT`, `REG_GET`, `REG_SET`, and `REG_UPDATE` to ensure token concatenation resolves to `AZF0INPUTENDPOINT4` through `AZF0INPUTENDPOINT7` macros where expected.
- Compare this header slice against `dcn_3_0_3_offset.h` to verify that every input-endpoint indexed register in endpoints 4-7 has matching shift/mask field definitions.
- Compare generated masks and shifts against the authoritative AMD register database for DCN 3.0.3, especially high-bit fields, full-width fields, and packed multichannel slot fields.
- Exercise DCN303 display-audio bring-up on hardware with HDMI/DisplayPort audio paths and verify input endpoint capability reads, stream format/rate support, channel allocation, HBR state, hot-plug audio enabled state, and input activity/status fields.
- Test hotplug, audio enable/disable, suspend/resume, and display reset paths while checking that driver state is reprogrammed or re-read consistently for converter format, stream/channel ID, digital converter flags, multichannel routing, LPIB snapshots, infoframe status, and unsolicited response controls.
- Validate that generated endpoint 5-7 field layouts match endpoint 4 and earlier input endpoint blocks where hardware intends symmetry, while preserving endpoint-specific prefixes.

## Open Cross-Chunk Questions

- The merge lane should combine this with the previous chunk to present endpoint 4 as a complete input endpoint, because this chunk starts after the beginning of `AZF0INPUTENDPOINT4_AZALIA_F0_CODEC_INPUT_CONVERTER_CONTROL_DIGITAL_CONVERTER`.
- Whole-file analysis should verify the expected number of DCN 3.0.3 Azalia input and output endpoint blocks and reconcile the generated endpoint map with DCN303 `num_audio` resource limits.
- Whole-file analysis should compare the DCN 3.0.3 generated field layout against nearby generations, especially DCN 3.0.2, to flag any intentional or accidental register-database divergence.
