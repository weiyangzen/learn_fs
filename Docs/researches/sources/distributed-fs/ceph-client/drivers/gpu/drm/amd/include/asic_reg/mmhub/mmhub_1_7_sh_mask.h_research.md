# Research: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mmhub/mmhub_1_7_sh_mask.h

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-002758`: lines 1-2364, `Docs/researches/chunks/subset-b-002758_research.md`
- `subset-b-002759`: lines 2365-4717, `Docs/researches/chunks/subset-b-002759_research.md`
- `subset-b-002760`: lines 4718-7076, `Docs/researches/chunks/subset-b-002760_research.md`
- `subset-b-002761`: lines 7077-9435, `Docs/researches/chunks/subset-b-002761_research.md`
- `subset-b-002762`: lines 9436-11789, `Docs/researches/chunks/subset-b-002762_research.md`
- `subset-b-002763`: lines 11790-14143, `Docs/researches/chunks/subset-b-002763_research.md`
- `subset-b-002764`: lines 14144-16497, `Docs/researches/chunks/subset-b-002764_research.md`
- `subset-b-002765`: lines 16498-18857, `Docs/researches/chunks/subset-b-002765_research.md`
- `subset-b-002766`: lines 18858-21209, `Docs/researches/chunks/subset-b-002766_research.md`
- `subset-b-002767`: lines 21210-23545, `Docs/researches/chunks/subset-b-002767_research.md`
- `subset-b-002768`: lines 23546-25902, `Docs/researches/chunks/subset-b-002768_research.md`
- `subset-b-002769`: lines 25903-28256, `Docs/researches/chunks/subset-b-002769_research.md`
- `subset-b-002770`: lines 28257-30631, `Docs/researches/chunks/subset-b-002770_research.md`
- `subset-b-002771`: lines 30632-32178, `Docs/researches/chunks/subset-b-002771_research.md`

## Chunk Research

### subset-b-002758: lines 1-2364

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mmhub/mmhub_1_7_sh_mask.h lines 1-2364

## Purpose

This chunk is the opening portion of the generated AMDGPU MMHUB 1.7 register field mask header. It provides preprocessor constants for MMHUB DAGB decoder register fields: every field is represented by a `<REGISTER>__<FIELD>__SHIFT` macro and a matching `<REGISTER>__<FIELD>_MASK` macro. The companion `mmhub_1_7_offset.h` file provides the register addresses; this file provides the bit layout needed to build, decode, and read-modify-write 32-bit register values.

The range covers the license/header guard, all of `addressBlock: mmhub_dagb_dagbdec0`, and the start of `addressBlock: mmhub_dagb_dagbdec1` through `DAGB1_RD_VC1_CNTL`. The definitions are hardware contract data for the MMHUB memory path, not executable driver logic.

## Major Register Families Covered

- `DAGB0_RDCLI0` through `DAGB0_RDCLI15`: per-read-client routing and throttling fields. Each client has `VIRT_CHAN`, `CHECK_TLB_CREDIT`, `URG_HIGH`, `URG_LOW`, `MAX_BW_ENABLE`, `MAX_BW`, `MIN_BW_ENABLE`, `MIN_BW`, `OSD_LIMITER_ENABLE`, and `MAX_OSD` fields.
- `DAGB0_RD_CNTL`, `DAGB0_RD_GMI_CNTL`, and `DAGB0_RD_ADDR_DAGB`: global read-side controls for clock/window sizing, IO level overrides, virtual-channel sharing, GMI credits/level/burst/timer fields, and address DAGB enable/jump/self-init/identity mode.
- `DAGB0_RD_OUTPUT_DAGB_*`, `DAGB0_RD_ADDR_DAGB_*`, and `DAGB0_RD_VC0_CNTL` through `DAGB0_RD_VC7_CNTL`: read output and address arbitration controls. These define per-VC max burst/lazy timer nibbles, per-client burst/timer tables for clients 0-15, and per-VC storage/EA credits plus max/min bandwidth and outstanding-request limits.
- `DAGB0_RD_CNTL_MISC`, `DAGB0_RD_TLB_CREDIT`, `DAGB0_RD_RDRET_CREDIT_CNTL`, and `DAGB0_RD_RDRET_CREDIT_CNTL2`: read-side pool credit, IO/EA credit, UTCL2 client ID, return FIFO credit, per-TLB credit, and read-return credit controls.
- `DAGB0_RDCLI_*_PENDING`: read-client status bitmaps for `ASK`, `GO`, `GBLSEND`, `TLB`, `OARB`, and `OSD` pending states.
- `DAGB0_WRCLI0` through `DAGB0_WRCLI15`: write-client mirrors of the read-client routing and throttling fields with the same virtual-channel, TLB-credit, urgency, bandwidth, and OSD-limit layout.
- `DAGB0_WR_CNTL`, `DAGB0_WR_GMI_CNTL`, `DAGB0_WR_ADDR_DAGB`, `DAGB0_WR_DATA_DAGB`, and related max-burst/lazy-timer tables: write-side global controls for address and data DAGB arbitration, per-client burst/timer limits, and per-VC write credits.
- `DAGB0_WR_CNTL_MISC`, `DAGB0_WR_TLB_CREDIT`, `DAGB0_WR_DATA_CREDIT`, `DAGB0_WR_MISC_CREDIT`, `DAGB0_WR_OSD_CREDIT_CNTL*`, and `DAGB0_WR_ATOMIC_FIFO_CREDIT_CNTL1`: write-side pool, TLB, data burst, OSD, deadlock-VC, and atomic FIFO credit fields.
- `DAGB0_WRCLI_GPU_SNOOP_OVERRIDE`, `DAGB0_WRCLI_GPU_SNOOP_OVERRIDE_VALUE`, and `DAGB0_WRCLI_*_PENDING`: write-client snoop override bitmaps and pending-state bitmaps for write request progress, including data-bus ask/go pending states.
- `DAGB0_DAGB_DLY`, `DAGB0_CNTL_MISC`, and `DAGB0_CNTL_MISC2`: top-level DAGB delay, EA virtual-channel remap, bandwidth initialization/gap timing, urgent boost/halt, clock-gating disable, busy-signal disable, swap control, HDP client ID, and read-return deadlock FIFO credit fields.
- `DAGB0_FATAL_ERROR_*`: fatal-error filter, clear, and status capture fields. Status fields expose validity, client ID, low/high address bits, tag, VFID/VF, address space, IO, size, FED, operation, TMZ, snoop, invalid, NACK, read-only, memory log, and EOP state.
- `DAGB0_FIFO_EMPTY`, `DAGB0_FIFO_FULL`, `DAGB0_WR_CREDITS_FULL`, and `DAGB0_RD_CREDITS_FULL`: broad status bitmaps for FIFO and credit saturation.
- `DAGB0_PERFCOUNTER_*`: low/high counter results, compare value, three performance counter configuration registers, and result-control fields for selection, triggers, enable, clear, and stop-on-saturate behavior.
- `DAGB0_L1TLB_REG_RW` and `DAGB0_RESERVE1` through `DAGB0_RESERVE4`: L1 TLB register read/write and exception/parity/check controls plus reserved full-width registers.
- `DAGB1_RDCLI0` through `DAGB1_RDCLI15`, `DAGB1_RD_CNTL`, `DAGB1_RD_GMI_CNTL`, `DAGB1_RD_ADDR_DAGB`, read output/address DAGB burst/timer tables, and `DAGB1_RD_VC0_CNTL` through the start of `DAGB1_RD_VC1_CNTL`: the beginning of the second DAGB decoder instance, using the same read-side field layout as `DAGB0`.

## Important APIs, Types, and Functions

This header defines no C functions, structs, enums, or variables. Its API surface is the macro namespace:

- `*_MASK` constants isolate bit fields in 32-bit MMHUB registers.
- `*__SHIFT` constants define the bit position for packing caller-provided field values or unpacking hardware register reads.
- `DAGB0_*` and `DAGB1_*` prefixes identify separate DAGB decoder instances; callers must pair them with the matching `regDAGB0_*` or `regDAGB1_*` offsets from `mmhub_1_7_offset.h`.

Typical AMDGPU use is through register helpers such as `RREG32`, `WREG32`, or field helper macros that combine an offset macro, the `*_MASK`, and the `*__SHIFT`. Because these are untyped preprocessor definitions, the compiler cannot prevent mixing a mask from the wrong MMHUB generation or DAGB instance.

## Control Flow

There is no runtime control flow in this file. Including the header only exposes constants under `_mmhub_1_7_SH_MASK_HEADER`. Runtime behavior is created in downstream driver code that uses these constants to program hardware registers.

The implied register manipulation flow is:

1. Select an MMHUB 1.7 register offset, usually from `mmhub_1_7_offset.h`.
2. Read the current register value when preserving unrelated fields.
3. Clear a field with the corresponding `*_MASK`.
4. Shift the new value by `*__SHIFT`, mask it, and OR it into the register value.
5. Write the result back to the MMHUB register.

Status decoding reverses that flow: read the register, mask the field, shift it down, then interpret the value as a bitmap, client ID, address fragment, credit count, pending flag, or performance/debug state.

## State and Persistence Behavior

The header has no mutable state and persists no data. The constants describe MMHUB hardware state that exists in GPU registers while the device is powered and initialized.

Many fields configure long-lived routing and arbitration state: virtual-channel assignment, urgency thresholds, bandwidth windows, min/max bandwidth enforcement, outstanding-request limits, storage/EA/TLB credits, per-client burst sizes, lazy timers, GMI controls, virtual-channel remapping, and clock-gating behavior. Other fields expose transient state such as pending client requests, FIFO empty/full state, credit fullness, performance counters, and fatal-error captures. Clear/control fields such as `DAGB0_FATAL_ERROR_CLEAR__CLEAR`, performance counter `CLEAR`, and result-control `CLEAR_ALL` represent hardware side effects; the header does not encode whether bits are sticky, self-clearing, write-one-to-clear, or read-only.

## Dependencies and Integration Points

- Depends only on C preprocessing and include guard discipline.
- Integrates directly with `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mmhub/mmhub_1_7_offset.h`, whose `regDAGB0_*` and `regDAGB1_*` address macros correspond to these field macros.
- Integrates with AMDGPU MMHUB/GMC/VM initialization, memory-translation, bandwidth/credit programming, fault diagnostics, and performance/debug paths for ASICs using the MMHUB 1.7 register map.
- Names such as `L1TLB`, `ATCVM`, `UTCL2`, `HDP_CID`, `VFID`, `VF`, `TMZ`, `GMI`, `OSD`, and `GPU_SNOOP` show integration with GPU virtual memory, IOMMU/address translation, host data path, virtualization/SRIOV state, encrypted memory modes, interconnect traffic, outstanding request tracking, and snoop behavior.
- The repeated `DAGB0`/`DAGB1` layout means code can often share programming tables or loops, but offsets and available fields still need to match the exact ASIC generation.

## Risks and Edge Cases

- A mask/shift mismatch can silently program the wrong hardware bits, affecting GPU memory routing, TLB credit flow, bandwidth throttling, or fatal-error reporting.
- `DAGB0` and `DAGB1` are structurally similar. Copying a field macro across instances without also changing the register offset can target the wrong decoder.
- Read-side, write-address, and write-data DAGB tables look similar but are not interchangeable; using an address-path mask for data-path programming can misconfigure client arbitration.
- Several fields are compact encoded values rather than raw units. Examples include address fragments in fatal-error status registers, virtual-channel IDs, credit counts, bandwidth windows, max burst nibbles, and lazy timer nibbles.
- Status and control fields live in the same macro namespace. Callers must know from hardware documentation which registers are read-only, write-only, sticky, clear-on-write, or self-clearing.
- Reserved full-width registers and `RESERVE` fields should not be treated as safe scratch space. Writing non-reset values to reserved bits can cause undefined hardware behavior.
- This chunk ends mid-`DAGB1` read-control family at `DAGB1_RD_VC1_CNTL`; later chunks must cover the rest of `DAGB1` before final per-file conclusions are reconciled.

## Test Signals

- Build coverage: include regressions, misspelled macros, or duplicated/missing definitions should surface as AMDGPU compile errors.
- Generated-header validation: compare masks and shifts against AMD register source data or adjacent MMHUB 1.7 offset/default headers before accepting edits.
- Hardware smoke signals: GPU bring-up, VM setup, TLB behavior, SDMA or graphics memory traffic, display scanout under memory pressure, suspend/resume, and SRIOV/VF paths indirectly exercise these fields.
- Runtime debug signals: pending bitmaps, FIFO empty/full status, credit-full registers, fatal-error status registers, and DAGB performance counters can confirm that field decoding matches hardware behavior.
- Negative signals: memory faults after VM/MMHUB init, hangs in memory traffic, unexpected fatal-error captures, stuck pending bits, saturated credit-full bits, broken performance counter reads, or bandwidth/latency anomalies suggest either a bad field definition or a caller using the wrong field/register pairing.

### subset-b-002759: lines 2365-4717

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mmhub/mmhub_1_7_sh_mask.h lines 2365-4717

## Scope

This chunk is the second generated slice of the AMD MMHUB 1.7 shift/mask header. It begins in the middle of the `DAGB1_RD_VC1_CNTL` field list and ends in the middle of the `DAGB2_WR_OUTPUT_DAGB_LAZY_TIMER` family. The covered range contains 2,353 preprocessor definitions for 165 DAGB register names. It is hardware metadata only: no functions, structs, storage, locks, allocation, or direct MMIO access live in this header.

The register families covered here are:

- Tail of `DAGB1_RD_VC1_CNTL`, then complete `DAGB1_RD_VC2_CNTL` through `DAGB1_RD_VC7_CNTL` read virtual-channel credit/bandwidth/OSD limiter fields.
- `DAGB1_RD_CNTL_MISC`, `DAGB1_RD_TLB_CREDIT`, `DAGB1_RD_RDRET_CREDIT_CNTL`, and `DAGB1_RD_RDRET_CREDIT_CNTL2` read-side shared credit, return-credit, CID, and FIFO-credit controls.
- `DAGB1_RDCLI_*_PENDING` busy masks for ask/go/global-send/TLB/output-arbiter/OSD read-client pipelines.
- `DAGB1_WRCLI0` through `DAGB1_WRCLI15` write-client routing, TLB-credit checking, urgency, bandwidth, and outstanding-request limiter fields.
- `DAGB1_WR_CNTL`, `DAGB1_WR_GMI_CNTL`, `DAGB1_WR_ADDR_DAGB`, output/address/data DAGB burst and lazy-timer controls, clock-gating test/threshold controls, write virtual-channel controls, write-side TLB/data/misc/OSD/atomic FIFO credits, snoop override masks, write-client pending masks, DAGB delay, miscellaneous DAGB controls, fatal-error controls/status, FIFO/credit fullness, performance counters, L1 TLB register read/write window, and reserve registers.
- The `mmhub_dagb_dagbdec2` address block starts at line 3601. This chunk then covers `DAGB2_RDCLI0` through `DAGB2_RDCLI15`, read-side DAGB2 controls, `DAGB2_RD_VC0` through `DAGB2_RD_VC7`, read credit and pending masks, `DAGB2_WRCLI0` through `DAGB2_WRCLI15`, `DAGB2_WR_CNTL`, `DAGB2_WR_GMI_CNTL`, `DAGB2_WR_ADDR_DAGB`, and the start of `DAGB2_WR_OUTPUT_DAGB_MAX_BURST` / `DAGB2_WR_OUTPUT_DAGB_LAZY_TIMER`.

Although the repository path is under `distributed-fs/ceph-client`, this file is AMDGPU hardware register metadata, not Ceph filesystem code.

## Purpose

The purpose of this chunk is to define bit positions and bit masks for MMHUB data-arbitration/global-buffer (`DAGB`) registers on MMHUB 1.7 hardware. Consumers pair these macros with register offsets from `mmhub_1_7_offset.h` and AMDGPU helper macros such as `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, `RREG32_SOC15_OFFSET`, `WREG32_SOC15_OFFSET`, and `SOC15_REG_GOLDEN_VALUE`.

Each field normally appears as:

- `<REGISTER>__<FIELD>__SHIFT`, the least-significant bit position.
- `<REGISTER>__<FIELD>_MASK`, the 32-bit mask for isolating or composing the field.

The fields describe MMHUB client arbitration and memory-system behavior: virtual-channel assignment, TLB-credit gating, read/write urgency, maximum/minimum bandwidth windows, outstanding request limits, storage/EA/GMI credits, return FIFO credits, clock-gating thresholds, snoop overrides, fatal-error reporting, FIFO fullness, performance counter selection, and indirect L1 TLB register access.

## Important Macro Families

The `DAGB*_RDCLI*` and `DAGB*_WRCLI*` client controls share a regular layout. `VIRT_CHAN` selects the client virtual channel, `CHECK_TLB_CREDIT` enables TLB credit enforcement, `URG_HIGH` and `URG_LOW` configure urgency thresholds, `MAX_BW_ENABLE`/`MAX_BW` and `MIN_BW_ENABLE`/`MIN_BW` control bandwidth limiting, and `OSD_LIMITER_ENABLE`/`MAX_OSD` gate outstanding demand. DAGB1 write clients and DAGB2 read/write clients each expose 16 client slots in this chunk.

The `DAGB*_RD_VC*` and `DAGB1_WR_VC*` virtual-channel controls define per-VC storage and EA credits plus maximum/minimum bandwidth and OSD limiter fields. DAGB1 read VC0 starts in the previous chunk; this chunk completes VC1 and covers VC2 through VC7. DAGB1 write and DAGB2 read VC0 through VC7 are complete in this range.

Credit-control macros include `DAGB*_RD_TLB_CREDIT`, `DAGB1_WR_TLB_CREDIT`, `DAGB1_WR_DATA_CREDIT`, `DAGB1_WR_MISC_CREDIT`, `DAGB1_WR_OSD_CREDIT_CNTL*`, `DAGB1_WR_ATOMIC_FIFO_CREDIT_CNTL1`, and `DAGB*_RD_RDRET_CREDIT_CNTL*`. These fields partition finite MMHUB internal resources across TLBs, virtual channels, IO/GMI/pool return paths, OSD queues, atomic return paths, data DAGBs, and miscellaneous write paths.

Clock-gating and delay fields are represented by `DAGB1_WR_CGTT_CLK_CTRL`, `DAGB1_L1TLB_WR_CGTT_CLK_CTRL`, `DAGB1_ATCVM_WR_CGTT_CLK_CTRL`, `DAGB2_RD_CGTT_CLK_CTRL`, `DAGB2_L1TLB_RD_CGTT_CLK_CTRL`, and `DAGB2_ATCVM_RD_CGTT_CLK_CTRL`. These expose disable, delay, ready-threshold, misc-threshold, register-id, and SOFT_OVERRIDE bits used by low-level power/clock gating policy or diagnostics.

`DAGB1_WRCLI_GPU_SNOOP_OVERRIDE` and `DAGB1_WRCLI_GPU_SNOOP_OVERRIDE_VALUE` are high-signal integration fields. `mmhub_v1_7_init_snoop_override_regs()` computes the distance between DAGB instances using `regDAGB1_WRCLI_GPU_SNOOP_OVERRIDE - regDAGB0_WRCLI_GPU_SNOOP_OVERRIDE`, then sets bit 15 in the override and value registers so SDMA writes probe-invalidate RW cache lines. The v1.8 implementation uses the same pattern across active AID/MMHUB instances.

Status and diagnostic fields include `DAGB*_RDCLI_*_PENDING`, `DAGB1_WRCLI_*_PENDING`, `DAGB1_FIFO_EMPTY`, `DAGB1_FIFO_FULL`, `DAGB1_WR_CREDITS_FULL`, `DAGB1_RD_CREDITS_FULL`, and `DAGB1_L1TLB_REG_RW`. The pending/full/empty masks are mostly full-width bitmaps or compact fullness bitmaps, while the L1 TLB register window exposes write data, read data, address, write enable, read enable, and status fields for indirect access.

Fatal-error fields are grouped under `DAGB1_FATAL_ERROR_CNTL`, `DAGB1_FATAL_ERROR_CLEAR`, and `DAGB1_FATAL_ERROR_STATUS0` through `STATUS3`. These define enables, clear bits, error decode fields, block IDs, interrupt source IDs, client IDs, virtual channel, MC ID, region, RW bit, ATC status, SDP packet fields, VMID, and client status. They are RAS/diagnostic-facing and should be treated as hardware-owned sticky or latched error state unless the consuming code explicitly clears them.

Performance counter fields include `DAGB1_PERFCOUNTER_LO`, `DAGB1_PERFCOUNTER_HI`, `DAGB1_PERFCOUNTER0_CFG` through `DAGB1_PERFCOUNTER2_CFG`, and `DAGB1_PERFCOUNTER_RSLT_CNTL`. These provide counter data, compare value, event selector ranges, mode, enable, clear, start/stop triggers, enable-any, clear-all, and stop-on-saturate behavior.

## Control Flow

This header has no runtime control flow. It influences code only through the C preprocessor.

Typical consumer flow is:

1. MMHUB code includes `mmhub/mmhub_1_7_offset.h` and `mmhub/mmhub_1_7_sh_mask.h`.
2. Code reads a register through `RREG32_SOC15*`, modifies fields with `REG_SET_FIELD` or explicit bit masks, and writes it back with `WREG32_SOC15*`.
3. For repeated DAGB instances, code may use offset arithmetic with `*_OFFSET` helpers. The snoop override setup is the clearest example: it computes a DAGB-instance stride from adjacent register offsets, then applies the same SDMA snoop override field to each DAGB instance.
4. Golden-setting tables can apply fixed mask/value programming. In `gmc_v9_0.c`, `SOC15_REG_GOLDEN_VALUE(MMHUB, 0, mmDAGB1_WRCLI2, 0x00000007, 0xfe5fe0fa)` programs the virtual-channel field of a DAGB1 write client in older MMHUB setup data.

The shift/mask file does not encode sequencing, polling, write-one-to-clear rules, reset ownership, RAS interrupt routing, or safe read/write policy. Those rules are in the consuming AMDGPU code, firmware contracts, and the hardware register specification.

## State And Persistence Behavior

No software state is stored by this file. The macros describe hardware state in MMHUB DAGB registers.

Persistent-until-reset or reprogrammed state includes client virtual-channel assignment, TLB-credit enforcement, urgency thresholds, bandwidth limiters, OSD limits, GMI/EA/storage credit pools, clock-gating thresholds, DAGB enable/jump settings, max-burst and lazy-timer values, snoop override masks and values, and some performance counter configuration.

Live or transient state includes pending client bitmaps, FIFO empty/full state, credit-full state, performance counter low/high values, indirect L1 TLB read status, and parts of fatal-error status. These fields can change with memory traffic, VM faults, SDMA writes, GMI traffic, cache/TLB pressure, power-gating state, or RAS events.

Some fields are command-like or destructive when written: fatal-error clear, performance counter clear/clear-all, performance counter trigger controls, indirect L1 TLB read/write enables, and clock-gating overrides. The header does not distinguish safe observation from action-triggering writes.

## Dependencies

This chunk depends on the generated AMD register-header convention:

- `mmhub_1_7_offset.h` supplies `reg*` and `mm*` register addresses for the DAGB names defined here.
- Other chunks of `mmhub_1_7_sh_mask.h` complete the same hardware namespace. This chunk starts and ends mid-family, so the adjacent chunks are required for a full per-file report.
- `mmhub_1_7.c` includes this file for MMHUB 1.7 GART, TLB, cache, VM context, invalidation, RAS, and snoop override programming.
- `gmc_v9_0.c` selects `mmhub_v1_7_funcs` and `mmhub_v1_7_ras` for MMHUB IP version 9.4.2 and initializes client-id tables used to interpret MMHUB faults.
- SOC15 register helpers and field helpers rely on these shift/mask definitions matching the offsets and actual MMHUB 1.7 hardware.

Cross-generation similarity is high but not exact. MMHUB 1.0, 1.7, 1.8, 9.3, 9.4, and 9.4.1 headers all contain related DAGB fields, but masks, instance counts, client IDs, and register availability can differ. Mixing offsets and masks across generations can compile while programming the wrong bits.

## Integration Points

Primary integration points are:

- `amdgpu/mmhub_v1_7.c`: includes this header and uses MMHUB masks throughout VM hub initialization. The specific DAGB fields in this chunk are most visibly tied to `mmhub_v1_7_init_snoop_override_regs()`, which programs SDMA snoop behavior across five DAGB instances.
- `amdgpu/mmhub_v1_8.c`: not a direct user of this v1.7 header, but it contains the same snoop-override pattern for the v1.8 register set, making the DAGB stride and SDMA client-bit assumptions an important cross-version design point.
- `amdgpu/gmc_v9_0.c`: selects MMHUB 1.7 functions/RAS hooks for IP 9.4.2 and contains MMHUB golden-setting tables that touch DAGB write-client fields.
- AMDGPU RAS and fault reporting: `DAGB1_FATAL_ERROR_*` fields and client-id tables provide context for fatal MMHUB error diagnosis and interrupt/fault attribution.
- Performance and debug tooling: `DAGB1_PERFCOUNTER*`, pending masks, FIFO/credit fullness, and L1 TLB indirect-access fields can be used by low-level profiling, debugfs, bring-up, or hardware validation flows.
- Power and clock management: CGTT clock-control fields intersect with MMHUB clock gating and power-management policy, even though the policy itself is outside this generated header.

## Risks And Edge Cases

- The chunk boundary is artificial. It begins after the `DAGB1_RD_VC1_CNTL` comment and earlier shift fields, and it ends before all `DAGB2_WR_OUTPUT_DAGB_LAZY_TIMER` masks are present. Adjacent chunks must be merged for complete register-family coverage.
- Bitfield drift is high impact. Wrong masks in client controls can alter virtual-channel routing, disable TLB credit checks, change urgency, or break bandwidth/OSD limits for MMHUB clients.
- Credit fields affect forward progress. Incorrect TLB, EA, storage, return, OSD, atomic, or data credits can manifest as hangs, throttling, FIFO pressure, or unfair arbitration under SDMA, video, display, or host traffic.
- Snoop override programming assumes a stable DAGB stride and SDMA client bit 15. If the offset layout or client mapping changes, the loop in MMHUB initialization can program the wrong instance or wrong client bit.
- Fatal-error status and clear fields are not ordinary configuration. Incorrect clear handling can lose diagnostic evidence; incorrect enable handling can mask or spuriously surface RAS events.
- Performance counter trigger and clear fields can disturb profiling state. `CLEAR`, `CLEAR_ALL`, start/stop trigger, and stop-on-saturate fields need the same sequencing as the owning performance-counter path.
- Clock-gating overrides can affect power, idle, and wake behavior. Misprogramming disable, threshold, or SOFT_OVERRIDE bits can cause unexpected MMHUB power usage or access latency.
- Indirect `DAGB1_L1TLB_REG_RW` fields require read/write enable and status sequencing. Treating this as a plain data register risks stale reads or incomplete writes.
- Reserve registers and reserved bits should not be repurposed from generated names alone.

## Test Signals

Useful validation signals include:

- Build AMDGPU with MMHUB 1.7 support enabled, especially `mmhub_v1_7.c`, `gmc_v9_0.c`, and RAS paths that include `mmhub_1_7_sh_mask.h`.
- Boot and GART-enable testing on MMHUB IP 9.4.2 hardware, confirming VM setup, TLB/cache initialization, and invalidation complete without MMHUB faults or ring timeouts.
- SDMA coherency testing after `mmhub_v1_7_init_snoop_override_regs()`: SDMA writes should correctly probe-invalidate RW cache lines across all expected DAGB instances.
- Golden-setting validation that `mmDAGB1_WRCLI2` mask/value programming produces the expected virtual-channel routing and does not clobber neighboring write-client fields.
- Stress memory clients simultaneously, including SDMA, video, display/host, and GMI paths, and watch for FIFO full, credit full, pending-mask stalls, VM fault storms, or forward-progress loss.
- RAS/fault-injection or error-reporting tests that exercise `DAGB1_FATAL_ERROR_*` enable, clear, and status decode fields without losing sticky error context.
- Performance-counter tests that configure `DAGB1_PERFCOUNTER*_CFG`, start/stop/clear through `DAGB1_PERFCOUNTER_RSLT_CNTL`, and verify counter low/high behavior and saturation handling.
- Suspend/resume, GPU reset, and power-gating tests that confirm DAGB client controls, snoop overrides, credit settings, and CGTT clock-control state are restored or reinitialized as expected.

### subset-b-002760: lines 4718-7076

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mmhub/mmhub_1_7_sh_mask.h lines 4718-7076

## Purpose

This chunk is part of a generated AMD MMHUB 1.7 register shift/mask header. It defines C preprocessor constants for bitfield extraction and composition in MMHUB DAGB register blocks. Each field is exposed through the conventional AMDGPU generated-header pair:

- `<REGISTER>__<FIELD>__SHIFT` for the low bit position.
- `<REGISTER>__<FIELD>_MASK` for the raw 32-bit field mask.

The repository path is under `distributed-fs/ceph-client`, but this source is GPU driver hardware metadata, not Ceph or filesystem logic. The chunk contains no executable functions, structs, callbacks, or software algorithms.

The range starts in the middle of DAGB2 write-path definitions and then enters `addressBlock: mmhub_dagb_dagbdec3`, covering a large part of DAGB3 read and write register layouts. DAGB appears to be an MMHUB data/arbitration gateway block with per-client, per-virtual-channel, credit, pending, clock-gating, performance, and fatal-error reporting fields.

## Important APIs, Types, And Macros

There are no normal C APIs or types in this slice. The macro namespace is the public interface consumed by AMDGPU register access code together with the matching MMHUB 1.7 offset header.

Major field families in this chunk include:

- `DAGB2_WR_*`: the tail of the DAGB2 write path, including output lazy timers, clock-gating controls, address/data DAGB burst and lazy-timer tables, per-VC write controls, credit controls, snoop override, pending-bit status, delay injection, miscellaneous remap/clock/busy controls, fatal-error decode fields, FIFO/credit fullness, performance counters, L1TLB register read/write controls, and reserved registers.
- `DAGB3_RDCLI0..15` and `DAGB3_WRCLI0..15`: repeated client control registers with `VIRT_CHAN`, TLB-credit checking, urgency high/low thresholds, max/min bandwidth controls, OSD limiter enable, and max outstanding request fields.
- `DAGB3_RD_CNTL` and `DAGB3_WR_CNTL`: shared read/write control words for SCLK frequency encoding, client and VC bandwidth windows, IO level override and compliance VC, shared VC count, and jump-fix behavior.
- `DAGB3_RD_GMI_CNTL` and `DAGB3_WR_GMI_CNTL`: GMI path credit, level, max-burst, and lazy-timer fields.
- `DAGB3_RD_ADDR_DAGB`, `DAGB3_WR_ADDR_DAGB`, and `DAGB3_WR_DATA_DAGB`: DAGB enable, jump-ahead enable, self-init disable, `WHOAMI`, and read/write address `JUMP_MODE` controls.
- `*_OUTPUT_DAGB_MAX_BURST` and `*_OUTPUT_DAGB_LAZY_TIMER`: per-VC nibbles for output burst and timer tuning across VC0-VC7.
- `*_ADDR_DAGB_MAX_BURST0/1`, `*_ADDR_DAGB_LAZY_TIMER0/1`, `*_DATA_DAGB_MAX_BURST0/1`, and `*_DATA_DAGB_LAZY_TIMER0/1`: per-client nibble fields for clients 0-15.
- `DAGB3_RD_VC0_CNTL..DAGB3_RD_VC7_CNTL` and `DAGB3_WR_VC0_CNTL..DAGB3_WR_VC7_CNTL`: per-virtual-channel storage and EA credits, bandwidth limiters, minimum bandwidth controls, OSD limiter enable, and max OSD fields.
- `*_CNTL_MISC`, `*_TLB_CREDIT`, `*_DATA_CREDIT`, `*_MISC_CREDIT`, `*_OSD_CREDIT_CNTL*`, `DAGB3_RD_RDRET_CREDIT_CNTL*`, and `DAGB3_WR_ATOMIC_FIFO_CREDIT_CNTL1`: pool, TLB, return, atomic FIFO, OSD, and data-credit allocation fields.
- `*_PENDING`: full-width busy bitmaps for ask/go/global-send/TLB/OARB/OSD/DBUS pending state.
- `DAGB2_PERFCOUNTER*` and `DAGB2_PERFCOUNTER_RSLT_CNTL`: low/high counter value fields, compare value, selector ranges, modes, enable/clear bits, trigger selection, enable-any, clear-all, and stop-on-saturate controls.
- `DAGB2_FATAL_ERROR_STATUS*` and `DAGB3_FATAL_ERROR_STATUS*`: fatal-error valid bit, client ID, address low/high fields, tag, VFID/VF, address space, IO, size, FED, operation, write/read TMZ, snoop, invalidate, NACK, read-only, memlog, and EOP decode fields.

## Control Flow

This header chunk has no runtime control flow. Its only behavior is C preprocessing.

Typical consumer flow is:

1. A MMHUB 1.7 AMDGPU source includes the companion offset header and this mask header.
2. The caller selects a `mmDAGB*` register offset from the offset header and the relevant `DAGB*__FIELD__SHIFT` and `DAGB*__FIELD_MASK` macros from this header.
3. Driver code uses AMDGPU register helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32`, `WREG32`, or SOC15-style wrappers to assemble, update, poll, or decode a 32-bit MMIO register.
4. Actual ordering, idle requirements, polling loops, reset handling, and firmware coordination live in the consumer driver code, not in this generated header.

The repeated macro layout implies several hardware programming patterns: per-client setup across 16 clients, per-VC setup across 8 virtual channels, per-direction read/write tuning, and status collection from full-width busy or error registers.

## State And Persistence Behavior

The macros persist no software state. They describe hardware-visible MMHUB DAGB state.

The represented hardware state includes:

- Persistent-until-reprogrammed configuration: virtual-channel selection, TLB credit checking, urgency thresholds, bandwidth windows, max/min bandwidth limits, OSD limits, GMI credit and burst behavior, DAGB enable/jump settings, per-client burst sizes, per-client lazy timers, per-VC credit pools, clock-gating delays, and VC remapping.
- Volatile live status: pending busy bitmaps, FIFO empty/full bits, write/read credit full fields, and fatal-error status words.
- Action or control bits: fatal-error clear, performance-counter enable/clear, performance result clear-all, stop-on-saturate, clock-gating override bits, GPU snoop override/value masks, and L1TLB register read/write control bits.
- Diagnostic and telemetry state: performance counter low/high values, compare value, performance select windows, start/stop triggers, DAGB delay fields, fatal-error address/tag/VF/client/operation decodes, and reserved scratch-like words.

Persistence is hardware-defined. Configuration fields are expected to be reprogrammed during ASIC initialization, reset recovery, power-management transitions, virtualization setup, or golden-setting application. Status and counter fields may be volatile, latched, clear-on-write, or meaningful only after specific blocks are idle or selected.

## Dependencies

This chunk depends on the generated AMD MMHUB 1.7 register set remaining synchronized:

- `mmhub_1_7_sh_mask.h` supplies the field masks and shifts documented here.
- The matching MMHUB 1.7 offset header supplies the actual register addresses for the `DAGB2_*` and `DAGB3_*` registers.
- AMDGPU bitfield helpers depend on exact macro spelling, especially the `__SHIFT` and `_MASK` suffix convention.
- MMHUB initialization, golden settings, memory-management bring-up, clock-gating setup, GPU reset/recovery, virtualization, and hang-dump paths depend on these bit layouts matching the ASIC specification.
- Similar DAGB register families exist across DAGB0, DAGB1, DAGB2, and DAGB3 and across MMHUB generations. The names are deliberately regular, but fields can still differ by generation or block instance.

## Integration Points

Primary integration points are:

- MMHUB register programming: consumers combine these masks with MMHUB offsets to program DAGB read/write client routing, bandwidth, credit, lazy-timer, and burst behavior.
- Power and clock management: `*_CGTT_CLK_CTRL`, `*_L1TLB_*_CGTT_CLK_CTRL`, `*_ATCVM_*_CGTT_CLK_CTRL`, and `DAGB*_CNTL_MISC2` fields expose clock-gating delays, light-sleep overrides, soft-stall overrides, and clock-gating disable bits.
- Memory-translation and TLB paths: TLB credit fields, TLB pending bits, ATCVM clock controls, L1TLB clock controls, and `DAGB2_L1TLB_REG_RW` connect this metadata to MMHUB address translation behavior.
- Performance and diagnostics: DAGB2 performance counter fields support selectable counter windows and triggered measurement. FIFO/credit fullness, pending bitmaps, and fatal-error status fields support hang analysis and low-level debug dumps.
- Error handling and RAS-like reporting: fatal-error control, clear, and status fields allow consumer code to filter errors, clear latches, and decode client, address, tag, VF/VFID, access type, operation, and response flags.
- Virtualization and isolation: fields such as `VFID`, `VF`, GPU snoop override/value, per-client controls, and virtual-channel mappings are relevant to SR-IOV or multi-client isolation paths.

## Risks And Edge Cases

- The chunk boundary is artificial. It begins after the first part of `DAGB2_WR_OUTPUT_DAGB_MAX_BURST` and ends after `DAGB3_FATAL_ERROR_STATUS3`, so adjacent chunks are required for the complete file-level picture.
- Header/offset mismatch is the main correctness risk. These masks can compile with the wrong generation's offset header but program or decode the wrong bits on hardware.
- Repeated client and VC groups are easy to copy incorrectly. Client 0-7 and 8-15 fields use separate registers, and read/write/address/data variants look nearly identical while targeting different hardware paths.
- Full-width pending and snoop masks do not mean arbitrary writes are safe. Some registers are status bitmaps, some are override controls, and consumer code must know the hardware access semantics.
- Credit and bandwidth fields can affect liveness. Incorrect TLB, return, OSD, atomic, GMI, or pool credits can create throttling, starvation, deadlock, or hangs under memory pressure.
- Clock-gating and light-sleep override fields can interact with active traffic, reset, and firmware-owned sequences. Writes may require block idle state or prescribed ordering not visible in this header.
- Fatal-error status fields are decoders, not policy. Error latches may require clear sequencing, and address/tag/VF fields may be invalid unless `VALID` is set.
- Reserved registers and reserve masks should generally be preserved during read-modify-write unless the hardware programming guide requires a full-register write.

## Test Signals

Useful validation signals include:

- Build coverage for AMDGPU sources that include MMHUB 1.7 offset and mask headers.
- Static generated-header checks that every field has matching `__SHIFT` and `_MASK` definitions, masks align with shifts, and repeated DAGB2/DAGB3 register families are complete.
- Cross-checks against the companion MMHUB 1.7 offset header so every `DAGB2_*` and `DAGB3_*` register named here has a matching register address where expected.
- Hardware bring-up on MMHUB 1.7 ASICs, confirming MMHUB initialization, memory translation, rings, VM faults, reset recovery, suspend/resume, and clock-gating transitions are stable.
- Stress tests that exercise high memory traffic, concurrent read/write clients, TLB pressure, atomics, virtualization/VF traffic, and bandwidth-limit settings without hangs or starvation.
- Debug and hang-dump tests that read pending, FIFO, credit, performance counter, and fatal-error status registers and decode fields consistently.
- Error-injection or fault-path tests, where available, that verify fatal-error valid/client/address/tag/VF/operation fields and clear behavior.

### subset-b-002761: lines 7077-9435

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mmhub/mmhub_1_7_sh_mask.h lines 7077-9435

## Purpose

This chunk is generated AMD MMHUB 1.7 register bitfield metadata. It defines `__SHIFT` and `_MASK` preprocessor macros for the tail of `DAGB3`, all of `mmhub_dagb_dagbdec4` (`DAGB4`), and the beginning of `mmhub_dagb_dagbdec5` (`DAGB5`). The macros describe how AMDGPU code packs and decodes fields in Data Address Generation Block registers for MMHUB traffic routing, bandwidth throttling, virtual-channel arbitration, TLB/credit accounting, clock gating, pending-status observation, fatal-error reporting, and performance counters.

Although this path sits under a Ceph-client source tree mirror, the file is Linux AMD GPU driver hardware metadata. It contains no Ceph filesystem logic, no executable code, and no runtime storage by itself.

The covered range includes:

- `DAGB3_FATAL_ERROR_STATUS3`, FIFO/credit-full indicators, perf counter controls/results, L1 TLB register read/write controls, and reserve registers. The previous chunk contains the earlier `DAGB3` field definitions, so this range begins mid-register-family.
- The complete `DAGB4` address block: read clients `RDCLI0..15`, read control/credit/VC registers, write clients `WRCLI0..15`, write control/credit/data/atomic/OSD registers, snoop override fields, pending-status registers, delay/control/miscellaneous registers, fatal-error status/clear/control registers, FIFO/credit fullness indicators, perf counters, L1TLB control, and reserved registers.
- The start of `DAGB5`: read clients `RDCLI0..15`, read bandwidth/GMI/DAGB controls, output max-burst/lazy-timer fields, read-side CGTT clock controls, L1TLB/ATCVM read clock controls, and the first `RD_ADDR_DAGB_MAX_BURST0` client fields. The next chunk is required for the rest of `DAGB5`.

## Important APIs, Types, And Macros

There are no C functions, structs, enums, callbacks, locks, allocations, or direct MMIO operations in this chunk. Its interface is the generated macro namespace consumed by AMDGPU register helpers:

- `DAGB<n>_<REGISTER>__<FIELD>__SHIFT` gives the bit position for a field.
- `DAGB<n>_<REGISTER>__<FIELD>_MASK` gives the 32-bit mask for the same field.
- These macros pair with `regDAGB*` offsets from `mmhub_1_7_offset.h` and are normally used through `REG_SET_FIELD`, `REG_GET_FIELD`, `SOC15_REG_FIELD`, direct mask operations, and SOC15 read/write helpers such as `RREG32_SOC15`, `WREG32_SOC15`, `RREG32_SOC15_OFFSET`, and `WREG32_SOC15_OFFSET`.

High-signal register families in this range are:

- `RDCLI0..15` and `WRCLI0..15`: per-client read/write routing and QoS fields. Each client exposes `VIRT_CHAN`, `CHECK_TLB_CREDIT`, `URG_HIGH`, `URG_LOW`, `MAX_BW_ENABLE`, `MAX_BW`, `MIN_BW_ENABLE`, `MIN_BW`, `OSD_LIMITER_ENABLE`, and `MAX_OSD`.
- Read and write global controls: `RD_CNTL`/`WR_CNTL` contain `SCLK_FREQ`, bandwidth windows, IO-level override/comply fields, shared VC count, and jump behavior. `RD_GMI_CNTL`/`WR_GMI_CNTL` carry EA credit, level, burst, and lazy-timer fields.
- DAGB routing controls: `RD_ADDR_DAGB`, `WR_ADDR_DAGB`, and `WR_DATA_DAGB` describe enable, jump-ahead, self-init disable, `WHOAMI`, and jump-mode style controls.
- Per-output and per-client burst/timer arrays: `*_OUTPUT_DAGB_MAX_BURST`, `*_OUTPUT_DAGB_LAZY_TIMER`, `*_ADDR_DAGB_MAX_BURST0/1`, `*_ADDR_DAGB_LAZY_TIMER0/1`, and write-data equivalents encode compact 4-bit fields for VCs or client slots.
- Virtual-channel controls: `RD_VC0..7_CNTL` and `WR_VC0..7_CNTL` define per-VC EA/storage credits, bandwidth limits, OSD limiter enable, and max OSD.
- Credit controls and status: `RD_TLB_CREDIT`, `WR_TLB_CREDIT`, `RD_RDRET_CREDIT_CNTL`, `RD_RDRET_CREDIT_CNTL2`, `WR_DATA_CREDIT`, `WR_MISC_CREDIT`, `WR_OSD_CREDIT_CNTL1/2`, `WR_ATOMIC_FIFO_CREDIT_CNTL1`, `WR_CREDITS_FULL`, and `RD_CREDITS_FULL`.
- Pending and fullness indicators: `RDCLI_*_PENDING`, `WRCLI_*_PENDING`, DBUS pending status, `FIFO_EMPTY`, and `FIFO_FULL` expose busy/full bitmaps used for diagnostics and drain checks.
- Clock and light-sleep controls: `RD_CGTT_CLK_CTRL`, `WR_CGTT_CLK_CTRL`, `L1TLB_*_CGTT_CLK_CTRL`, and `ATCVM_*_CGTT_CLK_CTRL` define on-delay, off-hysteresis, soft-stall override, and light-sleep override bits for write/read/return/register paths.
- Error and debug/observability: `FATAL_ERROR_CNTL`, `FATAL_ERROR_CLEAR`, `FATAL_ERROR_STATUS0..3`, `DAGB_DLY`, `CNTL_MISC`, `CNTL_MISC2`, `PERFCOUNTER_LO`, `PERFCOUNTER_HI`, `PERFCOUNTER0..2_CFG`, and `PERFCOUNTER_RSLT_CNTL`.
- Snoop override fields: `WRCLI_GPU_SNOOP_OVERRIDE` and `WRCLI_GPU_SNOOP_OVERRIDE_VALUE` expose enable bitmaps for write clients. `mmhub_v1_7.c` programs these by offset stride to enable SDMA snoop behavior across DAGB instances.

## Control Flow

This header chunk has no runtime control flow. Its behavior is entirely through C preprocessing and later MMIO operations in consumer code.

Typical consumer flow is:

1. MMHUB 1.7 driver code includes `mmhub_1_7_offset.h` and `mmhub_1_7_sh_mask.h`.
2. Code selects a register offset such as `regDAGB0_WRCLI_GPU_SNOOP_OVERRIDE`, `regDAGB4_WR_CNTL`, or another `regDAGB*` macro from the offset header.
3. Code uses a mask/shift macro from this header through `REG_SET_FIELD`, `REG_GET_FIELD`, or direct mask arithmetic to build or decode the 32-bit register value.
4. SOC15 helpers perform the actual MMIO read/write against the selected MMHUB instance.

The visible MMHUB 1.7 consumer in this tree is `amdgpu/mmhub_v1_7.c`. Most of that file programs VM hub, TLB, cache, GART aperture, invalidation, and RAS fields from other sections of this header, while DAGB integration appears in two important places:

- `mmhub_v1_7_init_snoop_override_regs()` computes the per-DAGB register stride from `regDAGB1_WRCLI_GPU_SNOOP_OVERRIDE - regDAGB0_WRCLI_GPU_SNOOP_OVERRIDE`, iterates five DAGB instances, and sets bit 15 in both `WRCLI_GPU_SNOOP_OVERRIDE` and `WRCLI_GPU_SNOOP_OVERRIDE_VALUE` so SDMA writes probe/invalidate cached RW lines.
- `mmhub_v1_7_update_medium_grain_clock_gating()` and `mmhub_v1_7_get_clockgating()` use `DAGB0_CNTL_MISC2` and `DAGB1_CNTL_MISC2` masks from earlier chunks to control/read DAGB clock-gating state. The `DAGB4_CNTL_MISC2` masks in this chunk follow the same generated field pattern for later instances even though this specific driver code only names DAGB0/1 directly.

The header does not encode safe access ordering, reset sequencing, drain loops, read side effects, sticky status clearing rules, or privilege/SR-IOV ownership. Those rules live in the MMHUB driver, SOC15 accessors, firmware expectations, and hardware specification.

## State And Persistence Behavior

This file stores no software state. The macros describe fields in MMHUB hardware registers whose persistence is hardware-defined.

The represented hardware state includes:

- Persistent configuration until reset or reprogramming: client-to-virtual-channel mapping, urgency thresholds, bandwidth windows, max/min bandwidth enforcement, OSD limits, EA/storage credits, GMI burst/lazy timing, DAGB enable/jump routing, client and VC burst settings, snoop override enable/value bits, and clock-gating/light-sleep override controls.
- Live status and diagnostic state: pending client bitmaps, FIFO empty/full bitmaps, read/write credit-full indicators, TLB/data/misc credit state, and performance counter low/high result registers.
- Error state: fatal-error status registers carry address high bits, request ID, source ID, client ID, VMID/VFID, tag, opcode, VF/space/IO/size/FED indicators, snoop/invalid/NACK/RO/MEMLOG/EOP style qualifiers, plus explicit clear/control fields.
- Reserved fields/registers: `RESERVE*` and explicit `RESERVE` masks are generated placeholders. They should not be treated as available driver-owned state.

Some fields are configuration knobs that persist across normal operation; others are counters, latches, status bitmaps, or write-trigger/clear bits. This header does not distinguish read-only, write-one-to-clear, sticky, or firmware-owned fields beyond macro names.

## Dependencies

This chunk depends on the AMDGPU SOC15 register stack and sibling generated MMHUB metadata:

- `mmhub_1_7_offset.h` supplies matching `regDAGB*` register offsets and base indices.
- Earlier and later chunks of `mmhub_1_7_sh_mask.h` complete the `DAGB3` and `DAGB5` field definitions and provide the rest of MMHUB 1.7 VM, ATC, MMEA, and DAGB masks.
- `amdgpu/mmhub_v1_7.c`, `soc15.h`, and `soc15_common.h` provide the runtime MMIO helpers and field manipulation macros that make these constants operational.
- Cross-generation MMHUB drivers such as `mmhub_v1_8.c` and `mmhub_v9_4.c` use closely related DAGB patterns, but offsets, instance counts, and field availability can differ.

The generated field names must stay synchronized with the offset header and with any code that computes register stride across DAGB instances. Because `DAGB4` is one of several repeated blocks, small differences in naming, spacing, or masks can break looped access patterns that start from `DAGB0` and stride across instances.

## Integration Points

Primary integration points are:

- MMHUB initialization and GART setup: `mmhub_v1_7.c` includes this header for MMHUB register field packing during VM, TLB, cache, aperture, invalidation, and fault-control setup.
- SDMA coherency/snoop setup: `mmhub_v1_7_init_snoop_override_regs()` writes the DAGB write-client snoop override registers across five DAGB instances. The `DAGB4_WRCLI_GPU_SNOOP_OVERRIDE*` masks in this chunk describe the final instance reached by that loop.
- Power management and clock gating: DAGB `CNTL_MISC2` and `*_CGTT_CLK_CTRL` fields integrate with medium-grain clock gating and light-sleep behavior. Incorrect masks can leave request, return, TLB, or register subpaths ungated or over-gated.
- Performance/debug tooling: `PERFCOUNTER*`, `FIFO_*`, pending, credit, and fatal-error fields are observability hooks for debugging MMHUB stalls, under-crediting, bandwidth throttling, and fatal transaction errors.
- RAS and fault handling: fatal-error status fields overlap conceptually with the broader AMD RAS path and error interrupt reporting. This chunk provides decode fields, while higher-level RAS event handling lives outside the header.
- Hardware generation tables: the file is part of the MMHUB 1.7 generated register contract and is consumed alongside other generated ASIC register headers under `include/asic_reg`.

## Risks And Edge Cases

- Chunk boundaries are artificial. This range starts mid-`DAGB3` and ends mid-`DAGB5`; reviewing it alone is insufficient for a complete per-instance DAGB model.
- `DAGB4` contains many repeated per-client and per-VC fields. Copy/paste or generator errors can compile cleanly while shifting one client or VC into the wrong nibble.
- Snoop override handling is instance-stride-sensitive. `mmhub_v1_7.c` computes a distance from `DAGB0` to `DAGB1` and applies it across five instances; offset/header mismatches can silently program the wrong DAGB instance or wrong register.
- Many fields influence memory-system QoS and coherency. Bad `VIRT_CHAN`, credit, bandwidth, OSD, burst, or lazy-timer masks can produce stalls, unfair arbitration, performance cliffs, or ordering/coherency bugs.
- Clock-gating and light-sleep override fields affect live MMHUB datapaths. Overly broad masks can stall read/write/return/register paths; under-broad masks can prevent intended power savings.
- Fatal-error clear/control fields should not be treated as ordinary status. Writes can clear latched error evidence or change fatal-error filtering.
- Reserved masks are full-width or high-bit placeholders in several registers. Driver code should avoid relying on reserved fields unless directed by an authoritative hardware programming guide.
- Cross-generation similarity is risky. MMHUB 1.7, 1.8, and 9.4 DAGB names are similar, but masks and instance behavior should not be assumed interchangeable.

## Test Signals

Useful validation signals include:

- Build coverage for `amdgpu/mmhub_v1_7.c` and any code including `mmhub_1_7_sh_mask.h`, ensuring all `DAGB*` field names referenced by consumers remain available.
- Generated-header consistency checks that every `DAGB4` and covered `DAGB5` field has both `__SHIFT` and `_MASK` forms and matches the register names in `mmhub_1_7_offset.h`.
- Static checks for repeated field layout consistency across `DAGB0..DAGB5`, especially `RDCLI/WRCLI`, `RD_VC/WR_VC`, `*_MAX_BURST`, `*_LAZY_TIMER`, pending, credit, and `CNTL_MISC2` families.
- Hardware boot smoke tests on MMHUB 1.7 ASICs covering GART enable, VM context setup, SDMA writes, cache coherency, suspend/resume, and SR-IOV VF paths.
- Coherency tests that exercise SDMA write snoop override behavior, looking for stale cache lines, missed probe invalidations, or data corruption.
- Stress tests for GPUVM memory traffic under mixed SDMA/display/media clients to expose DAGB credit, OSD, virtual-channel, and bandwidth-window mistakes.
- Power-management tests for medium-grain clock gating and light sleep, watching for MMHUB hangs, unexpected register-access timeouts, or missing power-state transitions.
- Diagnostic/RAS tests that read fatal-error, FIFO, pending, credit, and perf-counter registers and verify fields decode consistently with hardware events.
- Regression indicators include VM fault storms, SDMA coherency failures, MMHUB register access timeouts, GART enable failures, display/media traffic stalls, unexpected fatal-error interrupts, or power-gating instability after changing generated masks.

### subset-b-002762: lines 9436-11789

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mmhub/mmhub_1_7_sh_mask.h lines 9436-11789

## Scope And Purpose

This chunk is a generated AMD MMHUB 1.7 register shift/mask header slice. It contains C preprocessor constants only: each hardware register field is represented by a `<REGISTER>__<FIELD>__SHIFT` value and a matching `<REGISTER>__<FIELD>_MASK` value. There are no functions, structs, enums, global storage objects, or executable control-flow paths in this range.

The line range starts in the tail of `DAGB5_RD_ADDR_DAGB_MAX_BURST0` with only the `CLIENT6` and `CLIENT7` masks present in this chunk, then covers the rest of the `DAGB5` read/write data-arbitration register field vocabulary. It then enters `addressBlock: mmhub_ea_mmeadec0` and covers the beginning of `MMEA0` DRAM/GMI client grouping, priority, CAM, lazy-timer, page-burst, and address-normalization field definitions. The range ends at the `MMEA0_ADDRNORMGMI_HOLE_CNTL` register comment; that register's field definitions continue in the next chunk.

The purpose of the chunk is to provide symbolic bit layouts for MMHUB data-arbitration and memory/EA address-decoder registers used by the AMDGPU MMHUB 1.7 support code. Consumers combine these macros with register offsets from `mmhub/mmhub_1_7_offset.h` and register access helpers such as `RREG32_SOC15`, `WREG32_SOC15`, `REG_GET_FIELD`, `SOC15_REG_FIELD`, and raw `RREG32`/`WREG32` paths.

## Macro Interface

The exported interface is entirely macro based:

- `<REG>__<FIELD>__SHIFT` gives the right shift count for a field.
- `<REG>__<FIELD>_MASK` gives the bit mask in the 32-bit register word.
- Packed client, virtual-channel, group, and threshold registers use repeated low-nibble or byte lanes, such as `0x0000000f`, `0x000000f0`, or `0x000000ff`.
- Full-width status/counter fields and reserve registers use broad masks where appropriate; this chunk mainly uses packed control/status fields rather than whole-register data ports.

Typical consumers either use local AMDGPU helpers that expand through the mask/shift naming convention or perform explicit read-modify-write packing:

```c
field = (value & REG__FIELD_MASK) >> REG__FIELD__SHIFT;
value = (value & ~REG__FIELD_MASK) |
        ((new_field << REG__FIELD__SHIFT) & REG__FIELD_MASK);
```

The header does not constrain values before shifting and does not encode whether a field is read-only, write-one-to-clear, pulse, latched status, or persistent configuration. Those semantics are owned by the hardware register documentation and the driver code that sequences MMIO access.

## Register Families Covered

### DAGB5 Read-Side Arbitration And Credits

The opening `DAGB5_RD_*` section covers read-side behavior for the fifth DAGB instance. It includes:

- `DAGB5_RD_ADDR_DAGB_MAX_BURST*` and `DAGB5_RD_ADDR_DAGB_LAZY_TIMER*`: per-client burst and lazy-delay controls. The `0` register is partial in this chunk; client 0-5 definitions are in the previous chunk while client 6-7 masks and the complete lazy timer are here. The `1` register covers clients 8-15.
- `DAGB5_RD_VC0_CNTL` through `DAGB5_RD_VC7_CNTL`: per-virtual-channel storage and EA credits, max/min bandwidth enable and values, OSD limiter enable, and max outstanding controls.
- `DAGB5_RD_CNTL_MISC`, `DAGB5_RD_TLB_CREDIT`, `DAGB5_RD_RDRET_CREDIT_CNTL`, and `DAGB5_RD_RDRET_CREDIT_CNTL2`: pool, TLB, read-return, IO, GMI, and VC credit accounting.
- `DAGB5_RDCLI_*_PENDING`: busy/status bits for ask, go, global-send, TLB, OARB, and OSD read-client paths.

These fields form the bit-level contract for read request arbitration, outstanding credit limits, and status polling in the MMHUB DAGB.

### DAGB5 Write-Side Client, DAGB, Credit, And Clock Controls

The write-side `DAGB5_WR*` section is the largest part of the DAGB block in this range:

- `DAGB5_WRCLI0` through `DAGB5_WRCLI15` define each write client's virtual-channel assignment, TLB-credit checking, high/low urgency thresholds, max/min bandwidth controls, and OSD limiter/max-outstanding fields.
- `DAGB5_WR_CNTL` exposes SCLK frequency/window fields, IO-level override, shared-VC selection, and fixed-jump behavior.
- `DAGB5_WR_GMI_CNTL`, `DAGB5_WR_ADDR_DAGB`, `DAGB5_WR_DATA_DAGB`, and the output/address/data `MAX_BURST` and `LAZY_TIMER` registers tune write request routing and batching across output VCs, address clients, and data clients.
- `DAGB5_WR_CGTT_CLK_CTRL`, `DAGB5_L1TLB_WR_CGTT_CLK_CTRL`, and `DAGB5_ATCVM_WR_CGTT_CLK_CTRL` define clock-gating/light-sleep style delay and override bits for write, L1 TLB write, and ATC/VM write subpaths.
- `DAGB5_WR_TLB_CREDIT`, `DAGB5_WR_DATA_CREDIT`, `DAGB5_WR_MISC_CREDIT`, `DAGB5_WR_OSD_CREDIT_CNTL1/2`, and `DAGB5_WR_ATOMIC_FIFO_CREDIT_CNTL1` define write-side TLB, data-burst, OSD, atomic FIFO, pool, IO, GMI, deadlock-VC, and legacy credit controls.
- `DAGB5_WRCLI_GPU_SNOOP_OVERRIDE`, `DAGB5_WRCLI_GPU_SNOOP_OVERRIDE_VALUE`, and the `DAGB5_WRCLI_*_PENDING`/`DBUS_*_PENDING` status bits expose write-client snoop and pending-state behavior.

These constants are relevant to bandwidth shaping, request batching, clock gating, GPU snoop control, and hang diagnosis for MMHUB write traffic.

### DAGB5 Diagnostics, Fatal Error, And Performance Counters

The diagnostic tail of the DAGB block includes:

- `DAGB5_DAGB_DLY`, `DAGB5_CNTL_MISC`, and `DAGB5_CNTL_MISC2`: delay injection, VC remap, bandwidth timing windows, urgency boost/halt, clock-gating disables, busy-disable controls, swap controls, HDP CID, and read-return FIFO/deadlock-credit fields.
- `DAGB5_FATAL_ERROR_CNTL`, `DAGB5_FATAL_ERROR_CLEAR`, and `DAGB5_FATAL_ERROR_STATUS0` through `STATUS3`: fatal-error filter selection, clear bit, validity, client ID, address low/high, tag, VF/VFID, space/IO/size/FED attributes, and operation/snoop/nack/ordering/memlog/EOP status fields.
- `DAGB5_FIFO_EMPTY`, `DAGB5_FIFO_FULL`, `DAGB5_WR_CREDITS_FULL`, and `DAGB5_RD_CREDITS_FULL`: one-bit status fields for FIFO and credit fullness/emptiness.
- `DAGB5_PERFCOUNTER_LO`, `DAGB5_PERFCOUNTER_HI`, `DAGB5_PERFCOUNTER0_CFG` through `2_CFG`, and `DAGB5_PERFCOUNTER_RSLT_CNTL`: event selection, end event, mode, enable, clear, counter low/high, compare value, start/stop triggers, clear-all, enable-any, and stop-on-saturate controls.
- `DAGB5_L1TLB_REG_RW` and `DAGB5_RESERVE1` through `RESERVE4`: L1 TLB register read/write control, VMID exception interrupt control, parity/read-return checking controls, and reserve fields.

These fields are primarily consumed by debug, RAS-like diagnosis, performance counter setup, and low-level bring-up validation. Mis-decoding fatal error fields can lead to incorrect fault attribution even if the underlying hardware error is real.

### MMEA0 DRAM And GMI Grouping, Arbitration, And Priority

After `addressBlock: mmhub_ea_mmeadec0`, the chunk defines the beginning of the MMEA0 address/arbiter register vocabulary for DRAM and GMI paths:

- `MMEA0_DRAM_RD_CLI2GRP_MAP0/1`, `MMEA0_DRAM_WR_CLI2GRP_MAP0/1`, `MMEA0_GMI_RD_CLI2GRP_MAP0/1`, and `MMEA0_GMI_WR_CLI2GRP_MAP0/1`: map client IDs 0-31 into four arbitration groups. Each client field is two bits.
- `*_GRP2VC_MAP`: map groups 0-3 to virtual channels.
- `*_LAZY`: per-group delay plus request accumulation threshold, timeout, and idle-max fields.
- `*_CAM_CNTL`: per-group CAM depth, per-group reorder limit, and refill-chain controls. GMI variants also include `PAGEBASED_CHAINING`.
- `*_PAGE_BURST`: read/write low/high page burst limits.
- `*_PRI_AGE`, `*_PRI_QUEUING`, `*_PRI_FIXED`, `*_PRI_URGENCY`, and `*_PRI_QUANT_PRI1/2/3`: per-group coefficients, urgency modes, and threshold levels used by the DRAM and GMI arbitration priority model.
- `MMEA0_GMI_RD_PRI_URGENCY_MASKING` and `MMEA0_GMI_WR_PRI_URGENCY_MASKING`: per-CID urgency masking for client IDs 0-31 on GMI read and write paths.

This section expresses how MMHUB EA traffic is grouped and prioritized before it reaches DRAM or GMI fabric paths. It is not a software scheduler by itself; it defines the bitfields used to program hardware arbitration policy.

### MMEA0 Address Normalization

The last complete block in this chunk begins the `MMEA0_ADDRNORM*` address-normalization registers:

- `MMEA0_ADDRNORM_BASE_ADDR0` through `BASE_ADDR3` and `MMEA0_ADDRNORM_MEGABASE_ADDR0/1`: range valid, legacy MMIO hole enable, interleave channel/die/socket counts, interleave address select, and base-address fields.
- `MMEA0_ADDRNORM_LIMIT_ADDR0` through `LIMIT_ADDR3` and `MMEA0_ADDRNORM_MEGALIMIT_ADDR0/1`: destination fabric ID and limit-address fields.
- `MMEA0_ADDRNORM_OFFSET_ADDR1` and `OFFSET_ADDR3`: high-address offset enable and high-address offset fields.
- `MMEA0_ADDRNORMDRAM_HOLE_CNTL`: DRAM hole valid and hole offset fields.
- `MMEA0_ADDRNORMGMI_HOLE_CNTL`: only the register comment appears at the final line in this chunk; its field definitions are outside this line range.

These fields are part of the hardware address-routing contract. Incorrect packing can route memory transactions to the wrong fabric destination, mishandle interleaving, or misrepresent MMIO/DRAM holes.

## Control Flow And State Behavior

There is no local control flow in this header. Runtime behavior appears only when other code includes it and performs MMIO reads or writes.

The state represented by these macros is hardware state:

- DAGB read/write arbitration and credit fields persist in MMHUB registers until reset or reprogramming by initialization, power-management, clock-gating, debug, or recovery code.
- Pending, FIFO, full, fatal-error, and performance-counter fields are observed hardware state. Some fields are latched status or command/clear bits, but this header does not document those write semantics.
- MMEA0 grouping, VC mapping, priority coefficients, CAM controls, and address-normalization fields persist as programmed hardware policy for DRAM/GMI routing and arbitration.
- Performance counters have explicit enable/clear/start/stop control fields and low/high result fields. The masks allow programming and reading counters, but counter lifetime and sampling rules are implemented by the hardware and consuming driver paths.

The primary control-flow integration point is `amdgpu/mmhub_v1_7.c`, which includes `mmhub/mmhub_1_7_offset.h` and this shift/mask header. That file initializes MMHUB VM/GART apertures, TLB/cache registers, snoop overrides, VMID settings, invalidation, fault handling, clock gating, and RAS query/reset paths. This exact chunk is not a function body, but its `DAGB5_*` and `MMEA0_*` definitions are part of the same register namespace used by that implementation and by `SOC15_REG_FIELD`/`REG_GET_FIELD` style access.

## Dependencies And Integration Points

- Companion offsets live in `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mmhub/mmhub_1_7_offset.h`; this source tree does not have a `mmhub_1_7_d.h` companion for this generated header.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/mmhub_v1_7.c` directly includes this header and registers `mmhub_v1_7_funcs` and `mmhub_v1_7_ras` for the MMHUB 1.7 block.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gmc_v9_0.c` selects `mmhub_v1_7_funcs` and `mmhub_v1_7_ras` for matching ASIC paths, tying this register vocabulary into GMC/GART setup and VM management.
- Register access is through SOC15 MMIO helpers (`RREG32_SOC15`, `WREG32_SOC15`, `WREG32_SOC15_OFFSET`, `RREG32`, `WREG32`) and field helpers that rely on the exact generated naming convention.
- RAS integration in `mmhub_v1_7.c` uses `SOC15_REG_FIELD` definitions for MMEA EDC/error status fields elsewhere in the same header. The MMEA priority/address-normalization fields in this chunk are adjacent to those RAS-visible MMEA blocks and share the same register address space.
- Debug and validation tools can use the DAGB fatal-error, FIFO, credit, pending, and performance-counter field definitions to decode MMHUB hangs, traffic stalls, or bandwidth anomalies.

## Risks And Edge Cases

- The chunk boundaries split registers. `DAGB5_RD_ADDR_DAGB_MAX_BURST0` begins before line 9436, so this chunk only contains the tail masks for clients 6 and 7. `MMEA0_ADDRNORMGMI_HOLE_CNTL` begins at line 11789 but its fields are in the next chunk. Merge/reconciliation must not treat either partial register as complete based only on this file.
- Hardware contract drift is the main risk. A stale mask or shift can program the wrong client, VC, credit, urgency coefficient, fabric ID, base/limit address, or clear/status bit.
- Many fields are packed repeated lanes. Off-by-one client numbering or using a client 0-15 register where a client 16-31 register is required can silently modify the wrong arbitration group or priority mask.
- Address-normalization masks are high impact. Misprogramming `ADDR_RNG_VAL`, interleave fields, fabric destination IDs, base/limit addresses, hole controls, or high-address offsets can cause bad routing, memory holes, failed access to VRAM/system memory, or device hangs.
- Credit and OSD limiter fields can throttle or deadlock traffic if programmed outside valid hardware ranges. The header provides masks but does not validate maximum legal values or ordering between pool, VC, IO, GMI, TLB, and data credits.
- Clock-gating/light-sleep override fields can alter power behavior and timing. Incorrect read-modify-write code may disable intended gating or force hardware subblocks on/off unexpectedly.
- Fatal-error and clear/status fields require semantic care. The presence of masks for `CLEAR`, `VALID`, `FED`, `NACK`, and operation/status fields does not define whether writes are pulse, level, clear-on-write, or read-only.
- Similar `DAGB*` and `MMEA*` names exist across MMHUB generations. Consumers must use the MMHUB 1.7 offset and mask headers together; mixing with MMHUB 1.0, 1.8, 9.4, or 9.3.0 masks can compile but produce wrong register programming.

## Test And Validation Signals

There are no direct unit tests for these generated macro definitions. Useful validation signals are integration-level and hardware/static consistency checks:

- Build coverage for AMDGPU files that include `mmhub_1_7_sh_mask.h`, especially `amdgpu/mmhub_v1_7.c` and the `gmc_v9_0.c` paths that select MMHUB 1.7 functions.
- Static generated-header checks: every complete field should have both a `__SHIFT` and `_MASK`, single-bit masks should match the shift, contiguous multi-bit masks should collapse to dense low-bit fields after shifting, and repeated client/group lanes should follow the expected 2-bit, 4-bit, or 8-bit stride.
- Register namespace consistency against `mmhub_1_7_offset.h`: `regDAGB5_*`/`mmDAGB5_*` and `regMMEA0_*` offsets should exist for mask families used by driver code or diagnostic tooling.
- MMHUB bring-up smoke tests should initialize GART, VMID, cache/TLB, invalidation, fault, and clock-gating paths without invalid MMIO access warnings or hangs.
- Hardware validation can program DAGB performance counters, use result-control start/stop/clear fields, and verify low/high counters move and clear as expected.
- Stress tests that generate MMHUB traffic should avoid persistent `DAGB5_*_PENDING`, FIFO full, credit full, or fatal-error status after normal operation.
- RAS and hang diagnostics should correctly decode fatal error address, CID, VF/VFID, operation, NACK, and FED fields when errors are injected or observed on supported hardware.
- Address-normalization validation should check that DRAM/GMI ranges, interleaving, fabric IDs, holes, and high-address offsets match firmware/BIOS expectations and do not break VRAM/system-memory access.

## Chunk Notes For Merge Lane

This is one source-tree-aligned chunk of `mmhub_1_7_sh_mask.h`, not a final whole-file report. In whole-file reconciliation, combine it with neighboring chunks for the complete `DAGB5_RD_ADDR_DAGB_MAX_BURST0` and `MMEA0_ADDRNORMGMI_HOLE_CNTL` definitions. The main contribution of this range is late `DAGB5` read/write arbitration, DAGB5 diagnostics/perf/fatal-error masks, and the beginning of `MMEA0` DRAM/GMI arbitration plus address-normalization masks.

### subset-b-002763: lines 11790-14143

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mmhub/mmhub_1_7_sh_mask.h lines 11790-14143

## Scope

This chunk is part of the generated AMDGPU MMHUB 1.7 shift/mask header. It contains C preprocessor constants for register bit fields, not executable routines. The constants define `__SHIFT` and `_MASK` values consumed with matching register offsets from `mmhub_1_7_offset.h` and AMDGPU register access helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, and direct masked writes.

The covered range starts mid-register at `MMEA0_ADDRNORMGMI_HOLE_CNTL`, continues through most of `addressBlock: mmhub_ea_mmeadec0`, and ends in the early `addressBlock: mmhub_ea_mmeadec1` GMI read client-to-group map. The main functional surfaces are MMEA0 address normalization/decode, MMEA0 IO request grouping and arbitration, MMEA0 SDP arbitration/credits/error handling, and MMEA1 DRAM/GMI arbitration masks.

## Purpose

MMEA appears to be an MMHUB memory-client endpoint/address-decode block. These macros describe how firmware or driver code can program address decoding, client grouping, priorities, credits, error reporting, and clock/error-injection behavior for MMHUB 1.7 hardware. Because this is a register-definition header, its purpose is ABI-like: keep software field positions synchronized with the hardware register specification for this ASIC generation.

The chunk is especially important for memory topology and quality-of-service programming:

- `MMEA0_ADDRNORM*` and `MMEA0_ADDRDEC*` fields define how normalized addresses become DRAM/GMI chip-select, bank, row, column, rank-mirror, and channel selections.
- `MMEA0_IO_*` and `MMEA1_DRAM_*` fields map client IDs into four arbitration groups and tune group age, queuing, fixed-priority, urgency, and quantized priority thresholds.
- `MMEA0_SDP_*` fields control final request arbitration, virtual-channel credit/tag reservation, request block/pass behavior, and error escalation.
- `MMEA0_EDC*`, `MMEA0_DSM*`, and `MMEA0_ERR_STATUS` fields expose error-detection counters/status and hardware diagnostic/error-injection controls.

## Important Macro Families

Address normalization and decode:

- `MMEA0_ADDRNORMGMI_HOLE_CNTL` exposes DRAM hole validity and offset fields.
- `MMEA0_ADDRNORMDRAM_NP2_CHANNEL_CFG` and `MMEA0_ADDRNORMGMI_NP2_CHANNEL_CFG` define log2 non-power-of-two channel address spaces.
- `MMEA0_ADDRDEC_BANK_CFG`, `MMEA0_ADDRDEC_MISC_CFG`, `MMEA0_ADDRDECDRAM_HARVEST_ENABLE`, and `MMEA0_ADDRDECGMI_HARVEST_ENABLE` describe DRAM/GMI bank masks, bank-group selection/interleave, VCM enable bits, pseudo-channel/channel/chip-select/rank-mirror masks, and forced harvested bits.
- `MMEA0_ADDRDEC{0,1,2}_*` define three parallel address-decode channels. Each channel has primary and secondary chip-select base registers, masks for CS01/CS23 and SECCS01/SECCS23, geometry config (`NUM_BANK_GROUPS`, `NUM_RM`, row/column/bank counts, `HI_COL_EN`), bank/row selectors, optional `BANK5` and `CHAN_BIT` selectors, column low/high selectors, and rank-mirror selectors with row-MSB inversion.
- `MMEA0_ADDRNORM_MEGACONTROL_ADDR{0,1}`, `MMEA0_ADDRNORMDRAM_MASKING`, `MMEA0_ADDRNORMGMI_MASKING`, and `MMEA0_ADDRDEC_SELECT` provide wider selection/masking controls for normalized address high bits and channel ranges.

IO arbitration and grouping for MMEA0:

- `MMEA0_IO_RD_CLI2GRP_MAP{0,1}` and `MMEA0_IO_WR_CLI2GRP_MAP{0,1}` pack 32 client IDs into 2-bit group fields, with client IDs 0-15 in map0 and 16-31 in map1.
- `MMEA0_IO_RD_COMBINE_FLUSH` and `MMEA0_IO_WR_COMBINE_FLUSH` define per-group combine-flush timers and combine mode.
- `MMEA0_IO_GROUP_BURST` defines low/high burst limits for read and write IO traffic.
- `MMEA0_IO_*_PRI_AGE`, `MMEA0_IO_*_PRI_QUEUING`, `MMEA0_IO_*_PRI_FIXED`, `MMEA0_IO_*_PRI_URGENCY`, `MMEA0_IO_*_PRI_URGENCY_MASKING`, and `MMEA0_IO_*_PRI_QUANT_PRI{1,2,3}` provide group-based arbitration inputs: aging rates, age coefficients, queuing coefficients, fixed coefficients, urgency coefficients/modes, per-client urgency masks, and quantized priority thresholds.

SDP/final request path:

- `MMEA0_SDP_ARB_DRAM`, `MMEA0_SDP_ARB_GMI`, and `MMEA0_SDP_ARB_FINAL` describe burst limits, early read/write switch controls, end-of-burst behavior, read-only virtual-channel flags, GMI burst stretching, throttles, and error escalation bits such as `ERREVENT_ON_ERROR` and `HALTREQ_ON_ERROR`.
- `MMEA0_SDP_DRAM_PRIORITY`, `MMEA0_SDP_GMI_PRIORITY`, and `MMEA0_SDP_IO_PRIORITY` pack 4-bit read/write priorities for groups 0-3.
- `MMEA0_SDP_CREDITS`, `MMEA0_SDP_TAG_RESERVE{0,1}`, `MMEA0_SDP_VCC_RESERVE{0,1}`, and `MMEA0_SDP_VCD_RESERVE{0,1}` define tag, response, and per-virtual-channel credit reservation fields.
- `MMEA0_SDP_REQ_CNTL` has pass/chain override bits for reads, writes, atomics, DRAM, and GMI plus request block levels.

Observability, error, diagnostics, and clock control:

- `MMEA0_LATENCY_SAMPLING`, `MMEA0_PERFCOUNTER_LO`, `MMEA0_PERFCOUNTER_HI`, `MMEA0_PERFCOUNTER{0,1}_CFG`, and `MMEA0_PERFCOUNTER_RSLT_CNTL` support sampling and performance-counter configuration/result handling.
- `MMEA0_EDC_CNT`, `MMEA0_EDC_CNT2`, and `MMEA0_EDC_CNT3` expose SEC/SED/DED count fields for DRAM, GMI, IO, return tag, and MAM memories.
- `MMEA0_DSM_CNTL`, `MMEA0_DSM_CNTLA`, `MMEA0_DSM_CNTL2`, and `MMEA0_DSM_CNTL2A` define diagnostic single-write and error-injection controls for command/data/page/tag memories. `MMEA0_DSM_CNTLB` and `MMEA0_DSM_CNTL2B` are present as empty register comments in this chunk.
- `MMEA0_CGTT_CLK_CTRL` exposes clock-gating timing, soft stall overrides, light-sleep override, and soft read/write/return/register overrides.
- `MMEA0_EDC_MODE` and `MMEA0_ERR_STATUS` define fatal/uncorrectable error behavior, propagation/gating/bypass, error clearing, busy-on-error behavior, interrupt controls, and response status fields.
- `MMEA0_MISC`, `MMEA0_MISC2`, and `MMEA0_MISC_AON` contain miscellaneous arbitration, early write-return, request blocking, chip-select group swap, IO read/write priority enable, return swap, and link manager partial-ack fields.

MMEA1 block start:

- The range switches to `addressBlock: mmhub_ea_mmeadec1` near the end.
- `MMEA1_DRAM_RD_CLI2GRP_MAP{0,1}` and `MMEA1_DRAM_WR_CLI2GRP_MAP{0,1}` repeat the 32-client, 2-bit group mapping scheme for DRAM reads and writes.
- `MMEA1_DRAM_RD_GRP2VC_MAP` and `MMEA1_DRAM_WR_GRP2VC_MAP` map groups 0-3 to virtual channels.
- `MMEA1_DRAM_RD_LAZY`, `MMEA1_DRAM_WR_LAZY`, `MMEA1_DRAM_RD_CAM_CNTL`, `MMEA1_DRAM_WR_CAM_CNTL`, and `MMEA1_DRAM_PAGE_BURST` control lazy timer/max burst behavior, client CAM address/mask, match enable/update policy, and page burst limits.
- `MMEA1_DRAM_*_PRI_*` mirror the MMEA0 arbitration scheme for DRAM traffic: age, queuing, fixed, urgency, and quantized priority thresholds.
- The chunk ends after `MMEA1_GMI_RD_CLI2GRP_MAP1` begins, so the rest of MMEA1 GMI and later MMEA1 controls are cross-chunk dependencies.

## Control Flow and Data Flow

There is no runtime control flow in this header. At build time, the preprocessor exposes named bit positions and masks. At runtime, driver or firmware-facing code uses these macros to compose 32-bit register values, write MMIO registers, and decode readback/status values.

Typical flow implied by the macros:

1. Include `mmhub_1_7_offset.h` for register addresses and this header for fields.
2. Build register values by shifting field values by `__SHIFT` and applying `_MASK`, usually through AMDGPU helper macros.
3. Program address decode before memory traffic is enabled or when topology changes require updated channel/chip-select/bank mapping.
4. Program arbitration/group/credit controls before sustained traffic or power/performance transitions.
5. Read status/performance/error registers and extract fields using the masks.
6. For diagnostics, set DSM/error-injection controls, observe EDC counters/status, and clear error status through `CLEAR_ERROR_STATUS`.

## State and Persistence Behavior

The header itself has no state. The state represented by these fields lives in hardware MMIO registers. Register writes persist in the hardware block until reset, power-gating domain loss, driver reinitialization, suspend/resume restoration, or explicit reprogramming.

Several fields represent durable hardware configuration while the GPU is running:

- Address-decode base/mask/geometry/selector fields affect all subsequent address routing for the programmed channels.
- Client-to-group maps and priority coefficients persistently shape arbitration and QoS decisions.
- Credit/tag/VC reservation fields persistently affect outstanding request capacity and fairness.
- Diagnostic and error-injection bits can persist long enough to corrupt normal execution if left enabled outside controlled tests.
- Status and counter fields are hardware-observed state; some may be sticky or clear-on-write depending on the register spec. This chunk exposes the bit names but not write/clear semantics beyond visible names such as `CLEAR_ERROR_STATUS`.

## Dependencies and Integration Points

This chunk depends on the adjacent generated MMHUB headers:

- `mmhub_1_7_offset.h` provides the matching `reg...` addresses and base indices.
- Other chunks of `mmhub_1_7_sh_mask.h` provide the preceding MMEA0 fields, earlier DAGB fields, and the remainder of MMEA1 fields.
- AMDGPU register helper macros in the DRM AMD driver infrastructure consume the `REG__FIELD__SHIFT` and `REG__FIELD_MASK` naming convention.

Integration points are hardware-generation-specific. These masks should only be used by code paths that select MMHUB 1.7 register tables. Similar register names appear in other MMHUB generation headers, but bit layouts can differ, for example bank-mask widths and optional VCM/hash fields differ across ASIC versions. Code must not mix offsets from one MMHUB version with masks from another.

The register groups integrate with:

- GPU memory controller/topology setup through address decode and normalized-address controls.
- MMHUB arbitration and QoS policy through client group maps, priorities, credits, and virtual-channel controls.
- Power management through clock-gating override controls.
- RAS/EDC diagnostics through counters, status, error propagation/interrupt controls, and DSM/error-injection knobs.
- Performance tooling through latency sampling and performance counter fields.

## Risks and Edge Cases

- Incorrect address-decode masks, base addresses, chip-select enables, channel bits, bank selectors, row/column selectors, or rank-mirror inversion fields can route memory traffic incorrectly and cause data corruption or hangs.
- Programming DRAM/GMI/IO arbitration fields with mismatched client-group maps and priority coefficients can starve clients, reduce throughput, or break latency assumptions.
- Credit and tag-reservation values are capacity controls; bad values can deadlock, throttle, or overcommit the SDP path.
- Error-injection and DSM single-write fields are hazardous outside diagnostic sequences. Leaving them enabled can create artificial EDC events or corrupt internal memories.
- `MMEA0_ERR_STATUS` includes interrupt and busy-on-error controls; wrong configuration can either hide fatal faults or hold the block busy after an error.
- Empty comment-only registers such as `MMEA0_DSM_CNTLB` and `MMEA0_DSM_CNTL2B` should not be assumed to have no hardware behavior; they may be reserved or defined elsewhere in the hardware spec, but this header chunk provides no field macros for them.
- The chunk boundary splits MMEA1 GMI definitions after `MMEA1_GMI_RD_CLI2GRP_MAP1`. Whole-file research must reconcile later chunks before describing the full MMEA1 GMI path.
- Generated headers are easy to use mechanically but hard to validate by inspection. A one-bit shift/mask error can compile cleanly and only surface as hardware malfunction.

## Test and Verification Signals

Useful validation signals for this chunk are mostly integration and hardware tests rather than unit tests:

- Compile coverage for MMHUB 1.7 paths that include this header and use `REG_SET_FIELD`/`REG_GET_FIELD` with these macro names.
- Register readback tests after programming address-decode, arbitration, and credit fields, checking that packed values decode to the intended field values.
- GPU bring-up tests that exercise VRAM/DRAM and GMI traffic across all enabled channels/chip-selects, including harvested configurations and non-power-of-two channel spaces.
- Stress tests with mixed IO, DRAM, GMI, read, write, and atomic traffic to expose bad priority, urgency, credit, or virtual-channel programming.
- RAS/EDC diagnostic tests that intentionally inject errors through `MMEA0_DSM_CNTL2*`, observe `MMEA0_EDC_CNT*` and `MMEA0_ERR_STATUS`, then clear and verify recovery behavior.
- Suspend/resume and power-gating tests to ensure persistent hardware configuration is restored after domain loss.
- Cross-version register audit comparing `mmhub_1_7_offset.h` against this mask header and ensuring callers selected the matching MMHUB 1.7 tables.

## Cross-Chunk Notes

This chunk begins after the first line of `MMEA0_ADDRNORMGMI_HOLE_CNTL`; the register comment and any preceding fields are in the prior chunk. It ends inside the MMEA1 GMI client-group map area, so the remainder of MMEA1 GMI arbitration, MMEA1 SDP/error/diagnostic fields, and any later address blocks must be researched from subsequent chunks before producing a final per-file document.

### subset-b-002764: lines 14144-16497

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mmhub/mmhub_1_7_sh_mask.h lines 14144-16497

## Scope And Purpose

This chunk is a generated AMDGPU MMHUB 1.7 register bitfield header slice. It contains preprocessor constants only: `<REGISTER>__<FIELD>__SHIFT` and `<REGISTER>__<FIELD>_MASK` definitions for the `MMEA1` register range. There are no functions, structs, storage objects, loops, branches, or runtime side effects in this source range.

The macros describe how software should encode and decode 32-bit MMHUB MMIO register values for the second memory-management engine aperture/range (`MMEA1`). The covered register families span GMI request grouping and arbitration, address normalization and address decode, IO request grouping and priority, SDP arbitration and credit controls, miscellaneous local controls, latency/performance counter controls, RAS/EDC counters, and diagnostic/error-injection controls. These definitions are meant to be paired with register offset macros from `mmhub_1_7_offset.h` and access helpers in AMDGPU MMHUB code.

The chunk begins in the tail of `MMEA1_GMI_RD_CLI2GRP_MAP1` and ends after `MMEA1_DSM_CNTL2`. Adjacent chunks are needed for a complete whole-register view of the first and last registers.

## Important APIs, Types, And Constants

There are no callable APIs or C types in this range. The interface is the macro namespace consumed by C code through register-field helpers such as `SOC15_REG_FIELD()` and read/modify/write code.

Important macro groups in this chunk:

- `MMEA1_GMI_RD_CLI2GRP_MAP1`, `MMEA1_GMI_WR_CLI2GRP_MAP0`, and `MMEA1_GMI_WR_CLI2GRP_MAP1`: two-bit client-ID-to-group mappings. `CID0` through `CID31` are packed at two-bit intervals, allowing read/write GMI request clients to be assigned to one of four groups.
- `MMEA1_GMI_RD_GRP2VC_MAP` and `MMEA1_GMI_WR_GRP2VC_MAP`: three-bit group-to-virtual-channel selectors for four GMI groups.
- `MMEA1_GMI_RD_LAZY` and `MMEA1_GMI_WR_LAZY`: request accumulation and lazy dispatch controls. The fields include per-group delays plus `REQ_ACCUM_THRESH`, `REQ_ACCUM_TIMEOUT`, and `REQ_ACCUM_IDLEMAX`.
- `MMEA1_GMI_RD_CAM_CNTL` and `MMEA1_GMI_WR_CAM_CNTL`: per-group CAM depth and reorder-limit fields, plus `REFILL_CHAIN` and `PAGEBASED_CHAINING` control bits.
- `MMEA1_GMI_PAGE_BURST`: read/write page burst low/high limits for GMI paths.
- `MMEA1_GMI_RD_PRI_*` and `MMEA1_GMI_WR_PRI_*`: age, queuing, fixed priority, urgency, urgency masking, and quantum priority layouts. These fields tune how GMI reads and writes age, queue, mask urgent clients, and map request groups into priority classes.
- `MMEA1_ADDRNORM_*`: base/limit/offset and mega-base/mega-limit fields for normalized address ranges. These macros also define DRAM/GMI hole controls, non-power-of-two channel configuration, global controls, and masking controls.
- `MMEA1_ADDRDEC_*`: bank config, misc config, harvest enable masks, per-address-decoder base addresses, address masks, address config, address select fields, column select fields, and row/rank/misc select fields for decoder instances 0, 1, and 2. The naming covers normal and secondary chip-select forms such as `CS01`, `CS23`, `SECCS01`, and `SECCS23`.
- `MMEA1_IO_RD_CLI2GRP_MAP*` and `MMEA1_IO_WR_CLI2GRP_MAP*`: IO client-ID-to-group mappings that mirror the GMI two-bit-per-client scheme for IO read and write traffic.
- `MMEA1_IO_RD_COMBINE_FLUSH` and `MMEA1_IO_WR_COMBINE_FLUSH`: flush controls for IO request combining, including `GROUPx_FLUSH` fields and a `FORCE_COMBINE_FLUSH` bit.
- `MMEA1_IO_GROUP_BURST`, `MMEA1_IO_RD_PRI_*`, and `MMEA1_IO_WR_PRI_*`: IO-side burst, aging, queueing, fixed priority, urgency, urgency masking, and priority quantum layouts.
- `MMEA1_SDP_ARB_DRAM`, `MMEA1_SDP_ARB_GMI`, and `MMEA1_SDP_ARB_FINAL`: scheduler/arbitration fields for DRAM, GMI, and final arbitration. Fields include read/write priority, round-robin enable bits, no-starve controls, write-combine controls, and starve thresholds.
- `MMEA1_SDP_{DRAM,GMI,IO}_PRIORITY`, `MMEA1_SDP_CREDITS`, `MMEA1_SDP_TAG_RESERVE*`, `MMEA1_SDP_VCC_RESERVE*`, `MMEA1_SDP_VCD_RESERVE*`, and `MMEA1_SDP_REQ_CNTL`: request-class priorities, credit limits, tag and virtual-channel reserve fields, and request mode controls.
- `MMEA1_MISC`: operational and debug control bits for channel masks, urgent propagation, timeout or stall behavior, write-combine behavior, and clock/power related toggles.
- `MMEA1_LATENCY_SAMPLING`: latency sampling control, address/source matching, mode selection, and threshold/counter fields for observing MMHUB request latency.
- `MMEA1_PERFCOUNTER_LO`, `MMEA1_PERFCOUNTER_HI`, `MMEA1_PERFCOUNTER0_CFG`, `MMEA1_PERFCOUNTER1_CFG`, and `MMEA1_PERFCOUNTER_RSLT_CNTL`: 64-bit performance counter result fields and control fields for event selection, modes, enable/clear, trigger selection, global enable, global clear, and stop-on-saturation behavior.
- `MMEA1_EDC_CNT` and `MMEA1_EDC_CNT2`: two-bit packed error counters for SEC, DED, and SED events across DRAM read/write command memory, write data memory, return tag memory, IO command/data memory, GMI command/page/data memory, and MAM D0-D3 memories.
- `MMEA1_DSM_CNTL` and `MMEA1_DSM_CNTLA`: diagnostic single-write/DSM irritator data controls for command, data, page, return-tag, IO, GMI, and MAM-related memories.
- `MMEA1_DSM_CNTLB`: present only as a register comment in this line range; no fields are defined in this chunk.
- `MMEA1_DSM_CNTL2`: diagnostic error-injection enables and injection-delay selectors for DRAM, return-tag, GMI command, and GMI write data memories, plus a shared `INJECT_DELAY` field.

## Control Flow And State Behavior

This header chunk has no local control flow. Its contribution is compile-time substitution: consumers include the header, combine a register offset with a mask/shift pair, and then read, write, or decode a hardware register.

Runtime state is entirely in the GPU MMHUB hardware. The `MMEA1` registers described here influence how MMHUB routes and prioritizes memory traffic, how addresses are normalized and decoded, how SDP arbitration allocates credits and reserves tags/virtual channels, how performance and latency sampling are configured, and how RAS diagnostic counters or injection controls are interpreted.

Persistence is hardware-defined. Programmed arbitration, priority, address-decode, diagnostic, and performance-counter values can persist until overwritten by driver/firmware, reset by GPU reset, cleared by counter-control bits, or lost during power-gating/suspend/resume depending on the register block. The header does not cache values, manage ownership, serialize access, or provide restore sequencing.

The most visible consumer in this source tree is `drivers/gpu/drm/amd/amdgpu/mmhub_v1_7.c`. That file includes both `mmhub_1_7_offset.h` and this mask header, then builds RAS error counter tables with `SOC15_REG_ENTRY(MMHUB, 0, regMMEA1_EDC_CNT*)` and `SOC15_REG_FIELD(MMEA1_EDC_CNT*, ...)`. The field macros from this chunk therefore become metadata for extracting packed SEC/DED/SED counts from EDC counter registers.

## Dependencies And Integration Points

This chunk depends on matching MMHUB 1.7 register address definitions. The mask header alone cannot access hardware; it must be paired with `regMMEA1_*` offsets and base-index macros in `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mmhub/mmhub_1_7_offset.h`.

Primary integration points:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/mmhub_v1_7.c` includes `mmhub/mmhub_1_7_sh_mask.h`, `mmhub/mmhub_1_7_offset.h`, `soc15_common.h`, and `soc15.h`. Register access is routed through SOC15 helpers such as `RREG32_SOC15`, `WREG32_SOC15`, and table helpers such as `SOC15_REG_ENTRY` and `SOC15_REG_FIELD`.
- The `MMEA1_EDC_CNT` and `MMEA1_EDC_CNT2` fields are used by the MMHUB RAS error-query table. Entries name memory blocks such as `MMEA1_DRAMRD_CMDMEM`, `MMEA1_GMIRD_CMDMEM`, `MMEA1_GMIWR_DATAMEM`, and `MMEA1_MAM_D0MEM`, then associate each with SEC/DED/SED field masks from this chunk.
- Adjacent generated MMHUB headers provide equivalent `MMEA0`, `MMEA2`, and later `MMEA1_EDC_CNT3` definitions. The C consumer treats these ranges as a repeated hardware pattern, so consistency across generated macro names matters.
- GMI and IO grouping/priority fields are integration surfaces for firmware or driver initialization code that programs request classes. Even when not directly referenced by current C code in this repository snapshot, these macros document the hardware ABI used by register dumps, bring-up scripts, diagnostics, or future MMHUB tuning paths.
- Performance counter and latency sampling fields integrate with MMHUB debug/perf tooling. A caller must use the offset header to select `regMMEA1_PERFCOUNTER*` or `regMMEA1_LATENCY_SAMPLING`, and then use these masks to preserve unrelated bits during read-modify-write.
- DSM and error-injection fields are diagnostic/RAS-facing. They should only be used by carefully gated test paths, because they can deliberately perturb hardware memory structures.

## Risks And Edge Cases

- Hardware contract drift is the main risk. These constants must match the MMHUB 1.7 register specification exactly; an incorrect mask or shift can silently program the wrong arbitration class, decode the wrong address bits, corrupt performance counter configuration, or misreport RAS error counts.
- This chunk starts mid-register and ends before the next DSM register family is complete. Line 14144 is already inside `MMEA1_GMI_RD_CLI2GRP_MAP1`, and line 16497 ends with `MMEA1_DSM_CNTL2`. The merge lane should avoid treating this chunk as a complete `MMEA1` description.
- Many fields are tightly packed two-bit or three-bit values. Callers must mask and shift unsigned 32-bit values; signed arithmetic or host-width assumptions can break high-bit fields such as `0xC0000000L`, `0xFC000000L`, and `0xFF000000L`.
- Several register families have read and write variants with nearly identical field names. Mechanical edits can easily swap `RD` and `WR`, `GMI` and `IO`, or `DRAM` and `GMI`, which would compile but alter the wrong traffic path.
- `MMEA1_ADDRDEC*` macros are repetitive across decoder instances and chip-select pairs. Incorrectly mixing `ADDRDEC0`, `ADDRDEC1`, or `ADDRDEC2` fields, or `CS01` versus `CS23`, could produce invalid address interleave or harvesting behavior.
- RAS counters are packed into two-bit fields. Saturation, clear-on-read, or clear-by-control semantics are not described in the header; consumers must follow the MMHUB RAS code and hardware specification when accumulating or clearing counts.
- Performance counter and latency-sampling configuration can be destructive to in-flight debug sessions. The result-control fields include clear and stop-on-saturation bits, so callers should preserve unrelated fields and coordinate with other performance tooling.
- DSM and error-injection fields deliberately alter memory diagnostic behavior. Accidentally enabling injection or single-write irritator controls can create artificial SEC/DED/SED events or destabilize the MMHUB path during normal operation.

## Test And Validation Signals

There are no direct unit tests for these preprocessor definitions. Practical validation is integration and hardware oriented:

- Build coverage for `drivers/gpu/drm/amd/amdgpu/mmhub_v1_7.c` with this header included, especially the RAS table entries that use `SOC15_REG_FIELD(MMEA1_EDC_CNT, ...)` and `SOC15_REG_FIELD(MMEA1_EDC_CNT2, ...)`.
- Static generation checks can verify that every `_MASK` aligns with its matching `__SHIFT`, that repeated `CID` mappings advance by two bits, that group-to-VC fields advance by three bits, and that full-width result fields use shift zero with `0xffffffffL`.
- Cross-header checks should compare `MMEA1_*` mask names against `regMMEA1_*` offsets in `mmhub_1_7_offset.h`; missing offset/mask pairs indicate incomplete generation or a register that cannot be accessed symbolically.
- RAS runtime validation should confirm that MMHUB v1.7 error-query paths report expected SEC/DED/SED counters for `MMEA1_EDC_CNT` and `MMEA1_EDC_CNT2`, and that clear paths do not leave stale counts.
- Register-dump or debugfs validation can exercise performance counter and latency sampling fields by programming event selection, clearing counters, reading low/high result registers, and confirming that unrelated bits remain unchanged.
- Hardware bring-up or firmware validation should cover GMI/IO arbitration programming, address normalization/address decode layouts, and SDP credit/reserve settings under memory stress, suspend/resume, and GPU reset.

## Chunk Notes For Merge Lane

This is one chunk of a very large generated MMHUB 1.7 mask header. Merge with adjacent chunks before producing final whole-file conclusions, especially because this chunk begins after the start of `MMEA1_GMI_RD_CLI2GRP_MAP1` and stops before subsequent DSM/control families. The source-tree-aligned output for this item is this chunk document only.

### subset-b-002765: lines 16498-18857

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mmhub/mmhub_1_7_sh_mask.h lines 16498-18857

## Scope And Purpose

This chunk is a generated-style AMD MMHUB 1.7 register shift/mask header slice. It contains only C preprocessor constants that describe bit positions and masks for memory-mapped MMHUB registers. There are no functions, structs, enums, storage objects, or local executable paths in this line range.

The slice starts in the tail of `MMEA1_DSM_CNTL2` masks and then covers `MMEA1` controls for error injection, clock gating, EDC/error status, miscellaneous arbitration, address-decode selection, and always-on link-manager timing. Most of the range is the `// addressBlock: mmhub_ea_mmeadec2` block, which defines `MMEA2` arbitration, address normalization, address decode, GMI, DRAM, and IO priority fields. The range ends in the middle of `MMEA2_IO_WR_PRI_URGENCY_MASKING`, after CID26 shift definitions and before the remaining fields for that register.

The purpose of these macros is to let AMDGPU code form and decode MMIO register values with helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `SOC15_REG_FIELD`, `RREG32_SOC15`, and `WREG32_SOC15`, while register addresses come from the paired `mmhub_1_7_offset.h` header.

## Important APIs, Types, And Constants

This chunk exports constants rather than APIs. The macro naming contract is `<REGISTER>__<FIELD>__SHIFT` for bit positions and `<REGISTER>__<FIELD>_MASK` for corresponding register masks.

Important register families in this slice are:

- `MMEA1_DSM_CNTL2` tail and `MMEA1_DSM_CNTL2A`: error-injection controls for GMI read/write command memory, GMI write data memory, page memory, IO command/data memory, DRAM read/write page memory, and an injection-delay selector. `MMEA1_DSM_CNTL2B` appears only as an empty register marker in this range.
- `MMEA1_CGTT_CLK_CTRL`: memory-client clock-gating timing and overrides, including on delay, off hysteresis, soft stall overrides for write/read/return paths, light-sleep override, and soft override bits.
- `MMEA1_EDC_MODE`, `MMEA1_ERR_STATUS`, and `MMEA1_EDC_CNT3`: EDC behavior, fatal/uncorrectable status propagation, clear/error/busy status bits, interrupt policy bits, and DED count fields for DRAM, IO, and GMI page/command memories.
- `MMEA1_MISC2`, `MMEA1_ADDRDEC_SELECT`, and `MMEA1_MISC_AON`: arbitration swaps, burst limits, IO read/write priority enablement, request blocking/status, DRAM/GMI channel range selection, and always-on link-manager part-ack hysteresis/deassert mode.
- `MMEA2_DRAM_*`: DRAM read/write client-to-group maps for CIDs 0-31, group-to-VC maps, lazy request accumulation timers and thresholds, CAM depth/reorder/refill controls, page burst limits, and age/queue/fixed/urgency/quantum-priority coefficients.
- `MMEA2_GMI_*`: the same group mapping, lazy, CAM, page burst, age, queue, fixed, urgency, quantum-priority, and per-CID urgency masking surfaces for GMI traffic. GMI CAM control adds `PAGEBASED_CHAINING` along with refill-chain control.
- `MMEA2_ADDRNORM*` and `MMEA2_ADDRDEC*`: address range validation, legacy MMIO hole enablement, interleave topology fields, base/limit/offset and mega-base/mega-limit ranges, DRAM/GMI hole controls, non-power-of-two channel config, bank and bank-group selection, harvest enable overrides, and three repeated address-decode sets (`ADDRDEC0`, `ADDRDEC1`, `ADDRDEC2`) with chip-select base addresses, masks, row/column/bank/RM selections, secondary chip-select selections, and row-MSB inversion controls.
- `MMEA2_IO_*`: IO read/write client-to-group maps, combine-flush controls for CIDs, group burst limits, age/queue/fixed/urgency coefficients, urgency modes, and per-CID urgency masks. This chunk cuts off before the full write urgency-masking register is visible.

Representative layouts include two-bit client group fields packed across 32 CIDs, three-bit group coefficient fields for four groups, 8-bit burst/threshold lanes, single-bit control/status masks, and full upper-bit address masks such as `0xFFFFFFFEL` for base/mask registers with enable at bit 0.

## Control Flow And State Behavior

There is no local control flow in this header. Runtime control flow exists in consumers that include this header and the paired offset header.

In `amdgpu/mmhub_v1_7.c`, the MMHUB 1.7 code includes `mmhub/mmhub_1_7_offset.h` and `mmhub/mmhub_1_7_sh_mask.h`, then programs VM, aperture, TLB, cache, snoop, and power-management registers through SOC15 register helpers. The MMEA EDC and error-status families are integrated with the RAS path: `mmhub_v1_7_ras_fields` uses `SOC15_REG_FIELD(...)` entries for MMEA EDC counters, `mmhub_v1_7_query_ras_error_count()` decodes those counters, and `mmhub_v1_7_query_ras_error_status()` reads EA error-status registers and checks `SDP_RDRSP_STATUS`, `SDP_WRRSP_STATUS`, and `SDP_RDRSP_DATAPARITY_ERROR`.

The state represented here is hardware state. Error injection, EDC mode, error status, clock gating, arbitration, address normalization/decode, and priority coefficients persist in the MMHUB register file until reset, power-gating loss, firmware/driver reprogramming, or explicit counter/status clear operations. The header does not cache values, validate field ranges, serialize MMIO accesses, or define reset sequencing.

Some fields are configuration state, such as client-to-group maps, address-decode selectors, lazy thresholds, CAM depths, and priority coefficients. Others are status or command-like fields, such as `REQUESTS_BLOCKED`, `CLEAR_ERROR_STATUS`, EDC counters, combine-flush CIDs, and error-injection enable/delay bits. Correct read-modify-write semantics are owned by the hardware specification and by AMDGPU call sites, not by these masks.

## Dependencies And Integration Points

The direct companion for this chunk is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mmhub/mmhub_1_7_offset.h`, which provides `regMMEA1_*` and `regMMEA2_*` offsets matching these masks. `amdgpu/mmhub_v1_7.c` is the primary in-tree MMHUB 1.7 consumer.

Register access integrates through the SOC15 AMDGPU register layer: `SOC15_REG_ENTRY`, `SOC15_REG_FIELD`, `SOC15_REG_ENTRY_OFFSET`, `RREG32`, `WREG32`, `RREG32_SOC15`, `WREG32_SOC15`, and offset variants. Field packing and unpacking integrate through `REG_SET_FIELD` and `REG_GET_FIELD`.

RAS integration is visible for the MMEA EDC and error-status blocks. The driver enumerates MMEA0-MMEA5 EDC counters, including MMEA2 counters whose related page-memory DED fields are represented in this header family, and it resets counters by writing zero to EDC counter registers. EA status registers are queried and cleared as part of MMHUB RAS operations.

The arbitration and address-decode definitions in this chunk are lower-level hardware contract surfaces. They are expected to be consumed by initialization tables, firmware handoff flows, debug tooling, or future driver code that needs to inspect or program MMHUB EA decode behavior for DRAM, GMI, and IO traffic. Nearby generation headers (`mmhub_1_8_0_*`, `mmhub_9_*`) carry similar names with generation-specific differences, so include ordering and ASIC selection matter.

## Risks And Edge Cases

- The line range is not register-complete at either end: it begins after the start of `MMEA1_DSM_CNTL2` and ends before all `MMEA2_IO_WR_PRI_URGENCY_MASKING` fields and masks. Whole-file conclusions must merge adjacent chunks.
- A wrong shift or mask can silently program the wrong MMHUB bit. In this chunk the highest-impact cases are address-normalization/decode fields, client group mappings, priority/urgency masks, and error clear/injection bits.
- Similar MMEA names recur across MMHUB versions, but layouts are not guaranteed identical. For example, the same high-level error-status names differ across older `mmhub_1_0`/`mmhub_9_1` and newer MMHUB headers. Consumers must include the active ASIC generation's header.
- The mask header does not encode access type. Some bits may be read-only status, write-one-to-clear, pulse commands, sticky counters, or reserved fields. Generic read-modify-write code can accidentally clear sticky status, enable injection, or preserve invalid reserved bits.
- Address decode fields pack topology assumptions into small bitfields: chip-select enables, base/mask values, row/column/bank/RM selections, interleave counts, hole controls, and harvest overrides. Invalid combinations can lead to incorrect memory routing, lost memory ranges, or GPU hangs.
- Per-CID priority and urgency masks cover many clients. Misprogramming can starve a client, mask urgent traffic, over-prioritize IO, or perturb DRAM/GMI arbitration in ways that are difficult to diagnose from software logs alone.
- RAS decoding depends on fields matching hardware counter positions. If masks drift, CE/UE accounting may undercount, overcount, or attribute errors to the wrong MMEA subblock.

## Test And Validation Signals

There are no direct unit tests for these generated macros. Useful validation signals are integration-level:

- Build coverage of `amdgpu/mmhub_v1_7.c` with `mmhub_1_7_offset.h` and `mmhub_1_7_sh_mask.h` included, confirming all referenced `reg*` and field macros resolve.
- Static consistency checks for generated fields: single-bit masks should match `1u << shift`, packed multi-bit masks should be contiguous after shifting, full register/address fields should use expected low-bit enables and upper-bit masks, and repeated CID/group fields should follow the visible packing pattern.
- MMHUB RAS tests on supported hardware should exercise EDC counter reads, error-status reads, and reset paths. Expected signals include nonzero CE/UE counts decoded through `mmhub_v1_7_get_ras_error_count()`, EA warnings when status bits are set, and successful clearing through `CLEAR_ERROR_STATUS`.
- GART and VM initialization smoke tests should complete without MMHUB faults, invalid MMIO accesses, or protection-fault regressions, because the same header is included by the MMHUB 1.7 initialization path.
- Hardware bring-up or debug validation should inspect DRAM/GMI/IO arbitration fields, client-to-group maps, urgency masks, and address decode registers before and after firmware/driver programming to ensure only intended bits change.
- Stress tests that mix SDMA, graphics, display, peer/GMI, and CPU-visible IO traffic can expose priority, urgency, lazy accumulation, CAM depth, and page-burst misconfiguration through hangs, timeouts, RAS events, or performance anomalies.

## Chunk Notes For Merge Lane

Treat this as the MMEA1 tail plus the main `mmhub_ea_mmeadec2` MMEA2 slice of `mmhub_1_7_sh_mask.h`. The previous chunk is needed for the full `MMEA1_DSM_CNTL2` definition. The next chunk is needed for the remainder of `MMEA2_IO_WR_PRI_URGENCY_MASKING` and any following MMEA2 registers.

### subset-b-002766: lines 18858-21209

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mmhub/mmhub_1_7_sh_mask.h lines 18858-21209

## Scope

This chunk covers generated shift and mask macros from the AMD MMHUB 1.7 register mask header. It begins in the middle of `MMEA2_IO_WR_PRI_URGENCY_MASKING` and ends after the `MMEA3_ADDRDEC2_BASE_ADDR_SECCS0__CS_EN__SHIFT` definition, so both edges require adjacent chunks for complete register-family descriptions.

The covered range includes:

- The tail of MMEA2 IO write urgency masking for client IDs 27-31 and the complete 32-bit `CID*_MASK_MASK` layout.
- MMEA2 IO read/write priority quantum thresholds, SDP arbitration, final arbitration, priority, credit, tag reserve, VCC/VCD reserve, request-control, misc, latency sampling, perf counter, EDC counter, DSM, clock-gating, EDC mode, error-status, misc2, address-decoder select, and always-on misc fields.
- The `mmhub_ea_mmeadec3` address block start for MMEA3, covering DRAM/GMI client-to-group maps, group-to-VC maps, lazy accumulation, CAM controls, page burst, priority age/queuing/fixed/urgency/quantum controls, and GMI urgency masking.
- MMEA3 address normalization ranges, mega ranges, hole controls, non-power-of-two channel configuration, bank and misc decode configuration, harvest forcing, address-decoder 0 and 1 base/mask/config/select/column/rank-map fields, and the start of address-decoder 2 base-address fields.

The file is a generated hardware register bitfield map. It defines C preprocessor constants only: no functions, structs, variables, storage, or executable control flow are implemented in this chunk.

## Purpose

This header section provides the bit-level ABI used by AMDGPU code to compose and decode MMHUB 1.7 MMIO register values. Each field follows the generated AMD convention:

- `<REGISTER>__<FIELD>__SHIFT` gives the field's bit offset.
- `<REGISTER>__<FIELD>_MASK` gives the 32-bit mask for extracting or inserting that field.

The sibling `mmhub_1_7_offset.h` file supplies register addresses such as `regMMEA2_SDP_ARB_FINAL`, `regMMEA2_EDC_CNT`, `regMMEA3_ADDRNORM_BASE_ADDR0`, and `regMMEA3_ADDRDEC2_BASE_ADDR_CS0`; this file supplies the field locations for those registers. Driver code consumes these macros through helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `SOC15_REG_FIELD`, `SOC15_REG_ENTRY`, `RREG32_SOC15`, and `WREG32_SOC15`.

## Important Macro Families

### MMEA2 IO and SDP Arbitration

The chunk starts with the end of `MMEA2_IO_WR_PRI_URGENCY_MASKING`, mapping each client ID bit to an urgency-mask bit. It then defines read and write quantum threshold registers (`MMEA2_IO_RD_PRI_QUANT_PRI1..3` and `MMEA2_IO_WR_PRI_QUANT_PRI1..3`) with four 8-bit group thresholds per register.

The SDP arbitration group includes:

- `MMEA2_SDP_ARB_DRAM` and `MMEA2_SDP_ARB_GMI`, with read/write burst limits, early switch-to-read/write controls, end-of-burst-on-expire, decoupled read/write bank-state behavior, and GMI chain-breaking permission.
- `MMEA2_SDP_ARB_FINAL`, with DRAM/GMI/IO burst limits, burst multiplier, read-only virtual-channel bits for VC0-VC7, error event and halt request enables, GMI burst stretch, and DRAM/GMI read/write throttle bits.
- `MMEA2_SDP_DRAM_PRIORITY`, `MMEA2_SDP_GMI_PRIORITY`, and `MMEA2_SDP_IO_PRIORITY`, which pack four read priorities and four write priorities into 4-bit group fields.
- `MMEA2_SDP_CREDITS`, tag reserve registers, and VCC/VCD reserve registers, which define tag limits, response credits, per-VC credit reservations, and pool distribution.
- `MMEA2_SDP_REQ_CNTL`, which controls request pass-PW overrides, request-chain overrides for DRAM/GMI, inner-domain mode, and read/write/atomic block levels.

These definitions tune request scheduling and backpressure between MMHUB clients, DRAM, GMI, IO, virtual channels, and response paths.

### MMEA2 Misc, Performance, Clock, and Error Controls

The `MMEA2_MISC` and `MMEA2_MISC2` fields cover relative priority enablement across DRAM/GMI/IO read/write arbiters, early write return per virtual channel, link-manager dynamic and timing thresholds, CSGROUP swap controls, burst-limit data controls, IO read/write priority enablement, RRET swap mode, request blocking, and request-blocked status.

`MMEA2_LATENCY_SAMPLING`, `MMEA2_PERFCOUNTER_LO/HI`, `MMEA2_PERFCOUNTER0_CFG`, `MMEA2_PERFCOUNTER1_CFG`, and `MMEA2_PERFCOUNTER_RSLT_CNTL` expose a small performance-monitoring surface: sampling enable, sample ID, sample index, counter select/filtering, counter mode, bit range, and result control.

`MMEA2_CGTT_CLK_CTRL` defines clock-gating timing and override fields, including on delay, off hysteresis, soft stall overrides, light-sleep override, soft read/write/return/register overrides, and spare fields.

`MMEA2_EDC_MODE`, `MMEA2_ERR_STATUS`, `MMEA2_EDC_CNT`, `MMEA2_EDC_CNT2`, and `MMEA2_EDC_CNT3` describe error-detection and correction behavior and counters. They cover SEC/DED/SED counts for DRAM read/write command/page/data memories, IO command/data memories, GMI command/page/data memories, RRET/WRET tag memories, and MAM D0-D3 memories. `MMEA2_ERR_STATUS` also carries SDP read/write response status, read response data status, data parity, clear-error, busy-on-error, FUE, fatal interrupt, level interrupt, and completion fatal busy bits.

`MMEA2_DSM_CNTL*` and `MMEA2_DSM_CNTL2*` define diagnostic/error-injection controls for many of the same internal memories. The first set provides DSM irritator data and single-write enables; the second set provides error-injection enables, injection-delay selectors, and shared injection delay.

### MMEA2 Address Decoder Selection

`MMEA2_ADDRDEC_SELECT` defines start and end channel fields for DRAM and GMI address decoders. In this chunk it is a compact channel-routing register: 5-bit start/end fields for DRAM and 5-bit start/end fields for GMI.

`MMEA2_MISC_AON` adds always-on link-manager part-ack hysteresis and deassert mode controls.

### MMEA3 DRAM and GMI Request Grouping

The chunk then enters `addressBlock: mmhub_ea_mmeadec3`. The first MMEA3 families map clients, groups, virtual channels, and arbiter coefficients for DRAM and GMI request paths:

- `*_CLI2GRP_MAP0/1` maps 32 client IDs to four groups using 2-bit group fields.
- `*_GRP2VC_MAP` maps four groups to 3-bit virtual-channel fields.
- `*_LAZY` defines group delays plus request accumulation thresholds, timeout, and idle maximum.
- `*_CAM_CNTL` defines CAM depth per group, reorder limits per group, and refill-chain behavior.
- `*_PAGE_BURST` defines low/high page-burst limits for read and write traffic.
- `*_PRI_AGE`, `*_PRI_QUEUING`, `*_PRI_FIXED`, `*_PRI_URGENCY`, `*_PRI_URGENCY_MASKING`, and `*_PRI_QUANT_PRI1..3` define the priority model: aging rates and coefficients, queuing/fixed/urgency coefficients, urgency modes, per-client urgency masking, and four-group quantum thresholds.

The DRAM and GMI groups are structurally similar but independently named. The generated layout makes cross-channel copy-paste mistakes particularly risky because many masks are identical while register prefixes differ.

### MMEA3 Address Normalization and Decode

The address normalization families define how normalized MMHUB addresses map to fabric destinations and memory ranges:

- `MMEA3_ADDRNORM_BASE_ADDR0..3` and `LIMIT_ADDR0..3` define valid range bits, legacy MMIO hole enable, interleave channel/die/socket fields, interleave address selection, base address, destination fabric ID, and limit address.
- `MMEA3_ADDRNORM_OFFSET_ADDR1/3` define high-address offset enable and offset.
- `MMEA3_ADDRNORM_MEGABASE_ADDR0/1` and `MEGALIMIT_ADDR0/1` mirror the base/limit pattern for mega ranges.
- `MMEA3_ADDRNORMDRAM_HOLE_CNTL` and `MMEA3_ADDRNORMGMI_HOLE_CNTL` define hole-valid and hole-offset fields.
- `MMEA3_ADDRNORMDRAM_NP2_CHANNEL_CFG` and `MMEA3_ADDRNORMGMI_NP2_CHANNEL_CFG` define non-power-of-two 64K-space sizing fields.

The address-decoder families then describe DRAM/GMI bank, channel, chip-select, row, column, and rank-map decomposition:

- `MMEA3_ADDRDEC_BANK_CFG` selects bank masks, bank group selectors, and DRAM/GMI bank group interleave.
- `MMEA3_ADDRDEC_MISC_CFG` controls VCM enables and masks for PCH, channel, chip-select, and rank-map dimensions.
- `MMEA3_ADDRDECDRAM_HARVEST_ENABLE` and `MMEA3_ADDRDECGMI_HARVEST_ENABLE` can force bank bits B3-B5 enable/value pairs for harvested topology.
- `MMEA3_ADDRDEC0_*` and `MMEA3_ADDRDEC1_*` define base addresses for primary and secondary chip-selects, address masks, address configuration fields, bank/row selectors, extra bank/channel selection, low/high column selectors, rank-map selectors, channel-bit selection, and row-MSB inversion for even/odd rows.
- The chunk ends at the beginning of `MMEA3_ADDRDEC2_BASE_ADDR_SECCS0`, after completing `MMEA3_ADDRDEC2_BASE_ADDR_CS0..CS3` and defining only the `SECCS0` chip-select enable shift.

These fields are part of physical memory topology programming. They are not software allocation policy; they encode the hardware interpretation of address bits.

## Control Flow and State Behavior

There is no runtime control flow in this header. The macros affect compiled driver behavior by determining which bits AMDGPU code reads, writes, logs, or decodes in 32-bit MMIO registers.

The state described here is persistent hardware register state. Important state includes MMHUB arbitration thresholds, virtual-channel routing, tag and credit reservations, request blocking, link-manager behavior, performance counter configuration/results, clock-gating overrides, EDC mode and counters, sticky error status, diagnostic/error-injection controls, MMEA2 channel selection, MMEA3 client/group/VC mappings, priority coefficients, address normalization ranges, memory holes, non-power-of-two channel sizing, bank/channel/chip-select/rank/column address decode, and harvest-forced address bits.

Some fields are ordinary latched configuration fields, some are status fields, and some are command-like or clear bits. Examples include `MMEA2_ERR_STATUS__CLEAR_ERROR_STATUS`, request-blocked status in `MMEA2_MISC2`, diagnostic injection enable/select fields, performance result-control fields, and address decoder enable bits. Correct behavior depends on the owning AMDGPU code and hardware sequencing; the generated macros do not encode polling, timeout, reset, or write-one-to-clear semantics.

## Dependencies and Integration Points

This chunk depends on the generated MMHUB register-header set:

- `mmhub_1_7_offset.h` supplies the register offsets and base indices for the register names defined here.
- Other chunks of `mmhub_1_7_sh_mask.h` provide adjacent macro families, including the beginning of `MMEA2_IO_WR_PRI_URGENCY_MASKING` and the remaining `MMEA3_ADDRDEC2_BASE_ADDR_SECCS0` fields.
- AMDGPU SOC15 register helpers consume the `__SHIFT` and `_MASK` constants through `REG_SET_FIELD`, `REG_GET_FIELD`, `SOC15_REG_FIELD`, and register read/write wrappers.

The direct source-tree integration point is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/mmhub_v1_7.c`, which includes `mmhub/mmhub_1_7_sh_mask.h`. Within that file, the RAS tables use `SOC15_REG_FIELD(MMEA2_EDC_CNT*, ...)` and `SOC15_REG_FIELD(MMEA3_EDC_CNT*, ...)` to decode SEC/DED/SED counts, while RAS query/reset paths read and clear the corresponding EDC and error-status registers. This chunk supplies the MMEA2 EDC/status fields used there and the earlier MMEA3 arbitration/address-decode fields that share the same generated header namespace.

Many arbitration, performance, diagnostic, and address-decode fields in this chunk are hardware-facing definitions with no local function body in the header. They become integration points when platform initialization, RAS, bring-up diagnostics, firmware, or register-dump code reads or writes the matching `regMMEA*` offsets.

## Risks

- Bitfield drift is high impact. A wrong shift or mask can write unrelated MMHUB fields, causing memory routing errors, hangs, incorrect RAS accounting, bad performance data, lost fatal-error reporting, or request starvation.
- The repeated MMEA2 and MMEA3 families are mechanically fragile. DRAM/GMI, read/write, `CS01`/`CS23`, primary/secondary chip-select, and address-decoder instance names differ only by small tokens while many masks are identical.
- Arbitration and credit fields affect live memory traffic. Incorrect burst limits, priority coefficients, VC read-only bits, response credits, or tag reserves can alter QoS, throttle traffic, or deadlock under load.
- RAS decoding depends on exact EDC counter fields. If `SOC15_REG_FIELD` receives the wrong mask or shift, SEC/DED/SED counts can be silently misreported or cleared incorrectly.
- Error-status fields mix status, interrupt behavior, busy behavior, and clear controls. Treating clear bits or fatal-interrupt bits as passive status can hide or amplify hardware faults.
- Diagnostic DSM and error-injection fields should remain in controlled test paths. Enabling single-write or error-injection fields unintentionally can create artificial ECC/parity failures.
- Address normalization and decoder fields are topology-critical. Wrong base/limit, interleave, hole, bank, channel, chip-select, rank-map, column, row, or harvest settings can misroute physical memory accesses.
- The chunk starts and ends mid-family. A final merged document must reconcile the preceding `MMEA2_IO_WR_PRI_URGENCY_MASKING` definitions and the following `MMEA3_ADDRDEC2_BASE_ADDR_SECCS0` masks/remaining secondary chip-select fields.

## Test and Validation Signals

Useful validation is mostly integration and hardware bring-up coverage:

- Build AMDGPU with `mmhub_v1_7.c` and the MMHUB 1.7 headers enabled; this catches missing or renamed register-field macros consumed by `SOC15_REG_FIELD` and `REG_SET_FIELD`.
- MMHUB RAS tests should inject or observe SEC/DED/SED events and verify reported counts for `MMEA2_EDC_CNT`, `MMEA2_EDC_CNT2`, `MMEA2_EDC_CNT3`, and adjacent MMEA3 counters match raw register values.
- RAS reset tests should verify EDC counter clearing and `MMEA2_ERR_STATUS`/`MMEA3_ERR_STATUS` handling do not leave stale busy, fatal, or FUE state.
- Stress tests with DRAM, GMI, and IO traffic should watch for regressions in memory bandwidth, latency, hangs, and starvation after any change to SDP arbitration, priority, credit, VC, or urgency fields.
- Performance-counter validation should confirm `MMEA2_PERFCOUNTER*` select/filter/mode/result fields produce stable and expected counter reads.
- Power/clock validation should check `MMEA2_CGTT_CLK_CTRL` changes through suspend/resume, reset, and idle transitions.
- Address topology validation should cover VRAM discovery, GART/FB aperture programming, XGMI/GMI paths, non-power-of-two channel configurations, harvested parts, and memory tests that cross base/limit/hole boundaries.
- Register-dump or golden-header comparison tests should compare generated `mmhub_1_7_sh_mask.h` field values against the vendor register database for MMHUB 1.7.

## Unresolved Cross-Chunk References

This chunk starts after the first 27 shift definitions for `MMEA2_IO_WR_PRI_URGENCY_MASKING`; the complete family requires the previous chunk. It ends immediately after `MMEA3_ADDRDEC2_BASE_ADDR_SECCS0__CS_EN__SHIFT`, before the `BASE_ADDR` shift and masks for `SECCS0` and the rest of address-decoder 2. The merge/reconciliation lane should join those adjacent chunks before producing the final per-file document.

### subset-b-002767: lines 21210-23545

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mmhub/mmhub_1_7_sh_mask.h lines 21210-23545

## Purpose

This chunk is generated AMD MMHUB 1.7 register field metadata. It contains 2,336 source lines with 2,183 `#define` entries: 1,092 `__SHIFT` definitions and 1,235 `_MASK` definitions. The content is the bitfield half of the MMHUB register ABI; C code combines these field names with companion register offsets from `mmhub_1_7_offset.h` and SOC15 access helpers to pack, read, decode, and reset MMHUB hardware registers.

Although the source tree path is under a local `ceph-client` mirror, this file is AMDGPU memory-hub hardware metadata. It does not implement Ceph or distributed filesystem behavior.

The covered range starts inside the `MMEA3_ADDRDEC2_BASE_ADDR_SECCS0` definition and then covers late `MMEA3` external-address logic plus the beginning of `MMEA4`:

- `MMEA3_ADDRDEC2_*`: base-address, mask, address-configuration, address-select, column-select, and rank/memory-select fields for chip-select pairs `CS01`, `CS23`, secure chip-select pairs `SECCS01`, `SECCS23`, and individual `SECCS1..3`.
- `MMEA3_ADDRNORM*`: global address-normalization controls, mega-control bits, and masking controls for DRAM and GMI normalization.
- `MMEA3_IO_*`: IO read/write client-to-group maps, combine-flush controls, group burst controls, priority age/queue/fixed/urgency programming, urgency masking for client IDs 0-31, and priority quantum thresholds.
- `MMEA3_SDP_*`: system-data-port arbitration between DRAM, GMI, and IO, final arbitration controls, DRAM/GMI/IO priority fields, credits, tag/VCC/VCD reserve pools, and request-control behavior.
- `MMEA3_MISC`, `MMEA3_MISC2`, `MMEA3_MISC_AON`: broad control/status fields for memory access, clock gating, idle/response monitoring, error behavior, MAM/MCIC/SENDRSP enablement, interrupt handling, snoop, and TLB-related behavior.
- `MMEA3_LATENCY_SAMPLING`, `MMEA3_PERFCOUNTER*`: latency sampling and two performance counters with low/high result registers, event selection, source selection, instance selection, clear/start controls, edge/overflow behavior, and result control.
- `MMEA3_EDC_CNT*`, `MMEA3_DSM_CNTL*`, `MMEA3_CGTT_CLK_CTRL`, `MMEA3_EDC_MODE`, `MMEA3_ERR_STATUS`, `MMEA3_ADDRDEC_SELECT`: RAS/EDC counters, diagnostic scan controls, clock-gating controls, error-mode fields, EA error status/clear bits, and address-decoder selection.
- `MMEA4_DRAM_*` and `MMEA4_GMI_*`: read/write client grouping, group-to-virtual-channel mapping, lazy controls, CAM controls, page-burst controls, priority aging/queuing/fixed/urgency, urgency masking, and quantum thresholds for DRAM and GMI request paths.
- `MMEA4_ADDRNORM_*`: first normal and mega address range base/limit/offset fields, including range-valid, legacy MMIO hole, interleave topology, destination fabric ID, base/limit, and high-address offset controls.

The chunk boundary is artificial. The first line omits the preceding `MMEA3_ADDRDEC2_BASE_ADDR_SECCS0__CS_EN__SHIFT` definition, and the last covered register is `MMEA4_ADDRNORM_MEGALIMIT_ADDR0`; following `MMEA4_ADDRNORM_MEGABASE_ADDR1` and later fields are outside this work item.

## Important APIs, Types, And Macros

There are no C functions, structs, enums, variables, callbacks, locks, allocations, or direct MMIO operations in this chunk. Its interface is the generated macro namespace:

- `<REGISTER>__<FIELD>__SHIFT` gives the bit position used by `REG_SET_FIELD`, `REG_GET_FIELD`, and SOC15 field table macros.
- `<REGISTER>__<FIELD>_MASK` gives the field mask for extracting or preserving bits during MMIO read-modify-write operations.
- `SOC15_REG_FIELD(<REGISTER>, <FIELD>)` consumers derive shift/mask pairs from these names for RAS tables and register helpers.

High-signal field groups include:

- Address decoding: `CS_EN`, `BASE_ADDR`, `ADDR_MASK`, `NUM_BANK_GROUPS`, `NUM_RM`, `NUM_ROW_LO`, `NUM_ROW_HI`, `NUM_COL`, `NUM_BANKS`, `HI_COL_EN`, bank selectors `BANK0..BANK5`, row selectors, column selectors `COL0..COL15`, rank-map selectors `RM0..RM2`, channel-bit selectors, and even/odd row-MSB inversion fields.
- Address normalization: `ADDR_RNG_VAL`, `LGCY_MMIO_HOLE_EN`, `INTLV_NUM_CHAN`, `INTLV_NUM_DIES`, `INTLV_NUM_SOCKETS`, `INTLV_ADDR_SEL`, `BASE_ADDR`, `LIMIT_ADDR`, `DST_FABRIC_ID`, `HI_ADDR_OFFSET_EN`, and `HI_ADDR_OFFSET`.
- Client grouping and virtual-channel routing: `CLIENT0_GROUP..CLIENT31_GROUP`, `GROUP0_VC..GROUP3_VC`, and read/write variants for IO, DRAM, and GMI paths.
- Request throttling and arbitration: `RD_LAZY_THRESHOLD`, `WR_LAZY_THRESHOLD`, `RD_LAZY_TIMER`, `WR_LAZY_TIMER`, CAM pop/disable/debug fields, page-burst fields, `READ_PRI_AGE`, `WRITE_PRI_AGE`, `AFA` age-control fields, queuing-enable fields, fixed-priority fields, urgent-priority fields, `CID0_MASK..CID31_MASK`, and priority quantum group thresholds.
- SDP and credits: DRAM/GMI burst limits, early switch behavior, end-of-burst behavior, chain-breaking, readonly virtual-channel flags, error/halt request controls, DRAM/GMI/IO priorities, SDP credit limits, tag reserve, VCC/VCD reserve, `ROrW`, shared-credit behavior, and exact-reserve mode.
- RAS and diagnostics: EDC counter fields for DRAM read/write command/data/page memories, IO read/write command/data memories, GMI read/write command/data/page memories, return tag memories, MAM data memories, diagnostic scan `ENABLE/RESET/TC_CYCLE/SRAM_*` fields, `CGTT_CLK_CTRL`, EDC mode, and `MMEA3_ERR_STATUS` status/clear bits.
- Performance and latency: latency sampling enable/done/reset/data-select fields, `MMEA3_PERFCOUNTER_LO/HI`, performance counter event fields, source selection, instance selection, counter clear, counter enable, edge detection, range mode, overflow mode, and result-control fields.

## Control Flow

This chunk has no runtime control flow. Its only direct effect is C preprocessing.

Typical consumer flow is:

1. MMHUB 1.7 code includes `mmhub/mmhub_1_7_offset.h` and `mmhub/mmhub_1_7_sh_mask.h`.
2. Driver code reads a register with `RREG32_SOC15`, `RREG32_SOC15_OFFSET`, or `RREG32(SOC15_REG_ENTRY_OFFSET(...))`.
3. It extracts fields through `REG_GET_FIELD` or through table-generated masks and shifts such as `SOC15_REG_FIELD(MMEA3_EDC_CNT, DRAMRD_CMDMEM_SEC_COUNT)`.
4. For writable controls, it updates fields with `REG_SET_FIELD` and writes the value back through `WREG32_SOC15` or `WREG32`.

Concrete local flows include:

- `amdgpu/mmhub_v1_7.c` includes this header and the companion offset header for MMHUB 1.7 initialization, GART setup, TLB/cache setup, VM context programming, invalidation-range setup, clock gating, and RAS handling.
- `mmhub_v1_7_query_ras_error_count()` iterates `mmhub_v1_7_edc_cnt_regs`, reads `MMEA0..5_EDC_CNT*`, and decodes SEC/DED subfields through `mmhub_v1_7_ras_fields`. The in-scope `MMEA3_EDC_CNT*` and `MMEA4_EDC_CNT*` fields are used in those tables.
- `mmhub_v1_7_reset_ras_error_count()` clears the EDC counter registers by writing zero to each listed counter register, including `MMEA3` and `MMEA4` counters represented by this chunk.
- `mmhub_v1_7_query_ras_error_status()` and `mmhub_v1_7_reset_ras_error_status()` read `MMEA0..5_ERR_STATUS`, check SDP read/write response and data-parity status fields, and set `CLEAR_ERROR_STATUS`. The in-scope `MMEA3_ERR_STATUS` field definitions provide the layout for the `MMEA3` instance; the code also relies on the repeated layout matching the `MMEA0_ERR_STATUS` field names it uses for decoding.

The header does not encode register access order, reset timing, write-one-to-clear semantics, firmware ownership, clock/power prerequisites, or whether a given field is safe to write while traffic is active. Those rules live in the MMHUB driver code, platform firmware contracts, and hardware specifications.

## State And Persistence Behavior

No software state is stored in this header. The macros describe persistent or live hardware state inside the MMHUB external-address, address-normalization, arbitration, RAS, and diagnostic blocks.

The hardware state represented here includes:

- Address-decoder state: chip-select enables, base addresses, masks, bank/row/column/rank selections, channel-bit selections, secure chip-select address maps, and decoder selection. These settings affect how MMHUB EA ranges translate addresses toward DRAM/GMI targets.
- Address-normalization state: range-valid bits, interleave geometry, destination fabric IDs, legacy MMIO hole behavior, base/limit ranges, and high-address offsets. These are topology-sensitive and normally persist until reset or explicit reprogramming.
- Request-routing and QoS state: per-client group assignments, virtual-channel mapping, lazy thresholds/timers, page-burst behavior, priority age/queue/fixed/urgency policy, client-ID urgency masks, and quantum thresholds. These values govern traffic ordering and fairness for IO, DRAM, and GMI request paths.
- SDP state: arbitration limits, switching policy, final arbitration, readonly channel flags, error/halt signaling, credits, tag/VCC/VCD reserves, and request-control behavior.
- Counter and status state: latency sampling, performance counters, EDC SEC/DED counters, error status latches, and diagnostic scan control/status fields.
- Clock and diagnostic state: `CGTT_CLK_CTRL`, DSM controls, EDC mode, idle-monitoring fields, MAM/MCIC/SENDRSP enable bits, snoop controls, and assorted `MISC` control/status bits.

Persistence is hardware-defined. Configuration registers can persist across normal driver operation until reset, suspend/resume, power-gating, or reinitialization. Counter/status registers can be live, sticky, clear-on-write, clear-on-read, or reset by explicit writes depending on the register. The generated mask header does not distinguish those behaviors.

## Dependencies

This chunk depends on the generated MMHUB 1.7 register family and AMDGPU SOC15 register access layer:

- `mmhub_1_7_offset.h` supplies the matching `reg*` offsets for the registers whose fields are defined here.
- `amdgpu/mmhub_v1_7.c` includes this header directly and uses many MMHUB 1.7 fields through `REG_SET_FIELD`, `REG_GET_FIELD`, and RAS table helpers.
- SOC15 helpers such as `SOC15_REG_ENTRY`, `SOC15_REG_ENTRY_OFFSET`, `RREG32_SOC15`, `WREG32_SOC15`, and `SOC15_REG_FIELD` translate generated register and field names into actual MMIO operations.
- RAS infrastructure in `amdgpu_ras.h` and MMHUB RAS code depends on EDC counter masks and shifts matching hardware so SEC/DED totals are attributed to the correct subblocks.
- Sibling generated headers such as `mmhub_1_8_0_sh_mask.h` and later MMHUB versions have similar names but are not guaranteed layout-compatible. The matching offset and mask headers must be used for the same hardware generation.

## Integration Points

Primary integration points are:

- MMHUB 1.7 initialization: `amdgpu/mmhub_v1_7.c` uses this header for VM aperture setup, TLB/L2 control, VMID context programming, invalidation-range initialization, and clock-gating state. Those flows are outside this exact `MMEA3/MMEA4` slice but share the same generated header contract.
- MMHUB RAS accounting: `mmhub_v1_7_ras_fields` maps `MMEA3_EDC_CNT`, `MMEA3_EDC_CNT2`, `MMEA3_EDC_CNT3`, `MMEA4_EDC_CNT`, `MMEA4_EDC_CNT2`, and `MMEA4_EDC_CNT3` fields to named MMHUB memory subblocks such as DRAM command/page memories, IO command/data memories, GMI command/data/page memories, MAM data memories, and return tag memories.
- MMHUB RAS reset: `mmhub_v1_7_edc_cnt_regs` includes the same `MMEA3` and `MMEA4` EDC registers so the driver can reset accumulated error counters by writing zero.
- MMHUB EA error reporting: `mmhub_v1_7_ea_err_status_regs` includes `regMMEA3_ERR_STATUS` and `regMMEA4_ERR_STATUS`. The chunk provides the `MMEA3_ERR_STATUS` field layout for SDP read/write response status, read-response data parity, and clear-error behavior; `MMEA4_ERR_STATUS` is in a neighboring section.
- Hardware bring-up and tuning: address decode, normalization, DRAM/GMI/IO arbitration, SDP, priority, and diagnostic fields are generated definitions available to platform initialization, firmware golden settings, debug tooling, or future driver code even when the current C file does not touch each field explicitly.

## Risks And Edge Cases

- Mask/shift correctness is the main risk. These macros compile as constants; a wrong bit position silently programs or decodes the wrong hardware field.
- The range starts and ends mid-family. Final reconciliation should merge neighboring chunks before making file-level claims about complete `MMEA3_ADDRDEC2_BASE_ADDR_SECCS0` or `MMEA4_ADDRNORM_MEGALIMIT_ADDR0` coverage.
- Similar-looking MMHUB generations are not interchangeable. `mmhub_1_7_sh_mask.h`, `mmhub_1_8_0_sh_mask.h`, and later MMHUB headers use overlapping `MMEA*` names but may differ in register presence, field width, field meaning, or repeated-instance count.
- RAS fields are easy to misattribute because `MMEA3` and `MMEA4` repeat many counter names. A swapped mask can report SEC/DED counts against the wrong MMHUB subblock or miss a nonzero counter.
- `MMEA*_ERR_STATUS` fields may be sticky or clear-sensitive. Incorrect clear masks can leave stale RAS status, hide a real error, or repeatedly report the same event.
- Address-decoder and address-normalization fields are topology-critical. Bad base, limit, mask, interleave, fabric ID, high-offset, channel, bank, row, column, rank, or secure chip-select fields can route traffic to the wrong memory region or fabric target.
- Arbitration, priority, urgency masking, and SDP credit fields influence forward progress and fairness. Incorrect values can starve clients, produce latency spikes, trigger timeouts, or reduce GMI/DRAM/IO throughput.
- Diagnostic scan, clock-control, EDC mode, and reset-like fields are not ordinary configuration bits. They can affect live traffic, counter collection, RAS behavior, or clocking if written outside the expected sequencing window.
- Some consumers rely on repeated register-family layout. `mmhub_v1_7_query_ras_error_status()` decodes every `MMEA*_ERR_STATUS` value with `MMEA0_ERR_STATUS` field names, so the repeated instances must remain layout-equivalent.

## Test Signals

Useful validation signals include:

- Build AMDGPU with MMHUB 1.7 support enabled so all `mmhub_v1_7.c` uses of `mmhub_1_7_offset.h` and `mmhub_1_7_sh_mask.h` resolve.
- Static generated-header checks that every field in this chunk has both shift and mask definitions where expected, and that names line up with matching registers in `mmhub_1_7_offset.h`.
- RAS query tests that inject or observe MMHUB EDC events for `MMEA3` and `MMEA4`, then verify SEC/DED counts are decoded under the expected subblock names.
- RAS reset tests that write zero through `mmhub_v1_7_reset_ras_error_count()` and confirm `MMEA3_EDC_CNT*` and `MMEA4_EDC_CNT*` counters clear without disturbing unrelated state.
- EA error-status tests that exercise SDP read/write response and data-parity error paths, then verify status reporting and `CLEAR_ERROR_STATUS` behavior.
- Boot, suspend/resume, and GPU reset tests on MMHUB 1.7 hardware, watching for VM faults, MMHUB RAS warnings, GART setup failures, invalidation timeouts, or memory traffic hangs.
- Performance and stress tests that drive IO, DRAM, and GMI traffic while checking for unexpected starvation, latency regressions, RAS counter increments, or SDP arbitration errors.
- Hardware debug validation for address-decoder and address-normalization programming on multi-channel/interleaved systems, especially secure chip-select, fabric ID, high-offset, and legacy MMIO-hole behavior.

## Summary

Lines 21210-23545 of `mmhub_1_7_sh_mask.h` define generated bit shifts and masks for the tail of `MMEA3` address decoding plus `MMEA3` address normalization, IO/SDP arbitration, diagnostics, RAS, performance, and error-status fields, followed by the start of `MMEA4` DRAM/GMI arbitration and address-normalization fields. The chunk is hardware contract data, not executable logic. Correctness depends on exact field values, matching `mmhub_1_7_offset.h`, careful RAS/status handling, and hardware validation across MMHUB traffic, address routing, arbitration, diagnostics, reset, and error-reporting paths.

### subset-b-002768: lines 23546-25902

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mmhub/mmhub_1_7_sh_mask.h lines 23546-25902

## Scope And Purpose

This chunk is a generated-style AMD MMHUB 1.7 register mask header segment. It contains C preprocessor constants only: each hardware register field is exported as a `<REGISTER>__<FIELD>__SHIFT` and/or `<REGISTER>__<FIELD>_MASK` macro. There are no functions, structs, storage objects, branches, loops, or direct MMIO accesses in this line range.

The line range covers the tail of `mmhub_ea_mmeadec4` and the beginning of `mmhub_ea_mmeadec5`. In practical driver terms, it is part of the bitfield contract for the MMEA4/MMEA5 MMHUB EA address-decode engines: address normalization, DRAM/GMI channel decode, IO/DRAM/GMI arbitration and priority, SDP routing, performance counters, EDC/RAS counters, DSM/error-injection controls, clock gating, error status, and early MMEA5 DRAM/GMI priority map fields.

The source path is important because this header is paired with the matching MMHUB 1.7 offset header and the `amdgpu/mmhub_v1_7.c` implementation. The masks in this chunk let runtime code use symbolic register-field helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, and `SOC15_REG_FIELD` without open-coded bit literals.

## Important APIs, Types, And Constants

There are no callable APIs or C types defined here. The usable interface is the macro namespace.

Major macro groups in this chunk:

- `MMEA4_ADDRNORM_*`: address-normalization base/limit, mega-range, DRAM/GMI hole, NP2 channel, global control, mega-control, and masking fields. These describe validity, legacy MMIO hole handling, interleave channel/die/socket selection, base/limit address pieces, destination fabric IDs, DRAM/GMI hole offsets, and address-mask controls.
- `MMEA4_ADDRDEC_*`: bank and miscellaneous address-decode controls plus DRAM/GMI harvest force bits. The repeated `ADDRDEC[0-2]_*` groups define chip-select enable/base registers, address masks, DRAM geometry (`NUM_BANK_GROUPS`, `NUM_RM`, row/column/bank counts), bank/row/column bit selectors, channel bit selectors, and row-machine inversion fields for primary and secondary chip-select pairs.
- `MMEA4_IO_*`: IO read/write client-to-priority-group maps for CIDs 0-31, combine-flush timers, group burst limits, aging/queuing/fixed/urgency coefficients, per-CID urgency masking, and quantum-priority thresholds.
- `MMEA4_SDP_*`: DRAM/GMI/final SDP arbitration controls, DRAM/GMI/IO priority maps, credit limits, tag and VCC/VCD reserve controls, and request-control fields.
- `MMEA4_MISC`, `MMEA4_MISC2`, and `MMEA4_MISC_AON`: miscellaneous routing, request blocking, swap, stall, bypass, clock, and always-on link-manager fields.
- `MMEA4_LATENCY_SAMPLING` and `MMEA4_PERFCOUNTER*`: latency sampler enables/reset/count/type fields and two performance-counter configuration/result-control register layouts.
- `MMEA4_EDC_CNT`, `MMEA4_EDC_CNT2`, and `MMEA4_EDC_CNT3`: compact 2-bit single-error, double-error, and syndrome/error counters for DRAM, GMI, IO, return-tag, page memory, and MAM submemories.
- `MMEA4_DSM_CNTL*`: diagnostic/syndrome-memory controls and error-injection fields. These expose irritator data, single-write enable, error-injection enable, per-memory injection delay selectors, and global delay fields.
- `MMEA4_CGTT_CLK_CTRL`, `MMEA4_EDC_MODE`, and `MMEA4_ERR_STATUS`: clock-gating delay/override fields, EDC bypass/propagation/counting mode, and fatal/read/write response status bits including `CLEAR_ERROR_STATUS`.
- `MMEA4_ADDRDEC_SELECT`: selects DRAM and GMI address-decode channel start/end ranges.
- `MMEA5_DRAM_*` and early `MMEA5_GMI_RD_CLI2GRP_MAP*`: the beginning of the next EA decode block. This includes DRAM read/write client-to-group maps, group-to-virtual-channel maps, lazy/CAM/page-burst controls, priority coefficients, urgency modes, and quantum thresholds, followed by the start of GMI read client-to-group mapping.

The macros all represent 32-bit register field layouts. Common packing patterns include 2-bit group/CID fields at shifts `0, 2, 4, ...`, 3-bit priority coefficients at shifts `0, 3, 6, 9`, 4-bit row/column selectors at nibble boundaries, and full high address masks such as `0xFFFFF000L` or `0xFFFFFFFEL`.

## Control Flow And State Behavior

This header chunk has no local control flow. Its behavior appears when other AMDGPU files include it and compile the masks into register reads, writes, or field decoders.

Runtime state is hardware-owned:

- Address-normalization and address-decode fields shape how MMEA4 maps physical/fabric address ranges into DRAM or GMI resources, including chip-select windows, base/mask matching, row/column/bank extraction, channel selection, interleave geometry, and harvested/forced bank bits.
- IO, DRAM, and GMI priority fields influence arbitration policy for request classes. Client-to-group maps assign CIDs to four groups, group-to-VC maps select virtual channels, and age/queue/fixed/urgency/quantum fields determine when traffic is promoted or throttled.
- SDP and reserve fields control downstream request arbitration, credit reservation, tag/VCC/VCD reserve behavior, and request throttling/blocking. These values affect live traffic scheduling rather than any software data structure.
- EDC counters and error status fields are observed by RAS code. Counters accumulate in MMHUB hardware until reset by the driver or hardware reset, while `ERR_STATUS` records fatal/read/write response status and is cleared by writing `CLEAR_ERROR_STATUS`.
- DSM and error-injection fields are diagnostic controls. They can deliberately perturb internal memories or select injection timing; their persistence and side effects are hardware-defined and reset/power-state dependent.
- Clock-gating and EDC mode fields configure hardware block behavior. They are not cached by this header; any restore policy must live in the MMHUB implementation, firmware, or broader ASIC reset/resume flows.

The chunk itself does not enforce sequencing. Any consumer that changes address decode, arbitration, EDC, DSM, or clock-gating fields must handle hardware quiescing, read-modify-write ordering, polling, and reset interactions outside this file.

## Dependencies And Integration Points

This header depends on matching register-address definitions in `mmhub_1_7_offset.h`. For example, the same MMEA4 block appears under `addressBlock: mmhub_ea_mmeadec4`, with offsets such as `regMMEA4_ADDRNORM_MEGABASE_ADDR1`, `regMMEA4_ADDRDEC0_BASE_ADDR_CS0`, `regMMEA4_IO_RD_CLI2GRP_MAP0`, `regMMEA4_EDC_CNT`, and `regMMEA4_ERR_STATUS`. The MMEA5 definitions continue in the following address block.

Important in-tree consumers:

- `drivers/gpu/drm/amd/amdgpu/mmhub_v1_7.c` includes `mmhub/mmhub_1_7_offset.h` and this mask header. It uses `SOC15_REG_FIELD(MMEA4_EDC_CNT, ...)`, `SOC15_REG_FIELD(MMEA4_EDC_CNT2, ...)`, `SOC15_REG_FIELD(MMEA4_EDC_CNT3, ...)`, and the matching MMEA5 fields to build RAS field tables for MMHUB ranges 4 and 5.
- The same file builds `mmhub_v1_7_edc_cnt_regs` from `regMMEA4_EDC_CNT`, `regMMEA4_EDC_CNT2`, `regMMEA4_EDC_CNT3`, `regMMEA5_EDC_CNT`, `regMMEA5_EDC_CNT2`, and `regMMEA5_EDC_CNT3`, then reads them in `mmhub_v1_7_query_ras_error_count()` and clears them in `mmhub_v1_7_reset_ras_error_count()`.
- `mmhub_v1_7_query_ras_error_status()` and `mmhub_v1_7_reset_ras_error_status()` iterate over `regMMEA0_ERR_STATUS` through `regMMEA5_ERR_STATUS`. The code decodes status using the shared MMEA error-status field layout and clears errors by setting `CLEAR_ERROR_STATUS`.
- Later MMHUB generations, including `mmhub_v9_4.c` and `mmhub_9_4_1_sh_mask.h`, mirror the same generated field pattern. That makes this chunk part of a cross-generation register contract, not a standalone hand-written interface.
- Lower-level register helpers from the SOC15 AMDGPU infrastructure consume these macros through token-pasting. If a field name, mask suffix, or shift suffix is renamed, `SOC15_REG_FIELD` and `REG_{GET,SET}_FIELD` users fail to build or silently decode the wrong bits if the name still resolves to a bad value.

## Risks And Edge Cases

- Hardware contract drift is the dominant risk. A wrong mask or shift can misprogram MMEA4/MMEA5 address windows, route traffic to the wrong fabric target, corrupt DRAM/GMI chip-select decoding, or make RAS counters report the wrong subblock.
- This range starts in the middle of the `MMEA4_ADDRNORM_MEGALIMIT_ADDR0` definition pair: only the two mask lines are inside the chunk, while its shift definitions are in the previous chunk. The merge lane should join adjacent chunks before making whole-register coverage claims.
- This range ends in the middle of `MMEA5_GMI_RD_CLI2GRP_MAP1`; only the early CID16-CID19 shift lines are included at the tail. The remainder of that register belongs to the next chunk.
- The `MMEA4_ADDRDEC[0-2]_*` groups are highly repetitive. Mechanical edits or generated-regeneration mismatches can easily swap `CS01` and `CS23`, primary and secondary chip-selects, low and high column selectors, or address-decode instance numbers.
- Many fields have high-bit masks such as `0x80000000L`, `0xC0000000L`, or full-width masks. Consumers should keep operations unsigned and 32-bit, and avoid signed intermediate shifts.
- Several fields are operationally dangerous if written at the wrong time: `BLOCK_REQUESTS`, `CLEAR_ERROR_STATUS`, EDC bypass/propagation, DSM single-write/error-inject enables, address-decode enable/base/mask fields, clock-gating overrides, and priority/credit settings can alter live request handling.
- RAS error status handling in `mmhub_v1_7.c` uses the MMEA0 error-status field names to decode all MMEA instances because the layout is replicated. If one later instance diverged from that common layout, the current shared decode approach would become incorrect.
- Diagnostic EDC/DSM controls can intentionally generate or mask errors. Tests that exercise them need strict cleanup so injected errors do not look like persistent hardware faults.

## Test And Validation Signals

There are no unit tests for this generated macro chunk. Useful validation signals are build-time and hardware integration checks:

- Compile AMDGPU with `mmhub_v1_7.c` enabled. This verifies that `SOC15_REG_FIELD` can resolve all MMEA4/MMEA5 EDC counter fields used by the RAS tables.
- Static mask/shift checks: each `_MASK` should match its `_SHIFT` and field width; repeated CID map registers should pack 16 2-bit fields into 32 bits; priority coefficient registers should pack four 3-bit fields; column/bank selector registers should use nibble-aligned 4-bit or 5-bit masks as specified.
- Register-address alignment checks against `mmhub_1_7_offset.h`: every macro base in this chunk should have a matching `reg<base>` definition in the offset header, except where the chunk intentionally begins or ends mid-register.
- RAS runtime smoke tests on MMHUB 1.7 hardware: `mmhub_v1_7_query_ras_error_count()` should report nonzero SEC/DED values under controlled injection and zero/expected counts after `mmhub_v1_7_reset_ras_error_count()`.
- Error-status tests should verify that fatal/read/write response bits are detected and that writing `CLEAR_ERROR_STATUS` clears the relevant MMEA instance without clearing unrelated state.
- Suspend/resume, GPU reset, and SR-IOV paths should be checked for MMHUB stability because this header defines fields whose state may be reinitialized by firmware or the driver after reset.
- Performance and traffic tests should watch for regressions in memory/GMI/IO latency or starvation after any change to arbitration, grouping, burst, priority, or credit-reserve masks.

## Chunk Notes For Merge Lane

This is one chunk of a much larger generated register mask header. The whole-file research should merge it with adjacent chunks for `mmhub_1_7_sh_mask.h` before summarizing complete MMEA4/MMEA5 coverage. This specific range is best treated as: tail of MMEA4 address-normalization and address-decode masks, full MMEA4 IO/SDP/perf/RAS/DSM/error-status mask coverage, and the beginning of MMEA5 DRAM/GMI arbitration masks.

### subset-b-002769: lines 25903-28256

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mmhub/mmhub_1_7_sh_mask.h lines 25903-28256

## Scope And Purpose

This chunk is a generated-style AMDGPU MMHUB 1.7 register mask header section. It contains preprocessor constants only: each hardware register field is exposed as a `MMEA5_*__FIELD__SHIFT` and/or `MMEA5_*__FIELD_MASK` macro. There are no functions, structs, variables, local storage, or executable control-flow paths in this range.

The covered register namespace is the `MMEA5` MMHUB memory-management engine/arbitration range. The chunk defines bit layouts for:

- GMI read/write client-to-group mapping, group-to-virtual-channel mapping, lazy request accumulation, CAM depth/reorder control, page burst limits, and priority aging/queuing/fixed/urgency/quantum controls.
- Address normalization and address decode fields, including base/limit/offset windows, megabase/megalimit windows, DRAM/GMI hole controls, non-power-of-two channel sizes, bank/channel/chip-select/rank mapping, channel harvest enablement, and repeated `ADDRDEC0`, `ADDRDEC1`, and `ADDRDEC2` selectors.
- IO read/write client grouping, combine-flush timers, group burst limits, and priority controls parallel to the GMI priority model.
- SDP arbitration, priority, credit, tag reserve, virtual-channel credit reserve, and request-control fields.
- Miscellaneous MMEA5 arbitration/link-manager options, latency sampler selection, performance counter configuration/result controls, EDC/RAS counters, and DSM/error-injection controls.

The practical purpose is to let AMDGPU code use symbolic bit names with register access helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `SOC15_REG_FIELD`, `RREG32`, and `WREG32`, instead of embedding raw masks and shifts beside MMIO operations.

## Important APIs, Types, And Constants

This chunk exports no C API or type. Its interface is the macro namespace. The important families are:

- `MMEA5_GMI_RD_CLI2GRP_MAP1`, `MMEA5_GMI_WR_CLI2GRP_MAP0`, and `MMEA5_GMI_WR_CLI2GRP_MAP1`: 2-bit client ID group assignments. `MAP0` covers CIDs 0-15 and `MAP1` covers CIDs 16-31; this chunk starts midway through the read `MAP1` definition and then covers the write maps completely.
- `MMEA5_GMI_RD_GRP2VC_MAP` and `MMEA5_GMI_WR_GRP2VC_MAP`: 3-bit virtual-channel selections for groups 0-3.
- `MMEA5_GMI_RD_LAZY` and `MMEA5_GMI_WR_LAZY`: per-group delay fields plus request accumulation threshold, timeout, and idle maximum fields.
- `MMEA5_GMI_RD_CAM_CNTL` and `MMEA5_GMI_WR_CAM_CNTL`: per-group CAM depth, reorder limits, refill chaining, and page-based chaining controls.
- `MMEA5_GMI_PAGE_BURST`: 8-bit low/high read and write burst limits.
- `MMEA5_GMI_{RD,WR}_PRI_AGE`, `_PRI_QUEUING`, `_PRI_FIXED`, `_PRI_URGENCY`, `_PRI_URGENCY_MASKING`, and `_PRI_QUANT_PRI{1,2,3}`: four-group arbitration tuning. These describe aging rate/coefficient, queueing/fixed/urgency coefficients, urgency mode, per-client urgency masking for CIDs 0-31, and priority quantum thresholds.
- `MMEA5_ADDRNORM_BASE_ADDR{0,1,2,3}` and `MMEA5_ADDRNORM_MEGABASE_ADDR{0,1}`: address range valid bits, legacy MMIO hole enable, interleave channel/die/socket fields, interleave address selector, and base address fields. The matching limit registers carry destination fabric ID and limit address fields. `OFFSET_ADDR1` and `OFFSET_ADDR3` define high-address offset enable/value fields.
- `MMEA5_ADDRNORMDRAM_HOLE_CNTL`, `MMEA5_ADDRNORMGMI_HOLE_CNTL`, `MMEA5_ADDRNORMDRAM_NP2_CHANNEL_CFG`, `MMEA5_ADDRNORMGMI_NP2_CHANNEL_CFG`, `MMEA5_ADDRNORM_MEGACONTROL_ADDR{0,1}`, and `MMEA5_ADDRNORM{DRAM,GMI}_MASKING`: DRAM/GMI hole offsets, non-power-of-two 64K address space sizes, die-space sizing, and high-address masking.
- `MMEA5_ADDRDEC_BANK_CFG`, `MMEA5_ADDRDEC_MISC_CFG`, `MMEA5_ADDRDEC{DRAM,GMI}_HARVEST_ENABLE`, and `MMEA5_ADDRDEC{0,1,2}_*`: address-decoder field layouts for bank masks, bank group selection/interleave, VCM enables, PCH/channel/chip-select/rank masks, harvest masks for channels 0-5, chip-select base addresses, mask registers, address config registers, bank/row/channel selectors, column selectors, and rank-mapping selectors for primary and secondary chip selects.
- `MMEA5_IO_RD_CLI2GRP_MAP{0,1}`, `MMEA5_IO_WR_CLI2GRP_MAP{0,1}`, `MMEA5_IO_{RD,WR}_COMBINE_FLUSH`, `MMEA5_IO_GROUP_BURST`, and the `MMEA5_IO_{RD,WR}_PRI_*` families: IO-side equivalents for client grouping, flush timers, burst limits, and arbitration priority coefficients/masks/thresholds.
- `MMEA5_SDP_ARB_DRAM`, `MMEA5_SDP_ARB_GMI`, and `MMEA5_SDP_ARB_FINAL`: SDP arbitration controls for group selection, credit/retry behavior, round-robin or priority arbitration, and final request selection.
- `MMEA5_SDP_{DRAM,GMI,IO}_PRIORITY`, `MMEA5_SDP_CREDITS`, `MMEA5_SDP_TAG_RESERVE{0,1}`, `MMEA5_SDP_VCC_RESERVE{0,1}`, `MMEA5_SDP_VCD_RESERVE{0,1}`, and `MMEA5_SDP_REQ_CNTL`: per-group priorities, tag/read/write response credit limits, virtual-channel reserve pools, distributed-pool control, pass-PW overrides, chain overrides, inner-domain mode, and request block levels for read/write/atomic traffic.
- `MMEA5_MISC`: relative-priority enable bits for DRAM/GMI/IO read/write arbiters, per-VC early write return enables, early SDP original-data control, link-manager dynamic mode and timing thresholds, chip-select favoring, and write-to-read chip-select switching.
- `MMEA5_LATENCY_SAMPLING`: two sampler selectors across DRAM/GMI/IO, read/write/atomic request types, and virtual-channel masks.
- `MMEA5_PERFCOUNTER_LO`, `MMEA5_PERFCOUNTER_HI`, `MMEA5_PERFCOUNTER{0,1}_CFG`, and `MMEA5_PERFCOUNTER_RSLT_CNTL`: counter low/high fields, compare value, perf event range, mode, enable/clear bits, start/stop trigger masks, global enable/clear, and stop-on-saturate.
- `MMEA5_EDC_CNT` and `MMEA5_EDC_CNT2`: 2-bit SEC/DED/SED counter fields for DRAM read/write command memories, data memories, return tag memories, IO command/data memories, GMI command/page memories, and MAM D0-D3 memories.
- `MMEA5_DSM_CNTL`, `MMEA5_DSM_CNTLA`, and the beginning of `MMEA5_DSM_CNTL2`: DSM irritator data, single-write enable controls, and early error-injection controls for DRAM/GMI/IO command/page/data memory blocks.

## Control Flow And State Behavior

There is no local runtime control flow in this header. The macros become compile-time constants used by C files that already know the matching register offsets from `mmhub_1_7_offset.h`.

Runtime state is entirely hardware state:

- GMI and IO grouping/priority fields influence how client requests are grouped, delayed, reordered, masked for urgency, and mapped to virtual channels.
- Address normalization and decoder fields describe how incoming addresses are matched to ranges, transformed by high-address offsets, routed to destination fabric IDs, interleaved across channels/dies/sockets, and split into bank/row/column/rank/chip-select fields.
- SDP fields drive downstream arbitration, tag and response credit accounting, and request forwarding policy.
- `MISC`, latency sampling, and perf counter fields expose runtime tuning and observation controls for arbitration/link-manager behavior.
- EDC counter fields are hardware-maintained counts. `mmhub_v1_7.c` reads them through `mmhub_v1_7_query_ras_error_count()` and clears them in `mmhub_v1_7_reset_ras_error_count()` by writing zero to the relevant EDC count registers.
- DSM and error-injection fields describe diagnostic/test behavior; they do not provide any safety gate in the header itself.

Persistence is therefore register-defined. Values can persist until GPU reset, clock/power gating, firmware reprogramming, driver initialization, or an explicit counter reset. This file does not cache values in memory and has no save/restore sequencing.

## Dependencies And Integration Points

The masks are useful only with the matching address definitions in `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mmhub/mmhub_1_7_offset.h`, where this chunk's registers appear as `regMMEA5_GMI_*`, `regMMEA5_ADDRNORM*`, `regMMEA5_ADDRDEC*`, `regMMEA5_IO_*`, `regMMEA5_SDP_*`, `regMMEA5_MISC`, `regMMEA5_LATENCY_SAMPLING`, `regMMEA5_PERFCOUNTER*`, `regMMEA5_EDC_CNT*`, and `regMMEA5_DSM*` offsets.

The concrete consumer visible in this repository is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/mmhub_v1_7.c`. It includes `mmhub_1_7_sh_mask.h` and uses `SOC15_REG_FIELD(MMEA5_EDC_CNT, ...)` and `SOC15_REG_FIELD(MMEA5_EDC_CNT2, ...)` entries in `mmhub_v1_7_ras_fields[]` for MMHUB RAS reporting. The RAS path:

- associates subblock names such as `MMEA5_DRAMRD_CMDMEM`, `MMEA5_DRAMWR_CMDMEM`, `MMEA5_GMIRD_CMDMEM`, `MMEA5_GMIWR_DATAMEM`, and `MMEA5_MAM_D*MEM` with `regMMEA5_EDC_CNT` or `regMMEA5_EDC_CNT2`;
- decodes SEC/DED/SED bitfields through the generated masks and shifts;
- accumulates corrected errors into `ras_err_data.ce_count` and uncorrected errors into `ras_err_data.ue_count`;
- logs nonzero subblock counts and resets EDC counters by writing zero when MMHUB RAS is supported.

Other families in this chunk are register vocabulary for MMHUB initialization, firmware programming, diagnostics, register dumps, and low-level tuning paths. Even when no direct C reference appears for every macro in this source tree, the generated names must stay synchronized with the hardware register spec and offset header because table-driven register access code can construct `REG_SET_FIELD`/`REG_GET_FIELD` use from these names.

## Risks And Edge Cases

- Hardware contract drift is the dominant risk. A wrong shift or mask can silently program the wrong MMHUB arbitration, address decode, virtual-channel, or error-counter field.
- This chunk begins in the middle of `MMEA5_GMI_RD_CLI2GRP_MAP1`; the `CID16`-`CID19` shift definitions are in the previous chunk while their masks are visible here. Whole-file analysis must merge adjacent chunks before treating that register as complete.
- This chunk ends inside `MMEA5_DSM_CNTL2`. Only three shift definitions are present here; matching masks and later error-injection fields are in the next chunk. Do not infer complete DSM error-injection coverage from this chunk alone.
- The generated double suffix pattern is intentional for fields named `MASK`, for example `MMEA5_GMI_RD_PRI_URGENCY_MASKING__CID0_MASK_MASK`. Cleanup scripts must not collapse these names.
- Many packed fields use adjacent 2-bit, 3-bit, 4-bit, 5-bit, 6-bit, 7-bit, or 8-bit lanes. Off-by-one field widths are easy to miss and can corrupt neighboring settings.
- Address decode fields are especially sensitive. Incorrect `BASE_ADDR`, `LIMIT_ADDR`, `DST_FABRIC_ID`, `INTLV_*`, `CHAN_BIT`, bank/row/column selectors, or harvest masks can route memory requests to the wrong channel, chip select, rank, or fabric target.
- GMI/IO priority, lazy accumulation, CAM depth, reorder, and credit fields can affect fairness, latency, deadlock avoidance, and throughput. Bad defaults could show up as hangs or severe performance regressions rather than straightforward register errors.
- EDC counts are small 2-bit fields packed into 32-bit registers. Saturation, read-clear behavior, and reset semantics are hardware-defined; the driver RAS path assumes the masks identify the correct sub-counter and that writing zero resets the count registers.
- DSM and error-injection fields are diagnostic/destructive controls. Enabling them in normal runtime paths could inject memory errors or stress internal memories unexpectedly.
- High-bit masks such as `0x80000000L` and full-width fields such as `0xFFFFFFFFL` must be handled as unsigned 32-bit quantities. Signed shifts or implicit signed comparisons can misbehave in consumers.

## Test And Validation Signals

There are no direct unit tests for this macro-only chunk. Useful validation signals are:

- Compile coverage of `amdgpu/mmhub_v1_7.c` with this header and the matching `mmhub_1_7_offset.h`, especially the `SOC15_REG_FIELD(MMEA5_EDC_CNT, ...)` and `SOC15_REG_FIELD(MMEA5_EDC_CNT2, ...)` entries.
- Static consistency checks that every visible `_MASK` has the expected contiguous bit range for its matching `__SHIFT`, and that repeated register families use consistent layouts across read/write and GMI/IO variants.
- Cross-header validation that every `MMEA5_*` mask family in this chunk has a matching `regMMEA5_*` offset when the hardware register is addressable.
- RAS validation on MMHUB 1.7 hardware: inject or observe correctable/uncorrectable MMHUB errors, confirm `mmhub_v1_7_query_ras_error_count()` attributes nonzero counts to the expected `MMEA5_*` subblock, and confirm `mmhub_v1_7_reset_ras_error_count()` clears the relevant counters.
- Register-dump comparison against AMD's register specification for address normalization/decode and arbitration fields, with special attention to `ADDRDEC{0,1,2}` repeated layouts and `MMEA5_DSM_CNTL2` continuation across chunks.
- Runtime smoke tests for GPU memory traffic, GMI/IO request pressure, suspend/resume, reset, and RAS polling. Failures would likely present as hangs, page faults, unexpected RAS counts, or major latency/throughput changes.

## Chunk Notes For Merge Lane

This is one chunk of a much larger generated MMHUB 1.7 mask header. Merge it with neighboring chunks before preparing whole-file research. The beginning is a continuation of `MMEA5_GMI_RD_CLI2GRP_MAP1`, and the end is a continuation into `MMEA5_DSM_CNTL2`; the complete MMEA5 register story spans adjacent line ranges.

### subset-b-002770: lines 28257-30631

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mmhub/mmhub_1_7_sh_mask.h lines 28257-30631

## Scope

This chunk covers a large middle slice of the generated AMD MMHUB 1.7 shift/mask header. It begins in the `MMEA5_DSM_CNTL2` field group and continues through `VM_CONTEXT10_CNTL`. The range is entirely preprocessor data: `#define` constants for register-field shifts and masks, plus generated address-block comments. It contains no C functions, structs, enums, storage, locks, allocation, or executable control flow.

The register families in this slice cover:

- `MMEA5_*` error injection, EDC/RAS, clock-control, miscellaneous request blocking, address-decoder selection, and always-on link-manager fields.
- `MC_VM_MX_L1_*` L1 TLB status and L1 performance-counter fields.
- `PCTL0_*` MMHUB deep-sleep, power-gating ignore, per-slice busy/allow, and UTCL2/slice miscellaneous fields.
- `ATC_L2_*` ATC L2 request/cache controls, cache data/debug access, clock gating, light sleep, DSM error injection, and ATC performance-counter fields.
- `L2TLB_*` and `UTC_GPUVA_VMID_TRANSLATION_ASSIST_*` L2 TLB status, translation-assist request/response, and L2TLB performance counters.
- `VM_L2_*`, `VML2_*`, and `UTCL2_*` VM L2 cache, invalidation, protection fault, identity aperture, bank/class selection, parity, clock gating, ECC/EDC, and VM L2 performance-counter fields.
- `VM_CONTEXT0_CNTL` through `VM_CONTEXT10_CNTL`, where the chunk ends partway through the repeated VM context control register family.

## Purpose

`mmhub_1_7_sh_mask.h` is a generated hardware bitfield map for the AMDGPU MMHUB 1.7 block. This chunk gives symbolic shift and mask constants used by SOC15 register helpers to read, modify, and interpret MMHUB registers without hard-coded bit numbers.

The matching offset header identifies register addresses (`reg...` constants). This shift/mask header identifies the bit layout inside those registers (`REGISTER__FIELD__SHIFT` and `REGISTER__FIELD_MASK`). The constants are consumed by macros such as `REG_SET_FIELD`, `REG_GET_FIELD`, and `SOC15_REG_FIELD`, which depend on the generated naming convention.

For MMHUB 1.7 specifically, this slice supports three main driver surfaces:

- GPUVM and GART setup: VM L2 cache setup, L1/L2 invalidation behavior, VM context enablement, page-table depth/block size, retry-fault policy, and default-page fault routing.
- RAS and diagnostics: MMEA5 EDC counters, error-status fields, ECC/EDC controls, parity status, and fatal/interrupt behavior.
- Power/performance management: clock-gating and light-sleep fields, deep-sleep controls, per-slice power/deep-sleep gating, and performance-counter selector/result fields.

## Important APIs, Types, And Data

The exported "API" is the macro namespace. Important groups include:

- `MMEA5_DSM_CNTL2`, `MMEA5_DSM_CNTL2A`, and empty `MMEA5_DSM_CNTL2B` marker: error-injection enable, delay-selection, and injection-delay fields for command, data, tag, page, DRAM, GMI, and IO memory paths.
- `MMEA5_CGTT_CLK_CTRL`, `MMEA5_EDC_MODE`, `MMEA5_ERR_STATUS`, `MMEA5_MISC2`, `MMEA5_ADDRDEC_SELECT`, `MMEA5_EDC_CNT3`, and `MMEA5_MISC_AON`: clock/test gating, EDC mode, fatal/error status, request blocking, address decoder channel selection, DED count fields, and link-manager hysteresis controls.
- `MC_VM_MX_L1_TLB0_STATUS` through `MC_VM_MX_L1_TLB7_STATUS`: `BUSY` and `FOUND_PARITY_ERRORS` status fields for eight L1 TLB instances.
- `MC_VM_MX_L1_PERFCOUNTER0_CFG` through `MC_VM_MX_L1_PERFCOUNTER3_CFG`, `MC_VM_MX_L1_PERFCOUNTER_RSLT_CNTL`, `MC_VM_MX_L1_PERFCOUNTER_LO`, and `MC_VM_MX_L1_PERFCOUNTER_HI`: L1 perf event selection, mode, enable/clear, result selection, triggers, low/high counter values, and compare fields.
- `PCTL0_CTRL`, `PCTL0_MMHUB_DEEPSLEEP_*`, `PCTL0_PG_IGNORE_DEEPSLEEP*`, `PCTL0_SLICE{0..5}_CFG_DAGB_BUSY`, `PCTL0_SLICE{0..5}_CFG_DS_ALLOW*`, `PCTL0_UTCL2_MISC`, and `PCTL0_SLICE{0..5}_MISC`: power controller masks for deep-sleep entry, idle/busy sources, power-gating masks, slice-level DAGB status, and per-slice memory power state.
- `ATC_L2_CNTL`, `ATC_L2_CNTL2`, `ATC_L2_CNTL3`, `ATC_L2_CNTL4`, `ATC_L2_STATUS`, `ATC_L2_STATUS2`, `ATC_L2_MISC_CG`, `ATC_L2_MEM_POWER_LS`, `ATC_L2_CGTT_CLK_CTRL`, `ATC_L2_CACHE_*_DSM_*`, `ATC_L2_MM_GROUP_RT_CLASSES`, and ATC L2 perf-counter macros: ATC request depth, cache bank/update/VMID policy, translation reset/wait, busy/status, clock gating, light sleep, data SRAM error injection, real-time class mapping, and performance monitoring.
- `L2TLB_TLB0_STATUS`, `UTC_GPUVA_VMID_TRANSLATION_ASSIST_REQUEST_*`, and `UTC_GPUVA_VMID_TRANSLATION_ASSIST_RESPONSE_*`: L2 TLB parity/busy state and assisted GPUVA/VMID translation request/response fields including VMID, pasid/vmfid, permission flags, PTE address, ready/valid, and fault response metadata.
- `VM_L2_CNTL`, `VM_L2_CNTL2`, `VM_L2_CNTL3`, `VM_L2_CNTL4`, `VM_L2_STATUS`, `VM_DUMMY_PAGE_FAULT_*`, `VM_L2_PROTECTION_FAULT_*`, identity-aperture address registers, `VM_L2_BANK_SELECT_RESERVED_CID*`, `VM_L2_CACHE_PARITY_CNTL`, `VM_L2_CGTT_*`, `VML2_*_ECC_*`, `UTCL2_*_ECC_*`, `UTCL2_EDC_MODE`, and `UTCL2_EDC_CONFIG`: VM L2 cache enablement, fragment processing, invalidation, cache sizing/banking, protection-fault controls/status/default routing, identity mapping, reserved client ID banking, parity/ECC injection and status, and EDC mode.
- `MC_VM_L2_PERFCOUNTER0_CFG` through `MC_VM_L2_PERFCOUNTER7_CFG`, result-control, low, and high fields: VM L2 performance-counter selection and result access.
- `VM_CONTEXT0_CNTL` through `VM_CONTEXT10_CNTL`: repeated context-control fields for enabling contexts, configuring page-table depth/block size, retry behavior, and per-fault interrupt/default-page policy for range, dummy page, PDE0, valid, read, write, and execute protection faults.

There are no local types. The important external type relationships are indirect: `struct amdgpu_device`, `struct amdgpu_vmhub`, `struct ras_err_data`, `struct soc15_ras_field_entry`, and `struct soc15_reg_entry` in the AMDGPU driver consume these macros through register helper APIs.

## Control Flow

This header has no runtime control flow. Runtime behavior appears when AMDGPU MMHUB code includes the header and expands the macros in register read/modify/write sequences.

The primary local consumer is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/mmhub_v1_7.c`:

1. `mmhub_v1_7_gart_enable()` sequences GART setup, aperture setup, TLB setup, cache setup, snoop override, system-domain enablement, identity-aperture disable, VMID configuration, and invalidation programming.
2. `mmhub_v1_7_init_cache_regs()` reads and writes `regVM_L2_CNTL`, `regVM_L2_CNTL2`, `regVM_L2_CNTL3`, and `regVM_L2_CNTL4`, using fields from this chunk to enable VM L2 cache, enable fragment processing, invalidate L1/L2 state, select bank/fragment values, and adjust physical PDE/PTE request policy for XGMI-connected-to-CPU systems.
3. `mmhub_v1_7_enable_system_domain()` programs `VM_CONTEXT0_CNTL` fields for VMID0 using `ENABLE_CONTEXT`, `PAGE_TABLE_DEPTH`, `PAGE_TABLE_BLOCK_SIZE`, and retry-fault policy.
4. `mmhub_v1_7_setup_vmid_config()` loops over VMIDs 1 through 15 using offsets from the companion offset header and `VM_CONTEXT1_CNTL` field names. Because the context control registers are layout-compatible, `REG_SET_FIELD(..., VM_CONTEXT1_CNTL, ...)` is used for each offset in the repeated context range.
5. `mmhub_v1_7_set_fault_enable_default()` uses `VM_L2_PROTECTION_FAULT_CNTL` fields to toggle default-page handling for range, PDE, translate-further, NACK, dummy, valid, read, write, and execute faults; when default handling is disabled it sets crash-on-fault fields.
6. `mmhub_v1_7_init_system_aperture_regs()` writes `VM_L2_PROTECTION_FAULT_DEFAULT_ADDR_LO32/HI32` and updates `VM_L2_PROTECTION_FAULT_CNTL2__ACTIVE_PAGE_MIGRATION_PTE_READ_RETRY`.
7. Clock-gating helpers read/write `ATC_L2_MISC_CG__ENABLE_MASK` and `ATC_L2_MISC_CG__MEM_LS_ENABLE_MASK` to report and control MMHUB medium-grain clock gating and memory light sleep.
8. RAS helpers read MMEA EDC count registers, extract SEC/DED counts with `SOC15_REG_FIELD` metadata, check `MMEA*_ERR_STATUS` status fields via `REG_GET_FIELD`, and set `CLEAR_ERROR_STATUS` to reset hardware error status.

The perf-counter, PCTL0, translation-assist, ECC/EDC injection, and many debug/cache-data fields in this chunk are generated register definitions that may be used by diagnostics, firmware-facing flows, debug tooling, or future driver paths even when not directly touched by the current `mmhub_v1_7.c` setup path.

## State And Persistence Behavior

The macros are compile-time constants and do not own state. The registers they describe are persistent hardware state inside MMHUB until changed by driver writes, firmware, reset, suspend/resume restore, or GPU reset.

- VM L2 cache and invalidation fields persist after GART enable. Incorrect `VM_L2_CNTL*` values can affect address translation, cache residency, L1/L2 invalidation propagation, and page-table walk behavior for all MMHUB clients.
- VM context control fields persist per VMID. They define whether a context is active, how many page-table levels are walked, what page-table block size is used, whether retry faults are generated, and whether specific faults interrupt or resolve to the default page.
- Protection-fault status and address registers capture hardware fault state. Status fields such as VMID, client ID, fault type, RWX bits, and more-faults indicators are read by fault/RAS paths; default-address and fault-policy registers control where failed transactions are redirected.
- MMEA5 EDC/RAS counters and status registers accumulate hardware error evidence. Driver RAS paths read count registers to update corrected/uncorrected totals and write zero or `CLEAR_ERROR_STATUS` to reset the hardware view.
- ECC/EDC index/control/status registers for VML2, VML2 walker, and UTCL2 are stateful debug/RAS controls. Error-injection enable and status bits are especially sensitive because they can intentionally create correctable or uncorrectable events.
- Clock gating, deep sleep, memory light sleep, and PCTL slice controls persist as power-management policy. These fields affect whether MMHUB/ATC/UTCL2/slice logic can idle, gate clocks, or enter memory low-power states.
- Performance-counter configuration and result-selection fields persist while counters run. A profiling path must clear/configure/select counters carefully or it can observe stale results from prior measurements.

There is no disk persistence, allocation lifetime, refcounting, or software synchronization in the header. Serialization and ordering are the responsibility of the MMIO callers, usually under AMDGPU device initialization, reset, clockgating, VM, or RAS sequencing.

## Dependencies

This chunk depends on the generated MMHUB 1.7 register specification and must stay synchronized with:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mmhub/mmhub_1_7_offset.h`, which supplies the matching `reg...` register addresses and `_BASE_IDX` constants.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/mmhub_v1_7.c`, the primary MMHUB 1.7 consumer for GART setup, VM L2 setup, VM context setup, clock gating, and RAS handling.
- SOC15 register helper macros including `RREG32_SOC15`, `WREG32_SOC15`, `RREG32_SOC15_OFFSET`, `WREG32_SOC15_OFFSET`, `SOC15_REG_OFFSET`, `SOC15_REG_ENTRY`, `SOC15_REG_ENTRY_OFFSET`, `SOC15_REG_FIELD`, `REG_SET_FIELD`, and `REG_GET_FIELD`.
- AMDGPU state in `struct amdgpu_device`, especially `adev->gmc`, `adev->vm_manager`, `adev->vmhub[AMDGPU_MMHUB0(0)]`, `adev->cg_flags`, `adev->dummy_page_addr`, and RAS support state.
- RAS support code in `amdgpu_ras.h` and SOC15 RAS field descriptors, which rely on the shift/mask values for correct SEC/DED extraction and status clearing.

The generated macro naming convention is itself a dependency. `REG_SET_FIELD(tmp, VM_L2_CNTL, ENABLE_L2_CACHE, 1)` expands by concatenating `VM_L2_CNTL__ENABLE_L2_CACHE_MASK` and `VM_L2_CNTL__ENABLE_L2_CACHE__SHIFT`; a spelling or prefix mismatch compiles only if a wrong same-named macro exists elsewhere, or fails at build time.

## Integration Points

- MMHUB GART enable/disable: `mmhub_v1_7_gart_enable()` and `mmhub_v1_7_gart_disable()` use these fields to enable or disable VM contexts, L1 TLB, advanced driver model, VM L2 cache, invalidation, and context fault routing.
- VM fault handling: `mmhub_v1_7_set_fault_enable_default()` and the hub initialization fields `vm_l2_pro_fault_status` and `vm_l2_pro_fault_cntl` integrate this header with AMDGPU fault reporting, retry policy, default-page handling, and crash-on-fault behavior.
- VMID setup: `VM_CONTEXT0_CNTL` and `VM_CONTEXT1_CNTL` field layouts configure VMID0 and VMIDs 1-15. This chunk covers context 0-10 field definitions directly, while the file continues the repeated family after the chunk for later VMIDs.
- Clock and power gating: `ATC_L2_MISC_CG` masks integrate with `AMD_CG_SUPPORT_MC_MGCG` and `AMD_CG_SUPPORT_MC_LS`. PCTL0 fields describe the lower-level deep-sleep and slice gating controls that hardware or debug/power paths use around those policies.
- RAS count/status integration: `mmhub_v1_7_ras_fields`, `mmhub_v1_7_edc_cnt_regs`, and `mmhub_v1_7_ea_err_status_regs` use MMEA5 fields in this chunk for SEC/DED accounting and external-agent error status checks.
- Performance monitoring: L1, ATC L2, L2TLB, and VM L2 performance-counter macros provide selector/result layouts for MMHUB profiling and hardware debug. Their integration is through generic register access rather than a high-level C abstraction in this file.
- Translation assist and ATS/ATC behavior: `UTC_GPUVA_VMID_TRANSLATION_ASSIST_*` and `ATC_L2_*` fields describe interfaces between MMHUB address translation, ATC cache behavior, and VMID/GPUVA translation assistance.
- ECC/EDC and error injection: `VML2_MEM_ECC_*`, `VML2_WALKER_MEM_ECC_*`, `UTCL2_MEM_ECC_*`, `UTCL2_EDC_*`, and DSM controls integrate with RAS validation, hardware self-test, and debug flows that intentionally inject or observe memory-protection errors.

## Risks

- Bitfield drift is the central risk. These masks can compile cleanly while targeting the wrong bits if the generated header is out of sync with the MMHUB 1.7 register database.
- The chunk starts and ends mid-family. It begins after earlier `MMEA5_DSM_CNTL2` fields and ends partway through `VM_CONTEXT10_CNTL`; reconciliation must merge adjacent chunks to describe the full source file without treating this slice as complete for those families.
- Repeated VM context registers are easy to misuse. Context 1 field names are used with offset arithmetic for VMIDs 1-15; the repeated field layouts must remain identical, and `hub->ctx_distance` must match the offset header.
- VM L2 and invalidation fields are high-blast-radius. Incorrect cache enablement, bank selection, fragment size, or invalidate bits can create stale GPUVM translations, page-table walk failures, data corruption symptoms, or GPU hangs.
- Fault policy changes can mask or amplify bugs. Enabling default-page handling can hide invalid accesses; disabling it and enabling crash-on-fault can turn recoverable faults into device resets or process failures.
- RAS extraction depends on exact masks and shifts. Wrong MMEA5 EDC count fields can misreport corrected versus uncorrected errors, clear the wrong status, or miss fatal external-agent response errors.
- Error-injection and ECC/EDC controls are dangerous if exposed outside controlled diagnostics. Accidentally enabling injection can create artificial RAS events, poison status counters, or trigger recovery paths.
- Clock-gating and deep-sleep fields can cause intermittent failures if misprogrammed. Timing-sensitive hangs may appear only under idle, suspend/resume, or low-power transitions.
- Cross-generation copying is risky. Similar register names exist in GMC, DCN, later MMHUB, and earlier MMHUB headers, but bit positions and supported fields differ by ASIC generation.

## Test Signals

- Build AMDGPU with MMHUB 1.7 support and warnings enabled. This catches missing or misspelled generated macros used by `REG_SET_FIELD`, `REG_GET_FIELD`, and `SOC15_REG_FIELD`.
- Generated-header validation should compare every shift and mask in this line range against the authoritative MMHUB 1.7 register source and verify that corresponding offsets exist in `mmhub_1_7_offset.h`.
- MMHUB 1.7 boot smoke should exercise GART enable, VMID setup, VM L2 cache setup, TLB setup, invalidation programming, and GART disable without VM fault storms, register-access warnings, or GPU reset.
- GPUVM stress should create multiple processes/VMIDs, update and invalidate page tables repeatedly, exercise XNACK/retry-fault behavior, evict and remap buffers, and verify no stale translations after invalidation.
- Fault-policy tests should toggle default-page handling and validate expected behavior for invalid, read, write, execute, dummy-page, PDE, range, and retry/no-retry faults.
- RAS tests should read MMEA5 EDC counters, inject or simulate SEC/DED events where supported, verify corrected/uncorrected counts, verify status warnings for `SDP_RDRSP_STATUS`, `SDP_WRRSP_STATUS`, and data parity, and verify counter/status reset paths.
- Power-management tests should toggle medium-grain clock gating and memory light sleep, then run memory/VM workloads across idle, suspend/resume, and GPU reset to catch ATC/PCTL low-power regressions.
- Perf-counter diagnostics should configure L1, ATC L2, L2TLB, and VM L2 counters, clear/select results, and confirm monotonic or expected event counts under controlled address-translation workloads.
- ECC/EDC and DSM debug validation should confirm injection controls are disabled during normal boot and only enabled in controlled RAS/debug tests, with status bits clearing as documented.

### subset-b-002771: lines 30632-32178

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mmhub/mmhub_1_7_sh_mask.h lines 30632-32178

## Scope

This chunk covers the final MMHUB 1.7 register shift/mask definitions in `mmhub_1_7_sh_mask.h`. It is generated hardware metadata: every item is a C preprocessor macro defining either a bit shift or a bit mask for a 32-bit MMHUB register field. There are no C functions, structs, enums, variables, allocations, locks, loops, or direct MMIO operations in this range.

The range starts in the middle of `VM_CONTEXT10_CNTL`, then covers:

- Full `VM_CONTEXT11_CNTL` through `VM_CONTEXT15_CNTL` field encodings.
- `VM_CONTEXTS_DISABLE` bits for disabling contexts 0 through 15.
- VM invalidate engine semaphore, request, acknowledge, and address-range registers for engines 0 through 17.
- VM context page-table base, start, and end address registers for contexts 0 through 15.
- The `mmhub_utcl2_vmsharedhvdec` block: per-VF framebuffer size/offset, MARC windows, PCIe ATS controls, active function ID, and XGMI GPU IOV enable masks.
- The `mmhub_utcl2_vmsharedpfdec` block: PF/shared framebuffer offset, system aperture default address, steering, virtual reset request, memory light-sleep timing, cacheable/local DRAM/HBM apertures, APT control, UTCL2 clock-gating timing, XGMI local framebuffer controls, cacheable DRAM enable, and host mapping mode.
- The `mmhub_utcl2_vmsharedvcdec` block: framebuffer and AGP locations, system aperture bounds, and `MC_VM_MX_L1_TLB_CNTL`.

Although the repository path is under `sources/distributed-fs/ceph-client`, this file is AMDGPU DRM hardware register metadata and has no Ceph filesystem behavior.

## Purpose

The purpose of this header slice is to provide the bit-level ABI between MMHUB 1.7 driver code and AMD GPU memory-management hardware. The companion `mmhub_1_7_offset.h` file supplies symbolic register offsets such as `regVM_INVALIDATE_ENG0_REQ`, `regVM_CONTEXT0_PAGE_TABLE_BASE_ADDR_LO32`, `regMC_VM_MX_L1_TLB_CNTL`, and `regMC_VM_FB_LOCATION_BASE`; this file supplies the field positions and masks used to compose and decode those register values.

The exposed macro pattern is regular:

- `<REGISTER>__<FIELD>__SHIFT` gives the field's starting bit.
- `<REGISTER>__<FIELD>_MASK` gives the field's 32-bit mask.

AMDGPU code consumes these definitions through register helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `SOC15_REG_OFFSET`, `RREG32_SOC15`, `WREG32_SOC15`, and `WREG32_SOC15_OFFSET`. The direct in-tree implementation for this header is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/mmhub_v1_7.c`, which includes both `mmhub_1_7_offset.h` and `mmhub_1_7_sh_mask.h`.

## Important Macro Families

### VM Context Control

The first part of the chunk completes `VM_CONTEXT10_CNTL` and defines complete `VM_CONTEXT11_CNTL` through `VM_CONTEXT15_CNTL` layouts. These context-control registers share the same field encoding:

- `ENABLE_CONTEXT`
- `PAGE_TABLE_DEPTH`
- `PAGE_TABLE_BLOCK_SIZE`
- `RETRY_PERMISSION_OR_INVALID_PAGE_FAULT`
- `RETRY_OTHER_FAULT`
- range, dummy-page, PDE0, valid, read, write, and execute protection-fault interrupt/default enable bits

`VM_CONTEXTS_DISABLE` then provides one disable bit per context from `DISABLE_CONTEXT_0` through `DISABLE_CONTEXT_15`.

These fields are used by MMHUB VM setup to enable address translation for VMIDs and determine how faults are handled. In `mmhub_v1_7_setup_vmid_config()`, the driver programs contexts 1 through 15 by offsetting from `regVM_CONTEXT1_CNTL`, setting `ENABLE_CONTEXT`, page-table depth, block size, default-fault routing bits, and retry behavior. In `mmhub_v1_7_enable_system_domain()`, context 0 is enabled with the VMID0 page-table depth and block size. In `mmhub_v1_7_gart_disable()`, the driver clears all 16 context-control registers.

### Invalidate Engine Semaphores, Requests, Acks, and Ranges

The chunk defines four repeated register groups for invalidate engines 0 through 17:

- `VM_INVALIDATE_ENGn_SEM`, with a single `SEMAPHORE` bit.
- `VM_INVALIDATE_ENGn_REQ`, with `PER_VMID_INVALIDATE_REQ`, `FLUSH_TYPE`, `INVALIDATE_L2_PTES`, `INVALIDATE_L2_PDE0`, `INVALIDATE_L2_PDE1`, `INVALIDATE_L2_PDE2`, `INVALIDATE_L1_PTES`, `CLEAR_PROTECTION_FAULT_STATUS_ADDR`, and `LOG_REQUEST`.
- `VM_INVALIDATE_ENGn_ACK`, with `PER_VMID_INVALIDATE_ACK` and `SEMAPHORE`.
- `VM_INVALIDATE_ENGn_ADDR_RANGE_LO32/HI32`, with `S_BIT`, low logical page-address bits, and high logical page-address bits.

The request field layout is the core software contract for MMHUB TLB and page-walk-cache invalidation. Driver code selects a VMID bitmap, chooses the flush type, requests PTE/PDE/L1 invalidation, optionally clears fault status address state, and then waits for the matching acknowledgement bits. The macros also define the per-engine address-range encoding used for range-limited or full-range invalidation.

In `mmhub_v1_7_init()`, the driver records the SOC15 address for `regVM_INVALIDATE_ENG0_REQ` and `regVM_INVALIDATE_ENG0_ACK`, and computes `hub->eng_distance` from `regVM_INVALIDATE_ENG1_REQ - regVM_INVALIDATE_ENG0_REQ`. It also computes `hub->eng_addr_distance` from the address-range register spacing. `mmhub_v1_7_program_invalidation()` uses that spacing to initialize all 18 invalidate engine address ranges to the full supported range (`LO32 = 0xffffffff`, `HI32 = 0x1f`).

### VM Context Page-Table Addresses

The chunk defines page-table base address registers for contexts 0 through 15:

- `VM_CONTEXTn_PAGE_TABLE_BASE_ADDR_LO32`
- `VM_CONTEXTn_PAGE_TABLE_BASE_ADDR_HI32`

It also defines logical page-number aperture bounds for each context:

- `VM_CONTEXTn_PAGE_TABLE_START_ADDR_LO32/HI32`
- `VM_CONTEXTn_PAGE_TABLE_END_ADDR_LO32/HI32`

The base address fields are full 32-bit low/high pieces of the page-directory entry address. Start and end address fields use full low 32-bit logical page numbers and 4-bit high logical page-number fragments.

`mmhub_v1_7_setup_vm_pt_regs()` writes context page-table base registers using `hub->ctx_addr_distance` and the context 0 base-register pair. `mmhub_v1_7_init_gart_aperture_regs()` programs VMID0 start/end based on either the GART aperture or a combined VRAM-plus-GART aperture when `pdb0_bo` is used. `mmhub_v1_7_setup_vmid_config()` initializes contexts 1 through 15 with start address 0 and end address `adev->vm_manager.max_pfn - 1`.

### SR-IOV, VF Framebuffer Partitioning, and XGMI IOV

The `mmhub_utcl2_vmsharedhvdec` block defines hypervisor/shared fields that are relevant to virtualization and multi-function GPU operation:

- `MC_VM_FB_SIZE_OFFSET_VF0` through `MC_VM_FB_SIZE_OFFSET_VF15`, each packing `VF_FB_SIZE` and `VF_FB_OFFSET`.
- `MC_SHARED_ACTIVE_FCN_ID`, with `VFID` and `VF` fields indicating the active virtual function identity.
- `MC_VM_XGMI_GPUIOV_ENABLE`, with one enable bit for each VF 0 through 15 and a high PF enable bit.
- `MC_SHARED_VIRT_RESET_REQ` in the PF block, with VF and PF reset request bits.

These definitions describe hardware partition state rather than normal process VM state. They are privilege-sensitive: the PF/hypervisor side can use these fields to isolate framebuffer apertures and XGMI GPU IOV access for virtual functions, while VF paths in `mmhub_v1_7.c` intentionally skip several privileged setup steps such as system aperture programming, L2 cache programming, and clock-gating changes.

### MARC Windows and Relocation

The same hypervisor/shared block defines four MARC windows:

- `MC_VM_MARC_BASE_LO/HI_0..3`
- `MC_VM_MARC_RELOC_LO/HI_0..3`
- `MC_VM_MARC_LEN_LO/HI_0..3`

The low base/relocation/length fields start at bit 12, indicating page-aligned quantities. Each relocation-low register also includes `MARC_ENABLE_n` and `MARC_READONLY_n`. These fields represent address-window remapping and optional read-only behavior. The macros do not encode when the windows are legal to program or how they interact with IOMMU/VM policy; that sequencing must come from the owning MMHUB, firmware, or virtualization code.

### PCIe ATS and ATC Enablement

`VM_PCIE_ATS_CNTL` defines `STU` and `ATC_ENABLE` for the PF/global path. `VM_PCIE_ATS_CNTL_VF_0` through `VM_PCIE_ATS_CNTL_VF_15` define per-VF `ATC_ENABLE` bits. The VC block's `MC_VM_MX_L1_TLB_CNTL` also contains `ATC_EN`, so ATS/ATC state is split across PCIe-facing and MMHUB L1 TLB controls.

`mmhub_v1_7_init_tlb_regs()` sets `MC_VM_MX_L1_TLB_CNTL__ATC_EN` along with L1 TLB enablement, system access mode, advanced driver model, unmapped system aperture handling, and MTYPE. Correct ATC/ATS state is important for coherent PCIe address translation and for virtualized configurations where VF enablement may be controlled separately from PF policy.

### PF/Shared Apertures, Cacheability, and Local Memory Controls

The `mmhub_utcl2_vmsharedpfdec` block defines fields for PF/shared memory mapping:

- `MC_VM_FB_OFFSET`
- `MC_VM_SYSTEM_APERTURE_DEFAULT_ADDR_LSB/MSB`
- `MC_VM_STEERING`
- `MC_MEM_POWER_LS`
- `MC_VM_CACHEABLE_DRAM_ADDRESS_START/END`
- `MC_VM_APT_CNTL`
- `MC_VM_LOCAL_HBM_ADDRESS_START/END`
- `MC_VM_LOCAL_HBM_ADDRESS_LOCK_CNTL`
- `MC_VM_XGMI_LFB_CNTL`
- `MC_VM_XGMI_LFB_SIZE`
- `MC_VM_CACHEABLE_DRAM_CNTL`
- `MC_VM_HOST_MAPPING`

`mmhub_v1_7_init_system_aperture_regs()` uses the system aperture default address fields to route unmapped/protected system aperture accesses to the scratch page. It also programs the protection fault default address and L2 fault-control state outside this chunk. Other fields in this block control cacheability, local HBM aperture bounds and lock state, XGMI local framebuffer region/size, and host-mapping mode.

`MC_VM_APT_CNTL` is a compact policy register with `FORCE_MTYPE_UC`, `DIRECT_SYSTEM_EN`, `CHECK_IS_LOCAL`, and `PERMS_GRANTED`. Although `mmhub_v1_7.c` does not directly program this specific register in the inspected lines, same-generation golden-value tables in the AMDGPU tree program related `*_VM_APT_CNTL` registers for GC/IMU paths. That makes these fields part of system/host-memory routing policy rather than an isolated debug register.

### UTCL2 Clock Gating and VC Apertures

`UTCL2_CGTT_CLK_CTRL` defines clock-gating timing and override fields:

- `ON_DELAY`
- `OFF_HYSTERESIS`
- `SOFT_OVERRIDE_EXTRA`
- `MGLS_OVERRIDE`
- `SOFT_STALL_OVERRIDE`
- `SOFT_OVERRIDE`

The final `mmhub_utcl2_vmsharedvcdec` block defines virtual-client visible aperture and L1 TLB fields:

- `MC_VM_FB_LOCATION_BASE/TOP`
- `MC_VM_AGP_TOP/BOT/BASE`
- `MC_VM_SYSTEM_APERTURE_LOW_ADDR/HIGH_ADDR`
- `MC_VM_MX_L1_TLB_CNTL`

`mmhub_v1_7_get_fb_location()` masks `MC_VM_FB_LOCATION_BASE__FB_BASE_MASK` and `MC_VM_FB_LOCATION_TOP__FB_TOP_MASK` and shifts the values by 24 to populate `adev->gmc.fb_start` and `adev->gmc.fb_end`. `mmhub_v1_7_init_system_aperture_regs()` programs AGP and system aperture bounds, with a special path disabling FB/AGP apertures when VRAM is squeezed into the GART aperture. `mmhub_v1_7_init_tlb_regs()` and `mmhub_v1_7_gart_disable()` use `MC_VM_MX_L1_TLB_CNTL` fields to enable or disable MMHUB L1 translation behavior.

## Control Flow

This header has no runtime control flow. Its only behavior is compile-time substitution of symbolic masks and shifts.

The implied runtime flow in the MMHUB 1.7 driver is:

1. `mmhub_v1_7.c` includes this shift/mask header and the matching offset header.
2. Initialization code computes register spacing and records hub register addresses in `adev->vmhub[AMDGPU_MMHUB0(0)]`.
3. GART/MMHUB setup writes page-table base/start/end registers, aperture registers, L1 TLB controls, L2 controls, context-control registers, and invalidate range registers.
4. VM invalidation paths use the recorded engine request/ack addresses and field encodings to request flushes and observe completion.
5. Suspend/resume, reset, SR-IOV, and clock/power-management paths preserve, skip, or reprogram subsets of this hardware state according to device mode.

The header does not encode ordering, polling, timeout, privilege, reset, or clear-on-write semantics. Those constraints live in driver code, firmware contracts, and the hardware specification.

## State and Persistence Behavior

The macros themselves are stateless. Persistent state exists in MMHUB hardware registers and in the memory objects whose addresses are programmed into those registers.

Hardware state represented by this chunk includes enabled VM contexts, page-table depth and block-size configuration, retry/default fault behavior, disabled-context bits, invalidate engine semaphore/request/ack state, invalidate address ranges, per-context page-table roots and aperture bounds, per-VF framebuffer partitions, MARC remap windows, PCIe ATS/ATC enables, active function selection, XGMI IOV enables, system/default aperture addresses, AGP and FB locations, cacheable/local memory aperture state, L1 TLB policy, clock-gating timing, and host mapping policy.

Some fields are durable configuration that persists until reset or reprogramming, such as context page-table bases, aperture bounds, L1 TLB control, VF framebuffer size/offset, and MARC windows. Other fields are transactional or status-like, especially invalidate `REQ`, `ACK`, and `SEM` fields, virtual reset request bits, and lock/control bits. Consumers must avoid treating all masks as ordinary persistent configuration.

## Dependencies and Integration Points

This chunk depends on the generated MMHUB 1.7 register set staying synchronized:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mmhub/mmhub_1_7_offset.h` supplies register offsets for the names defined here.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mmhub/mmhub_1_7_default.h`, where present for the broader file, supplies reset/default values outside this chunk.
- AMDGPU SOC15 helpers provide the actual address calculation and MMIO access behavior.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/mmhub_v1_7.c` is the direct consumer for MMHUB 1.7 VM setup, GART enable/disable, system aperture setup, L1 TLB setup, invalidation range initialization, and hub register address bookkeeping.
- Shared AMDGPU VM and GMC structures, especially `struct amdgpu_vmhub` and `adev->gmc`, provide the page-table roots, aperture bounds, VMID dimensions, and cached register addresses that are programmed with these masks.

Similar-looking macros exist in other MMHUB, GFXHUB, GMC, and DCN generation headers. They must not be substituted across ASIC families by name alone, because field names can remain stable while offsets, masks, widths, and privilege domains change.

## Risks and Edge Cases

- Generated bitfield drift is high impact. A wrong shift or mask can program the wrong MMHUB field while still compiling cleanly.
- This chunk starts mid-register at `VM_CONTEXT10_CNTL`; complete context-control coverage requires the previous chunk for contexts 0 through 10.
- Repeated families are easy to corrupt mechanically. Contexts 0 through 15, invalidate engines 0 through 17, VF registers 0 through 15, and MARC windows 0 through 3 rely on stable spacing and consistent naming.
- Invalidate request/ack fields are sequencing-sensitive. Missing `ACK` polling, using the wrong engine distance, or invalidating the wrong VMID bitmap can leave stale translations or cause VM faults after page-table updates.
- Page-table start/end fields have narrower high parts than base-address fields. Treating all high registers as full 32-bit quantities can produce incorrect logical aperture bounds.
- Fault behavior fields affect recovery policy. Incorrect default-fault, retry, read/write/execute, or clear-fault-status settings can convert recoverable faults into hangs, hide diagnostic fault addresses, or route accesses to an unexpected dummy page.
- SR-IOV and XGMI IOV fields are isolation-sensitive. Incorrect VF framebuffer size/offset, ATC enablement, active function ID, XGMI enable, or virtual reset fields can break PF/VF isolation or multi-GPU partitioning.
- MARC relocation and read-only fields describe address remapping. Incorrect programming can redirect memory traffic or grant writes where only reads should be permitted.
- Clock-gating and light-sleep timing fields can affect stability. Bad UTCL2 clock override or hysteresis settings may produce intermittent memory-translation failures that look like workload-specific hangs.
- The direct driver skips privileged setup in VF mode. Any future use of PF/shared fields must preserve those SR-IOV checks.

## Test and Validation Signals

Useful validation is mostly generated-data consistency plus MMHUB integration coverage:

- Build AMDGPU with MMHUB 1.7 support enabled; this catches missing or renamed macros in `mmhub_v1_7.c`.
- Mechanically compare shifts and masks in this chunk against AMD's authoritative MMHUB 1.7 register database.
- Boot on matching hardware and verify GART enablement, framebuffer location discovery, VMID0 setup, and contexts 1 through 15 setup complete without MMHUB VM faults.
- Exercise VM bind/unbind and page-table update paths that trigger invalidate engine requests, then verify acknowledgements arrive for the requested VMID bitmap.
- Test XNACK/retry-fault behavior, because `mmhub_v1_7_setup_vmid_config()` enables retry permission or invalid-page faults for contexts 1 through 15.
- Run suspend/resume and GPU reset paths to confirm page-table bases, L1 TLB control, system aperture, AGP/FB locations, and invalidation range setup are restored correctly.
- Run SR-IOV PF and VF configurations to verify privileged aperture/cache setup is skipped for VFs while VF-visible translation still works.
- Exercise PCIe ATS/ATC and XGMI-connected configurations where address translation and local framebuffer controls can differ from the non-virtualized, non-XGMI path.
- Use register dumps to decode `MC_VM_MX_L1_TLB_CNTL`, `VM_INVALIDATE_ENG*_REQ/ACK`, `VM_CONTEXT*_PAGE_TABLE_*`, and `MC_VM_FB_LOCATION_*` values with these masks and compare against expected driver state.

## Cross-Chunk Notes

This is only the chunk research document for `subset-b-002771`. The final per-file report should merge this with adjacent chunks for complete `mmhub_1_7_sh_mask.h` coverage. The previous chunk owns the beginning of the VM context-control family and earlier MMHUB L2/fault-control fields; this chunk owns the end of the file through `#endif`.
