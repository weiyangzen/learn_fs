# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mmhub/mmhub_1_8_0_offset.h

Chunk: `subset-b-002772`
Lines researched: 1-2465 of `mmhub_1_8_0_offset.h`

## Purpose

This chunk is the first large-file chunk of the AMDGPU MMHUB 1.8.0 register offset header. It defines preprocessor constants for MMHUB register offsets and register-base indices used by the `mmhub_v1_8.c` driver code when programming memory-management hardware through SOC15 register access macros.

The file is generated-style hardware metadata, not executable driver logic. Each register has a `reg...` offset macro and a matching `reg..._BASE_IDX` macro. In this chunk, every visible `_BASE_IDX` value is `0`, meaning these registers are addressed through MMHUB base-index 0 for this IP version.

## Covered Register Blocks

The chunk includes the header guard and these address blocks:

| Lines | Address block | Base address | Main macro families |
| --- | --- | --- | --- |
| 28-287 | `aid_mmhub_dagb_dagbdec0` | `0x60000` | `regDAGB0_*` |
| 288-543 | `aid_mmhub_dagb_dagbdec1` | `0x60200` | `regDAGB1_*` |
| 544-795 | `aid_mmhub_dagb_dagbdec2` | `0x60400` | `regDAGB2_*` |
| 796-1047 | `aid_mmhub_dagb_dagbdec3` | `0x60600` | `regDAGB3_*` |
| 1048-1299 | `aid_mmhub_dagb_dagbdec4` | `0x60800` | `regDAGB4_*` |
| 1300-1525 | `aid_mmhub_ea_mmeadec0` | `0x60c00` | `regMMEA0_*` |
| 1526-1751 | `aid_mmhub_ea_mmeadec1` | `0x61100` | `regMMEA1_*` |
| 1752-1977 | `aid_mmhub_ea_mmeadec2` | `0x61600` | `regMMEA2_*` |
| 1978-2202 | `aid_mmhub_ea_mmeadec3` | `0x61b00` | `regMMEA3_*` |
| 2203-2427 | `aid_mmhub_ea_mmeadec4` | `0x62000` | `regMMEA4_*` |
| 2428-2465 | `aid_mmhub_pctldec0` | `0x62a00` | beginning of `regPCTL0_*` |

The chunk stops mid-`PCTL0`; later `PCTL0`, L1 TLB, UTCL2, and MM CANE definitions are in following chunks.

## Important APIs, Types, and Constants

There are no C functions, structs, enums, or runtime APIs in this chunk. The exported interface is the macro namespace consumed by AMDGPU MMHUB code:

- `regDAGB[0-4]_*`: five data aggregator block decoder instances. Each block exposes read-client registers (`RDCLI0` through `RDCLI15`), write-client registers (`WRCLI0` through `WRCLI15`), read/write control, GMI control, DAGB address/data path controls, virtual-channel controls, credit controls, pending-state registers, fatal-error controls/status, FIFO full/empty status, performance counters, and an L1TLB indirect access register.
- `regMMEA[0-4]_*`: five memory-management/effective-address decoder instances. These include DRAM, GMI, and IO client-to-group maps, group-to-VC maps, lazy timers, CAM controls, page/group burst settings, priority aging/queuing/fixed/urgency/quantum registers, SDP arbitration and reserve registers, latency sampling, perf counters, corrected/uncorrected error status, DSM controls, clock-gating, EDC, and miscellaneous control/status registers.
- `regPCTL0_*`: beginning of the power/control block. This chunk includes `regPCTL0_CTRL`, MMHUB deep-sleep override/ignore registers, and per-slice `DAGB_BUSY` and `DS_ALLOW` controls for slices 0-3.
- `*_BASE_IDX`: paired base-index constants used by SOC15 addressing helpers. In this chunk they are all `0`.

Representative offset ranges:

- `regDAGB0_RDCLI0` starts at `0x0000`; `regDAGB1_RDCLI0`, `regDAGB2_RDCLI0`, `regDAGB3_RDCLI0`, and `regDAGB4_RDCLI0` start at `0x0080`, `0x0100`, `0x0180`, and `0x0200`.
- `regMMEA0_DRAM_RD_CLI2GRP_MAP0` starts at `0x0300`; `regMMEA1`, `regMMEA2`, `regMMEA3`, and `regMMEA4` start at `0x0440`, `0x0580`, `0x06c0`, and `0x0800`.
- `regPCTL0_CTRL` starts at `0x0a80`; this chunk ends at `regPCTL0_SLICE3_CFG_DS_ALLOW_IB`.

## Control Flow

This header has no branches or executable control flow. Its effective control flow is compile-time macro substitution into callers. The most direct integration point is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/mmhub_v1_8.c`, which includes this file with `mmhub_1_8_0_sh_mask.h`.

Important visible use patterns from the consumer:

- `mmhub_v1_8_init_snoop_override_regs()` computes a stride as `regDAGB1_WRCLI_GPU_SNOOP_OVERRIDE - regDAGB0_WRCLI_GPU_SNOOP_OVERRIDE` and loops across five DAGB instances. This depends on the repeated DAGB offsets in this chunk being regularly spaced.
- The same function reads and writes `regDAGB0_WRCLI_GPU_SNOOP_OVERRIDE` and `regDAGB0_WRCLI_GPU_SNOOP_OVERRIDE_VALUE` with `RREG32_SOC15_OFFSET()` and `WREG32_SOC15_OFFSET()` to set the SDMA client snoop bit across DAGB instances.
- RAS tables in `mmhub_v1_8.c` reference `regMMEA[0-4]_CE_ERR_STATUS_LO/HI` and `regMMEA[0-4]_UE_ERR_STATUS_LO/HI` from this chunk through `AMDGPU_RAS_REG_ENTRY()`.
- Broader VM and cache setup in `mmhub_v1_8.c` uses the same offset-header pattern through `RREG32_SOC15()`, `WREG32_SOC15()`, `WREG32_SOC15_OFFSET()`, and `SOC15_REG_OFFSET()`.

## State and Persistence Behavior

The header does not own state and persists nothing. It describes hardware register locations that are used to read and write persistent device state while the GPU is initialized, configured, or monitored.

The state influenced by these constants includes:

- DAGB client arbitration, read/write path behavior, pending-state observation, FIFO/credit state, fatal-error status, performance-counter configuration, and snoop override state.
- MMEA memory path routing and arbitration for DRAM, GMI, and IO traffic, including priority, urgency masking, SDP reserves, latency sampling, EDC, corrected error, and uncorrected error status registers.
- PCTL deep-sleep and per-slice power-control gating state for the portion visible in this chunk.

Because the file only provides numeric offsets, persistence and reset semantics are determined by hardware and the runtime driver code that writes these registers.

## Dependencies

Compile-time dependencies are minimal:

- The header guard `_mmhub_1_8_0_OFFSET_HEADER` prevents duplicate inclusion.
- No other headers are included from this chunk.
- The meaningful dependency is on matching generated metadata in `mmhub_1_8_0_sh_mask.h`, which provides bit shifts and masks for fields in the same register set.
- Consumers depend on SOC15 register access infrastructure (`RREG32_SOC15`, `WREG32_SOC15`, `RREG32_SOC15_OFFSET`, `WREG32_SOC15_OFFSET`, `SOC15_REG_OFFSET`) to combine these offsets with MMHUB base addresses and instance indices.

The offsets are ASIC/IP-version-specific. Similar headers exist for other MMHUB versions, and some variants use different `_BASE_IDX` values, so these constants should not be shared across unrelated IP versions.

## Integration Points

- Direct include: `drivers/gpu/drm/amd/amdgpu/mmhub_v1_8.c`.
- Register programming: MMHUB VM/GART initialization, cache/TLB setup, fault handling, invalidation setup, snoop override programming, and disable paths use the same offset-header contract.
- RAS integration: `regMMEA[0-4]_CE_ERR_STATUS_*` and `regMMEA[0-4]_UE_ERR_STATUS_*` feed corrected and uncorrected MMHUB RAS error register lists.
- Multi-instance integration: `adev->aid_mask` loops in `mmhub_v1_8.c` select MMHUB instances, while this header supplies per-register offsets within each instance. DAGB and MMEA instance repetition inside the address map is represented by numbered macro prefixes.

## Risks and Edge Cases

- Offset accuracy is critical. A single wrong macro value can program or read a different hardware register, causing memory-management faults, incorrect RAS reporting, broken snoop behavior, bad power gating, or hangs during GART/MMHUB initialization.
- Repeated block spacing is an implicit contract. `mmhub_v1_8_init_snoop_override_regs()` relies on `regDAGB1_WRCLI_GPU_SNOOP_OVERRIDE - regDAGB0_WRCLI_GPU_SNOOP_OVERRIDE` matching all five DAGB instances. Non-uniform future hardware layout would require caller changes.
- The chunk boundary splits `PCTL0`. Any whole-file research or validation must merge later chunks before making complete statements about PCTL controls.
- Generated headers are easy to review poorly because they are large and repetitive. Useful review should compare against authoritative register XML/spec generation outputs or adjacent known-good MMHUB version headers.
- All visible `_BASE_IDX` values are `0`; if copied from another IP version with a different base index, register access macros can resolve to the wrong SOC15 base.

## Test Signals

Good signals that this chunk is correct:

- The tree compiles for AMDGPU targets that include `mmhub_v1_8.c`; missing or renamed macros would fail compile immediately.
- Boot/runtime logs on MMHUB 1.8 hardware show successful GART enablement, VM context setup, TLB/cache setup, and no early MMHUB access faults.
- VM fault tests and GPU memory stress paths do not show unexpected MMHUB fault status or invalidation failures.
- RAS injection or error-status polling, where available, maps MMEA0-4 corrected and uncorrected error status to the expected registers.
- Snoop override behavior for SDMA writes remains stable; regressions would likely appear as cache coherency issues in SDMA write-heavy workloads.
- Register dumps from hardware match the expected block layout: DAGB blocks at offsets `0x0000`, `0x0080`, `0x0100`, `0x0180`, `0x0200`; MMEA blocks at `0x0300`, `0x0440`, `0x0580`, `0x06c0`, `0x0800`; and PCTL beginning at `0x0a80`.

## Cross-Chunk Notes

This is not the full file. Later chunks must cover the remainder of `aid_mmhub_pctldec0`, L1TLB, UTCL2, shared VM/TLB blocks, performance-counter control blocks, and MM CANE definitions before producing the final source-tree-aligned per-file research document.
