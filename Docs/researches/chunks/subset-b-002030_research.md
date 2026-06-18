# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_2_1_sh_mask.h lines 7583-10082

## Scope

This chunk is a generated AMD DCN 3.2.1 register field shift/mask header segment. It covers 2,500 source lines and 2,111 `#define` entries. The chunk has no executable C code; its API surface is the macro namespace that gives low-bit shifts and already-positioned masks for display HUBP, HUBPREQ, HUBPRET, cursor, DMDATA, VM, timing, MALL, power, and status registers.

The range begins at the tail of pipe 0 HUBPRET read-line status, covers the pipe 0 cursor block, then spans the complete visible HUBP/HUBPREQ/HUBPRET/cursor groups for pipes 1 and 2. It ends inside the pipe 3 HUBPREQ timing block at `HUBPREQ3_PREFETCH_SETTINGS__VRATIO_PREFETCH__SHIFT`, so adjacent chunks are needed to complete pipe 3.

## Purpose

The purpose of this header slice is to provide compile-time metadata for packing and unpacking DCN 3.2.1 display hub register fields. Every hardware field is represented as:

- `<REGISTER>__<FIELD>__SHIFT`, the least-significant bit position.
- `<REGISTER>__<FIELD>_MASK`, the field mask in its register position.

Driver code combines these constants with register offset macros from `dcn_3_2_1_offset.h` and register helper macros from AMD Display Core. This keeps register programming code focused on semantic field names such as `SURFACE_PIXEL_FORMAT`, `CURSOR_ENABLE`, `VMID`, `SURFACE_FLIP_PENDING`, `REFCYC_PER_REQ_DELIVERY`, or `HUBP_UNDERFLOW_STATUS`, while the generated header preserves the exact silicon bit layout.

## Important APIs, Types, And Macros

There are no functions, structs, enums, or storage objects in this chunk. The important API is the set of generated preprocessor constants.

The covered register families include:

- `HUBPRET0_HUBPRET_READ_LINE_STATUS`: pipe 0 read-line/vblank status bits at the chunk boundary.
- `CURSOR0_0_*`, `CURSOR0_1_*`, and `CURSOR0_2_*`: cursor enable, request mode, magnification, mode, trusted-memory-zone bit, pitch, line chunking, surface address, size, position, hot spot, stereo offsets, destination offset, cursor memory power state, and DMDATA controls/status.
- `HUBP1_*` and `HUBP2_*`: surface format, rotation, mirror, alpha-plane enable, tiling/address configuration, primary/secondary viewport geometry for luma and chroma planes, request sizing, HUBP blank/reset/status controls, clock gating/status, virtual-memory page config, MALL config, sub-viewport MALL start lines, clock-measurement windows, and MALL state.
- `HUBPREQ1_*` and `HUBPREQ2_*`: surface pitch, VMID, primary/secondary and meta surface addresses for luma/chroma, TMZ and DCC surface-control bits, flip control, flip interrupts, in-use/earliest-in-use address readbacks, expansion modes, TTU/QoS controls, DMDATA VM controls, system aperture and L1 TLB controls, blank/destination/prefetch timing, vblank/flip/nominal delivery parameters, cursor fetch settings, memory power controls/status, UCLK p-state force controls, and request/status registers.
- `HUBPRET1_*` and `HUBPRET2_*`: DET buffer base, crossbar source selection, pack disable, memory power control/status, read-line thresholds, interrupt fields, read-line values, and read-line status.
- `HUBP3_*` and the start of `HUBPREQ3_*`: pipe 3 repeats the same HUBP surface, viewport, request-size, MALL, and early HUBPREQ surface-address/flip/VM/timing layout before the chunk cuts off.

The macro prefixes are pipe-indexed. For example, `HUBPREQ1_DCSURF_PRIMARY_SURFACE_ADDRESS_HIGH__PRIMARY_SURFACE_ADDRESS_HIGH_MASK` and `HUBPREQ2_DCSURF_PRIMARY_SURFACE_ADDRESS_HIGH__PRIMARY_SURFACE_ADDRESS_HIGH_MASK` describe the same field shape on different hardware instances. Higher-level register table macros typically use pipe 0 names as templates and pair them with per-instance register offsets.

## Control Flow And Behavior

This header has no runtime control flow. Runtime behavior appears when included by DCN 3.2.1 resource construction and consumed through AMD Display Core register helper tables.

A typical consumer flow is:

1. A DCN 3.2.1 resource file includes `dcn_3_2_1_offset.h` and `dcn_3_2_1_sh_mask.h`.
2. HUBP/DPP/IPP register-table macros such as `HUBP_SF` or related field-list helpers copy the generated shift and mask values into hardware block descriptors.
3. Runtime code uses `REG_UPDATE`, `REG_UPDATE_N`, `REG_GET`, or related helpers to modify fields by semantic names rather than open-coded bit arithmetic.
4. Hardware latches the values into the display hub pipeline, where they control fetch addresses, tiling, DCC/TMZ, timing, prefetch, VM translation, cursor fetch, MALL behavior, and flip synchronization.

Important implied hardware flows represented by the chunk:

- Plane programming: pixel format, rotation, mirror, alpha-plane state, address configuration, tiling, viewport start/dimension, pitch, DCC, TMZ, primary/secondary surface addresses, and meta addresses describe how HUBP fetches the current scanout surface.
- Flip sequencing: `DCSURF_FLIP_CONTROL`, `DCSURF_FLIP_CONTROL2`, `SURFACE_FLIP_INTERRUPT`, in-use address registers, earliest-in-use registers, stereo sync fields, GSL/triple-buffer controls, and pending-delay/min-time fields support atomic flips and frame-latched surface transitions.
- Display timing and watermarks: `BLANK_OFFSET_*`, `DST_DIMENSIONS`, `DST_AFTER_SCALER`, `PREFETCH_SETTINGS`, `VBLANK_PARAMETERS_*`, `FLIP_PARAMETERS_*`, `NOM_PARAMETERS_*`, `PER_LINE_DELIVERY*`, `DCN_TTU_QOS_WM`, and `DCN_*_TTU_CNTL*` encode DML-derived delivery timing and QoS programming.
- VM and memory fetch: VMID, system aperture, L1 TLB enable/mode, VM group/request timing, page-table request sizes, DPTE/MPTE/meta/PDE memory power fields, and DMDATA VM fault/underflow/late/done status connect display fetch to GPU virtual memory.
- Cursor and DMDATA: cursor address, size, position, hot spot, stereo, chunking, memory power, DMDATA address/control/QoS/status, and software DMDATA controls support hardware cursor display and display metadata delivery.
- MALL and power management: `DCHUBP_MALL_CONFIG`, `DCHUBP_MALL_SUB_VP`, `HUBP_MALL_STATUS`, `UCLK_PSTATE_FORCE`, clock gates, memory power state fields, self-refresh allowances, and p-state status bits expose low-power scanout and memory/cache behavior.
- Interrupt/status paths: read-line/vblank, flip, timeout, underflow, segmentation allocation error, MALL status, VM faults, and request-status registers provide diagnostics and event state.

## State And Persistence

The header itself stores no state. Its constants describe state held in GPU hardware registers after driver or firmware writes them.

State classes represented here include:

- Latched plane state: format, tiling, viewport, pitch, surface and metadata addresses, VMID, TMZ/DCC enablement, and cursor address/geometry persist in the display pipe until reprogrammed, reset, or power-gated.
- Flip and scanout state: pending, in-use, earliest-in-use, stereo-sync, update-lock, GSL, and triple-buffer fields track transition state across frame and vblank boundaries.
- Timing state: prefetch, vblank, flip, nominal, TTU, QoS, and per-line delivery fields are derived from mode timing and bandwidth calculations and must match the current stream/plane configuration.
- VM and fault state: system aperture, L1 TLB mode, VMID, DMDATA VM status, underflow, late, fault status, and clear bits are tied to GPU VM programming and display fetch health.
- Power and residency state: clock-enable/status, memory power force/disable/state, MALL use, sub-viewport MALL retrieval, self-refresh, p-state allowance, and UCLK force bits reflect low-power display operation.
- Sticky or clear-on-write status: underflow clear, timeout status clear, DMDATA underflow/fault clears, flip clears, and read-line interrupt clears likely require precise hardware-defined write sequences.

Because this is a generated bitfield schema, it does not encode read/write permissions, reset defaults, legal enumerations, self-clearing behavior, polling requirements, or ordering constraints. Those rules live in the hardware programming sequence and in the display core functions that use the fields.

## Dependencies And Integration Points

This chunk depends on the matching DCN 3.2.1 generated register map:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_2_1_offset.h`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_2_1_sh_mask.h`

`dcn321_resource.c` directly includes both generated headers. HUBP field-list macros in files such as `display/dc/hubp/dcn31/dcn31_hubp.h`, `display/dc/hubp/dcn32/dcn32_hubp.h`, and the shared DCN hubp headers consume the same field names through `HUBP_SF` definitions. The resulting mask/shift descriptors are used by hubp implementation files through register helpers such as `REG_UPDATE`, `REG_UPDATE_2`, `REG_UPDATE_4`, `REG_GET`, and related macros.

Cursor fields also integrate with DMUB cursor offload payload structures in `display/dmub/inc/dmub_cmd.h`, which use matching field-oriented names for cursor address, size, position, hot spot, destination offset, enable, mode, magnification, pitch, and line-chunk data. This means cursor register layout changes affect both host-side register programming and firmware offload command interpretation.

Even though this repository path is under `ceph-client`, the researched code is AMDGPU display hardware metadata. It has no Ceph filesystem protocol behavior, distributed filesystem persistence, or storage control flow.

## Risks And Edge Cases

- Silent hardware misprogramming: a wrong `_MASK` or `__SHIFT` compiles cleanly but can update the wrong MMIO bits, causing blank screens, underflow, incorrect colors, address faults, or unstable flips.
- Pipe-index repetition: the same field shapes are repeated for `HUBP1`, `HUBP2`, `HUBP3`, `HUBPREQ1`, `HUBPREQ2`, `HUBPREQ3`, `HUBPRET1`, `HUBPRET2`, and cursor instances. Generation or copy errors can be valid C while affecting only one physical pipe.
- Chunk boundaries: the range starts after the beginning of the pipe 0 HUBPRET block and ends inside `HUBPREQ3_PREFETCH_SETTINGS`; final per-file analysis must reconcile adjacent chunks before drawing conclusions about full pipe 0 or pipe 3 coverage.
- Address width and high-bit handling: surface and metadata addresses are split into low 32-bit and high 16-bit fields, with VMID fields often in high address registers. Incorrect packing can point scanout at the wrong memory object or VM context.
- Flip synchronization hazards: update locks, pending flags, stereo sync mode, GSL enable/mask, triple buffering, and in-use address readbacks are timing-sensitive and can deadlock or tear if accessed out of order.
- VM and fault clear hazards: DMDATA VM fault, underflow, late, done, system aperture, L1 TLB mode, and clear fields can mask real GPU VM faults or leave stale fault state if decoded incorrectly.
- Power-management coupling: MALL, UCLK p-state force, self-refresh allow bits, memory power force/disable/state, and clock-gating fields interact with runtime power management and display underflow margins.
- Reserved or status fields: status and clear bits should not be treated as ordinary writable configuration fields. The header names and masks alone do not prevent unsafe writes.

## Test Signals

Useful validation signals for consumers of this chunk include:

- Kernel build coverage for DCN 3.2.1 display resource construction and HUBP/DPP/IPP register-table initialization.
- Generated-header consistency checks that every paired `_MASK` and `__SHIFT` describes a non-overlapping field and matches the authoritative register database.
- Boot and modeset tests on DCN 3.2.1 hardware using all available display pipes, with rotation, mirroring, alpha planes, luma/chroma surfaces, DCC, TMZ, and cursor enabled.
- Atomic page-flip and vblank tests that exercise update locks, flip pending, flip interrupts, stereo/GSL/triple-buffer paths, in-use address readbacks, and earliest-in-use tracking.
- Cursor tests for address split, size, hot spot, position, destination offset, magnification, pitch, chunk size, MALL cursor caching, and DMUB cursor offload.
- Display bandwidth and DML validation using high-resolution and multi-plane modes to confirm prefetch, vblank, flip, nominal, TTU, QoS, and per-line delivery programming avoids underflow.
- GPU VM tests that exercise display VMID, system aperture, L1 TLB, DMDATA VM fault/underflow/late/done status, and VM fault clear behavior.
- Runtime power tests covering MALL, sub-viewport MALL, static-screen behavior, UCLK/FCLK p-state transitions, clock gating, memory power state, suspend/resume, and hotplug.
- Debugfs or trace readbacks for HUBP underflow, timeout, segment allocation errors, read-line/vblank status, MALL status, DMDATA status, flip status, and request status registers.

## Research Notes

The source was read as a large generated-header chunk rather than as hand-written logic. The final per-file research document should merge this with neighboring chunks of `dcn_3_2_1_sh_mask.h` so the complete repeated-pipe layout is described once, with this chunk contributing the pipe 1/2 hub, request, return, cursor, VM, MALL, timing, and status details plus the pipe 3 boundary note.
