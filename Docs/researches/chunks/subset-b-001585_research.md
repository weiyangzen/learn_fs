# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_1_0_sh_mask.h lines 9957-12472

## Scope And Purpose

This chunk is a generated AMD DCN 1.0 register field shift/mask table. It contains no executable C logic; its purpose is to publish compile-time bitfield metadata for DCN display MMIO registers so AMDGPU display code can compose and decode register values safely.

The source path is under a local `ceph-client` mirror, but this file is AMDGPU display-driver hardware metadata. It does not implement Ceph filesystem behavior.

The chunk starts in the middle of `DC_PERFMON8_PERFMON_CNTL`: the initial lines finish interrupt-enable/status/ack shift and mask definitions whose register family began in the previous chunk. It then covers full or near-full field families for:

- `DC_PERFMON8_*` tail fields for performance monitor 8 control, counted-value interrupt/misc status, and high/low counter reads.
- HUBP/HUBPREQ/HUBPRET/CURSOR instance 1 blocks: `HUBP1_*`, `HUBPREQ1_*`, `HUBPRET1_*`, `CURSOR1_*`, plus associated `DC_PERFMON9_*`.
- HUBP/HUBPREQ/HUBPRET/CURSOR instance 2 blocks: `HUBP2_*`, `HUBPREQ2_*`, `HUBPRET2_*`, `CURSOR2_*`, plus associated `DC_PERFMON10_*`.
- HUBP/HUBPREQ/HUBPRET instance 3 blocks and the beginning of `CURSOR3_CURSOR_CONTROL`.

The chunk ends inside `CURSOR3_CURSOR_CONTROL`; only the shift fields and first two masks are in this range, while the remaining `CURSOR3` masks and registers continue in the following chunk.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, or storage objects in this range. The public surface is the generated macro naming convention:

- `<REGISTER>__<FIELD>__SHIFT` gives the low bit position for a field.
- `<REGISTER>__<FIELD>_MASK` gives the field mask in the 32-bit register value.
- Numeric suffixes identify repeated DCN display hub pipe instances and their local performance monitors.

Important register families in this chunk:

- `HUBP[1-3]_DCSURF_*` defines surface format, rotation, mirror, address/tiling configuration, primary/secondary luma and chroma viewport start/dimension, swath/request size, HUBP blank/disable/VTG selection, underflow status/clear, clock enables/gates/status bits, virtual-memory page size, debug data, and DCFCLK/DPPCLK measurement-window controls.
- `HUBPREQ[1-3]_DCSURF_*` defines surface pitch, primary/secondary surface addresses and high address halves, chroma variants, primary/secondary meta-surface addresses, DCC enable and 64-byte block indicators, surface update/flip locks and pending state, frame pacing, flip interrupts, current and earliest-in-use addresses, and DRQ/CRQ/MRQ/PRQ expansion modes.
- `HUBPREQ[1-3]_DCN_*` defines TTU/QoS watermarks, global TTU control, surface and cursor request-delivery timing, VM system aperture low/high/default addresses, VM context-0 protection fault defaults, page-table base/start/end addresses, protection-fault status and clear bits, page-table depth/fault interrupt/default behavior, and L1 TLB controls.
- `HUBPREQ[1-3]_*PARAMETERS*`, `*_PREFETCH*`, and `*_PER_LINE_DELIVERY*` define display-logistics timing inputs: blank offsets, destination dimensions after scaler, prefetch ratios, vblank PTE/meta group timing, nominal PTE/meta row timing, per-line delivery timing, cursor delivery adjustments, and reference-frequency-to-pixel-frequency conversion.
- `HUBPREQ[1-3]_HUBPREQ_MEM_PWR_*` defines DPTE, MPTE, and META request-memory power force/disable/fine-grain controls and status fields.
- `HUBPRET[1-3]_*` defines DET buffer base address, 3-to-2 packing disable, channel crossbar source selection, DET memory power controls/status, read-line interval/window registers, vblank/read-line interrupt mask/type/clear/status fields, current/snapshot read-line values, and inside/outside/vblank read-line status.
- `CURSOR1_*` and `CURSOR2_*` define cursor enable, mode, snoop/system, pitch, rotation/mirror bypass, lines per chunk, latency measurement, surface address/high address, size, position, hot spot, stereo offsets, destination X offset, and cursor memory power controls/status. `CURSOR3_CURSOR_CONTROL` begins the same instance-3 control layout.
- `DC_PERFMON9_*` and `DC_PERFMON10_*` mirror the performance counter/monitor layout for HUBP instances 1 and 2: event selection, counted-value selection, increment mode, hardware control/start/stop selections, count-off selection, per-counter state, monitor report count, interrupt enable/status/ack, counted-value high/low data, and read selectors.

## Control Flow

This chunk has no runtime control flow. Every meaningful line is a preprocessor definition consumed by C register-helper code.

Runtime flow exists in callers that combine these field macros with addresses from the companion offset header. Typical usage is:

1. Select a DCN display instance through register addresses and instance offsets.
2. Program HUBP surface format, viewport, request-size, VM, and TTU/QoS registers while the plane update path is locked or synchronized to vblank.
3. Program HUBPREQ surface addresses, meta addresses, DCC/tiling state, prefetch, vblank, nominal, and per-line delivery parameters computed by display-mode validation and bandwidth code.
4. Enable or disable HUBP/HUBPREQ/HUBPRET/CURSOR memory power and clocks around pipe allocation, blanking, reset, suspend/resume, or power-gating transitions.
5. Use HUBPRET read-line/vblank interrupt fields and HUBPREQ surface-flip interrupt fields to drive vblank, read-line, or page-flip event handling.
6. Read status, in-use address, fault, underflow, power-state, performance-counter, and debug fields for synchronization, diagnostics, and error recovery.

Because this header is declarative, it does not encode ordering. Consumers must provide the sequencing around update locks, pending/taken bits, interrupt clear semantics, MMU/TLB programming, memory-power transitions, and active display scanout.

## State And Persistence Behavior

The header itself stores no state and has no persistence behavior. The macros describe state held in DCN hardware registers.

The represented hardware state includes:

- Plane configuration: pixel format, rotation, mirror, tiling, viewport, luma/chroma dimensions, surface pitch, surface addresses, metadata addresses, DCC enablement, update/flip lock state, flip-pending state, frame pacing, and current/earliest in-use addresses.
- Request and timing state: swath height, chunk sizes, PTE/MPTE/meta group sizing, TTU/QoS controls, prefetch timing, vblank and nominal PTE/meta timing, per-line delivery timing, cursor delivery adjustment, reference-to-pixel-frequency ratio, and destination/blank offsets.
- VM and fault state: system aperture bounds/defaults, context-0 page-table base/start/end, protection-fault default address attributes, fault status, faulting address fragments, page-table depth, L1 TLB enablement, and fault interrupt/default controls.
- Power and clock state: HUBP clock enables/gates/status bits, request-memory power force/disable/fine-grain controls, DET memory power state, cursor memory power state, and related status fields.
- Interrupt and diagnostic state: surface flip interrupts, HUBPRET vblank/read-line interrupts, underflow status/clear bits, read-line snapshot/status bits, performance-counter state and interrupts, and debug/performance measurement windows.

Persistence is register-specific and not declared by this generated table. Some fields are control bits that remain programmed until a modeset, plane disable, power transition, reset, or later write. Others are transient or sticky status bits, read-only counters, write-one-to-clear bits, self-clearing clear/ack bits, or hardware-latched pending values. Field names such as `*_STATUS`, `*_CLEAR`, `*_ACK`, `*_PENDING`, `*_INUSE`, `*_FAULT`, `*_MEM_PWR_STATE`, and `*_INT_STATUS` hint at behavior but do not specify access type or side effects.

## Dependencies And Integration Points

This chunk depends on the generated AMD ASIC register-header convention and DCN 1.0 hardware layout. It is meaningful when paired with:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_1_0_offset.h` for register addresses and base-index macros.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_1_0_enum.h` for symbolic field values where generated enum values exist.
- AMD display register helpers and macros that use address, shift, and mask triplets for read-modify-write operations.

Direct include users found in this source tree include DCN 1.0 resource, IRQ, and GPIO code:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn10/dcn10_resource.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn10/irq_service_dcn10.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn10/hw_factory_dcn10.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn10/hw_translate_dcn10.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn20/hw_translate_dcn20.c`

The practical integration points are DCN resource construction, hub pipe programming, plane address flips, cursor programming, VM aperture/page-table setup for display fetch, DCC/meta-surface setup, bandwidth and prefetch timing programming, display request QoS, memory power management, vblank/read-line/page-flip interrupt handling, underflow/fault diagnostics, and performance counter readout.

The instance numbering is important. The macro families in this chunk correspond to repeated hub pipe instances 1, 2, and 3 and their local performance-monitor instances 9 and 10. They must stay layout-compatible with the corresponding address definitions in the offset header and with repeated instance tables in DCN resource code.

## Risks And Edge Cases

- The masks and shifts are hardware ABI. A one-bit error can compile cleanly while writing the wrong MMIO field, corrupting neighboring fields, misprogramming a plane, failing to clear an interrupt, or hiding a real fault.
- This range is generated and repetitive. Copy/paste or generator drift across instances 1, 2, and 3 would be difficult to see in review because most register layouts are intentionally identical with only the instance number changed.
- Chunk boundaries split register families. `DC_PERFMON8_PERFMON_CNTL` is incomplete without the previous chunk, and `CURSOR3_CURSOR_CONTROL` is incomplete without the next chunk.
- Surface update and flip fields are sequencing-sensitive. Incorrect use of `SURFACE_UPDATE_LOCK`, `SURFACE_FLIP_PENDING`, `SURFACE_UPDATE_PENDING`, frame pacing, or in-use address status can lead to missed flips, torn updates, stuck commits, or page-flip timeout behavior.
- VM and TLB fields are high risk. Incorrect aperture, page-table, fault-default, or L1 TLB fields can turn display fetch faults into black frames, memory faults, fault storms, or security-sensitive access behavior.
- Request timing, TTU, QoS, prefetch, vblank, and nominal parameter fields must match mode validation and bandwidth calculations. Bad values can cause underflow, flicker, corruption, or power-management regressions that appear only under high memory pressure or multi-display modes.
- Interrupt fields mix mask, type, clear, occurred, and status semantics. Surface flip, vblank, and read-line paths need the correct clear polarity and ordering to avoid lost events or interrupt storms.
- Power controls operate on live display fetch memories. Forcing or disabling DPTE/MPTE/META/DET/CROB memory power at the wrong time can break scanout, cursor fetch, VM translation, or resume.
- The header does not describe access permissions. Callers must know which fields are read-only, write-one-to-clear, reserved, self-clearing, clock-gated, or only valid while a pipe is enabled.

## Test Signals

Useful validation is mostly compile-time plus hardware/display behavior:

- Build AMDGPU/DCN 1.0 display code; renamed or missing macros should be caught by resource, IRQ, GPIO, and register helper users.
- Compare generated masks/shifts against `dcn_1_0_offset.h`, adjacent chunks of `dcn_1_0_sh_mask.h`, and repeated instance families to catch instance drift or split-family omissions.
- Exercise modesets and plane commits on pipes using HUBP instances 1, 2, and 3: primary/secondary planes, luma/chroma formats, DCC-enabled surfaces, rotated or mirrored surfaces, viewport changes, and fast page flips.
- Test cursor enable/disable, movement, hot spot, stereo offset, surface-address update, and cursor memory power behavior for cursor instances 1 and 2, with instance 3 covered after merging the next chunk.
- Exercise vblank, read-line, and page-flip interrupt paths and verify that occurred/status bits set and clear without storms or lost events.
- Stress memory-pressure and bandwidth-sensitive modes: multi-display, high resolution, high refresh, scaling, DCC, chroma formats, suspend/resume, power gating, and repeated flips while monitoring for HUBP underflow or DCN VM fault status.
- Use debug and performance signals where available: HUBPREQ debug data, DCFCLK/DPPCLK measurement windows, `DC_PERFMON9/10` counters, in-use/earliest-in-use surface addresses, read-line snapshots, memory power status, and protection-fault address/status fields.
