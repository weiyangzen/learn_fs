# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_2_sh_mask.h lines 7203-9815

## Scope And Purpose

This chunk is part of AMDGPU's generated DCN 3.0.2 shift/mask header. It contains C preprocessor constants only: no functions, structs, enums, storage, branches, loops, or local policy. The exported surface is a set of `REGISTER__FIELD__SHIFT` and `REGISTER__FIELD_MASK` macros that describe bit offsets and already-positioned masks for memory-mapped display-controller registers.

The range spans 2,613 source lines and 2,065 `#define` entries. It starts at the final mask for `AZALIA_CONTROLLER_CLOCK_GATING`, covers Azalia/HDA audio, DCHUBBUB memory/VM/arbitration/performance, VM request/fault context registers, the first HUBP0/HUBPREQ0/HUBPRET0/cursor0 instance, DC performance monitor 5 and 6 blocks, and ends after the first fields of `HUBP1_DCSURF_ADDR_CONFIG`. Because the start and end are both chunk boundaries inside larger register groups, file-level reconciliation must merge adjacent chunks before making whole-file completeness claims.

The purpose is to let DCN302 display code program hardware fields through symbolic masks rather than open-coded bit constants. The companion `dcn_3_0_2_offset.h` supplies matching register addresses and base indices, while DCN302 resource code includes both generated headers and builds register tables for hubbub, VMID, HUBP, audio, stream encoder, and hardware sequencer components.

Although the repository path is under `sources/distributed-fs/ceph-client`, this file is AMD display hardware metadata. It has no Ceph, filesystem, distributed-storage, or network protocol behavior.

## Register Blocks Covered

The opening audio section completes an Azalia clock-gating field and then defines Azalia audio DTO, SOC clock, underflow filler, DMA cache/snoop/isochronous controls, cyclic-buffer sync, payload capability, stream arbiter, input/output CRC controls and results, and audio memory-power force/status fields.

`dce_dc_hda_azf0root_dispdec` covers HDA function-zero codec root parameters and controls: vendor/device and revision IDs, channel-count controls, resync FIFO startup keepout, function parameter capabilities, power-state set/actual state, codec reset, subsystem ID response bytes, converter synchronization, audio port connectivity overrides, GTC group offsets, and register-backed connectivity overrides.

The `AZF0STREAM8` through `AZF0STREAM15` blocks expose indexed stream register access through `AZALIA_STREAM_INDEX` and `AZALIA_STREAM_DATA`. The `AZF0INPUTENDPOINT0` through `AZF0INPUTENDPOINT7` blocks similarly expose indexed endpoint access through input endpoint index/data registers.

`dce_dc_dchubbub_hubbub_sdpif_dispdec` defines SDPIF request/response, credit, force-IO, physical VM request, framebuffer/AGP/local-HBM apertures, per-pipe security levels for DCC metadata, cursor, GPUVM, surface, and DM data requests, SDPIF memory power, snoop control, host-VM security level, and unit-ID masks.

`dce_dc_dchubbub_hubbub_ret_path_dispdec` covers return-path DCC configuration constants, return-path memory power, and DCHUBBUB CRC controls/results.

`dce_dc_dchubbub_hubbub_dispdec` covers DCHUBBUB arbitration and global controls: outstanding request limits, saturation/QoS force, DRAM-state controls, four watermark sets A-D for urgency, self-refresh, and DRAM clock changes, watermark-change sequencing, timeout enable, global timer, surface check addresses/in-use bits, VTG0-VTG4 controls, soft reset, clock gating, DCFCLK gating delays, latency/performance measurement, timeout detection/interrupt status, fractional urgency bandwidth for nominal/flip cases, and `FMON_CTRL`/`FMON_CTRL_1`.

`dce_dc_dchubbub_dchubbub_dcperfmon_dc_perfmon_dispdec` defines DC performance monitor 5. `dce_dc_dcbubp0_dispdec_hubp_dcperfmon_dc_perfmon_dispdec` defines DC performance monitor 6. Both expose counter event selection, counted-value type, run/stop/count-off controls, per-counter state selectors, perfmon state/report count, comparison values, interrupt status/ack fields, and high/low readback.

`dce_dc_dchubbub_hubbub_vmrq_if_dispdec` defines display VM request interface state for contexts 0-15. Each VM context has page-table depth, block size, base address high/low, logical start high/low, and logical end high/low masks. The block also defines default address, default SPA/snoop, VM fault control, status, VMID/table-level/pipe decode, interrupt status, and fault address high/low fields.

`dce_dc_dcbubp0_dispdec_hubp_dispdec` defines the first HUBP instance's surface format, address/tiling configuration, primary/secondary luma and chroma viewport start/dimensions, request-size configuration for luma/chroma, HUBP enable/blank/timeout/underflow control, clock gating/status, VM page size, and DCFCLK/DPPCLK measurement windows.

`dce_dc_dcbubp0_dispdec_hubpreq_dispdec` covers HUBPREQ0 fetch-side state: surface pitch, VMID, primary/secondary and metadata surface addresses, surface control, flip control and interrupt status/clear bits, in-use and earliest-in-use addresses, expansion mode, TTU/QoS controls for surfaces and cursors, DM data VM controls, system aperture and L1 TLB controls, blanking/destination/prefetch/vblank/flip/nominal timing parameters, per-line delivery, cursor request settings, reference-to-pixel frequency conversion, DRQ limit, and request memory-power state.

`dce_dc_dcbubp0_dispdec_hubpret_dispdec` covers HUBPRET0 return-side state: DET buffer base, element packing, crossbar component selection, DET/DMROB/PIXCDC memory power, read-line windows, vblank/read-line interrupt mask/type/clear/status fields, current/snapshot read-line values, and read-line status.

`dce_dc_dcbubp0_dispdec_cursor0_dispdec` covers cursor0 and DM data delivery for HUBP0: cursor enable, mode, security/snoop/system flags, pitch, rotation/mirroring bypass, lines per chunk, latency measurement, address high/low, size, position, hot spot, stereo offsets, destination offset, cursor memory power, DM data address/security flags, hardware and software DM data control, QoS, status, underflow clear, and software payload data.

The final lines begin `dce_dc_dcbubp1_dispdec_hubp_dispdec` by defining `HUBP1_DCSURF_SURFACE_CONFIG` and the first two `HUBP1_DCSURF_ADDR_CONFIG` shifts. The rest of HUBP1 continues in the next chunk.

## Important APIs, Types, And Macros

There are no callable APIs in this chunk. The important contract is the generated macro naming scheme:

- `<REGISTER>__<FIELD>__SHIFT` gives the low bit position of a field.
- `<REGISTER>__<FIELD>_MASK` gives the field mask in register position.
- Register-heading comments, such as `//HUBPREQ0_DCSURF_FLIP_CONTROL`, group field macros by hardware register.
- Address-block comments, such as `// addressBlock: dce_dc_dcbubp0_dispdec_hubpreq_dispdec`, identify generated hardware blocks and replicated instances.

The most operationally important macro families are the Azalia audio DMA/codec/power fields, DCHUBBUB arbitration and watermark fields, VM context and fault fields, HUBP0 surface/request/clock/underflow fields, HUBPREQ0 address/flip/TTU/QoS/prefetch/timing fields, HUBPRET0 read-line and interrupt fields, cursor0 address/mode/DM-data fields, and DC_PERFMON5/6 diagnostics fields.

Several names legitimately contain a logical field named `MASK`, producing identifiers such as `DCHUBBUB_TIMEOUT_INTERRUPT_STATUS__DCHUBBUB_TIMEOUT_INT_MASK_MASK`, `HUBPRET0_HUBPRET_INTERRUPT__PIPE_VBLANK_INT_MASK_MASK`, and `DC_PERFMON*_PERFCOUNTER_CNTL__PERFCOUNTER_OFF_MASK_MASK`. Tooling must not treat the first `_MASK` substring as the generated suffix.

## Control Flow

This header has no local control flow. Runtime behavior is created by consumers that include `dcn_3_0_2_offset.h` and this shift/mask header, assemble register/shift/mask structures, and call AMD display register helpers such as `REG_GET`, `REG_SET`, `REG_UPDATE`, `REG_FIELD`, `SF`, `SRI`, and related generated-list macros.

Typical runtime flows represented by these fields include:

- Audio setup: audio and stream encoder code programs Azalia DMA snoop/isochronous policy, DTO values, payload capability, stream/indexed endpoint access, HDA codec power/reset controls, and audio memory-power state.
- Display memory setup: hubbub code programs framebuffer/AGP/local address ranges, VM contexts, default/fault handling, VM request policy, security levels, and page-table aperture fields.
- Bandwidth and watermarks: DCHUBBUB and HUBPREQ fields encode urgency, self-refresh, DRAM-clock-change, TTU, QoS, prefetch, vblank, flip, nominal, and per-line delivery timing values derived from display-mode and DML calculations.
- Plane programming and flips: HUBP0/HUBPREQ0 fields carry surface format, tiling, pitch, viewport, primary/secondary/meta addresses, flip mode, flip pending/in-use status, and surface update interrupt/clear state.
- Cursor and metadata delivery: cursor0 fields program cursor image location, mode, size, position, hot spot, stereo offsets, memory security/snoop/system attributes, DM data payload location, QoS, and underflow status.
- Diagnostics and interrupt handling: CRC, timeout, force-IO, VM fault, hubp underflow, hubpret vblank/read-line, DM data, and perfmon status/ack fields expose transient hardware state to debug or IRQ paths.

The chunk does not encode whether a field is read-only, write-one-to-clear, self-clearing, sticky, safe only in vblank, or dependent on clocks/power. Those semantics live in the hardware specification and higher-level AMD display code.

## State And Persistence Behavior

The macros themselves hold no mutable state and persist nothing. They describe state in MMIO registers whose lifetime is controlled by the display hardware, the AMD display driver, DMUB/DMCU firmware, modesets, page flips, cursor updates, power transitions, suspend/resume, and GPU reset.

Configuration state includes Azalia audio DMA/cache policy, codec power/reset settings, SDPIF security and snoop policy, DCHUBBUB watermarks, VM page-table base/start/end registers, fault policy, HUBP surface format/tiling/viewports/request sizing, HUBPREQ surface addresses and timing parameters, HUBPRET read-line windows, cursor mode/address/size/position, memory-power force/disable fields, and perfmon event selections.

Live or latched state includes audio CRC completion/results, memory-power status, SDPIF response/credit errors, force-IO sticky status, DCHUBBUB CRC values, surface-check in-use bits, timeout status, VM fault status/address, HUBP timeout/underflow status, flip/in-use/earliest-in-use addresses, DM data fault/underflow/late/done state, HUBPRET read-line/vblank status, cursor/DM data underflow, and perfmon counter/interrupt/readback state.

Several fields are clear or ack bits (`*_CLEAR`, `*_ACK`, `*_STATUS_CLEAR`, `*_UNDERFLOW_CLEAR`, `*_INT_CLEAR`). The header only supplies bit positions; callers must preserve hardware-specific clear semantics when using read/modify/write helpers.

## Dependencies And Integration Points

The direct companion is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_2_offset.h`, which defines matching register addresses and base indices. The main visible include site is `display/dc/resource/dcn302/dcn302_resource.c`, which includes both generated DCN 3.0.2 headers and builds DCN302 register, shift, and mask tables.

Concrete integration points visible in the DCN302 resource path include:

- `dcn302_hubbub_create()`, which constructs the hubbub and VMID objects using generated hubbub and VMID register/mask tables. This ties in the DCHUBBUB, VM context, VM fault, memory aperture, watermark, and arbitration families in this chunk.
- `dcn302_hubp_create()`, which constructs HUBP instances with generated `hubp_regs`, `hubp_shift`, and `hubp_mask`; the HUBP0/HUBPREQ0/HUBPRET0/cursor0 families here form the instance-0 plane fetch and cursor surface.
- `dcn302_create_audio()` and `dcn302_stream_encoder_create()`, which construct audio, VPG, AFMT, and stream encoder resources. The Azalia/HDA macros in this chunk provide the audio-side register fields used by those paths.
- DCN302 hardware sequencer setup, which uses `HWSEQ_DCN302_REG_LIST()` and `HWSEQ_DCN302_MASK_SH_LIST()` tables from generated offsets/masks for power gating, hubp control, and display sequencing.
- IRQ and diagnostics paths that consume timeout, VM fault, underflow, surface flip, vblank/read-line, audio CRC, and perfmon status/ack fields through common DC register helpers.

The broader dependencies are the AMD display core register helper framework, DCN resource creation, DML bandwidth calculations, hubbub/hubp/hubpret/cursor implementations, audio/HDA components, DMUB firmware coordination, and ASIC-version dispatch that selects DCN302 layouts for compatible GPUs.

## Risks And Edge Cases

The primary risk is silent hardware misprogramming. A wrong mask or shift can still compile but cause read/modify/write helpers to update the wrong bits, leave stale state, truncate values, or decode status incorrectly.

Chunk boundaries matter. The first line is only the `AZALIA_CONTROLLER_CLOCK_GATING__CLOCK_ON_STATE_MASK`; its matching shift and register context are in the previous chunk. The final register, `HUBP1_DCSURF_ADDR_CONFIG`, is incomplete in this chunk and continues later. Whole-file research must reconcile adjacent chunks before declaring complete Azalia clock-gating or HUBP1 coverage.

Audio fields affect both display audio and memory/cache policy. Incorrect DMA snoop, isochronous, underflow, DTO, codec power, or stream endpoint masks can produce HDMI/DP audio dropouts, bad HDA responses, broken CRC diagnostics, or low-power audio failures.

DCHUBBUB and HUBPREQ timing fields have high display risk. Bad watermarks, TTU, QoS, prefetch, vblank, flip, nominal, per-line-delivery, or DRQ-limit masks can cause underflow, visible corruption, failed page flips, missed prefetch windows, or unstable memory-clock/self-refresh transitions.

VM context and fault fields are security- and stability-sensitive. Wrong page-table base/start/end, aperture, default address, snoop/SPA, TLB, or fault clear/status masks can route display fetches through the wrong address space, hide faults, report the wrong VMID/pipe, or fault during flip/cursor/DM-data fetches.

HUBP0/HUBPREQ0/HUBPRET0/cursor0 are instance-specific. A generated error in instance 0 can affect only one plane or cursor and may pass tests that happen to light a different pipe. The repeated structure also makes copy/paste or diff review easy to misread.

Interrupt, status, and clear fields are easy to misuse. Fields named `*_STATUS`, `*_INT_STATUS`, `*_CLEAR`, `*_ACK`, `*_UNDERFLOW_CLEAR`, and `*_MASK_MASK` require hardware-specific write semantics; generic tooling or naive suffix parsing can corrupt event handling.

Memory-power fields are compact but broad in effect. Incorrect force/disable/state masks for Azalia, SDPIF, return path, HUBPREQ, HUBPRET, cursor, DET, DMROB, PIXCDC, or CROB memories can create failures that appear only during blanking, runtime power management, suspend/resume, or low-power display states.

## Test Signals

Build-time signals are direct: stale or missing macros should fail compilation in DCN302 resource, hubbub, hubp, audio, stream encoder, hardware sequencer, IRQ, and register-list paths around generated `SF`, `SRI`, `REG_FIELD`, `REG_GET`, `REG_SET`, `REG_UPDATE`, shift, and mask identifiers.

Generated-header validation should check that every visible `__SHIFT` has the expected matching `_MASK`, masks fit in 32-bit registers, repeated instance families retain expected parity, and all register names exist in `dcn_3_0_2_offset.h`. Validation must account for legitimate `_MASK_MASK` names and for this chunk's partial first and last register groups.

Runtime display tests should exercise DCN302 modesets, plane enable/disable, page flips, format/tiling changes, primary/secondary and chroma surfaces, DCC metadata paths, cursor enable/move/resize/stereo/security flags, DM data payload delivery, and multi-pipe operation that includes HUBP0 and HUBP1.

Bandwidth and power tests should cover DML-driven watermark programming, memory clock changes, self-refresh entry/exit, urgent traffic, prefetch windows, vblank/flip timing, VM fetches, low-power memory modes, suspend/resume, and runtime power transitions. Watch for HUBP underflow, DCHUBBUB timeout, force-IO sticky status, VM faults, and DM data underflow/late flags.

Audio tests should cover HDMI/DP audio playback, compressed/HBR channel counts, stream index/data paths, codec power-state transitions, audio CRC readback, underflow filler behavior, and suspend/resume with audio active.

Diagnostics should include perfmon 5/6 counter programming/readback, DCHUBBUB CRC capture, VM fault injection or fault-status validation where available, read-line/vblank interrupt behavior through HUBPRET, surface flip interrupt clear/status behavior, and register dumps on DCN302 hardware compared against expected bitfield layouts.

## Cross-Chunk Notes

This chunk is a middle slice of `dcn_3_0_2_sh_mask.h`. The previous chunk owns the earlier `AZALIA_CONTROLLER_CLOCK_GATING` fields and likely the preceding HDA register context. The next chunk continues `HUBP1_DCSURF_ADDR_CONFIG` and the rest of the replicated HUBP1/HUBPREQ1/HUBPRET1/cursor1 surface. The merge lane should combine these slices before describing full Azalia or all-HUBP instance coverage.
