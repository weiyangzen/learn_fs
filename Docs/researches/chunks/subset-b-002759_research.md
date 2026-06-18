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
