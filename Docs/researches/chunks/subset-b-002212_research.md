# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_4_2_0_offset.h lines 2954-5582

## Scope And Purpose

This chunk is a generated AMD DCN 4.2.0 register-offset map for part of the display controller address space. It is not executable code; it provides C preprocessor constants used by AMDGPU display code to translate symbolic register names into MMIO offsets. The matching `dcn_4_2_0_sh_mask.h` header supplies field shifts and masks, while this file supplies register addresses and per-register base-index selectors.

The requested span starts mid-list with 15 `ixAZALIA_F2_CODEC_INPUT_*` indirect-codec definitions, then covers 65 complete `addressBlock` sections. Those sections describe display performance monitors, display microcontroller and power-gating registers, interrupt/status registers, DMCUB firmware interface registers, display writeback and MMHUBBUB registers, HDA/Azalia audio stream and endpoint registers, DCHUBBUB arbitration/VM registers, and HUBP/HUBPREQ/HUBPRET/CURSOR register sets for HUBP instances 0, 1, and the beginning of instance 2.

The chunk contains 2,369 `#define` lines: 1,192 value macros and 1,177 `_BASE_IDX` macros. Most names use the `reg*` prefix and are consumed through normal display MMIO register tables. The opening 15 `ix*` names are indirect-indexed Azalia codec/performance/debug style registers and do not carry `_BASE_IDX` companions.

## Register Families Covered

The major address-block groups in this span are:

- `dce_dc_dccg_dccg_dcperfmon{0,1}_dc_perfmon_dispdec`: `DC_PERFMON0_*` and `DC_PERFMON1_*` control/state/counter registers.
- `dce_dc_dmu_dc_pg_dispdec`: display power-gating domain configuration/status registers, `DCPG_INTERRUPT_*`, `DC_IP_REQUEST_CNTL`, and `LONO_MEM_PWR_REQ_CNTL`.
- `dce_dc_dmu_*`: DMU misc, IHC interrupt/status, FGSEC, RBBMIF, and a large `dce_dc_dmu_dmcub_dispdec` block for DMCUB control, scratch, inbox/outbox, region, timer, interrupt, debug, and fault registers.
- `dce_dc_mmhubbub_*`: MCIF writeback, MMHUBBUB VM/aperture, memory power, and MMHUBBUB perfmon registers.
- `dce_dc_hda_*`: HDA/Azalia stream, endpoint, controller, root, misc, perfmon, and input endpoint register windows.
- `dce_dc_dchubbubl_*`: HUBBUB SDPIF, return path, global DCHUBBUB arbitration/watermark/self-refresh/clock/power/compression-buffer/VM/FAMS registers, DCHUBBUB perfmon, and VMRQ interface registers.
- `dce_dc_dcbubp{0,1,2}_*`: HUBP, HUBPREQ, HUBPRET, cursor, and per-HUBP perfmon register windows. The chunk includes full register sets for instances 0 and 1 and continues through HUBPREQ2 status registers at line 5582.

Repeated instances are encoded by baking the hardware instance number into the macro name. For example, `regHUBPREQ0_DCSURF_PRIMARY_SURFACE_ADDRESS`, `regHUBPREQ1_DCSURF_PRIMARY_SURFACE_ADDRESS`, and `regHUBPREQ2_DCSURF_PRIMARY_SURFACE_ADDRESS` have separate offset constants, and each has a matching `_BASE_IDX` macro selecting the DCN segment base.

## Important APIs, Types, And Macros

This header exports macros only. There are no C functions, structs, enums, or storage definitions in the chunk.

The important macro forms are:

- `reg<NAME>`: a register offset within a DCN base segment. Example families include `regDMCUB_CNTL`, `regDCHUBBUB_ARB_DATA_URGENCY_WATERMARK_A`, `regHUBP0_DCHUBP_CNTL`, and `regHUBPREQ0_DCSURF_PRIMARY_SURFACE_ADDRESS`.
- `reg<NAME>_BASE_IDX`: the segment selector used by register-table initialization. In this span almost all regular DCN registers use base index `2`, while the generated form still preserves the selector for code that computes `BASE(reg..._BASE_IDX) + reg...`.
- `ix<NAME>`: indirect-index constants. In this span these are Azalia F2 codec input converter/pin parameter and control indexes, continuing a list that begins before line 2954.
- `addressBlock` comments and `base address` comments: generated metadata documenting the hardware block and instance spacing. Consumers do not parse these comments at runtime, but they are important review signals when validating offsets against ASIC register specifications.

The register families in this chunk are later projected into typed register-table structs in display code. For example, DCN42 resource code defines helpers such as `SR`, `SRI`, `SRI_ARR`, and related macros that expand a symbolic register name into `BASE(reg..._BASE_IDX) + reg...`. DMUB code similarly uses `REG_OFFSET_EXP(reg_name)` to initialize `dmub_srv_dcn42_regs` offsets from this header.

## Control Flow And Runtime Use

There is no local control flow in the header. Runtime control flow appears in consumers:

1. DCN42-specific modules include `dcn/dcn_4_2_0_offset.h` and `dcn/dcn_4_2_0_sh_mask.h`.
2. During construction/init, modules build register tables by combining the segment base selected by `_BASE_IDX` with the offset value from the `reg*` macro.
3. Generic display register helpers such as `REG_READ`, `REG_WRITE`, `REG_SET`, `REG_UPDATE`, and `REG_GET` use those tables plus the shift/mask tables to perform MMIO reads and writes.
4. Higher-level display code programs the hardware: DMCUB boot/reset/mailbox setup, HUBBUB watermarks and VM configuration, HUBP surface address/pitch/format/deadline programming, cursor and 3D LUT DMA state, flip handling, power gating, audio stream state, and performance monitoring.

Concrete integration examples from nearby code:

- `display/dmub/src/dmub_dcn42.c` includes this header and initializes `dmub->regs_dcn42` with `REG_OFFSET_EXP`. The DMCUB block in this chunk backs reset, boot options, scratch registers, inbox/outbox pointers, region windows, GPINT, timer, and fault/debug reads.
- `display/dc/resource/dcn42/dcn42_resource.c` includes this header and defines the `BASE`, `SR`, `SRI`, and array helpers used by DCN42 resource construction to fill per-block register structs.
- `display/dc/hubp/dcn42/dcn42_hubp.c` operates on HUBP/HUBPREQ/HUBPRET names represented in this chunk. It programs surface formats, DLG/TTU deadline registers, requestor behavior, cursor-related state, fine-grain clock gating, and 3D LUT DMA-related registers.
- `display/dc/hubbub/dcn42/dcn42_hubbub.c` operates on DCHUBBUB registers from this span to program urgent/stutter watermarks, arbitration timing, self-refresh, VM/aperture, and memory-power behavior.
- `display/dc/irq/dcn42/irq_service_dcn42.c` includes the same offset and mask headers for DCN42 interrupt-service mappings, including vblank/vupdate/flip/HPD/DMCUB outbox sources.

## State And Persistence Behavior

The header itself has no mutable state and persists nothing. Its values become part of the compiled driver image and define the MMIO contract for DCN 4.2 hardware.

At runtime, the register names in this chunk control persistent hardware state for the lifetime of the GPU/display session:

- DMCUB scratch, boot-option, inbox/outbox, region-window, reset, interrupt, and timer registers hold firmware communication state and boot/debug state until reset or power loss.
- HUBBUB and HUBPREQ registers hold display memory-fetch programming: surface addresses, metadata addresses, VMID settings, VM aperture bounds, TLB control, TTU/DLG timing, watermarks, arbitration, self-refresh, MALL, clock gating, and memory power state.
- HUBP/HUBPRET/CURSOR registers hold per-pipe presentation state such as pixel format, surface configuration, cursor position/address/control, detile/decompression behavior, 3D LUT DMA configuration, and per-pipe perfmon state.
- HDA/Azalia stream and endpoint registers hold display-audio stream descriptors, link position/status, endpoint configuration, converter/pin state, and controller/root capabilities.
- Perfmon blocks hold counter selection, state, and counter values. These are volatile but user/debug-visible through driver diagnostics or perf tooling.

Because these constants address live MMIO, a wrong offset is not a local logic bug. It can redirect a read or write to another hardware register, causing hangs, display corruption, missed interrupts, incorrect audio behavior, firmware boot failure, or incorrect power-management state.

## Dependencies And Integration Points

This chunk depends on the generated DCN 4.2 ASIC register specification and on the broader AMD display register framework. Important dependencies are:

- `dcn_4_2_0_sh_mask.h`, which must define field masks and shifts for the same symbolic register names.
- DCN base-address setup, exposed in consumers through `ctx->dcn_reg_offsets[...]` or fixed segment base macros. `_BASE_IDX` values are meaningful only with the correct base table for the ASIC instance.
- `reg_helper.h` and display register helper macros, which combine register offsets with shifts/masks for read-modify-write access.
- DCN42 block constructors and register-list macros in HUBP, HUBBUB, MMHUBBUB, DCCG, clock manager, GPIO, IRQ, DIO, resource, and DMUB code.
- Hardware firmware contracts for DMCUB mailbox/scratch/region registers and audio contracts for HDA/Azalia stream/endpoint registers.
- Linux DRM/AMDGPU display initialization and atomic commit paths, which indirectly rely on these constants when programming planes, flips, watermarks, interrupts, clocks, and link/audio state.

The repeated instance spacing is an important integration signal. In this chunk, HDA stream blocks are spaced by `0x8` for streams 0-7 and again at higher offsets for streams 8-15; HDA endpoints are spaced by `0x18`; HDA input endpoints are spaced by `0x10`; HUBP/HUBPREQ/HUBPRET/CURSOR instances are spaced by `0x370` for instances 0, 1, and 2. If a consumer uses array helpers with the wrong instance name or index, the generated offset still compiles but targets the wrong hardware pipe.

## Risks And Edge Cases

- The requested range starts in the middle of an indirect Azalia block and ends in the middle of the HUBPREQ2 block. This chunk is not a standalone semantic unit for the whole header; adjacent chunks are needed for the beginning/end of those generated lists.
- The file is generated hardware data. Manual edits are high risk because register names and offsets must match the ASIC specification and the sibling mask/shift header exactly.
- `_BASE_IDX` values are as important as the offset values. A correct offset with a wrong base index computes a wrong absolute MMIO address.
- Register families with repeated instances are easy to miswire. HUBP0/HUBPREQ0/HUBPRET0/CURSOR0 and HUBP1/HUBPREQ1/HUBPRET1/CURSOR0 share repeated field names but differ in macro prefixes and offsets.
- Several registers represent paired low/high addresses, such as DMCUB region offsets, DCSURF primary/secondary surface addresses, metadata surface addresses, and VM aperture bounds. Missing one half or swapping high/low names breaks 64-bit addressing.
- DMCUB reset and mailbox registers are tightly ordered by firmware protocols. Incorrect offsets can make firmware stop/reset handshakes time out or make GPINT/inbox/outbox state appear corrupt.
- HUBBUB/HUBPREQ timing registers come from DML calculations. A wrong mapping can compile cleanly but produce underruns, flicker, failed flips, or memory-clock/pstate behavior that only appears under bandwidth stress.
- Some register macros in consumers are optional-gated by checking whether a register-table field is nonzero. A generated zero offset may be valid for a register at block base, so optional checks must be interpreted in the context of the surrounding inherited register tables.
- The opening `ixAZALIA_*` constants do not have `_BASE_IDX` companions because they are indirect indexes, not the normal DCN segment-offset form. Treating them like `reg*` macros would be incorrect.

## Test Signals

Useful validation for this chunk is mostly compile-time, register-table, and hardware/driver integration oriented:

- Build the AMDGPU display code with DCN42 enabled and ensure all symbolic names referenced by DCN42 consumers resolve against `dcn_4_2_0_offset.h` and `dcn_4_2_0_sh_mask.h`.
- Add or run static checks that every `reg*` macro used in DCN42 register-list macros has a matching `_BASE_IDX` macro and matching shift/mask fields where field operations are used.
- Compare generated offsets and base indexes against the authoritative DCN 4.2 ASIC register database, especially DMCUB, DCHUBBUB, HUBP/HUBPREQ instance spacing, and HDA stream/endpoint spacing.
- Exercise DMCUB reset/release and mailbox paths and watch for timeout, scratch-register, GPINT, inbox/outbox, and firmware-version diagnostics.
- Run display atomic modeset/flip tests across multiple pipes to cover `HUBPREQ0`, `HUBPREQ1`, and `HUBPREQ2` surface-address, flip, DLG/TTU, cursor, and perfmon mappings.
- Stress memory bandwidth, self-refresh, MALL, and UCLK pstate transitions to validate DCHUBBUB and HUBPREQ watermark/arbiter register addressing.
- Exercise display audio over HDMI/DP to validate Azalia stream/endpoint/controller/root register mappings and codec input pin/converter indirect indexes.
- Verify interrupt delivery for vblank, vupdate, page flip, HPD/HPDRX, and DMCUB outbox sources on DCN42 hardware.
- Use debug/perf tooling to read DC_PERFMON, MMHUBBUB, HDA, DCHUBBUB, and HUBP perfmon counters and confirm counters increment for the expected block, not a neighboring instance.
