# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_0_offset.h lines 15502-18022

## Purpose

This chunk is the tail of the generated AMDGPU DCN 3.0 register offset header. It contains no executable logic; its public interface is preprocessor constants mapping symbolic display/audio hardware register names to register offsets plus companion `*_BASE_IDX` constants used by AMD display register-table macros.

The path is under a local `ceph-client` source mirror, but this file is AMD display-controller hardware metadata. It does not implement Ceph or distributed filesystem behavior.

The range starts in the middle of the MPC RMU color pipeline register table, then covers DC performance monitor instances, AFMT/VPG/DME audio packet blocks, HPO clock control, six ABM blocks, Azalia controller and endpoint registers, legacy VGA indirect register offsets, Azalia stream descriptors, eight Azalia output endpoints, eight Azalia input endpoints, and the final `#endif` for the include guard.

Within lines 15502-18022 there are 2,286 `#define` entries: 1,677 register-address macros and 609 `*_BASE_IDX` macros.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, or runtime storage objects in this chunk. The important API surface is the generated macro namespace consumed by DCN 3.0 register descriptors:

- `mmMPC_RMU0_*`, `mmMPC_RMU1_*`, and `mmMPC_RMU2_*`: remaining multi-plane compositor RMU shaper and 3D LUT offsets. This includes shaper offsets/scales, LUT index/data/write masks, RAM A/B start/end/region controls, 3D LUT mode/index/data/read-write controls, output normalization, and output RGB offsets. The chunk begins in the middle of RMU0 shaper entries and later includes RMU1/RMU2 entries.
- `mmDC_PERFMON28_*` and `mmDC_PERFMON29_*`: DC performance counter control, state, count value, high/low counter, and interrupt/misc offsets.
- `mmAFMT6_*`, `mmVPG6_*`, and `mmDME6_*`: display audio packet formatter, video packet generator, and DME offsets for instance 6. These cover audio info packets, IEC 60958 channel-status data, CRC controls/results, ramp controls, generic packet access/data/status, ISRC/MPEG info, and memory power controls.
- `mmHPO_TOP_CLOCK_CONTROL`: high-performance output top clock-control offset. This is referenced by DCN hardware sequencing code for HDMI stream clock gating fields through the matching mask header.
- `mmABM0_*` through `mmABM5_*`: adaptive backlight management register offsets for six instances. Each instance maps PWM user/target/current/final/minimum duty state, ABM control, update sample rate, group lock, ACE slope/threshold controls, histogram/luma statistics controls/results, sample rates, histogram bin shift indexes, 24 histogram result registers, and backlight master lock.
- `mmAZALIA_*`, `mmAUDIO_*`, `mmCORB_*`, `mmRIRB_*`, `mmIMMEDIATE_COMMAND_*`, `mmWALL_CLOCK_*`, `mmDMA_*`, and `mmRESPONSE_*`: Azalia/HDA controller register offsets for global capabilities, stream position, input/output payload capability, wake, state change, GCTL, CORB/RIRB, immediate commands, wall clock, SSYNC, DMA position lower-base, interrupt control/status, and response interrupt count.
- `mmAZF0ENDPOINT_*` and `mmAZF0INPUTENDPOINT_*`: top-level Azalia endpoint and input endpoint index/data offsets used to access codec endpoint-indirect register spaces.
- `ixSEQ*`, `ixCRT*`, `ixGRA*`, and `ixATTR*`: legacy VGA sequencer, CRT controller, graphics-controller, and attribute-controller indirect offsets.
- `ixAZENDPOINT_*`, `ixAZINPUTENDPOINT_*`, `ixAZROOT_*`, `ixAZF0STREAM*_*`, `ixAZF0ENDPOINT*_*`, and `ixAZF0INPUTENDPOINT*_*`: Azalia codec/function/stream/endpoint/input-endpoint indirect offsets. These cover codec function parameters, stream descriptor controls, endpoint converter and pin widgets, ELD/sink info, audio descriptors, multichannel control, HBR capability, channel allocation, hotplug/audio-enable control, unsolicited responses, configuration defaults, LPIB snapshots, input activity, and infoframe state.

Names prefixed with `mm` are normal memory-mapped register offsets. Names prefixed with `ix` are indirect register indexes used through an index/data register pair. The companion `*_BASE_IDX` value selects a generated register base via the display driver's `BASE(...)` macro before the offset is added.

## Control Flow

This header chunk has no local control flow. It is declarative register layout data used by code that constructs tables and then performs MMIO or indirect register accesses.

Runtime use follows this broad pattern:

1. DCN 3.0 display code includes `dcn_3_0_0_offset.h` with `dcn_3_0_0_sh_mask.h`.
2. Resource files expand macros such as `SR(...)`, `SRI(...)`, `SRII(...)`, and `SRII_MPC_RMU(...)` into absolute register offsets by adding `BASE(mm..._BASE_IDX)` to the generated `mm...` offset.
3. Subsystems pass those register tables to typed display objects such as MPC, AFMT, audio, IRQ, GPIO, clock-manager, and DMUB helpers.
4. Runtime helpers use `REG_READ`, `REG_WRITE`, `REG_SET`, `REG_UPDATE`, `REG_GET_FIELD`, `AZ_REG_READ`, and `AZ_REG_WRITE` against those tables and the matching shift/mask metadata.

For indirect Azalia and VGA entries, this file only defines the index values. The actual sequence is performed by consumers: write the desired `ix...` index to the endpoint/index register, then read or write the paired data register.

The macros do not encode sequencing rules. Clock enablement, power gating, register locking, double-buffer latching, interrupt acknowledgement, and index/data access ordering are enforced by the consuming driver code and the hardware specification, not by this generated header.

## State And Persistence Behavior

This chunk stores no software state and persists nothing. It describes hardware-visible state held in DCN 3.0 display and audio registers.

The represented hardware state includes:

- MPC/RMU color state: shaper LUT programming, RAM A/B piecewise-linear region definitions, 3D LUT mode/index/data, 30-bit 3D LUT access, output normalization, output RGB offsets, and RMU memory/pipeline state accessed through adjacent register tables.
- Performance-monitor state: perf counter selection/control, active counter state, current counter values, high/low readback words, and interrupt/misc status for `DC_PERFMON28` and `DC_PERFMON29`.
- Audio packet state: AFMT audio info, IEC 60958 channel-status words, packet controls, CRC generation/checking, ramp controls, source control, status/interrupt state, and AFMT/VPG/DME memory power state.
- ABM/backlight state: ambient/user/target/current/final duty levels, minimum duty cycle, ABM enable/control state, sample rates, group locks, ACE tone-mapping coefficients/thresholds, histogram/luma-statistic accumulators, histogram result bins, and backlight master locks.
- HDA/Azalia controller state: CORB/RIRB command rings, immediate command/response registers, wall clock, stream synchronization, DMA position buffer base, interrupt controls/status, global controller state, stream position, and payload capability.
- Azalia endpoint state: converter formats, stream/channel IDs, digital converter controls, pin capabilities, hotplug/audio-enable state, ELD and sink info, audio descriptors, channel allocation, HBR and multichannel settings, unsolicited responses, configuration defaults, LPIB snapshots, input activity, and infoframe data.
- Legacy VGA indirect state: indexed sequencer, CRT controller, graphics-controller, and attribute-controller registers retained for compatibility paths.

Persistence is entirely hardware-dependent. Some registers are stable configuration until modeset, suspend/resume, power-gating transition, audio reconfiguration, or ASIC reset. Others are counters, snapshots, status bits, sticky interrupts, command ring pointers, write-one-to-clear acknowledgements, or index/data windows with side effects. Names containing `STATUS`, `INTERRUPT`, `ACK`, `RIRB`, `CORB`, `IMMEDIATE_COMMAND`, `LPIB`, `CRC`, `RESULT`, `READ_PROGRESS`, `CLOCK`, `MEM_PWR`, and `LOCK` should be treated as side-effect-sensitive unless the consumer path proves otherwise.

## Dependencies And Integration Points

The required companion for this offset header is:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_0_sh_mask.h`

Direct include points for the DCN 3.0 offset/mask pair in this tree include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn30/dcn30_resource.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn30/irq_service_dcn30.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn302/irq_service_dcn302.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn30/hw_factory_dcn30.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn30/hw_translate_dcn30.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn30/dcn30_clk_mgr.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn30.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn302.c`

Notable consumers and integration paths:

- `dcn30_resource.c` and related DCN 3.0/3.02 resource files use `SR`, `SRI`, `SRII`, and `SRII_MPC_RMU` macros to build typed register tables from this header's `mm...` and `*_BASE_IDX` definitions.
- `display/dc/mpc/dcn30/dcn30_mpc.h` declares the MPC/RMU register and field list shapes used to program shaper LUTs and 3D LUTs. DCN 3.x resource files instantiate RMU register lists for RMU instances using this offset header.
- `display/dc/dce/dce_audio.c` uses audio and Azalia abstractions such as `AZ_REG_READ` and `AZ_REG_WRITE` for endpoint/pin-indirect accesses. It depends on endpoint index/data offsets plus the indirect `ixAZ...` register numbers represented in this chunk.
- `display/dc/hwss/dce/dce_hwseq.h` includes hardware sequencer register fields for `AZALIA_AUDIO_DTO`, `AZALIA_CONTROLLER_CLOCK_GATING`, and `HPO_TOP_CLOCK_CONTROL`; this chunk contains the HPO top clock-control offset used with the matching field masks.
- IRQ, GPIO, clock-manager, and DMUB files include the same generated pair so interrupt source setup, pin translation, clock programming, and firmware-mediated display control use one register contract for the ASIC generation.

## Risks And Edge Cases

- These macros are a hardware ABI. A wrong offset or base index can compile cleanly while redirecting reads/writes to the wrong register, producing blank displays, incorrect color transforms, audio loss, bad hotplug behavior, broken backlight control, interrupt storms, or register access hangs.
- The chunk starts mid-table for MPC RMU0. Complete RMU coverage requires adjacent chunks; this chunk alone should not be treated as the full RMU register map.
- Repeated instance blocks create copy/paste drift risk. `MPC_RMU0/1/2`, `ABM0` through `ABM5`, `AZF0STREAM0` through `AZF0STREAM15`, `AZF0ENDPOINT0` through `AZF0ENDPOINT7`, and `AZF0INPUTENDPOINT0` through `AZF0INPUTENDPOINT7` are highly regular. A single instance-specific offset error may only fail on one pipe, one link, or one audio endpoint.
- `mm` and `ix` namespaces are not interchangeable. Treating an indirect codec index as an MMIO offset, or skipping the endpoint index/data access sequence, can read or write unrelated hardware state.
- `*_BASE_IDX` is part of the address calculation. Using an offset without its base, or using the wrong base index, is especially risky in this chunk because it spans MPC, OPP/ABM, HPO, HDA, AFMT/VPG/DME, and indirect spaces.
- Audio command rings and stream pointers are side-effect-sensitive. CORB/RIRB, immediate command, stream descriptor, DMA position, LPIB, and unsolicited response registers require ordering and acknowledgement discipline outside this header.
- ABM and backlight registers affect visible panel brightness and content-adaptive processing. Bad offsets can cause flicker, incorrect brightness, stuck ABM locks, invalid histogram/luma reads, or user brightness controls that appear to work only on some instances.
- RMU shaper and 3D LUT registers affect color pipeline programming. Errors can produce subtle color inaccuracies, failed LUT loads, stale RAM bank reads, or corruption limited to particular planes or RMU instances.
- HPO and audio clock-control offsets are tied to power management. Accessing clock-gated or memory-powered-down blocks at the wrong time can return stale data or drop writes.
- Legacy VGA indirect offsets are compatibility state. Even though modern display paths rarely depend on them, accidental changes can regress boot console, VGA fallback, or low-level diagnostic paths.

## Test Signals

Useful validation is a mix of compile-time checks and hardware behavior:

- Build AMDGPU/DC with DCN 3.0 and DCN 3.02 support. Missing or renamed macros should fail at resource, IRQ, GPIO, clock-manager, DMUB, MPC, audio, and hardware-sequencer table initializers.
- Diff this generated range against AMD's source register database and adjacent DCN generation headers to catch instance drift across RMU, ABM, AFMT/VPG/DME, stream, endpoint, and input-endpoint blocks.
- Exercise hardware with enough active displays and audio endpoints to use AFMT/VPG/DME instance 6, multiple ABM instances, and multiple Azalia endpoints. Validate modeset, hotplug, DPMS, suspend/resume, and audio route changes.
- Run color-management tests that program shaper LUTs and 3D LUTs through MPC/RMU, including 30-bit LUT paths, bank switching, readback where supported, and multi-plane or multi-pipe configurations.
- Validate ABM and backlight behavior: user brightness changes, content-adaptive brightness transitions, histogram/luma-statistic reads, lock/unlock behavior, and resume from low-power states.
- Test HDMI/DP audio: stream format changes, channel allocation, HBR formats, multichannel layout, ELD/sink info updates, hotplug audio enable/disable, unsolicited response handling, and LPIB snapshot/readback.
- Stress HDA controller command paths: CORB/RIRB traffic, immediate command responses, interrupt status/ack handling, stream reset/run transitions, and DMA position buffer updates.
- Use perfmon/debug tooling to configure `DC_PERFMON28` and `DC_PERFMON29`, start and stop counters, read high/low values, and verify interrupt/status behavior.
- Monitor kernel logs and display diagnostics for register access failures, audio timeouts, underflow/flicker, unexpected hotplug events, IRQ storms, backlight regressions, color LUT mismatches, and resume failures.

## Cross-Chunk Notes

Lines before 15502 define the earlier part of the MPC RMU0/RMU2 register tables and other DCN 3.0 offset namespaces. This chunk begins at `mmMPC_RMU0_SHAPER_RAMA_REGION_4_5_BASE_IDX`, so the RMU0 shaper list is incomplete at the top boundary. The chunk ends with the file's include-guard `#endif`, so there is no later source chunk for this header after line 18022.
