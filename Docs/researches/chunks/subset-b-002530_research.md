# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_11_0_3_sh_mask.h lines 9880-12211

## Scope

This chunk is a large middle segment of the generated AMD GC 11.0.3 shift/mask header. It contains only C preprocessor `#define` constants for register bit positions (`__SHIFT`) and bit masks (`_MASK`). It declares no functions, structs, enums, storage, initialization tables, or executable code.

The range starts in the tail of `DB_DEBUG5`, covers DB/CB/GB render-backend and color/depth control masks, then moves through three GCEA address blocks (`gc_gceadec`, `gc_gceadec2`, and `gc_gceadec3`). It ends in the `gc_rmi_rmidec` address block at the first mask for `RMI_TCIW_FORMATTER1_CNTL`, so the last register block is intentionally incomplete in this chunk and must be reconciled with the next chunk during the per-file merge.

## Purpose

`gc_11_0_3_sh_mask.h` is generated hardware metadata for AMDGPU GC 11.0.3 ASICs. Its macros define how driver code encodes and decodes bitfields in 32-bit Graphics Core registers. Consumers pair this file with the matching `gc_11_0_3_offset.h` register addresses and, where available, `gc_11_0_3_default.h` reset values.

This chunk's purpose is to expose field-level register layout for:

- Depth Buffer (`DB`) debug, clock-gating override, FIFO depth, and interface control fields.
- Color Buffer (`CB`) hardware-control, DCC, cache-eviction, arbitration, and fine-grain clock-gating fields.
- Graphics backend (`GB`) address configuration, render backend mapping, GPU ID, backend-disable, redundancy, and daisy-chain fields.
- GCEA client-to-group mapping, DRAM/IO arbitration, virtual-channel assignment, laziness/combining, priority, credit, reserve, error, EDC, DSM, probe, and backdoor-credit fields.
- SPI queue/event throttling fields.
- RMI/RMIDE C crossbar, UTC/UTCL1, XNACK, demux, status, FIFO, and TCIW formatter fields.

The header is part of the register-description contract, not a policy module. Hardware programming policy lives in AMDGPU implementation files that use these macros with register access helpers.

## Important APIs, Types, And Macros

There are no callable APIs or C types in this chunk. The exported interface is the macro naming convention:

- `<REGISTER>__<FIELD>__SHIFT` gives the least-significant bit position of a field.
- `<REGISTER>__<FIELD>_MASK` gives the field mask in the 32-bit register word.
- Consumers typically combine these macros through AMDGPU helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `WREG32_SOC15`, `RREG32_SOC15`, and `SOC15_REG_OFFSET`.

Important register groups in this range:

- `DB_DEBUG5`: tail fields for depth-buffer debug/disable controls, including tile-cache preloading, secondary mip tail compression, FLQ/MCC checks, no-Z power savings, VRS conflicts, tile cache prefetch, HTILE harvesting, residency checks, PRT-related Z/S NACK behavior, and spare high bits.
- `DB_FGCG_SRAMS_CLK_CTRL` and `DB_FGCG_INTERFACES_CLK_CTRL`: fine-grain clock-gating override bits for DB SRAMs and DB interfaces to SC, CB export, RMI read/write request paths, tile/wave/free-wave paths, and CB RMI return.
- `DB_FIFO_DEPTH4`: OSB squad, tile, scoreboard, and event FIFO depth fields.
- `CC_RB_REDUNDANCY`, `CC_RB_BACKEND_DISABLE`, `CC_RB_DAISY_CHAIN`, `GB_BACKEND_MAP`, `GB_GPU_ID`, `GB_ADDR_CONFIG`, and `GB_ADDR_CONFIG_READ`: render-backend disable/redundancy, backend map, GPU ID, pipe/interleave/PKR/SE/RB topology, and readback topology layout.
- `CB_HW_CONTROL`, `CB_HW_CONTROL_1`, `CB_HW_CONTROL_2`, `CB_HW_CONTROL_3`, and `CB_HW_CONTROL_4`: Color Buffer behavior controls covering compression, metadata, DCC, CMASK/HTILE interaction, hazard/workaround bits, state-machine behavior, event/export handling, and other generated hardware knobs.
- `CB_DCC_CONFIG` and `CB_DCC_CONFIG2`: DCC RAM, meta, pipe/hash, cache, and configuration fields.
- `CB_HW_MEM_ARBITER_RD` and `CB_HW_MEM_ARBITER_WR`: read/write arbitration selection and queue/control masks.
- `CB_FGCG_SRAM_OVERRIDE`, `CHICKEN_BITS`, and `CB_CACHE_EVICT_POINTS`: generated override/debug/cache eviction fields.
- `GCEA_DRAM_*` and `GCEA_IO_*` client/group blocks: read/write `CLI2GRP_MAP0/1` fields map 32 client IDs (`CID0`-`CID31`) into four groups; `GRP2VC_MAP` assigns groups to virtual channels; `LAZY`, `CAM_CNTL`, page/group burst, priority aging, queuing, fixed, urgency, masking, and quantum threshold registers control arbitration policy.
- `GCEA_SDP_*`: final SDP arbitration, DRAM/IO priority, tag/write/read/probe credit limits, virtual-channel tag and VCC/VCD reserves, request controls, backdoor command/data/misc credits, and enable fields.
- `GCEA_MISC`, `GCEA_MISC2`, `GCEA_LATENCY_SAMPLING`, `GCEA_MAM_CTRL`, `GCEA_MAM_CTRL2`, `GCEA_RRET_MEM_RESERVE`, and `GCEA_PROBE_*`: miscellaneous GCEA routing, sampling, MAM memory addressing/latency controls, read-return reserves, probe mapping/filtering, and block/request override fields.
- `GCEA_EDC_CNT`, `GCEA_EDC_CNT2`, and `GCEA_EDC_CNT3`: error-detection/correction count and mask fields for DRAM, GMI, IO, return, SDP, and MAM memories.
- `GCEA_DSM_CNTL`, `GCEA_DSM_CNTLA`, `GCEA_DSM_CNTLB`, `GCEA_DSM_CNTL2`, `GCEA_DSM_CNTL2A`, and `GCEA_DSM_CNTL2B`: DSM irritator, single-write, error-injection, and injection-delay controls across DRAM/GMI/IO/page/MAM memories.
- `GCEA_ERR_STATUS`: SDP response status, data status/parity, clear, busy-on-error, FUE, fatal interrupt, and level interrupt fields.
- `SPI_PQEV_CTRL` and `SPI_EXP_THROTTLE_CTRL`: SPI packet/queue event and export throttle controls.
- `RMI_GENERAL_CNTL`, `RMI_GENERAL_CNTL1`, and `RMI_GENERAL_STATUS`: RMI global controls and status/error fields, including clock gating, write-combine and reorder controls, skid FIFO errors, PRT/XNACK related state, and reserved/status bits.
- `RMI_SUBBLOCK_STATUS0` through `RMI_SUBBLOCK_STATUS3`: UTC external latency FIFO usage, skid FIFO free-space, PRT FIFO usage, and TCIW in-flight counters.
- `RMI_XBAR_CONFIG`, `RMI_PROBE_POP_LOGIC_CNTL`, `RMI_UTC_XNACK_N_MISC_CNTL`, `RMI_DEMUX_CNTL`, `RMI_UTCL1_CNTL1`, `RMI_UTCL1_CNTL2`, and `RMI_UTC_UNIT_CONFIG`: RMI crossbar arbitration, probe pop/fifo tuning, UTC/XNACK timer behavior, demux arbitration, UTCL1 GPUVM/invalidation/response/permission/perf/EDC controls, and TMZ request enable bits.
- `RMI_TCIW_FORMATTER0_CNTL` and the beginning of `RMI_TCIW_FORMATTER1_CNTL`: TCIW maximum in-flight, reorder-disable, write-combine, and fault-return-data controls. The `FORMATTER1` block continues after line 12211.

## Control Flow

There is no runtime control flow in this chunk. The C preprocessor substitutes constants at compile time.

The implied consumer flow is:

1. Include the GC 11.0.3 offset and shift/mask headers selected by the active ASIC generation.
2. Select a register address from the companion offset header.
3. Construct or decode the register value by applying the field mask and shift, often through `REG_SET_FIELD` or `REG_GET_FIELD`.
4. Read or write the register using SOC15/MMIO helpers or an indirect register path when the register belongs to an indexed block.

For example, a consumer programming a GCEA priority register would preserve unrelated bits, clear a field using `GCEA_*_MASK`, shift the new field value by `GCEA_*__SHIFT`, then write the full 32-bit word. A consumer collecting RMI diagnostics would read a status register and isolate FIFO or error fields using the corresponding `RMI_*_MASK` values.

## State And Persistence

This chunk stores no software state and allocates no memory. All macros are compile-time constants.

The represented state is hardware state:

- DB/CB/GB fields affect or describe render-backend topology, compression/cache behavior, fine-grain clock gating, debug disables, FIFO depths, backend disable maps, and RB redundancy.
- GCEA fields configure and report cross-client arbitration, virtual-channel routing, request batching, credit reserves, page/group burst limits, latency sampling, MAM behavior, EDC accounting, error status, and debug/error-injection state.
- SPI fields affect export throttling and packet/queue event control.
- RMI fields configure and report request crossbar routing, UTC/UTCL1 GPUVM behavior, XNACK/PRT handling, FIFO occupancy/free-space, TCIW formatting, demux arbitration, and error/status signals.

Persistence depends on the hardware register class, not on this header. Values may be reset by GPU reset, suspend/resume, runtime power-state transitions, firmware initialization, or ASIC-specific boot sequences. Some fields are normal policy knobs; others are diagnostic, reserved, debug, or error-injection controls that should not be casually programmed by generic paths.

## Dependencies And Integration Points

This generated header depends on the rest of the GC 11.0.3 register set:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_11_0_3_offset.h` supplies the matching register addresses.
- Other GC 11.0.3 generated headers supply defaults and related block metadata where present.
- AMDGPU implementation files include the generated register headers through ASIC-specific or SOC15 paths and use the macros with MMIO helpers, register field helpers, and indirect register access sequences.
- DB/CB/GB masks integrate with graphics initialization, render-backend harvesting/topology setup, compression/DCC policy, and workaround programming.
- GCEA masks integrate with memory fabric/client arbitration, GL2C/XBR/SDP credit tuning, error reporting, and low-level diagnostics.
- RMI and UTC/UTCL1 masks integrate with GPUVM, XNACK/PRT behavior, RMI crossbar configuration, fault handling, and status collection.

The file must remain synchronized with the hardware generator. A mask or shift mismatch can compile cleanly while programming the wrong bitfield at runtime.

## Risks And Edge Cases

- Generated-header drift is the main risk. Offsets, masks, shifts, and defaults must all come from the same GC 11.0.3 hardware database.
- This chunk begins inside `DB_DEBUG5` and ends inside `RMI_TCIW_FORMATTER1_CNTL`; merge/reconciliation must combine adjacent chunks before making whole-file statements about those two register blocks.
- Many fields are debug, workaround, reserved, clock-gating, or error-injection controls. Incorrect writes can cause hangs, performance loss, power regressions, false error reporting, or broken reset/resume behavior.
- GCEA has many repeated read/write and DRAM/IO register families with similar names and bit layouts. Copying a read mask into a write path, or a DRAM field into an IO path, can silently target the wrong policy.
- The `CID0`-`CID31`, `VC0`-`VC7`, and group-indexed macros are dense bitfields. Off-by-one client, group, or virtual-channel indexing errors are plausible even when the masks are correct.
- Some masks cover reserved bits or high-bit status fields. Code should avoid writing reserved fields unless the hardware sequence explicitly requires it.
- RMI/UTCL1 fields touch GPUVM response, fault, invalidate, permission, XNACK, and TMZ behavior. Bad values can surface as page-fault handling failures, retry/XNACK problems, memory-permission bugs, or fault-reporting anomalies.
- EDC and DSM controls include error-injection and irritator fields. These should be isolated to diagnostics, validation, or hardware bring-up paths.

## Test Signals

There are no unit-testable functions in this chunk. Useful validation signals are build, generated-header, and hardware-integration oriented:

- Compile AMDGPU GC 11.0.3 paths that include this header; missing or renamed macros should fail at build time.
- Regenerate the header from the authoritative hardware database and compare the emitted masks/shifts and block ordering.
- Run GPU initialization, reset, suspend/resume, and runtime power-management tests on GC 11.0.3 hardware to catch DB/CB/GB/GCEA/RMI programming drift.
- Exercise graphics workloads that use DCC/compression, render-backend topology, and memory arbitration to expose CB/DB/GB or GCEA policy mistakes.
- Run GPUVM, PRT, XNACK, and fault-handling tests to validate RMI/UTC/UTCL1 field usage.
- Monitor hardware error and EDC counters, interrupt behavior, and fault logs when touching `GCEA_ERR_STATUS`, `GCEA_EDC_*`, `RMI_GENERAL_STATUS`, or DSM injection fields.
- Use low-level register dumps before and after init/resume/reset to verify expected fields are set and reserved bits remain untouched.
