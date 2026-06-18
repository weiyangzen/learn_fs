# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_5_0_sh_mask.h lines 13253-15470

## Scope And Purpose

This chunk is part of AMD's generated DCN 3.5.0 register shift/mask header. It contains C preprocessor constants for display hardware bitfields, not executable driver logic. Each `REGISTER__FIELD__SHIFT` macro gives a field bit position and each `REGISTER__FIELD_MASK` macro gives the already-positioned mask used by AMD display register helpers.

The requested range contains 2,218 `#define` lines: 1,108 shift macros and 1,110 mask macros. The imbalance is caused by chunk boundaries. The first two lines are only the trailing masks for `HUBP1_DCSURF_ADDR_CONFIG` fields whose shifts appear in the previous chunk, and the range ends immediately after `CURSOR0_3_DMDATA_ADDRESS_HIGH` before `CURSOR0_3_DMDATA_ADDRESS_LOW` and the remaining DMDATA control/status fields continue in the next chunk.

The substantive hardware surface covered here is the DCN 3.5 HUBP pipeline register layout for instances 1 through 3, including surface tiling, viewport geometry, memory request sizing, VM/QoS timing, flip control, HUBPREQ request-side state, HUBPRET return-side state, cursor programming, DMDATA programming for cursor instances 1 and 2, and the start of cursor/DMDATA instance 3.

## Important Constants And Register Areas

`HUBP1_*`, `HUBP2_*`, and `HUBP3_*` define the hub pipe front-end fields used to fetch and present plane data:

- `DCSURF_ADDR_CONFIG` and `DCSURF_TILING_CONFIG` describe memory layout: pipe count, pipe interleave, compressed fragment limits, packetizer count, swizzle mode, dimension type, metadata linearity, and pipe alignment. The requested range only has the final two masks for `HUBP1_DCSURF_ADDR_CONFIG`; `HUBP2` and `HUBP3` include the complete address-config field set.
- `DCSURF_PRI_VIEWPORT_*` and `DCSURF_SEC_VIEWPORT_*`, plus `_C` chroma variants, pack X/Y starts and width/height values in 14-bit halves. These fields establish luma/chroma primary and secondary viewport windows.
- `DCHUBP_REQ_SIZE_CONFIG` and `_C` define swath height, PTE row height, chunk size, meta chunk size, DPTE group size, and VM group size. These fields feed request sizing and address-translation behavior for luma and chroma fetches.
- `DCHUBP_CNTL` contains blank/reset/status/control bits such as `HUBP_BLANK_EN`, no-outstanding-request indicators, soft reset, VTG select, unbounded request mode, TTU disable/mode, timeout status/threshold/interrupt enable, and underflow status/clear bits.
- `HUBP_CLK_CNTL`, `DCHUBP_VMPG_CONFIG`, and `HUBP_MEASURE_WIN_CTRL_DCFCLK/DPPCLK` describe clock enable/gating status, virtual memory page size, and performance measurement windows.

`HUBPREQ1_*`, `HUBPREQ2_*`, and `HUBPREQ3_*` define request-side surface and timing fields:

- Surface pitch, VMID, primary/secondary surface addresses, primary/secondary metadata addresses, and high address halves for luma and chroma.
- Surface control, surface in-use and earliest-in-use tracking, flip interrupt masking/clear/status fields, and flip control fields such as immediate flip, horizontal timing, flip pending/armed status, page-queue and earliest-in-use toggles, and memory format checks.
- TTU/QoS and delivery timing fields: `DCN_GLOBAL_TTU_CNTL`, `DCN_SURF*_TTU_CNTL*`, `DCN_CUR*_TTU_CNTL*`, `DCN_TTU_QOS_WM`, `PREFETCH_SETTINGS`, `PER_LINE_DELIVERY`, nominal/vblank/flip parameters, destination dimensions, blank offsets, and reference-cycle-to-pixel-frequency conversion.
- VM control fields for system aperture low/high addresses, L1 TLB control, and DMDATA VM timing/status/clear fields.
- Request memory power control/status for DPTE, MPTE, metadata, and PDE memories.

`HUBPRET1_*`, `HUBPRET2_*`, and `HUBPRET3_*` define return-side and cursor-return state:

- `HUBPRET_CONTROL` maps DET buffer base address, 3-to-2 packing disable, and crossbar source selection for alpha, Y/G, Cb/B, and Cr/R.
- `HUBPRET_MEM_PWR_CTRL` and `_STATUS` control and report DMROB and PIXCDC memory power state.
- `HUBPRET_READ_LINE_CTRL*`, `READ_LINE0`, `READ_LINE1`, `INTERRUPT`, `READ_LINE_VALUE`, and `READ_LINE_STATUS` define vblank/read-line window programming, interrupt mask/type/clear/status bits, current read line snapshots, and inside/outside window status.

`CURSOR0_1_*` and `CURSOR0_2_*` are complete in this range, while `CURSOR0_3_*` is partial. The complete cursor instances include cursor enable/request mode/magnification/mode/TMZ/pitch/line-per-chunk/perfmon fields, cursor surface address, size, position, hotspot, stereo offsets, destination X offset, cursor ROB memory power fields, and DMDATA address/control/QoS/status/software-control/data fields. The partial instance 3 coverage includes cursor control through `DMDATA_ADDRESS_HIGH`.

## APIs, Types, And Functions

There are no functions, structs, enums, or inline helpers in this chunk. The API surface is the generated macro namespace consumed by higher-level register tables.

The constants pair with `dcn_3_5_0_offset.h`, which supplies matching `reg...` addresses such as `regHUBP1_DCSURF_ADDR_CONFIG` and `regCURSOR0_3_DMDATA_STATUS`. They are then lifted into typed shift/mask structures through display block macros. In the DCN35 HUBP layer, `HUBP_MASK_SH_LIST_DCN35(mask_sh)` extends the DCN32 HUBP field list and is instantiated by DCN35/351/36 resource code as both `__SHIFT` and `_MASK` lists. Runtime code uses register helper APIs such as `REG_SET`, `REG_UPDATE`, `REG_UPDATE_N`, `REG_GET`, `REG_READ`, `REG_WRITE`, and `REG_WAIT` with these generated field definitions.

## Control Flow And Runtime Behavior

This header has no local control flow. Runtime behavior occurs when the display driver uses the fields to program memory-mapped DCN hardware.

The implied HUBP surface programming flow is: configure tiling/address layout from framebuffer tiling metadata, set viewport and pitch for luma/chroma planes, program VMID and surface/meta addresses, set request sizing and TTU/QoS timing from DML/DLG calculations, arm flips through `DCSURF_FLIP_CONTROL*`, and observe or clear flip/underflow/timeout status bits. Surface update locking and vblank timing matter because many of these fields are consumed by active scanout hardware.

The implied HUBPRET flow is return-path setup and monitoring: select DET buffer base and color component crossbar mapping, configure read-line/vblank interrupt windows, and sample read-line status for synchronization or diagnostics. Interrupt-related masks and clear/status fields integrate with the DC IRQ service's page-flip and vline/vblank paths.

The implied cursor/DMDATA flow is: program cursor address, size, position, hotspot, format/mode, memory power state, and optional display metadata delivery. For hardware DMDATA mode, the HUBP code toggles `DMDATA_UPDATED`, sets repeat and size, programs low/high address fields, and configures QoS. For software DMDATA mode, it toggles software update fields and writes `DMDATA_SW_DATA`.

## State And Persistence

The file stores no mutable state. It defines how software addresses persistent hardware state in per-pipe HUBP, HUBPREQ, HUBPRET, cursor, and DMDATA registers.

Hardware state represented here persists until reset, modeset reprogramming, plane update, cursor update, DMDATA update, power transition, or suspend/resume restore. Important state includes surface base and metadata addresses, pitch, viewport geometry, tiling mode, VMID, VM aperture/TLB settings, timing and QoS watermarks, flip pending/armed/status bits, read-line interrupt windows, cursor image attributes, DMDATA address/control/QoS settings, and memory power states for HUBPREQ/HUBPRET/cursor memories.

Several fields are status or clear-on-write style controls rather than simple configuration. Examples include underflow clear, timeout status clear, flip interrupt clear, VM fault/underflow status clear, read-line interrupt clear, and DMDATA underflow clear in the complete cursor instances. Callers must preserve write semantics through the central register helpers instead of treating all masks as ordinary persistent configuration bits.

## Dependencies And Integration Points

This generated header must match the DCN 3.5.0 register offset header and the hardware register database used to generate both files. The masks are not independently portable to other ASIC generations unless the register database and block-specific field lists show compatible layouts.

Key integration points include:

- `drivers/gpu/drm/amd/display/dc/resource/dcn35/dcn35_resource.c`, which includes `dcn_3_5_0_offset.h` and this shift/mask header when constructing DCN35 resources.
- `drivers/gpu/drm/amd/display/dc/hubp/dcn35/dcn35_hubp.h`, where `HUBP_MASK_SH_LIST_DCN35` feeds DCN35 HUBP shift and mask structures.
- `drivers/gpu/drm/amd/display/dc/irq/dcn35/irq_service_dcn35.c`, which includes the same generated headers for DCN35 interrupt programming, including page-flip sources backed by `DCSURF_SURFACE_FLIP_INTERRUPT`.
- `drivers/gpu/drm/amd/display/dmub/src/dmub_dcn35.c`, which includes this header for DMUB/DCN35 register interaction.
- Generic HUBP, DPP, IRQ, DML/DLG, cursor, and DMDATA paths that use the field names through register helper macros rather than directly referencing instance-specific `HUBP1_`, `HUBPREQ2_`, or `CURSOR0_3_` tokens.

## Risks And Edge Cases

Generated-header drift is the primary risk. Incorrect masks or shifts compile normally but can route writes into adjacent fields, causing wrong tiling, bad scanout addresses, broken flips, cursor corruption, DMDATA failures, false interrupts, or unsafe memory power transitions.

Chunk boundaries are locally incomplete. The opening `HUBP1_DCSURF_ADDR_CONFIG` field group lacks its shift lines in this slice, and `CURSOR0_3_DMDATA_ADDRESS_HIGH` is the last complete register in the requested range. Any whole-file reconciliation must merge neighboring chunks before claiming complete coverage of those boundary register groups.

Repeated-instance consistency is important. HUBP/HUBPREQ/HUBPRET and cursor instances are mechanically parallel, but one wrong instance-specific token or numeric value can produce failures only on a particular pipe. Multi-pipe, multi-monitor, and cursor-on-nonzero-pipe paths are therefore valuable validation targets.

Several fields have sequencing or side-effect hazards. Flip control and flip interrupt fields must be synchronized with surface update locks and vertical timing. Memory power force/disable/status fields must not be changed while dependent request, return, cursor, or metadata memories are actively needed. Clear bits should be written according to established IRQ/status handling paths to avoid losing real fault evidence.

The constants use 32-bit masks with `L` suffixes, including high-bit masks such as `0x80000000L` and `0xFFFF0000L`. Consumers should rely on existing unsigned register helper paths and avoid open-coded signed arithmetic.

## Test And Validation Signals

Compile-time validation should build all DCN35 display users that include this header, especially resource initialization, HUBP construction, IRQ service code, and DMUB DCN35 code. Missing or renamed macros are usually caught at compile time through the generated register field lists.

Generated-data checks should compare this chunk against the authoritative DCN 3.5.0 register database, verify that complete registers have non-overlapping masks matching their shifts, and diff repeated instances (`HUBP1/2/3`, `HUBPREQ1/2/3`, `HUBPRET1/2/3`, `CURSOR0_1/2`) while accounting for intentional boundary incompleteness.

Runtime signals include successful modesets and page flips on DCN35 hardware, correct scanout of tiled and linear buffers, stable chroma/luma viewport programming, no HUBP underflow or VM fault status under normal bandwidth conditions, correct vblank/read-line/page-flip interrupt delivery and clearing, cursor correctness on multiple pipes, DMDATA hardware/software update completion, and clean suspend/resume or runtime power-management transitions.

## Research Notes

This is chunk-level research only for `subset-b-002062`. It intentionally writes only `Docs/researches/chunks/subset-b-002062_research.md`; final per-file synthesis for `dcn_3_5_0_sh_mask.h` must be produced later by the merge/reconciliation lane after adjacent chunks are available.
