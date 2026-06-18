# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_2_offset.h lines 1-2677

## Purpose

This chunk is the beginning of a generated AMD DCN 3.0.2 register-offset header. It contains no executable C logic; it publishes preprocessor constants that map symbolic display-controller register names to MMIO register offsets and base-index selectors. Consumers pair these `mm...` offsets with matching field shift/mask headers and AMDGPU register access helpers to program display clocks, power domains, firmware mailboxes, display memory hubs, audio, VM contexts, HUBP pipes, cursors, and performance counters.

The requested slice covers lines 1-2677 of a 16,273-line file and contains 2,379 `#define` lines. It starts with the copyright/license, include guard, and legacy VGA/MMHUBBUB definitions, then covers early DCN 3.0.2 blocks: DCCG clock generation, DMU/DMCU/DMCUB control, MCIF writeback, MMHUBBUB/VGAIF, Azalia/HDA audio, DCHUBBUB/VM/HUBBUB memory arbitration, complete HUBP0 and HUBP1 register groups, and the start of HUBP2. The chunk ends mid-`dce_dc_dcbubp2_dispdec_hubp_dispdec` after `mmHUBP2_DCHUBP_REQ_SIZE_CONFIG_BASE_IDX`; later chunks are required for the rest of HUBP2 and subsequent display blocks.

Although the repository path is under a local `ceph-client` mirror, this file is AMDGPU display hardware metadata, not Ceph or distributed filesystem logic.

## Important APIs, Types, And Macros

There are no functions, structs, enums, global variables, includes, locks, or allocator paths in this range. The public interface is the generated macro namespace:

- `mm<REGISTER>`: numeric register offset relative to the register aperture selected by the base-index table.
- `mm<REGISTER>_BASE_IDX`: base index used by SOC15-style register macros to choose the correct hardware register base.
- `// addressBlock: ...` and `// base address: ...`: generated grouping metadata from AMD's register database; these comments define the hardware block context but are not consumed by the compiler.

Major macro groups visible in this chunk:

- VGA and VGAIF: `mmVGA_*`, `mmD1VGA_CONTROL` through `mmD6VGA_CONTROL`, legacy CRTC/attribute/graphics/sequencer aliases, `mmVGA_SOURCE_SELECT`, and VGAIF memory-page/latency/debug controls.
- DCCG: PHY pixel-clock resync, DP DTO phase/modulo controls, `DSCCLK*` and `DPPCLK*` DTO parameters, reference/disp/soc/symbol clock gating registers, global timebase divisors, GTC DTO/current counters, soft reset, audio DTO registers, VSYNC latch/counter registers, and `SYMCLK*` enable/disable controls.
- DC perfmon blocks: `DC_PERFMON0`, `DC_PERFMON1`, `DC_PERFMON2`, `DC_PERFMON3`, `DC_PERFMON4`, `DC_PERFMON6`, and `DC_PERFMON7` control/state/value registers for DCCG, DMU, MMHUBBUB, audio, HUBP0, and HUBP1 blocks.
- DMU/DMCU/DMCUB: display power-domain config/status registers, DMCU firmware address/checksum/interrupt/communication registers, interrupt handler controller destinations, RBBMIF timeout/status, DMCUB region-window addresses, inbox/outbox queues, scratch registers, timers, GPINT, fault, memory-power, security, and control/status registers.
- MCIF writeback and MMHUBBUB: writeback buffer manager, Y/C buffer addresses and high bits, pitch, resolution, watermark, VMID, QoS, p-state/self-refresh/clock-gating controls, warmup, MCIF arbiter/debug, and MCIF perf/status registers.
- Azalia/HDA audio: stream index/data pairs for streams 0-15, codec endpoint index/data pairs, input endpoints, controller DMA/DTO/CRC/payload/memory-power registers, and codec root parameters such as vendor/device, channel count, supported rates/formats, power state, reset, converter sync, and audio port connectivity.
- DCHUBBUB/HUBBUB: SDPIF and memory aperture registers, VM framebuffer/AGP/local-HBM address registers, return-path DCC config and CRC, arbitration QoS/watermark registers, self-refresh/DRAM clock-change watermarks, urgent and p-state controls, fault/status/debug registers, and DCN VM context 0-15 page-table control/base/start/end registers plus fault/default address registers.
- HUBP0 and HUBP1: per-pipe surface format/tiling/viewport/request-size controls, request-side surface pitch/address/meta-address/flip/in-use/TTU/prefetch/vblank/flip/nominal/per-line/cursor/timing registers, return-side read-line/control/memory-power/interrupt registers, cursor/DMDATA registers, and per-HUBP perfmon blocks.
- HUBP2 start: the first surface configuration, address, tiling, viewport, and request-size offsets for the third HUBP instance.

## Control Flow

This header has no runtime control flow. It contributes compile-time constants to the AMDGPU/DCN register access path:

1. DCN 3.0.2 resource and block code includes this offset header and a matching shift/mask header for the same ASIC revision.
2. Register-list macros in DCN block headers token-paste instance IDs and register names into symbols such as `mmHUBPREQ0_DCSURF_PRIMARY_SURFACE_ADDRESS` or `mmDCCG_AUDIO_DTO0_PHASE`.
3. Resource construction stores those offsets in typed register tables for DCCG, HUBBUB, HUBP, DMCUB, audio, and perfmon blocks.
4. Runtime display code uses register helpers such as `RREG32`, `WREG32`, and SOC15/DC register wrappers to read, write, or update MMIO registers by table entry.

The macros do not encode sequencing. The driver must still handle ordering around clocks, power gating, firmware boot, mailbox setup, VM page-table programming, surface flips, cursor updates, memory watermarks, interrupt clear/ack, and perfmon start/stop.

## State And Persistence Behavior

The file itself stores no software state and persists no data. It names hardware state that lives in DCN MMIO registers:

- Clock state in DCCG registers controls display, DSC, DPP, DP, audio, symbol, GTC, and timebase DTO behavior.
- Power state in DMU, DMCU, DMCUB, Azalia, HUBBUB, HUBPREQ, HUBPRET, cursor, and MCIF registers controls memory-power, clock-gating, self-refresh, and domain power transitions.
- Firmware state in DMCU/DMCUB registers covers firmware image windows, code-window mappings, inbox/outbox ring pointers, scratch registers, timers, GPINT, fault addresses, and security controls.
- Display memory state in HUBBUB/HUBP/HUBPREQ registers covers VM apertures, page-table contexts, surface addresses, metadata addresses, tiling, viewport dimensions, prefetch timing, watermarks, flip status, and fault state.
- Audio state in Azalia registers covers stream/endpoint index-data windows, DMA controls, payload capabilities, codec parameters, DTO configuration, CRC, and power status.
- Diagnostic state in perfmon, CRC, interrupt, debug, timeout, and fault registers can be sticky, self-clearing, write-one-to-clear, or clock-dependent depending on hardware semantics.

Persistence is hardware-defined. Register contents generally survive until a modeset, fast update, power transition, suspend/resume, GPU reset, or explicit driver write changes them. This header does not protect reserved bits or preserve current values; consumers must use the matching masks and register-update helpers when side effects matter.

## Dependencies And Integration Points

This chunk depends on AMD's generated DCN 3.0.2 register database and must remain synchronized with:

- The matching DCN 3.0.2 shift/mask header, which gives field-level bit positions for these offsets.
- Shared AMDGPU register access infrastructure that interprets `mm...` offsets and `_BASE_IDX` values for SOC15 display registers.
- DCN resource constructors and block register-list macros for DCCG, HUBBUB, HUBP, DMU/DMCU/DMCUB, MCIF writeback, audio, and perfmon components.
- Firmware-facing DMCUB code, which uses mailbox, scratch, timer, region, interrupt, and GPINT offsets to communicate with display microcontroller firmware.
- Memory-management and modeset paths, which use HUBBUB VM context registers, HUBPREQ surface/meta address registers, watermarks, and fault/status registers during plane programming and flip handling.

The integration style is purely symbolic and preprocessor-driven. A rename, wrong offset, wrong base index, or missing generated macro is normally caught either by compile failures in register-table initializers or, more dangerously, by runtime MMIO writes landing in the wrong hardware register.

## Risks And Edge Cases

- Offset drift is the primary risk. These constants are untyped integers, so a stale generated value can compile cleanly and corrupt unrelated display hardware state at runtime.
- Base-index drift can be as damaging as offset drift because the same numeric offset can target a different MMIO aperture when `_BASE_IDX` is wrong.
- This chunk crosses many hardware ownership boundaries. A local-looking edit to a DCCG, DMCUB, Azalia, HUBBUB, or HUBP define can break modeset, audio, firmware, memory arbitration, VM fault handling, cursor, or diagnostics.
- Several groups are instance-patterned. `HUBP0`, `HUBP1`, and `HUBP2` offsets are separated by hardware instance bases; copy/paste mistakes may affect only one pipe and only multi-display or multi-plane configurations.
- The DCHUBBUB VM-context block exposes repeated context 0-15 page-table registers. Off-by-one context mappings can produce display VM faults or memory access outside the intended aperture.
- Firmware and mailbox registers are sequencing-sensitive. Wrong DMCUB region, inbox/outbox pointer, scratch, interrupt, or GPINT offsets can cause firmware boot failures, lost commands, stuck waits, or resume-only failures.
- Power and clock controls are timing-sensitive. Misprogramming DTO, clock-gating, memory-power, self-refresh, p-state, or watermark registers can produce underflow, blank display, hangs, or rare corruption under low-power transitions.
- Audio index/data windows and codec endpoint registers require correct pairing. Wrong stream or endpoint offsets can break only particular audio streams, formats, or display connectors.
- The chunk boundary is artificial and stops in the beginning of HUBP2, so the final per-file research must merge later chunks before making complete claims about all HUBP instances.

## Test Signals

Useful validation signals for this chunk are generated-header consistency plus hardware-facing behavior:

- Build AMDGPU/DC with DCN 3.0.2 support enabled; missing or renamed macros should fail in DCN resource table initializers, DMCUB register definitions, audio code, or block register lists.
- Mechanically compare these offsets and `_BASE_IDX` values against AMD's authoritative DCN 3.0.2 register database and adjacent generated headers for related ASIC revisions.
- Check that every `mm<REGISTER>` in this range has the expected paired `mm<REGISTER>_BASE_IDX`, and that repeated instance groups keep the expected stride and naming pattern.
- Exercise display modesets across single and multi-display configurations so DCCG, HUBBUB, HUBP0, HUBP1, and later HUBP2 code paths are active.
- Test plane flips, cursor movement, metadata updates, VM-backed framebuffer scanout, suspend/resume, hotplug, p-state changes, self-refresh, and memory-power transitions while watching for underflow, VM faults, DMCUB timeouts, and display corruption.
- Validate audio over display links with multiple streams and endpoints, including format/rate changes and suspend/resume.
- Use diagnostics such as perfmon counters, CRC registers, interrupt status, DCHUBBUB fault status, DMCUB scratch/fault registers, and kernel logs to catch wrong offsets that compile but misaddress hardware.

## Cross-Chunk Notes

Earlier content is not needed for this file because this chunk starts at line 1 with the include guard. Later chunks continue from the middle of HUBP2 and eventually cover the rest of the generated DCN 3.0.2 offset namespace. The final merged per-file research document should treat this report as the early-register-block summary and combine it with later chunk reports before drawing whole-file conclusions.
