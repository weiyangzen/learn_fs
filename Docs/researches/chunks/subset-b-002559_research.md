# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_11_5_0_sh_mask.h lines 24949-27593

## Scope

This chunk is a generated AMD GC 11.5.0 shift/mask register-header segment. It contains preprocessor constants only: each hardware register field has a `<REGISTER>__<FIELD>__SHIFT` macro and a matching `<REGISTER>__<FIELD>_MASK` macro for packing and extracting 32-bit register values.

The requested range contains 1,054 `__SHIFT` constants and 1,054 `_MASK` constants. It begins in the middle of the `CP_GFX_RS64_GP0_HI0` register family, starting with the `M_RET_ADDR` mask whose shift was in the previous chunk, and ends on a complete `SPI_PERFCOUNTER0_SELECT` field set. The covered address blocks are the tail of command-processor RS64 state, `gc_gl1dec`, `gc_chdec`, `gc_gl2dec`, `gc_gl1hdec`, `gc_perfddec`, and the first part of `gc_perfsdec`.

Although the repository path is under a local `ceph-client` mirror, this file is AMDGPU DRM graphics-core metadata. It does not implement Ceph or distributed filesystem logic.

## Purpose

`gc_11_5_0_sh_mask.h` supplies bit layouts for GC 11.5.0 graphics hardware. Driver code pairs these macros with register offsets from `gc_11_5_0_offset.h` and typically consumes them through helper macros such as `REG_SET_FIELD` and `REG_GET_FIELD`.

This chunk covers these main hardware surfaces:

- CP graphics RS64 general-purpose, instruction-pointer, pending-interrupt, data-cache aperture, and interrupt fields.
- GL1 cache/decode controls and status, including arbitration, DRAM burst behavior, fine-grain clock-gating overrides, UTCL0 controls, retry knobs, and status flags.
- CH decode/channel cache controls and status, including arbitration, burst controls, client free-delay, FGCG overrides, and CHC request counters.
- GL2 cache/decode controls, status, address matching, writeback/invalidate, soft reset, CM control/stall fields, loopback counter data/select registers, configuration, discard-stall, GL2A address matching, priority, disable, and response throttling.
- GL1H arbitration and burst controls/status.
- Performance counter data registers for CP, GRBM, GE, PA, SPI, PC, SQ, SQG, SX, GCEA, GDS, TA, TD, TCP, GL2C, GL2A, GL1C, CHC, CB, DB, RLC, RMI, GCR, PA_PH, UTCL1, GL1A, GL1H, and CHA blocks.
- Performance counter select/control registers for CP, GRBM, GE1, GE2, PA_SU, PA_SC, and the first SPI counter.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, includes, allocations, locks, callbacks, or executable branches in this range. The public interface is the generated macro naming contract:

- `<REGISTER>__<FIELD>__SHIFT` gives the least-significant bit for a field.
- `<REGISTER>__<FIELD>_MASK` gives the raw bit mask inside the 32-bit register value.
- Matching register addresses live in `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_11_5_0_offset.h`.
- Consumers generally combine these macros with `REG_SET_FIELD`, `REG_GET_FIELD`, `SOC15_REG_OFFSET`, `RREG32*`, `WREG32*`, and command-stream/register dump tooling.

Important register groups in this chunk include:

- `CP_GFX_RS64_GP*`, `CP_GFX_RS64_INSTR_PNTR*`, and `CP_GFX_RS64_PENDING_INTERRUPT*`: command-processor RS64 micro-engine state, including return addresses, read/write selector fields, stack pointers, scratch data, halted-state bits, instruction pointers, and interrupt state.
- `CP_GFX_RS64_DC_APERTURE0_*` through `CP_GFX_RS64_DC_APERTURE15_*` for both aperture banks 0 and 1: data-cache aperture base/mask/control triplets. The control registers expose `VMID` and `BYPASS_MODE` bits.
- `CP_GFX_RS64_INTERRUPT1`: per-bit interrupt fields such as `EXCP`, `HOST`, `DOORBELL`, `MC_WRREQ_ERR`, and `FAULT`.
- `GL1_ARB_CTRL`, `GL1C_CTRL`, `GL1C_STATUS`, `GL1C_UTCL0_CNTL1`, `GL1C_UTCL0_CNTL2`, `GL1C_UTCL0_STATUS`, `GL1C_UTCL0_RETRY`, and `GL1C_CTRL2`: GL1 arbitration, clock-gating, cache enable/reset/invalidating, status, client and probe FIFO state, fault-stall, response scheduling, request miss behavior, and retry controls.
- `CH_ARB_CTRL`, `CHA_CLIENT_FREE_DELAY`, `CHI_CHR_REP_FGCG_OVERRIDE`, `CHC_CTRL`, and `CHC_STATUS`: channel/decode arbitration and CHC request/status fields.
- `GL2C_CTRL*`, `GL2C_STATUS`, `GL2C_ADDR_MATCH_*`, `GL2C_WBINVL2`, `GL2C_SOFT_RESET`, `GL2C_CM_CTRL*`, `GL2C_CM_STALL`, `GL2C_LB_*`, `CC_GC_GL2C_CONFIG`, and `GL2C_DISCARD_STALL_CTRL`: GL2 cache behavior, reset, invalidation, address matching, cache-management control, loopback counter reads, configuration, and discard-stall handling.
- `GL2A_*`: GL2A address-match, priority, enable/disable, and response-throttle fields.
- `*_PERFCOUNTER*_LO` and `*_PERFCOUNTER*_HI`: data registers for low/high halves of hardware performance counters. Most expose a full-width `PERFCOUNTER` field.
- `TCP_PERFCOUNTER_FILTER`, `TCP_PERFCOUNTER_FILTER2`, and `TCP_PERFCOUNTER_FILTER_EN`: TCP performance counter filtering by shader array, WGP/SIMD, VMID, mode, slot, client, bank, request/coherency type, and enable mask.
- `*_PERFCOUNTER*_SELECT` and `*_SELECT1`: event-select and mode registers. The common layout packs `PERF_SEL0`/`PERF_SEL1` in bits 0-9 and 10-19, `CNTR_MODE` in bits 20-23, and `PERF_MODE*` in high nibbles; the companion `SELECT1` registers carry `PERF_SEL2`/`PERF_SEL3` and mode fields.
- `CP_PERFMON_CNTL` and CP latency/window select registers: control CP performance monitoring, including clock gating, counter halt, and windowing/latency-stat source selection.
- `CP_DRAW_OBJECT*`, `CP_DRAW_WINDOW_*`, and `CP_DRAW_WINDOW_CNTL`: draw/object count and draw-window performance filtering controls.

## Control Flow

This header has no runtime control flow. Its direct behavior is compile-time macro substitution.

The implied runtime flow is:

1. GC 11.5.0 driver code includes the offset and shift/mask headers for the active ASIC.
2. A caller selects a register offset from `gc_11_5_0_offset.h`.
3. It uses field masks from this file with `REG_SET_FIELD` or `REG_GET_FIELD` to compose, update, or decode the register value.
4. The value is written or read through SOC15 MMIO helpers, indexed register helpers, RLC-safe accessors, command-stream packets, debugfs/register-dump paths, or profiling tools.

For cache-control registers, higher-level AMDGPU code sequences reset, invalidate, clock-gating, retry, and throttle writes around GPU init, suspend/resume, reset, or diagnostics. For performance counters, profiling code programs select/filter registers, starts or freezes counters, then reads low/high data registers. For RS64 state, register dump and command-processor control paths observe or program the micro-engine scratch, aperture, interrupt, and instruction-pointer surfaces. This file only provides bit positions and masks; ordering, waits, W1C/W1S behavior, privilege rules, and side effects are owned by hardware documentation and the driver call sites.

## State And Persistence Behavior

The macros themselves hold no state and persist nothing. They describe hardware-visible state:

- RS64 GP, instruction pointer, pending interrupt, aperture, and interrupt registers are CP micro-engine state. Some fields are software-programmed configuration, while others reflect hardware-updated execution or interrupt status.
- RS64 data-cache aperture base/mask/control state persists until explicitly reprogrammed or reset. The `VMID` and `BYPASS_MODE` fields affect which virtual address context and translation behavior is used for RS64 data-cache aperture accesses.
- GL1, CH, GL2, GL2A, and GL1H control registers persist as cache/decode configuration until reset or reprogramming. Status registers can change as shader, cache, and memory traffic runs.
- GL2 invalidation, writeback, soft-reset, discard-stall, and CM stall fields are side-effect-prone control surfaces even though this generated header does not annotate access semantics.
- Performance counter select/filter/control registers persist as profiling configuration until cleared, overwritten, context-switched, reset, or power-gated. Counter data registers are hardware-updated while their selected counters are active.
- Low/high counter pairs represent wider counter state split across two 32-bit registers. Readers need a coherent sampling strategy outside this header.

Reserved or `RESERVED` fields appear throughout the range. Callers should preserve them in read-modify-write sequences unless an authoritative full-register value is being emitted.

## Dependencies And Integration Points

The primary dependency is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_11_5_0_offset.h`, which supplies the corresponding `reg*` register offsets and base-index metadata. This shift/mask header must remain synchronized with that offset header and AMD's generated GC 11.5.0 register database.

Observed integration points in this tree include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfxhub_v11_5_0.c`, which includes `gc_11_5_0_offset.h` and `gc_11_5_0_sh_mask.h` and uses the generated masks through `REG_SET_FIELD` and `REG_GET_FIELD` for GCVM/gfxhub programming and fault decoding.
- Common AMDGPU register helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, and `WREG32_FIELD15_PREREG`, which rely on the generated `__SHIFT` and `_MASK` names.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/navi10_enum.h`, which carries performance event enumerations such as GL2C performance selectors used with the `*_PERFCOUNTER*_SELECT` fields represented here.
- Profiling, debugfs, performance monitoring, and register-dump tooling that programs or decodes `CPG/CPC/CPF`, `GRBM`, `GE`, `PA`, `SPI`, `TCP`, `GL2`, and related performance counters.
- ASIC bring-up, reset, suspend/resume, and power-management paths that may need cache-control and clock-gating fields from GL1, CH, GL2, and GL1H blocks.

Behaviorally, this chunk sits at the boundary between command-processor RS64 state, graphics cache/decode control, address matching/throttling, and the GC performance-monitoring fabric.

## Risks And Edge Cases

- Generated-header drift is the central risk. A bad shift or mask can compile cleanly while programming the wrong hardware bits.
- The chunk begins mid-register. The `CP_GFX_RS64_GP0_HI0__M_RET_ADDR__SHIFT` definition is in the previous chunk, while this chunk starts with its mask. File-level research must reconcile that artificial boundary.
- RS64 GP and instruction-pointer fields are low-level CP state. Mis-decoding them can confuse diagnostics; misprogramming them can affect CP micro-engine execution, stack handling, interrupt delivery, or aperture access.
- Aperture base/mask/control triplets are highly repetitive across 16 apertures and two banks. Copy/paste or generation errors can alias VMIDs, bypass behavior, or aperture ranges in ways that only show for specific aperture indices.
- GL1/GL2/CH reset, invalidation, retry, and clock-gating controls can cause hangs, stale cache contents, bad retry behavior, or power/performance regressions if masks do not match the ASIC.
- Status registers often contain transient, latched, or clear-sensitive bits. This header does not encode whether fields are read-only, write-one-to-clear, sticky, or side-effecting.
- GL2 address-match and size masks may have implicit address granularity. Consumers must apply the hardware-defined address units rather than treating every field as byte-addressed.
- Performance counter select fields are dense and repeated. Wrong `PERF_SEL*`, `CNTR_MODE`, or `PERF_MODE*` masks can silently measure the wrong event, combine wrong lanes, or make profiling data incomparable across ASICs.
- Low/high performance counter reads can race counter updates. The header does not provide latching or read-order guarantees.
- `TCP_PERFCOUNTER_FILTER` has many narrow fields for shader-array, WGP, SIMD, VMID, slot, client, bank, request, and coherency selection. An off-by-one shift can make profiling look plausible while filtering an unintended workload or VMID.
- The range ends just after `SPI_PERFCOUNTER0_SELECT`; subsequent chunks own the remaining SPI select registers and other performance select families. Merge lanes should avoid claiming this chunk covers the full `gc_perfsdec` block.

## Test Signals

Useful validation should combine generated-data checks, build coverage, and hardware-oriented runtime signals:

- Build AMDGPU code that includes `gfxhub_v11_5_0.c` and the GC 11.5.0 register headers. Missing or renamed macros should surface at compile time.
- Mechanically compare this range against AMD's authoritative GC 11.5.0 register database. Each complete register in the range should have matching `__SHIFT` and `_MASK` entries.
- Cross-check every register family against `gc_11_5_0_offset.h` for matching `reg*` offsets and base indices, especially repeated RS64 aperture and performance counter families.
- Run static mask sanity checks: masks should align with shifts, full-width fields should use `0xFFFFFFFFL`, repeated aperture/control blocks should be structurally identical, and common performance select layouts should match across `CPG/CPC/CPF`, `GRBM`, `GE`, `PA`, and `SPI`.
- Exercise GPU init, reset, suspend/resume, and gfxhub fault-handling paths on GC 11.5.0 hardware. Relevant signals include successful cache setup, no unexpected protection faults, and clean reset recovery.
- Run cache/coherency stress tests that trigger GL1/GL2 invalidation, writeback, retry, and throttling behavior. Watch for stale data, VM faults, hangs, retry storms, or GL2/GL1 status errors.
- Run performance profiling that programs counters from the covered blocks, reads low/high data registers, and verifies expected event changes under controlled graphics, compute, memory, and shader workloads.
- Validate TCP performance counter filters using workloads isolated by VMID, shader array, WGP/SIMD, and request/coherency type. Expected signal is selective counter movement only for the configured filter.
- Compare register dumps from known-good GC 11.5.0 hardware or simulator traces against decoded values from these masks, focusing on CP RS64 state, GL1/GL2 status, and performance select registers.

## Cross-Chunk Notes

The previous chunk owns the beginning of the CP RS64 register definitions and includes the missing shift for the first field in this range. This chunk then completes the remaining RS64 GP/aperture/interrupt region, covers GL1/CH/GL2/GL1H cache-decode controls, covers performance counter data registers, and starts performance counter select registers through `SPI_PERFCOUNTER0_SELECT`. The next chunk should continue `gc_perfsdec` with the remaining SPI and later performance select fields. The final per-file research document should merge these artificial boundaries before describing the complete GC 11.5.0 shift/mask header.
