# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_4_1_0_sh_mask.h lines 7557-10071

## Scope

This chunk is part of AMD DCN 4.1.0 generated ASIC register metadata. It contains C preprocessor definitions for register-field bit shifts and masks, not executable driver logic. The covered range starts in the tail of the `HUBPREQ0` register field list, covers the `HUBPRET0` and `CURSOR0_0` blocks, covers complete replicated HUBP/HUBPREQ/HUBPRET/CURSOR register-field blocks for pipe instances 1 and 2, and ends partway through the `HUBP3_DCHUBP_CNTL` field list.

The chunk contains 2113 `#define` lines: 1061 shift definitions, 1052 mask definitions, and 361 distinct register-name groups. It is organized by generated register comments and `addressBlock` comments such as `dcn_dcec_dcbubp1_dispdec_hubp_dispdec`, `dcn_dcec_dcbubp1_dispdec_hubpreq_dispdec`, `dcn_dcec_dcbubp1_dispdec_hubpret_dispdec`, and `dcn_dcec_dcbubp1_dispdec_cursor0_dispdec`.

## Purpose

The purpose of this chunk is to encode the DCN 4.1 hardware bit layout for display hub pipe programming. These definitions let the AMD display driver compose and decode MMIO register fields for:

- HUBPREQ timing, QoS, VM, address, flip, prefetch, cursor-request, status, and memory power fields.
- HUBPRET return-path control, DET base/crossbar selection, read-line tracking, interrupt status/clear/mask fields, and memory power state.
- CURSOR blocks for cursor image address, size, position, hot spot, stereo, memory power, DMData, software DMData, and HUBP 3DLUT fetch fields.
- HUBP surface format, tiling, viewport, request sizing, blank/reset/underflow/status control, clock control, virtual memory page configuration, MALL/mcache configuration, measure windows, and MALL status fields for replicated pipes.

Correctness here is a hardware contract. Higher-level DCN401 code names logical fields such as `HUBP_BLANK_EN`, `SURFACE_FLIP_PENDING`, `DMDATA_VM_FAULT_STATUS_CLEAR`, or `HUBP_3DLUT_WIDTH`; this header supplies the exact bit positions and masks that make those names target the intended hardware bits.

## Important APIs, Types, And Macros

There are no C functions, structs, or enums declared in this chunk. The exported interface is the generated symbol convention:

- `<REGISTER>__<FIELD>__SHIFT` gives the least-significant bit position of a hardware field.
- `<REGISTER>__<FIELD>_MASK` gives the 32-bit MMIO mask for that field.
- Register comments such as `//HUBPREQ1_DCSURF_FLIP_CONTROL` group the shift/mask pairs by physical register.
- `addressBlock` comments mark replicated hardware blocks for each hub pipe instance.

Important register families in this range include:

- `HUBPREQ0_*`, continuing from `DCN_CUR1_TTU_CNTL0` through status registers. These include DMData VM timing/fault bits, VM aperture and L1 TLB control, blank/prefetch/vblank/flip/nominal DLG parameters, per-line delivery, cursor request settings, request memory power, UCLK pstate force, and detailed request pipeline status.
- `HUBPRET0_*`, including `HUBPRET_CONTROL`, memory power control/status, read-line controls, read-line values, and interrupt state.
- `CURSOR0_0_*`, including cursor control/address/size/position/hot spot/stereo/memory power plus DMData and HUBP 3DLUT fetch fields.
- `HUBP1_*` and `HUBP2_*`, which describe per-pipe surface configuration, address configuration, tiling, primary/secondary viewport coordinates, request-size controls, HUBP control/status fields, clock controls, VMPG, MALL, MCACHEID, measurement windows, and MALL status.
- `HUBPREQ1_*` and `HUBPREQ2_*`, which replicate the HUBPREQ surface-address, flip, VM, timing, QoS, memory power, pstate, and status register layouts for pipe instances 1 and 2.
- `HUBPRET1_*`, `HUBPRET2_*`, `CURSOR0_1_*`, and `CURSOR0_2_*`, which replicate return-path and cursor/DMData/3DLUT field layouts for pipe instances 1 and 2.
- `HUBP3_*`, starting the pipe instance 3 HUBP block through the `HUBP3_DCHUBP_CNTL` fields at the chunk boundary.

The direct consumers in this tree are DCN401 register-list and field-list macros. `display/dc/resource/dcn401/dcn401_resource.c` includes `dcn/dcn_4_1_0_offset.h` and this `dcn/dcn_4_1_0_sh_mask.h`, then builds `hubp_regs`, `hubp_shift`, and `hubp_mask` using `HUBP_REG_LIST_DCN401_RI(id)` and `HUBP_MASK_SH_LIST_DCN401(...)`. `display/dc/resource/dcn401/dcn401_resource.h` maps register instances with `SRI_ARR(...)`, while `display/dc/hubp/dcn401/dcn401_hubp.h` maps field names with `HUBP_SF(...)`.

## Control Flow

This chunk has no runtime control flow. It affects driver control flow indirectly through register accessor expansion:

- DCN401 resource construction initializes per-instance HUBP register tables for instances 0-3. `dcn401_hubp_create()` calls `hubp_regs_init(0)`, `hubp_regs_init(1)`, `hubp_regs_init(2)`, and `hubp_regs_init(3)`, then passes the selected register table plus shared shift/mask tables into `hubp401_construct()`.
- HUBP programming paths call `REG_UPDATE`, `REG_UPDATE_2`, `REG_UPDATE_3`, `REG_WRITE`, `REG_GET`, and `REG_WAIT`. Those macros use the register offsets from `dcn_4_1_0_offset.h` and the shift/mask symbols from this header to isolate or compose MMIO field values.
- Surface programming, flip programming, VM setup, cursor programming, DMData programming, MALL programming, and 3DLUT programming are implemented in hubp code using logical field names. For example, `hubp401_program_3dlut_fl_addr()` writes `HUBP_3DLUT_ADDRESS_HIGH` and `HUBP_3DLUT_ADDRESS_LOW`; `hubp401_program_3dlut_fl_config()` updates `HUBP_3DLUT_WIDTH`, `HUBP_3DLUT_ADDRESSING_MODE`, and `HUBP_3DLUT_TMZ`; `hubp401_update_mall_sel()` updates `USE_MALL_SEL`, `USE_MALL_FOR_CURSOR`, `MALL_PREF_CMD_TYPE`, and `MALL_PREF_MODE`.
- Older inherited HUBP code paths still consume many of these fields through the DCN401 tables, including underflow clear/readback, blanking, request sizing, viewport, surface addresses, flip state, cursor, DMData, MALL, and read-line status.

The effective runtime path is: DCN401 resource setup chooses the DCN 4.1.0 generated offset and shift/mask headers; resource constructors bind these generated tables to HUBP objects; display update paths issue logical register-field operations; the generated masks and shifts in this chunk decide which hardware bits are read or written.

## State And Persistence Behavior

The header itself persists no software state. It describes persistent and sticky hardware state in several display-hub domains:

- Programmed plane state persists in surface format, tiling, viewport, surface pitch, primary/secondary luma/chroma addresses, DCC/TMZ enable bits, VMID, aperture bounds, request sizing, and timing/prefetch/DLG parameters until the driver updates them or the hardware block resets.
- Flip state includes pending/armed/occurred bits, flip mode, triple-buffer/GSL controls, master update lock status, in-use address captures, and earliest-in-use captures. These fields are used to sequence page flips and diagnose which surface address is currently fetched.
- VM and fault state includes L1 TLB enable/system access controls, DMData VM fault status, underflow/late status, done status, and write-to-clear fields. These fields can be sticky and must be cleared with exact masks.
- Power and clock state includes HUBPREQ/HUBPRET/CURSOR memory power force/disable/status fields, HUBP clock enable and gate-disable/status bits, VMPG controls, MALL controls, MCACHEID mapping, and UCLK pstate force. These values influence low-power behavior and display fetch availability.
- Status fields include HUBP no-outstanding-request, in-blank, timeout, underflow, request pipeline status registers, read-line counters/status, return-path interrupts, cursor DMData done/underflow, HUBP 3DLUT done, and MALL status. Many are diagnostic or synchronization points rather than normal control settings.

Because these are hardware register fields, persistence is governed by hardware reset, power gating, display pipe disable, and explicit writes from driver paths. A wrong mask can leave stale state active across modesets, fail to clear a sticky fault, or corrupt adjacent fields during a read-modify-write operation.

## Dependencies And Integration Points

Primary dependencies:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_4_1_0_offset.h` supplies the register offsets paired with these field masks and shifts.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn401/dcn401_resource.c` includes this header and instantiates `hubp_shift` and `hubp_mask` with `HUBP_MASK_SH_LIST_DCN401(__SHIFT)` and `HUBP_MASK_SH_LIST_DCN401(_MASK)`.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn401/dcn401_resource.h` provides `HUBP_REG_LIST_DCN401_RI(id)`, which maps the replicated physical register instances such as `HUBPREQ1_*`, `HUBPRET1_*`, and `CURSOR0_1_*` into the generic HUBP register structure.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hubp/dcn401/dcn401_hubp.h` provides `HUBP_MASK_SH_LIST_DCN401(mask_sh)`, which lists many fields present in this chunk and maps generated symbols into the generic `dcn_hubp2_shift` and `dcn_hubp2_mask` structures.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hubp/dcn401/dcn401_hubp.c` uses the resulting tables for 3DLUT fetch programming and MALL selection. It also inherits much of the broader HUBP behavior from DCN20/DCN21/DCN30/DCN31/DCN32 code included by `dcn401_hubp.h`.

Important integration behavior:

- The shift/mask table is instance-agnostic in the C structure: macros typically use the instance 0 field names, while the register table picks the per-instance offset. This chunk still must define replicated instance 1 and 2 symbols because `HUBP_REG_LIST_DCN401_RI(id)` initializes register offsets for each physical pipe.
- The chunk boundary is not a semantic subsystem boundary. It starts after earlier `HUBPREQ0` fields and ends inside `HUBP3_DCHUBP_CNTL`, so final file-level analysis must reconcile this with adjacent chunks before making conclusions about complete pipe 0 or pipe 3 coverage.
- DMUB, IRQ, GPIO, and clock-manager DCN401 files also include the same generated header for their own register domains. This chunk is specifically relevant to HUBP/HUBPREQ/HUBPRET/CURSOR definitions, but the header as a whole is shared across DCN401 display subsystems.

## Risks

- Generated-header drift is high impact. A shift or mask can be wrong while the code still compiles, causing valid `REG_UPDATE` calls to modify the wrong hardware bits.
- Replicated pipe symmetry is easy to break. Pipe instances 0, 1, 2, and 3 must keep compatible layouts where hardware expects replicated HUBP/HUBPREQ/HUBPRET/CURSOR blocks. This chunk covers full instances 1 and 2 but only partial instances 0 and 3, so merge-lane analysis should check adjacent chunks for continuity.
- Read-modify-write hazards are significant. Wrong masks for fields such as `HUBP_UNDERFLOW_CLEAR`, `HUBP_TIMEOUT_STATUS_CLEAR`, `DMDATA_VM_FAULT_STATUS_CLEAR`, `DMDATA_VM_UNDERFLOW_STATUS_CLEAR`, `SURFACE_FLIP_CLEAR`, and interrupt clear fields can fail to clear sticky status or clear neighboring diagnostics.
- Address fields span high/low registers and luma/chroma primary/secondary variants. Incorrect field widths in surface, cursor, DMData, or 3DLUT address registers can truncate DMA addresses, fetch from the wrong memory, or mis-handle TMZ protected surfaces.
- Timing and QoS fields are tightly coupled to display bandwidth calculations. Bad masks in TTU, prefetch, vblank, flip, nominal, per-line delivery, and UCLK pstate force fields can create underruns or intermittent blanking that only appears under high-resolution, cursor, chroma, MALL, or low-power workloads.
- MALL, VMPG, MCACHEID, and request-size fields couple hardware caching and VM behavior. Incorrect field definitions can produce cache allocation errors, stale fetches, or failures in sub-viewport/MALL modes.
- 3DLUT fetch fields add a DCN401-specific path using cursor-adjacent HUBP 3DLUT registers. Mask errors in width, addressing mode, TMZ, crossbar selection, address, or done status can break color pipeline DMA without affecting simpler display paths.

## Test Signals

Useful validation signals for this chunk or its generator include:

- Build coverage for DCN401 display code. Missing or renamed symbols should fail in `HUBP_MASK_SH_LIST_DCN401`, `HUBP_REG_LIST_DCN401_RI`, or register table initialization.
- Mechanical comparison against trusted AMD-generated DCN 4.1.0 register XML/header output. For generated shift/mask files, exact diffing against the authoritative source is the strongest baseline.
- Display bring-up and modeset smoke tests on DCN401 hardware with all four HUBP instances available, confirming that resource construction, HUBP creation, blank/unblank, and timing generator association work.
- Plane tests covering luma/chroma formats, DCC enabled and disabled, TMZ and non-TMZ surfaces, rotation/mirror/alpha flags, primary and secondary viewports, pitch changes, and page flips. These exercise `HUBP*_DCSURF_*` and `HUBPREQ*_DCSURF_*` fields.
- Flip sequencing tests covering immediate flips, pending flips, triple buffering, GSL/stereo synchronization, in-use address readback, flip interrupt mask/clear/status, and master update lock status.
- Cursor and DMData tests covering cursor enable/move/resize, stereo cursor fields, cursor memory power, DMData address/control/QoS/status, software DMData, VM fault/underflow/late clear behavior, and cursor-request timing fields.
- MALL and low-power tests covering MALL cache selection, cursor-in-MALL, VMPG configuration, MCACHEID programming, memory power force/status, HUBP clock gating, UCLK pstate forcing, idle/blank transitions, suspend/resume, and underflow monitoring.
- 3DLUT fetch tests covering 17x17x17 and 33x33x33 LUTs, 1D packed transform mode, RGBA/BGRA crossbar choices, address high/low programming, TMZ surfaces, done status, and visible color output.
- VM and fault-injection tests with invalid or unmapped surface/cursor/DMData/3DLUT addresses, aperture boundary checks, VMID changes, and fault status clear/readback.
- Read-line and interrupt diagnostics for HUBPRET, validating `PIPE_READ_LINE`, read-line min/max modes, read-line status, vblank/reference compare interrupts, urgency interrupts, and clear/mask behavior.

## Notes For Merge Lane

This chunk should be merged with adjacent `dcn_4_1_0_sh_mask.h` chunks before producing a final per-file document. The start boundary is inside the `HUBPREQ0` block, and the end boundary is inside `HUBP3_DCHUBP_CNTL`. Whole-file conclusions should account for the earlier HUBP0/HUBPREQ0 definitions and the later completion of HUBP3 plus any following HUBPREQ3/HUBPRET3/CURSOR0_3 blocks.
