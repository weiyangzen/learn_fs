# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_4_2_0_sh_mask.h lines 64690-67202

## Purpose

This chunk is generated AMD DCN 4.2.0 register-field metadata. It contains no executable C logic; it exports C preprocessor constants that describe bit shifts and masks for MMIO register fields. AMDGPU display code pairs these definitions with `dcn_4_2_0_offset.h` and register helper macros to pack, update, and read individual fields without hard-coding bit positions.

The range covers the tail of HDMI transmitter packet/audio/control definitions, HPO HDMI stream/link/FRL encoder support blocks, HPO top clock/performance controls, ABM backlight and adaptive-brightness blocks for instances 0 through 3, DPIA MU and DPIA glue/performance-counter fields, the Azalia/HDA controller command transport block, endpoint immediate-command windows, and output stream descriptors for Azalia streams 0 through the beginning of stream 6. It starts mid-register in `HDMI_TB_ENC_GENERIC_PACKET_CONTROL1` and ends mid-register in `AZSTREAM6_1_OUTPUT_STREAM_DESCRIPTOR_FORMAT`; both partial boundaries must be reconciled with adjacent chunks.

Although the repository path is under a local `ceph-client` mirror, this file is AMDGPU display hardware metadata. It does not implement Ceph or distributed filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, includes, allocation paths, locks, callbacks, or direct MMIO operations in this chunk. The exported interface is the generated macro convention:

- `<REGISTER>__<FIELD>__SHIFT`: the bit position for a field.
- `<REGISTER>__<FIELD>_MASK`: the bit mask for isolating or updating the field.
- `// addressBlock:` comments group the generated definitions by hardware block; they are not C syntax, but they preserve the register-database layout for humans and tools.

This line range contains 2,091 `#define` lines: 1,034 shift macros and 1,057 mask macros. Major register families are:

- `HDMI_TB_ENC_*`: HDMI transmitter generic-packet controls, immediate-send and pending bits, per-packet line selection/EMP flags, double-buffer pending/disable status, ACR CTS/N programming and status for 32/44.1/48 kHz families, buffer prefill and memory-power controls, metadata packet control, active/blank timing fields, CRC configuration/result fields, EESS encryption control, borrow mode, and input FIFO error status.
- `APG9_*`, `VPG9_*`, and `DME9_*`: HPO HDMI stream encoder audio packet generator, video packet generator, and dynamic metadata engine fields. These include generic packet byte/index windows, frame and immediate update controls for generic packets 0-14, lock/conflict status, ISRC data windows, metadata requestor selection, engine enable, double-buffer state, missed-transmission flags, and memory-power controls.
- `HDMI_LINK_ENC_*` and `HDMI_FRL_ENC_*`: HDMI link encoder enable/reset/clock fields plus FRL lane count, link training, scrambler disable, per-lane training pattern, jitter-threshold, meter-buffer, and memory-power fields.
- `HPO_TOP_*`, `DP_STREAM_MAPPER_CONTROL*`, and `DC_PERFMON23_*`: top-level HPO clock enables/status for HDMI/FRL/DP stream and link encoders, stream mapping controls, and HPO performance-monitor counter selection, state, compare/increment interrupt setup, and counter readback fields.
- `ABM0_*` through `ABM3_*`: four adaptive backlight management instances. Each instance defines PWM ambient/user/target/current/final/minimum levels, ABM/PWM control and update-rate fields, ABM enable/bypass, IPCSC coefficient selection, ACE PWL index/data/lock fields, missed-frame/read-progress status, histogram and luma-stat controls, luma sums/min/max/pixel counts, threshold/count registers, sample rates, histogram bin shift/index/result windows, and the backlight master lock.
- `DPIA_MU_*`, `DPIA_GLUE_CTRL`, and `DPIA_PERF_COUNT_*`: USB4/DPIA message-unit clocks, per-port clock/reset controls for ports 0-3, TPI credit/status fields, per-port and local interrupt status/masks/acknowledgements, RBBMIF timeout and invalid-access status, microsecond reference divider, hidden-port status, glue debug bus selectors, six performance-counter controls, counter index/data, and spare bits.
- `GLOBAL_CAPABILITIES`, version, payload capability, global control/status, wake/state-change, interrupt control/status, wall clock, stream synchronization, CORB/RIRB, immediate command, and DMA position fields: the Azalia/HDA controller view of stream counts, reset/accept-unsolicited controls, codec wake/status bits, per-stream interrupt masks/status, stream sync bits, command output ring and response input ring base pointers/pointers/control/status/sizes, immediate command output/data/index/response/status, DMA position base addresses, and wall-clock alias.
- `AZENDPOINT1_*`, `AZINPUTENDPOINT1_*`, and `AZROOT1_*`: small endpoint/root immediate command data/index windows.
- `AZSTREAM0_1_*` through `AZSTREAM6_1_*`: output stream descriptor control/status, link position, cyclic buffer length, last valid index, FIFO size, format, buffer descriptor list lower/upper base address, and position alias fields. The stream 6 format register is only partially included in this chunk.

## Control Flow

This header has no local control flow. Runtime sequencing is supplied by AMDGPU display and audio code:

1. DCN 4.2 components include `dcn_4_2_0_offset.h` and this shift/mask header.
2. Resource, IRQ, clock, GPIO, DMUB, link, audio, ABM, and diagnostics code token-pastes symbolic register/field names into register tables and helper calls.
3. Runtime paths use helpers such as `REG_READ`, `REG_WRITE`, `REG_GET`, `REG_SET`, `REG_UPDATE`, `REG_UPDATE_N`, and indexed variants to touch the fields described here.
4. The numeric masks and shifts determine which bits are read or written while programming HDMI packets and FRL training, sending metadata, enabling HPO clocks, collecting perf counters, controlling ABM/backlight state, routing DPIA/USB4 events, handling HDA command rings, and starting/stopping audio stream DMA.

The macros do not encode ordering constraints. Consumers must still follow hardware sequencing for generic-packet double buffering, immediate-send pending polling, metadata DB handoff, FRL/link training, memory power transitions, ABM histogram/luma-stat latching, DPIA interrupt acknowledgement, CORB/RIRB setup, immediate command busy/result-valid polling, and HDA stream reset/run programming.

## State And Persistence Behavior

This chunk stores no software state and persists nothing to disk. It describes hardware-backed state:

- HDMI/HPO state includes packet scheduling, immediate packet pending bits, line references, ACR CTS/N values and readbacks, metadata enable/missed flags, buffer levels, memory power state, CRC result state, link/FRL enable/training/scrambler state, and clock-on status.
- ABM state includes PWM input/output levels, automatic brightness controls, ACE PWL programming, missed-frame/read-progress flags, histogram bins/results, luma statistics, sample rates, and master-lock state for each of four instances.
- DPIA state includes per-port clock/reset control, TPI credit counts, interrupt and acknowledgement state, timeout and invalid-access diagnostics, port hidden-status bits, debug bus selection, and performance-counter values.
- Azalia controller state includes global capability and reset/status bits, wake/status/interrupt masks, stream synchronization, wall-clock counter, CORB/RIRB DMA ring base addresses/pointers/control/status/sizes, immediate command windows, and DMA position buffer base addresses.
- Azalia stream state includes stream reset/run, interrupt enables and sticky status bits, FIFO ready/error, traffic priority, stream number, DMA position, cyclic-buffer length, last valid BDL index, format fields, BDL base address, and position alias readback.

Persistence is hardware-defined. Configuration fields typically remain until modeset, audio reconfiguration, power gating, suspend/resume, GPU reset, or driver reinitialization. Pending, missed, busy, interrupt, reset, FIFO-ready, error, timeout, read-progress, status-clear, and acknowledgement fields may be transient, sticky, self-clearing, write-one-to-clear, read-only, or only valid while their clock and power domains are active. This generated header does not express access type, volatility, reset values, or side effects.

## Dependencies And Integration Points

This chunk depends on AMD's generated DCN 4.2.0 register database and must stay synchronized with:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_4_2_0_offset.h`, which provides matching register offsets and base-index selectors.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn42/dcn42_resource.c`, which includes this header for DCN 4.2 resource/register-table construction.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn42.c`, which includes the generated offset and shift/mask headers for DCN 4.2 DMUB register access.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn42/irq_service_dcn42.c`, which includes this header for DCN 4.2 interrupt table definitions.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn42/dcn42_clk_mgr.c`, which includes this header for DCN 4.2 clock-manager register access.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn42/hw_factory_dcn42.c` and `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn42/hw_translate_dcn42.c`, which include this header for GPIO/HPD/AUX translation on DCN 4.2 hardware.
- Shared display code for ABM/backlight, HDMI/HPO packet generation, FRL/link training, DPIA/USB4 routing, HDA/Azalia audio, perfmon diagnostics, and register dump/debug paths.

The integration contract is mostly macro spelling plus numeric bit layout. Missing or renamed macros usually fail at compile time through token-pasted register tables. Incorrect numeric values are more dangerous because the build can succeed while runtime code reads or writes the wrong hardware bits.

## Risks And Edge Cases

- These are untyped preprocessor constants. A bad mask or shift can compile cleanly and still corrupt adjacent fields or read misleading status.
- The chunk is partial at both ends. `HDMI_TB_ENC_GENERIC_PACKET_CONTROL1` begins in the previous chunk, and `AZSTREAM6_1_OUTPUT_STREAM_DESCRIPTOR_FORMAT` continues in the next chunk.
- Generic-packet and metadata fields have update, pending, lock, conflict, missed, DB taken, and DB disable bits. Using masks without the expected double-buffer or pending-bit sequencing can drop HDMI infoframes, metadata, ISRC, or other generic packets.
- HDMI ACR, timing, FRL, and link encoder fields are user-visible. Bad values can cause audio clock recovery errors, link-training failures, blank output, CRC mismatches, or unstable HDMI FRL behavior.
- Memory-power fields appear in HDMI buffer, APG, VPG, DME, and FRL blocks. Status bits may be invalid when clocks are gated, and force/disable bits can interact with broader power-management policy.
- ABM fields mix live statistics, latch/read-progress state, missed-frame flags, PWL programming, locks, and PWM levels. Wrong masks can create brightness jumps, stale histogram/luma reads, missed-frame loops, or incorrect backlight duty-cycle updates.
- DPIA MU fields cover clocks, resets, interrupts, TPI credits, timeout diagnostics, and per-port state. Incorrect interrupt masks or acknowledgements can hide USB4/DPIA port events, leave resets incomplete, or misdiagnose RBBMIF timeouts.
- HDA CORB/RIRB and DMA position fields include base-address alignment and unimplemented low bits. Treating them as unconstrained full-width addresses can break command transport or DMA position reporting.
- Immediate command status requires busy/result-valid handling. Masks alone do not provide the polling/timeout logic needed to avoid stale codec responses.
- Azalia stream descriptors contain reset/run bits, interrupt enable/status bits, error flags, FIFO-ready status, stream number, format, BDL base address, and cyclic-buffer metadata. Wrong fields can cause no audio, descriptor errors, FIFO errors, incorrect sample format, or DMA overrun/underrun behavior.
- Repeated ABM and AZSTREAM instances are copy-sensitive. Testing only ABM0 or stream0 can miss an instance-specific generated typo in ABM3 or stream6.

## Test Signals

Useful validation combines generated-header consistency checks with DCN 4.2 hardware behavior:

- Build AMDGPU display support with DCN 4.2 enabled. DMUB, IRQ, clock-manager, GPIO, resource, audio, ABM, HDMI, DPIA, and diagnostics code should catch missing or renamed symbols.
- Mechanically verify every complete field in this range has both a `__SHIFT` and `_MASK` definition, allowing for the deliberate boundary exceptions in `HDMI_TB_ENC_GENERIC_PACKET_CONTROL1` and `AZSTREAM6_1_OUTPUT_STREAM_DESCRIPTOR_FORMAT`.
- Diff this slice against AMD's authoritative DCN 4.2.0 register database and the paired `dcn_4_2_0_offset.h`; repeated ABM0-3 and AZSTREAM0-6 layouts should match the expected per-instance schema.
- Exercise HDMI output paths that program generic packets, metadata packets, ISRC data, ACR CTS/N, active/blank timing, CRC collection, EESS/AVMUTE-related behavior, and input FIFO error reporting.
- Exercise HPO HDMI FRL modes, including link encoder reset/enable, clock-on status, FRL lane count/training patterns, scrambler control, jitter/meter-buffer status, and FRL memory power transitions.
- Exercise ABM/backlight control on all exposed instances: PWM ambient/user/target/current/final/minimum levels, auto-update behavior, ACE PWL programming, histogram/luma-stat sampling, missed-frame clears, result-index/data reads, and master-lock behavior.
- Exercise DPIA/USB4 flows across ports 0-3 and interrupt/status coverage for ports 0-5: clock/reset sequencing, TPI credit counts, local interrupt acknowledge, timeout diagnostics, hidden-port state, glue debug selection, and performance counters.
- Exercise HDA/Azalia controller command paths: global reset, CORB/RIRB base pointer and size setup, write/read pointer handling, DMA enable/status, immediate command output/response polling, DMA position buffer programming, and wall-clock readback.
- Exercise output audio stream descriptors for streams 0-6: reset/run transitions, stream number assignment, interrupt enables/status clears, FIFO ready/error handling, cyclic buffer length, last valid index, BDL lower/upper base address alignment, link position alias, and format fields for channel count, bits per sample, divisor/multiple, and base rate.
- Monitor display/audio logs, DC traces, link-training traces, hotplug/audio events, register dumps, CRC results, ABM brightness behavior, RBBMIF timeout reports, FIFO/descriptor errors, and suspend/resume behavior as high-signal indicators of bad field metadata.

## Cross-Chunk Notes

The previous chunk owns the beginning of `HDMI_TB_ENC_GENERIC_PACKET_CONTROL1`; this chunk starts with the masks for generic packet 8-14 in that register and then owns `HDMI_TB_ENC_GENERIC_PACKET_CONTROL2` and the following HDMI/HPO/ABM/DPIA/Azalia blocks through the first five fields of `AZSTREAM6_1_OUTPUT_STREAM_DESCRIPTOR_FORMAT`. The next chunk owns the remaining stream6 format masks, stream6 BDL pointer and position-alias fields, stream7 descriptors, and the closing guard. The merge lane should preserve this source path and line range and reconcile the boundary-split registers before producing the final per-file report.
