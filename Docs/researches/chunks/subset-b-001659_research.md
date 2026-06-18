# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_2_1_0_sh_mask.h lines 7157-9803

## Scope And Purpose

This chunk is generated AMD DCN 2.1 register bitfield metadata. It contains no executable C logic. Its purpose is to publish compile-time `__SHIFT` and `_MASK` constants used by AMDGPU display-core register helpers to pack, update, and read fields in MMIO registers.

The file is under a local `ceph-client` source mirror, but this path is Linux AMDGPU display-driver hardware metadata. It does not implement Ceph filesystem behavior.

The requested range contains 2,056 `#define` lines across 38 generated address blocks and 477 register comments. It is source-tree-aligned to a large generated header chunk, not to semantic subsystem boundaries. The slice starts with `AZF0STREAM7_AZALIA_STREAM_INDEX`, covers the remainder of the Azalia/HDA audio register family in this area, covers DCHUBBUB and VM request register fields, then enters the first HUBP/HUBPREQ/HUBPRET/CURSOR instance. It ends inside `DC_PERFMON7_PERFCOUNTER_CNTL`; the matching `DC_PERFMON7_PERFCOUNTER_CNTL2` and later perfmon fields are in the next chunk.

Major register families covered here:

- HDA/Azalia stream, endpoint, controller, root-node, stream 8-15, and input endpoint index/data fields.
- DC perfmon instance 5 for HDA and instance 6 for DCHUBBUB, plus the first register of instance 7 for HUBP0.
- DCHUBBUB SDPIF, VM framebuffer/aperture/HBM window, security-level, return-path DCC, CRC, arbitration, watermark, host-VM, timeout, reset, clock, and performance-measurement fields.
- DCN VM request interface contexts 0-15, default address, fault control/status, and fault address fields.
- HUBP0 surface configuration, tiling, viewport, request size, hubp control, clock, VMPG, and measurement fields.
- HUBPREQ0 surface address, metadata address, flip, surface-in-use, TTU/QoS, VM aperture/TLB, prefetch, vblank/flip/nominal timing, cursor, memory power, and delivery fields.
- HUBPRET0 request return, read-line, vblank/read-line interrupt, and memory power fields.
- CURSOR0_0 cursor image, position, size, hot spot, stereo, display metadata, QoS, software metadata, memory power, and underflow fields.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, or storage objects in this range. The public interface is the macro set consumed by generated register lists and display register-access helpers.

Every complete field follows the generated naming contract:

- `<REGISTER>__<FIELD>__SHIFT` for bit offsets.
- `<REGISTER>__<FIELD>_MASK` for bit masks.

The corresponding register offsets live in the paired `dcn_2_1_0_offset.h` header. Consumer code normally reaches these constants through AMD display macros such as `SRI(...)`, `SR(...)`, `SE_SF(...)`, `LE_SF(...)`, `REG_SET`, `REG_SET_2`, `REG_UPDATE`, `REG_GET`, and `REG_WAIT`, rather than by writing raw bit arithmetic.

Important macro families in this chunk:

- `AZF0STREAM7_AZALIA_STREAM_INDEX/DATA` and `AZF0STREAM8` through `AZF0STREAM15` expose indirect stream register index, write-enable, and data fields for HDA stream windows.
- `AZ_CLOCK_CNTL` defines Azalia clock-gating and test clock selection bits.
- `DC_PERFMON5_*`, `DC_PERFMON6_*`, and partial `DC_PERFMON7_PERFCOUNTER_CNTL` provide event selection, counted-value selection, increment/run modes, counter state, interrupt status/acknowledge, high/low counter values, and read selectors for display performance counters.
- `AZF0ENDPOINT[0-7]_*` and `AZF0INPUTENDPOINT[0-7]_*` define indirect endpoint register index/data fields for output and input codec endpoints.
- `AZALIA_*` controller fields cover DTO programming, SOCCLK control, underflow filler sample data, DMA control for data/BDL/CORB/RIRB paths, cyclic buffer sync, payload capabilities, stream arbitration, CRC controls/results, and Azalia memory power control/status.
- `AZALIA_F0_CODEC_*`, `CC_RCU_DC_AUDIO_*`, `REG_DC_AUDIO_*`, and `AZALIA_F0_GTC_GROUP_OFFSET*` expose codec root parameters, channel counts, resync FIFO, function parameters, power/reset controls, converter synchronization, audio port connectivity, and global-time-counter offsets.
- `DCHUBBUB_SDPIF_*`, `VM_REQUEST_PHYSICAL`, `DCN_VM_FB_*`, `DCN_VM_AGP_*`, and `DCN_VM_LOCAL_HBM_*` describe hubbub request routing, forced IO status, framebuffer/agp/HBM apertures, lock control, pipe security levels, and SDPIF memory power state.
- `DCHUBBUB_RET_PATH_DCC_CFG*`, `DCHUBBUB_RET_PATH_MEM_PWR_*`, and `DCHUBBUB_CRC*` define display compression return-path controls, memory power controls, CRC enable/selection/continual mode, and CRC result components.
- `DCHUBBUB_ARB_*`, `DCHUBBUB_GLOBAL_TIMER_CNTL`, `SURFACE_CHECK*`, `VTG[0-3]_CONTROL`, `DCHUBBUB_SOFT_RESET`, `DCHUBBUB_CLOCK_CNTL`, `DCFCLK_CNTL`, `DCHUBBUB_TIMEOUT_*`, and `FMON_CTRL` define arbitration thresholds, QoS forces, self-refresh/DRAM-clock-change watermarks A-D, watermark change request/done state, timeout detection/interrupt state, surface-check addresses, VTG enables, soft resets, clocks, host-VM behavior, and firmware-monitor control.
- `DCN_VM_CONTEXT[0-15]_*`, `DCN_VM_DEFAULT_ADDR_*`, `DCN_VM_FAULT_*` define VM context enable/page table ranges, default-address behavior, and fault reporting.
- `HUBP0_DCSURF_*`, `HUBP0_DCHUBP_*`, and `HUBP0_HUBP_*` cover surface pixel format/rotation/mirror, address/tiling, primary and secondary viewport geometry for luma/chroma planes, request sizing, blank enable, underflow/TTU disable, clock gating, and measurement windows.
- `HUBPREQ0_DCSURF_*`, `HUBPREQ0_DCN_*`, `HUBPREQ0_*PARAMETERS*`, and `HUBPREQ0_*DELIVERY*` describe surface pitch, primary/secondary and metadata addresses, flip control/status/interrupts, surface-in-use and earliest-in-use latches, TTU watermarks, VM/TLB aperture, blank offsets, destination dimensions, prefetch, vblank/flip/nom timing, cursor prefetch, and memory power state.
- `HUBPRET0_*` covers HUBP return path control, detile-buffer memory power, read-line control/ranges, vblank/read-line interrupt mask/type/clear/status bits, current/snapshot read-line value, and read-line inside/outside status.
- `CURSOR0_0_*` covers cursor enable, magnification, mode, TMZ/snoop/system flags, pitch, rotation/mirroring bypass, cursor address high/low, size, position, hot spot, stereo offsets, destination offset, cursor memory power, DMDATA address/control/QoS/status/software-data fields, and DMDATA underflow clear.

## Control Flow

This header chunk has no internal runtime control flow. Its data flow is compile-time substitution: DCN 2.1 code includes `dcn_2_1_0_sh_mask.h`, expands these generated macro names into per-register mask/shift tables, and then display register helpers use those constants during MMIO reads, writes, updates, waits, and interrupt acknowledgements.

Representative runtime flows in local consumers:

- `display/dc/resource/dcn21/dcn21_resource.c` includes this header when constructing DCN 2.1 resources and wiring generated register offset/mask tables into hubbub, hubp, irq, gpio, clock, and display-pipeline objects.
- `display/dmub/src/dmub_dcn21.c` includes this header with `dcn_2_1_0_offset.h` and `renoir_ip_offset.h` for DMUB-facing DCN 2.1 register access.
- `display/dc/irq/dcn21/irq_service_dcn21.c` includes these constants for interrupt source definitions and acknowledge/mask handling.
- `display/dc/gpio/dcn21/hw_factory_dcn21.c` and `display/dc/gpio/dcn21/hw_translate_dcn21.c` include the generated DCN 2.1 register headers as part of GPIO/DDC/HPD translation support.
- HUBBUB/HUBP runtime code programs watermarks, surface apertures, VM contexts, flip state, and cursor or DMDATA state using register-table abstractions backed by these field constants.

Because the file is declarative, it does not enforce required sequencing. Consumers must decide when to program apertures before enabling VM, when to update watermarks relative to modesets and clock changes, when to arm flips and wait for pending/in-use status, when to clear sticky interrupt/status fields, when to lock or latch double-buffered values, and when power-gated memories are safe to access.

## State And Persistence Behavior

The header itself stores no software state and has no persistence behavior. The macros describe fields in hardware MMIO registers.

Hardware state represented by this chunk includes:

- Azalia audio state: stream indirect register selectors, endpoint index/data windows, controller clocking, DTO and SOCCLK selection, DMA enables/positions, cyclic buffer sync, stream payload capacity, CRC controls/results, underflow filler samples, codec root parameters, power/reset controls, converter synchronization, audio connectivity, GTC offsets, and Azalia memory power status.
- Performance-counter state: event selectors, run/stop mode, counter active state, counted values, compare/off events, interrupt status, interrupt acknowledge, and high/low readback registers for DC perfmon instances.
- DCHUBBUB global state: SDPIF routing/security, framebuffer and AGP apertures, local HBM range locks, return-path DCC configuration, return-path memory power, CRC control/results, arbitration outstanding/saturation/QoS settings, watermark sets A-D, timeout detection, reset/clock controls, host-VM configuration, performance measurement, and FMON control.
- VM state: per-context page-table base/start/end addresses for contexts 0-15, default address programming, fault enable/retry/protection controls, fault status, and fault address readback.
- HUBP0/HUBPREQ0 state: surface format/tiling/viewports, request-size calculation, blank/underflow controls, clock gating, VM page settings, surface and metadata addresses, flip scheduling and completion/interrupt bits, surface-in-use latches, TTU/QoS watermarks, destination/prefetch/vblank/flip/nominal timing parameters, memory power status, and line delivery controls.
- HUBPRET0 state: return-path enabled/forced behavior, read-line interrupt ranges and masks, vblank/read-line clear/status bits, read-line snapshot/current values, and detile-buffer memory power.
- CURSOR0_0 state: cursor image address, dimensions, screen position, hot spot, stereo offsets, display metadata addresses and transfer status, metadata QoS, cursor memory power, underflow flag, and software metadata payload.

Persistence is hardware-specific and not encoded in this file. Some fields are programming knobs that remain until modeset, reset, suspend/resume, power-gating transition, or explicit rewrite. Others are read-only status, sticky interrupt/status, write-one-to-clear acknowledgement, self-clearing update/send requests, pending/in-use latches, CRC result fields, fault registers, or double-buffered values latched at vblank or flip boundaries. Names such as `*_STATUS`, `*_ACK`, `*_CLEAR`, `*_DONE`, `*_PENDING`, `*_INUSE`, `*_FAULT`, `*_UPDATED`, `*_FORCE`, and `*_LOCK` signal possible side effects but do not define access type by themselves.

## Dependencies And Integration Points

This chunk depends on the generated AMD ASIC register-header contract:

- `dcn_2_1_0_offset.h` supplies the matching MMIO register offsets for these field masks and shifts.
- `dcn_2_1_0_sh_mask.h` is included by DCN 2.1 resource, DMUB, IRQ, and GPIO code in the AMD display tree.
- DCN/DCE display code supplies register access helpers and mask/shift structs that combine offsets from the offset header with field constants from this header.
- Hardware programming logic in hubbub, hubp, cursor, IRQ, audio, and VM paths supplies the legal values and access ordering; this header only supplies bit positions.

Practical integration points include:

- Azalia/HDA display audio paths that program stream windows, codec endpoint/root registers, DMA controls, CRC validation, payload capacity, and audio power-gating behavior.
- HUBBUB memory/arbitration paths that program framebuffer apertures, AGP/HBM windows, self-refresh and DRAM-clock-change watermarks, host-VM behavior, timeouts, soft resets, clocks, and performance measurements.
- VM request handling and diagnostics that program per-context page tables and inspect fault status/address fields.
- HUBP0 plane paths that program surface format, tiling, addresses, viewports, pitch, request sizing, VM settings, flips, prefetch timing, TTU watermarks, and memory power state.
- Interrupt paths for surface flip, vblank/read-line, timeout, perf counter, fault, and status/ack fields.
- Cursor and display metadata paths that update cursor address/position/size/hot spot and DMDATA transfer/QoS/underflow state.

## Risks And Edge Cases

- These constants are hardware ABI. A wrong mask or shift can compile cleanly but write the wrong bits in a live display register.
- The chunk boundary is not semantic. It starts at `AZF0STREAM7_AZALIA_STREAM_INDEX` after stream 6 in the previous chunk and ends after the masks for `DC_PERFMON7_PERFCOUNTER_CNTL`, before `DC_PERFMON7_PERFCOUNTER_CNTL2` in the next chunk. Merge/reconciliation needs to preserve those boundary facts.
- Instance repetition is easy to damage manually. Endpoint 0-7, input endpoint 0-7, stream 8-15, VM context 0-15, watermark sets A-D, DCC config 0-7, and repeated surface address pairs have nearly identical layouts with only prefix/index changes.
- Status, clear, acknowledge, and programming bits are interleaved in the same register families. Treating every mask as ordinary read/write state can accidentally clear a sticky condition, miss an interrupt, or poll the wrong bit.
- Azalia DMA, cyclic-buffer, codec power, and stream index/data masks affect display audio. Drift can cause silent audio, channel-count errors, underflows, corrupted CRC validation, wrong endpoint access, or stuck DMA.
- VM aperture and page-table fields are address-critical. Incorrect high/low masks or context fields can route display fetches to wrong memory, trigger page faults, produce blank planes, or expose security/isolation bugs.
- Watermark, QoS, TTU, and prefetch timing masks are latency-critical. Bad fields can produce underflow, flicker, missed flips, power-state entry/exit stalls, or memory-clock-change instability.
- Flip and surface-in-use fields are synchronization-critical. Incorrect pending/clear/interrupt/in-use masks can lead to missed page-flip completion, tearing, stale addresses, or incorrect earliest-in-use accounting.
- Cursor and DMDATA masks directly affect visible overlay and metadata transfer. Bad address, TMZ/snoop/system, underflow-clear, QoS, size, hot-spot, or position masks can cause cursor corruption, metadata underflow, or memory-attribute mismatches.
- Power-gating memory control/status fields must be interpreted with hardware access rules. Writing force/disable bits at the wrong time can make dependent blocks inaccessible or leave status polling stuck.

## Test Signals

Useful validation is build coverage plus hardware/display behavior:

- Build AMDGPU/DC with DCN 2.1 support enabled. Missing or renamed macros should fail in DCN 2.1 resource, DMUB, IRQ, GPIO, hubbub, hubp, cursor, or audio paths.
- Compare this generated range against `dcn_2_1_0_offset.h` and adjacent DCN generation headers to catch instance-prefix, mask-width, or field-layout drift.
- Exercise display audio on DCN 2.1 hardware: stream setup, endpoint/root codec access, DMA enable/disable, channel count, suspend/resume, hotplug, CRC/error status, and audio playback without underflow.
- Exercise modesets and page flips on HUBP0-backed planes: surface address changes, metadata/DCC addresses, primary/chroma surfaces, VMID changes, flip interrupt delivery, surface-in-use latches, vblank timing, and suspend/resume.
- Validate VM fault behavior by checking that normal display fetches do not produce `DCN_VM_FAULT_STATUS`, and that deliberate invalid mappings report plausible fault addresses/status.
- Validate watermark and power behavior across memory-clock changes, self-refresh, DRAM-state transitions, high-bandwidth modes, multi-plane composition, and low-power entry/exit; watch for underflow, timeout interrupts, or flicker.
- Exercise cursor paths: enable/disable, size/mode changes, position/hot-spot updates, stereo offsets if relevant, TMZ/snoop/system memory attributes, DMDATA updates, and underflow-clear behavior.
- Read diagnostic counters/status: DC perfmon 5/6/partial 7, DCHUBBUB CRC results, timeout status, HUBPRET read-line/vblank interrupt state, HUBP measurement windows, memory power statuses, and DMDATA status. Stuck pending bits, wrong clears, repeated underflows, or implausible counter values are strong mask/shift regression signals.
