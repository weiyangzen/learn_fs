# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_4_sh_mask.h lines 12037-14354

## Scope

This chunk is a generated DCN 3.1.4 register-field mask slice from `dcn_3_1_4_sh_mask.h`. It contains C preprocessor constants only: `_SHIFT` macros for bit positions, `_MASK` macros for raw 32-bit register masks, and comment markers naming registers and address blocks. There are no functions, structs, enums, branches, loops, or driver-owned state objects in this range.

The slice starts in the tail of `DISP_INTERRUPT_STATUS`, covers `DISP_INTERRUPT_STATUS_CONTINUE` through `DISP_INTERRUPT_STATUS_CONTINUE25`, defines a broad set of display interrupt destination registers, then covers DMCUB/RBBMIF security, timeout, memory-region, content-window, and interrupt-control field masks through the beginning of `DMCUB_INTERRUPT_STATUS`.

## Purpose And Hardware Surface

The purpose of this header range is to provide the bit layout ABI between AMDGPU Display Core/DMUB code and DCN 3.1.4 display hardware. Companion offset headers provide MMIO register addresses; this mask header supplies the field masks and shifts used by register helper macros to pack, update, or decode individual fields without hard-coded bit numbers.

Major hardware areas represented here:

- Display interrupt status continuation chain: `DISP_INTERRUPT_STATUS_CONTINUE*` fields expose latched interrupt status bits across display pipes, encoders, HPD/AUX, HUBP/HUBBUB, DPP, OPP, OPTC/OTG, DCCG, MMHUBBUB, WB/WBSCL, DCPG, DCIO/DPCS, AZ audio, DSC, HPO, ABM, DPIA, and DMCUB events.
- Interrupt destination controls: `*_INTERRUPT_DEST` registers route interrupt sources for DCCG, DMU/DMCUB/DMCU, DCPG, MMHUBBUB, WB, DCHUB, DPP, MPC, OPP, OPTC, OTG0-OTG5, DIG, I2C/DDC/HPD, DIO/DCIO, AZ audio, AUX, DSC, and HPO.
- DMCUB security and RBBM interface state: `DMCUB_RBBMIF_SEC_CNTL`, `RBBMIF_TIMEOUT`, `RBBMIF_STATUS`, `RBBMIF_STATUS_2`, `RBBMIF_INT_STATUS`, timeout-disable registers, and status flags define trust/source metadata, timeout timing, fault-client decode, timeout address/op/status readback, per-client timeout masking, and secure/nonsecure region status.
- DMCUB memory aperture programming: `DMCUB_REGION0/1/2/4/5/6/7_*` and `DMCUB_REGION3_CW0` through `CW7` base/top/offset registers describe lower and upper address bits, 29-bit base/top fields, enable bits, and offset alignment for DMCUB firmware/data windows.
- DMCUB interrupt control: `DMCUB_INTERRUPT_ENABLE`, `DMCUB_INTERRUPT_ACK`, and the beginning of `DMCUB_INTERRUPT_STATUS` define timer, inbox/outbox, GPINT, IH GPINT, undefined address fault, instruction fetch fault, and data write fault fields.

## Important Definitions

The exported interface is the generated macro convention:

- `<REGISTER>__<FIELD>__SHIFT` gives the field's low bit position.
- `<REGISTER>__<FIELD>_MASK` gives the unshifted bit mask within the 32-bit register.
- `//<REGISTER>` comments group definitions by MMIO register.
- `// addressBlock: ...` comments identify hardware address blocks for the following register groups.

Important field families in this chunk:

- `DISP_INTERRUPT_STATUS_CONTINUE` through `CONTINUE5` map pipe/connector events for OPTC data underflow, OTG snapshot/force-count/trigger/vsync/set-v-total-min events, DIGB-DIGF fast-training-complete and video-stream-disable events, HPD2-HPD6 and HPD RX, AUX2-AUX6 software/link-service done events, OTG vertical interrupts, and WBSCL overflow.
- `DISP_INTERRUPT_STATUS_CONTINUE6` through `CONTINUE12` add DPP performance counters, WB/WBSCL performance and overflow, DCCG latch/DRR/perfmon events, MPCC stall events, VGA CRT interrupt, MPC counters, and continuation bits that chain the interrupt-status register bank.
- `DISP_INTERRUPT_STATUS_CONTINUE13` through `CONTINUE18` map HUBBUB VM/timeout/compbuf and perfmon signals, DCPG domain0-domain7 power-up/down events, HUBP0-HUBP7 vblank/vline/vline2/timeout/flip/flip-away events, OPP/OPTC/MMHUBBUB perfmon events, DCIO DPCS TX/RX error events, and AZ perfmon events.
- `DISP_INTERRUPT_STATUS_CONTINUE19` through `CONTINUE25` cover AZ endpoint audio format/enabled/disabled interrupts, DIGG/DIGH fast-training/video-stream-disable events, DCPG domain16-domain21 power-up/down events, DSC0-DSC5 input-underflow/core-error/perfmon events, DMCUB high/low priority inbox/outbox/timer/general data/undefined address fault interrupts, ABM2-ABM5 ready/backlight-update events, DPIA, DMCUB whitelist invalid access, HPO perfmon, and MMHUBBUB warmup.
- Destination registers mirror many of the status families with `*_DEST` fields. These bits select where individual interrupt sources are delivered inside the interrupt handling fabric, so the same source families appear as routing controls rather than status readbacks.
- OTG destination fields repeat per timing generator instance (`OTG0_INTERRUPT_DEST` through `OTG5_INTERRUPT_DEST`) and include CPU subsecond, DRR timing, vupdate, snapshot, force-count, force-vsync-next-line, trigger A/B, GSL vsync gap, vertical0/1/2, vstartup, vready, vsync nominal, no-lock vupdate, and DRR vtotal reach events.
- DMCUB region fields use 64-bit address composition split across low/high offset registers. Offset low fields are shifted by 8 with mask `0xFFFFFF00`, offset-high fields use mask `0x0000FFFF`, and top/base fields use a 29-bit `0x1FFFFFFF` address mask plus a top-address enable bit at bit 31.
- `DMCUB_INTERRUPT_ENABLE`, `ACK`, and `STATUS` share the timer0/timer1, inbox0/1 ready/done, outbox0/1 ready/done, GPINT0-GPINT6, GPINT IH, and undefined-address-fault layout. `DMCUB_INTERRUPT_STATUS` also exposes instruction-fetch and data-write fault status bits in this chunk.

## Control Flow And State Behavior

There is no executable control flow in this header. Runtime behavior occurs when Display Core, IRQ service, or DMUB service code combines these constants with register addresses from `dcn_3_1_4_offset.h` and register helper macros such as `REG_GET`, `REG_SET`, `REG_SET_2`, `REG_UPDATE`, `REG_WRITE`, and generated field-table initializers.

The state represented here is hardware register state:

- Status fields are volatile hardware observations. `DISP_INTERRUPT_STATUS_CONTINUE*`, `RBBMIF_STATUS*`, `RBBMIF_INT_STATUS`, `RBBMIF_STATUS_FLAG`, and `DMCUB_INTERRUPT_STATUS` fields reflect latched or live hardware events such as underflow, vblank/vline, HPD/AUX completion, DCPG power transitions, DPCS errors, DMCUB mailbox/timer/GPINT events, and DMCUB/RBBM faults.
- Destination fields are persistent routing configuration. `*_INTERRUPT_DEST` bits determine how display interrupt sources enter the interrupt handling path; a wrong destination bit can leave a real hardware event unhandled or routed to the wrong consumer.
- RBBMIF timeout controls are persistent diagnostic and fault-handling configuration. Timeout delay/hold fields, timeout-disable bitmaps, and timeout client/status flags influence whether bus/interface stalls are reported and how timeout state is decoded.
- DMCUB region and content-window registers persist memory aperture configuration used by the DMCUB firmware interface. The base/top/offset/high/enable fields define which physical or GPU-address windows the display microcontroller can access.
- DMCUB ACK fields are side-effecting write paths. Interrupt service code typically writes an ACK bit and then clears it back to zero, so generic read/modify/write handling must preserve the intended pulse semantics.
- Continuation bits at bit 31 in most `DISP_INTERRUPT_STATUS_CONTINUE*` registers indicate that another status register must be examined. Consumers that walk the interrupt status chain must not treat each register as an isolated final status word.

Ordering constraints are not encoded in these masks. Correct callers still need to coordinate with IRQ masking, display locks, DMCUB firmware state, power-domain sequencing, mailbox ownership, and MMIO read/write ordering.

## Dependencies And Integration Points

This chunk integrates with:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn314.c`, which includes `dcn_3_1_4_offset.h` and this mask header to build `dmub_srv_dcn314_regs`.
- DMUB field lists such as `dmub_dcn31.h` and `dmub_dcn315.h`, which expand `DMUB_SF(register, field)` into generated mask and shift table entries. Fields from this chunk include DMCUB region top/enable fields and DMCUB interrupt enable/ACK fields.
- DC IRQ service tables such as `display/dc/irq/dcn314/irq_service_dcn314.c`, which reference DMCUB interrupt ACK fields for DMCUB outbox interrupt handling.
- OPTC/OTG resources and timing-generator code, including DCN 3.1/3.1.4 OPTC headers, which use `OTG*_INTERRUPT_DEST` fields to route vertical, vupdate, snapshot, DRR, and trigger interrupts.
- Display resource and hardware-sequencing code that lists and writes `RBBMIF_TIMEOUT_DIS` and `RBBMIF_TIMEOUT_DIS_2`, including timeout-disable setup in the DCE/DCN hardware sequence.
- DMUB service code for later DCN generations that shows the same programming pattern for `DMCUB_REGION3_CW*` windows: write low/high offsets, write base address, then set top address and enable fields with `REG_SET_2`.
- IV source ID headers under `include/ivsrcid/dcn/`, which map named interrupt sources such as HPD, AUX, DIG fast training, and video stream disable to corresponding `DISP_INTERRUPT_STATUS_CONTINUE*` fields.
- Display diagnostics, perfmon, and debug paths that depend on perf counter interrupts, RBBM timeout readbacks, DSC error/underflow signals, DPCS errors, HUBP timeout/flip/vblank/vline events, and DMCUB fault bits.

Because this file is generated, many dependencies are indirect through macros. A macro name mismatch tends to fail at compile time where the field is referenced, but a numeric mask/shift drift can compile cleanly and misprogram MMIO at runtime.

## Risks And Maintenance Notes

- Numeric drift from the DCN 3.1.4 register specification is the primary risk. Incorrect masks or shifts can misroute interrupts, miss latched faults, program DMCUB memory windows incorrectly, or acknowledge the wrong DMCUB event.
- The continuation status chain is easy to truncate. Missing a `DISP_INTERRUPT_STATUS_CONTINUE*_MASK` bit can hide later-register events such as DMCUB mailbox interrupts, DSC faults, ABM events, or MMHUBBUB warmup.
- Destination fields are configuration, not status. Treating `*_INTERRUPT_DEST` bits like harmless readback fields can change interrupt delivery behavior and break HPD, AUX, vblank/vline, DMUB, DSC, audio, or power-domain event handling.
- The register names are highly repetitive across instances. Prefix mistakes such as `OTG4` versus `OTG5`, `AUX5` versus `AUX6`, `DIGG` versus `DIGH`, or `DCPG_INTERRUPT_DEST` versus `DCPG_INTERRUPT_DEST2` can target a different hardware block while still compiling if the mistaken macro exists.
- DMCUB memory region fields are address-sensitive. Base/top fields expose only 29 bits, low offsets are 256-byte aligned, and high offsets are split into separate registers; callers must validate ranges and preserve alignment before packing values.
- DMCUB ACK bits are side-effecting. Read/modify/write helpers that leave an ACK bit set or clear unrelated bits can lose interrupts or generate repeated acknowledgements.
- RBBMIF timeout and security fields affect fault visibility and access permissions. Disabling timeout sources or programming trust/source fields incorrectly can hide real bus faults or create invalid DMCUB access behavior.
- Some event names reflect hardware spelling, including `OCCURED` and `INTERRPUT`; generated names must be preserved exactly because driver code depends on the macro spelling.
- This chunk starts and ends mid-file. It begins after the initial `DISP_INTERRUPT_STATUS` shift definitions and ends before the rest of `DMCUB_INTERRUPT_STATUS` and following DMCUB registers; the merge lane must combine adjacent chunks for a complete per-file report.

## Test Signals

Useful validation signals for this chunk are compile-time, generated-header consistency, and display/DMUB hardware behavior:

- Build AMDGPU with DCN 3.1.4 support and ensure all generated field names used by DMUB, IRQ, OPTC, resource, and hardware-sequencing code resolve.
- Run generated-header consistency checks that every field has the expected `_SHIFT`/`_MASK` pair, masks fit in 32 bits, continuation bits occupy bit 31 where expected, and fields do not overlap unexpectedly within each register.
- Exercise HPD and HPD RX events across HPD1-HPD6, and verify the expected `DISP_INTERRUPT_STATUS_CONTINUE*` bits and `HPD_INTERRUPT_DEST` routing behavior.
- Exercise AUX and I2C/DDC transactions, including software done, link-service done, hardware done, DDC read-request, and AUX GTC sync lock/error paths.
- Run vblank/vline/vline2, flip, flip-away, vupdate, vertical0/1/2, snapshot, DRR timing, and force-count/force-vsync timing tests across active OTG/HUBP instances.
- Exercise DisplayPort link events that map to DIG fast-training-complete and video-stream-disable interrupts for DIGB through DIGH.
- Validate DCPG power-up/down interrupts for domain0-domain7 and domain16-domain21 during display power sequencing, suspend/resume, and power-gating transitions.
- Run DSC-enabled modes and check DSC input-underflow/core-error/perfmon interrupts for DSC0-DSC5.
- Verify DMCUB mailbox and GPINT flows, including DMCUB high/low priority inbox/outbox ready/done, timer, general data in/out, GPINT, GPINT IH, undefined address fault, whitelist invalid access, instruction fetch fault, and data write fault reporting/ACK behavior.
- Exercise DMUB region programming during firmware boot and reinitialization, confirming base/top/offset/high/enable programming produces valid windows and that readbacks match expected alignment and ranges.
- Trigger or simulate RBBMIF timeout diagnostics where available, checking timeout delay/hold configuration, timeout-disable registers, decoded client status, timeout address/op/read-write status, and secure/nonsecure status flags.
- Run audio enable/disable/format-change tests for AZ endpoints 0-7 and verify status and destination bits correspond to the expected endpoint.

## Chunk-Specific Summary

Lines 12037-14354 define a dense DCN 3.1.4 register-field surface for interrupt status, interrupt routing, RBBMIF/DMCUB fault state, DMCUB memory apertures, and DMCUB interrupt enable/ACK/status control. Correctness depends on exact generated masks and shifts, preserving hardware spelling and instance prefixes, walking the `DISP_INTERRUPT_STATUS_CONTINUE*` chain fully, programming DMCUB region fields with correct alignment/range, and handling side-effecting ACK and timeout/security fields with the required MMIO sequencing.
