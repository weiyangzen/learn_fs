# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_12_0_0_offset.h lines 9954-11061

## Scope

This chunk is the final segment of the generated AMD GC 12.0.0 register offset header. It contains C preprocessor constants only: `reg...` macros define MMIO/register offsets, matching `reg..._BASE_IDX` macros define the SOC15 register base index, and `ix...` macros define offsets inside indirect/indexed register spaces. There are no functions, structs, enums, variables, includes, allocations, locks, callbacks, or executable branches in this range.

The slice starts mid-family with `regSQG_PERFCOUNTER7_LO_BASE_IDX`, whose matching `regSQG_PERFCOUNTER7_LO` definition is in the previous adjacent chunk. It then completes graphics/shader-engine performance counter result registers, provides performance counter selection/control registers for the per-SE performance decoder, maps clock-gating/power-management registers, lists user/harvest/remap/security registers, and finishes with several indexed register blocks: GC CAC, RTAVFS, DBGU GFX ports, shader queue debug/wave state, and SE CAC. The chunk ends with the header's `#endif`, so this is the terminal chunk for `gc_12_0_0_offset.h`.

Although the repository path is under a `ceph-client` source mirror, this file is AMDGPU DRM hardware metadata for AMD graphics IP and is unrelated to Ceph filesystem client behavior.

## Purpose

`gc_12_0_0_offset.h` is the address half of the generated GC 12.0.0 register interface. AMDGPU code combines these symbols with matching shift/mask/default headers and register access helpers to read, write, poll, and program graphics-core hardware registers without hard-coded numeric offsets in driver logic.

This chunk specifically describes:

- Performance counter result registers for shader and render blocks, including `SX`, `TA`, `TD`, `TCP`, `GL1C`, `GL1XC`, `CB`, `DB`, `RMI`, `PA_PH`, `UTCL1`, `GL1A`, and `GL1XA` counter low/high pairs.
- Per-shader-engine performance counter control/select registers under `gc_gfx_se_gfx_se_perfsdec`, including `GE2_SE`, `GRBMH`, `PA_SU`, `PA_SC`, `SPI`, `PC`, `SQ`, `SQG`, `SX`, `TA`, `TD`, `TCP`, `GL1C`, `GL1XC`, `CB`, `DB`, `RMI`, `PA_PH`, `UTCL1`, `GL1A`, and `GL1XA`.
- Shader queue thread-trace registers, including buffer sizes, buffer base addresses, trace control/masks, write pointer, halt/status, poweroff restore, draw/marker counters, dropped packet counter, and finish debug status.
- Graphics clock-gating/power registers under `gc_gfx_se_gfx_se_pwrdec`, `gc_gfx_se_gfx_sc_pwrdec`, and `gc_gfx_se_gfx_se_gl1_pwrdec`, covering SPI, PC, BCI, VGT, GS/NGG, PA, SQ/SQG, SX, TA/TD, DB, CB, RMI, SE CAC, PH, TCP, LDS, UTCL1, GRBMH, SC, GL1C, GL1XC, GL1A, and GL1XA controls.
- Hypervisor/user-topology registers under `gc_gfx_se_gfx_se_hypdec` and related GRBMH/GRBM blocks, including GL1 pipe steering, user shader-array configuration, WGP/RB/RMI disable or redundancy state, shader-rate configuration aliases, and shader-engine/remap controls.
- Security and indirect-register spaces, including `UTCL1_SECURITY`, `ixGC_CAC_*`, `ixRTAVFS_REG0..194`, `ixPACKER_CONTROL`, `ixSQ_*` wave/debug registers, and `ixSE_CAC_*`.

## Important APIs, Types, And Macros

There are no callable APIs or C types. The public interface is the generated macro contract:

- `regNAME` gives the register offset used with AMDGPU SOC15/MMIO register helpers or command-packet register programming.
- `regNAME_BASE_IDX` gives the SOC15 base index. Every `reg..._BASE_IDX` visible in this chunk is `1`, indicating these registers belong to the second base aperture for the GC 12.0.0 generated address map.
- `ixNAME` gives an offset within an indirect/indexed register space rather than a normal `reg...` MMIO offset. Callers must use the matching indirect access path for the block, not a plain MMIO access using the numeric value alone.

Important macro families in this chunk include:

- Counter result pairs: `regSX_PERFCOUNTER0..3_{LO,HI}`, `regTA_PERFCOUNTER0..1_{LO,HI}`, `regTD_PERFCOUNTER0..1_{LO,HI}`, `regTCP_PERFCOUNTER0..3_{LO,HI}`, `regGL1C_PERFCOUNTER0..3_{LO,HI}`, `regGL1XC_PERFCOUNTER0..3_{LO,HI}`, `regCB_PERFCOUNTER0..3_{LO,HI}`, `regDB_PERFCOUNTER0..3_{LO,HI}`, `regRMI_PERFCOUNTER0..3_{LO,HI}`, `regPA_PH_PERFCOUNTER0..7_{LO,HI}`, `regUTCL1_PERFCOUNTER0..3_{LO,HI}`, `regGL1A_PERFCOUNTER0..3_{LO,HI}`, and `regGL1XA_PERFCOUNTER0..3_{LO,HI}`.
- Counter selection/control: `regGE2_SE_PERFCOUNTER*_SELECT*`, `regGRBMH_PERFCOUNTER*_SELECT`, `regPA_SU_PERFCOUNTER*_SELECT*`, `regPA_SC_PERFCOUNTER*_SELECT*`, `regSPI_PERFCOUNTER*_SELECT*`, `regPC_PERFCOUNTER*_SELECT*`, `regSQ_PERFCOUNTER0..15_SELECT`, `regSQG_PERFCOUNTER*_SELECT`, `regSQG_PERFCOUNTER_CTRL*`, `regSQ_PERFCOUNTER_CTRL*`, and block-local select/filter/control registers for SX, TA, TD, TCP, GL1C/GL1XC, CB, DB, RMI, PA_PH, UTCL1, GL1A, and GL1XA.
- Thread trace: `regSQ_THREAD_TRACE_BUF0_*`, `regSQ_THREAD_TRACE_BUF1_*`, `regSQ_THREAD_TRACE_CTRL`, `regSQ_THREAD_TRACE_MASK`, `regSQ_THREAD_TRACE_TOKEN_MASK`, `regSQ_THREAD_TRACE_WPTR`, `regSQ_THREAD_TRACE_HALT`, `regSQ_THREAD_TRACE_STATUS*`, counter registers for GFX/HP3D draw and marker events, dropped counter, and finish debug.
- Clock gating and power: `regGFX_ICG_*`, `regCGTT_*_CLK_CTRL*`, `regCGTX_SPI_DEBUG_CLK_CTRL`, `regSQ_*_CLK_CTRL`, `regICG_*_CLK_CTRL`, `regDB_CGTT_CLK_CTRL_0`, and GL1 medium-grain clock-gating override registers.
- Topology, harvest, remap, and security: `regGL1_PIPE_STEER`, `regGL1X_PIPE_STEER`, `regGC_USER_SHADER_ARRAY_CONFIG`, `regGRBMH_GC_USER_SA_UNIT_DISABLE`, `regGC_USER_SA_UNIT_DISABLE_1`, `regGC_USER_RB_BACKEND_DISABLE`, `regGC_USER_RMI_REDUNDANCY`, `regGC_USER_SHADER_RATE_CONFIG`, `regGRBMH_WGP_SA*_REMAP_CNTL`, `regGRBMH_RB_SA*_REMAP_CNTL`, `regGRBMH_GRBM_SA_REMAP_CNTL`, and `regUTCL1_SECURITY`.
- Indirect blocks: `ixGC_CAC_ID`, `ixGC_CAC_CNTL`, many `ixGC_CAC_ACC_*` accumulator sources, stall/power-break lookup registers, fixed-pattern counters, hardware LUT update status registers, `ixRTAVFS_REG0..194`, `ixPACKER_CONTROL`, shader queue debug/wave state registers such as `ixSQ_WAVE_STATUS`, `ixSQ_WAVE_PC_{LO,HI}`, `ixSQ_WAVE_TTMP0..15`, and `ixSE_CAC_ID/CNTL`.

## Control Flow

This header has no runtime control flow. It contributes compile-time macro substitution only.

The implied driver flow is in AMDGPU consumers:

1. Select the GC 12.0.0 register header set for the active ASIC/IP version.
2. Use a `reg...` offset with the correct SOC15 base index for direct register reads, writes, read-modify-write operations, polling, or command-stream programming.
3. Use an `ix...` offset only through the owning indexed-register accessor, after programming the appropriate indirect address/data registers or block-specific debug window.
4. Pair offsets from this file with bit definitions from the matching GC 12.0.0 shift/mask header when composing field values or decoding register contents.
5. Apply hardware-specific ordering outside this header: counter event selection before enable/readback, thread-trace buffer setup before capture, clock-gating writes during safe power-management windows, and topology/security/remap writes only during initialization or privileged transitions.

For performance counters, the usual flow is to program `*_SELECT` and control registers, clear or arm counters through the owning block, run a workload, then read `*_LO` and `*_HI` result registers with the hardware's required latching or snapshot sequence. For thread tracing, software programs buffer base/size registers, masks and token filters, enables capture, polls/halt/status registers, and consumes buffer data using the write pointer. For power and topology registers, initialization, reset, suspend/resume, or virtualization paths write configuration registers after firmware and fuse/harvest policy have established legal values.

## State And Persistence Behavior

The macros themselves are stateless and persist nothing. They describe GPU register addresses whose contents are owned by hardware, firmware, and AMDGPU runtime code.

Performance counter selector/control registers persist as profiling configuration until changed, reset, or power-gated. Result low/high registers expose hardware accumulation state. Because 64-bit counters are split across low/high 32-bit registers, readers may need a documented snapshot or high-low-high pattern to avoid torn samples; this header does not express atomicity.

Thread trace buffer size/base/control/mask registers are active debug state. Buffer base low/high fields identify memory used by trace capture, and stale or wrong addresses can corrupt memory or make diagnostics misleading. Trace status and dropped/finish counters are live hardware state and may be sticky or require defined clear sequencing in the consumer path.

Clock-gating and power control registers are durable hardware configuration across normal engine operation and can affect clock domains, idle behavior, power savings, and debug visibility. They should be written only by initialization, power-management, reset, or firmware-coordinated code that knows which domains are safe to gate. Full-register writes must preserve reserved bits unless the hardware specification says otherwise.

Topology, harvest, pipe-steering, user shader-array, shader-rate, RMI redundancy, RB disable, and remap registers describe active hardware layout. Bad programming can expose disabled units, hide valid units, steer traffic incorrectly, or attribute per-SE/per-SA work to the wrong physical block. These registers are especially sensitive around virtualization, SKU harvesting, reset recovery, and diagnostics.

`regUTCL1_SECURITY` and the CAC/RTAVFS/SQ indexed spaces are not ordinary passive constants. Security state, clock/activity counters, adaptive voltage/frequency indexed registers, and wave debug state can be privileged, sticky, command-like, or transient. The indirect `ix...` offsets persist only as addresses in the indexed namespace; the actual state and sequencing live in the hardware block and its driver/firmware owner.

## Dependencies And Integration Points

This chunk depends on the generated GC 12.0.0 register family remaining synchronized:

- `gc_12_0_0_sh_mask.h` supplies field shifts and masks for the register names addressed here.
- `gc_12_0_0_default.h`, when present in the same generated family, supplies reset/default values for some registers.
- AMDGPU SOC15 register helpers consume `reg...` offsets and `reg..._BASE_IDX` values for direct MMIO access.
- AMDGPU indirect-register helpers consume `ix...` offsets for CAC, RTAVFS, DBGU, SQ wave/debug, and SE CAC register spaces.
- GFX, CP, RLC, KFD/compute, perf counter, debugfs, GPU reset, suspend/resume, power-management, SR-IOV/virtualization, and hang-dump paths rely on this address map indirectly.

Important integration points include hardware performance monitoring, shader-engine perf event programming, thread-trace capture, graphics clock gating, shader/texture/cache/render-backend power controls, GL1 pipe steering, harvested-unit exposure, shader-array and render-backend disable masks, remap controls used for topology repair or virtualization, UTCL1 security setup, CAC accumulator access, RTAVFS indexed tuning/status, packer debug control, and shader wave inspection.

Because this is an offset header, most correctness is relational. A `reg...` value must match the hardware register database, the same symbol's masks in `gc_12_0_0_sh_mask.h`, the base index used by the SOC15 tables, and any generated default. An `ix...` value must match the indexed aperture selected by the accessor; using an indexed offset through a direct MMIO path or using a direct `reg...` offset as an index would target the wrong state.

## Risks And Edge Cases

- Generated-header drift is the primary risk. A wrong numeric offset or base index compiles cleanly but sends driver writes to the wrong register.
- The chunk begins mid-family at `regSQG_PERFCOUNTER7_LO_BASE_IDX`; the matching low-register offset is in the previous chunk. Merge logic must combine adjacent chunks before drawing whole-file conclusions about SQG counters.
- Counter families are highly repetitive but not perfectly uniform. Some blocks have select1 registers, filters, control registers, or fewer counters. Assuming symmetry across SQ, SQG, SPI, TCP, PA, CB, DB, RMI, GL1, and UTCL1 can miss real hardware differences.
- Split low/high counter and address-like registers are easy to read or write incorrectly. The header names identify pairs but do not provide latching, ordering, alignment, or overflow rules.
- `regCP_PERFMON_CNTL_1` aliases the same offset as `regGRBMH_CP_PERFMON_CNTL` in this chunk. Callers and reviewers must recognize alias names can exist for the same hardware location.
- Similar aliasing appears in topology/user registers, such as `regGRBMH_GC_USER_SA_UNIT_DISABLE` with `regGC_USER_SA_UNIT_DISABLE_1`, and `regGC_USER_SHADER_RATE_CONFIG` with `_1`. Alias drift can confuse diagnostics if one name is updated without the other in generated sources.
- Clock-gating and power registers have side effects. Accidental full-register writes, use outside safe windows, or preserving the wrong reserved bits can produce intermittent hangs, bad power state, or lost debug visibility.
- Harvest, remap, pipe-steering, RB disable, RMI redundancy, and shader-rate registers can affect hardware topology and isolation. Incorrect values may only fail on specific SKUs, shader-engine counts, harvested configurations, or SR-IOV partitions.
- `ix...` symbols look like simple offsets but require the correct indirect access mechanism. Misrouting an indexed access can read stale data, write a control register in a different aperture, or silently report meaningless debug state.
- RTAVFS and CAC indexed registers represent adaptive power/clock or counter/accumulator state. They may have firmware ownership or handshake requirements not captured by this offset-only header.
- Wave debug registers such as PC, EXEC, TTMP, trap, scratch, allocation, and status are context-sensitive. Reading them without selecting the intended wave/SIMD/SE context can produce misleading hang or shader-debug evidence.
- Security and virtualization-sensitive registers, especially `UTCL1_SECURITY` and topology/remap controls, should be considered privileged integration points even though the header itself has no access-control logic.

## Test Signals

Useful validation is mostly generated-data consistency plus hardware/runtime behavior:

- Build coverage for AMDGPU files that include the GC 12.0.0 register headers, especially GFX 12 initialization, KFD/compute, perf counter, thread trace, debugfs, reset, virtualization, and power-management paths.
- Mechanical comparison against AMD's authoritative GC 12.0.0 register database to verify every `reg...` offset, every `reg..._BASE_IDX`, every alias, and every `ix...` offset in lines 9954-11061.
- Cross-header checks that register names in this offset chunk have matching field masks in `gc_12_0_0_sh_mask.h` where the register is field-addressable, and matching defaults in the generated default header where expected.
- Static consistency checks for repeated families: low/high counter pairs should be adjacent where documented, select/control families should preserve expected stride patterns, aliases should share identical offsets, and all direct registers in this chunk should keep base index `1`.
- Perf counter tests that select events for SX, TA, TD, TCP, GL1C/GL1XC, CB, DB, RMI, PA_PH, UTCL1, GL1A/GL1XA, SQ/SQG, SPI, PC, GE2_SE, PA_SU, and PA_SC blocks, run controlled workloads, and verify nonzero or monotonic low/high results.
- Counter readback tests that stress 64-bit low/high read ordering and compare snapshot behavior against expected overflow/latch semantics.
- Thread-trace tests that program SQ trace buffers and masks, capture wave execution, verify write-pointer/status/dropped counters, and decode expected draw or marker events.
- Power-management tests that exercise suspend/resume, reset, clock-gating enablement, and idle transitions while monitoring SPI, SQ, SX, TCP, GL1, DB, CB, RMI, PH, UTCL1, and GRBMH clock-control state.
- Topology and harvest tests across SKUs or emulated fuse configurations to validate GL1/GL1X pipe steering, shader-array config, WGP/RB/RMI disable or remap registers, and shader-rate aliases.
- Virtualization/SR-IOV tests that verify remap, disable, redundancy, and security-related registers are accessible only through intended PF/VF or firmware-owned paths and decode to the expected partition topology.
- Indirect access tests for GC CAC, SE CAC, RTAVFS, DBGU packer control, and SQ wave/debug registers, ensuring the correct index/data window is selected before using each `ix...` offset.
- Hang-dump and shader-debug tests that select a known wave context and confirm `ixSQ_WAVE_*`, PC, EXEC, TTMP, trap, scratch, allocation, and shader-cycle registers decode coherently.
- Runtime warning signals include zero or nonsensical perf counters under active workloads, GPU hangs after clock-gating changes, failed thread trace capture, wrong harvested-unit exposure, invalid shader-engine remap, unexpected UTCL1/security behavior, misleading wave debug dumps, or register read/write traces that touch offsets adjacent to but not equal to the generated values.

## Cross-Chunk Notes

This is only the chunk research document for `subset-b-002568`. It covers lines 9954-11061 of `gc_12_0_0_offset.h`, the final chunk of that file. The final per-file report should merge it with chunks `subset-b-002564` through `subset-b-002567` so the complete GC 12.0.0 offset map includes earlier SDMA, GFX, VM, CP, RLC, shader, and performance-counter definitions, plus the SQG counter low offset that immediately precedes this slice.
