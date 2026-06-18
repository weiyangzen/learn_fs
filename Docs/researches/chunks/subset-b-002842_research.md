# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mmhub/mmhub_9_4_1_sh_mask.h lines 2368-4723

## Scope

This chunk covers part of the generated AMD MMHUB 9.4.1 shift/mask header. It starts inside the `DAGB1_RD_CNTL_MISC` register field list, continues through the remainder of the `DAGB1` DAGB decode block, then enters `addressBlock: mmhub_dagb_dagbdec2` and covers the `DAGB2` read path plus the early/middle write path. The final covered line is `DAGB2_WR_VC1_CNTL__OSD_LIMITER_ENABLE_MASK`; `DAGB2_WR_VC1_CNTL__MAX_OSD_MASK` and later write virtual-channel registers are in the next chunk.

The file is generated register metadata. It defines no C functions, structs, storage, locking, allocation, or runtime control flow. Its usable API is the preprocessor naming convention:

- `<REGISTER>__<FIELD>__SHIFT` gives the bit offset for a register field.
- `<REGISTER>__<FIELD>_MASK` gives the 32-bit field mask for that field.

## Purpose

`mmhub_9_4_1_sh_mask.h` is the bitfield companion to the MMHUB 9.4.1 register address/default headers. The matching `mmhub_9_4_1_offset.h` supplies symbols such as `mmDAGB1_CNTL_MISC2`, `mmDAGB1_WRCLI_GPU_SNOOP_OVERRIDE`, `mmDAGB2_RD_CNTL_MISC`, and `mmDAGB2_WR_VC1_CNTL`; this chunk supplies the masks and shifts needed to compose or decode those register values.

Within the AMDGPU driver, these definitions are consumed through register helper macros such as `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32_SOC15_OFFSET`, `WREG32_SOC15_OFFSET`, and `SOC15_REG_OFFSET`. `amdgpu/mmhub_v9_4.c` directly includes this header and uses these families to configure MMHUB instance register spacing, SDMA snoop override bits, and DAGB clock-gating controls.

## Important Macro Families

### DAGB1 Read-Tail and Pending State

The chunk begins at line 2368 after the first two `DAGB1_RD_CNTL_MISC` shift fields. The visible fields cover `IO_EA_CREDIT`, legacy credit-control mode bits, `UTCL2_CID`, read-return FIFO credits, and all masks for `STOR_POOL_CREDIT`, `EA_POOL_CREDIT`, and related credit fields.

`DAGB1_RD_TLB_CREDIT` then packs six five-bit TLB credit fields (`TLB0` through `TLB5`) into one register. The following `DAGB1_RDCLI_*_PENDING` registers expose full-width `BUSY` bitmaps for ask, go, global-send, TLB, OARB, and OSD pending read-client state.

### DAGB1 Write Client Controls

`DAGB1_WRCLI0` through `DAGB1_WRCLI15` are repeated per-client write controls. Each client has identical fields:

- `VIRT_CHAN` chooses the write virtual channel.
- `CHECK_TLB_CREDIT` enables TLB-credit checking.
- `URG_HIGH` and `URG_LOW` define urgency thresholds.
- `MAX_BW_ENABLE`/`MAX_BW` and `MIN_BW_ENABLE`/`MIN_BW` implement bandwidth shaping.
- `OSD_LIMITER_ENABLE` and `MAX_OSD` control outstanding request limiting.

The repetition means mechanical correctness matters. A single shifted field in one client can alter QoS, throttling, or outstanding depth for that traffic source without causing a compile error.

### DAGB1 Write Path Policy, Crossbar Timers, and Credits

`DAGB1_WR_CNTL` defines write-side global policy: SCLK frequency, client and VC bandwidth windows, IO-level override, IO compliance VC, and shared VC selection. `DAGB1_WR_GMI_CNTL` adds EA credit, level, max burst, and lazy timer fields for GMI-oriented behavior.

`DAGB1_WR_ADDR_DAGB` and `DAGB1_WR_DATA_DAGB` configure address/data DAGB enables, jump-ahead behavior, self-init disable, and `WHOAMI`. The `*_MAX_BURST0/1` and `*_LAZY_TIMER0/1` groups pack four-bit controls for clients 0-15. `DAGB1_WR_OUTPUT_DAGB_MAX_BURST` and `DAGB1_WR_OUTPUT_DAGB_LAZY_TIMER` similarly pack per-VC output max-burst and lazy-timer values for VC0-VC7.

`DAGB1_WR_VC0_CNTL` through `DAGB1_WR_VC7_CNTL` provide virtual-channel-level storage/EA credits, max/min bandwidth limits, OSD limiting, and max outstanding depth. `DAGB1_WR_CNTL_MISC`, `DAGB1_WR_TLB_CREDIT`, `DAGB1_WR_DATA_CREDIT`, and `DAGB1_WR_MISC_CREDIT` define shared write credit pools, burst-size credits, atomic credits, OSD credits, and deadlock VC credit fields.

### DAGB1 Debug, Status, Clock Gating, and Counters

`DAGB1_WRCLI_*_PENDING` mirrors the read pending bitmaps for write ask/go/global-send/TLB/OARB/OSD plus DBUS ask/go. `DAGB1_WRCLI_GPU_SNOOP_OVERRIDE` and `DAGB1_WRCLI_GPU_SNOOP_OVERRIDE_VALUE` are full-width client bitmaps. In `mmhub_v9_4.c`, the driver computes the distance from DAGB0 to DAGB1 and then sets bit 15 for SDMA snoop override/value across DAGB instances.

`DAGB1_CNTL_MISC` remaps EA VC0-VC7 and controls bandwidth init/gap cycles. `DAGB1_CNTL_MISC2` contains urgency boost/halt, disable bits for write/read request and return clock gating, TLB write/read clock gating, EA request busy behavior, swap control, read-return FIFO performance mode, and deadlock credits. `mmhub_v9_4_update_medium_grain_clock_gating()` uses the DAGB0 version of these masks and register-distance arithmetic to apply the same policy across DAGB instances, so matching DAGB1/DAGB2 field layouts are an integration assumption.

Status and instrumentation registers include `DAGB1_FIFO_EMPTY`, `DAGB1_FIFO_FULL`, `DAGB1_WR_CREDITS_FULL`, `DAGB1_RD_CREDITS_FULL`, `DAGB1_PERFCOUNTER_LO/HI`, `DAGB1_PERFCOUNTER0_CFG`, `DAGB1_PERFCOUNTER1_CFG`, `DAGB1_PERFCOUNTER2_CFG`, and `DAGB1_PERFCOUNTER_RSLT_CNTL`. These cover FIFO/credit saturation, counter low/high readout, compare values, event select ranges, modes, enable/clear bits, start/stop triggers, enable-any, clear-all, and stop-on-saturate.

`DAGB1_RESERVE0` through `DAGB1_RESERVE13` are full-width generated reserve placeholders. They preserve the register map shape but should not be treated as supported software-facing controls without hardware documentation.

### DAGB2 Read Path

The chunk marks the start of `addressBlock: mmhub_dagb_dagbdec2`. `DAGB2_RDCLI0` through `DAGB2_RDCLI15` mirror the `DAGB1_WRCLI*` field pattern for read clients: VC selection, TLB-credit checking, urgency thresholds, max/min bandwidth shaping, OSD limiter enable, and max OSD.

`DAGB2_RD_CNTL`, `DAGB2_RD_GMI_CNTL`, and `DAGB2_RD_ADDR_DAGB` provide read-side global bandwidth windows, IO-level override, GMI credit/burst/lazy timing, address DAGB enable/jump-ahead/self-init/identity fields. `DAGB2_RD_OUTPUT_DAGB_MAX_BURST` and `DAGB2_RD_OUTPUT_DAGB_LAZY_TIMER` pack per-VC settings. `DAGB2_RD_ADDR_DAGB_MAX_BURST0/1` and `DAGB2_RD_ADDR_DAGB_LAZY_TIMER0/1` pack per-client read address DAGB burst/timer settings.

`DAGB2_RD_CGTT_CLK_CTRL`, `DAGB2_L1TLB_RD_CGTT_CLK_CTRL`, and `DAGB2_ATCVM_RD_CGTT_CLK_CTRL` define clock-gating timing and light-sleep override controls: `ON_DELAY`, `OFF_HYSTERESIS`, `SOFT_STALL_OVERRIDE`, and low-power state override/write/read/return/register bits.

`DAGB2_RD_VC0_CNTL` through `DAGB2_RD_VC7_CNTL` mirror the VC credit and bandwidth controls described above. `DAGB2_RD_CNTL_MISC`, `DAGB2_RD_TLB_CREDIT`, and `DAGB2_RDCLI_*_PENDING` expose read credit pool fields, TLB credit fields, and full-width pending busy bitmaps.

### DAGB2 Write Path Start

The range covers `DAGB2_WRCLI0` through `DAGB2_WRCLI15`, `DAGB2_WR_CNTL`, `DAGB2_WR_GMI_CNTL`, `DAGB2_WR_ADDR_DAGB`, output per-VC max-burst/lazy-timer controls, write-side clock-gating controls, address DAGB client burst/timer controls, `DAGB2_WR_DATA_DAGB`, and write data DAGB client burst/timer controls.

The final section starts the write VC controls: all of `DAGB2_WR_VC0_CNTL` is visible, and `DAGB2_WR_VC1_CNTL` is present through `OSD_LIMITER_ENABLE_MASK`. The last `MAX_OSD_MASK` for VC1 and subsequent VC controls are outside this chunk.

## Control Flow and State Behavior

There is no executable control flow in this header. The control flow lives in AMDGPU code that includes the header and performs MMIO reads/writes. The macros in this range are compile-time constants that allow those code paths to preserve unrelated bits while setting or decoding specific fields.

The represented state is hardware register state. Some fields are durable configuration until reset or reprogramming, including bandwidth windows, VC maps, credits, max burst, lazy timers, OSD limits, clock-gating disable/override bits, snoop override bitmaps, and DAGB enable/self-init controls. Other fields are status or command-like: pending `BUSY` bitmaps, FIFO empty/full state, credit-full indicators, counter clear/enable/trigger bits, and performance counter readouts.

Persistence and ordering are not described by this header. Correct callers must rely on the owning MMHUB initialization, power-management, clock-gating, RAS, and debug paths for read-modify-write ordering, polling, reset, and suspend/resume sequencing.

## Dependencies and Integration Points

This chunk depends on the generated MMHUB 9.4.1 header set:

- `mmhub_9_4_1_offset.h` provides the matching `mm*` register address macros and base indices.
- `mmhub_9_4_1_default.h` provides reset/default values for registers such as `mmDAGB1_CNTL_MISC2`, `mmDAGB2_RD_CNTL_MISC`, and `mmDAGB2_WR_VC1_CNTL`.
- `soc15.h` and AMDGPU MMIO helpers consume the field naming convention through `REG_SET_FIELD`, `REG_GET_FIELD`, and SOC15 read/write helpers.

Observed integration in this tree:

- `amdgpu/mmhub_v9_4.c` includes `mmhub_9_4_1_sh_mask.h`, `mmhub_9_4_1_offset.h`, and `mmhub_9_4_1_default.h`.
- `mmhub_v9_4_init_snoop_override_regs()` uses the spacing between `mmDAGB1_WRCLI_GPU_SNOOP_OVERRIDE` and `mmDAGB0_WRCLI_GPU_SNOOP_OVERRIDE` to apply SDMA snoop override bit 15 across DAGB instances.
- `mmhub_v9_4_update_medium_grain_clock_gating()` uses the spacing between `mmDAGB1_CNTL_MISC2` and `mmDAGB0_CNTL_MISC2` plus `DAGB0_CNTL_MISC2__DISABLE_*_CG_MASK` fields to toggle DAGB clock gating across instances. The repeated DAGB1/DAGB2 layouts in this chunk support that distance-based programming model.
- `mmhub_v9_4_setup_vm_pt_regs()` and adjacent MMHUB setup paths demonstrate the broader pattern: read a register, update fields with generated masks/shifts, then write it back at a hub instance offset.

## Risks

- Bitfield drift is high impact. A wrong shift or mask can alter unrelated MMHUB hardware fields, producing GPU hangs, bad memory traffic throttling, broken snoop behavior, incorrect credit accounting, or misleading performance/status reads.
- Repeated client and VC families are easy to corrupt with mechanical edits. `DAGB1_WRCLI*`, `DAGB2_RDCLI*`, and `DAGB2_WRCLI*` all look similar but target different DAGB instances and traffic directions.
- Clock-gating masks in `CNTL_MISC2` affect power-management stability. Incorrect disable/enable bits can block low-power states or gate a live request/return path.
- Snoop override registers are full-width client bitmaps. Setting the wrong client bit can leave SDMA writes without expected probe invalidation or apply snoop override to an unrelated client.
- Credit and OSD fields can deadlock or starve traffic if programmed outside hardware expectations. This is especially sensitive for TLB credits, deadlock VC credits, burst credits, and max outstanding depths.
- Pending/status fields are not configuration knobs. Treating `BUSY`, FIFO, credit-full, or perf counter readout masks as writable policy fields would be a driver bug.
- Reserve registers are generated map placeholders. Software should not infer stable behavior from `DAGB1_RESERVE*`.
- The chunk starts and ends mid-register-family. Any final per-file summary must merge adjacent chunks before claiming complete coverage of `DAGB1_RD_CNTL_MISC` or `DAGB2_WR_VC1_CNTL`.

## Test and Validation Signals

Useful validation is mostly compile, integration, and hardware bring-up:

- Build AMDGPU code that includes `mmhub/mmhub_9_4_1_sh_mask.h`; this catches missing or renamed generated macros.
- Exercise MMHUB 9.4 initialization on supported hardware and verify `mmhub_v9_4_init_snoop_override_regs()` applies SDMA snoop override across the expected DAGB instance count.
- Run suspend/resume and clock-gating tests with `AMD_CG_SUPPORT_MC_MGCG` and `AMD_CG_SUPPORT_MC_LS` enabled/disabled to catch incorrect `CNTL_MISC2` or CGTT field behavior.
- Use memory traffic stress tests to cover read/write clients, virtual-channel throttling, OSD limiting, burst/lazy-timer controls, and credit pool pressure.
- Validate perf counter programming by selecting DAGB events, clearing/enabling counters, using trigger fields, and checking low/high readout behavior.
- During debug or hardware validation, poll pending, FIFO empty/full, and credit-full registers while traffic is active and idle to confirm masks decode expected busy and saturation bits.
- Compare generated masks against AMD register specifications or a known-good generated header; these headers are too repetitive for manual review to be the only assurance.

## Unresolved Cross-Chunk References

Lines 2366-2367 define the first two `DAGB1_RD_CNTL_MISC` shifts and are in the previous chunk, while this chunk starts at line 2368. Line 4724 completes `DAGB2_WR_VC1_CNTL` with `MAX_OSD_MASK`, but this chunk stops at line 4723. The merge lane should stitch those boundaries before producing the source-file-level research document.
