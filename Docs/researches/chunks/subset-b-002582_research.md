# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_12_0_0_sh_mask.h lines 32556-35081

## Scope

This chunk is a generated AMD GC 12.0.0 shift/mask register-header segment. It contains C preprocessor constants only: every hardware register field is represented by a `<REGISTER>__<FIELD>__SHIFT` macro and a corresponding `<REGISTER>__<FIELD>_MASK` macro. There are no functions, structs, enums, variables, includes, loops, allocations, locks, callbacks, or executable branches in this range.

The selected range begins in the tail of `SC_MEM_SCOPE`, covering `HIZ_SCOPE` and `HIS_SCOPE` shift/mask values after the VRS fields started in the previous lines. It then covers shader-queue, shader-pipe, UTCL1, TCP, SPI resource reservation, graphics user, GL1, SE CAC/DIDT EDC, and the beginning of performance-counter mask definitions. The final selected line is only the `//TCP_PERFCOUNTER0_LO` register comment; its shift/mask definitions are in the following chunk.

Although the source tree path is under a `ceph-client` mirror, this file is AMDGPU DRM hardware metadata for AMD GC 12.0.0 graphics IP. It is not Ceph filesystem logic.

## Purpose

`gc_12_0_0_sh_mask.h` gives AMDGPU code the bit layouts for GC 12.0.0 hardware registers. Callers pair these field masks with matching register addresses from the companion GC 12.0.0 offset header and typically use helper macros such as `REG_SET_FIELD` and `REG_GET_FIELD` to pack or decode fields without hard-coding raw bit positions.

This chunk focuses on shader engine and shader-array infrastructure:

- `SC_MEM_SCOPE` tail fields define memory-scope controls for hierarchical Z and hierarchical stencil alongside the VRS rate/feedback scope fields that begin just before this chunk.
- `gc_gfx_se_gfx_se_pfvf_sqdec` covers SQ runtime/debug status, shader memory base/config fields, trap-base and trap-memory-address registers, and shader debug toggles.
- `gc_gfx_se_gfx_se_pfonly_spidec` covers SPI/CDBG enablement, graphics-debug wave stall/trap controls, reset-debug disable bits, GDS compute max wave id, SPI/PC arbitration and feature limits, shader resource limits, and per-pipe/per-queue compute wavefront context-save busy status.
- `gc_gfx_se_gfx_se_pfonly_utcl1dec` covers UTCL1 control, invalidation-disable, FIFO sizing, GCRD target/credit safety, and eight identity-mode templates that describe synthesized translation-return attributes.
- `gc_gfx_se_gfx_se_pfonly_tcpdec` covers texture/cache pipe invalidation, busy/status bits, data/cache controls, credit knobs, compression controls, and arbitration.
- `gc_gfx_se_gfx_se_pfonly2_spidec` covers repeated per-CU SPI resource reservations and reservation-enable masks for 16 CUs.
- `gc_gfx_se_gfx_se_gfxudec` covers tessellation/offchip and GE ring sizing, line stipple and screen extents, pre-shader trap-screen controls, SQ thread-trace userdata, SQC cache invalidation, TA buffer-cache base address, DB occlusion counters, SPI configuration/throttle/attribute ring/event/launch-guarantee registers.
- `gc_gfx_se_gfx_se_gl1dec` covers GL1/GL1X arbitration, burst, clock-gating, compression, credit, client delay, compressor override, GL1C/GL1XC controls, status, UTCL0 controls/status/retry, and compression-bypass overrides.
- `gc_gfx_se_gfx_se_pfonly_secacdec` covers shader-engine CAC/LCAC controls, DIDT EDC throttling/status/perf-counter fields, and a large bank of per-block CAC signal weights plus indirect index/data access.
- `gc_gfx_se_gfx_se_perfddec` starts the performance-counter readout map for GE2_SE, GRBMH, PA_SU, PA_SC, SPI, PC, SQ, SQG, SX, TA, and TD counters; the TCP counter family continues after this chunk.

## Important APIs, Types, And Macros

There are no callable APIs or C types in this slice. The exported interface is the generated macro naming contract:

- `<REGISTER>__<FIELD>__SHIFT` gives the low bit position for a field within a 32-bit register.
- `<REGISTER>__<FIELD>_MASK` gives the bit mask for that field.
- Full-register data or counter fields use `0xFFFFFFFFL`; high address or high counter halves may expose narrower masks such as `0x000000FFL` or `0x7FFFFFFFL`.
- Register-address symbols are expected in the matching GC 12.0.0 offset header under the same register names.
- AMDGPU register helper code, MMIO accessors, PM4 packet builders, context-save/restore logic, debug dumps, reset paths, RAS/power-management code, and performance-monitor logic are the likely direct consumers.

The major macro families in this chunk are:

- `SQ_RUNTIME_CONFIG`, `SQ_DEBUG_STS_GLOBAL`, `SQ_DEBUG_STS_GLOBAL2`, `SH_MEM_BASES`, `SH_MEM_CONFIG`, `SQ_DEBUG`, `SQ_SHADER_TBA_*`, and `SQ_SHADER_TMA_*`: shader queue status, memory addressing/configuration, debug control, and trap handler/trap memory address fields.
- `SPI_CDBG_SYS_*`, `SPI_GDBG_*`, `SPI_RESET_DEBUG`, `SPI_ARB_CNTL_0`, `SPI_FEATURE_CTRL`, `SPI_SHADER_RSRC_LIMIT_CTRL`, `PC_CONFIG_CNTL_*`, and `SPI_COMPUTE_WF_CTX_SAVE_STATUS`: SPI debug, wave stall/trap, reset-debug, arbitration, shader resource limit, primitive control, and context-save status fields.
- `UTCL1_CTRL_0`, `UTCL1_CTRL_2`, `UTCL1_FIFO_SIZING`, `GCRD_*`, and `UTCL1_IDENTITY_MODE0..7`: UTCL1 translation/cache invalidation, credit, identity-mode, return-attribute, fault, PTE TMZ, XNACK, physical-address, IO steer, MTYPE, and dirty-bit fields.
- `TCP_INVALIDATE`, `TCP_STATUS`, `TCP_CNTL`, `TCP_CNTL2`, `TCP_CREDIT`, `TCP_COMPRESSION_CNTL`, and `TCP_ARB`: TCP invalidate trigger, busy/status observation, cache behavior, MGCG/FGCG override, write combining, end-of-wave forcing, data-compression, credit, and arbitration fields.
- `SPI_RESOURCE_RESERVE_CU_0..15` and `SPI_RESOURCE_RESERVE_EN_CU_0..15`: per-CU reserved VGPR/SGPR/LDS/wave/barrier resources and enable/type/queue masks.
- `VGT_TF_RING_SIZE`, `VGT_HS_OFFCHIP_PARAM`, `GE_POS_RING_*`, `GE_PRIM_RING_*`, `PA_*`, `SQ_THREAD_TRACE_USERDATA_*`, `SQC_CACHES`, `TA_CS_BC_BASE_ADDR*`, and `DB_OCCLUSION_COUNT*`: tessellation, geometry-engine rings, raster/pre-shader trap coordinates, thread trace metadata, SQC invalidate/complete, texture address base, and occlusion counter fields.
- `SPI_CONFIG_CNTL*`, `SPI_GS_THROTTLE_CNTL*`, `SPI_ATTRIBUTE_RING_*`, `SPI_SQG_EVENT_CTL`, and `SPI_GRP_LAUNCH_GUARANTEE_*`: SPI priority, export allocation, power-save, context-save wait, throttle, attribute ring, SQG events, and launch-guarantee fields.
- `GL1*` and `GL1X*` plus `GL1C*` and `GL1XC*`: GL1/GL1X arbitration/burst/compression and client/cache behavior, GL1C/GL1XC status, UTCL0 response/fault modes, invalidation VMID/toggle fields, retry counters, in-flight limits, and compression bypass overrides.
- `SE_CAC_*` and `DIDT_EDC_*`: shader-engine current/activity counter controls, low-current activity counter overrides, DIDT EDC enable/reset/throttle/stall-pattern/status/overflow/rolling-power/perf-counter fields, many per-client 16-bit weighting signals, and indirect CAC register access.
- `*_PERFCOUNTER*_LO` and `*_PERFCOUNTER*_HI`: performance counter low/high readout fields for GE2_SE, GRBMH, PA_SU, PA_SC, SPI, PC, SQ, SQG, SX, TA, and TD blocks.

## Control Flow

This header has no runtime control flow. All behavior is compile-time macro substitution.

The implied driver flow is:

1. Select the GC 12.0.0 register headers for the active ASIC.
2. Select a register address from the matching offset header.
3. Read a register, prepare a context-state value, build a PM4 packet, poll status, or decode a debug/performance readback.
4. Use the `__SHIFT` and `__MASK` pair, usually via AMDGPU register helper macros, to pack or extract a field.
5. Apply the resulting value to SQ/SPI/PC/TCP/UTCL1/GL1/CAC/performance-counter setup, diagnostics, reset handling, or context-save/restore.

For programming registers, the control flow is owned by AMDGPU graphics, compute, debug, reset, power, and performance-monitor code. For status and counter registers, callers typically poll, snapshot, or expose decoded values through debugfs, trace, hang-dump, RAS, or performance tooling. This chunk does not encode ordering, synchronization, side effects, valid value ranges, or poll timeouts; those must come from surrounding driver code and the hardware programming guide.

## State And Persistence Behavior

The macros themselves are stateless and persist nothing. They describe fields in live GPU hardware registers whose values may be context state, global engine state, volatile status, side-effect triggers, or read-only counters.

SQ/SPI/PC fields are mostly shader-engine and shader-pipe control/debug state. Trap-base/trap-memory address registers are split low/high address fields plus `TRAP_EN`; incorrect composition affects shader trap dispatch. `SH_MEM_BASES` and `SH_MEM_CONFIG` are per-shader addressing and cache behavior state that can participate in context save/restore and VMID isolation. Debug stall and reset-disable fields can change forward progress and reset behavior for active queues.

`SPI_COMPUTE_WF_CTX_SAVE_STATUS` is volatile status: each pipe/queue busy bit reports context-save activity and can change while waves are running. `SPI_RESOURCE_RESERVE_CU_*` and enable registers persist resource-reservation policy until reprogrammed and can reduce visible CU resources or gate specific queue/type classes.

UTCL1, GL1, GL1C, GL1X, and GL1XC fields describe cache, translation, invalidation, credit, retry, fault, compression, and request-tracking state. Some fields are configuration knobs, some are volatile busy/fault/retry status, and some trigger or shape invalidation behavior. Identity-mode registers synthesize translation-return attributes such as snoop, fragment size, permission, XNACK, PTE TMZ, no-PTE, physical address, IO steering, MTYPE, and dirty status; bad settings can bypass normal VM semantics in identity-mode paths.

TCP fields include explicit side effects (`TCP_INVALIDATE__START`), volatile busy/status bits, and cache/compression policy. `TCP_COMPRESSION_CNTL` and GL1 compressor override fields affect data-compression behavior and can interact with memory coherency, cache policy, sparse residency, and performance.

GFXU state covers ring base/size fields, screen extents, trap-screen controls, thread-trace userdata, SQC cache invalidate/complete, TA buffer-cache base address, and DB occlusion counters. Ring and base-address fields persist as graphics context/global engine configuration; counters and status fields change as work executes.

SE CAC and DIDT EDC registers are power/current-management instrumentation and throttling controls. CAC windowing and weight tables affect activity/current estimation. DIDT EDC enable, thresholds, stall patterns, throttle controls, and force-stall fields can intentionally stall SQ/DB/TCP/TD paths; status, overflow, rolling power delta, and perf counter fields are dynamic readbacks.

Performance-counter fields are readout-only or readout-oriented data surfaces from monitored blocks. The low/high pairs must be sampled coherently according to the performance-monitor sequence outside this header. The header only says that each low/high field occupies the full 32-bit register.

Reserved, unused, and spare fields appear throughout the chunk. Their presence as generated macros does not make them safe for arbitrary writes; read-modify-write code should preserve unrelated bits unless the hardware sequence documents a full-register write.

## Dependencies And Integration Points

This chunk depends on the generated GC 12.0.0 register set staying synchronized:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_12_0_0_offset.h` supplies matching register address macros.
- Matching generated default headers, where present, supply reset/default values for many of these registers.
- AMDGPU register helper macros provide field packing/extraction and MMIO/PM4 access patterns.
- ASIC-specific AMDGPU graphics, compute, KFD-adjacent, VM, cache, reset, debug, RAS, power-management, and performance-monitor code can include these constants.
- Userspace graphics and compute stacks depend on these values indirectly through kernel command submission, context programming, debug/perf queries, and firmware/kernel ABI behavior.

Important integration surfaces include shader trap setup, SQ debug status dumps, shader memory aperture setup, SPI wavefront/context-save coordination, graphics reset inhibition/debugging, PC/SPI arbitration tuning, per-CU resource reservations, UTCL1 translation and invalidation behavior, TCP invalidation and compression policy, SQC cache invalidation, GL1/GL1X cache and compression behavior, DB occlusion counter readback, thread-trace userdata, attribute-ring programming, launch-guarantee controls, CAC/LCAC and DIDT EDC power throttling, and performance counter sampling.

## Risks And Edge Cases

- Generated-header drift is the main risk. A wrong shift or mask still compiles but writes or decodes the wrong hardware bits.
- The selected chunk starts mid-register and ends on a register comment without the matching definitions. Complete file-level analysis must merge adjacent chunks for the full `SC_MEM_SCOPE` and `TCP_PERFCOUNTER0_*` families.
- Many families are repeated and index-sensitive: UTCL1 identity modes `0..7`, SPI resource reservations `0..15`, CU reservation enables `0..15`, occlusion counters `0..3`, and performance counters. Single-index generation mistakes can affect only one lane and be hard to diagnose.
- Side-effect fields such as `TCP_INVALIDATE__START`, `SQC_CACHES__INVALIDATE`, `SQC_CACHES__COMPLETE`, shader debug stalls, reset-disable bits, and DIDT force/throttle controls must not be treated as passive configuration.
- Address split fields such as `SQ_SHADER_TBA_*`, `SQ_SHADER_TMA_*`, `TA_CS_BC_BASE_ADDR*`, and GE ring base fields require correct low/high composition and alignment assumptions from the hardware spec.
- Cache, translation, retry, fault, compression, snoop, atomic, and invalidation fields in UTCL1/GL1/TCP can cause memory ordering bugs, coherency failures, page-fault behavior changes, or silent data corruption if programmed with the wrong policy.
- `SH_MEM_CONFIG`, `SH_MEM_BASES`, and UTCL1 identity-mode fields have VM/security implications because they affect address translation, permission, and trap behavior.
- SPI resource limits and per-CU reservation masks can starve waves, underutilize CUs, or break queue isolation if queue/type masks are wrong.
- DIDT EDC and CAC fields tie performance to power/current estimation. Bad thresholds, weights, or stall patterns can cause excessive throttling, missed protection, unstable clocks, or misleading telemetry.
- Performance-counter low/high readbacks require coherent sampling; this header does not describe latch order or overflow behavior.
- Reserved/spare fields appear with masks. They should be preserved unless a documented sequence requires writing them.

## Test Signals

Useful validation is mostly generated-data consistency, build coverage, hardware bring-up, and runtime diagnostics:

- Kernel build coverage for AMDGPU code that includes `gc_12_0_0_sh_mask.h`.
- Mechanical comparison against AMD's authoritative GC 12.0.0 register database for every `__SHIFT` and `__MASK` in lines 32556-35081.
- Cross-checks that each register in this chunk has a matching address symbol in `gc_12_0_0_offset.h` and, where generated, an expected default value in the matching default header.
- Static sanity checks that masks align with shifts, full-width fields use `0xFFFFFFFFL`, high halves have the expected widths, and repeated families keep identical field layouts across indices.
- SQ/SPI debug tests that verify busy/status decode, trap-base programming, wave stall/trap behavior, and compute context-save busy reporting across pipes and queues.
- VM/cache tests that exercise UTCL1 invalidation, identity-mode behavior, GL1/GL1X/GL1C/GL1XC fault/retry/status paths, TCP invalidation, cache compression controls, atomic/snoop behavior, and sparse or faulting memory accesses.
- Graphics workload tests covering tessellation/offchip buffering, GE primitive/position rings, line stipple, screen extents, trap-screen counting, DB occlusion counters, attribute rings, and launch-guarantee behavior.
- SQC/thread-trace diagnostics that confirm `SQC_CACHES` invalidate/complete transitions and thread-trace userdata capture.
- Resource scheduling tests that validate SPI per-CU reservation and enable masks do not strand queues, misroute queue types, or violate resource accounting.
- Power/current-management tests that compare CAC window/weight output and DIDT EDC throttle/status/performance-counter behavior under controlled SQ/DB/TCP/TD workloads.
- Performance-monitor tests that sample GE2_SE, GRBMH, PA_SU, PA_SC, SPI, PC, SQ, SQG, SX, TA, and TD counter low/high pairs and check monotonicity, overflow handling, and block attribution.
- Runtime warning signals include GPU hangs during context save/restore, unexpected reset suppression, incorrect shader trap behavior, VM faults or missing faults, cache incoherency, broken compression/decompression, excessive throttling, impossible busy/status dumps, performance counters stuck at zero, or rendering/compute corruption isolated to GC 12.0.0 paths.

## Cross-Chunk Notes

This is only the chunk research document for `subset-b-002582`. It covers lines 32556-35081 of `gc_12_0_0_sh_mask.h`. The final per-file research should merge this with adjacent chunks to complete the surrounding `SC_MEM_SCOPE` and TCP performance-counter definitions and to place these SQ/SPI/UTCL1/TCP/GL1/CAC/performance-counter masks in the full GC 12.0.0 register map.
