# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_2_0_offset.h lines 1-2628

## Scope And Purpose

This chunk is the first 2,628 lines of the DCN 3.2.0 display-core register offset header. It is generated-style hardware metadata for AMDGPU's Display Core Next 3.2 generation, not executable driver logic. The file defines `reg...` address-offset macros and matching `reg..._BASE_IDX` segment selectors for display clock generation, DMU/DMCUB, display writeback, MMHUBBUB, HDA/Azalia audio, DCHUBBUB memory arbitration, VM request handling, and the first two HUBP/HUBPREQ/HUBPRET/cursor instances.

The macros are consumed by DCN32 display and DMUB code through register-list expansion macros. Consumers combine `regFOO_BASE_IDX` with `ctx->dcn_reg_offsets[base_idx]` and then add `regFOO` to produce a final MMIO register address. In `display/dc/resource/dcn32/dcn32_resource.c`, macros such as `SR()`, `SR_ARR()`, `SRI()`, and `SRI_ARR()` expand these names into typed register tables for display components. In `display/dmub/src/dmub_dcn32.c`, `REG_OFFSET_EXP()` performs the same base-plus-offset expansion for DMUB service registers.

This chunk ends at `regCURSOR0_1_DMDATA_ADDRESS_LOW_BASE_IDX`; later lines in the same header continue with additional pipes and display blocks.

## Register Macro Shape

Each register is represented by two preprocessor constants:

- `regNAME`: the block-local register offset, for example `regDENTIST_DISPCLK_CNTL 0x0064`.
- `regNAME_BASE_IDX`: the index into the DCN register base table, commonly `1` for DCCG/display-decode blocks and `2` for most DC/DMU/HUBBUB/HUBP blocks; the VGA memory page registers at the start of the VGA section include base index `0`.

The source comments divide definitions into `addressBlock` groups and list each group's hardware base address. Those comments are important for humans auditing generated offsets, while driver code relies on the macro names and base-index values.

There are no C functions, structs, enums, static data, locks, or direct reads/writes in this header. The API surface is entirely macro symbols used by other headers and C files.

## Address Blocks Covered

The chunk defines these block families:

- DCCG and DCCG DFS: display clocking, pixel-clock resync, DP/DSC/DPP DTOs, clock gating controls, GTC, audio DTOs, vblank latch/counter controls, and soft reset.
- DMU and DMCUB: RBBM interface status, interrupt-hub status and destination registers, power-gating domains, DMCUB region windows, mailboxes, scratch registers, GPINT, firmware status, timer, instruction/cache controls, fault reporting, and debug/status registers.
- DWB0 and DWB color pipeline: display writeback enable, memory power, viewport/scaler, crop, capture rate, CRC, host-read and overflow status, plus output gamut remap and OGAM RAM A/B LUT programming registers.
- MMHUBBUB: VGA legacy aperture/control registers, VGA interface MCIF counters, MCIF writeback buffer and arbitration registers, writeback watermarks, warmup, memory power, clock/reset/status, and SMU watermark control.
- HDA/Azalia: controller clock/audio DTO/DMA/CRC/memory-power registers, root codec parameters and controls, stream index/data pairs for streams 0-15, output endpoint index/data pairs for endpoints 0-7, and input endpoint index/data pairs for endpoints 0-7.
- DCHUBBUB: arbitration watermarks for sets A-D, MALL control, global timer, surface check addresses, VTG controls, timeout detection, SDPIF VM aperture/security controls, ret-path CRC/DCC/DET/compbuf controls, and VM context/page-table/fault registers.
- HUBP/HUBPREQ/HUBPRET/cursor for pipes 0 and 1: surface layout and viewport registers, VMID and surface addresses, meta-surface addresses, flip controls, in-use/earliest-in-use latches, TTU/QoS/prefetch/nominal/flip/vblank timing parameters, memory power/status, read-line controls, cursor address/size/position/hotspot/memory power, and DMDATA addresses.

The block count is large but regular. For example, the DMCUB block contributes 123 registers, the DCHUBBUB VM request block contributes 118 registers, and each HUBPREQ instance contributes 85 registers. Pipe 1 repeats the pipe 0 HUBP/HUBPREQ/HUBPRET/cursor layout with `HUBP1`, `HUBPREQ1`, `HUBPRET1`, and `CURSOR0_1` prefixes.

## Important Integration Points

The most important consumers are the DCN32 resource and DMUB initialization layers:

- `dcn32_resource.c` includes this header with `dcn_3_2_0_sh_mask.h`, then expands component-specific register lists. `SR(AZALIA_CONTROLLER_CLOCK_GATING)`, `SR(DOMAIN0_PG_CONFIG)`, `SR(D1VGA_CONTROL)`, and similar entries rely on this chunk's offsets.
- `dmub_dcn32.c` initializes `struct dmub_srv_dcn32_regs` from this header. DMUB reset, backdoor-load, CW region setup, scratch polling, GPINT, and framebuffer-base translation depend on the DMCUB and VM macros defined here.
- `amdgpu/gmc_v11_0.c`, DCN32 IRQ service, GPIO factory/translation, and clock-manager code also include the header, so these offsets affect memory controller setup, interrupt routing, GPIO/DDC/HPD handling, and display-clock programming.
- The companion `dcn_3_2_0_sh_mask.h` supplies field masks and shifts for the same register names. Offset macros only identify register addresses; field-level operations such as `REG_GET`, `REG_UPDATE`, and `REG_SET_2` need the sh/mask header as well.

The naming convention is part of the ABI between generated hardware headers and hand-written DC code. A missing or renamed macro breaks compile-time expansion rather than failing at runtime.

## Control Flow

This header has no internal control flow. Runtime control flow appears in consumers:

- During DCN32 resource creation, register-list macros expand into register tables. Later component constructors pass those tables to common register helpers, so ordinary DC methods can use symbolic register names rather than raw addresses.
- During DMUB service initialization, `dmub_srv_dcn32_regs_init()` expands DMUB register and field lists, storing offsets, masks, and shifts in the DMUB service object.
- During runtime display programming, register helper macros use those stored offsets for MMIO reads/writes. Examples include DMUB firmware reset and region-window setup through `DMCUB_REGION3_CW*`, framebuffer address translation through `DCN_VM_FB_LOCATION_BASE` and `DCN_VM_FB_OFFSET`, and DCCG/HUBBUB/HUBP programming during modeset, flip, power, cursor, writeback, and audio operations.

Because this header is pure metadata, the effective behavior is an indirect control-flow dependency: incorrect offsets cause otherwise correct component code to access the wrong hardware register.

## State And Persistence Behavior

The header itself persists no state. Its macros describe hardware state locations:

- Clock and DTO registers preserve display clocking state while the display engine is active.
- DMCUB mailbox, scratch, GPINT, region-window, and fault registers hold live firmware communication and boot/runtime state.
- DCHUBBUB arbitration, watermark, MALL, VM context, and timeout registers hold memory-fetch policy and fault state across modeset and power-management transitions until rewritten or reset.
- HUBPREQ surface address, flip, in-use, prefetch, and timing registers represent per-plane scanout state and are updated around commits, page flips, and cursor updates.
- DWB and MCIF writeback registers hold capture/writeback pipeline state, buffer addresses, CRC state, overflow counters, and memory-power status.
- Azalia registers hold audio stream/controller state and endpoint/codec metadata for display audio paths.

Persistence is controlled by hardware reset, power gating, and explicit driver programming in consumers, not by this header.

## Dependencies

This chunk depends on the generated DCN register schema being synchronized with silicon and with companion headers:

- `dcn_3_2_0_sh_mask.h` must expose field names matching the register names used here.
- Register-list macros in DC component headers must use exact symbol names emitted here, including instance prefixes like `HUBPREQ0_`, `HUBPREQ1_`, and `CURSOR0_1_`.
- `ctx->dcn_reg_offsets[]` must provide valid base addresses for every `_BASE_IDX` value used by these macros.
- DCN32-specific C files must include this header before expanding register lists, otherwise generated symbols are unavailable.

No external libraries are involved; these are preprocessor constants compiled into the AMDGPU kernel driver.

## Risks And Edge Cases

The main risks are hardware-address correctness and generated-header drift:

- A wrong `reg...` value can redirect MMIO to a different hardware register, causing silent display corruption, hangs, failed firmware boot, bad watermark programming, VM faults, interrupt storms, or broken audio/writeback/cursor behavior.
- A wrong `_BASE_IDX` can be just as damaging as a wrong offset because the same local offset may be valid in multiple register spaces.
- Repeated instance blocks require exact naming. Pipe 1's `HUBPREQ1_*` offsets are not derived at runtime from pipe 0; they are explicit constants. Copy/paste or generator errors can break only one pipe.
- Legacy VGA definitions include overlapping offsets and different base indices, which is intentional for index/data style and legacy alias registers. Consumers must use the expected symbol rather than assuming one offset maps to one semantic register.
- The chunk mixes operational controls, status registers, interrupt destinations, address registers, and power controls. Tests that only compile the header cannot prove the values are electrically correct.
- Since the header is shared by DC and DMUB paths, changes can affect firmware boot/control and host display programming at the same time.

## Test Signals

Useful validation signals are layered:

- Build-time: AMDGPU/DCN32 compilation catches missing macro names, mismatched register-list names, and missing companion field-mask definitions.
- Boot/init: successful DCN32 display initialization and successful DMUB firmware reset/startup exercise the DMCUB, VM framebuffer-base, scratch, GPINT, and region-window offsets.
- Modeset and flip: multi-plane scanout, page flips, cursor updates, and multiple active pipes exercise HUBP/HUBPREQ/HUBPRET/cursor offsets for pipe 0 and pipe 1.
- Power management: display clock changes, clock gating, domain power gating, memory power status, MALL, and watermark transitions exercise DCCG, DMU/DC PG, DCHUBBUB, MMHUBBUB, HUBPREQ, and DWB memory-power registers.
- Interrupt handling: vblank, flip, HPD/DDC/AUX/audio/DMCUB/DMU/OTG interrupt routing and status handling exercise the IHC and interrupt-destination offsets.
- Display audio: HDMI/DP audio playback and stream enumeration exercise Azalia controller, root, stream, endpoint, and input-endpoint registers.
- Writeback/capture: DWB enable, viewport/scaler/crop, MCIF writeback buffers, CRC values, and overflow counters exercise the DWB and MCIF_WB sections.
- Fault/debug: VM fault reporting, timeout interrupt status, DMCUB fault addresses, DCHUBBUB CRC/DCC stats, and performance/debug counters provide diagnostic signals when offset programming is wrong.

No standalone unit test can fully validate this file. The strongest evidence comes from hardware-backed DCN32 integration tests, boot smoke tests on supported GPUs, display modeset/flip stress, suspend/resume, audio, cursor, writeback, and GPU VM fault-path testing.
