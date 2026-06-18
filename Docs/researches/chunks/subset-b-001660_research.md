# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_2_1_0_sh_mask.h lines 9804-12312

## Purpose

This chunk is generated AMDGPU DCN 2.1 register field metadata. It contains no executable C logic; its API is a set of preprocessor constants that describe bit positions and masks for display-controller registers. Each decoded field is represented by paired macros:

- `REGISTER__FIELD__SHIFT` gives the least-significant bit position.
- `REGISTER__FIELD_MASK` gives the already-positioned bit mask.

The path is under a local `ceph-client` source mirror, but the content is AMD display-driver hardware metadata. It does not implement Ceph or distributed filesystem behavior.

The range starts in the middle of `DC_PERFMON7_PERFCOUNTER_CNTL` mask definitions, then covers DCN hub pipe and request/return blocks for pipe instances 1 and 2, cursor blocks for instances 1 and 2, performance-monitor blocks 8 and 9, and the beginning of pipe instance 3 HUBP/HUBPREQ coverage. The chunk ends inside `HUBPREQ3_PER_LINE_DELIVERY`; later instance-3 fields continue in the next chunk.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, or runtime storage objects in this range. The important surface is the generated macro namespace consumed by AMD display register helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `REG_UPDATE`, `REG_READ`, `REG_WRITE`, `SRI(...)`, and `HUBP_SF(...)`.

Major macro families in this chunk:

- `DC_PERFMON7_*`, `DC_PERFMON8_*`, and `DC_PERFMON9_*`: performance counter control, counted-value type, hardware start/stop/count-off selection, per-counter state selection, perfmon global control, clock/run-enable control, interrupt status/ack fields, counter value low/high fields, and read selector fields. `DC_PERFMON7` is partial at the start of the chunk; `DC_PERFMON8` and `DC_PERFMON9` are complete in this range.
- `HUBP1_*`, `HUBP2_*`, and visible `HUBP3_*`: hub pipe display surface descriptors for pixel format, rotation, horizontal mirror, address/tiling configuration, primary and secondary viewport start/dimensions for luma and chroma planes, request-size configuration, request/control fields, clock control, virtual memory page config, debug DB, and DCFCLK/DPPCLK measurement-window controls.
- `HUBPREQ1_*`, `HUBPREQ2_*`, and visible `HUBPREQ3_*`: hub request surface programming, including luma/chroma pitch, VMID, primary/secondary surface and metadata addresses, surface control for TMZ/DCC/independent-64B-block fields, flip control and flip interrupts, in-use and earliest-in-use address reporting, request expansion modes, TTU/QoS watermarks, VM aperture and L1 TLB control, blanking/scaler/prefetch timing, vblank/flip/nominal PTE and meta-row timing parameters, per-line delivery timing, cursor request settings, reference-frequency conversion, DRQ limits, and memory power controls/status.
- `HUBPRET1_*` and `HUBPRET2_*`: hub return control, DET buffer plane base and crossbar selection, memory power control/status, read-line controls and read-line values, read-line status, and interrupt mask/type/status/ack fields for DET buffer underflow and read-line events.
- `CURSOR0_1_*` and `CURSOR0_2_*`: cursor control, cursor surface addresses, size, position, hot spot, stereo control, destination offset, cursor memory power control/status, and display metadata (`DMDATA`) address/control/QoS/status/software-data fields.

The repeated suffixes `1`, `2`, and `3` are hardware pipe or instance selectors. The field layouts are mostly cloned across instances, so a consumer normally writes generic HUBP code against `HUBPREQ0_*` masks in register-table macros and instantiates addresses per pipe with `SRI(..., id)`.

## Control Flow

This header chunk has no control flow. It is declarative hardware layout data used by code that builds register descriptor tables and then performs MMIO read-modify-write operations.

Runtime use follows this pattern:

1. DCN 2.1 display code includes `dcn_2_1_0_offset.h` for register addresses and `dcn_2_1_0_sh_mask.h` for field masks/shifts.
2. Resource, hubp, cursor, IRQ, GPIO, and DMUB code expands generated names through macros such as `SRI(...)`, `HUBP_SF(...)`, and related register-list helpers.
3. HUBP code programs surface format, tiling, addresses, viewport, VMID, flip control, DCC/TMZ, TTU/QoS, VM aperture, TLB, blanking, prefetch, and delivery timing fields during plane updates, flips, modesets, and power transitions.
4. Cursor and DMDATA code programs cursor address/geometry/hotspot/stereo state and metadata packets used by display streams.
5. IRQ and diagnostic paths read or acknowledge flip, HUBPRET, and perfmon status fields and may configure perf counters for display-block profiling.

The macros do not encode sequencing. Consumers must know when clocks are enabled, when double-buffered plane updates latch, how flip-pending and interrupt bits are cleared, and which fields are read-only status versus writable control.

## State And Persistence Behavior

The header stores no software state and persists nothing. It describes MMIO-backed GPU display hardware state.

The represented hardware state includes:

- Plane and surface state: pixel format, rotation, mirror, tiling/swizzle, address-bank configuration, luma/chroma viewport geometry, pitches, primary/secondary surface addresses, metadata addresses, DCC enablement, TMZ protection bits, and current in-use/earliest-in-use addresses.
- Flip and update state: flip type/mode, stereo sync, flip pending, surface update lock, master update lock status, triple buffering, VM update mode, flip clear/status bits, and flip-away interrupt fields.
- Memory-system and QoS state: request-size tuning, DRQ/CRQ/MRQ/PRQ expansion modes, TTU/QoS watermarks, request-delivery reference-cycle values for surfaces and cursors, prefetch ratios, vblank/flip/nominal PTE/meta timing, VM system aperture, and L1 TLB/system-access controls.
- Power and clock state: HUBP clock enable/disable and gating controls, DCFCLK/DPPCLK measurement controls, HUBPREQ/HUBPRET/CURSOR memory power force/disable/status fields, and virtual-memory page config.
- Cursor and metadata state: cursor mode, 2x magnify, pitch, alpha and color controls, surface address, size/position/hotspot/stereo settings, destination offsets, and DMDATA buffer address/control/status/QoS/software data.
- Diagnostics and events: HUBPRET read-line status and interrupt fields, HUBPREQ debug DB, perfmon counter active/state/interrupt/value fields, and measurement-window counters.

Persistence depends on hardware behavior outside this generated header. Some fields are normal configuration that remains until a modeset, plane update, power-gating transition, suspend/resume, or ASIC reset. Others are status, sticky interrupt, snapshot, self-clearing request, or read-only diagnostic fields. Names such as `*_INT_STATUS`, `*_ACK`, `*_CLEAR`, `*_PENDING`, `*_INUSE`, `*_MEM_PWR_STATUS`, and `*_CLOCK_ENABLE` should be treated as side-effect-sensitive unless the consuming driver path or hardware specification proves otherwise.

## Dependencies And Integration Points

This chunk depends on the matching generated address header:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_2_1_0_offset.h`

Direct include points for `dcn_2_1_0_sh_mask.h` in this tree include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn21/dcn21_resource.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn21/irq_service_dcn21.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn21/hw_factory_dcn21.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn21/hw_translate_dcn21.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn21.c`

The closest generic consumers are the DCN hub pipe implementations and register-list definitions under `display/dc/hubp`, especially `dcn10_hubp.h` and DCN 2.x variants. They define HUBP register lists for `DCSURF_*`, `HUBPREQ_*`, and `HUBPRET_*` registers, then bind fields with `HUBP_SF(HUBPREQ0_..., FIELD, mask_sh)` style macros. Runtime code in `dcn10_hubp.c` and DCN 2.x hubp files uses those tables to program plane addresses, viewport, tiling, DCC, flip behavior, VM/TLB state, QoS timing, DET/read-line state, and power controls.

IRQ integration uses `HUBPREQ` entries for surface-flip interrupts. DMUB integration includes the DCN 2.1 offset/mask headers so firmware mailbox and register access code can use the same generated register contract. Legacy memory-management code in adjacent ASIC generations also reads `HUBPREQ*_DCSURF_SURFACE_PITCH` via `REG_GET_FIELD`, illustrating why the generated pitch masks must remain compatible with MMIO consumers.

## Risks And Edge Cases

- These macros are a hardware ABI. Wrong masks or shifts usually compile successfully but write the wrong bits, causing blank planes, corrupted scanout, broken flips, bad cursor placement, incorrect DCC/TMZ state, or QoS underflow failures.
- Repeated instance blocks create drift risk. `HUBP1`, `HUBP2`, and `HUBP3`, plus `HUBPREQ1/2/3`, `HUBPRET1/2`, `CURSOR0_1/2`, and `DC_PERFMON8/9`, are highly similar. A single copied mask from the wrong instance can produce failures only on one pipe or high display count.
- The chunk boundaries are artificial. The first lines are only the tail masks of `DC_PERFMON7_PERFCOUNTER_CNTL`, and the final line stops before the complete `HUBPREQ3_PER_LINE_DELIVERY` mask list. Whole-file conclusions require adjacent chunks.
- Packed fields require read-modify-write discipline. Surface control, flip control, QoS, memory power, cursor control, DMDATA control, and interrupt registers pack unrelated fields together; full-register writes can corrupt neighboring state.
- Flip and interrupt fields may be sticky or write-one-to-clear. Misusing `SURFACE_FLIP_CLEAR`, `SURFACE_FLIP_AWAY_CLEAR`, `*_INT_ACK`, or status fields can miss flips, leave stale interrupts, or produce interrupt storms.
- Address fields are split into low/high words and luma/chroma/metadata variants. Mixing primary, secondary, chroma, or metadata address masks can scan out stale memory, break stereo/dual-plane formats, or violate protection settings.
- VM/TLB and TMZ/DCC fields interact with memory management and compression. Bad masks can cause page faults, decompression artifacts, security-policy mistakes for trusted memory, or failures limited to compressed/protected surfaces.
- QoS and prefetch timing fields are workload-sensitive. Incorrect `REFCYC_*`, `DST_Y_*`, `VRATIO_*`, or TTU watermark masks may only show up at high resolution, high refresh, multi-plane, scaling, cursor-heavy, or low-memory-clock conditions.
- Power and clock fields have sequencing dependencies not represented here. Accessing HUBP/HUBPREQ/HUBPRET/CURSOR state while clocks or memories are disabled may return stale data or drop writes.

## Test Signals

Useful validation is compile-time plus hardware behavior:

- Build AMDGPU/DC with DCN 2.1 support; missing or renamed macros should fail at include sites and in generated HUBP/IRQ/DMUB/GPIO register tables.
- Diff this generated chunk against AMD's register database and adjacent DCN family headers to catch instance drift across `HUBP1/2/3`, `HUBPREQ1/2/3`, `HUBPRET1/2`, `CURSOR0_1/2`, and `DC_PERFMON8/9`.
- Exercise multi-display DCN 2.1 hardware with enough active pipes to use instances 1, 2, and 3. Validate modesets, page flips, plane enable/disable, cursor movement, cursor format changes, scaling, rotation/mirroring, suspend/resume, hotplug, and DPMS.
- Test luma/chroma and metadata address paths with RGB and YUV formats, DCC-enabled surfaces, primary and secondary surfaces, and protected/TMZ surfaces where supported.
- Stress flip paths: immediate and vblank-synchronized flips, triple buffering, stereo sync modes, update locks, flip-away interrupt handling, and flip-pending status.
- Validate bandwidth and QoS behavior at high resolution/refresh and low memory-clock states. Watch for underflow, flicker, corruption, missed vblank, stalled flips, and failures that appear only with multiple planes or cursors.
- Exercise cursor and DMDATA programming: large cursor sizes, hot-spot offsets, stereo cursor settings, cursor memory power transitions, metadata address/control/QoS/status updates, and software DMDATA writes.
- Use perfmon tests or debug tools to configure `DC_PERFMON8` and `DC_PERFMON9`, start/stop counters, read low/high values, and verify interrupt/status/ack behavior.
- Monitor kernel logs and display diagnostics for hubp underflow, page faults, DCC errors, flip timeout, IRQ storms, power-gating resume failures, and pipe-specific regressions.

## Cross-Chunk Notes

Previous chunks of `dcn_2_1_0_sh_mask.h` define the earlier `DC_PERFMON7_PERFCOUNTER_CNTL` shift fields and masks before line 9804. Later chunks continue `HUBPREQ3_PER_LINE_DELIVERY` and the remaining DCN 2.1 generated register namespace. The final per-file research document should merge those chunks before making complete claims about perfmon7 or pipe instance 3 coverage.
