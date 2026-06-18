# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_5_1_offset.h lines 1-2727

## Purpose

This chunk is the opening slice of AMD's generated DCN 3.5.1 register-offset header. It has no executable C logic; it publishes preprocessor constants that name DCN 3.5.1 MMIO registers, indirect-register indices, and register-base selector indices for display, audio, DMU/DMCUB, clock, writeback, hub, and interrupt-routing blocks. Driver code combines these offsets with the companion `dcn_3_5_1_sh_mask.h` shift/mask header so register-list macros can construct per-ASIC register tables.

The requested range covers the license, header guard opening, and the first 2,337 `#define` entries in a 15,259-line file. Within this range there are 1,322 `reg*` defines, 1,014 `ix*` indirect-index defines, and one header-guard define. The `reg*` entries appear as offset/base-index pairs, where `regFOO` gives a register offset and `regFOO_BASE_IDX` selects the base segment used by the AMD display register helpers. The `ix*` entries are indirect register indices used through paired index/data windows, especially Azalia codec endpoint, stream, and function nodes.

Although the repository path is under a local `ceph-client` mirror, this file is AMDGPU display hardware metadata. It does not implement Ceph or distributed filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, includes, locks, or allocation paths in this chunk. The exported interface is the generated macro namespace:

- `reg<REGISTER>`: numeric MMIO register offset within the corresponding DCN register segment.
- `reg<REGISTER>_BASE_IDX`: segment selector passed through `BASE(reg..._BASE_IDX)` style macros before adding the register offset.
- `ix<INDIRECT_REGISTER>`: index value for an indirect register reached through an index/data pair.

The main macro families in this line range are:

- HDA/Azalia global controller offsets for capabilities, version fields, payload capacities, global control/status, wake and state-change status, interrupt control/status, wall-clock counter, CORB/RIRB ring base addresses and pointers, immediate command/response windows, and DMA position buffer addresses.
- Azalia sink and diagnostics indirect indices for manufacturer/product ID, port IDs, sink-description bytes, input CRC result channels, output CRC result channels, and per-stream FIFO/latency counters for streams 0-15.
- Azalia F0 endpoint indirect indices for output endpoints 0-7. Each endpoint has the same converter and pin-control shape: widget capabilities, stream formats, supported rates, converter format, channel/stream ID, digital-converter control, GTC embedding and deltas, pin capabilities, unsolicited responses, pin sense, widget control, speaker/channel allocation, audio descriptors 0-13, multichannel controls, lipsync, HBR, sink info, hotplug, IEC 60958 channel-status override indices, LPIB snapshots, coding type, format-change state, wireless display identification, remote keepalive, audio enable status, and endpoint interrupt status.
- Azalia F0 input-endpoint indirect indices for input endpoints 0-7. These cover input converter format, channel/stream ID, digital-converter state, supported formats/rates, input pin capabilities, unsolicited response, input pin sense, widget control, multichannel enables, HBR, channel allocation, hotplug, LPIB snapshots, input status control, and infoframe indices.
- Function-2 codec indirect verb indices for root, output endpoint, and input endpoint paths. These map HDA verb-like codec controls and parameters such as vendor/device ID, revision, power state, subsystem ID, converter synchronization, converter controls, pin controls, descriptor data, sink info access, multichannel enablement, IEC channel-status overrides, and input channel-status registers.
- DCCG display clock offsets for PHYPLL pixel-clock resync, DP and HDMI stream DTOs, DSC/DPP clock DTOs, display/reference/SOC/symbol clock gate controls, GTC counters, DTBCLK DTOs, OTG pixel-rate controls for OTG0-3, audio DTO source/phase/module registers, vsync latch/counter registers, soft reset, and symbol-clock force-disable controls.
- DC performance monitor offsets for DCCG/DMU/MMHUBBUB/HDA perfmon instances 0, 1, 2, 4, and 5.
- DMU and power-management offsets for display power-gate domain config/status registers, DCPG interrupt status/control registers, memory/global power request registers, DMU clock and SMU interrupt controls, ZSC controls/status, deep-sleep force control, GPU timer start/read registers, display interrupt status continuations, and interrupt destination routing registers for DCCG, DMU, DCPG, MMHUBBUB, WB, DCHUB, DPP, MPC, OPP, OPTC, OTG, DIG, DDC/HPD, DIO, DCIO, HPD, AZ, AUX, DSC, and HPO.
- DMCUB offsets for region offsets/high offsets/top addresses, region 3 code-window base/top/offset registers, DMCUB interrupt enable/ack/status/type, external interrupt status/context/ack, instruction/data/undefined-address fault registers, security and memory controls, inbox/outbox mailboxes, timer triggers/window/current time, scratch registers, GPINT registers, low-power wake interrupt enable, memory power control, processor ID, control registers, and TMR AXI-space mapping.
- MMHUBBUB and MCIF writeback offsets for writeback buffer manager control/status, buffer pitch/status/address/high-address/resolution, arbitration, p-state and watermark controls, security/VMID controls, warmup config/base/region controls, memory power, clock, soft reset, DMU interface error status, and outstanding counters.
- HDA display-space windows for Azalia stream, endpoint, input-endpoint, controller, root, clock, memory-power, and audio perfmon registers.
- DCHUBBUBL SDPIF and return-path offsets for VM framebuffer/AGP/local HBM address programming, security levels for pipe/data/cursor/GPUVM paths, SDPIF request rate limiting, SDPIF memory power, return-path memory power, CRC values, DCC stats, compbuf control, and DET0-2 controls. The chunk ends at `regDCHUBBUB_DET2_CTRL_BASE_IDX`.

## Control Flow

This header has no runtime branches, calls, or sequencing. The runtime flow is supplied by AMDGPU display code:

1. DCN 3.5.1 code includes `dcn/dcn_3_5_1_offset.h` and `dcn/dcn_3_5_1_sh_mask.h`.
2. Register-list macros token-paste symbolic names into offset, shift, and mask initializers.
3. For DMUB, `dmub_srv_dcn351_regs_init()` in `display/dmub/src/dmub_dcn351.c` uses `REG_OFFSET_EXP(reg_name)` as `BASE(reg##reg_name##_BASE_IDX) + reg##reg_name`, then expands `DMUB_DCN35_REGS()` and `DMCUB_INTERNAL_REGS()` into `dmub->regs_dcn35`.
4. Runtime DMUB/DCN paths then use the initialized register tables through helper macros and functions to reset DMCUB, program code windows, set up inbox/outbox mailboxes, issue GPINTs, configure memory mappings, inspect firmware boot state, route interrupts, and access display/audio hardware.

For the Azalia indirect indices, the runtime sequencing is external to this header: consumers must program the relevant stream, endpoint, root, or codec index register and then read or write the paired data register. The index values here do not encode ordering requirements for HDA ring setup, codec verb submission, audio endpoint programming, or interrupt acknowledgement.

## State And Persistence Behavior

This chunk stores no software state and persists nothing by itself. It describes hardware state surfaces:

- HDA/Azalia controller state for global capabilities, stream payload limits, wake/status/interrupt bits, CORB/RIRB DMA rings, immediate command response handling, and DMA position buffers.
- Azalia codec, stream, endpoint, input-endpoint, sink-info, CRC, and audio timing state used for HDMI/DisplayPort audio enumeration, format programming, hotplug signaling, multichannel/HBR output, LPIB snapshots, and audio diagnostics.
- Clock-generator state for pixel clocks, stream clocks, reference clocks, DSC/DPP clocks, DTBCLK, audio DTOs, GTC timebase, vsync latches, clock gating, and soft reset.
- DMU/DMCUB state for power domains, display interrupts, interrupt routing, GPU timer reads, DMCUB memory windows, mailbox pointers, scratch registers, GPINTs, firmware-visible control/status registers, fault addresses, low-power wake, and memory power controls.
- MMHUBBUB/MCIF writeback and DCHUBBUBL state for memory-hub warmup, writeback buffers, VM address apertures, security levels, request throttling, CRC capture, DCC stats, and DET/compbuf controls.

Persistence is hardware-defined. Many configuration registers survive until a modeset, block reset, power-gating event, suspend/resume transition, GPU reset, or ASIC reset. Status, interrupt, counter, CRC, mailbox pointer, and fault-address registers may be volatile, sticky, write-one-to-clear, self-clearing, or only valid while the relevant display, audio, hub, or DMCUB power/clock domain is active. This generated offset header does not carry access-type metadata; consumers must rely on the paired shift/mask definitions, register specifications, and block-specific driver code for side-effect rules.

## Dependencies And Integration Points

This chunk depends on AMD's generated DCN 3.5.1 register database and must remain synchronized with:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_5_1_sh_mask.h`, which supplies the matching field shifts and masks for these symbolic register names.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn351.c`, which directly includes this header and initializes DCN351 DMUB offsets via `dmub_srv_dcn351_regs_init()`.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn35.h`, whose `DMUB_DCN35_REGS()` and `DMUB_DCN35_FIELDS()` macro lists define the shared register-table shape used by DCN35/DCN351 DMUB code.
- DCN 3.5.1 display resource, DIO/audio, clock, hub, IRQ, writeback, and DMUB paths that consume these generated symbols directly or indirectly through AMD display register helper macros.

The strongest direct integration in this exact range is DMUB and DMCUB initialization: many `DMCUB_*`, `CC_DC_PIPE_DIS`, `MMHUBBUB_SOFT_RESET`, `DCN_VM_FB_LOCATION_BASE`, `DCN_VM_FB_OFFSET`, and `DMU_CLK_CNTL` offsets in this chunk are referenced by the shared DCN35 DMUB register table that DCN351 reuses. The Azalia and HDA families provide the register-addressing substrate for HDMI/DP audio control and diagnostics, while DCCG, DMU, MMHUBBUB, and DCHUBBUBL families support clocking, power, interrupt, memory-hub, writeback, and VM setup.

## Risks And Edge Cases

- These constants are untyped preprocessor values. A wrong offset or base index can compile cleanly while directing a register helper to the wrong MMIO address or segment.
- The file is generated metadata. Manual edits can diverge from AMD's authoritative register database, the matching shift/mask header, firmware expectations, and silicon documentation.
- `reg*` macros are only half of an address. Consumers must add the correct base selected by `_BASE_IDX`; using a raw `reg*` value as an absolute address is wrong for segmented DCN register spaces.
- Indirect `ix*` values require the correct index/data aperture. Reusing an endpoint index with a stream, root, input-endpoint, or function-2 data window can silently read or write unrelated hardware state.
- Repeated stream, endpoint, input-endpoint, code-window, mailbox, scratch, and perfmon families are mechanically similar. A generator error in one instance can affect only that instance, so stream 0 or endpoint 0 working does not prove streams/endpoints 1-15 or 1-7 are correct.
- Audio registers are interoperability-sensitive. Wrong HDA ring, immediate command, converter format, IEC channel-status, HBR, multichannel, sink-info, or hotplug offsets can cause silent HDMI/DP audio, channel mapping errors, bad sample-rate reporting, stuck hotplug state, or codec command timeouts.
- DMCUB offsets are boot- and firmware-critical. Wrong code-window, top-address, mailbox, GPINT, scratch, or fault/status offsets can prevent firmware boot, corrupt command queues, hide boot diagnostics, or break reset/release flows.
- Interrupt destination and status offsets are side-effect-sensitive. Misrouting or acknowledging the wrong display interrupt can cause missed events, interrupt storms, or resume-only failures.
- Memory aperture, VM, security, and writeback buffer offsets can affect isolation and data integrity. Incorrect values around `DCN_VM_*`, `DCHUBBUB_SDPIF_*_SEC_LVL`, `MCIF_WB_*_ADDR*`, DMCUB regions, or top-address registers can produce invalid DMA, display corruption, firmware faults, or security boundary violations.
- The chunk boundary is artificial. It ends in the middle of the DCHUBBUBL return-path register family, so later chunks must be merged before making whole-file claims about all DCN 3.5.1 hub, pipe, timing, link, or display-engine registers.

## Test Signals

Useful validation combines generated-header checks with hardware behavior:

- Build AMDGPU display support with DCN 3.5.1 enabled. Missing or renamed macros should fail where `dmub_dcn351.c` expands `DMUB_DCN35_REGS()`, `DMCUB_INTERNAL_REGS()`, and related shift/mask tables.
- Mechanically verify that each `reg*` entry in this chunk has the expected `reg*_BASE_IDX` companion and that no `ix*` indirect index is accidentally paired with a base-index macro.
- Diff this range against AMD's authoritative DCN 3.5.1 generated register database and compare nearby families with `dcn_3_5_0_offset.h` where DCN35 and DCN351 are expected to share layouts.
- Boot on DCN351 hardware and verify DMUB firmware reset/release, backdoor load, code-window setup, inbox/outbox pointers, GPINT acknowledgement, scratch/status reads, fault-address diagnostics, and low-power wake behavior.
- Exercise HDMI and DisplayPort audio across plug/unplug, modeset, suspend/resume, stream enable/disable, format changes, multichannel LPCM, HBR/compressed formats, and sink changes. Watch for HDA command timeouts, bad sink descriptors, stale LPIB snapshots, CRC mismatches, missed audio enabled/disabled interrupts, and silent audio after resume.
- Validate DCCG and timing behavior across display clock changes, DP/HDMI stream-clock DTO changes, DSC/DPP clock programming, DTBCLK transitions, GTC reads, vsync latch/counter paths, and clock-gating transitions.
- Validate power and interrupt paths by checking DCPG domain transitions, DMU/SMU interrupts, display interrupt continuation registers, interrupt destination routing, memory power controls, and suspend/resume logs.
- Exercise writeback and hub paths that use MCIF/MMHUBBUB/DCHUBBUBL offsets, including writeback buffer programming, p-state/watermark changes, VM aperture setup, SDPIF security-level programming, CRC capture, DCC stats, and DET/compbuf behavior.

## Cross-Chunk Notes

This is the first chunk of `dcn_3_5_1_offset.h`. Later chunks continue from DCHUBBUBL return-path registers and cover the rest of the DCN 3.5.1 register-offset namespace. The final per-file research document should merge adjacent chunks before drawing conclusions about complete block coverage, all display pipes, all timing generators, all link encoders, or the full DCN351 register map.
