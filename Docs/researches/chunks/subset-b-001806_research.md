# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_2_sh_mask.h lines 9887-12399

## Scope And Purpose

This chunk is generated AMD DCN 3.1.2 register shift/mask metadata. It contains preprocessor constants that describe bit positions (`__SHIFT`) and masks (`_MASK`) for display-controller MMIO registers. The matching `dcn_3_1_2_offset.h` header supplies register offsets; this header supplies the field layout consumed by AMD display register helpers.

The requested range contains 2,106 `#define` lines: 1,052 shift macros and 1,054 mask macros. It starts in the tail of the `DC_PERFMON6_PERFMON_CNTL` mask definitions, completes the rest of perfmon 6, then covers HUBP/HUBPREQ/HUBPRET/cursor/perfmon register fields for HUBP instances 0 and 1. It then starts the same generated register layout for HUBP instance 2 and stops in the middle of `HUBPREQ2_HUBPREQ_MEM_PWR_CTRL`; `REQ_PDE_MEM_PWR_*` masks and the following memory-power status fields continue in the next chunk.

There are no functions, structs, branches, loops, local includes, allocations, locks, or direct runtime side effects in this chunk. The exported surface is macro metadata. Runtime behavior appears when DCN 3.1 resource, HUBP, IRQ, and DMUB code binds these macros into register tables and later uses `REG_SET`, `REG_UPDATE`, `REG_GET`, and related helpers to program or read hardware.

Although the repository path is under a `ceph-client` mirror, this source is AMDGPU display-driver hardware metadata. It does not implement distributed filesystem behavior.

## Register Blocks Covered

The chunk begins with the end of `DC_PERFMON6`, including perfmon count-off mask bits, count-off interrupt type/clock/start-stop selection, counter-value interrupt status and acknowledgement bits, high counter-value readback, and low/high perfmon readback registers.

For `HUBP0`, `HUBP1`, and the beginning of `HUBP2`, the generated `dce_dc_dcbubp*_dispdec_hubp_dispdec` blocks define fields for:

- Surface format, rotation, horizontal mirror, alpha plane enable, address configuration, tiling configuration, primary/secondary viewport start and dimension fields, and chroma-plane viewport equivalents.
- Request sizing for luma and chroma planes: swath height, PTE row height, chunk size, minimum chunk size, metadata chunk size, DPTE group size, and VM group size where present.
- HUBP control state: blank enable/in-blank status, no outstanding requests, soft reset, VTG selection, vready/vsync relation, stop-data behavior during VM activity, unbounded request mode, segment allocation error status, TTU mode/disable, timeout fields, underflow status, and underflow clear.
- Clock-control and measurement-window fields for HUBP, DCFCLK, and DPPCLK timing measurement.

For `HUBPREQ0`, `HUBPREQ1`, and partial `HUBPREQ2`, the range defines request-path fields for:

- Surface pitch, chroma pitch, VMID selection, primary/secondary luma and chroma surface addresses, metadata addresses, in-use address readbacks, and earliest-in-use address readbacks.
- Surface control bits for TMZ and DCC enable/independent-block state across primary, secondary, luma, chroma, and metadata surfaces.
- Flip controls, stereo-sync flip behavior, pending/update-lock status, triple buffering, global swap lock enable, and surface flip interrupt mask/type/status/clear fields.
- Request expansion mode, TTU QoS watermarks, global TTU controls, per-surface and cursor TTU controls, VM aperture and L1 TLB controls, blank offset, destination timing, prefetch timing, vblank/flip/nominal delivery parameters, per-line delivery parameters, cursor request settings, reference-to-pixel clock ratio, DRQ delta limits, and request-path memory power controls/status.

For `HUBPRET0` and `HUBPRET1`, the generated `hubpret` blocks cover detile buffer and post-request processing: plane-1 DET buffer base address, pack-3-to-2 element disable, component crossbar source selection for alpha/Y-G/Cb-B/Cr-R, memory-power controls and status for DMROB and PIXCDC memories, read-line control windows, read-line values/status, and pipe vblank/read-line interrupt mask/type/clear/status fields.

For `CURSOR0_0` and `CURSOR0_1`, the chunk covers cursor and DMDATA fields: cursor enable/mode/request mode, 2x magnification, pitch, lines-per-chunk, address high/low, size, position, hot spot, stereo control, destination X offset, cursor memory power status/control, DMDATA address, control, QoS, status, and software data/update fields.

`DC_PERFMON7` and `DC_PERFMON8` repeat the standard DC performance monitor field layout for HUBP instances 0 and 1. The visible fields include perf counter control, secondary counter control, state/readback fields, perfmon control, perfmon secondary control, interrupt/ack status for counter values, and low/high readback registers.

## Important APIs, Types, And Macros

The important interface is the generated macro naming contract:

- `<register>__<field>__SHIFT` gives the field bit offset in a 32-bit register.
- `<register>__<field>_MASK` gives the field mask.
- Comments such as `//HUBP0_DCSURF_SURFACE_CONFIG` and `// addressBlock: ...` delimit generated register groups but are not compiled APIs.
- Instance prefixes in this chunk include `HUBP0`, `HUBPREQ0`, `HUBPRET0`, `CURSOR0_0`, `DC_PERFMON7`, the matching instance-1 prefixes, and partial instance-2 `HUBP2`/`HUBPREQ2`.

The main DCN 3.1 include path is `display/dc/resource/dcn31/dcn31_resource.c`, which includes `dcn/dcn_3_1_2_offset.h` and this `dcn/dcn_3_1_2_sh_mask.h`. It builds per-HUBP register tables with `HUBP_REG_LIST_DCN30(id)` and initializes shared shift/mask tables using `HUBP_MASK_SH_LIST_DCN31(__SHIFT)` and `HUBP_MASK_SH_LIST_DCN31(_MASK)`. `dcn31_hubp_create()` then constructs HUBP objects through `hubp31_construct()`.

`display/dc/hubp/dcn31/dcn31_hubp.h` maps canonical driver field names to the instance-0 generated macros through `HUBP_SF(...)`. The runtime code can then use generic field names such as `DCSURF_SURFACE_CONFIG.SURFACE_PIXEL_FORMAT`, `DCHUBP_CNTL.HUBP_UNDERFLOW_CLEAR`, `DCSURF_SURFACE_CONTROL.PRIMARY_SURFACE_DCC_EN`, `HUBPRET_CONTROL.CROSSBAR_SRC_Y_G`, `CURSOR_CONTROL.CURSOR_REQ_MODE`, and `DMDATA_CNTL.DMDATA_UPDATED` while resource construction supplies per-instance offsets.

The runtime implementation lives mostly in the DCN10/DCN20/DCN30/DCN31 HUBP code. `dcn31_hubp.c` adds DCN31-specific operations such as unbounded requesting, cursor request mode, soft reset, extended blank programming, and segment allocation error readback. Broader inherited paths program surface config, flips, VM apertures, DCC, viewport, cursor attributes/position, DMDATA, underflow handling, clock control, and register-state readback through these generated masks.

`display/dc/irq/dcn31/irq_service_dcn31.c` includes the same generated header for interrupt register mapping, including HUBPREQ page-flip-related fields. `display/dmub/src/dmub_dcn31.c` also includes the DCN 3.1.2 offset and mask headers so DMUB-facing code can share the same register field definitions.

## Functional Field Groups

Surface and viewport fields describe how a HUBP fetches primary and secondary planes. Pixel format, rotation, mirror, alpha enable, tiling mode, address pipe/interleave configuration, luma/chroma viewport starts and dimensions, and pitch fields must match the framebuffer layout and scaler input expectations.

Address and metadata fields expose the base addresses for luma/chroma primary and secondary surfaces plus metadata planes. The matching in-use and earliest-in-use readback fields let the driver reason about which addresses hardware has consumed during flips and surface updates.

Request-size, TTU, prefetch, vblank, flip, nominal, and per-line delivery fields are the low-level bandwidth scheduling surface. The display mode library computes delivery timing and request sizes; HUBP programming writes those values through fields such as `SWATH_HEIGHT`, `CHUNK_SIZE`, `DPTE_GROUP_SIZE`, `REFCYC_PER_REQ_DELIVERY`, `DST_Y_PREFETCH`, `REFCYC_PER_PTE_GROUP_*`, and `REFCYC_PER_META_CHUNK_*`.

VM and memory-protection fields include VMID selection, VM system aperture bounds, L1 TLB enable/access-mode controls, TMZ bits on surface and metadata paths, and DMDATA VM fault/underflow/late status in the DCN31 mask list. These fields connect scanout fetches to GPU virtual memory, protected memory, and fault reporting.

Flip and update fields handle double-buffered surface changes. `SURFACE_FLIP_PENDING`, `SURFACE_UPDATE_LOCK`, `HUBPREQ_MASTER_UPDATE_LOCK_STATUS`, `SURFACE_TRIPLE_BUFFER_ENABLE`, `SURFACE_GSL_ENABLE`, and flip interrupt fields tell the driver when a pending address/config update has been latched or when it should hold updates for synchronization.

HUBP control fields expose enable/reset/error state. Blanking, in-blank status, no-outstanding-request status, soft reset, VTG selection, unbounded request mode, timeout, underflow, segment allocation error, and TTU controls are used during modeset, blanking, recovery, diagnostics, and bandwidth-sensitive operation.

HUBPRET fields configure data unpacking and component routing after request processing. DET buffer base selection, pack-3-to-2 disable, and component crossbar selections must match plane format and downstream pixel processing assumptions.

Cursor and DMDATA fields provide the per-pipe cursor plane and metadata path. Cursor address, size, mode, request mode, pitch, magnification, position, hotspot, stereo, memory power, and destination offset fields are paired with DMDATA address/control/QoS/status/software update fields for metadata delivery.

Perfmon fields expose hardware diagnostic counters. Counter enable, clear, event selection, threshold, interrupt status/ack, read selection, and low/high counter readback fields are stateful observability surfaces rather than display-mode configuration.

## Control Flow And State Behavior

This header has no direct control flow. Runtime sequencing comes from resource construction and register helper calls:

1. DCN31 resource code includes the DCN 3.1.2 offset and shift/mask headers.
2. Register-list macros paste each instance number into generated names such as `HUBP1_DCHUBP_CNTL`, `HUBPREQ1_DCSURF_SURFACE_CONTROL`, or `CURSOR0_1_CURSOR_CONTROL`.
3. `hubp31_construct()` stores per-instance register offsets plus shared shift/mask tables in each HUBP object.
4. HUBP, IRQ, and DMUB code later use those tables to read, write, poll, clear, or update hardware registers.

Hardware state represented by these fields persists in DCN registers until the driver, DMUB, power-management logic, reset logic, or hardware status events change it. Configuration state includes surface format, tiling, addresses, pitches, viewport, request sizing, TTU/delivery timing, VM aperture, flip policy, cursor attributes, DMDATA attributes, memory-power force/disable bits, and perfmon configuration. Live status includes flip pending, update-lock status, in-use addresses, earliest-in-use addresses, no-outstanding-request, underflow/timeout/segment-error flags, interrupt status, memory-power state, read-line state, DMDATA done/fault/late indicators, and perfmon counter values.

Several groups are ordering-sensitive. Surface address and metadata writes are double-buffered around flip/update controls. TTU and prefetch values must align with timing and watermark calculations before scanout depends on them. Cursor and DMDATA updates require coherent address/control/QoS/status sequencing. Memory-power force or disable fields should not be changed while the corresponding request, cursor, metadata, or HUBPRET memory is actively needed.

## Dependencies And Integration Points

This file must stay synchronized with `dcn_3_1_2_offset.h`. The offset header gives the MMIO addresses for the same register names, while this header gives the field layout. A mismatch can either fail compilation in token-pasted register lists or silently program the wrong bits if both names still exist but no longer describe the same hardware field.

The direct include sites visible in this tree are:

- `display/dc/resource/dcn31/dcn31_resource.c`
- `display/dc/irq/dcn31/irq_service_dcn31.c`
- `display/dmub/src/dmub_dcn31.c`

The primary HUBP integration point is `display/dc/hubp/dcn31/dcn31_hubp.h`, whose `HUBP_MASK_SH_LIST_DCN31` consumes many fields from this chunk. The associated runtime code in `dcn31_hubp.c` and inherited DCN10/DCN20/DCN30 HUBP implementations programs surfaces, DCC, VM, TTU, blanking, flip, cursor, and DMDATA state through these masks.

IRQ integration uses HUBPREQ flip interrupt fields and related masks so page-flip and timing interrupt handling can map source IDs to concrete register bits. DMUB integration shares the same generated definitions for firmware-command register programming and state capture.

The register families are repeated per HUBP instance. Resource construction relies on instance-0 shift/mask definitions as the canonical field layout and combines them with instance-specific offsets. The generated fields for instances 1 and 2 in this chunk therefore serve both as direct metadata and as consistency evidence that the repeated hardware blocks have matching layouts.

## Risks And Edge Cases

Generated-header drift is the central risk. A wrong shift or mask can compile cleanly while corrupting scanout format, address, pitch, tiling, viewport, DCC/TMZ, request sizing, TTU timing, cursor, DMDATA, memory-power, interrupt, or perfmon behavior.

The chunk boundaries are artificial. The first lines are only the tail of `DC_PERFMON6_PERFMON_CNTL`, and the final line stops inside `HUBPREQ2_HUBPREQ_MEM_PWR_CTRL`. Adjacent chunks are required before making complete file-level claims about perfmon 6 or HUBP instance 2.

Bandwidth and timing fields are high impact. Incorrect swath/chunk/group sizes or delivery timings may only fail under high resolution, high refresh rate, DSC, multi-plane, chroma, or bandwidth-pressure scenarios, where symptoms show up as underflow, corruption, missed flips, or unstable power/performance behavior.

Address, VM, TMZ, and metadata fields are security- and stability-sensitive. Incorrect VMID, aperture, surface address, metadata address, or TMZ/DCC mask handling can fetch from the wrong memory, mishandle protected content, trigger VM faults, or produce display corruption that is hard to attribute to a single register field.

Flip and update fields are synchronization-sensitive. Code that mishandles update locks, pending bits, triple buffering, GSL enablement, or interrupt clear/status semantics can lose page flips, report vblank completion too early, or leave a plane stuck on an old surface.

Memory-power fields can create intermittent failures around blanking, suspend/resume, clock gating, and modeset. Forcing or disabling DPTE/MPTE/meta/PDE/cursor/HUBPRET memories at the wrong time can make otherwise valid register programming fail only during power-state transitions.

Perfmon fields are diagnostic state. Wrong event selection, clear/enable ordering, read selection, threshold programming, or interrupt acknowledgement can make profiling data misleading without visibly breaking display output.

## Test Signals

Build-time coverage should catch missing or renamed generated macros in `dcn31_resource.c`, `dcn31_hubp.h`, `irq_service_dcn31.c`, and `dmub_dcn31.c`. High-signal compile failures include missing `HUBP0_*`, `HUBPREQ0_*`, `HUBPRET0_*`, `CURSOR0_0_*`, or `DC_PERFMON*` field names referenced through the register-list macros.

Mechanical validation should compare this chunk against the authoritative DCN 3.1.2 register database and verify that repeated instance families remain structurally consistent across HUBP0, HUBP1, and HUBP2 where covered. The requested range has a nearly one-to-one shift/mask pairing, with imbalance explained by the partial start and partial end.

Runtime display validation should exercise modesets across enough active pipes to use HUBP instances 0, 1, and 2. Useful signals include correct plane format, rotation, mirroring, alpha handling, viewport/crop, pitch, tiling, DCC, TMZ, and chroma-plane behavior.

Bandwidth validation should cover high-resolution and multi-plane modes that stress DML-calculated swath, chunk, group-size, prefetch, vblank, flip, nominal, and per-line delivery parameters. Watch for HUBP underflow, timeout, segment allocation errors, stuck no-outstanding-request state, visual corruption, and watermark-related regressions.

Flip validation should cover immediate flips, vblank-synchronized flips, triple buffering, global swap lock, update lock/unlock, page-flip interrupts, and in-use/earliest-in-use readbacks. Correct behavior is pending bits clearing at the intended update point and no lost or early-completed flips.

Cursor and DMDATA tests should cover cursor enable/disable, mode, size, position, hotspot, 2x magnification, stereo, destination offset, cursor memory power, metadata update/repeat/size, QoS, and DMDATA completion/fault signals.

Power-management and resume tests should exercise blanking, soft reset, clock gating, memory-power controls/status, suspend/resume, hotplug modesets, and repeated stream enable/disable cycles. Perfmon tests should validate clear/enable/readback sequencing for `DC_PERFMON6`, `DC_PERFMON7`, and `DC_PERFMON8` where available.

## Cross-Chunk Notes

The previous chunk owns the beginning of `DC_PERFMON6_PERFMON_CNTL`. The next chunk completes `HUBPREQ2_HUBPREQ_MEM_PWR_CTRL`, covers `HUBPREQ2_HUBPREQ_MEM_PWR_STATUS`, and continues the remaining HUBP instance-2 generated fields. The later merge/reconciliation lane should combine these adjacent chunk documents before presenting complete per-file coverage for `dcn_3_1_2_sh_mask.h`.
