# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mmhub/mmhub_1_7_offset.h lines 1-2457

## Scope

This chunk covers the first 2,457 lines of the generated-style AMD MMHUB 1.7 register offset header. It contains the AMD license, an include guard, and 2,400 `#define` symbols for MMHUB register offsets and their `_BASE_IDX` values.

The range is entirely preprocessor metadata. There are no functions, structs, enums, includes, variables, allocations, locks, loops, callbacks, or runtime branches. Although the source tree path is under a `ceph-client` mirror, this file is AMDGPU DRM hardware register metadata, not Ceph filesystem logic.

The chunk contains these address blocks:

- `mmhub_dagb_dagbdec0` through `mmhub_dagb_dagbdec5`, base addresses `0x68000` through `0x68a00`.
- `mmhub_ea_mmeadec0`, base address `0x68c00`.
- Most of `mmhub_ea_mmeadec1`, base address `0x69100`.

The selected range ends at `regMMEA1_ADDRDEC_SELECT_BASE_IDX` on line 2457. The immediately following lines define `regMMEA1_EDC_CNT3`, `regMMEA1_MISC_AON`, and then begin `mmhub_ea_mmeadec2`, so full-file research must reconcile this chunk with later chunks before treating the MMEA1 and MMEA2+ domains as complete.

## Purpose

`mmhub_1_7_offset.h` provides symbolic register-offset names for AMDGPU's MMHUB 1.7 IP block. Driver code uses these names with SOC15 register access helpers such as `RREG32_SOC15`, `WREG32_SOC15`, `RREG32_SOC15_OFFSET`, `WREG32_SOC15_OFFSET`, `SOC15_REG_ENTRY`, and `SOC15_REG_OFFSET` to compute MMIO addresses without hard-coding raw offsets at call sites.

The `DAGB` blocks describe duplicated data/address gateway decode instances. Each instance exposes read and write client registers, request/return path controls, virtual-channel controls, credit counters, pending-state registers, snoop override registers, fatal-error status/clear registers, FIFO fullness/emptiness status, performance-counter registers, and reserve slots.

The `MMEA` blocks describe MMHUB external-address/address-decoder instances. They expose DRAM/GMI/IO client-to-group maps, group-to-virtual-channel maps, lazy timers, CAM/page-burst controls, priority/urgency registers, address-normalization base/limit/offset/mega-region registers, address-decoder chip-select and row/column/rank-selection registers, SDP arbitration/priority/credit registers, latency/performance counters, EDC counters, DSM controls, clock-gating controls, error status, and address-decoder selection.

## Important APIs, Types, And Constants

The exported interface is entirely compile-time constants:

- Register names use the `reg<block>_<register>` pattern and map to MMHUB register offsets, not byte addresses. SOC15 helpers combine these offsets with the MMHUB IP base/index metadata.
- Every register offset in this chunk is paired with a `<name>_BASE_IDX` definition. All base indexes in this range are `0`, which ties these symbols to MMHUB base index 0 for this IP version.
- The six complete `DAGB` instances each contribute 128 register-offset defines and 128 base-index defines. Their offset windows are regular: `DAGB0` starts at `0x0000`, `DAGB1` at `0x0080`, through `DAGB5` at `0x0280`.
- Important `DAGB` families include `RDCLI0..15`, `WRCLI0..15`, `RD_CNTL`, `WR_CNTL`, `RD_GMI_CNTL`, `WR_GMI_CNTL`, `RD_ADDR_DAGB`, `WR_ADDR_DAGB`, `WR_DATA_DAGB`, `*_MAX_BURST*`, `*_LAZY_TIMER*`, `RD_VC0..7_CNTL`, `WR_VC0..7_CNTL`, `*_TLB_CREDIT`, `*_CREDIT_CNTL`, `*_PENDING`, `WRCLI_GPU_SNOOP_OVERRIDE`, `FATAL_ERROR_*`, `FIFO_*`, `PERFCOUNTER_*`, and `L1TLB_REG_RW`.
- `MMEA0` contributes a complete address-decoder block in this chunk, from `regMMEA0_DRAM_RD_CLI2GRP_MAP0` at `0x0300` through `regMMEA0_MISC_AON` at `0x0415`.
- `MMEA1` contributes most of the next address-decoder block, from `regMMEA1_DRAM_RD_CLI2GRP_MAP0` at `0x0440` through `regMMEA1_ADDRDEC_SELECT` at `0x0553`. The chunk omits the following `MMEA1_EDC_CNT3` and `MMEA1_MISC_AON` definitions.
- Important `MMEA` families include DRAM/GMI/IO `*_CLI2GRP_MAP*`, `*_GRP2VC_MAP`, `*_LAZY`, `*_CAM_CNTL`, priority age/queue/fixed/urgency/quantum registers, `ADDRNORM_*`, `ADDRDEC*_*`, `SDP_*`, `PERFCOUNTER_*`, `EDC_CNT*`, `DSM_CNTL*`, `CGTT_CLK_CTRL`, `EDC_MODE`, `ERR_STATUS`, `MISC*`, and `ADDRDEC_SELECT`.

## Control Flow

This header has no direct control flow. The implied driver flow is:

1. `mmhub_v1_7.c` includes this offset header and `mmhub_1_7_sh_mask.h`.
2. MMHUB setup, power-management, RAS, and diagnostic code chooses symbolic register names from this header.
3. SOC15 register macros combine the selected offset with MMHUB IP-instance/base-index metadata.
4. Driver code reads, writes, polls, or records the resulting MMIO register address.

Concrete consumers in `mmhub_v1_7.c` include:

- Snoop override initialization computes the distance between `regDAGB1_WRCLI_GPU_SNOOP_OVERRIDE` and `regDAGB0_WRCLI_GPU_SNOOP_OVERRIDE`, then iterates DAGB instances with `RREG32_SOC15_OFFSET`/`WREG32_SOC15_OFFSET`.
- Medium-grain clock gating reads and updates `regDAGB0_CNTL_MISC2` and `regDAGB1_CNTL_MISC2` using bit masks from the companion shift/mask header.
- RAS field tables use `regMMEA0_EDC_CNT`, `regMMEA0_EDC_CNT2`, `regMMEA0_EDC_CNT3`, `regMMEA1_EDC_CNT`, `regMMEA1_EDC_CNT2`, `regMMEA1_EDC_CNT3`, and related `ERR_STATUS` registers to query and reset MMHUB error counters.

All sequencing, error handling, locking, and hardware state transitions live in the C driver and MMIO helper layers, not in this header.

## State And Persistence Behavior

The file itself is stateless and persistent only as source metadata. Its constants describe hardware state locations.

When surrounding AMDGPU code writes DAGB registers, state can persist in the MMHUB until reset, power-gated, or explicitly reprogrammed. Examples include snoop override bits, clock-gating controls, read/write path controls, virtual-channel controls, credit settings, and fatal-error clear/status behavior.

MMEA address-normalization and address-decoder registers define how physical address ranges, DRAM/GMI/IO routing, chip-select mapping, rank/row/column selection, harvesting, holes, and non-power-of-two channel behavior are interpreted. Wrong persisted values can route memory traffic incorrectly or make diagnostic counters point at the wrong memory path.

MMEA EDC and error-status registers are diagnostic state. `mmhub_v1_7.c` reads EDC counters for correctable/uncorrectable error reporting and resets the counters by writing zero when MMHUB RAS is supported. The counters are not owned by this header, but the offsets here decide which hardware counters the driver reads or clears.

Performance-counter registers in the DAGB and MMEA blocks are dynamic hardware observations controlled by adjacent `PERFCOUNTER*_CFG` and result-control registers. Incorrect offsets can produce plausible-looking but wrong performance data.

## Dependencies And Integration Points

This header depends on the MMHUB 1.7 register database remaining synchronized with the companion `mmhub_1_7_sh_mask.h` field definitions and the SOC15 MMHUB IP-base table. The constants are meaningful only when used with matching MMHUB 1.7 hardware.

Key integration points are:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/mmhub_v1_7.c`, which includes this header directly and uses these symbols for MMHUB initialization, cache/TLB setup, DAGB snoop override, clock gating, RAS/EDC counter reporting, and error-status reads.
- SOC15 register helper macros that translate `reg...` offsets and `_BASE_IDX` data into actual MMIO addresses.
- The companion shift/mask header, which provides bit positions and masks for the registers named here.
- AMDGPU GMC/VM code, because MMHUB register programming affects GPU virtual memory apertures, page-table access, protection-fault handling, memory routing, and cache/TLB behavior.
- AMDGPU RAS code, because the `MMEA*_EDC_CNT*` and `MMEA*_ERR_STATUS` offsets feed correctable/uncorrectable error accounting.
- Power-management and clock-gating paths, because `DAGB*_CNTL_MISC2`, `MMEA*_CGTT_CLK_CTRL`, and related registers participate in MMHUB gating behavior.

The chunk also has cross-version coupling by naming convention. Other MMHUB versions carry similarly named `regDAGB*` and `regMMEA*` symbols with different offsets or base indexes, so include selection must match the active IP version.

## Risks And Edge Cases

- Generated-header drift is the main risk. A wrong offset or stale `_BASE_IDX` compiles successfully but makes the driver read or write the wrong MMHUB register.
- The `DAGB` windows are regular, and driver code relies on offset deltas between instances. If a later ASIC revision breaks spacing but code still computes instance offsets from `DAGB1 - DAGB0`, snoop override or diagnostics could target the wrong instance.
- The chunk boundary is inside `MMEA1`. Research or validation based only on this chunk must not assume MMEA1 is complete, because `EDC_CNT3` and `MISC_AON` appear immediately after line 2457.
- All symbols are preprocessor macros in the global namespace. Including multiple generated headers for different MMHUB versions in one C translation unit can create name collisions or accidental version mixing.
- RAS paths are sensitive to offset accuracy. A wrong `MMEA*_EDC_CNT*` or `ERR_STATUS` offset can undercount, overcount, misattribute, or incorrectly clear memory error telemetry.
- Address-normalization and address-decoder registers are hardware-routing controls. Misprogramming them can cause memory corruption, VM faults, bad GMI/DRAM/IO routing, or failures that look like unrelated GPU hangs.
- Pending, FIFO, credit, and fatal-error status registers are often used for debug and recovery. Bad definitions can hide real deadlocks or make recovery code diagnose the wrong sub-block.
- `_BASE_IDX` values are all zero in this chunk; accidentally copying definitions from a different MMHUB version with a different base index would silently change SOC15 address calculation.

## Test Signals

Useful validation signals include:

- AMDGPU kernel build coverage for `mmhub_v1_7.c` with this header and `mmhub_1_7_sh_mask.h`.
- Mechanical comparison against AMD's authoritative MMHUB 1.7 register database for every offset and `_BASE_IDX` in lines 1-2457.
- Static checks that repeated `DAGB0..5` windows have the expected stride and identical register families where the hardware database says they should.
- Cross-checks that every `reg...` symbol used by `mmhub_v1_7.c` is defined by the matching MMHUB 1.7 offset header, and every `SOC15_REG_FIELD` use has a matching shift/mask definition.
- Boot and initialization tests on MMHUB 1.7 hardware, especially VM/GART setup, page-table access, TLB/cache initialization, and protection-fault default-address behavior.
- Snoop override validation for SDMA writes, because `mmhub_v1_7_init_snoop_override_regs()` depends on the DAGB instance spacing and the `WRCLI_GPU_SNOOP_OVERRIDE` offsets.
- Clock-gating tests that toggle medium-grain clock gating and light sleep, then verify no MMHUB access failures, hangs, or incorrect gating-state reporting.
- RAS tests or fault-injection runs that exercise `MMEA0` and `MMEA1` EDC counters and `ERR_STATUS` registers, checking that correctable and uncorrectable counts are attributed to the expected sub-blocks.
- Performance-counter smoke tests for DAGB and MMEA counters under targeted memory traffic, looking for nonzero and plausible counter movement.
- Runtime warning signs include GPU VM faults during normal memory traffic, failed GART/VRAM aperture setup, SDMA coherency issues, unexpected MMHUB RAS counts, unchanging performance counters, bad error-status attribution, or GPU hangs around MMHUB clock-gating transitions.

## Cross-Chunk Notes

This is only the chunk research document for `subset-b-002755`. It covers lines 1-2457 of `mmhub_1_7_offset.h`. The final per-file research should merge this with later chunks to complete the remaining `MMEA1` tail, `MMEA2+` address-decoder blocks, VM/L2/ATC/MC registers, and the closing include guard.
