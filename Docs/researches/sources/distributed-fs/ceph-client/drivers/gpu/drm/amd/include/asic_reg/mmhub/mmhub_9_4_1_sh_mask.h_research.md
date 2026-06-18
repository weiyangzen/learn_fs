# Research: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mmhub/mmhub_9_4_1_sh_mask.h

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-002841`: lines 1-2367, `Docs/researches/chunks/subset-b-002841_research.md`
- `subset-b-002842`: lines 2368-4723, `Docs/researches/chunks/subset-b-002842_research.md`
- `subset-b-002843`: lines 4724-7102, `Docs/researches/chunks/subset-b-002843_research.md`
- `subset-b-002844`: lines 7103-9460, `Docs/researches/chunks/subset-b-002844_research.md`
- `subset-b-002845`: lines 9461-11822, `Docs/researches/chunks/subset-b-002845_research.md`
- `subset-b-002846`: lines 11823-14186, `Docs/researches/chunks/subset-b-002846_research.md`
- `subset-b-002847`: lines 14187-16550, `Docs/researches/chunks/subset-b-002847_research.md`
- `subset-b-002848`: lines 16551-18899, `Docs/researches/chunks/subset-b-002848_research.md`
- `subset-b-002849`: lines 18900-21241, `Docs/researches/chunks/subset-b-002849_research.md`
- `subset-b-002850`: lines 21242-23604, `Docs/researches/chunks/subset-b-002850_research.md`
- `subset-b-002851`: lines 23605-25971, `Docs/researches/chunks/subset-b-002851_research.md`
- `subset-b-002852`: lines 25972-28443, `Docs/researches/chunks/subset-b-002852_research.md`
- `subset-b-002853`: lines 28444-30822, `Docs/researches/chunks/subset-b-002853_research.md`
- `subset-b-002854`: lines 30823-33173, `Docs/researches/chunks/subset-b-002854_research.md`
- `subset-b-002855`: lines 33174-35538, `Docs/researches/chunks/subset-b-002855_research.md`
- `subset-b-002856`: lines 35539-37903, `Docs/researches/chunks/subset-b-002856_research.md`
- `subset-b-002857`: lines 37904-40269, `Docs/researches/chunks/subset-b-002857_research.md`
- `subset-b-002858`: lines 40270-42638, `Docs/researches/chunks/subset-b-002858_research.md`
- `subset-b-002859`: lines 42639-45068, `Docs/researches/chunks/subset-b-002859_research.md`

## Chunk Research

### subset-b-002841: lines 1-2367

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mmhub/mmhub_9_4_1_sh_mask.h lines 1-2367

## Scope

This chunk covers the opening 2,367 lines of the generated AMDGPU MMHUB 9.4.1 shift/mask header. The range starts the include guard `_mmhub_9_4_1_SH_MASK_HEADER`, then defines bit-field shift and mask macros for the `mmhub_dagb_dagbdec0` address block and the beginning of `mmhub_dagb_dagbdec1`. It contains the complete `DAGB0` field surface and cuts off in the first `DAGB1_RD_CNTL_MISC` fields; later lines continue that partially captured register.

Within this chunk there are 2,177 `#define` lines: one include guard define, 1,089 `__SHIFT` definitions, and 1,087 `_MASK` definitions. The shift/mask mismatch is expected because the chunk boundary lands inside `DAGB1_RD_CNTL_MISC`.

## Purpose

The file is a machine-generated hardware register field map. It does not implement executable logic; it gives the AMDGPU driver symbolic names for MMHUB 9.4.1 DAGB register bit positions and masks so C code can safely construct read-modify-write values with register helper macros such as `REG_SET_FIELD`, `RREG32_SOC15_OFFSET`, and `WREG32_SOC15_OFFSET`.

The `DAGB` blocks covered here describe arbitration, credits, virtual channels, outstanding request limits, pending status, clock gating, snoop override, FIFO/credit status, and performance counter controls for MMHUB data/address gateway blocks. These fields matter because MMHUB owns GPU memory-management traffic routing between clients, TLBs, memory fabric, and cache/coherency paths.

## Important Macro Families

The chunk is dominated by repeated register-field pairs:

- `DAGB0_RDCLI0` through `DAGB0_RDCLI15` and `DAGB0_WRCLI0` through `DAGB0_WRCLI15` define per-client read/write arbitration fields: `VIRT_CHAN`, `CHECK_TLB_CREDIT`, urgency thresholds, max/min bandwidth controls, OSD limiter enable, and max OSD.
- `DAGB0_RD_CNTL`, `DAGB0_WR_CNTL`, `DAGB0_RD_GMI_CNTL`, and `DAGB0_WR_GMI_CNTL` define global read/write timing and fabric-control fields such as SCLK frequency, bandwidth windows, IO level override, EA credit, level, max burst, and lazy timer.
- `DAGB0_RD_ADDR_DAGB`, `DAGB0_WR_ADDR_DAGB`, and `DAGB0_WR_DATA_DAGB` define DAGB enable, jump-ahead, self-init disable, and `WHOAMI` identity fields for address/data paths.
- `DAGB0_*_MAX_BURST*` and `DAGB0_*_LAZY_TIMER*` define packed 4-bit nibbles for VC0-VC7 or CLIENT0-CLIENT15 burst/timer tuning.
- `DAGB0_RD_VC0_CNTL` through `DAGB0_RD_VC7_CNTL` and `DAGB0_WR_VC0_CNTL` through `DAGB0_WR_VC7_CNTL` define per-virtual-channel storage credit, EA credit, bandwidth, and OSD limit fields.
- `DAGB0_RD_TLB_CREDIT` and `DAGB0_WR_TLB_CREDIT` define six packed TLB credit fields.
- `DAGB0_*_PENDING` registers expose full-width busy bitmaps for read/write client ask/go/global-send/TLB/OARB/OSD states, plus write DBUS pending states.
- `DAGB0_WRCLI_GPU_SNOOP_OVERRIDE` and `DAGB0_WRCLI_GPU_SNOOP_OVERRIDE_VALUE` expose full-width enable/value bitmaps used by the driver to force coherency behavior for selected write clients.
- `DAGB0_CNTL_MISC` and `DAGB0_CNTL_MISC2` define VC remapping, bandwidth cycle timing, urgency boost/halt, clock-gating disable bits for request/return/TLB paths, busy behavior disables, swap control, and read-return FIFO deadlock credits.
- `DAGB0_FIFO_EMPTY`, `DAGB0_FIFO_FULL`, `DAGB0_WR_CREDITS_FULL`, and `DAGB0_RD_CREDITS_FULL` expose status bitmaps.
- `DAGB0_PERFCOUNTER_*` defines low/high counter values, compare value, counter selection/configuration, triggers, enable, clear, and stop-on-saturate controls.
- `DAGB0_RESERVE0` through `DAGB0_RESERVE13` reserve full 32-bit register fields.
- `DAGB1_RDCLI0` through `DAGB1_RD_VC7_CNTL` repeat the read-side DAGB0 pattern for the next DAGB decoder instance; `DAGB1_RD_CNTL_MISC` begins at the chunk boundary.

## APIs, Types, and Functions

There are no C functions, structs, enums, or storage objects in this chunk. The exported API is the preprocessor namespace itself:

- `<REGISTER>__<FIELD>__SHIFT` macros provide bit offsets.
- `<REGISTER>__<FIELD>_MASK` macros provide the corresponding register masks.

Consumers are expected to combine these macros with the matching MMHUB 9.4.1 offset header (`mmhub_9_4_1_offset.h`) and AMDGPU register access helpers. The naming convention is part of the interface: register names here match `mmDAGB...` register address macros from the offset header and field names used by AMDGPU register helper macros.

## Control Flow

This header contributes no runtime branches or sequencing. Control flow appears only in consumers that use the masks during MMHUB setup and power-management transitions.

The directly relevant consumer is `drivers/gpu/drm/amd/amdgpu/mmhub_v9_4.c`, which includes this header with `mmhub_9_4_1_offset.h` and `mmhub_9_4_1_default.h`. Two visible call paths use fields from this chunk:

- `mmhub_v9_4_init_snoop_override_regs()` computes the distance between `mmDAGB1_WRCLI_GPU_SNOOP_OVERRIDE` and `mmDAGB0_WRCLI_GPU_SNOOP_OVERRIDE`, iterates DAGB instances across the two MMHUB instances, and sets bit 15 in both override and override-value registers so SDMA writes probe-invalidate RW lines.
- `mmhub_v9_4_update_medium_grain_clock_gating()` computes the distance between `mmDAGB1_CNTL_MISC2` and `mmDAGB0_CNTL_MISC2`, then clears or sets the `DAGB0_CNTL_MISC2__DISABLE_*_CG_MASK` bits across DAGB instances depending on `AMD_CG_SUPPORT_MC_MGCG` and the requested clock-gating state. `mmhub_v9_4_get_clockgating()` reads related masks when reporting clock-gating state.

## State and Persistence Behavior

The macros themselves are compile-time constants and hold no state. They describe persistent MMIO register state in the GPU. Writes using these masks affect hardware configuration until overwritten by later driver actions, GPU reset/reinitialization, power management transitions, or firmware/hardware reset behavior.

State represented by this chunk includes client-to-VC mapping, per-client and per-VC bandwidth/credit limits, outstanding request controls, pending/busy status, snoop override state, clock-gating disable state, FIFO/credit status, and performance counter programming. Status-style registers such as `*_PENDING`, `*_FIFO_*`, `*_CREDITS_FULL`, and perf counter result registers should be treated as live hardware observations, not durable software state.

## Dependencies and Integration Points

This header depends on inclusion from AMDGPU ASIC-specific code that already knows the MMHUB 9.4.1 register addresses. It is paired with:

- `mmhub_9_4_1_offset.h` for register addresses such as `mmDAGB0_CNTL_MISC2` and `mmDAGB1_WRCLI_GPU_SNOOP_OVERRIDE`.
- `mmhub_9_4_1_default.h` for default register values.
- AMDGPU SOC15 register helpers in `soc15.h` / `soc15_common.h`.
- Higher-level MMHUB logic in `amdgpu/mmhub_v9_4.c`.

The DAGB0/DAGB1 spacing assumptions are important integration details. `mmhub_v9_4.c` derives per-DAGB register offsets by subtracting DAGB0 addresses from DAGB1 addresses, then applying that distance in loops. Field masks from this header must remain aligned with those address macros, or read-modify-write operations may alter the wrong bits in repeated DAGB instances.

## Risks

- Because this is generated hardware metadata, a single incorrect mask or shift can silently corrupt unrelated register fields during read-modify-write operations.
- Full-width masks such as `0xFFFFFFFFL` for pending, reserve, perf low, and snoop override registers require consumers to know which bits are meaningful for a specific ASIC and client topology.
- Repeated DAGB0/DAGB1 patterns make copy-generation errors hard to detect by review. DAGB instance spacing used by consumers depends on consistent register layout across instances.
- Clock-gating masks in `DAGB0_CNTL_MISC2` are power-management sensitive. Reversed semantics or stale masks can leave memory-controller clock gating disabled, or gate paths that must remain active.
- The chunk boundary splits `DAGB1_RD_CNTL_MISC`; research or reconciliation that treats this chunk as a complete file-level view could miss the remaining masks and shifts.

## Test Signals

Useful validation signals are mostly compile-time and hardware bring-up oriented:

- Build AMDGPU with `mmhub_v9_4.c` enabled and confirm all referenced `DAGB0_*` and `DAGB1_*` masks resolve against this header.
- On MMHUB 9.4.1 ASICs, exercise driver init and confirm SDMA coherency-sensitive workloads pass after `mmhub_v9_4_init_snoop_override_regs()` sets SDMA client bit 15.
- Toggle medium-grain clock gating and verify `AMD_CG_SUPPORT_MC_MGCG` reporting changes as expected without memory faults, hangs, or RAS noise.
- Use register dumps before/after clock-gating transitions to confirm only `DAGB*_CNTL_MISC2` clock-gating disable bits change.
- Run GPU memory stress, VM fault, SDMA copy, suspend/resume, and reset tests; failures in these areas can indicate bad MMHUB routing, credit, snoop, or clock-gating field definitions.

### subset-b-002842: lines 2368-4723

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

### subset-b-002843: lines 4724-7102

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mmhub/mmhub_9_4_1_sh_mask.h lines 4724-7102

## Scope

This chunk covers the middle of the generated AMDGPU MMHUB 9.4.1 shift/mask header. The range starts inside the `mmhub_dagb_dagbdec2` address block, completing the later `DAGB2_WR_*` write-side virtual-channel, credit, status, snoop, misc, FIFO, counter, and reserve definitions. It then covers the complete visible `mmhub_dagb_dagbdec3` block for `DAGB3`, and ends just after the first shift definition of `DAGB4_RD_GMI_CNTL` in the next `mmhub_dagb_dagbdec4` block.

The source is hardware register metadata, not executable driver logic. It defines preprocessor constants named as `<REGISTER>__<FIELD>__SHIFT` and `<REGISTER>__<FIELD>_MASK`. The matching register offsets are in `mmhub_9_4_1_offset.h`; consumers pair those offsets with the masks here through AMDGPU helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32_SOC15_OFFSET`, and `WREG32_SOC15_OFFSET`.

Although the repository path is under `sources/distributed-fs/ceph-client`, this chunk belongs to Linux DRM AMDGPU register programming. It has no Ceph client, distributed filesystem, networking, or storage-protocol behavior.

## Purpose

The purpose of this chunk is to provide the bit-level ABI for programming and decoding MMHUB 9.4.1 DAGB decoder instances. DAGB blocks arbitrate and meter memory-hub traffic by client and virtual channel. The fields in this range describe virtual-channel routing, TLB-credit checking, urgency thresholds, max/min bandwidth controls, outstanding-operation limits, output and per-client burst/timer tuning, clock-gating overrides, read/write credit pools, pending-status bitmaps, write-client GPU snoop overrides, FIFO/credit status, and DAGB performance counters.

The exact values are important because each register is a packed 32-bit MMIO word. Driver code can use symbolic names instead of literal bit positions, but the correctness of every later read/modify/write depends on these masks matching the hardware register database for MMHUB 9.4.1.

## Important APIs, Types, And Macro Families

There are no functions, structs, enums, variables, or callable APIs in this range. The exported interface is the macro namespace.

The `DAGB2_WR_*` opening slice completes the write-side controls for DAGB instance 2. It starts at the tail of `DAGB2_WR_VC1_CNTL`, then defines `DAGB2_WR_VC2_CNTL` through `DAGB2_WR_VC7_CNTL`. Each virtual-channel control register uses the same packed fields: storage credit, EA credit, maximum bandwidth enable/value, minimum bandwidth enable/value, OSD limiter enable, and maximum OSD. The same DAGB2 tail also defines write-side miscellaneous pool credits (`STOR_POOL_CREDIT`, `EA_POOL_CREDIT`, `IO_EA_CREDIT`, legacy mode bits, `UTCL2_CID`, and read-return FIFO credits), six TLB credit lanes, data burst credits, atomic/DLOCK/OSD miscellaneous credits, write-pipeline pending status bitmaps, full-width GPU snoop override enable/value bitmaps, delay selection, misc control fields, FIFO empty/full status, read/write credit-full status, performance counter registers, result-control fields, and `DAGB2_RESERVE0` through `DAGB2_RESERVE13`.

The `DAGB3_RDCLI0` through `DAGB3_RDCLI15` group defines the repeated per-read-client arbitration layout for DAGB instance 3. Each client register exposes `VIRT_CHAN`, `CHECK_TLB_CREDIT`, `URG_HIGH`, `URG_LOW`, `MAX_BW_ENABLE`, `MAX_BW`, `MIN_BW_ENABLE`, `MIN_BW`, `OSD_LIMITER_ENABLE`, and `MAX_OSD`. The matching `DAGB3_WRCLI0` through `DAGB3_WRCLI15` group repeats that layout for write clients.

`DAGB3_RD_CNTL` and `DAGB3_WR_CNTL` define aggregate read/write policy: SCLK frequency encoding, client and virtual-channel max-bandwidth windows, IO-level override, IO-level value, IO-level-compliant VC selection, and shared VC count. `DAGB3_RD_GMI_CNTL` and `DAGB3_WR_GMI_CNTL` define EA credit, level, max burst, and lazy-timer fields for GMI traffic.

`DAGB3_RD_ADDR_DAGB`, `DAGB3_WR_ADDR_DAGB`, and `DAGB3_WR_DATA_DAGB` describe core DAGB enable and identity controls: enable lanes, jump-ahead enable, self-init disable, and `WHOAMI`. The read and write address/output/data burst and lazy-timer families use 4-bit lanes. Output DAGB registers pack virtual channels 0-7 into one word, while address/data DAGB max-burst and lazy-timer registers split clients 0-7 and 8-15 into `...0` and `...1` words.

Clock and light-sleep control is represented by `DAGB3_RD_CGTT_CLK_CTRL`, `DAGB3_WR_CGTT_CLK_CTRL`, `DAGB3_L1TLB_RD_CGTT_CLK_CTRL`, `DAGB3_L1TLB_WR_CGTT_CLK_CTRL`, `DAGB3_ATCVM_RD_CGTT_CLK_CTRL`, and `DAGB3_ATCVM_WR_CGTT_CLK_CTRL`. These registers share `ON_DELAY`, `OFF_HYSTERESIS`, `SOFT_STALL_OVERRIDE`, and several `LS_OVERRIDE*` fields for write/read/return/register paths.

`DAGB3_RD_VC0_CNTL` through `DAGB3_RD_VC7_CNTL` and `DAGB3_WR_VC0_CNTL` through `DAGB3_WR_VC7_CNTL` define virtual-channel credit, bandwidth, and outstanding-depth policy. They share the storage credit, EA credit, max/min bandwidth enable/value, OSD limiter, and max OSD field layout also seen in the DAGB2 tail.

Credit and status registers include `DAGB3_RD_CNTL_MISC`, `DAGB3_RD_TLB_CREDIT`, `DAGB3_WR_CNTL_MISC`, `DAGB3_WR_TLB_CREDIT`, `DAGB3_WR_DATA_CREDIT`, and `DAGB3_WR_MISC_CREDIT`. These fields control or report pool credits, UTCL2 IDs, TLB lanes, burst credits, DLOCK VC credits, atomic credits, and OSD credits.

Pending-status groups include `DAGB3_RDCLI_ASK_PENDING`, `DAGB3_RDCLI_GO_PENDING`, `DAGB3_RDCLI_GBLSEND_PENDING`, `DAGB3_RDCLI_TLB_PENDING`, `DAGB3_RDCLI_OARB_PENDING`, `DAGB3_RDCLI_OSD_PENDING`, and the corresponding `DAGB3_WRCLI_*_PENDING` write-side registers. The write side additionally has `DAGB3_WRCLI_DBUS_ASK_PENDING` and `DAGB3_WRCLI_DBUS_GO_PENDING`. These expose full-width `BUSY` bitmaps.

`DAGB3_WRCLI_GPU_SNOOP_OVERRIDE` and `DAGB3_WRCLI_GPU_SNOOP_OVERRIDE_VALUE` expose full-width per-write-client enable/value masks. The concrete C integration in `drivers/gpu/drm/amd/amdgpu/mmhub_v9_4.c` programs this register family: `mmhub_v9_4_init_snoop_override_regs()` computes the spacing between `mmDAGB1_WRCLI_GPU_SNOOP_OVERRIDE` and `mmDAGB0_WRCLI_GPU_SNOOP_OVERRIDE`, iterates the DAGB instances assigned to each MMHUB, and sets bit 15 in both the override and override-value registers for the SDMA client.

`DAGB3_DAGB_DLY`, `DAGB3_CNTL_MISC`, and `DAGB3_CNTL_MISC2` contain cross-cutting controls such as delay selection, bandwidth-init cycle/gap timing, busy override, swap control, read-return FIFO performance control, and tap-chain clock-gating disable fields. `DAGB3_FIFO_EMPTY`, `DAGB3_FIFO_FULL`, `DAGB3_WR_CREDITS_FULL`, and `DAGB3_RD_CREDITS_FULL` expose FIFO and credit fullness/emptiness status bitmaps.

`DAGB3_PERFCOUNTER_LO`, `DAGB3_PERFCOUNTER_HI`, `DAGB3_PERFCOUNTER0_CFG`, `DAGB3_PERFCOUNTER1_CFG`, `DAGB3_PERFCOUNTER2_CFG`, and `DAGB3_PERFCOUNTER_RSLT_CNTL` define the DAGB3 performance counter block. The fields cover low/high counter words, compare value, event-select start/end, counter mode, enable, clear, result counter select, start/stop triggers, enable-any, clear-all, and stop-on-saturate.

The end of the `DAGB3` block defines `DAGB3_RESERVE0` through `DAGB3_RESERVE13` as full-width reserved fields. This is a version-specific detail: similarly shaped regions in some neighboring MMHUB headers include fatal-error or indirect L1TLB control registers, but the visible MMHUB 9.4.1 range here ends the DAGB3 block with reserve registers.

The final lines begin `DAGB4_RDCLI0` through `DAGB4_RDCLI15`, `DAGB4_RD_CNTL`, and only the first shift of `DAGB4_RD_GMI_CNTL`. The complete DAGB4 read GMI masks and later DAGB4 read/write controls continue in the next chunk.

## Control Flow

This chunk has no runtime control flow. It does not call functions, branch, allocate memory, perform IO, acquire locks, or access hardware directly.

Runtime behavior appears in consuming AMDGPU code. A typical flow is: include the offset and shift/mask headers, read a 32-bit MMHUB register with a SOC15 helper, compose or decode fields with `REG_SET_FIELD` or `REG_GET_FIELD`, and write the result back with a SOC15 helper. `mmhub_v9_4.c` follows this pattern broadly for MMHUB VM/cache/TLB setup and directly uses the DAGB register spacing and write-client snoop override register family covered by this chunk.

The generated macros influence control flow only indirectly: a caller may branch based on decoded pending, FIFO, credit, or performance-counter status, or may choose different initialization paths depending on hardware instance and SR-IOV mode. Those decisions are not represented in this header.

## State And Persistence Behavior

The macros themselves have no state and persist nothing. They are compile-time constants.

The state described by the macros is MMIO-backed hardware state inside MMHUB. Configuration fields such as VC assignment, credit budgets, bandwidth windows, OSD limits, burst/lazy timers, clock-gating overrides, snoop override bits, and counter selection persist in hardware until reset, power gating, firmware programming, suspend/resume restore, or driver reprogramming changes them. Status fields such as pending bitmaps, FIFO empty/full, credit-full flags, and performance counter values are hardware-maintained and can change while traffic is active.

Several fields are command-like or sequencing-sensitive rather than durable policy: performance counter clear bits, clear-all, start/stop triggers, busy overrides, snoop override enable/value bitmaps, and any status registers with latched or side-effect semantics. This generated header does not encode access direction, write-one-to-clear rules, polling requirements, or reset ordering.

## Dependencies And Integration Points

The immediate companion dependency is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mmhub/mmhub_9_4_1_offset.h`. In that file, examples from this range include `mmDAGB2_WR_VC2_CNTL` at `0x014f`, `mmDAGB3_RDCLI0` at `0x0180`, `mmDAGB3_WRCLI0` at `0x01ac`, `mmDAGB3_WR_VC0_CNTL` at `0x01cd`, `mmDAGB4_RDCLI0` at `0x0200`, and `mmDAGB4_RD_GMI_CNTL` at `0x0211`, all using base index 1. The masks here are meaningful only when paired with those offsets and the correct SOC15 MMHUB instance.

The main C integration point in this tree is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/mmhub_v9_4.c`, which includes `mmhub_9_4_1_offset.h`, `mmhub_9_4_1_sh_mask.h`, and `mmhub_9_4_1_default.h`. That file initializes MMHUB apertures, VM page-table bases, L1/L2 cache and TLB controls, VMID contexts, invalidation, protection fault handling, and DAGB snoop overrides for the two MMHUB instances. The specific DAGB code sets SDMA snoop override bit 15 across DAGB instances 0-4 in hub 0 and 5-7 in hub 1 by using the repeated DAGB register offset spacing.

Additional dependencies are the AMDGPU SOC15 register access layer, common register-field helpers, the generated `mmhub_9_4_1_default.h` defaults for reset/default values, and the underlying AMD register database that generated this header. Cross-generation similarity with headers such as `mmhub_1_8_0_sh_mask.h` is useful for review, but client counts, reserved regions, base indices, offsets, and field layouts must remain version-specific.

## Risks And Edge Cases

The largest risk is hardware ABI drift. A single wrong shift or mask can silently write unrelated bits in a packed MMHUB register, causing bad traffic routing, throttling, credit starvation, hangs, false pending status, incorrect power behavior, or misleading performance data.

The repeated client, VC, and DAGB-instance families are easy to review incorrectly. `RDCLI0..15`, `WRCLI0..15`, VC0..VC7 controls, burst/timer lanes, and pending masks look highly regular, so an isolated generator error in one index can evade visual inspection.

Read-side and write-side blocks are similar but not identical. Write-side blocks include data DAGB controls, data credits, miscellaneous atomic/DLOCK/OSD credits, DBUS pending status, and GPU snoop override fields. Callers must not substitute read macros for write registers or assume every read-side field has a write-side twin.

Several masks are full-width `0xFFFFFFFFL` values. Code and diagnostics should treat them as 32-bit register fields and avoid signed-format or host-width assumptions that obscure the intended bitmap semantics.

Status and control registers share the same macro style. Pending, FIFO, credit-full, performance counter result, and reserve fields should not be treated as ordinary writable policy. The header does not mark read-only, write-only, reserved, sticky, or self-clearing fields.

Clock-gating and light-sleep override fields can affect power and reset sequencing. Misprogramming `SOFT_STALL_OVERRIDE` or `LS_OVERRIDE*` bits can force a block active, hide true busy state, or interfere with low-power entry.

Snoop override fields are integration-sensitive. `mmhub_v9_4_init_snoop_override_regs()` relies on DAGB register spacing and SDMA client bit 15. A mismatch between offset spacing, hub instance mapping, or bitmap width can set the wrong client override.

The chunk boundary matters. It starts after part of `DAGB2_WR_VC1_CNTL` and ends before `DAGB4_RD_GMI_CNTL` is complete, so the final per-file report must merge adjacent chunks before making complete statements about DAGB2 and DAGB4.

## Test Signals

There are no unit tests for this macro-only chunk. Useful validation is build-time, static, and hardware-observation based:

- Compile AMDGPU code that includes `mmhub_9_4_1_sh_mask.h`, especially `mmhub_v9_4.c`, to catch missing or renamed register-field macros.
- Mechanically compare the header against the authoritative MMHUB 9.4.1 register database and verify that every `_MASK` is contiguous, aligned with its matching `__SHIFT`, and non-overlapping within a register.
- Cross-check this chunk with `mmhub_9_4_1_offset.h` so each covered register family has the expected `mmDAGB*` offset and base index.
- Inspect generated defaults in `mmhub_9_4_1_default.h` for covered counter/status/control registers, especially performance counter defaults and reserved register defaults.
- On MMHUB 9.4.1 hardware or simulator, run VM/GART initialization, memory traffic, SDMA traffic, compute, display, and reset/suspend/resume paths while checking for MMHUB faults, hangs, unexpected throttling, or broken snoop behavior.
- Read back `DAGB*_WRCLI_GPU_SNOOP_OVERRIDE` and `DAGB*_WRCLI_GPU_SNOOP_OVERRIDE_VALUE` after `mmhub_v9_4_init_snoop_override_regs()` and verify that SDMA client bit 15 is set in the intended DAGB instances for each hub.
- Exercise debug/performance paths that program `DAGB3_PERFCOUNTER*_CFG`, select results through `DAGB3_PERFCOUNTER_RSLT_CNTL`, read low/high counter words, and validate clear, trigger, and stop-on-saturate behavior.
- Under high traffic, sample pending, FIFO, and credit-full registers to confirm decoded bitmaps are plausible for active clients and do not show stuck busy/credit exhaustion after traffic drains.

## Chunk Notes For Merge Lane

This is a middle chunk of `mmhub_9_4_1_sh_mask.h`. It completes the visible tail of DAGB2 write controls, covers DAGB3 from read-client arbitration through reserved registers, and starts DAGB4 read controls through the first `DAGB4_RD_GMI_CNTL` shift. The merge lane should reconcile this with the previous chunk for complete DAGB2 coverage and with the next chunk for complete DAGB4 coverage before producing the final per-file research document.

### subset-b-002844: lines 7103-9460

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mmhub/mmhub_9_4_1_sh_mask.h lines 7103-9460

## Scope

This chunk covers lines 7103-9460 of the generated AMD MMHUB 9.4.1 shift/mask header. The range begins in the middle of the `DAGB4_RD_GMI_CNTL` register definition, continues through the rest of the `DAGB4` read/write DAGB register-field namespace, and then enters the `mmhub_ea_mmeadec0` address block for the first `MMEA0` EA/MMEA decoder register families. The last covered line is only the `//MMEA0_ADDRNORM_LIMIT_ADDR5` marker; its field definitions start after this chunk and belong to the next chunk.

The covered range contains 2,181 `#define` lines: 1,090 `__SHIFT` macros and 1,091 `_MASK` macros. The one-extra mask is an artifact of the chunk starting after the first `DAGB4_RD_GMI_CNTL` shift field. All definitions follow the generated AMDGPU convention:

- `<REGISTER>__<FIELD>__SHIFT` is the field's bit offset.
- `<REGISTER>__<FIELD>_MASK` is the 32-bit mask for extracting or composing that field.

This is hardware register metadata only. It declares no C functions, structs, enums, variables, storage, locks, includes, or executable paths. Although this repository path is under a `ceph-client` mirror, the file is AMDGPU MMHUB register ABI data, not Ceph or distributed-filesystem logic.

## Purpose

This header section supplies bitfield constants for programming and decoding MMHUB 9.4.1 registers from AMDGPU driver code. The companion `mmhub_9_4_1_offset.h` file provides the matching register offsets and base indices, while this file provides the masks and shifts consumed by helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `SOC15_REG_FIELD`, `RREG32_SOC15`, and `WREG32_SOC15`.

The covered `DAGB4` fields describe the fifth DAGB instance's read/write arbitration, bandwidth, virtual-channel, credit, pending-status, snoop-override, clock-gating, FIFO, reserved, and performance-counter registers. The covered `MMEA0` fields describe the first MMEA/EA decoder's DRAM and GMI client-to-group mapping, group-to-virtual-channel mapping, lazy timers, CAM controls, page burst limits, age/queue/fixed/urgency priority controls, GMI urgency masks, priority quantization thresholds, and the beginning of address-normalization ranges.

## Important Macro Families

### DAGB4 Read-Side Controls

The chunk starts with the tail of `DAGB4_RD_GMI_CNTL`. In this visible range, the register exposes `LEVEL`, `MAX_BURST`, and `LAZY_TIMER` shifts plus masks for `EA_CREDIT`, `LEVEL`, `MAX_BURST`, and `LAZY_TIMER`. The missing `EA_CREDIT__SHIFT` is just before the requested line range, so consumers need the whole generated header, not this chunk in isolation, for a complete register view.

The read-side DAGB fields then cover:

- `DAGB4_RD_ADDR_DAGB`: read address DAGB enable lanes, jump-ahead enable, self-init disable, and `WHOAMI`.
- `DAGB4_RD_OUTPUT_DAGB_MAX_BURST` and `DAGB4_RD_OUTPUT_DAGB_LAZY_TIMER`: 4-bit values for `VC0..VC7`, packing eight virtual-channel controls into one register.
- `DAGB4_RD_CGTT_CLK_CTRL`, `DAGB4_L1TLB_RD_CGTT_CLK_CTRL`, and `DAGB4_ATCVM_RD_CGTT_CLK_CTRL`: common clock-gating/light-sleep timing and override fields, including `ON_DELAY`, `OFF_HYSTERESIS`, `SOFT_STALL_OVERRIDE`, `LS_OVERRIDE`, and write/read/return/register override bits.
- `DAGB4_RD_ADDR_DAGB_MAX_BURST0..1` and `DAGB4_RD_ADDR_DAGB_LAZY_TIMER0..1`: 4-bit per-client fields for clients 0-15.
- `DAGB4_RD_VC0_CNTL` through `DAGB4_RD_VC7_CNTL`: per-VC storage credit, EA credit, max/min bandwidth enable and values, OSD limiter enable, and max OSD fields.
- `DAGB4_RD_CNTL_MISC`: storage-pool credit, ATOMIC/UTCL2 VCI control, read-return compression/legacy behavior, and compression-bypass fields.
- `DAGB4_RD_TLB_CREDIT`: separate 6-bit TLB credit fields for `VC0..VC5`.
- `DAGB4_RDCLI_*_PENDING`: packed pending client masks for ask, go, global-send, TLB, OARB, and OSD stages.

Together these fields describe the read path's traffic shaping and visibility for DAGB4: how requests are assigned to output VCs, how much burstiness/latency is tolerated, how credit checking is configured, and how in-flight work can be observed.

### DAGB4 Write Client And Write-Side Controls

The chunk defines `DAGB4_WRCLI0` through `DAGB4_WRCLI15`. Every write client has the same packed field layout:

- `VIRT_CHAN`, selecting the virtual channel.
- `CHECK_TLB_CREDIT`, enabling TLB-credit enforcement.
- `URG_HIGH` and `URG_LOW`, setting urgency thresholds.
- `MAX_BW_ENABLE` and `MAX_BW`, applying maximum bandwidth throttling.
- `MIN_BW_ENABLE` and `MIN_BW`, applying minimum bandwidth behavior.
- `OSD_LIMITER_ENABLE` and `MAX_OSD`, limiting outstanding operations.

The aggregate write-side controls mirror the read side but add write-specific address/data paths:

- `DAGB4_WR_CNTL`: SCLK frequency, client/VC bandwidth windows, IO level override, IO level, IO level compliance VC, and shared VC count.
- `DAGB4_WR_GMI_CNTL`: EA credit, level, max burst, and lazy timer for GMI write traffic.
- `DAGB4_WR_ADDR_DAGB` and `DAGB4_WR_DATA_DAGB`: enable, jump-ahead, self-init, and identity controls for write address and write data DAGB paths.
- `DAGB4_WR_OUTPUT_DAGB_MAX_BURST` and `DAGB4_WR_OUTPUT_DAGB_LAZY_TIMER`: per-output-VC write burst and timer controls.
- `DAGB4_WR_CGTT_CLK_CTRL`, `DAGB4_L1TLB_WR_CGTT_CLK_CTRL`, and `DAGB4_ATCVM_WR_CGTT_CLK_CTRL`: write-side clock-gating and light-sleep overrides.
- `DAGB4_WR_ADDR_DAGB_MAX_BURST0..1`, `DAGB4_WR_ADDR_DAGB_LAZY_TIMER0..1`, `DAGB4_WR_DATA_DAGB_MAX_BURST0..1`, and `DAGB4_WR_DATA_DAGB_LAZY_TIMER0..1`: per-client write address/data burst and lazy-timer controls for clients 0-15.
- `DAGB4_WR_VC0_CNTL` through `DAGB4_WR_VC7_CNTL`: per-VC credit, bandwidth, and OSD limit controls.
- `DAGB4_WR_CNTL_MISC`: storage-pool credit, HDP client ID, DCC compression bypass, DCC meta-data related behavior, and F32 bypass/routing fields.
- `DAGB4_WR_TLB_CREDIT`, `DAGB4_WR_DATA_CREDIT`, and `DAGB4_WR_MISC_CREDIT`: write-side TLB, data FIFO, return, atomic, and mixed credit budgets.

Write pending/status fields include the same ask/go/global-send/TLB/OARB/OSD stages as reads, plus DBUS ask/go status and GPU snoop override masks. `DAGB4_WRCLI_GPU_SNOOP_OVERRIDE` selects affected write clients and `DAGB4_WRCLI_GPU_SNOOP_OVERRIDE_VALUE` supplies the override value.

### DAGB4 Miscellaneous, FIFO, Reserve, And Performance Fields

The later `DAGB4` block defines control and observability fields:

- `DAGB4_DAGB_DLY`: delay selection values for soft-stall, CAM clear, and SDP-to-DAGB delay behavior.
- `DAGB4_CNTL_MISC`: bandwidth initialization, clock-cycle selection, LUT selection, fatal-edge mode, busy overrides, cycle count selection, swap mode, VC swap behavior, and read-return FIFO performance mode.
- `DAGB4_CNTL_MISC2`: DCC-capacity, DCC switch, L1 TLB read/write tap-chain disable, and address/data block-request disable fields.
- `DAGB4_FIFO_EMPTY`, `DAGB4_FIFO_FULL`, `DAGB4_WR_CREDITS_FULL`, and `DAGB4_RD_CREDITS_FULL`: compact full-width status masks.
- `DAGB4_PERFCOUNTER_LO`, `DAGB4_PERFCOUNTER_HI`, `DAGB4_PERFCOUNTER0_CFG`, `DAGB4_PERFCOUNTER1_CFG`, `DAGB4_PERFCOUNTER2_CFG`, and `DAGB4_PERFCOUNTER_RSLT_CNTL`: low/high result fields, high compare fields, event selection, clear, enable, mode, status, start/stop selection, and saturation controls.
- `DAGB4_RESERVE0` through `DAGB4_RESERVE13`: full-register reserved definitions.

These fields are integration points for diagnostics, performance collection, power management, and reset/hang analysis. They do not express the sequencing rules for sampling or clearing; they only name the bits.

### MMEA0 DRAM And GMI Client Mapping

At line 8430, the chunk enters `// addressBlock: mmhub_ea_mmeadec0`. The initial MMEA0 fields define traffic grouping and virtual-channel routing for DRAM and GMI paths:

- `MMEA0_DRAM_RD_CLI2GRP_MAP0..1` and `MMEA0_DRAM_WR_CLI2GRP_MAP0..1`: 2-bit client group assignments for client IDs `CID0..CID31`, split across two registers for read and write directions.
- `MMEA0_GMI_RD_CLI2GRP_MAP0..1` and `MMEA0_GMI_WR_CLI2GRP_MAP0..1`: the same 32-client mapping layout for GMI traffic.
- `MMEA0_DRAM_RD_GRP2VC_MAP`, `MMEA0_DRAM_WR_GRP2VC_MAP`, `MMEA0_GMI_RD_GRP2VC_MAP`, and `MMEA0_GMI_WR_GRP2VC_MAP`: 3-bit virtual-channel selections for groups 0-3.

This establishes a two-step routing model: client ID maps to a traffic group, then group maps to an MMHUB virtual channel. The read/write and DRAM/GMI namespaces are deliberately separate, so a client can be routed differently depending on direction and target fabric.

### MMEA0 Timing, CAM, Page Burst, And Priority Controls

The DRAM and GMI halves then expose parallel timing and arbitration controls:

- `*_RD_LAZY` and `*_WR_LAZY`: read/write lazy-timer settings for virtual channels `VC0..VC6`.
- `*_RD_CAM_CNTL` and `*_WR_CAM_CNTL`: per-group stop-counter enable bits, stop-counter value, and CAM allocation limits. GMI CAM control includes additional `GROUP0_SDP_HRT_ALLOC_LIMIT` and `GROUP0_SDP_NRT_ALLOC_LIMIT` fields that are not present in the DRAM CAM control layout in this chunk.
- `MMEA0_DRAM_PAGE_BURST` and `MMEA0_GMI_PAGE_BURST`: per-group page-burst controls.
- `*_RD_PRI_AGE` and `*_WR_PRI_AGE`: per-group age-coefficient and age-mode fields.
- `*_RD_PRI_QUEUING` and `*_WR_PRI_QUEUING`: per-group queuing-coefficient fields.
- `*_RD_PRI_FIXED` and `*_WR_PRI_FIXED`: fixed-priority values per group.
- `*_RD_PRI_URGENCY` and `*_WR_PRI_URGENCY`: per-group urgency coefficients and urgency-mode bits.
- `MMEA0_GMI_RD_PRI_URGENCY_MASKING` and `MMEA0_GMI_WR_PRI_URGENCY_MASKING`: one mask bit per `CID0..CID31`, allowing client-specific masking of GMI urgency behavior.
- `*_RD_PRI_QUANT_PRI1..3` and `*_WR_PRI_QUANT_PRI1..3`: per-group threshold registers for priority quantization.

These fields are the MMEA0 policy surface for arbitration. They determine how grouped client traffic ages, queues, asserts urgency, gets quantized into priorities, and consumes page/CAM resources.

### MMEA0 Address Normalization

The end of the chunk starts the MMEA0 address-normalization range:

- `MMEA0_ADDRNORM_BASE_ADDR0..5`: range-valid, legacy MMIO hole enable, channel/die/socket interleave counts, interleave address selection, and base-address fields.
- `MMEA0_ADDRNORM_LIMIT_ADDR0..4`: destination fabric ID and limit-address fields.
- `MMEA0_ADDRNORM_OFFSET_ADDR1` and `MMEA0_ADDRNORM_OFFSET_ADDR3`: high-address-offset enable and offset fields.

The chunk ends at the comment marker for `MMEA0_ADDRNORM_LIMIT_ADDR5`, before its shifts and masks. The final file-level report must merge this with the following chunk before treating address-normalization range 5 as complete.

## Control Flow

There is no runtime control flow in this header. The only "execution" is C preprocessor expansion. Driver code names a field through macros such as `REG_SET_FIELD(value, REGISTER, FIELD, field_value)` or `REG_GET_FIELD(reg_value, REGISTER, FIELD)`, and the preprocessor resolves that to the matching `REGISTER__FIELD__SHIFT` and `REGISTER__FIELD_MASK` constants.

Runtime sequencing belongs to the MMHUB/GMC/RAS/power-management code that includes this header. In this source tree, `drivers/gpu/drm/amd/amdgpu/mmhub_v9_4.c` includes `mmhub_9_4_1_offset.h`, `mmhub_9_4_1_sh_mask.h`, and `mmhub_9_4_1_default.h`. That file uses the same generated field convention when reading MMEA error status with `REG_GET_FIELD`, and its register-access paths use SOC15 offset/base helpers rather than hard-coded bit positions.

For the fields in this chunk, expected runtime control flow in consumers is:

- Program DAGB4 read/write QoS, VC, credit, snoop, and timer registers during ASIC initialization or power/reset restore.
- Poll DAGB4 pending/FIFO/credit status during quiesce, debugging, reset, or hang analysis.
- Configure or sample DAGB4 performance counters around diagnostic windows.
- Program MMEA0 group, VC, lazy, CAM, priority, urgency, quantization, and address-normalization registers as part of MMHUB fabric policy setup.
- Decode MMEA0-related status and error information elsewhere in the generated MMEA namespace.

This header does not define the order of those operations and does not state whether fields are read-only, write-one-to-clear, sticky, self-clearing, or reset-sensitive.

## State And Persistence Behavior

The file stores no software state. It describes MMIO-backed hardware state in the MMHUB 9.4.1 DAGB and MMEA blocks. Configuration state generally persists in the hardware register file until reset, power gating, firmware/driver reprogramming, or suspend/resume restore. Status, pending, FIFO, credit, and performance-counter state is maintained by hardware and can change asynchronously as traffic flows through the memory hub.

Important hardware state represented in this chunk includes:

- DAGB4 read/write virtual-channel selection, bandwidth windows, min/max bandwidth policy, urgency thresholds, outstanding-operation limits, TLB and data credits, burst limits, lazy timers, and storage/EA credits.
- DAGB4 clock-gating and light-sleep override state for read/write, L1TLB, and ATCVM paths.
- DAGB4 pending client masks, DBUS pending state, GPU snoop override selection/value, FIFO full/empty status, credit-full status, and performance-counter state.
- MMEA0 DRAM/GMI client-to-group and group-to-VC routing tables.
- MMEA0 lazy timers, CAM allocation/stop controls, page-burst limits, age/queue/fixed/urgency priority coefficients, urgency masking, quantization thresholds, and address-normalization base/limit/offset ranges.

Some fields are policy-like and should be restored after reset or power transitions; others are observation or command fields and should be read or written only under the hardware-defined sequence. The generated shift/mask macros do not encode those semantics.

## Dependencies And Integration Points

This chunk depends on AMD's generated MMHUB 9.4.1 register database and must stay synchronized with:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mmhub/mmhub_9_4_1_offset.h`, which supplies register offsets and base indices for these field names.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mmhub/mmhub_9_4_1_default.h`, which supplies generated default values for the same IP generation where present.
- AMDGPU SOC15 register helpers and register-field macros in the surrounding driver code.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/mmhub_v9_4.c`, which includes this header for MMHUB 9.4 programming and RAS/error-status handling.

Functional integration points include GPU VM hub setup, memory-client QoS, DRAM/GMI fabric routing, address normalization, clock-gating/light-sleep policy, reset and suspend/resume restore, RAS/error collection, performance-counter diagnostics, and virtualization-aware memory-hub attribution where client IDs or fabric IDs are involved.

The generated naming is ASIC-specific. Similar fields appear in other MMHUB versions, but code must include the mask/offset headers for the active IP block because register presence, index counts, and bit layouts can differ across generations.

## Risks And Edge Cases

- The chunk starts and ends on artificial boundaries. `DAGB4_RD_GMI_CNTL__EA_CREDIT__SHIFT` is outside this range, while `MMEA0_ADDRNORM_LIMIT_ADDR5` only appears as a marker here. Any final per-file summary must reconcile neighboring chunks.
- Bitfield drift is high impact. A wrong shift or mask can silently write unrelated MMHUB fields, causing memory-client starvation, broken virtual-channel routing, credit underflow, hangs, misreported status, or bad address normalization.
- Repeated register families are copy-sensitive. `DAGB4_WRCLI0..15`, VC controls, per-client burst/timer registers, and MMEA0 client/group maps use highly repetitive layouts; an index, direction, DRAM/GMI, read/write, or client-ID mismatch can affect one traffic class while leaving broad smoke tests apparently healthy.
- Read/write layouts are similar but not identical. DAGB write has separate address/data DAGB and write-data credit fields, while MMEA DRAM and GMI CAM controls diverge for some allocation-limit fields.
- Status and counter fields are side-effect-sensitive. Pending masks, FIFO/fullness state, credit state, performance-counter clear/enable/result controls, and hardware-maintained counters can change while being read.
- Clock-gating overrides can hide true idle/busy behavior. Misuse of `SOFT_STALL_OVERRIDE`, `LS_OVERRIDE`, and read/write/register override fields can interfere with power management or reset quiescing.
- MMEA0 priority knobs interact. Group mapping, VC mapping, age, queuing, fixed priority, urgency mode, urgency masking, quantization, lazy timers, page burst, and CAM allocation should be tuned coherently; isolated changes can starve clients or over-prioritize traffic.
- Address-normalization fields are fabric-critical. Incorrect base/limit, interleave, legacy MMIO hole, destination fabric ID, or high-offset values can route memory transactions to the wrong fabric target or range.
- Some names are broad status masks rather than per-field semantic values. Full-width reserve/status definitions should not be treated as stable programmable policy unless hardware documentation says so.

## Test Signals

Useful validation for this chunk is mostly generated-header consistency plus hardware behavior:

- Build AMDGPU with MMHUB 9.4.1 support enabled; missing, renamed, or malformed macros should surface as compile failures in MMHUB users.
- Mechanically verify that every visible `_MASK` aligns with its matching `__SHIFT` and field width, allowing for the deliberate chunk-boundary exception at the first register.
- Cross-check the covered register names against `mmhub_9_4_1_offset.h` so each field-bearing register has a matching offset/base-index definition.
- Compare the header with AMD's authoritative generated register database for MMHUB 9.4.1; hand edits to generated masks should be treated as suspect.
- Exercise GPU VM and memory traffic across graphics, compute, SDMA, display, DRAM-local, and GMI/peer traffic while watching for hangs, VM faults, RAS errors, bandwidth starvation, and unexpected throttling.
- Test reset, suspend/resume, and clock-gating paths that restore or depend on DAGB4 and MMEA0 policy registers.
- Validate DAGB4 performance counters by selecting events, enabling/clearing counters, reading low/high results, testing start/stop selection, and checking saturation behavior.
- During diagnostics or fault injection, inspect DAGB4 pending/FIFO/credit status and MMEA0 routing/priority state for plausible values under known traffic patterns.
- For multi-die or fabric-heavy configurations, validate MMEA0 address-normalization ranges and `DST_FABRIC_ID` handling with peer/GMI traffic and large BAR/fabric-memory layouts.

## Cross-Chunk Notes

Earlier chunks of this same file cover the beginning of `mmhub_9_4_1_sh_mask.h` and the earlier DAGB instances. This chunk specifically covers the remainder of `DAGB4` after `DAGB4_RD_GMI_CNTL` has already begun, then starts `MMEA0`. Later chunks must complete `MMEA0_ADDRNORM_LIMIT_ADDR5` and the rest of the MMEA0/MMHUB 9.4.1 namespace before any final per-file document makes complete claims about the generated header.

### subset-b-002845: lines 9461-11822

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mmhub/mmhub_9_4_1_sh_mask.h lines 9461-11822

## Scope

This chunk is a generated AMDGPU MMHUB 9.4.1 shift/mask header slice. It contains only C preprocessor constants: no functions, structs, enums, local variables, allocations, locks, callbacks, or executable branches. The slice has 2,362 source lines and 2,171 `#define` entries: 1,087 `__SHIFT` constants and 1,184 `_MASK` constants.

The range starts at the complete `MMEA0_ADDRNORM_LIMIT_ADDR5` field definitions and ends inside `MMEA1_DRAM_WR_PRI_QUANT_PRI1` after `GROUP0_THRESHOLD_MASK`; the remaining masks for that write-priority quantum register continue in the next chunk. The previous chunk contains the immediately preceding `MMEA0_ADDRNORM_BASE_ADDR5` register.

Major covered areas are:

- `MMEA0` address normalization and address-decode programming for address range 5, DRAM/GMI holes, non-power-of-two channel spacing, bank/misc masks, DRAM and GMI address hashing, harvest override bits, and three address-decode tables.
- `MMEA0` IO arbitration controls: client-to-group maps, group-to-virtual-channel maps, lazy/flush behavior, CAM depth and reorder limits, burst limits, priority aging/queuing/fixed/urgency/quantum controls, and urgency masking.
- `MMEA0` SDP request/response arbitration, priority, credit reservation, request policy, misc link-manager behavior, latency sampling, and performance counters.
- `MMEA0` RAS/EDC and diagnostic controls: EDC count registers, DSM/single-write/error-injection controls, clock control, EDC mode, error status, misc2, address-decode channel select, and late `EDC_CNT3` DED counters.
- Beginning of `addressBlock: mmhub_ea_mmeadec1`, covering the first `MMEA1` DRAM read/write arbitration controls through the first mask of `MMEA1_DRAM_WR_PRI_QUANT_PRI1`.

Although the repository path is under `sources/distributed-fs/ceph-client`, this header is AMD GPU MMIO metadata, not Ceph or distributed-filesystem logic.

## Purpose

The purpose of this slice is to publish the bit-level ABI for MMHUB 9.4.1 memory endpoint/address-decode registers. Each hardware register field follows the generated AMD convention:

- `<REGISTER>__<FIELD>__SHIFT`: bit offset for composing or extracting the field value.
- `<REGISTER>__<FIELD>_MASK`: 32-bit mask for isolating or updating the field.

The matching `mmhub_9_4_1_offset.h` file supplies register addresses such as `mmMMEA0_ADDRNORM_LIMIT_ADDR5`, `mmMMEA0_EDC_CNT`, `mmMMEA0_ERR_STATUS`, and `mmMMEA1_DRAM_RD_CLI2GRP_MAP0`. This header supplies the masks and shifts consumed by SOC15 helpers such as `SOC15_REG_FIELD`, `SOC15_REG_ENTRY`, `REG_GET_FIELD`, `REG_SET_FIELD`, `RREG32`, and `RREG32_SOC15`.

Operationally, these constants describe how the MMHUB endpoint address logic maps normalized addresses to DRAM/GMI fabric resources and how MMHUB traffic is grouped, prioritized, credited, sampled, and diagnosed. The chunk is especially important for RAS reporting in `amdgpu/mmhub_v9_4.c`, where the `MMEA*_EDC_CNT*` and `MMEA*_ERR_STATUS` fields are decoded into correctable/uncorrectable error counts and status warnings.

## Important APIs, Types, And Macros

There are no callable APIs or C types in this range. The public interface is the macro namespace.

Important macro groups include:

- Address normalization: `MMEA0_ADDRNORM_LIMIT_ADDR5`, `MMEA0_ADDRNORM_OFFSET_ADDR5`, `MMEA0_ADDRNORMDRAM_HOLE_CNTL`, `MMEA0_ADDRNORMGMI_HOLE_CNTL`, `MMEA0_ADDRNORMDRAM_NP2_CHANNEL_CFG`, `MMEA0_ADDRNORMGMI_NP2_CHANNEL_CFG`, and the DRAM/GMI global hash controls.
- Address-decode steering: `MMEA0_ADDRDEC_BANK_CFG`, `MMEA0_ADDRDEC_MISC_CFG`, DRAM/GMI hash-bank registers, hash program-counter/chip-select registers, and `MMEA0_ADDRDECDRAM_HARVEST_ENABLE` / `MMEA0_ADDRDECGMI_HARVEST_ENABLE`.
- Address-decode tables: repeated `MMEA0_ADDRDEC0_*`, `MMEA0_ADDRDEC1_*`, and `MMEA0_ADDRDEC2_*` groups. Each table covers chip-select base addresses for CS0-CS3 and SECCS0-SECCS3, CS pair masks, row/column/bank geometry, bank/row selectors, high/low column selectors, row-mask selectors, secondary CS row-mask selectors, channel-bit selection, and row-MSB inversion bits.
- IO arbitration and priority: `MMEA0_IO_RD_CLI2GRP_MAP*`, `MMEA0_IO_WR_CLI2GRP_MAP*`, `MMEA0_IO_RD_COMBINE_FLUSH`, `MMEA0_IO_WR_COMBINE_FLUSH`, `MMEA0_IO_GROUP_BURST`, `MMEA0_IO_RD_PRI_*`, `MMEA0_IO_WR_PRI_*`, and read/write urgency masking registers.
- SDP control: `MMEA0_SDP_ARB_DRAM`, `MMEA0_SDP_ARB_GMI`, `MMEA0_SDP_ARB_FINAL`, `MMEA0_SDP_DRAM_PRIORITY`, `MMEA0_SDP_GMI_PRIORITY`, `MMEA0_SDP_IO_PRIORITY`, `MMEA0_SDP_CREDITS`, tag/VCC/VCD reserve registers, and `MMEA0_SDP_REQ_CNTL`.
- Diagnostic and performance surfaces: `MMEA0_LATENCY_SAMPLING`, `MMEA0_PERFCOUNTER_LO`, `MMEA0_PERFCOUNTER_HI`, `MMEA0_PERFCOUNTER0_CFG`, `MMEA0_PERFCOUNTER1_CFG`, and `MMEA0_PERFCOUNTER_RSLT_CNTL`.
- RAS/EDC registers: `MMEA0_EDC_CNT`, `MMEA0_EDC_CNT2`, and `MMEA0_EDC_CNT3` count SEC/DED/SED events for DRAM read/write command memories, data memories, return tag memories, IO command/data memories, GMI command/data/page memories, and MAM D0-D3 memories.
- Error injection and EDC mode: `MMEA0_DSM_CNTL`, `MMEA0_DSM_CNTLA`, `MMEA0_DSM_CNTL2`, `MMEA0_DSM_CNTL2A`, `MMEA0_EDC_MODE`, and `MMEA0_ERR_STATUS`.
- Clock and misc controls: `MMEA0_CGTT_CLK_CTRL`, `MMEA0_MISC`, `MMEA0_MISC2`, and `MMEA0_ADDRDEC_SELECT`.
- Beginning of MMEA1 DRAM arbitration: `MMEA1_DRAM_RD_CLI2GRP_MAP*`, `MMEA1_DRAM_WR_CLI2GRP_MAP*`, `MMEA1_DRAM_RD_GRP2VC_MAP`, `MMEA1_DRAM_WR_GRP2VC_MAP`, lazy controls, CAM controls, page-burst limits, priority age/queue/fixed/urgency controls, read quantum threshold registers, and the first field mask of `MMEA1_DRAM_WR_PRI_QUANT_PRI1`.

## Control Flow

This header chunk has no runtime control flow. Runtime behavior is supplied by code that includes this generated header, primarily `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/mmhub_v9_4.c`.

Observed control-flow integration in this tree:

1. `mmhub_v9_4.c` includes `mmhub/mmhub_9_4_1_offset.h` and `mmhub/mmhub_9_4_1_sh_mask.h`, binding the register address namespace to the field shift/mask namespace.
2. Static RAS field tables use `SOC15_REG_ENTRY(MMHUB, 0, mmMMEA0_EDC_CNT)` and `SOC15_REG_FIELD(MMEA0_EDC_CNT, ...)` style initializers. The `SOC15_REG_FIELD` entries resolve to the shift/mask constants defined in this header.
3. `mmhub_v9_4_query_ras_error_count()` iterates `mmhub_v9_4_edc_cnt_regs`, reads each EDC register with `RREG32(SOC15_REG_ENTRY_OFFSET(...))`, and passes nonzero values to `mmhub_v9_4_get_ras_error_count()`.
4. `mmhub_v9_4_get_ras_error_count()` scans the static field table for matching register offsets, extracts SEC and DED counts with `(value & mask) >> shift`, logs nonzero subblock counts, and accumulates CE/UE totals.
5. `mmhub_v9_4_reset_ras_error_count()` reads each EDC count register to reset counters when MMHUB RAS is supported. The read-to-reset behavior is driver-commented in `mmhub_v9_4.c`, not encoded by the macros.
6. `mmhub_v9_4_query_ras_error_status()` reads each `MMEA*_ERR_STATUS` register and uses `REG_GET_FIELD(..., MMEA0_ERR_STATUS, SDP_RDRSP_STATUS)`, `SDP_WRRSP_STATUS`, and `SDP_RDRSP_DATAPARITY_ERROR` to warn before GPU reset when SDP response/parity conditions are present.

Most address-decode, arbitration, performance, DSM, and clock-control fields in this chunk are not actively programmed by the nearby Linux driver code found in this tree. They remain part of the generated register ABI for firmware, platform initialization, debug tooling, validation, or future driver paths.

## State And Persistence Behavior

The header itself stores no software state and persists nothing. It describes MMIO-backed hardware state in the MMHUB endpoint/address-decode path.

Hardware state represented by this chunk includes:

- Address normalization state: range limit/fabric destination, high-address offset enable/value, DRAM/GMI hole validity and offset, non-power-of-two 64K channel spacing, and global hash interleave control for 64K/2M/1G granularities.
- Address-decode state: bank masks, bank-group selection/interleave, pseudo-channel/channel/chip-select/rank-mask fields, DRAM/GMI hash XOR enables and XOR source bits, harvested bank force enables/values, and three complete address-decoder tables with CS enable/base/mask/geometry/selector fields.
- Arbitration state: client-to-group assignment for 32 client IDs, group-to-VC assignment, lazy request accumulation delays and thresholds, reorder CAM depth/limits, page-burst limits, age/queue/fixed/urgency priority coefficients, urgency modes, priority quantum thresholds, and urgency masking against response/credit/full/urgency sources.
- SDP state: DRAM/GMI/final arbitration burst limits, early switch behavior, priority selection, group credits, tag and virtual-channel credit reservations, request pass/chain override policy, and inner-domain mode.
- Diagnostic state: latency sampler selectors, performance-counter event selection, result selection, trigger/clear/stop-on-saturate bits, and 48-bit counter payload split across LO and HI/compare fields.
- RAS/EDC state: SEC/DED/SED counters for multiple MMHUB memories, DSM irritator/single-write controls, error-injection enables and delay selection, EDC mode controls, and fatal/error status fields.
- Power/clock state: CGTT on-delay/off-hysteresis, stall/soft overrides, light-sleep override, and misc traffic/link-manager arbitration bits.
- Multi-instance state: `MMEA0` registers represent range/endpoint instance 0, and the chunk starts the structurally similar `MMEA1` DRAM arbitration programming for range/endpoint instance 1.

Persistence and side effects are hardware-defined. Configuration fields generally persist until reset, power-gating loss, firmware/driver reinitialization, or explicit MMIO writes. EDC counters and error status fields are stateful status surfaces; the driver comments that reading EDC count registers resets those counters. Error-injection, clear-status, performance-counter clear, and request/override fields may have immediate side effects and must be sequenced by hardware-specific code rather than treated as passive data.

## Dependencies And Integration Points

Direct dependencies:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mmhub/mmhub_9_4_1_offset.h` provides the matching register offsets and base indices. For example, this chunk's fields pair with offsets including `mmMMEA0_ADDRNORM_LIMIT_ADDR5`, `mmMMEA0_EDC_CNT`, `mmMMEA0_EDC_CNT2`, `mmMMEA0_EDC_CNT3`, `mmMMEA0_ERR_STATUS`, `mmMMEA1_DRAM_RD_CLI2GRP_MAP0`, and `mmMMEA1_DRAM_WR_PRI_QUANT_PRI1`.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/mmhub_v9_4.c` includes this header and uses its field names through SOC15 helper macros.
- Common AMDGPU/SOC15 register helpers provide `SOC15_REG_ENTRY`, `SOC15_REG_FIELD`, `SOC15_REG_ENTRY_OFFSET`, `REG_GET_FIELD`, `RREG32`, and related MMIO access abstractions.

Observed integration points:

- The `mmhub_v9_4_ras_fields` table decodes `MMEA0_EDC_CNT`, `MMEA0_EDC_CNT2`, and `MMEA0_EDC_CNT3` fields from this chunk for MMHUB range 0. It also decodes later `MMEA1`-`MMEA7` EDC count registers using the same generated naming pattern outside this slice.
- `mmhub_v9_4_edc_cnt_regs` enumerates `mmMMEA0_EDC_CNT`, `mmMMEA0_EDC_CNT2`, and `mmMMEA0_EDC_CNT3` from the paired offset header so RAS query/reset code can read every MMHUB endpoint's EDC counters.
- `mmhub_v9_4_query_ras_error_status()` uses `MMEA0_ERR_STATUS` fields as the decoding template while iterating over `MMEA0_ERR_STATUS` through `MMEA7_ERR_STATUS`; this relies on identical field layout across the endpoint instances.
- Firmware or low-level initialization code outside the observed Linux source may program address-decode and arbitration fields. These tables define fabric/channel/bank/chip-select mapping and traffic arbitration, so they integrate with memory topology, XGMI/GMI routing, RAS validation, and performance tuning.
- Performance/debug tooling can use `MMEA0_PERFCOUNTER*` and `MMEA0_LATENCY_SAMPLING` fields to select events, clear counters, enable counting, trigger start/stop, and read LO/HI counter values.

## Risks And Edge Cases

- Bitfield drift is high impact. A wrong shift or mask can silently decode the wrong error count, program the wrong address-decode selector, or change arbitration/credit behavior.
- The chunk ends mid-register. `MMEA1_DRAM_WR_PRI_QUANT_PRI1` is incomplete here: only shifts and `GROUP0_THRESHOLD_MASK` are in this slice, while the remaining masks continue after line 11822. The merge lane must reconcile adjacent chunks before making complete file-level claims for that register.
- Address-decode fields are topology-critical. Incorrect base/mask/CS enable, bank/row/column selector, channel bit, or row-MSB inversion fields can misroute memory accesses, alias addresses, or break DRAM/GMI interleave assumptions.
- Hashing and harvest override fields are sensitive. Changing XOR source fields or forced bank-enable/value fields can alter address distribution or collide with physical fuse/harvest state.
- Repeated decoder tables invite copy/stride mistakes. `ADDRDEC0`, `ADDRDEC1`, and `ADDRDEC2` use near-identical layouts, so consumers must match the correct register offset with the correct instance and CS pair.
- Arbitration fields can affect correctness under load as well as performance. Bad CAM depth, reorder limits, lazy thresholds, burst limits, urgency coefficients, or credit reservations can cause starvation, response stalls, or hard-to-reproduce hangs.
- RAS counter extraction depends on exact count widths. The `MMEA0_EDC_CNT*` fields are packed two-bit counters in many places; an incorrect mask/shift can report false CE/UE totals or miss real errors before reset.
- EDC counter reset is side-effectful. `mmhub_v9_4_reset_ras_error_count()` relies on readback to clear counters, so extra reads from debug paths may change later RAS accounting.
- Error-injection and DSM controls should not be used accidentally. Fields such as `ENABLE_ERROR_INJECT`, `SELECT_INJECT_DELAY`, and DSM irritator/single-write controls are validation-oriented and can intentionally perturb hardware behavior.
- `MMEA0_ERR_STATUS__CLEAR_ERROR_STATUS_MASK` and other clear/status bits are not self-describing from the macro names alone. Consumers need hardware sequencing rules to avoid losing status or leaving fatal conditions uncleared.
- Cross-instance decoding assumes identical layouts. `mmhub_v9_4_query_ras_error_status()` uses `MMEA0_ERR_STATUS` field names while iterating status registers for all instances; this is valid only while all `MMEA*` status registers retain identical bit positions.

## Test Signals

Useful validation signals for this chunk are generated-header consistency, build coverage, and RAS/arbitration behavior:

- Build AMDGPU with MMHUB 9.4 support enabled. Compile-time failures in `mmhub_v9_4.c` would catch missing or renamed macros used by `SOC15_REG_FIELD` and `REG_GET_FIELD`.
- Compare this slice against AMD's authoritative MMHUB 9.4.1 register database and the paired `mmhub_9_4_1_offset.h`; every field name must align with the intended register offset and bit layout.
- Run MMHUB RAS query paths with known injected or simulated EDC values. `mmhub_v9_4_get_ras_error_count()` should report the expected SEC/DED counts for `MMEA0_EDC_CNT`, `MMEA0_EDC_CNT2`, and `MMEA0_EDC_CNT3`.
- Verify read-to-clear behavior for EDC counters on supported hardware: after `mmhub_v9_4_reset_ras_error_count()`, subsequent RAS queries should not re-report the same counts.
- Exercise `MMEA*_ERR_STATUS` handling by provoking or injecting SDP read/write response and read-data parity status. The driver should log the expected MMHUB EA status before reset handling.
- Validate address-decode programming through firmware/platform tests: DRAM/GMI interleaving, hole handling, non-power-of-two channel mapping, chip-select routing, and harvested-bank behavior should match memory topology tables.
- Stress mixed read/write/atomic traffic across IO, DRAM, and GMI paths to expose arbitration regressions from client grouping, urgency, lazy/CAM, page-burst, or credit-reservation fields.
- Use performance-counter tooling to select events, enable/clear counters, trigger start/stop, read LO/HI values, and confirm stop-on-saturate or compare behavior.
- Run suspend/resume and power-gating tests where CGTT and clock/LS override state may be reinitialized or lost.

## Cross-Chunk Notes

The previous chunk owns the immediately preceding `MMEA0_ADDRNORM_BASE_ADDR5` register. This chunk owns the complete `MMEA0_ADDRNORM_LIMIT_ADDR5` through `MMEA1_DRAM_WR_PRI_QUANT_PRI1__GROUP0_THRESHOLD_MASK` range. The next chunk must add the remaining `MMEA1_DRAM_WR_PRI_QUANT_PRI1` masks and subsequent MMEA1 registers before the final per-file report describes the full `MMEA1` DRAM priority quantum register set.

### subset-b-002846: lines 11823-14186

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mmhub/mmhub_9_4_1_sh_mask.h lines 11823-14186

## Purpose

This chunk is part of the generated AMDGPU MMHUB 9.4.1 shift/mask register header. It does not define executable logic, functions, or C types. Instead, it publishes preprocessor constants that describe 32-bit bitfield layouts for MMEA1 registers in the second MMHUB/MMEA instance: GMI arbitration, address normalization and address decoding, IO arbitration, SDP request/credit handling, misc arbitration behavior, latency sampling, and the beginning of MMEA1 performance counter configuration.

Each register field appears as a pair of macros:

- `REG__FIELD__SHIFT`, the low bit position.
- `REG__FIELD_MASK`, the bit mask to isolate or set the field.

The companion files provide the other parts of the contract: `mmhub_9_4_1_offset.h` maps these symbolic register names to MMIO offsets and base indices, while `mmhub_9_4_1_default.h` supplies reset/default values. `amdgpu/mmhub_v9_4.c` includes all three headers for MMHUB v9.4 support.

## Important Register Groups

The opening lines complete the MMEA1 DRAM write priority quantum definitions, then the chunk switches to GMI fields. The GMI client-to-group maps (`MMEA1_GMI_RD_CLI2GRP_MAP0/1`, `MMEA1_GMI_WR_CLI2GRP_MAP0/1`) pack 32 client IDs into two registers using 2-bit group fields. The group-to-virtual-channel maps (`MMEA1_GMI_RD_GRP2VC_MAP`, `MMEA1_GMI_WR_GRP2VC_MAP`) assign four arbitration groups to 3-bit virtual channel values.

GMI throttling and arbitration fields include lazy-delay registers, CAM controls, page burst limits, and read/write priority coefficient sets for age, queuing, fixed priority, urgency, urgency masking, and three quantum threshold registers. The pattern is mirrored for read and write paths. Urgency masking uses one bit per client ID across all 32 IDs, while coefficient registers use compact 3-bit per-group fields and quantum registers use 8-bit thresholds for four groups.

The address normalization section describes `MMEA1_ADDRNORM_BASE_ADDR0..5`, matching limit registers, and high-address offset registers for selected ranges. These fields define range validity, legacy MMIO hole enable, channel/die/socket interleave geometry, interleave address selection, base address, destination fabric ID, limit address, and optional high address offsets. Hole control and NP2 channel config fields appear for both DRAM and GMI paths.

Address decoder definitions cover bank and misc config, DRAM/GMI hash controls, harvest controls, and repeated decoder blocks `MMEA1_ADDRDEC0`, `MMEA1_ADDRDEC1`, and `MMEA1_ADDRDEC2`. Each decoder block contains base-address registers for primary CS0-CS3 and secondary CS0-CS3, address masks for CS pairs, address geometry config fields, bank/row selectors, extended bank selectors, column low/high selectors, and RM/channel row-selection controls. These macros encode how physical addresses are split into memory-controller dimensions.

The IO section mirrors the GMI arbitration structure for IO clients: read/write client-to-group maps, combine flush timers, group burst limits, age/queuing/fixed/urgency coefficients, urgency masks, and quantum thresholds. IO default values in the companion default header differ from GMI, so code must pair these masks with the correct `MMEA1_IO_*` register names rather than assuming identical policy values.

The SDP section defines arbitration and credit fields for traffic leaving the MMHUB path. `MMEA1_SDP_ARB_DRAM`, `MMEA1_SDP_ARB_GMI`, and `MMEA1_SDP_ARB_FINAL` expose burst-limit and switching behavior. Priority fields distinguish DRAM, GMI, and IO priority control. Credit and reserve registers define tag limits, read/write response credits, per-VC tag reserves, and VCC/VCD credit reserves, including `DISTRIBUTE_POOL` bits. `MMEA1_SDP_REQ_CNTL` controls request pass/chain overrides and inner-domain mode.

The tail contains global knobs and observability definitions. `MMEA1_MISC` includes relative-priority toggles for DRAM/GMI/IO read/write arbiters, early write return enable bits per VC, link manager mode/threshold/delay fields, and chip-select arbitration preferences. `MMEA1_LATENCY_SAMPLING` selects two samplers across DRAM/GMI/IO, read/write/atomic classes, and VC fields. `MMEA1_PERFCOUNTER_LO`, `MMEA1_PERFCOUNTER_HI`, and the start of `MMEA1_PERFCOUNTER0_CFG`/`1_CFG` define performance counter data, compare, event select, mode, enable, and clear fields.

## Control Flow and State

There is no runtime control flow in this chunk. The state represented here is hardware state in MMIO registers, accessed elsewhere through AMDGPU register read/write helpers such as `RREG32_SOC15`, `WREG32_SOC15`, and related macros. The header only supplies compile-time constants used to build masks, shifts, and register field values.

Persistence is hardware-defined. Register contents persist according to GPU reset, power-gating, suspend/resume, firmware, and driver initialization behavior, not according to this header. The default reset contract is externalized in `mmhub_9_4_1_default.h`; for example, this chunk's address decoder and SDP fields have matching `mmMMEA1_*_DEFAULT` constants there.

## Dependencies and Integration Points

This file depends only on the C preprocessor. It is guarded by `_mmhub_9_4_1_SH_MASK_HEADER` at file scope and is included by MMHUB v9.4 driver code along with:

- `mmhub/mmhub_9_4_1_offset.h` for register addresses and base indices.
- `mmhub/mmhub_9_4_1_default.h` for reset/default register values.
- SOC15 register access infrastructure in the AMDGPU driver.

The macros in this chunk are useful only when paired with the matching MMHUB 9.4.1 register offsets. The `MMEA1_*` offsets in `mmhub_9_4_1_offset.h` use base index `1` for this instance, so consumers must preserve instance/base-index selection when reading or writing fields.

## Risks

The main risk is silent hardware misprogramming from stale or mismatched generated constants. Adjacent MMHUB generations expose similarly named fields with different bit positions or masks; for example, address normalization interleave fields and SDP request control fields differ across sibling headers. Accidentally mixing `mmhub_9_4_1_sh_mask.h` with a different generation's offset/default header can compile cleanly but write the wrong bits.

Because most fields are dense packed bitfields, incorrect shift/mask use can corrupt neighboring fields in the same register. This is especially risky for address decoder and address normalization registers because bad base, limit, mask, hash, or selector fields can redirect or alias memory traffic. Arbitration and credit fields can also create performance regressions, starvation, deadlock-like stalls, or incorrect QoS behavior if programmed outside hardware expectations.

The chunk is generated-looking and repetitive, so hand edits are risky. Any manual change should be treated as a hardware contract change and checked against the ASIC register source, the offset header, default header, and any firmware programming tables.

## Test Signals

Useful validation is mostly integration and hardware-facing:

- Build coverage for `amdgpu/mmhub_v9_4.c` and any MMHUB 9.4.1 users verifies that macro names remain available and do not collide.
- Register read/write smoke tests on MMHUB 9.4.1 hardware can confirm that fields are programmed through the expected offsets and base index.
- Suspend/resume, GPU reset, GART setup, VM context setup, and multi-MMHUB instance tests are relevant because they exercise MMHUB register programming around persisted hardware state.
- Memory stress, page fault handling, peer/GMI traffic, IO traffic, and performance counter sampling are behavioral signals for the address normalization, decoder, arbitration, SDP, latency, and perf-counter fields defined here.
- Static comparison against generated ASIC register sources, plus consistency checks between `_offset.h`, `_sh_mask.h`, and `_default.h`, is the best low-level guard against drift.

## Chunk Boundary Notes

This chunk starts mid-register at the final mask entries for `MMEA1_DRAM_WR_PRI_QUANT_PRI1` and ends after `MMEA1_PERFCOUNTER1_CFG__ENABLE__SHIFT`, before the remaining fields for `MMEA1_PERFCOUNTER1_CFG` and subsequent MMEA1 registers. Whole-file reconciliation should merge this with neighboring chunks to describe the complete MMHUB 9.4.1 register surface.

### subset-b-002847: lines 14187-16550

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mmhub/mmhub_9_4_1_sh_mask.h lines 14187-16550

## Scope

This chunk is a generated AMDGPU MMHUB 9.4.1 shift/mask header slice. It contains C preprocessor constants only: no functions, structs, enums, storage, allocations, locks, loops, or executable branches. The range starts inside `MMEA1_PERFCOUNTER1_CFG` after its field shifts were emitted in the previous chunk, then covers the end of the `mmhub_ea_mmeadec1` block and most of the `mmhub_ea_mmeadec2` block. It ends inside `MMEA2_IO_WR_CLI2GRP_MAP1` after `CID30_GROUP_MASK`; the `CID31_GROUP_MASK` definition and later MMEA2 registers continue in the next chunk.

Within those boundaries the slice defines bit offsets and masks for these major areas:

- MMEA1 performance-counter result control, EDC/RAS counters, DSM error-injection controls, clock-gating controls, EDC mode, error status, miscellaneous arbitration controls, address-decoder channel selection, and extra DED counters.
- `addressBlock: mmhub_ea_mmeadec2`, covering MMEA2 DRAM/GMI read and write client-to-group maps, group-to-virtual-channel maps, lazy request accumulation, CAM/reorder controls, page-burst limits, priority aging/queuing/fixed/urgency coefficients, GMI urgency client masks, and priority quantum thresholds.
- MMEA2 address normalization ranges 0-5, limit and offset registers, DRAM/GMI hole controls, non-power-of-two channel configuration, address-decoder bank and misc configuration, DRAM/GMI hash controls, harvest-enable controls, and repeated channel/chip-select address-decoder tables for decoders 0, 1, and 2.
- MMEA2 DRAM/GMI global address-normalization hash controls and the start of MMEA2 IO read/write client grouping.

Although this path lives under `sources/distributed-fs/ceph-client`, this file is AMD GPU MMIO register metadata, not distributed-filesystem logic.

## Purpose

The purpose of this chunk is to publish the bit-level ABI for MMHUB 9.4.1 MMEA register programming. Each generated definition follows the AMD register-header convention:

- `<REGISTER>__<FIELD>__SHIFT`: the bit position of a field.
- `<REGISTER>__<FIELD>_MASK`: the 32-bit mask for isolating or composing that field.

The matching `mmhub_9_4_1_offset.h` header supplies register addresses such as `mmMMEA1_EDC_CNT`, `mmMMEA1_EDC_CNT2`, `mmMMEA1_EDC_CNT3`, `mmMMEA1_ERR_STATUS`, and the MMEA2 address-decoder and arbitration registers. This header supplies the field masks used by helper macros such as `SOC15_REG_FIELD`, `REG_GET_FIELD`, `REG_SET_FIELD`, `SOC15_REG_ENTRY`, `RREG32`, `RREG32_SOC15`, `RREG32_SOC15_OFFSET`, `WREG32_SOC15`, and `WREG32_SOC15_OFFSET`.

Operationally, the covered registers describe the MMHUB external-address/memory-fabric path for the second and third MMEA ranges: request grouping and virtual-channel selection, read/write arbitration behavior, address normalization and interleave geometry, bank/rank/column address decoding, DRAM/GMI hash selection, harvested-bank overrides, clock-gating behavior, performance counters, and RAS/ECC/error-injection surfaces.

## Important APIs, Types, And Macros

There are no callable APIs or C types in this range. The public interface is the generated macro namespace consumed by AMDGPU MMHUB code and by generated/default register-setting tables.

Important macro groups include:

- `MMEA1_PERFCOUNTER1_CFG` tail and `MMEA1_PERFCOUNTER_RSLT_CNTL`: event selection, event-range end, mode, enable/clear, result-counter select, start/stop triggers, clear-all, enable-any, and stop-on-saturate fields for MMEA1 performance measurement.
- `MMEA1_EDC_CNT`, `MMEA1_EDC_CNT2`, and `MMEA1_EDC_CNT3`: SEC/DED/SED counter fields for DRAM read command memory, DRAM write command/data/page memory, GMI read/write command/data/page memory, IO read/write command/data memory, return tag memories, and MAM D0-D3 memories.
- `MMEA1_DSM_CNTL`, `MMEA1_DSM_CNTLA`, `MMEA1_DSM_CNTL2`, and `MMEA1_DSM_CNTL2A`: diagnostic/scrub/error-injection controls. These select irritator data, single-write behavior, enable-error-inject values, per-memory inject-delay selection, and a common inject-delay field.
- `MMEA1_CGTT_CLK_CTRL`: clock-gating timing and overrides, including on delay, off hysteresis, spare fields, soft stall override for write/read/return, light-sleep override, and write/read/return/register soft overrides.
- `MMEA1_EDC_MODE`, `MMEA1_ERR_STATUS`, `MMEA1_MISC2`, and `MMEA1_ADDRDEC_SELECT`: EDC policy bits, response/error status bits, clear-error/busy-on-error/FUE status, arbitration swap and burst-limit controls, IO read/write priority enable, return swap mode, and DRAM/GMI decoder channel start/end selectors.
- `MMEA2_DRAM_*` and `MMEA2_GMI_*` arbitration registers: `*_CLI2GRP_MAP0/1` map client IDs 0-31 into four traffic groups; `*_GRP2VC_MAP` maps groups to virtual channels; `*_LAZY` controls per-group delay and request accumulation thresholds/timeouts; `*_CAM_CNTL` controls group CAM depth, reorder limits, and refill-chain behavior; `*_PAGE_BURST`, `*_PRI_AGE`, `*_PRI_QUEUING`, `*_PRI_FIXED`, `*_PRI_URGENCY`, `*_PRI_URGENCY_MASKING`, and `*_PRI_QUANT_PRI*` define arbitration policy.
- `MMEA2_ADDRNORM_BASE_ADDR0` through `MMEA2_ADDRNORM_BASE_ADDR5`, their `LIMIT_ADDR*` companions, and `OFFSET_ADDR1/3/5`: range-valid bits, legacy MMIO hole enable, channel/die/socket interleave geometry, address-select fields, base/limit address fields, fabric-destination IDs, and high-address offset controls.
- `MMEA2_ADDRNORMDRAM_HOLE_CNTL`, `MMEA2_ADDRNORMGMI_HOLE_CNTL`, `MMEA2_ADDRNORMDRAM_NP2_CHANNEL_CFG`, `MMEA2_ADDRNORMGMI_NP2_CHANNEL_CFG`, `MMEA2_ADDRNORMDRAM_GLOBAL_CNTL`, and `MMEA2_ADDRNORMGMI_GLOBAL_CNTL`: DRAM/GMI hole validity and offset, non-power-of-two channel address-space sizing, and 64K/2M/1G global hash interleave controls.
- `MMEA2_ADDRDEC_BANK_CFG` and `MMEA2_ADDRDEC_MISC_CFG`: DRAM/GMI bank masks, bank-group selection, bank-group interleave, VCM enable bits, package-channel/channel/chip-select/rank-multiplier masks.
- `MMEA2_ADDRDECDRAM_*` and `MMEA2_ADDRDECGMI_*`: XOR hash controls for bank0-bank5, pseudo-channel, pseudo-channel extension, and chip-select hash registers, plus harvest-enable force bits for banks 3-5.
- `MMEA2_ADDRDEC0_*`, `MMEA2_ADDRDEC1_*`, and `MMEA2_ADDRDEC2_*`: repeated decoder tables for chip-select base enables and base addresses, address masks, chip-select address geometry, bank and row address-source selection, bank5 selection, column low/high selection, rank-multiplier selection, channel bit selection, and even/odd row-MSB inversion for primary and secondary chip-select pairs.
- `MMEA2_IO_RD_CLI2GRP_MAP0/1` and partial `MMEA2_IO_WR_CLI2GRP_MAP0/1`: IO traffic client-to-group maps. The chunk contains complete IO read maps, complete IO write map0, and all but the final mask of IO write map1.

## Control Flow

This header chunk has no runtime control flow. Runtime sequencing is supplied by consumers, mainly `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/mmhub_v9_4.c`, which includes `mmhub_9_4_1_offset.h`, `mmhub_9_4_1_sh_mask.h`, and `mmhub_9_4_1_default.h`.

The most direct consumer path in this range is RAS counting:

1. `mmhub_v9_4_ras_fields` maps human-readable subblock names to `SOC15_REG_ENTRY(MMHUB, 0, mmMMEA*_EDC_CNT*)` and `SOC15_REG_FIELD(MMEA*_EDC_CNT*, ...)` pairs. For MMEA1 and MMEA2, the `EDC_CNT`, `EDC_CNT2`, and `EDC_CNT3` field macros in this chunk provide the SEC/DED/SED shifts and masks.
2. `mmhub_v9_4_edc_cnt_regs` lists the EDC counter registers to poll, including `mmMMEA1_EDC_CNT`, `mmMMEA1_EDC_CNT2`, `mmMMEA1_EDC_CNT3`, `mmMMEA2_EDC_CNT`, `mmMMEA2_EDC_CNT2`, and `mmMMEA2_EDC_CNT3`.
3. `mmhub_v9_4_query_ras_error_count()` reads each listed register with `RREG32(SOC15_REG_ENTRY_OFFSET(...))`.
4. `mmhub_v9_4_get_ras_error_count()` compares the register offset, extracts SEC and DED values by applying the generated masks and shifts, logs nonzero subblock counts, and accumulates corrected and uncorrected error totals.
5. `mmhub_v9_4_reset_ras_error_count()` resets those counters by reading the EDC counter registers when MMHUB RAS is supported.

`MMEA1_ERR_STATUS` is also integrated through `mmhub_v9_4_err_status_regs` and `mmhub_v9_4_query_ras_error_status()`, though the current code path compares status bits with the `MMEA0_ERR_STATUS` field names because sibling MMEA status registers share the same layout.

The other macros in this chunk are primarily register-programming surfaces. They are used through SOC15 register helpers, golden/default register tables, firmware initialization, or debug tooling rather than through explicit C branches in this header. For example, `gmc_v9_0.c` has an older-generation golden setting for `mmMMEA1_DRAM_WR_CLI2GRP_MAP0`, illustrating how the client-to-group maps are patched through mask/value register writes.

## State And Persistence Behavior

The header stores no software state and persists nothing. It describes MMIO-backed hardware state whose lifetime is the GPU's programmed register state across initialization, reset, suspend/resume, and RAS service operations.

The represented hardware state includes:

- RAS and EDC counters for MMEA1/MMEA2 internal memories. These counters are read by the driver for error reporting; in the v9.4 code path the EDC counters are reset by readback when MMHUB RAS is enabled.
- Error status and mode bits for MMEA1, including response status, data status/parity flags, clear-error-status, busy-on-error, FUE status, DED mode, propagation/gating policy, and EDC bypass.
- Diagnostic and error-injection state for selected MMEA1 SRAM/tag/page memories. These fields can intentionally inject or delay memory errors and should be treated as validation/RAS controls rather than normal data-path tuning.
- Clock-gating state for MMEA1. Values affect power-management timing and whether write/read/return/register blocks are held in software override or light-sleep override modes.
- DRAM/GMI/IO traffic-group and virtual-channel state for MMEA2. These registers shape how clients are grouped, which virtual channel each group uses, how requests accumulate, and how priority is computed under age, queueing, fixed, urgency, mask, and quantum policies.
- Address-normalization and address-decoder state for MMEA2. These fields define base/limit ranges, interleave geometry, address offsets, address holes, non-power-of-two channel sizing, hash behavior, bank/chip-select/rank/channel/column extraction, and harvested-bank override behavior.

Because these are hardware registers, state persistence depends on GPU reset and power-management sequencing. The generated masks do not encode whether a field is read-only, write-one-to-clear, sticky, self-clearing, shadowed by firmware, or safe to change while traffic is active; that semantic contract lives in the hardware specification and driver sequencing.

## Dependencies

This chunk depends on the AMDGPU SOC15 register-header ecosystem:

- `mmhub_9_4_1_offset.h` provides the corresponding register offsets and base indices.
- `mmhub_9_4_1_default.h` can provide reset/default values for the same register namespace.
- `amdgpu/mmhub_v9_4.c` includes this header and consumes the RAS counter/status fields through `SOC15_REG_FIELD`, `SOC15_REG_ENTRY`, `RREG32`, and MMHUB RAS helpers.
- `soc15.h` and `soc15_common.h` supply register-address construction and register access helpers used by the consumer code.
- `amdgpu_ras.h` and RAS core types such as `struct ras_err_data` consume the decoded EDC counters as corrected and uncorrected error totals.
- Hardware/firmware initialization flows depend on field layout compatibility between this generated header and the actual MMHUB 9.4.1 silicon.

The generated names are coupled to exact register layout. A shift/mask mismatch is not a local compile-only problem; it can silently misprogram memory-fabric arbitration or misdecode RAS counters.

## Integration Points

- `mmhub_v9_4.c` is the direct integration point for this header in the source tree. It includes the header at file scope and uses MMEA1/MMEA2 `EDC_CNT*` field macros in the RAS field table.
- MMHUB RAS reporting integrates through `mmhub_v9_4_query_ras_error_count()`, `mmhub_v9_4_reset_ras_error_count()`, and `mmhub_v9_4_query_ras_error_status()`.
- SOC15 MMIO helpers integrate these macros with register offsets. `SOC15_REG_FIELD(REG, FIELD)` relies on both `REG__FIELD_MASK` and `REG__FIELD__SHIFT` existing and matching the generated naming convention.
- Address-normalization and decoder definitions in this chunk align with physical memory layout programming. They must remain synchronized with any code or firmware that programs DRAM/GMI base/limit/interleave/hash tables.
- Arbitration/client grouping fields align with GPU client IDs and virtual channels. Changes affect memory QoS, request ordering, fairness, and latency behavior for DRAM, GMI, and IO paths.
- Golden-setting and default-register infrastructure can apply selected masks during ASIC initialization. Even when a specific MMEA2 field is not referenced by hand-written C in this repository, generated defaults and firmware-facing initialization may still depend on it.

## Risks

- Boundary risk: this research chunk starts and ends in the middle of registers. `MMEA1_PERFCOUNTER1_CFG` is incomplete at the start, and `MMEA2_IO_WR_CLI2GRP_MAP1` is incomplete at the end. Consumers need the merged file-level view to see those full register definitions.
- Silent misdecode risk: wrong `EDC_CNT*` shifts/masks would cause RAS code to undercount, overcount, or mislabel corrected/uncorrected MMHUB errors. Since the extraction is simple mask-and-shift arithmetic, errors may compile cleanly.
- Error-injection risk: DSM controls can inject hardware memory errors. Accidentally programming these outside validation/RAS flows could create artificial faults or stress paths that look like real hardware failures.
- Memory-fabric risk: address-normalization, interleave, hash, bank, chip-select, rank, and column-selection masks describe physical address routing. Incorrect values can steer requests to the wrong memory location, break interleave assumptions, or reduce usable memory.
- QoS/performance risk: client-to-group, group-to-VC, lazy accumulation, CAM, page-burst, and priority fields influence ordering and fairness. Incorrect tuning can create starvation, latency spikes, throughput loss, or deadlock-like backpressure symptoms.
- Power-management risk: clock-gating override fields can affect idle behavior and wake latency. Misprogramming can increase power, mask busy state, or stall register/read/write/return paths.
- Generated-header drift risk: manual edits to generated masks are brittle. The shift/mask names must match offsets, default values, ASIC register specs, and all `SOC15_REG_FIELD` users.

## Test Signals

Useful validation signals for this chunk are mostly integration and hardware/RAS oriented:

- Build coverage: compile AMDGPU code that includes `mmhub_v9_4.c`. This catches missing or renamed macros used through `SOC15_REG_FIELD`, especially MMEA1/MMEA2 `EDC_CNT*` and `ERR_STATUS` fields.
- Static macro consistency: verify every `SOC15_REG_FIELD(MMEA1_EDC_CNT*)` and `SOC15_REG_FIELD(MMEA2_EDC_CNT*)` use in `mmhub_v9_4.c` has both matching `__SHIFT` and `_MASK` definitions in this header.
- RAS query behavior: on MMHUB 9.4.1 hardware with RAS enabled, inject or observe known SEC/DED events and confirm `mmhub_v9_4_query_ras_error_count()` reports the expected subblock names and corrected/uncorrected totals.
- Counter reset behavior: after reading EDC counter registers through `mmhub_v9_4_reset_ras_error_count()`, re-query counters and confirm the read-to-clear behavior matches hardware expectations.
- Register smoke tests: read MMEA1/MMEA2 EDC and error-status registers through debugfs or driver tracing and confirm decoded fields align with raw register values.
- Initialization stability: boot/resume/reset tests on supported ASICs should show no MMHUB faults, memory-training fallout, VM faults caused by address routing, or unexplained fabric/RAS status bits after default/golden programming.
- Performance regression signals: memory bandwidth, latency, GMI traffic, and IO-heavy workloads are sensitive to the client grouping, virtual-channel, lazy, CAM, and priority fields covered here.

### subset-b-002848: lines 16551-18899

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mmhub/mmhub_9_4_1_sh_mask.h lines 16551-18899

## Scope

This chunk covers generated shift and mask macros from the AMD MMHUB 9.4.1 register mask header. The range starts in the middle of `MMEA2_IO_WR_CLI2GRP_MAP0` and continues through the beginning of `MMEA3_ADDRDEC0_COL_SEL_LO_CS23`. It spans the tail of the MMEA2 address-engine controls and the start of the `mmhub_ea_mmeadec3` address block.

The file is a hardware register bitfield map only. It defines preprocessor constants with the standard AMDGPU generated-header shape:

- `<REGISTER>__<FIELD>__SHIFT` for the bit offset.
- `<REGISTER>__<FIELD>_MASK` for the 32-bit mask.

There are no C functions, structs, variables, memory allocation paths, locks, or executable control flow in this chunk.

## Purpose

The purpose of this header section is to provide the bit-level ABI between the AMDGPU MMHUB v9.4 driver code and MMHUB 9.4.1 hardware. The covered MMEA registers describe request grouping, arbitration, priorities, virtual-channel mapping, SDP credit behavior, error detection/correction counters, error injection controls, clock-gating controls, performance counters, and physical address decoding for MMEA2 and MMEA3.

Driver code normally consumes these masks through AMDGPU register helpers and macros such as `SOC15_REG_FIELD`, `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, and `SOC15_REG_OFFSET`. The matching offset names live in the sibling MMHUB offset header, while this file supplies field positions and masks.

## Important Macro Families

### MMEA2 IO Arbitration and Priority

The opening MMEA2 IO section completes the `MMEA2_IO_WR_CLI2GRP_MAP0` masks and defines `MMEA2_IO_WR_CLI2GRP_MAP1`. These map client IDs `CID0` through `CID31` into 2-bit arbitration groups. In this chunk only the upper half of `MAP0` is present, followed by the complete `MAP1` for `CID16` through `CID31`.

The IO read/write controls that follow are symmetric:

- `MMEA2_IO_RD_COMBINE_FLUSH` and `MMEA2_IO_WR_COMBINE_FLUSH` provide four group timers plus `FORWARD_COMB_ONLY`.
- `MMEA2_IO_GROUP_BURST` defines independent low/high read and write burst limits.
- `MMEA2_IO_RD_PRI_AGE` and `MMEA2_IO_WR_PRI_AGE` define per-group aging rates and age coefficients.
- `MMEA2_IO_RD_PRI_QUEUING`, `MMEA2_IO_WR_PRI_QUEUING`, `MMEA2_IO_RD_PRI_FIXED`, and `MMEA2_IO_WR_PRI_FIXED` define queueing and fixed-priority coefficients.
- `MMEA2_IO_RD_PRI_URGENCY` and `MMEA2_IO_WR_PRI_URGENCY` define urgency coefficients and urgency modes for groups 0-3.
- `MMEA2_IO_RD_PRI_URGENCY_MASKING` and `MMEA2_IO_WR_PRI_URGENCY_MASKING` expose one mask bit per `CID0` through `CID31`.
- `MMEA2_IO_RD_PRI_QUANT_PRI1/2/3` and `MMEA2_IO_WR_PRI_QUANT_PRI1/2/3` define per-group threshold fields used by the quantitative priority path.

These fields are policy knobs for IO-side arbitration. A bad value can change fairness, latency, or starvation behavior across clients rather than just affecting a single request.

### MMEA2 SDP Arbitration and Credits

The `MMEA2_SDP_*` families describe the SDP path after the IO/DRAM/GMI arbiters:

- `MMEA2_SDP_ARB_DRAM`, `MMEA2_SDP_ARB_GMI`, and `MMEA2_SDP_ARB_FINAL` configure burst limits, early read/write switching, end-of-burst behavior, read/write bank-state coupling, chain breaking, read-only virtual channels, and error event/halt behavior.
- `MMEA2_SDP_DRAM_PRIORITY`, `MMEA2_SDP_GMI_PRIORITY`, and `MMEA2_SDP_IO_PRIORITY` map read and write groups 0-3 to 4-bit priority values.
- `MMEA2_SDP_CREDITS` controls tag, write-response, and read-response credit limits.
- `MMEA2_SDP_TAG_RESERVE0/1`, `MMEA2_SDP_VCC_RESERVE0/1`, and `MMEA2_SDP_VCD_RESERVE0/1` reserve tag and virtual-channel credits across VC0-VC7, with distribution-pool controls on the second reserve registers.
- `MMEA2_SDP_REQ_CNTL` provides request override bits for read, write, atomic, DRAM/GMI chaining, and inner-domain mode.

Together these masks describe how requests are admitted and shaped after client grouping. They are tightly coupled to hardware scheduling assumptions and are not generic software queue controls.

### MMEA2 Miscellaneous, Latency, Performance, and EDC

`MMEA2_MISC` exposes a dense set of arbitration and link-manager controls: relative priority enables for DRAM/GMI/IO read and write arbiters, early write-return enablement per VC0-VC7, early SDP original-data handling, link-manager dynamic mode and thresholds, mid-chain/last-chip-select favoritism, and write-to-read chip-select switching.

`MMEA2_LATENCY_SAMPLING` selects latency sampler filters. It can independently choose DRAM, GMI, IO, read, write, atomic-return, atomic-no-return, and VC masks for two samplers. `MMEA2_PERFCOUNTER_LO`, `MMEA2_PERFCOUNTER_HI`, `MMEA2_PERFCOUNTER0_CFG`, `MMEA2_PERFCOUNTER1_CFG`, and `MMEA2_PERFCOUNTER_RSLT_CNTL` define the local performance counter data, selector ranges, modes, enable/clear bits, start/stop triggers, and saturation behavior.

The EDC and diagnostic sections are hardware reliability integration points:

- `MMEA2_EDC_CNT`, `MMEA2_EDC_CNT2`, and `MMEA2_EDC_CNT3` expose SEC/DED/SED count fields for DRAM read/write command memory, write data memory, read/write return tag memory, page memory, IO command/data memory, GMI command/data/page memory, and MAM D0-D3 memories.
- `MMEA2_DSM_CNTL`, `MMEA2_DSM_CNTLA`, `MMEA2_DSM_CNTL2`, and `MMEA2_DSM_CNTL2A` expose DSM irritator data, single-write enables, error-injection enables, delay selectors, and global injection delay fields for the same memory classes.
- `MMEA2_EDC_MODE` provides count, gate, DED mode, propagation, and bypass bits.
- `MMEA2_ERR_STATUS` exposes SDP read/write response status, data status, data parity error, clear-error-status, busy-on-error, and FUE flag bits.

In-tree `amdgpu/mmhub_v9_4.c` consumes the `MMEA2_EDC_CNT*` and `MMEA3_EDC_CNT*` fields in its MMHUB RAS register table via `SOC15_REG_FIELD(...)`, mapping these generated masks into correctable, deferred, and uncorrectable error reporting.

### MMEA2 Clock and Address-Decoder Selection

`MMEA2_CGTT_CLK_CTRL` defines clock-gating timing and override fields: on-delay, off-hysteresis, spare fields, soft-stall overrides for write/read/return, light-sleep override, and soft overrides for write/read/return/register paths.

`MMEA2_MISC2` contains chip-select group swap controls, chip-select group burst limits for DRAM and GMI, IO read/write priority enablement, and read-return swap mode. `MMEA2_ADDRDEC_SELECT` selects the DRAM and GMI address-decoder channel ranges, pairing start and end fields for each target.

### MMEA3 DRAM and GMI Request Scheduling

The `mmhub_ea_mmeadec3` address block starts at line 17514. Its first families mirror the MMEA2 scheduling ideas for MMEA3 DRAM and GMI traffic:

- `MMEA3_DRAM_RD_CLI2GRP_MAP0/1`, `MMEA3_DRAM_WR_CLI2GRP_MAP0/1`, `MMEA3_GMI_RD_CLI2GRP_MAP0/1`, and `MMEA3_GMI_WR_CLI2GRP_MAP0/1` map `CID0` through `CID31` into four 2-bit client groups.
- `MMEA3_DRAM_RD_GRP2VC_MAP`, `MMEA3_DRAM_WR_GRP2VC_MAP`, `MMEA3_GMI_RD_GRP2VC_MAP`, and `MMEA3_GMI_WR_GRP2VC_MAP` map groups 0-3 to 3-bit virtual-channel values.
- `MMEA3_DRAM_RD_LAZY`, `MMEA3_DRAM_WR_LAZY`, `MMEA3_GMI_RD_LAZY`, and `MMEA3_GMI_WR_LAZY` configure per-group delays plus request accumulation threshold, timeout, and idle maximum.
- `MMEA3_DRAM_RD_CAM_CNTL`, `MMEA3_DRAM_WR_CAM_CNTL`, `MMEA3_GMI_RD_CAM_CNTL`, and `MMEA3_GMI_WR_CAM_CNTL` define group CAM depths and, for GMI, chip-select CAM depths.
- `MMEA3_DRAM_PAGE_BURST` and `MMEA3_GMI_PAGE_BURST` define read/write page-burst limits.
- DRAM and GMI read/write priority families cover aging, queueing, fixed coefficients, urgency coefficients/modes, urgency masks, and quantitative threshold registers.

The MMEA3 GMI urgency masking registers again expose one bit per CID for both reads and writes. These masks can suppress urgency behavior for selected clients and therefore directly affect request latency under contention.

### MMEA3 Address Normalization and Decode

From `MMEA3_ADDRNORM_BASE_ADDR0` onward, the chunk moves from scheduling into address normalization and chip-select decode:

- `MMEA3_ADDRNORM_BASE_ADDR0` through `MMEA3_ADDRNORM_BASE_ADDR5` define valid bits, legacy MMIO hole enable, interleave channel/die/socket counts, interleave address selection, and high base address fields.
- `MMEA3_ADDRNORM_LIMIT_ADDR0` through `MMEA3_ADDRNORM_LIMIT_ADDR5` define destination fabric IDs and high limit address fields.
- `MMEA3_ADDRNORM_OFFSET_ADDR1`, `MMEA3_ADDRNORM_OFFSET_ADDR3`, and `MMEA3_ADDRNORM_OFFSET_ADDR5` define high-address offset enable and offset values.
- `MMEA3_ADDRNORMDRAM_HOLE_CNTL` and `MMEA3_ADDRNORMGMI_HOLE_CNTL` define DRAM hole valid/offset fields for DRAM and GMI spaces.
- `MMEA3_ADDRNORMDRAM_NP2_CHANNEL_CFG` and `MMEA3_ADDRNORMGMI_NP2_CHANNEL_CFG` define non-power-of-two 64K-space sizing fields.
- `MMEA3_ADDRDEC_BANK_CFG` and `MMEA3_ADDRDEC_MISC_CFG` define bank masks, bank-group selection/interleave, VCM enables, package/channel/chip-select/rank-mask fields for DRAM and GMI.
- `MMEA3_ADDRDECDRAM_ADDR_HASH_*` and `MMEA3_ADDRDECGMI_ADDR_HASH_*` define XOR-based hash controls for banks 0-5, pseudo-channel, chip-select, and bank XOR fields.
- `MMEA3_ADDRDECDRAM_HARVEST_ENABLE` and `MMEA3_ADDRDECGMI_HARVEST_ENABLE` define force-enable/value controls for harvested bank bits B3-B5.
- `MMEA3_ADDRDEC0_BASE_ADDR_CS*`, `MMEA3_ADDRDEC0_BASE_ADDR_SECCS*`, `MMEA3_ADDRDEC0_ADDR_MASK_*`, `MMEA3_ADDRDEC0_ADDR_CFG_*`, `MMEA3_ADDRDEC0_ADDR_SEL_*`, `MMEA3_ADDRDEC0_ADDR_SEL2_*`, and the beginning of `MMEA3_ADDRDEC0_COL_SEL_LO_*` define chip-select enables, base addresses, masks, geometry, bank/row selector routing, secondary chip-select regions, and low column selectors.

These fields determine how physical addresses are normalized, interleaved, hashed, and routed to DRAM or GMI chip-select resources. They are part of platform bring-up and memory topology programming, not normal runtime data structures.

## Control Flow

This chunk has no runtime control flow. Its "flow" is structural:

1. Driver code includes `mmhub_9_4_1_sh_mask.h`.
2. Register programming code combines one or more `__SHIFT` and `_MASK` constants with a register address from the offset header.
3. MMIO helpers read, compose, write, or extract 32-bit hardware register values.
4. Hardware interprets those bitfields as scheduling, decoding, reliability, or counter state.

For RAS counters specifically, `amdgpu/mmhub_v9_4.c` stores register/field triples in tables, and the RAS path later uses those table entries to read and classify MMHUB EDC counts.

## State and Persistence Behavior

The macros themselves hold no state. The state lives in MMHUB hardware registers:

- Arbitration, priority, credit, clock-gating, address-normalization, and address-decoder fields are persistent hardware configuration until rewritten or reset.
- Performance counters and EDC counters are hardware-observed state that may accumulate until cleared, reset, or reconfigured.
- `CLEAR`, `CLEAR_ALL`, `CLEAR_ERROR_STATUS`, error-injection enable, and DSM single-write controls are command/configuration fields where write ordering and hardware side effects matter.
- Address decode and hash fields persist as part of the active memory topology and can affect every memory access routed through the corresponding MMEA instance.

Because these fields describe MMIO state, persistence is tied to device reset, suspend/resume, GPU reset, and driver initialization sequences rather than C object lifetime.

## Dependencies and Integration Points

This header depends on the AMDGPU generated register-header convention and is paired with MMHUB 9.4.1 offset definitions. It is included by `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/mmhub_v9_4.c`, which provides the main in-tree integration for this ASIC generation.

Important integration points include:

- `amdgpu/mmhub_v9_4.c`, which includes this header and consumes `MMEA2_EDC_CNT*` and `MMEA3_EDC_CNT*` fields for RAS register tables.
- AMDGPU SOC15 register helpers that require exact `<REGISTER>__<FIELD>__SHIFT` and `<REGISTER>__<FIELD>_MASK` names.
- RAS handling, which relies on the EDC count masks to classify correctable, deferred, and uncorrectable MMHUB errors.
- GPU memory initialization and platform topology code, which would use the address normalization, address hash, chip-select, bank, row, and column selector fields when programming MMHUB memory decode.
- Performance/debug tooling, which can use the MMEA performance counter and latency sampler fields for MMHUB traffic observation.

## Risks

- The range starts mid-register at `MMEA2_IO_WR_CLI2GRP_MAP0`; consumers need the previous chunk for the corresponding lower fields and `__SHIFT` definitions for `CID0` through `CID15`.
- Off-by-one shift or mask errors in generated headers silently program the wrong hardware bits. For arbitration and address decode fields, that can manifest as severe performance regressions, memory routing failures, or hangs rather than obvious build failures.
- Address normalization, hash, chip-select, and bank selector masks are topology-critical. Incorrect programming can route physical addresses to the wrong fabric ID, chip select, bank, row, or column.
- Error-injection and EDC mode fields can create or mask reliability events. Tests or debug code using `MMEA2_DSM_*` must avoid leaving injection enabled.
- `CLEAR`, `CLEAR_ALL`, and `CLEAR_ERROR_STATUS` fields have side effects; read-modify-write code must avoid accidentally toggling them while updating unrelated fields.
- The generated naming convention is part of the source contract. Renaming fields breaks `SOC15_REG_FIELD(...)` expansion even when numeric masks are unchanged.

## Test Signals

Useful validation signals for changes touching this chunk are:

- Compile coverage of `amdgpu/mmhub_v9_4.c`; failures in `SOC15_REG_FIELD(MMEA2_EDC_CNT*, ...)` or `SOC15_REG_FIELD(MMEA3_EDC_CNT*, ...)` catch missing or renamed EDC masks.
- Header consistency checks ensuring every field has both a `__SHIFT` and `_MASK` definition, with masks aligned to shifts and no unintended overlap within a register.
- RAS tests or hardware validation that read MMHUB EDC counters through the v9.4 RAS table and confirm expected SEC/DED/SED classification.
- GPU reset, suspend/resume, and memory-init validation on MMHUB 9.4.1 ASICs to catch address-decoder, clock-gating, or arbitration register programming regressions.
- Performance counter smoke tests that configure `MMEA2_PERFCOUNTER*_CFG`, start/stop via `MMEA2_PERFCOUNTER_RSLT_CNTL`, and verify stable counter reads from `MMEA2_PERFCOUNTER_LO/HI`.
- Stress tests with DRAM, GMI, and IO traffic under contention to detect regressions in client grouping, virtual-channel mapping, urgency masks, priority coefficients, and SDP credit settings.

### subset-b-002849: lines 18900-21241

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mmhub/mmhub_9_4_1_sh_mask.h lines 18900-21241

## Scope

This chunk covers generated shift and mask macros from the AMD MMHUB 9.4.1 register mask header. It starts inside the `MMEA3_ADDRDEC0_COL_SEL_LO_CS23` field list at `COL4` and ends inside `MMEA4_GMI_RD_PRI_URGENCY`, after the urgency coefficient masks and before the urgency mode masks that continue in the next chunk.

The covered range includes 2,180 preprocessor definitions and no executable C. The major register families are:

- Remaining `MMEA3_ADDRDEC0` column-selection and row/memory-channel selection fields.
- Complete `MMEA3_ADDRDEC1` and `MMEA3_ADDRDEC2` address decoder windows for chip-select base addresses, masks, address geometry, bank/row/column selection, and row-mask selection.
- `MMEA3_ADDRNORMDRAM_GLOBAL_CNTL` and `MMEA3_ADDRNORMGMI_GLOBAL_CNTL` normalization controls.
- `MMEA3_IO_*` client-to-group maps, combine flush controls, group burst limits, priority aging/queuing/fixed/urgency settings, urgency client masks, and quantum thresholds.
- `MMEA3_SDP_*` arbitration, priority, credit, reserve, and request-control fields.
- `MMEA3_MISC`, latency sampling, performance counter, EDC counter/mode/status, DSM, clock-gating, address-decoder select, and miscellaneous control/status fields.
- Start of the `mmhub_ea_mmeadec4` address block, covering `MMEA4_DRAM_*` arbitration and priority fields, then `MMEA4_GMI_*` mapping, lazy accumulation, CAM, page burst, and priority fields through `MMEA4_GMI_RD_PRI_URGENCY`.

## Purpose

This header section is the bitfield ABI for MMHUB's memory-mapping and memory-client arbitration hardware on ASICs using the 9.4.1 MMHUB register set. Each hardware field is represented by the conventional generated pair:

- `<REGISTER>__<FIELD>__SHIFT`, the bit offset used when composing or extracting the field.
- `<REGISTER>__<FIELD>_MASK`, the 32-bit mask for the field.

The sibling `mmhub_9_4_1_offset.h` header supplies addresses such as `mmMMEA3_EDC_CNT` or `mmMMEA4_EDC_CNT2`; this file supplies only field layouts. The main consumer in this source tree is `drivers/gpu/drm/amd/amdgpu/mmhub_v9_4.c`, which includes `mmhub_9_4_1_offset.h`, `mmhub_9_4_1_sh_mask.h`, and `mmhub_9_4_1_default.h`. AMDGPU helpers such as `REG_SET_FIELD`, `SOC15_REG_FIELD`, `RREG32_SOC15`, and `WREG32_SOC15` depend on these exact `__SHIFT` and `_MASK` names.

## Important Macro Families

### MMEA3 Address Decode

The first part completes `MMEA3_ADDRDEC0_COL_SEL_LO_CS23` and then defines `MMEA3_ADDRDEC0_COL_SEL_HI_*` plus `MMEA3_ADDRDEC0_RM_SEL_*`. These fields describe how selected physical address bits are interpreted as DRAM column bits and row-mask bits for chip-select groups `CS01`, `CS23`, `SECCS01`, and `SECCS23`.

`MMEA3_ADDRDEC1_*` and `MMEA3_ADDRDEC2_*` are complete repeated decoder windows. Each decoder has:

- `BASE_ADDR_CS0..CS3` and `BASE_ADDR_SECCS0..SECCS3`, with `CS_EN` plus a wide `BASE_ADDR` field.
- `ADDR_MASK_*`, with a wide `ADDR_MASK` field.
- `ADDR_CFG_*`, encoding `NUM_BANK_GROUPS`, `NUM_RM`, row low/high widths, column width, bank count, and `HI_COL_EN`.
- `ADDR_SEL_*` and `ADDR_SEL2_*`, selecting source address bits for bank and row fields, including a separate `BANK5` selector.
- `COL_SEL_LO_*` and `COL_SEL_HI_*`, selecting source address bits for columns `COL0..COL15`.
- `RM_SEL_*`, selecting row-mask source bits and row-MSB inversion behavior for even and odd rows.

These fields are low-level DRAM/GMI address mapping controls. They are data-driven from hardware strap/fuse/platform policy rather than ordinary driver algorithm state.

### MMEA3 Normalization and IO Arbitration

`MMEA3_ADDRNORMDRAM_GLOBAL_CNTL` and `MMEA3_ADDRNORMGMI_GLOBAL_CNTL` provide a `BIG_PAGE` field that affects address normalization for DRAM and GMI paths.

The `MMEA3_IO_*` block maps IO clients into arbitration groups and tunes request handling:

- `IO_RD_CLI2GRP_MAP0/1` and `IO_WR_CLI2GRP_MAP0/1` pack sixteen client-to-group fields per direction as 2-bit values.
- `IO_RD_COMBINE_FLUSH` and `IO_WR_COMBINE_FLUSH` expose per-client flush bits for combined request paths.
- `IO_GROUP_BURST` provides read/write burst limits.
- `IO_RD_PRI_AGE` and `IO_WR_PRI_AGE` encode aging rates and age coefficients for four groups.
- `IO_RD_PRI_QUEUING`, `IO_WR_PRI_QUEUING`, `IO_RD_PRI_FIXED`, and `IO_WR_PRI_FIXED` encode group priority coefficients.
- `IO_RD_PRI_URGENCY` and `IO_WR_PRI_URGENCY` encode group urgency coefficients and per-group urgency mode bits.
- `IO_RD_PRI_URGENCY_MASKING` and `IO_WR_PRI_URGENCY_MASKING` expose one mask bit per `CID0..CID31`.
- `IO_RD_PRI_QUANT_PRI1..3` and `IO_WR_PRI_QUANT_PRI1..3` provide per-group quantum thresholds.

Together these definitions describe MMHUB scheduling policy between IO clients before their traffic enters later MMHUB/SDP paths.

### MMEA3 SDP and Diagnostics

`MMEA3_SDP_*` fields configure the shared data path arbitration stage. They cover DRAM/GMI/final arbitration weights or controls, DRAM/GMI/IO priorities, credits, tag reserves, virtual channel command/data reserves, and request-control bits such as `DISABLE_CREDITS` and `DISABLE_FORCE_ORDERED`.

The diagnostic/control group includes:

- `MMEA3_MISC`, including field-update disallowing, self-init, clock gating, black-hole mode, address range behavior, clock switching, and extra latency.
- `MMEA3_LATENCY_SAMPLING`, with period, threshold, reset, count, overflow, enable, interrupt enable/status, and select fields.
- `MMEA3_PERFCOUNTER_LO/HI`, `PERFCOUNTER0_CFG`, `PERFCOUNTER1_CFG`, and `PERFCOUNTER_RSLT_CNTL`, which select performance counter events, control instances, and expose results.
- `MMEA3_EDC_CNT`, `MMEA3_EDC_CNT2`, and `MMEA3_EDC_CNT3`, which pack correctable, single-error-detected, and double-error-detected counters for DRAM, GMI, IO, return-tag, and MAM memories.
- `MMEA3_DSM_CNTL*`, `MMEA3_DSM_CNTL*A`, and `MMEA3_DSM_CNTL2*`, which expose DSM dump controls, modes, timers, offsets, memory selection, and status.
- `MMEA3_CGTT_CLK_CTRL`, `MMEA3_EDC_MODE`, `MMEA3_ERR_STATUS`, `MMEA3_MISC2`, and `MMEA3_ADDRDEC_SELECT`.

The EDC fields are directly integrated by `mmhub_v9_4.c` in its error-counter table for `MMEA3_*` entries. The driver maps readable labels such as `MMEA3_DRAMRD_CMDMEM`, `MMEA3_GMIRD_CMDMEM`, and `MMEA3_MAM_D0MEM` to `SOC15_REG_ENTRY(MMHUB, 0, mmMMEA3_EDC_CNT*)` plus `SOC15_REG_FIELD(MMEA3_EDC_CNT*, ...)` field descriptors.

### MMEA4 DRAM and GMI Arbitration

The chunk then enters `addressBlock: mmhub_ea_mmeadec4`, starting the `MMEA4` range. Covered `MMEA4_DRAM_*` fields mirror the memory-client scheduler structures used for MMEA3 paths:

- Read/write client-to-group maps.
- Read/write group-to-virtual-channel maps.
- Read/write lazy request accumulation delays, thresholds, timeouts, and idle maximums.
- Read/write CAM depth, reorder limits, refill chaining, and page-based chaining.
- Page burst limits.
- Read/write priority aging, queuing, fixed priority, urgency, and quantum thresholds.

The covered `MMEA4_GMI_*` fields repeat the same scheduler pattern for GMI traffic: client-to-group maps, group-to-VC maps, lazy request accumulation, CAM controls, page burst limits, priority aging, queuing, fixed priority, and the start of read urgency. The range ends before the `MMEA4_GMI_RD_PRI_URGENCY__GROUP*_URGENCY_MODE_MASK` definitions, so that register is incomplete in this chunk.

## Control Flow and State Behavior

There is no runtime control flow in this header chunk. It changes driver behavior only by determining how compile-time macros compose and decode MMIO register values.

The state described is persistent hardware register state. Address-decoder fields determine how MMHUB maps address bits into chip selects, banks, rows, columns, row masks, and normalized DRAM/GMI addressing. Arbitration fields persist priority, grouping, burst, lazy accumulation, CAM/reorder, reserve, and credit policy until hardware reset or reprogramming. Diagnostic fields persist counter configuration, sampled latency status, performance counter control, DSM capture mode/status, EDC mode/status, and clock-gating behavior.

Some fields are status or action-like rather than passive configuration. Examples include latency sampling reset/overflow/interrupt status, combine flush bits, DSM dump controls/status, EDC error status, and field-update disallowing. The macros do not encode required ordering, polling, or clear semantics; users must follow MMHUB initialization, RAS, and debug code sequencing.

## Dependencies and Integration Points

This chunk depends on the generated AMD register header convention:

- `mmhub_9_4_1_offset.h` supplies register offsets and base indices.
- `mmhub_9_4_1_default.h` supplies reset/default values where generated.
- `soc15.h` and related AMDGPU helpers use `__SHIFT` and `_MASK` suffixes to implement `REG_SET_FIELD`, `REG_GET_FIELD`, `SOC15_REG_FIELD`, and register read/write helpers.

Observed integration in this tree:

- `amdgpu/mmhub_v9_4.c` includes this header and programs MMHUB through SOC15 register helpers for the 9.4 generation.
- `mmhub_v9_4.c` directly consumes `MMEA3_EDC_CNT*` and `MMEA4_EDC_CNT*` field macros in its RAS/error-count table, exposing corrected/detected MMHUB memory errors by source memory label.
- The same C file initializes MMHUB address translation, apertures, TLB/cache behavior, VMID contexts, invalidation ranges, and snoop override registers. Those paths rely on the same offset/mask/default header set, even though the exact fields in this chunk are primarily MMEA address decoder, scheduler, perf, and EDC surfaces.
- Generated MMEA3/MMEA4 address-decoder and scheduler fields are likely consumed by firmware, bring-up tooling, debugfs/register-dump tooling, or future driver paths rather than high-level filesystem code. Their names remain part of the source-level hardware contract.

## Risks

- Bitfield drift is high impact. A wrong shift or mask can write unrelated MMHUB hardware fields and produce memory misrouting, broken chip-select decoding, bad GMI/DRAM normalization, starvation, hangs, or misleading diagnostics.
- The chunk starts and ends mid-register family. Adjacent chunks are required to describe the complete `MMEA3_ADDRDEC0_COL_SEL_LO_CS23` and `MMEA4_GMI_RD_PRI_URGENCY` registers.
- The address-decoder families are highly repetitive across decoder index, chip-select pair, and secondary chip-select pair. Mechanical edits can easily copy a `CS01` mask into `CS23`, omit `SECCS`, or mismatch `ADDRDEC1` and `ADDRDEC2`.
- Scheduler fields encode policy tradeoffs between latency and fairness. Incorrect client-to-group maps, urgency masks, CAM depths, reorder limits, lazy thresholds, or quantum thresholds can starve clients or collapse bandwidth under IO, DRAM, or GMI load.
- EDC counter fields are operationally visible through RAS. Wrong `MMEA3_EDC_CNT*` or `MMEA4_EDC_CNT*` masks can misclassify correctable versus uncorrectable errors, attribute faults to the wrong internal memory, or hide an error signal.
- Performance counter and latency sampling fields can be confused with ordinary status fields. Reset, overflow, interrupt, instance selection, and event selection need explicit sequencing to avoid stale or partial observations.
- DSM and clock-gating fields are debug/power-sensitive. Incorrect dump mode, clock gating, or black-hole configuration can perturb the hardware while debugging the hardware.

## Test and Validation Signals

Useful validation is mostly build, hardware bring-up, and RAS/debug observation:

- Build AMDGPU code that includes `mmhub/mmhub_9_4_1_sh_mask.h`; this catches missing or renamed macros consumed through `REG_SET_FIELD` and `SOC15_REG_FIELD`.
- On MMHUB 9.4.1 hardware, verify GART/VM initialization, suspend/resume, reset, and multi-hub operation still complete after any mask update.
- RAS tests should read/inject MMHUB EDC paths and confirm `MMEA3_*` and `MMEA4_*` labels in `mmhub_v9_4.c` report expected SEC/SED/DED counts from `EDC_CNT`, `EDC_CNT2`, and `EDC_CNT3`.
- Register-dump comparison against known-good hardware or generated headers should confirm address-decoder base/mask/config/selection fields match the hardware spec for `ADDRDEC1` and `ADDRDEC2`.
- Stress tests with IO, DRAM, and GMI traffic should watch for starvation, timeout, VM faults, or bandwidth regression that could indicate broken priority, grouping, CAM, burst, or lazy accumulation fields.
- Performance-counter and latency-sampling validation should confirm selected `MMEA3_PERFCOUNTER*` events count, reset, overflow, and interrupt as expected.
- Debug capture validation should exercise DSM control/status fields without leaving dump state, clock gating, or field-update blocking enabled unexpectedly.

### subset-b-002850: lines 21242-23604

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mmhub/mmhub_9_4_1_sh_mask.h lines 21242-23604

## Scope

This chunk is a generated AMD MMHUB 9.4.1 shift/mask header segment. It is almost entirely the `MMEA4` address-decode, arbitration, address-normalization, address-decode, IO, SDP, performance, RAS, error-injection, clock, and miscellaneous field layout, followed by the start of the `mmhub_pctldec0` power-control block with complete `PCTL0_CTRL` field masks. The final covered line is only the `//PCTL0_MMHUB_DEEPSLEEP_IB` comment; the `PCTL0_MMHUB_DEEPSLEEP_IB__*` definitions begin in the following line/chunk.

The file contains preprocessor constants only. Each concrete hardware register field is represented by a `REGISTER__FIELD__SHIFT` macro and a matching `REGISTER__FIELD_MASK` macro. There are no C functions, structs, global variables, runtime branches, loops, locks, memory allocation, or direct MMIO reads/writes in this chunk. Runtime behavior comes from AMDGPU code that includes this header together with `mmhub_9_4_1_offset.h` and expands the field macros through helpers such as `SOC15_REG_FIELD`, `REG_SET_FIELD`, and `REG_GET_FIELD`.

Major covered register families are:

- Tail of `MMEA4_GMI_RD_PRI_URGENCY` and full `MMEA4_GMI_WR_PRI_URGENCY`, plus GMI read/write urgency masks and quantum priority thresholds.
- `MMEA4_ADDRNORM_*` normal address ranges 0 through 5, DRAM/GMI hole controls, and non-power-of-two channel configuration.
- `MMEA4_ADDRDEC_*` DRAM/GMI bank, hash, harvest, chip-select base/mask/config/select/column/rank-multiplier fields for address-decode instances 0 through 2.
- `MMEA4_IO_*` client-to-group maps, combine-flush controls, burst controls, priority age/queue/fixed/urgency/masking/quantum registers.
- `MMEA4_SDP_*` arbitration, priority, credit, reserve, and request-control fields.
- `MMEA4_MISC`, `MMEA4_MISC2`, latency sampling, MMHUB performance counters, EDC counters, DSM error-injection controls, CGTT clock controls, EDC mode, error status, and address-decode select.
- `PCTL0_CTRL` in the `mmhub_pctldec0` address block.

## Purpose

The purpose of this header segment is to define the bit layout for programming and decoding MMHUB 9.4.1 hardware registers. The companion offset header gives the register addresses, for example `mmMMEA4_GMI_WR_PRI_URGENCY`, `mmMMEA4_EDC_CNT`, `mmMMEA4_ERR_STATUS`, and `mmPCTL0_CTRL`; this shift/mask header gives the field positions and bit masks inside those registers.

This chunk is especially relevant to the fourth MMHUB memory-engine/address-decode range, `MMEA4`. The fields describe how MMHUB routes address ranges to DRAM or GMI, hashes addresses into bank/channel/chip-select selections, groups clients for arbitration, assigns priority and urgency policy to GMI and IO traffic, exposes SDP credits and arbitration controls, counts reliability events, injects diagnostic memory errors, reports SDP response errors, and controls local MMHUB clock/power policy.

Because the file is generated register metadata, exactness is the contract. A typo in a mask or shift normally compiles cleanly but can make the driver set the wrong MMIO bit, misdecode hardware status, or report incorrect RAS data.

## Important Macro Families

### GMI Priority and Urgency

The chunk starts mid-register in the tail of `MMEA4_GMI_RD_PRI_URGENCY` with group urgency-mode masks, then fully defines `MMEA4_GMI_WR_PRI_URGENCY`. The write urgency register has four group urgency coefficients and four group urgency-mode bits. `MMEA4_GMI_RD_PRI_URGENCY_MASKING` and `MMEA4_GMI_WR_PRI_URGENCY_MASKING` expose one mask bit for each CID 0 through 31, allowing per-client urgency participation to be suppressed or enabled by register programming.

`MMEA4_GMI_RD_PRI_QUANT_PRI1..3` and `MMEA4_GMI_WR_PRI_QUANT_PRI1..3` define four 8-bit group thresholds per register. Together with the urgency and fixed/age/queuing fields defined in neighboring regions, these constants describe GMI request-priority policy for the MMEA4 path.

### Address Normalization

`MMEA4_ADDRNORM_BASE_ADDR0..5`, `LIMIT_ADDR0..5`, and `OFFSET_ADDR1/3/5` define address-normalization windows. Base registers include fields for range validity, legacy MMIO-hole behavior, DRAM/GMI selection, reverse-invert control, symmetric-mode topology, xGMI interleave mode, destination fabric ID, and high base address bits. Limit registers carry the high limit address bits, and offset registers carry high address-offset bits for translated ranges.

`MMEA4_ADDRNORMDRAM_HOLE_CNTL` and `MMEA4_ADDRNORMGMI_HOLE_CNTL` define offset controls for DRAM and GMI holes. `MMEA4_ADDRNORMDRAM_NP2_CHANNEL_CFG` and `MMEA4_ADDRNORMGMI_NP2_CHANNEL_CFG` define non-power-of-two channel masking for 3/5/6/7/10/12/14-channel configurations. These fields are topology-sensitive and must match the memory fabric layout exposed by firmware and the ASIC register database.

### Address Decode, Hashing, Harvesting, and Chip Selects

`MMEA4_ADDRDEC_BANK_CFG` defines bank, bank-group, pseudo-channel, and channel-count settings. `MMEA4_ADDRDEC_MISC_CFG` adds rank count, bank xor, rank-bit selection, channel xor, dimm-pair, low-bit, bank-hash, hashing-enable, and linear/xor remap controls.

The DRAM and GMI hash families are parallel:

- `MMEA4_ADDRDECDRAM_ADDR_HASH_BANK0..5`, `PC`, `PC2`, `CS0`, and `CS1`.
- `MMEA4_ADDRDECGMI_ADDR_HASH_BANK0..5`, `PC`, `PC2`, `CS0`, and `CS1`.

The bank hash registers select address-bit inputs and optionally enable hashing. PC and chip-select hash registers provide compact hash-selection and enable bits. `MMEA4_ADDRDECDRAM_HARVEST_ENABLE` and `MMEA4_ADDRDECGMI_HARVEST_ENABLE` define per-channel harvest-disable masks for CH0 through CH5, plus aggregate channel harvest disable and enable bits. These are integration points for SKU harvesting and memory-channel availability.

`MMEA4_ADDRDEC0`, `MMEA4_ADDRDEC1`, and `MMEA4_ADDRDEC2` then repeat full chip-select layouts. Each decode instance has base-address enable/address fields for CS0 through CS3 and secondary CS0 through CS3; masks for CS01, CS23, secondary CS01, and secondary CS23; address configuration for row/rank/bank/bank-group/channel/pseudo-channel bit counts; address select and select2 fields; low/high column selects; and rank-multiplier selects for normal and secondary chip selects. These macros are the detailed bit map for constructing the physical memory address from normalized inputs.

`MMEA4_ADDRDEC_SELECT` appears later and selects DRAM and GMI address-decode channel start/end indices. It is a compact selector for which decode-channel range is active for each memory fabric path.

### IO Arbitration and Priorities

`MMEA4_ADDRNORMDRAM_GLOBAL_CNTL` and `MMEA4_ADDRNORMGMI_GLOBAL_CNTL` each expose an address-hashing disable bit. The IO priority block follows:

- `MMEA4_IO_RD_CLI2GRP_MAP0/1` and `MMEA4_IO_WR_CLI2GRP_MAP0/1` map CIDs 0 through 15 to 2-bit group IDs for read and write paths.
- `MMEA4_IO_RD_COMBINE_FLUSH` and `MMEA4_IO_WR_COMBINE_FLUSH` provide per-group flush controls and data flush enablement.
- `MMEA4_IO_GROUP_BURST` defines 4-bit burst limits for groups 0 and 1.
- `MMEA4_IO_RD_PRI_AGE` and `MMEA4_IO_WR_PRI_AGE` define per-group age controls, plus read/write-disable bits.
- `MMEA4_IO_RD_PRI_QUEUING` and `MMEA4_IO_WR_PRI_QUEUING` define per-group queuing thresholds.
- `MMEA4_IO_RD_PRI_FIXED` and `MMEA4_IO_WR_PRI_FIXED` define fixed-priority levels.
- `MMEA4_IO_RD_PRI_URGENCY` and `MMEA4_IO_WR_PRI_URGENCY` mirror the GMI urgency coefficient/mode model.
- `MMEA4_IO_RD_PRI_URGENCY_MASKING` and `MMEA4_IO_WR_PRI_URGENCY_MASKING` expose per-CID urgency masks for all 32 CIDs.
- `MMEA4_IO_RD_PRI_QUANT_PRI1..3` and `MMEA4_IO_WR_PRI_QUANT_PRI1..3` define group quantum priority thresholds.

These definitions describe policy knobs for scheduling IO reads and writes through MMEA4. The header itself does not choose the policy; it only supplies the field map used by platform-specific programming.

### SDP Arbitration, Credits, and Request Controls

The SDP block defines downstream arbitration among DRAM, GMI, IO, and final paths:

- `MMEA4_SDP_ARB_DRAM`, `MMEA4_SDP_ARB_GMI`, and `MMEA4_SDP_ARB_FINAL` include LRU disablement, disable bits for request classes, burst controls, priority ordering, and urgent arbitration masks.
- `MMEA4_SDP_DRAM_PRIORITY`, `MMEA4_SDP_GMI_PRIORITY`, and `MMEA4_SDP_IO_PRIORITY` provide PRI0 through PRI3 fields for read/write or path-specific priority order.
- `MMEA4_SDP_CREDITS` exposes read and write response credit fields.
- `MMEA4_SDP_TAG_RESERVE0/1`, `VCC_RESERVE0/1`, and `VCD_RESERVE0/1` reserve tags or virtual-channel credits for multiple MMHUB clients.
- `MMEA4_SDP_REQ_CNTL` exposes start time, stop response/data, combined write-disconnect status, and idle-mask fields.

These fields integrate MMEA4 with the SDP request/response path. Bad masks here would affect fairness, throughput, backpressure, and idle detection rather than normal C data structures.

### Miscellaneous Controls, Latency, and Performance Counters

`MMEA4_MISC` is a dense control/status register with virtual-channel switching, credit-send disablement, requester ID, force-urgent, reorder disablement, AID ID, error-capture ID, no-allocate ID, reorder and read-credit controls, optimized write flush, no-allocate credit status, GMI-link-down disablement, force response-decode, response status selection, XSP/MAM route controls, GART aperture disablement, forced inactivity, performance-counter clock enablement, and HBM backup-request controls.

`MMEA4_LATENCY_SAMPLING` defines a request-ID match, read/write ID, request path selector, sample enable, and minimum latency threshold. `MMEA4_PERFCOUNTER_LO`, `MMEA4_PERFCOUNTER_HI`, `MMEA4_PERFCOUNTER0_CFG`, `MMEA4_PERFCOUNTER1_CFG`, and `MMEA4_PERFCOUNTER_RSLT_CNTL` provide a 64-bit counter view, compare value, performance selector, mode, enable, clear, global enable, clear-all, and stop-on-saturate controls.

These fields are observability and tuning hooks. Performance-counter and latency-sampling controls are stateful hardware controls, not passive constants.

### RAS Counters, DSM Injection, EDC Mode, and Error Status

`MMEA4_EDC_CNT`, `MMEA4_EDC_CNT2`, and `MMEA4_EDC_CNT3` define SEC/SED and DED counters for internal MMEA4 memories. Covered subblocks include DRAM read/write command memories, DRAM write data memory, return tag memories, DRAM page memories, IO read/write command/data memories, GMI read/write command/data/page memories, and MAM data memories. `mmhub_v9_4.c` consumes these fields through `mmhub_v9_4_ras_fields`, using `SOC15_REG_FIELD(MMEA4_EDC_CNT*, ...)` entries to decode counts for MMHUB RAS reporting.

`MMEA4_DSM_CNTL`, `MMEA4_DSM_CNTLA`, `MMEA4_DSM_CNTL2`, and `MMEA4_DSM_CNTL2A` define diagnostic error-injection enable and delay-selection bits for the same broad memory families. They include an `INJECT_DELAY` field where present. These should be treated as lab/debug controls; accidentally setting them in a production path can create synthetic RAS events or hardware faults.

`MMEA4_EDC_MODE` defines output counting, FUE gating, DED mode, FED propagation, and EDC bypass controls. `MMEA4_ERR_STATUS` exposes SDP read/write response status, read-response data status, data parity error, clear-error-status, busy-on-error, and FUE flag fields. `mmhub_v9_4.c` includes `mmMMEA4_ERR_STATUS` in `mmhub_v9_4_err_status_regs` for MMHUB error-status queries.

`MMEA4_CGTT_CLK_CTRL` defines on delay, off hysteresis, spare fields, soft stall override bits, light-sleep override, and soft override bits for write/read/return/register paths. `MMEA4_MISC2` includes DRAM/GMI CS-group swap controls, burst-limit data fields, IO read/write priority enablement, and return-swap mode.

### PCTL0 Control Boundary

The chunk enters a new address block at `// addressBlock: mmhub_pctldec0` and fully defines `PCTL0_CTRL`. Its fields include power-gating enablement, allowed deep-sleep mode, RSMU and DAGB idle thresholds, state-controller ignore-protection-fault behavior, EA0 through EA4 SDP partial-ack and full-ack override bits, and a `PGFSM_CMD_STATUS` field.

The next comment, `//PCTL0_MMHUB_DEEPSLEEP_IB`, is included as the final line of this chunk, but none of its DS bit definitions are in scope here. Neighboring code such as JPEG ring start/end paths references the `PCTL0_MMHUB_DEEPSLEEP_IB` register by offset/comment, so the merge lane should connect this boundary to the following chunk before making file-level statements about PCTL deep-sleep IB fields.

## Control Flow and State Behavior

There is no executable control flow in this chunk. All control flow is in consumers such as `drivers/gpu/drm/amd/amdgpu/mmhub_v9_4.c`, which includes `mmhub_9_4_1_offset.h` and `mmhub_9_4_1_sh_mask.h`.

The state represented by these macros is hardware MMIO state:

- Configuration state: address ranges, address-normalization policy, channel/chip-select topology, hashing, harvesting, arbitration policy, priority policy, SDP reserves, PCTL power behavior, CGTT clock controls, and EDC mode.
- Status state: no-allocate credit status, SDP request/idle status, error status, FUE flag, and PGFSM command status.
- Counter state: EDC SEC/DED counters, performance counters, and latency sampling thresholds/results.
- Request/debug state: combine flush controls, performance clear/enable bits, DSM error-injection controls, and clear-error-status bits.

Persistence is not implemented in this header. Register values live in hardware and are initialized, queried, reset, or restored by driver code and firmware sequencing. Some counters are read-to-reset in the RAS path: `mmhub_v9_4_reset_ras_error_count()` reads EDC counter registers, including `mmMMEA4_EDC_CNT`, `mmMMEA4_EDC_CNT2`, and `mmMMEA4_EDC_CNT3`, to reset counts when MMHUB RAS is supported.

## Dependencies and Integration Points

Direct dependencies are the AMD generated-register convention and the matching headers:

- `mmhub_9_4_1_offset.h` supplies `mm...` offsets and base indices for the same register names. For this chunk, examples include `mmMMEA4_GMI_WR_PRI_URGENCY` at offset `0x07ab`, `mmMMEA4_GMI_WR_PRI_URGENCY_MASKING` at `0x07ad`, `mmPCTL0_CTRL` at `0x08c0`, and `mmPCTL0_MMHUB_DEEPSLEEP_IB` at `0x08c1`.
- `mmhub_9_4_1_default.h` supplies generated default values for the same register generation where available.
- `soc15.h` and related AMDGPU helpers provide `SOC15_REG_ENTRY`, `SOC15_REG_FIELD`, `RREG32`, `WREG32`, `REG_SET_FIELD`, and `REG_GET_FIELD` behavior that expands these masks and shifts.

Observed local integration points include:

- `drivers/gpu/drm/amd/amdgpu/mmhub_v9_4.c`, which includes this header and the matching offset header.
- `mmhub_v9_4_ras_fields`, which maps `MMEA4_EDC_CNT`, `MMEA4_EDC_CNT2`, and `MMEA4_EDC_CNT3` fields to named MMHUB RAS subblocks such as `MMEA4_DRAMRD_CMDMEM`, `MMEA4_GMIRD_CMDMEM`, `MMEA4_GMIWR_PAGEMEM`, and `MMEA4_MAM_D*MEM`.
- `mmhub_v9_4_edc_cnt_regs`, which lists the MMEA4 EDC counter registers that are read by `mmhub_v9_4_query_ras_error_count()` and `mmhub_v9_4_reset_ras_error_count()`.
- `mmhub_v9_4_err_status_regs`, which lists `mmMMEA4_ERR_STATUS` for MMHUB RAS error-status polling.
- `mmhub_v9_4_set_clockgating()` and adjacent clock/power paths, which are part of the same MMHUB generation and rely on generated field headers for clock-gating and power-control programming, even when specific fields from this chunk are not all referenced directly in the visible code.
- `gmc_v9_0.c`, which selects `mmhub_v9_4_funcs` and `mmhub_v9_4_ras` for the relevant GMC/MMHUB IP path, making this generated header part of GPU memory-management bring-up for that ASIC family.

## Risks

- Generated mask/shift drift is silent at compile time. A wrong mask can still build but program a different hardware bit than intended.
- Address-normalization and address-decode fields are data-integrity sensitive. Incorrect base/limit/offset, hash, channel, chip-select, column, or rank-multiplier fields can route memory traffic incorrectly or make RAS reports point at the wrong channel/rank.
- Harvest-enable and non-power-of-two channel fields are SKU/topology sensitive. A field mismatch may only appear on partially harvested dies or uncommon channel-count configurations.
- IO and GMI priority fields affect fairness and forward progress. Incorrect client-to-group maps, urgency masks, quantum thresholds, or burst controls can cause starvation, latency spikes, or reduced fabric throughput.
- SDP credit/reserve and arbitration masks control backpressure. Bad values can produce hangs or poor utilization without obvious software-side errors.
- EDC and error-status fields feed RAS accounting. Wrong SEC/DED masks can invert corrected versus uncorrected counts, double-count, miss a failing subblock, or emit misleading `MMHUB SubBlock ...` logs.
- DSM error-injection controls are hazardous outside diagnostics. Misprogramming injection enable or delay bits can synthesize faults and pollute RAS telemetry.
- Clear/status fields such as `MMEA4_ERR_STATUS__CLEAR_ERROR_STATUS` should not be treated as ordinary persistent configuration; writing them can acknowledge or drop hardware error state.
- `PCTL0_CTRL` power-gating/deep-sleep policy is timing and platform sensitive. Bad idle thresholds, ack overrides, or protection-fault ignore behavior may only fail under suspend/resume, reset, low-power, or high-load concurrency.
- The chunk begins and ends at artificial boundaries. The first covered lines are the tail of `MMEA4_GMI_RD_PRI_URGENCY`, and the final `PCTL0_MMHUB_DEEPSLEEP_IB` comment has no field definitions until the next chunk.

## Test and Validation Signals

Useful validation is mostly build and hardware integration testing:

- Build AMDGPU with MMHUB 9.4 support to catch missing, renamed, or malformed field macros used by `mmhub_v9_4.c`.
- Boot on hardware using `mmhub_v9_4_funcs` and verify GART/VM bring-up, memory allocation, DMA, and page-table update workloads. Address-decode mistakes can surface as VM faults, memory corruption, or GPU hangs.
- Query MMHUB RAS counters and confirm `MMEA4_EDC_CNT*` decoding reports expected subblock names and separates SEC/SED from DED counts correctly.
- Reset MMHUB RAS counts and verify read-to-reset behavior clears the relevant `MMEA4_EDC_CNT*` counters without losing unrelated state.
- Trigger or inject controlled MMHUB reliability events in a lab environment and check that `MMEA4_ERR_STATUS` and EDC counter fields decode consistently with hardware documentation.
- Stress GMI and IO traffic with mixed read/write clients to expose priority, urgency, quantum, and SDP arbitration regressions as latency, starvation, or throughput anomalies.
- Exercise platform power-management paths, including clock gating, light sleep, suspend/resume, and reset, to catch `PCTL0_CTRL` and `MMEA4_CGTT_CLK_CTRL` field problems.
- Compare regenerated `mmhub_9_4_1_sh_mask.h` and `mmhub_9_4_1_offset.h` against the authoritative register database, paying special attention to repeated per-CID/per-group/per-channel macros where copy-generation errors are easy to miss.

## Cross-Chunk Notes

The range starts after the beginning of `MMEA4_GMI_RD_PRI_URGENCY`, so the complete read-urgency register must be reconciled with the previous chunk. The range ends immediately after the `//PCTL0_MMHUB_DEEPSLEEP_IB` marker, before any `PCTL0_MMHUB_DEEPSLEEP_IB__DS*` shift/mask definitions. The final per-file report should merge this chunk with its neighbors before describing complete GMI urgency or PCTL deep-sleep IB coverage.

### subset-b-002851: lines 23605-25971

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mmhub/mmhub_9_4_1_sh_mask.h lines 23605-25971

## Scope And Purpose

This chunk is a generated AMDGPU MMHUB 9.4.1 shift/mask header section. It contains preprocessor constants only: no C functions, structs, enums, storage objects, branches, or loops. The constants define bit offsets and masks for MMHUB power-control, ATC/L2, page-fault, VM-context, and invalidation-engine registers.

The covered range starts inside the `mmhub_pctldec0` address block immediately after the `PCTL0_MMHUB_DEEPSLEEP_IB` register heading, continues through `mmhub_l1tlb_vml1dec`, `mmhub_l1tlb_vml1pldec`, `mmhub_l1tlb_vml1prdec`, `mmhub_utcl2_atcl2dec`, `mmhub_utcl2_vml2pfdec`, and the first part of `mmhub_utcl2_vml2vcdec`, and ends inside the `VML2VC0_VM_INVALIDATE_ENG6_REQ` register. The neighboring chunk is needed for the final `CLEAR_PROTECTION_FAULT_STATUS_ADDR_MASK` for engine 6 and all later invalidation request/ack/address registers.

The practical purpose is to provide the bit-field contract consumed by AMDGPU MMHUB v9.4 code. Driver code combines these `REGISTER__FIELD__SHIFT` and `REGISTER__FIELD_MASK` macros with companion register offsets from `mmhub_9_4_1_offset.h`, defaults from `mmhub_9_4_1_default.h`, and helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `SOC15_REG_FIELD`, `RREG32_SOC15_OFFSET`, and `WREG32_SOC15_OFFSET`.

## Important APIs, Types, And Register Families

There are no callable APIs or local types in this chunk. The public surface is the generated macro namespace.

Important register families covered here are:

- `PCTL0_MMHUB_DEEPSLEEP_IB`, `PCTL0_MMHUB_DEEPSLEEP_OVERRIDE`, `PCTL0_MMHUB_DEEPSLEEP_OVERRIDE_IB`, `PCTL0_PG_IGNORE_DEEPSLEEP`, and `PCTL0_PG_IGNORE_DEEPSLEEP_IB`: per-domain deep-sleep request, override, inbound, and ignore bitmaps. They expose `DS0` through `DS16`, plus ATHUB/all-IP aggregate fields on selected registers and a `SETCLEAR` bit on the inbound deep-sleep register.
- `PCTL0_SLICE[0-4]_CFG_DAGB_BUSY`: single `BUSY` bit per slice for DAGB activity gating state.
- `PCTL0_SLICE[0-4]_CFG_DS_ALLOW` and `_IB`: per-slice deep-sleep-allow bitmaps for domains `DS0` through `DS16`.
- `PCTL0_UTCL2_MISC` and `PCTL0_SLICE[0-4]_MISC`: critical-register lock, tile idle threshold, RENG memory light-sleep enable, state-controller force-done, execute-on-register-update, read-timer enable, and slice-only `DEEPSLEEP_DISCSDP`.
- `PCTL0_UTCL2_RENG_EXECUTE` and `PCTL0_SLICE[0-4]_RENG_EXECUTE`: register-engine execution controls, including execute-now, execute-now mode, start pointer, and end pointer. UTCL2 uses an 11-bit index/start/end range shape, while slices use a 10-bit range shape.
- `PCTL0_*_RENG_RAM_INDEX` and `PCTL0_*_RENG_RAM_DATA`: register-engine RAM address and full 32-bit data fields for UTCL2 and slices 0-4.
- `PCTL0_*_STCTRL_REGISTER_SAVE_RANGE[0-4]` and `PCTL0_*_STCTRL_REGISTER_SAVE_EXCL_SET[0-1]`: state-controller register save base/limit pairs and exclusion pairs for UTCL2 and slices 0-4.
- `VML1_0_MC_VM_MX_L1_TLB[0-7]_STATUS`: L1 TLB status registers with `BUSY` and `VMID` fields.
- `VML1PL0_MC_VM_MX_L1_PERFCOUNTER[0-3]_CFG`, `VML1PL0_MC_VM_MX_L1_PERFCOUNTER_RSLT_CNTL`, `VML1PR0_MC_VM_MX_L1_PERFCOUNTER_LO`, and `VML1PR0_MC_VM_MX_L1_PERFCOUNTER_HI`: L1 TLB performance counter event select, compare, mode, enable, clear, start/stop trigger, low/high result, and saturation behavior.
- `ATCL2_0_ATC_L2_CNTL`, `CNTL2`, `CNTL3`, and `CNTL4`: ATC L2 cache enablement, faulting behavior, debugger disablement, invalidate requests, cache-update policy, transaction-limit, and real-time/non-real-time controls.
- `ATCL2_0_ATC_L2_CACHE_DATA[0-2]`, `ATCL2_0_ATC_L2_CACHE_4K_DSM_*`, and `ATCL2_0_ATC_L2_CACHE_2M_DSM_*`: cache debug/readback and DSM/error-injection fields for 4K and 2M entries, including inject delay, irritator data, single write, error injection, counter write, SEC/DED count, and FUE test fields.
- `ATCL2_0_ATC_L2_STATUS`, `STATUS2`, and `STATUS3`: ATC L2 busy and invalidation-finished status.
- `ATCL2_0_ATC_L2_MISC_CG`, `MEM_POWER_LS`, and `CGTT_CLK_CTRL`: clock gating, memory light-sleep, delay/hysteresis, and soft override controls.
- `ATCL2_0_ATC_L2_MM_GROUP_RT_CLASSES`: full-width group real-time class mapping.
- `VML2PF0_VM_L2_CNTL`, `CNTL2`, `CNTL3`, and `CNTL4`: VM L2 cache enablement, fragment processing, endian swap, PDE/PTE cache policy, default-page handling, invalidate mode, cache sizing, bank selection, force-miss controls, identity-mode fragment size, TAP request physical controls, transaction limits, and clock-gating override.
- `VML2PF0_VM_L2_STATUS`: L2 busy, per-context-domain busy bitmap, and PTE/PDE parity-error status fields.
- `VML2PF0_VM_DUMMY_PAGE_FAULT_*`: dummy-page fault enable/address controls.
- `VML2PF0_VM_L2_PROTECTION_FAULT_CNTL`, `CNTL2`, `MM_CNTL3`, `MM_CNTL4`, `STATUS`, address, and default-address registers: global protection-fault control, client interrupt masks, retry/PRT controls, VML1 read/write client masks, fault status decode fields, faulting logical address, and default physical page address.
- `VML2PF0_VM_L2_CONTEXT1_IDENTITY_APERTURE_*` and `VML2PF0_VM_L2_CONTEXT_IDENTITY_PHYSICAL_OFFSET_*`: identity aperture low/high logical-page bounds and physical offset fields.
- `VML2PF0_VM_L2_MM_GROUP_RT_CLASSES`: 32 one-bit group real-time class flags.
- `VML2PF0_VM_L2_BANK_SELECT_RESERVED_CID` and `CID2`: reserved read/write client IDs, enable, reserved-cache invalidation mode, and private invalidation fields.
- `VML2PF0_VM_L2_CACHE_PARITY_CNTL` and `VML2PF0_VM_L2_CGTT_CLK_CTRL`: parity interrupt enables and cache/clock-gating override timing fields.
- `VML2VC0_VM_CONTEXT0_CNTL` through `VML2VC0_VM_CONTEXT15_CNTL`: per-VMID context enable, page-table depth, block size, retry behavior, and protection-fault interrupt/default controls.
- `VML2VC0_VM_CONTEXTS_DISABLE`: disable bitmap for contexts 0-15.
- `VML2VC0_VM_INVALIDATE_ENG0_SEM` through `ENG17_SEM`: one-bit invalidation-engine semaphore fields.
- `VML2VC0_VM_INVALIDATE_ENG0_REQ` through the partial `ENG6_REQ`: per-VMID invalidate request mask, flush type, invalidate L2 PTEs/PDE0/PDE1/PDE2/L1 PTEs, and clear-protection-fault-status-address request fields.

## Control Flow And State Behavior

This header chunk has no runtime control flow. Its constants are substituted into MMHUB driver code at compile time.

The runtime flow that uses these definitions is in AMDGPU MMHUB setup and maintenance code. `mmhub_v9_4.c` includes `mmhub_9_4_1_offset.h`, this shift/mask header, and `mmhub_9_4_1_default.h`. It reads default or current register values, uses `REG_SET_FIELD` with macros such as `VML2VC0_VM_CONTEXT0_CNTL__ENABLE_CONTEXT_MASK`, and writes the composed values through SOC15 register helpers.

Several flow patterns are implied by the field groups:

- Power-management and deep-sleep control code programs PCTL registers to allow, override, or ignore deep-sleep requests for UTCL2, slices, MMHUB, ATHUB, and aggregate domains. The `PCTL0_*_MISC` and RENG fields describe how register save/restore and register-engine command execution are triggered around power transitions.
- VM/GART initialization programs L2 cache controls, identity aperture bounds, default fault addresses, VM context controls, and invalidate ranges. In `mmhub_v9_4.c`, `mmhub_v9_4_enable_system_domain()` updates `VML2VC0_VM_CONTEXT0_CNTL`, `mmhub_v9_4_setup_vmid_config()` programs contexts 1-15 with page-table depth/block-size and fault policy, and `mmhub_v9_4_program_invalidation()` initializes invalidation-engine address ranges that are adjacent to this chunk.
- TLB/cache invalidation flow uses per-engine semaphore, request, ack, and address registers. This chunk covers semaphore fields for engines 0-17 and request fields for engines 0-6; the generic VM hub setup in `mmhub_v9_4_init()` records engine 0 register offsets and computes `eng_distance` from engine 1 minus engine 0 so common VM invalidation code can address all engines.
- Fault handling and diagnostics read `VML2PF0_VM_L2_PROTECTION_FAULT_STATUS` and fault address registers, then clear or control subsequent status updates through protection-fault control bits. The status fields decode `MORE_FAULTS`, walker error, permission fault class, mapping error, client ID, read/write, atomic, VMID, VF, and VFID.
- Clock-gating code reads and writes fields such as `ATCL2_0_ATC_L2_MISC_CG__ENABLE_MASK` and `ATCL2_0_ATC_L2_CGTT_CLK_CTRL` overrides to enable or disable medium-grain and light-sleep behavior.

State is entirely hardware state. The header does not store values, serialize writes, or validate access rights. Many fields are persistent configuration until reset, suspend/resume, GPU reset, power-gating, firmware programming, or driver reinitialization. Status, semaphore, request, invalidate, clear, counter, and fault-address fields are transient or side-effectful: they may be set by hardware, polled by the driver, cleared by write-one/control bits, or consumed by common VM invalidation/fault paths.

## Dependencies And Integration Points

The immediate companion files are:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mmhub/mmhub_9_4_1_offset.h`, which supplies `mm*` register offsets and base-index macros for the register names in this chunk.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mmhub/mmhub_9_4_1_default.h`, which supplies default register values such as VM context defaults, invalidation request defaults, and PCTL defaults.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/mmhub_v9_4.c`, the primary consumer in this tree. It includes this header and uses these masks for VM context setup, L2 cache programming, fault controls, clock gating, EDC counters near the previous chunk boundary, and VM hub register layout initialization.

Key integration points in `mmhub_v9_4.c` include:

- `mmhub_v9_4_enable_system_domain()` uses `VML2VC0_VM_CONTEXT0_CNTL` fields to enable context 0 and set depth/retry behavior.
- `mmhub_v9_4_setup_vmid_config()` uses the repeated `VML2VC0_VM_CONTEXT1_CNTL` field layout as a template for contexts 1-15, relying on offset distances rather than hand-coded register names for every context.
- `mmhub_v9_4_init_cache_regs()` uses `VML2PF0_VM_L2_CNTL*` fields for cache enablement, bank selection, fragment size, and TAP request physical controls.
- `mmhub_v9_4_update_fault_enable_default()` uses `VML2PF0_VM_L2_PROTECTION_FAULT_CNTL` fields to control default fault handling and crash-on-fault behavior.
- `mmhub_v9_4_init()` records VM hub offsets for context base addresses, invalidation sem/request/ack, context control, and L2 protection fault status/control, then computes context and invalidation-engine distances from adjacent generated register offsets.
- `mmhub_v9_4_update_medium_grain_clock_gating()` uses `ATCL2_0_ATC_L2_MISC_CG__ENABLE_MASK` and related clock-gating fields.
- The RAS/EDC table in `mmhub_v9_4.c` uses adjacent `MMEA4_EDC_CNT3` fields from just before this chunk boundary; this chunk continues into other MMHUB reliability and diagnostics fields such as ATC DSM counters and parity/fault status.

Other consumers include media ring setup code that writes hard-coded packet values for `PCTL0_MMHUB_DEEPSLEEP_IB` in older JPEG paths. Comments in JPEG v4.0.3 note that the `PCTL0_MMHUB_DEEPSLEEP_IB` register can vary by MMHUB version, which reinforces why the matching versioned offset/mask header matters.

Although this repository path is under a Ceph client source import, this file belongs to the Linux AMDGPU DRM hardware interface. It has no Ceph filesystem control flow, wire protocol behavior, distributed lock state, or on-disk persistence.

## Risks And Edge Cases

- This file is a hardware ABI. A wrong mask, wrong shift, or mismatched versioned header can compile cleanly while programming the wrong MMHUB field, causing GPU memory faults, failed invalidations, stale translations, lost fault diagnostics, power-management regressions, or hangs.
- The chunk starts after the `PCTL0_MMHUB_DEEPSLEEP_IB` comment and ends before the final `VML2VC0_VM_INVALIDATE_ENG6_REQ__CLEAR_PROTECTION_FAULT_STATUS_ADDR_MASK`. Whole-file analysis must reconcile neighboring chunks before treating those two registers as complete.
- PCTL deep-sleep and register-engine fields are power-state controls, not passive metadata. Mistakes can prevent deep sleep, force domains into sleep at the wrong time, skip register save/restore, or run register-engine RAM commands with the wrong start/end pointer.
- `CRITICAL_REGS_LOCK`, save range, and exclusion-set fields imply protected register windows. Incorrect programming can either leave critical state unprotected during power transitions or block intended state restoration.
- `RENG_RAM_DATA` and several address/status fields use full-width `0xFFFFFFFFL` masks. Callers should treat them as 32-bit register values and avoid signed-extension or format-string confusion in diagnostics.
- ATC and VM L2 invalidate fields are side-effectful. Read-modify-write patterns must avoid accidentally asserting `INVALIDATE_ALL_L1_TLBS`, `INVALIDATE_L2_CACHE`, per-VMID invalidate bits, or clear-fault-status bits.
- Repeated VM context controls are highly regular but easy to misuse. The driver programs context 1 as a template using context-distance arithmetic; a broken generated offset or field layout for any context would affect many VMIDs.
- Fault-control fields combine default action, interrupt enable, retry/PRT behavior, client masks, and crash policy in adjacent bits. Incorrect defaults can suppress important faults, create interrupt storms, change no-retry/retry behavior, or crash the GPU on recoverable faults.
- Protection-fault status fields are packed and diagnostic-critical. Misdecoding `CID`, `VMID`, `VF`, or `VFID` can send debugging and RAS analysis toward the wrong client or virtual function.
- Identity aperture and dummy/default fault addresses are split into low 32-bit and high 4-bit fields. Callers must preserve GPU page-number semantics and not treat these as arbitrary byte addresses without the surrounding driver convention.
- ATC DSM/error-injection and parity controls should be isolated to diagnostics/RAS validation. Leaving injection, counter-write, FUE, or parity interrupt bits enabled unexpectedly can create false error reports or real fault handling noise.
- Clock-gating and memory light-sleep fields are timing-sensitive. Bad `ON_DELAY`, `OFF_HYSTERESIS`, light-sleep setup/hold, or override values can reduce power savings, introduce wake latency, or destabilize active VM/ATC traffic.
- Invalidation-engine request groups are repeated. This chunk contains complete request masks for engines 0-5 and all but one mask for engine 6; reviewers should check engine 0, a middle engine, and the boundary engine when validating generated consistency.

## Test And Validation Signals

There are no direct unit tests for this macro-only chunk. Useful validation is compile-time, generated-data, and hardware-observation based:

- Build AMDGPU code that includes `mmhub_v9_4.c` and the MMHUB 9.4.1 headers to catch missing, renamed, or syntactically invalid macros.
- Run static mask/shift consistency checks: single-bit masks should match their shifts, multi-bit masks should be contiguous, fields in a register should not overlap, full-width fields should have shift zero, and repeated registers should preserve identical layouts.
- Cross-check `mmhub_9_4_1_sh_mask.h` against `mmhub_9_4_1_offset.h` so every register family in this chunk has the expected `mm*` offset and base index.
- Compare defaults in `mmhub_9_4_1_default.h` with the masks here, especially `PCTL0_CTRL`, `VML2VC0_VM_CONTEXT[0-15]_CNTL`, invalidation request defaults, and L2/fault-control defaults.
- Exercise GART and VM initialization on MMHUB 9.4 hardware or simulator. Signals include successful context 0 enablement, contexts 1-15 configured with expected depth/block size, correct L2 cache setup, and no unexpected VM fault storms.
- Exercise TLB invalidation under BO map/unmap, VM update, GPU reset, and process teardown. Watch per-engine semaphore/request/ack behavior and ensure invalidations complete without stale translations.
- Inject or observe protection faults and confirm that `VML2PF0_VM_L2_PROTECTION_FAULT_STATUS` decodes the expected client, VMID, VF/VFID, access type, and fault reason, and that clear/subsequent-update controls behave as expected.
- Run suspend/resume, runtime power management, and clock-gating tests to validate PCTL, ATC L2 clock-gating, memory light-sleep, and register-save/restore behavior.
- Use RAS/debug validation for ATC DSM, parity, and cache status fields only in controlled diagnostic paths, verifying that injection and counter bits do not persist into normal operation.

## Chunk Notes For Merge Lane

This is chunk 11 of 19 for `mmhub_9_4_1_sh_mask.h`. It continues the `mmhub_pctldec0` block that started in the previous chunk, then covers L1 TLB status/performance masks, ATC L2 masks, VM L2/page-fault/identity-aperture masks, VM context controls for contexts 0-15, context disable masks, invalidation semaphores for engines 0-17, and invalidation request masks through most of engine 6. The final per-file report should merge this with chunks 10 and 12 before making complete statements about PCTL0 control or the full invalidation-engine register set.

### subset-b-002852: lines 25972-28443

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mmhub/mmhub_9_4_1_sh_mask.h lines 25972-28443

## Scope

This chunk is part of AMDGPU's generated ASIC register bitfield header for the MMHUB 9.4.1 block. It contains C preprocessor constants only: each register field has a `__SHIFT` macro and a matching `_MASK` macro using the hardware register name as the prefix. There are no functions, structs, enums, allocations, or executable control flow in this chunk. Runtime behavior comes from driver code that includes this header and uses these masks with register addresses from the companion `*_offset.h`/`*_d.h` headers and AMDGPU register access helpers.

## Purpose

The chunk documents bit layouts for several MMHUB sub-blocks:

- `VML2VC0` virtual-channel 0 invalidation and context page table registers.
- `VMSHAREDPF0`, `VMSHAREDVC0`, and `VMSHAREDHV0` shared PF/VC/HV memory aperture, virtualization, ATS, IOMMU, and XGMI controls.
- `ATCL2PFCNTR0`/`ATCL2PFCNTL0` and `VML2PL0`/`VML2PR0` performance counter programming and result fields.
- `DAGB5` read/write data-arbitration gateway controls for clients, virtual channels, bandwidth windows, outstanding request limits, TLB credits, pending-status bits, and clock-gating overrides.

The constants let C code compose and decode 32-bit MMIO register values without embedding raw bit positions or masks in driver logic.

## Important Macro Families

`VML2VC0_VM_INVALIDATE_ENG7_REQ` through `ENG17_REQ` define per-engine invalidate requests. Each request register exposes `PER_VMID_INVALIDATE_REQ` in bits 0-15, `FLUSH_TYPE` in bits 16-17, and individual invalidation selectors for L2 PTEs, PDE0/PDE1/PDE2, L1 PTEs, and protection-fault status address clearing. The chunk begins with the final mask from `ENG6_REQ`, so line 25972 is a boundary from the prior chunk.

`VML2VC0_VM_INVALIDATE_ENG0_ACK` through `ENG17_ACK` define acknowledgement status fields: `PER_VMID_INVALIDATE_ACK` and `INVALIDATE_ALL_ACK`. Code using the request fields should poll or inspect these acknowledgements to know whether the corresponding invalidate engine has completed.

`VML2VC0_VM_INVALIDATE_ENG*_ADDR_RANGE_LO32/HI32` provide optional logical-page address range fields for engines 0-17. The low register has a full 32-bit `LOGICAL_ADDR_LO32` mask and an `ENABLE` bit at bit 31; the high register carries a 30-bit `LOGICAL_ADDR_HI32` field. These fields pair with invalidate requests when callers need ranged invalidation rather than whole-context invalidation.

`VML2VC0_VM_CONTEXT0..15_PAGE_TABLE_BASE/START/END_ADDR_LO32/HI32` describe VM context page table base and logical range registers. Low halves are full 32-bit page-number fields, while high halves are 4-bit `*_HI4` fields. These define the base page table pointer and valid logical address window for each VM context.

`VMSHAREDPF0_*` covers PF-shared host bridge and memory mapping controls: NB MMIO base/limit, PCI MMIO enable, VGA hole, top-of-DRAM slots, framebuffer offset, default system aperture address, steering, PF/VF reset request, memory light-sleep timing, cacheable DRAM aperture, local HBM aperture with lock control, and XGMI local framebuffer region/size fields. It also includes shorter unprefixed `MC_VM_XGMI_LFB_CNTL/SIZE` aliases with slightly narrower masks than the `VMSHAREDPF0` versions.

`VMSHAREDVC0_*` defines shared VC framebuffer, AGP, and system aperture bounds plus `MC_VM_MX_L1_TLB_CNTL`. The L1 TLB control fields enable the L1 TLB, select system access mode, configure unmapped aperture behavior, enable advanced driver model behavior, set ECO/MTYPE bits, and enable ATC.

`VMSHAREDHV0_*` is the hypervisor-facing virtualization block. It includes per-VF framebuffer size/offset registers for VF0-VF15, IOMMU MMIO/control/performance enables, four MARC base/relocation/length register groups, PF and VF PCIe ATS enable controls, UTCL2 clock-gating overrides, active function ID reporting, and per-PF/VF XGMI GPU IOV enable bits.

`ATCL2PFCNTR0` and `ATCL2PFCNTL0` define ATC L2 performance counter result and configuration fields. Config registers have `PERF_SEL`, `PERF_SEL_END`, `PERF_MODE`, `ENABLE`, and `CLEAR`; result control has counter select, start/stop trigger fields, enable-any, clear-all, and stop-on-saturate.

`VML2PL0` and `VML2PR0` define VM L2 performance counter control/result fields. `VML2PL0_MC_VM_L2_PERFCOUNTER0_CFG` through `7_CFG` mirror the ATC counter config shape, while `VML2PR0_MC_VM_L2_PERFCOUNTER_LO/HI` expose 48-bit counter result pieces plus a high-register compare value.

`DAGB5_RDCLI0..15` and `DAGB5_WRCLI0..15` repeat the same client arbitration layout for 16 read clients and 16 write clients: virtual channel selection, TLB-credit checking, high/low urgency thresholds, max/min bandwidth enable and value fields, OSD limiter enable, and maximum outstanding request count. The repeated layout is likely consumed by indexed setup code or table-driven initialization even though this header does not provide arrays.

`DAGB5_RD_CNTL/WR_CNTL`, `*_GMI_CNTL`, `*_ADDR_DAGB`, `*_OUTPUT_DAGB_MAX_BURST`, and `*_OUTPUT_DAGB_LAZY_TIMER` configure global read/write arbitration policy: SCLK frequency bucket, client/VC bandwidth windows, IO level override and compliance VC, shared VC count, EA credit, GMI burst and lazy timer, DAGB enable/jump-ahead/self-init/identity, and per-VC output burst/timer nibbles.

`DAGB5_RD_VC0..7_CNTL`, present for read-side VCs in this chunk, configures per-VC storage credit, EA credit, max/min bandwidth, OSD limiting, and max outstanding requests. The write-side VC-specific section is not fully present before line 28443, so cross-chunk reconciliation should check subsequent chunks for matching `DAGB5_WR_VC*` definitions.

`DAGB5_*_CGTT_CLK_CTRL`, `DAGB5_L1TLB_*_CGTT_CLK_CTRL`, and `DAGB5_ATCVM_*_CGTT_CLK_CTRL` provide clock-gating and light-sleep override fields for read/write DAGB, L1 TLB, and ATC VM sub-blocks. They define on delay, off hysteresis, soft-stall override, and LS override bits for write/read/return/register paths.

## Control Flow and State

This chunk has no executable flow. Its implicit flow is the hardware protocol encoded by the fields:

1. Driver code programs VM context page table base/start/end values.
2. It enables shared apertures, L1 TLB/ATC/IOMMU/ATS, PF/VF mappings, XGMI IOV, and arbitration policy as appropriate for the ASIC and virtualization mode.
3. On mapping changes, it writes a `VML2VC0_VM_INVALIDATE_ENG*_REQ` value, optionally with address range registers, then observes the matching `*_ACK` bits.
4. Diagnostic or profiling code programs `ATC_L2` or `VM_L2` perf counter config registers, starts/stops counting through result-control fields, and reads low/high result registers.

The state represented here persists in GPU hardware registers until reset, power management transitions, or later driver writes change it. Some fields are explicit transient controls (`CLEAR`, `CLEAR_ALL`, reset request bits, invalidate request bits), while others are durable configuration (`PAGE_TABLE_BASE`, aperture bounds, ATS enable, DAGB bandwidth controls). Because this is a generated mask header, persistence and ordering requirements must be enforced by the callers, not by this file.

## Dependencies and Integration Points

The macros depend only on the C preprocessor and fixed-width register semantics. They are typically paired with:

- register address headers for MMHUB 9.4.1, such as companion `mmhub_9_4_1_offset.h` or similar generated files;
- AMDGPU helpers/macros such as `REG_SET_FIELD`, `REG_GET_FIELD`, `WREG32`, `RREG32`, and indirect register accessors;
- MMHUB/GMC VM setup paths that program page tables, invalidation engines, apertures, ATS/IOMMU controls, and SR-IOV/XGMI virtualization;
- debugfs, perf, or tracing paths that read/write performance counter fields;
- power-management code that sets CGTT and light-sleep override controls.

The source path under `drivers/gpu/drm/amd/include/asic_reg/mmhub` indicates this is a Linux AMD GPU driver hardware-description dependency, not Ceph client logic despite the repository's broader `distributed-fs/ceph-client` tree.

## Risks

Bitfield correctness is critical. A wrong mask or shift in this file would silently write the wrong hardware bits, causing VM faults, stale TLB translations, broken ATS/IOMMU behavior, bad VF isolation, XGMI aperture exposure, arbitration starvation, or power-management hangs.

The chunk contains highly repetitive families. Copy-generation mistakes are especially plausible around numeric suffixes (`ENG*`, `CONTEXT*`, `VF*`, `RDCLI*`, `WRCLI*`) and boundary chunks. This chunk starts inside `ENG6_REQ` and ends inside the `DAGB5_WR_ADDR_DAGB_LAZY_TIMER0` block, so merge validation must preserve adjacent definitions from neighboring chunks.

Several register names encode privilege or isolation boundaries: `VMSHAREDHV0`, per-VF framebuffer offset/size, `ACTIVE_FCN_ID`, `PCIE_ATS_CNTL_VF_*`, and `MC_VM_XGMI_GPUIOV_ENABLE`. Incorrect usage by caller code can affect SR-IOV partitioning and address-translation isolation.

The `DAGB5` arbitration fields control credit, bandwidth, urgency, and outstanding request limits. Bad values may not fail immediately; they can surface as throughput regressions, latency spikes, starvation, or hangs under memory pressure.

The perf counter `CLEAR`, `CLEAR_ALL`, `ENABLE`, and stop-on-saturate bits are stateful hardware controls. Callers must avoid accidentally clearing counters while sampling and must account for split low/high reads.

## Test and Validation Signals

Useful validation signals are mostly integration-level because this header has no functions to unit test:

- Build coverage for AMDGPU code that includes MMHUB 9.4.1 register headers; missing or renamed macros should fail at compile time.
- Register readback tests or debug traces confirming that VM context base/start/end, aperture, ATS, XGMI IOV, and DAGB values land in expected bit positions after initialization.
- GPU VM stress tests that map/unmap buffers and verify `VML2VC0` invalidate request/ack behavior under multiple VMIDs and ranged invalidations.
- SR-IOV validation for VF framebuffer size/offset isolation, per-VF ATS enable, active function selection, PF/VF reset request handling, and XGMI GPU IOV enablement.
- IOMMU/ATS tests with PCIe ATS enabled/disabled and ATC/L1 TLB controls toggled according to platform support.
- Perf counter smoke tests that program ATC L2 and VM L2 event selectors, clear/start/stop counters, and verify monotonically plausible low/high result reads.
- Bandwidth and latency tests that exercise read/write DAGB client and VC settings, including OSD limiter, TLB-credit checking, urgency thresholds, max/min bandwidth windows, and clock-gating override behavior.

## Cross-Chunk Notes

This report covers only lines 25972-28443. Earlier chunks contain the beginning of the `VML2VC0_VM_INVALIDATE_ENG*` request family and likely broader VM L2 fault/control definitions. Later chunks should be checked for the remainder of `DAGB5_WR_ADDR_DAGB_LAZY_TIMER0`, write-side client 8-15 burst/timer registers, write VC controls, and subsequent DAGB or MMHUB blocks before producing the final per-file research document.

### subset-b-002853: lines 28444-30822

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mmhub/mmhub_9_4_1_sh_mask.h lines 28444-30822

## Scope And Purpose

This chunk is a middle section of the generated AMDGPU MMHUB 9.4.1 register shift/mask header. It covers the tail of `mmhub_dagb_dagbdec5`, the complete `mmhub_dagb_dagbdec6` mask block, and the start of `mmhub_dagb_dagbdec7` through the shift definitions for `DAGB7_RDCLI9`. The range contains 2,181 `#define` entries: 1,092 shift constants and 1,089 mask constants.

The file is not executable code. It is a hardware register-field contract for MMHUB DAGB arbitration and status registers. Callers include it with the matching offset header and use macros such as `REGISTER__FIELD__SHIFT` and `REGISTER__FIELD_MASK` through AMDGPU helpers like `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32_SOC15*`, and `WREG32_SOC15*`.

Within this chunk, the dominant purpose is to describe DAGB5 write-side completion controls, all DAGB6 read/write client arbitration controls, DAGB6 clock-gating, credit, pending, snoop override, FIFO, performance counter, and reserved registers, plus the beginning of DAGB7 read-client arbitration.

## Important APIs, Types, And Register Families

There are no local C functions, structs, enums, variables, or callable APIs in this chunk. The public interface is the macro namespace exported by `mmhub_9_4_1_sh_mask.h`.

Important covered register families include:

- `DAGB5_WR_ADDR_DAGB_MAX_BURST1`, `DAGB5_WR_ADDR_DAGB_LAZY_TIMER1`, `DAGB5_WR_DATA_DAGB`, `DAGB5_WR_DATA_DAGB_MAX_BURST[0-1]`, and `DAGB5_WR_DATA_DAGB_LAZY_TIMER[0-1]`: tail of DAGB5 write-address/write-data DAGB burst and lazy-timer programming. The max-burst and lazy-timer registers pack 4-bit client fields for clients 0-15 across low/high words.
- `DAGB5_WR_VC0_CNTL` through `DAGB5_WR_VC7_CNTL`: per-write-virtual-channel storage and EA credits, max/min bandwidth enable and values, OSD limiter enable, and max outstanding fields.
- `DAGB5_WR_CNTL_MISC`, `DAGB5_WR_TLB_CREDIT`, `DAGB5_WR_DATA_CREDIT`, and `DAGB5_WR_MISC_CREDIT`: write-side storage pool, EA pool, IO/EA, UTCL2 CID, RDRET FIFO, TLB, burst, atomic, DLOCK, and OSD credit packing.
- `DAGB5_WRCLI_*_PENDING`, `DAGB5_WRCLI_DBUS_*_PENDING`, `DAGB5_WRCLI_GPU_SNOOP_OVERRIDE`, and `DAGB5_WRCLI_GPU_SNOOP_OVERRIDE_VALUE`: full-width busy/status and snoop override bitmaps for write clients.
- `DAGB5_DAGB_DLY`, `DAGB5_CNTL_MISC`, `DAGB5_CNTL_MISC2`, FIFO/credit-full status, `DAGB5_PERFCOUNTER_*`, and `DAGB5_RESERVE0` through `DAGB5_RESERVE13`: delay selection, EA virtual-channel remap, bandwidth timing, urgent boost/halt, clock-gating disable bits, status fields, performance counters, and full-width reserved placeholders.
- `DAGB6_RDCLI0` through `DAGB6_RDCLI15` and `DAGB6_WRCLI0` through `DAGB6_WRCLI15`: per-client read/write controls. Each client uses the repeated layout `VIRT_CHAN`, `CHECK_TLB_CREDIT`, `URG_HIGH`, `URG_LOW`, `MAX_BW_ENABLE`, `MAX_BW`, `MIN_BW_ENABLE`, `MIN_BW`, `OSD_LIMITER_ENABLE`, and `MAX_OSD`.
- `DAGB6_RD_CNTL` and `DAGB6_WR_CNTL`: shared read/write arbitration controls for `SCLK_FREQ`, client and VC bandwidth windows, IO-level override and compliance fields, and shared VC count.
- `DAGB6_RD_GMI_CNTL` and `DAGB6_WR_GMI_CNTL`: GMI path credit, level, max-burst, and lazy-timer fields.
- `DAGB6_RD_ADDR_DAGB`, `DAGB6_WR_ADDR_DAGB`, and `DAGB6_WR_DATA_DAGB`: DAGB enable, jump-ahead enable, self-init disable, and `WHOAMI` fields for read address, write address, and write data paths.
- `DAGB6_RD_OUTPUT_DAGB_MAX_BURST`, `DAGB6_RD_OUTPUT_DAGB_LAZY_TIMER`, `DAGB6_WR_OUTPUT_DAGB_MAX_BURST`, and `DAGB6_WR_OUTPUT_DAGB_LAZY_TIMER`: 4-bit packed controls for output virtual channels 0-7.
- `DAGB6_RD_CGTT_CLK_CTRL`, `DAGB6_L1TLB_RD_CGTT_CLK_CTRL`, `DAGB6_ATCVM_RD_CGTT_CLK_CTRL`, `DAGB6_WR_CGTT_CLK_CTRL`, `DAGB6_L1TLB_WR_CGTT_CLK_CTRL`, and `DAGB6_ATCVM_WR_CGTT_CLK_CTRL`: clock/light-sleep controls with on-delay, off-hysteresis, soft-stall override, and light-sleep override bits for normal, L1TLB, and ATCVM read/write paths.
- `DAGB6_RD_ADDR_DAGB_MAX_BURST[0-1]`, `DAGB6_RD_ADDR_DAGB_LAZY_TIMER[0-1]`, `DAGB6_WR_ADDR_DAGB_MAX_BURST[0-1]`, `DAGB6_WR_ADDR_DAGB_LAZY_TIMER[0-1]`, `DAGB6_WR_DATA_DAGB_MAX_BURST[0-1]`, and `DAGB6_WR_DATA_DAGB_LAZY_TIMER[0-1]`: packed 4-bit per-client controls for clients 0-15.
- `DAGB6_RD_VC0_CNTL` through `DAGB6_RD_VC7_CNTL` and `DAGB6_WR_VC0_CNTL` through `DAGB6_WR_VC7_CNTL`: per-VC credit, bandwidth, OSD limiter, and max outstanding request controls.
- `DAGB6_RD_CNTL_MISC`, `DAGB6_WR_CNTL_MISC`, `DAGB6_RD_TLB_CREDIT`, `DAGB6_WR_TLB_CREDIT`, `DAGB6_WR_DATA_CREDIT`, and `DAGB6_WR_MISC_CREDIT`: pool and per-resource credit registers. TLB credits use packed 5-bit fields for TLB0-TLB5; data and misc credits use larger packed byte or sub-byte fields.
- `DAGB6_RDCLI_*_PENDING`, `DAGB6_WRCLI_*_PENDING`, and `DAGB6_WRCLI_DBUS_*_PENDING`: full-width `BUSY` bitmaps for ask, go, global-send, TLB, output-arbiter, OSD, and data-bus pending states.
- `DAGB6_WRCLI_GPU_SNOOP_OVERRIDE` and `DAGB6_WRCLI_GPU_SNOOP_OVERRIDE_VALUE`: full-width write-client snoop override enable/value bitmaps.
- `DAGB6_DAGB_DLY`, `DAGB6_CNTL_MISC`, and `DAGB6_CNTL_MISC2`: delay injection selection, EA VC remapping, bandwidth initialization/gap timing, urgent boost/halt, clock-gating disable flags, EA request busy suppression flags, swap control, RDRET FIFO performance, and DLOCK credit fields.
- `DAGB6_FIFO_EMPTY`, `DAGB6_FIFO_FULL`, `DAGB6_WR_CREDITS_FULL`, and `DAGB6_RD_CREDITS_FULL`: status bitfields for FIFO and credit conditions.
- `DAGB6_PERFCOUNTER_LO`, `DAGB6_PERFCOUNTER_HI`, `DAGB6_PERFCOUNTER0_CFG` through `DAGB6_PERFCOUNTER2_CFG`, and `DAGB6_PERFCOUNTER_RSLT_CNTL`: low/high counter words, compare value, event select ranges, modes, enable/clear bits, start/stop triggers, enable-any, clear-all, and stop-on-saturate controls.
- `DAGB6_RESERVE0` through `DAGB6_RESERVE13`: generated full-width reserved register field masks.
- `DAGB7_RDCLI0` through the shift-only portion of `DAGB7_RDCLI9`: beginning of DAGB7 read-client controls with the same field layout as DAGB6 read clients. The `DAGB7_RDCLI9` masks are just outside this chunk, so the merge lane should treat that register as split.

## Control Flow And State Behavior

This chunk has no runtime control flow. All behavior occurs when other AMDGPU code expands these constants into register read/modify/write or decode operations.

The state represented by these macros lives in MMHUB hardware registers. Configuration fields affect DAGB routing and quality of service: virtual-channel selection, TLB-credit checks, urgency thresholds, max/min bandwidth limiting, outstanding request limiting, burst sizing, lazy timers, GMI crediting, and data/address DAGB enablement. Clock control and `CNTL_MISC2` fields affect power and clock-gating behavior. Snoop override bitmaps affect how write clients participate in GPU snooping. Pending/FIFO/credit fields expose live hardware status, and performance counter fields control or report hardware counters.

Persistence is hardware-local. Register values remain until reset, power-gating, firmware initialization, or driver programming changes them. This header does not cache values, serialize access, distinguish read-only status from writable controls, or validate legal field values.

## Dependencies And Integration Points

The immediate companion is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mmhub/mmhub_9_4_1_offset.h`. Its matching `mmhub_dagb_dagbdec6` block gives base address `0x74200`, `mmDAGB6_RDCLI0` at `0x3080`, `mmDAGB6_WRCLI0` at `0x30ac`, `mmDAGB6_WR_DATA_DAGB` at `0x30c8`, `mmDAGB6_CNTL_MISC2` at `0x30e7`, and `mmDAGB6_PERFCOUNTER_LO` at `0x30ec`. The same offset file starts `mmhub_dagb_dagbdec7` at base address `0x74400`, with `mmDAGB7_RDCLI0` at `0x3100` and `mmDAGB7_RDCLI9` at `0x3109`.

`sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mmhub/mmhub_9_4_1_default.h` supplies default values for the same register names, including `mmDAGB6_RDCLI0_DEFAULT`, `mmDAGB6_WRCLI0_DEFAULT`, `mmDAGB6_CNTL_MISC_DEFAULT`, `mmDAGB6_CNTL_MISC2_DEFAULT`, and the DAGB6 performance counter defaults. Those defaults are useful for reset-state comparison and for checking whether runtime programming diverges from generated expectations.

The principal source consumer is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/mmhub_v9_4.c`, which includes the 9.4.1 offset, shift/mask, and default headers. That implementation mostly uses VM, aperture, protection fault, and RAS fields from the same header family, but it also depends on the DAGB register layout:

- `mmhub_v9_4_init_system_aperture_regs()` iterates DAGB instances and writes `mmDAGB0_WRCLI_GPU_SNOOP_OVERRIDE` and `mmDAGB0_WRCLI_GPU_SNOOP_OVERRIDE_VALUE` with a stride computed from `mmDAGB1_WRCLI_GPU_SNOOP_OVERRIDE - mmDAGB0_WRCLI_GPU_SNOOP_OVERRIDE`. The comments state DAGB instances 0-4 are in hub0 and 5-7 are in hub1, so the DAGB5-DAGB7 macros in this chunk are part of that instance family.
- `mmhub_v9_4_update_medium_grain_clock_gating()` computes a DAGB stride from `mmDAGB1_CNTL_MISC2 - mmDAGB0_CNTL_MISC2` and toggles `DAGB0_CNTL_MISC2__DISABLE_WRREQ_CG_MASK`, `DISABLE_WRRET_CG_MASK`, `DISABLE_RDREQ_CG_MASK`, `DISABLE_RDRET_CG_MASK`, `DISABLE_TLBWR_CG_MASK`, and `DISABLE_TLBRD_CG_MASK` across DAGB instances. The masks are named for DAGB0 but share the same layout as the DAGB5 and DAGB6 `CNTL_MISC2` masks in this chunk.

Although this repository path is under a Ceph client source import, this header is Linux AMDGPU DRM hardware-interface data. It has no Ceph filesystem semantics.

## Risks And Edge Cases

- These macros are a hardware ABI. A wrong shift or mask can silently program the wrong MMIO field while still compiling, affecting MMHUB arbitration, memory traffic fairness, snooping, clock gating, or diagnostics.
- The chunk is highly repetitive. DAGB6 read/write client macros repeat 16 times each, VC controls repeat 8 times for read and write, and burst/lazy timers repeat packed client lanes. Generator drift in one client or VC can be hard to notice by visual review.
- Packed fields require read-modify-write discipline. Client burst/lazy timers use 4-bit lanes, TLB credits use 5-bit lanes, VC controls pack several unrelated controls into one word, and status registers often use full-width or near-full-width bitmaps.
- Full-width masks such as `0xFFFFFFFFL` should be handled as 32-bit register masks. Signed promotion or wrong diagnostic formatting can make register dumps misleading on some build targets.
- Status and control registers use the same macro style. Pending, FIFO, credit-full, performance-counter result, and reserved fields may be read-only or side-effectful according to the hardware specification; this header does not encode access permissions.
- `DAGB*_CNTL_MISC2` and `*_CGTT_CLK_CTRL` fields are not passive metadata. Incorrect writes can disable clock gating, force/suppress busy behavior, or change light-sleep override behavior.
- `WRCLI_GPU_SNOOP_OVERRIDE` and `WRCLI_GPU_SNOOP_OVERRIDE_VALUE` are full-client bitmaps. A bad bit position or instance stride can affect an unrelated write client or DAGB instance.
- The chunk boundary splits context in both directions: it starts after the first `DAGB5_WR_ADDR_DAGB_LAZY_TIMER0` definitions and ends before the `DAGB7_RDCLI9` masks. The final per-file merge should reconcile adjacent chunks before making whole-register claims for those boundary registers.

## Test And Validation Signals

There are no direct unit tests for this macro-only range. Useful validation signals are compile-time, generated-data, and hardware-observation based:

- Build AMDGPU code that includes `mmhub_9_4_1_sh_mask.h`, especially `amdgpu/mmhub_v9_4.c`, to catch missing or renamed register-field macros.
- Run static consistency checks over this chunk: each `__SHIFT` should have the expected paired `_MASK`, masks should be contiguous for multi-bit fields, single-bit masks should match their shifts, and fields inside one register should not overlap.
- Cross-check covered register groups with `mmhub_9_4_1_offset.h`: every complete `DAGB6_*` register group in this chunk should have a corresponding `mmDAGB6_*` offset/base-index entry, and the DAGB7 partial group should align with the offset block that starts at `mmDAGB7_RDCLI0`.
- Compare generated defaults in `mmhub_9_4_1_default.h` against reset-time hardware dumps for `DAGB6_RDCLI*`, `DAGB6_WRCLI*`, `DAGB6_CNTL_MISC*`, FIFO/credit status, and performance counter registers.
- On MMHUB 9.4.1 hardware or simulator, validate that clock-gating updates in `mmhub_v9_4_update_medium_grain_clock_gating()` affect all intended DAGB instances and preserve unrelated `CNTL_MISC2` bits.
- Exercise GPU snoop override programming in `mmhub_v9_4_init_system_aperture_regs()` and inspect `DAGB5` through `DAGB7` register dumps to confirm the computed instance stride selects the expected registers.
- For diagnostic/performance paths, verify counter enable, clear, select, trigger, high/low reads, and stop-on-saturate behavior without leaving clear bits or trigger state unexpectedly asserted.

## Chunk Notes For Merge Lane

This is chunk 13 of 19 for `mmhub_9_4_1_sh_mask.h`. It should be merged with chunk 12 for the beginning of the DAGB5 write-address lazy-timer register and with chunk 14 for the remainder of `DAGB7_RDCLI9` plus later DAGB7 registers. The complete per-file report should describe this as part of the generated MMHUB 9.4.1 register mask namespace rather than as standalone driver logic.

### subset-b-002854: lines 30823-33173

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mmhub/mmhub_9_4_1_sh_mask.h lines 30823-33173

## Purpose

This chunk is generated AMDGPU MMHUB 9.4.1 register field metadata. It supplies `__SHIFT` and `_MASK` preprocessor constants for two adjacent hardware register regions:

- The tail of `addressBlock: mmhub_dagb_dagbdec7`, covering late `DAGB7_RDCLI9` masks, `DAGB7_RDCLI10` through `DAGB7_RDCLI15`, the full `DAGB7` read/write control sets, pending/status registers, snoop override controls, delay/miscellaneous controls, FIFO/credit status, performance counters, and reserved registers.
- The start of `addressBlock: mmhub_ea_mmeadec5`, covering `MMEA5` DRAM and GMI client-to-group mapping, group-to-virtual-channel mapping, lazy request accumulation, CAM/reorder controls, page-burst limits, priority aging/queuing/fixed/urgency weights, urgency masking, and quantization thresholds through the first shift macro for `MMEA5_GMI_RD_PRI_QUANT_PRI3`.

The macros let driver code manipulate specific bitfields inside 32-bit SOC15 MMHUB registers without hard-coding bit positions. The matching register offsets live in `mmhub_9_4_1_offset.h`, and reset/default values live in `mmhub_9_4_1_default.h`.

## Important APIs, Types, And Data

The chunk defines no C functions, structs, enums, storage, or runtime APIs. Its interface is the macro namespace consumed by register access helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `SOC15_REG_FIELD`, `RREG32_SOC15_OFFSET`, and `WREG32_SOC15_OFFSET`.

Important `DAGB7` field groups include:

- `DAGB7_RDCLI*` and `DAGB7_WRCLI*` client arbitration fields: `VIRT_CHAN`, `CHECK_TLB_CREDIT`, `URG_HIGH`, `URG_LOW`, `MAX_BW_ENABLE`, `MAX_BW`, `MIN_BW_ENABLE`, `MIN_BW`, `OSD_LIMITER_ENABLE`, and `MAX_OSD`.
- `DAGB7_RD_CNTL` and `DAGB7_WR_CNTL`: clock/window and IO-level controls such as `SCLK_FREQ`, max bandwidth windows, `IO_LEVEL_OVERRIDE_ENABLE`, `IO_LEVEL`, `IO_LEVEL_COMPLY_VC`, and `SHARE_VC_NUM`.
- GMI and DAGB output controls: `EA_CREDIT`, `LEVEL`, `MAX_BURST`, `LAZY_TIMER`, `DAGB_ENABLE`, jump-ahead/self-init controls, per-virtual-channel burst and lazy timer values, and read/write data DAGB enables.
- Clock-gating test/toggle controls for read/write, L1 TLB, and ATCVM paths: `SOFT_OVERRIDE`, `STOP`, `RESERVED`, `MISC`, and `REG_IDLE`.
- Virtual-channel controls for `RD_VC0..7` and `WR_VC0..7`: `MAX_BW_ENABLE`, `MAX_BW`, `MIN_BW_ENABLE`, `MIN_BW`, `MAX_OSD`, and `INTERLEAVE_DISABLE`.
- Status and telemetry fields: read/write pending bits, `FIFO_EMPTY`, `FIFO_FULL`, write/read credit-full bitmaps, 48-bit style performance counter low/high fields, three perf-counter config registers, and result-control triggers.
- `DAGB7_CNTL_MISC2` fields used by local driver code for DAGB clock gating: `DISABLE_WRREQ_CG`, `DISABLE_WRRET_CG`, `DISABLE_RDREQ_CG`, `DISABLE_RDRET_CG`, `DISABLE_TLBWR_CG`, and `DISABLE_TLBRD_CG`.

Important `MMEA5` field groups include:

- `MMEA5_{DRAM,GMI}_{RD,WR}_CLI2GRP_MAP0/1`: 2-bit `CID0..CID31_GROUP` mappings that bucket clients into four arbitration groups.
- `MMEA5_{DRAM,GMI}_{RD,WR}_GRP2VC_MAP`: 3-bit `GROUP0..3_VC` mappings that route arbitration groups to virtual channels.
- `MMEA5_{DRAM,GMI}_{RD,WR}_LAZY`: per-group delay plus `REQ_ACCUM_THRESH`, `REQ_ACCUM_TIMEOUT`, and `REQ_ACCUM_IDLEMAX`.
- `MMEA5_{DRAM,GMI}_{RD,WR}_CAM_CNTL`: per-group CAM depths, per-group reorder limits, and `REFILL_CHAIN`.
- `MMEA5_{DRAM,GMI}_PAGE_BURST`: byte-wide read/write low/high page-burst limits.
- Priority controls for read/write DRAM and GMI paths: aging rates, age coefficients, queuing coefficients, fixed coefficients, urgency coefficients, urgency modes, 32-bit client urgency masks, and byte-wide quantization thresholds.

## Control Flow

There is no executable control flow in this header fragment. The compile-time flow is simple macro expansion:

1. A C file includes `mmhub_9_4_1_offset.h`, `mmhub_9_4_1_sh_mask.h`, and usually `mmhub_9_4_1_default.h`.
2. Callers pass a register name and field name to helper macros such as `REG_SET_FIELD(reg, DAGB0_CNTL_MISC2, DISABLE_WRREQ_CG, value)` or `SOC15_REG_FIELD(MMEA5_EDC_CNT2, GMIRD_CMDMEM_SEC_COUNT)`.
3. The helper composes or extracts bitfields using the `REGISTER__FIELD__SHIFT` and `REGISTER__FIELD_MASK` constants from this header.
4. SOC15 register helpers read or write the actual MMHUB register selected by the sibling offset header.

The local driver file `drivers/gpu/drm/amd/amdgpu/mmhub_v9_4.c` includes this header directly. Its visible use of this chunk is mainly through the `DAGB*_CNTL_MISC2` mask pattern in clock-gating code: it calculates spacing between `mmDAGB0_CNTL_MISC2` and `mmDAGB1_CNTL_MISC2`, iterates across DAGB instances, and clears or sets the `DISABLE_*_CG_MASK` bits before writing each instance. The same file also programs DAGB snoop override registers using offsets from this register family, although the SDMA client bit is currently manipulated as a literal bit rather than via this header's full-width `ENABLE` mask.

## State And Persistence Behavior

The macros themselves are stateless build-time constants. The state they describe is MMHUB hardware register state:

- DAGB client arbitration registers control virtual-channel assignment, urgency thresholds, min/max bandwidth shaping, outstanding-request limits, and TLB-credit checks for the eighth DAGB instance.
- DAGB read/write control, GMI control, address/data DAGB, virtual-channel, and miscellaneous fields influence how MMHUB read/write traffic is routed, delayed, interleaved, clock-gated, and throttled.
- DAGB pending, FIFO, credit-full, and performance-counter fields expose volatile hardware status and telemetry. Counter values can advance, clear, saturate, or wrap depending on hardware behavior and perf-counter control bits.
- MMEA5 DRAM/GMI arbitration fields persist current routing and priority policy for that MMEA instance until reset or reprogramming. They determine client grouping, group-to-VC routing, request accumulation, reorder depth, burst limiting, and priority calculations.
- Default policy values are mirrored in `mmhub_9_4_1_default.h`; for example, DAGB7 client defaults use values such as `0xfe5fe0f9`, DAGB7 perf counters default to zero, MMEA5 DRAM/GMI priority defaults use patterns such as `0x00db6249`, `0x00000db6`, `0x00000924`, `0x0000fdb6`, and quantization defaults use `0x3f3f3f3f`, `0x7f7f7f7f`, and `0xffffffff`.

No filesystem persistence or software cache is implemented here. Durable behavior comes from hardware reset defaults, firmware/platform initialization, and driver writes during MMHUB setup, suspend/resume, clock-gating changes, or diagnostics.

## Dependencies

This chunk depends on the generated MMHUB 9.4.1 register set remaining internally consistent:

- `mmhub_9_4_1_offset.h` provides the `mmDAGB7_*` and `mmMMEA5_*` register addresses and base indices. The range covered here maps, for example, `mmDAGB7_RDCLI10` at `0x310a` through `mmDAGB7_RESERVE13`, then `mmMMEA5_DRAM_RD_CLI2GRP_MAP0` through `mmMMEA5_GMI_RD_PRI_QUANT_PRI3`.
- `mmhub_9_4_1_default.h` provides reset/default values for the same register names.
- `soc15.h`/AMDGPU register helpers provide the field manipulation and MMIO access macros that consume the shift/mask definitions.
- `mmhub_v9_4.c` provides the main local integration point for MMHUB 9.4 initialization, VM hub programming, snoop override setup, clock gating, RAS counters, and MMHUB fault handling.

The macro names are ASIC-generation-specific. Similar MMEA and DAGB names exist in `mmhub_1_7_*` headers with different base indices and register addresses, so cross-generation code must include the correct header rather than sharing numeric literals.

## Integration Points

Primary integration points are:

- MMHUB v9.4 driver initialization in `drivers/gpu/drm/amd/amdgpu/mmhub_v9_4.c`, which includes this header and uses its field masks for `REG_SET_FIELD`, `REG_GET_FIELD`, and direct mask operations.
- SOC15 register access macros that pair this file's field-level constants with the sibling offset constants for actual MMIO reads and writes.
- Clock-gating control for DAGB instances, where `DAGB0_CNTL_MISC2__DISABLE_*_CG_MASK` defines the same field layout repeated for `DAGB7_CNTL_MISC2`.
- Snoop override setup for DAGB write clients, tied to `DAGB7_WRCLI_GPU_SNOOP_OVERRIDE` and `DAGB7_WRCLI_GPU_SNOOP_OVERRIDE_VALUE` offsets and their full-width enable masks.
- MMHUB performance and debug tooling that can select DAGB7 performance events, clear counters, enable counters, read low/high counter values, and apply result triggers.
- RAS and diagnostics infrastructure for MMEA instances. `mmhub_v9_4.c` contains MMEA error-counter tables for instances 0 through 7; while those tables target `MMEA*_EDC_CNT*`, they share the same generated MMEA register namespace and SOC15 field extraction mechanism as the arbitration fields in this chunk.

## Risks

- A wrong shift or mask can corrupt unrelated bits in a hardware register, changing traffic routing, QoS, clock-gating, snoop, or performance-counter behavior.
- This chunk starts and ends mid-register-block: it begins with the mask half of `DAGB7_RDCLI9` and ends after only `MMEA5_GMI_RD_PRI_QUANT_PRI3__GROUP0_THRESHOLD__SHIFT`. Consumers and merge tooling must reconcile adjacent chunks before treating the whole source file as documented.
- DAGB and MMEA layouts are highly repetitive across instances. Copying a field name from the wrong instance or ASIC family can compile but program the wrong register or use the wrong base index.
- Bandwidth, urgency, virtual-channel, lazy-timer, and reorder-limit fields directly affect memory-system scheduling. Bad values can cause unfairness, latency spikes, throughput loss, or hardware hangs under load.
- Full-width masks such as pending bitmaps, urgency masks, snoop override enables, and reserve fields are easy to overwrite accidentally if code performs raw writes instead of masked read-modify-write operations.
- Performance counters and status registers are volatile. Tests that compare exact values need to account for counter progression, clear bits, saturation, and wraparound.
- Reserved register masks are exposed as full-width constants, but writing reserved registers or reserved bits may be unsafe unless explicitly required by hardware documentation.

## Test Signals

Useful validation signals include:

- Build coverage for `amdgpu` code that includes `mmhub_9_4_1_sh_mask.h` with `mmhub_9_4_1_offset.h` and `mmhub_9_4_1_default.h`.
- Static consistency checks that every `DAGB7_*` and `MMEA5_*` field block in this line range has matching offset/default entries where expected, and that each mask aligns with its shift and field width.
- Clock-gating tests on MMHUB v9.4 hardware that toggle medium/light clock gating and confirm `DAGB*_CNTL_MISC2` disable bits change as expected without breaking MMHUB traffic.
- Snoop override validation that SDMA write snoop behavior remains correct when DAGB write-client override registers are programmed.
- MMHUB stress tests with read/write traffic over DRAM and GMI paths to expose regressions in client grouping, virtual-channel assignment, lazy accumulation, CAM reorder limits, page-burst limits, and priority policy.
- Perf-counter smoke tests that configure `DAGB7_PERFCOUNTER*_CFG`, enable/clear counters through `DAGB7_PERFCOUNTER_RSLT_CNTL`, run traffic, and observe plausible `PERFCOUNTER_LO/HI` deltas.
- RAS and fault-injection testing on MMHUB v9.4 devices to ensure generated field metadata remains compatible with MMEA diagnostics and does not break existing error-counter extraction paths.

### subset-b-002855: lines 33174-35538

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mmhub/mmhub_9_4_1_sh_mask.h lines 33174-35538

## Scope

This chunk covers generated shift and mask macros from the AMD MMHUB 9.4.1 register mask header. It starts in the `MMEA5_GMI_RD_PRI_QUANT_PRI3` priority threshold fields, covers the remainder of the `mmhub_ea_mmeadec5` register field map, and ends partway through the initial `mmhub_ea_mmeadec6` DRAM CAM control fields. The range contains only C preprocessor definitions and register-block comments. There are no functions, structs, variables, runtime branches, allocations, locks, or persistent software data structures in this chunk.

The main register families covered are:

- `MMEA5_GMI_*` read/write priority quantum threshold registers.
- `MMEA5_ADDRNORM*` range, hole, interleave, non-power-of-two channel, and global hash-control registers.
- `MMEA5_ADDRDEC*` bank, channel, chip-select, row/column, hash, harvest, and address selection fields for DRAM and GMI address decode.
- `MMEA5_IO_*` client-to-group, combine flush, burst, priority, urgency, and quantum fields for IO traffic.
- `MMEA5_SDP_*` arbitration, priority, credit, tag reserve, virtual-channel reserve, and request-control fields.
- `MMEA5_MISC`, latency sampling, performance counter, EDC, DSM, clock-gating, error-status, and address-decoder select fields.
- The beginning of `MMEA6_DRAM_*` QoS fields: client-to-group maps, group-to-VC maps, lazy accumulation, and read/write CAM depth/reorder controls.

## Purpose

`mmhub_9_4_1_sh_mask.h` is the bitfield layout companion for MMHUB 9.4.1 registers. For each hardware register field, it exposes the conventional generated pair:

- `<REGISTER>__<FIELD>__SHIFT`, the field's bit position.
- `<REGISTER>__<FIELD>_MASK`, the field's 32-bit mask.

The sibling `mmhub_9_4_1_offset.h` header supplies register addresses, while `mmhub_9_4_1_default.h` supplies reset/default values. `amdgpu/mmhub_v9_4.c` includes all three headers and uses the same register helper style (`RREG32_SOC15`, `RREG32_SOC15_OFFSET`, `WREG32_SOC15_OFFSET`, `REG_SET_FIELD`) to compose and access MMHUB registers. This specific chunk is mostly hardware contract data for address decoding and QoS scheduling, even if many of these fields are not directly referenced by open-coded initialization paths in `mmhub_v9_4.c`.

## Important Macro Families

### GMI Priority Quantum Fields

The chunk begins with `MMEA5_GMI_RD_PRI_QUANT_PRI3` and then defines `MMEA5_GMI_WR_PRI_QUANT_PRI1..3`. Each register packs four 8-bit group thresholds at shifts `0x0`, `0x8`, `0x10`, and `0x18`, with masks covering each byte. The matching defaults in `mmhub_9_4_1_default.h` are `0x3f3f3f3f`, `0x7f7f7f7f`, and `0xffffffff` for priority levels 1 through 3. These fields describe traffic aging/threshold behavior for GMI read/write priority arbitration.

### Address Normalization

`MMEA5_ADDRNORM_BASE_ADDR0..5`, `LIMIT_ADDR0..5`, and `OFFSET_ADDR1/3/5` describe address normalization windows. Base registers include:

- `ADDR_RNG_VAL`, enabling a range.
- `LGCY_MMIO_HOLE_EN`, handling legacy MMIO hole behavior.
- `INTLV_NUM_CHAN`, `INTLV_NUM_DIES`, `INTLV_NUM_SOCKETS`, and `INTLV_ADDR_SEL`, describing interleave topology.
- `BASE_ADDR`, using the high 20 bits of the register.

Limit registers pair `DST_FABRIC_ID` with `LIMIT_ADDR`. Offset registers provide `HI_ADDR_OFFSET_EN` and high-address offset fields. The default header initializes these ranges and holes to zero, which means firmware or platform-specific setup must program meaningful topology before hardware uses the ranges.

The chunk also covers DRAM and GMI hole controls, non-power-of-two channel configuration, and global hash interleave controls. The DRAM/GMI variants are parallel: the same logical field names are repeated for separate DRAM and GMI paths, so mismatched edits between those families would create asymmetric address routing.

### Address Decode and Hashing

`MMEA5_ADDRDEC_BANK_CFG` and `MMEA5_ADDRDEC_MISC_CFG` configure bank masks, bank-group selection/interleave, VCM enables, physical channel masks, channel masks, chip-select masks, and rank-mask fields. The DRAM and GMI hash families then expose XOR-enable and XOR input selections for bank, pseudo-channel, and chip-select hashing:

- `MMEA5_ADDRDECDRAM_ADDR_HASH_BANK0..5`, `PC`, `PC2`, `CS0`, `CS1`, and `HARVEST_ENABLE`.
- `MMEA5_ADDRDECGMI_ADDR_HASH_BANK0..5`, `PC`, `PC2`, `CS0`, `CS1`, and `HARVEST_ENABLE`.

The hash bank fields split into `XOR_ENABLE`, `COL_XOR`, and `ROW_XOR`. Chip-select hashes use `NA_XOR` after the enable bit. Harvest-enable fields can force bank bits B3/B4/B5 to fixed values, likely to hide harvested or unavailable memory resources.

### Per-Decoder Chip-Select Layout

The chunk defines repeated `MMEA5_ADDRDEC0`, `ADDRDEC1`, and `ADDRDEC2` families. Each decoder includes:

- Base address registers for `CS0..CS3` and secondary chip selects `SECCS0..SECCS3`, with `CS_EN` and `BASE_ADDR`.
- Address mask registers for `CS01`, `CS23`, `SECCS01`, and `SECCS23`.
- Address configuration registers defining bank-group count, rank-mask count, row-low/high widths, column width, bank count, and high-column enable.
- Address selection registers mapping bank bits, row low/high bits, and the sixth bank bit.
- Column selection low/high registers mapping `COL0..COL15`.
- Rank-mask selection registers for primary and secondary chip-select pairs, including rank-map inputs, channel-bit selection, and row-MSB inversion controls.

The repeated structure is important: driver or firmware code can derive programming loops over decoder instances, but the actual ABI is still a flat macro namespace. Any automated update must preserve identical field layouts across decoder 0, 1, and 2 unless the hardware spec intentionally diverges.

### IO QoS and Priority Control

`MMEA5_IO_RD_CLI2GRP_MAP0/1` and `MMEA5_IO_WR_CLI2GRP_MAP0/1` pack 32 client IDs into two registers, with two bits per client selecting group 0 through 3. `MMEA5_IO_RD_COMBINE_FLUSH` and `WR_COMBINE_FLUSH` contain four group timers and a `FORWARD_COMB_ONLY` bit. `MMEA5_IO_GROUP_BURST` defines read/write low/high burst limits.

The IO priority registers mirror common QoS math:

- `*_PRI_AGE` has four aging-rate fields and four age-coefficient fields.
- `*_PRI_QUEUING`, `*_PRI_FIXED`, and `*_PRI_URGENCY` provide per-group queue, fixed, and urgency coefficients.
- `*_PRI_URGENCY` also has per-group urgency mode bits.
- `*_PRI_URGENCY_MASKING` has one mask bit per client ID.
- `*_PRI_QUANT_PRI1..3` has four 8-bit group thresholds per priority level.

The defaults show the intended reset policy: client-to-group maps default to `0xe4e4e4e4`, priority coefficients have non-zero tuned defaults, urgency masks default to all ones, and priority quantum registers follow the same `0x3f`, `0x7f`, `0xff` threshold pattern used by GMI.

### SDP Arbitration and Reservations

`MMEA5_SDP_ARB_DRAM`, `MMEA5_SDP_ARB_GMI`, and `MMEA5_SDP_ARB_FINAL` define arbitration score thresholds, score update factors, winners, and arbiter behavior across DRAM, GMI, and final arbitration stages. The priority registers (`MMEA5_SDP_DRAM_PRIORITY`, `GMI_PRIORITY`, `IO_PRIORITY`) expose four per-target priority fields.

`MMEA5_SDP_CREDITS`, `TAG_RESERVE0/1`, `VCC_RESERVE0/1`, and `VCD_RESERVE0/1` manage return/data credit and reserved tag/virtual-channel capacity. `MMEA5_SDP_REQ_CNTL` exposes per-source request enable bits for DRAM, GMI, both SDP subpaths, and IO. These fields are integration points for bandwidth and fairness tuning between memory paths.

### Miscellaneous, Observability, and Error Fields

`MMEA5_MISC` contains a dense set of mode bits and limits: dynamic credit handling, XGMI flags, page-flip and channel width settings, atomic/datapath modes, credit counters, delay/disable knobs, and forced-partial-read behavior. `MMEA5_LATENCY_SAMPLING` configures sampling enable, select, masks, IDs, timer, and threshold. `MMEA5_PERFCOUNTER_*` exposes low/high counters, event selectors, clear/select fields, and result-control options.

`MMEA5_EDC_CNT`, `EDC_CNT2`, `EDC_CNT3`, and `EDC_MODE` provide error-detection counters, clear bits, count selectors, read/write data access, and disable flags. `MMEA5_ERR_STATUS` distinguishes correctable and uncorrectable error status, validity, logging, and clear bits. DSM and clock controls (`DSM_CNTL*`, `CGTT_CLK_CTRL`) define memory power/clock gating behavior. `MMEA5_ADDRDEC_SELECT` selects DRAM and GMI address decoders.

These registers are stateful hardware controls or counters. The macros do not persist anything by themselves, but writes through the MMIO helpers program persistent hardware state until reset or reprogramming; status and counter fields represent hardware-maintained state.

### MMEA6 DRAM QoS Start

At line 35331 the chunk enters `addressBlock: mmhub_ea_mmeadec6`. The covered `MMEA6_DRAM_*` families mirror the QoS pattern used by earlier blocks:

- `RD_CLI2GRP_MAP0/1` and `WR_CLI2GRP_MAP0/1` map 32 client IDs to four groups with two-bit fields.
- `RD_GRP2VC_MAP` and `WR_GRP2VC_MAP` map the four groups to three-bit virtual-channel IDs.
- `RD_LAZY` and `WR_LAZY` configure per-group lazy delay plus request accumulation threshold, timeout, and idle maximum.
- `RD_CAM_CNTL` and the beginning of `WR_CAM_CNTL` define CAM depth per group, reorder limits per group, and refill-chain control.

The range ends at `MMEA6_DRAM_WR_CAM_CNTL__REORDER_LIMIT_GROUP2__SHIFT`, so the remaining write-CAM masks and subsequent MMEA6 DRAM priority fields belong to later chunks.

## Control Flow

There is no executable control flow in this chunk. The effective runtime flow is indirect:

1. A C file includes `mmhub_9_4_1_offset.h`, `mmhub_9_4_1_sh_mask.h`, and often `mmhub_9_4_1_default.h`.
2. Code reads a 32-bit MMIO register with `RREG32_SOC15*` or starts from a default value.
3. Code composes or extracts fields with `REG_SET_FIELD`, `REG_GET_FIELD`, masks, and shifts from this header.
4. Code writes the value back with `WREG32_SOC15*`.
5. The hardware interprets the bits as address decode, QoS, counter, error, or clock/power configuration.

Because the macros are compile-time constants, there is no runtime validation that a given value fits a field. Callers must mask, shift, and range-check values before writing hardware registers.

## State and Persistence

The header itself has no storage and no persistence. The persistent state is in MMHUB hardware registers programmed using these macros. Important state classes represented in this chunk include:

- Address normalization and decode topology, which controls how physical addresses map onto DRAM/GMI fabric destinations, channels, banks, rows, columns, ranks, and chip selects.
- QoS and arbitration policy, including group mappings, priority coefficients, thresholds, virtual-channel mappings, lazy accumulation, and CAM reorder limits.
- Debug and observability state, including latency sampling, performance counters, EDC counters, and error status bits.
- Clock/power mode state, including DSM and CGTT controls.

Several fields are status or clear bits (`*_ERR_STATUS__CLR_*`, EDC counter clear fields, performance-counter clear/select fields). These must be treated differently from ordinary configuration fields because reads may expose latched hardware state and writes may acknowledge or clear it.

## Dependencies and Integration Points

- `amdgpu/mmhub_v9_4.c` includes this header with the matching offset/default headers and demonstrates the MMHUB register access pattern for v9.4 hardware.
- `soc15.h` and related AMDGPU helpers provide the register access macros that use these generated names.
- `mmhub_9_4_1_offset.h` is required to map the field names to actual MMIO register addresses.
- `mmhub_9_4_1_default.h` is useful for reset-value validation and for detecting whether a field map matches the expected silicon defaults.
- Firmware, SMU/platform initialization, and RAS/debug paths are likely consumers of these address-decode, QoS, EDC, and error-status definitions even when the open `mmhub_v9_4.c` path does not explicitly program every register in this chunk.

## Risks

- The macro names encode a hardware ABI. Renaming or changing a shift/mask silently changes generated register values at compile time and can misprogram memory routing or QoS policy.
- Address normalization, address decode, hash, and harvest fields are high risk: incorrect values can route requests to the wrong memory channel, chip select, row/column bit, GMI destination, or harvested resource.
- DRAM and GMI register families are intentionally parallel. Updating only one side can create asymmetric behavior between local memory and fabric memory paths.
- Client-to-group and priority fields are dense packed bitfields. Off-by-one client IDs, wrong two-bit group encodings, or unmasked values can alter multiple clients at once.
- Status/clear fields such as EDC and error-status bits must not be handled like normal read-modify-write configuration without checking hardware semantics; write-one-to-clear style fields can lose diagnostic information.
- The chunk boundary starts and ends mid-family. Research or generated edits that assume complete families inside this one chunk can miss the first part of `MMEA5_GMI_RD_PRI_QUANT_PRI3` and the rest of `MMEA6_DRAM_WR_CAM_CNTL`.

## Test Signals

Useful validation signals for this chunk are mostly compile-time, register-dump, and hardware-behavior checks:

- Build AMDGPU with `mmhub_v9_4.c` including this header to catch missing or malformed macro definitions.
- Compare generated masks and shifts against the sibling default values by decoding known defaults such as `MMEA5_IO_RD_CLI2GRP_MAP0_DEFAULT`, `MMEA5_SDP_*_DEFAULT`, `MMEA5_MISC_DEFAULT`, and `MMEA6_DRAM_RD_CAM_CNTL_DEFAULT`.
- On supported hardware, use MMIO/register dumps before and after MMHUB initialization to confirm address decode, QoS, EDC, and counter fields match expected firmware/driver programming.
- Exercise memory allocation, GPUVM/GART access, peer/GMI traffic, and IO DMA paths; address-decode mistakes are likely to surface as memory faults, data corruption, hangs, or RAS errors.
- Exercise performance-counter and latency-sampling paths if these fields are programmed by diagnostics; verify counters increment, clear, and select expected events.
- Check RAS/error-injection or fault-reporting paths for correctable/uncorrectable `MMEA5_ERR_STATUS` handling where platform support exists.

### subset-b-002856: lines 35539-37903

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mmhub/mmhub_9_4_1_sh_mask.h lines 35539-37903

## Scope And Purpose

This chunk is a generated AMD MMHUB 9.4.1 shift/mask register header slice for the MMEA6 memory-engine/address-decoder block. It contains preprocessor constants that describe bit positions and bit masks for fields in MMEA6 DRAM, GMI, IO, address-normalization, address-decoder, and SDP arbitration registers.

The source file has no executable code. Its purpose is to provide the field layout contract used by AMDGPU register helpers when they construct, extract, or update MMHUB register values. This header is paired with `mmhub_9_4_1_offset.h`, which defines register offsets, and `mmhub_9_4_1_default.h`, which defines reset/default values for the same register names.

The requested range contains 2,167 `#define` entries: 1,082 `__SHIFT` constants and 1,085 `_MASK` constants. The count is not exactly paired because the range begins inside the tail of `MMEA6_DRAM_WR_CAM_CNTL` and ends inside the beginning of `MMEA6_SDP_VCC_RESERVE0`. This partial-boundary behavior matters for reconciliation with adjacent chunks.

## Register Families Covered

The first lines complete the `MMEA6_DRAM_WR_CAM_CNTL` field layout started before this chunk. The covered fields include reorder-limit shifts, refill-chain shift, CAM depth masks for groups 0-3, reorder-limit masks for groups 0-3, and the refill-chain mask. The matching `MMEA6_DRAM_RD_CAM_CNTL` layout is immediately before this slice.

The DRAM arbitration section defines `MMEA6_DRAM_PAGE_BURST`, read/write priority aging, queuing, fixed priority, urgency, and three priority quantum registers for read and write traffic. These fields encode per-group coefficients, thresholds, burst limits, and urgency modes for four traffic groups.

The GMI arbitration section defines read/write client-to-group maps, group-to-virtual-channel maps, lazy request accumulation, CAM controls, page-burst controls, age/queue/fixed/urgency priority controls, urgency masking, and priority quantum registers. GMI maps split client IDs 0-31 across two map registers per read/write direction, with 2-bit group fields for each client. Urgency masking uses 32 single-bit client masks per read/write direction.

The address-normalization section defines `MMEA6_ADDRNORM_BASE_ADDR0..5`, `LIMIT_ADDR0..5`, and `OFFSET_ADDR1/3/5`, plus DRAM/GMI hole controls, non-power-of-two channel configuration, and global controls. Base registers expose base, interleave, crop, hole-mode, channel, fine-grain channel, and hash fields; limit/offset registers expose narrower address boundary fields.

The address-decoder section defines bank configuration, miscellaneous address decoder controls, DRAM and GMI address-hash controls, DRAM and GMI harvest-enable controls, and three repeated chip-select decoder instances: `ADDRDEC0`, `ADDRDEC1`, and `ADDRDEC2`. Each decoder has base addresses for CS0-CS3 and secondary CS0-CS3, address masks, address configuration, address selection, column-selection low/high registers, and rank-mapping selection registers.

The IO arbitration section defines read/write client-to-group maps, read/write combine flush controls, group-burst controls, age/queue/fixed/urgency priority controls, urgency masking, and priority quantum registers. Like GMI, the client maps cover client IDs 0-31 with 2-bit group selectors, while urgency masking has one mask bit per client.

The SDP section begins the System Data Path arbitration and credit layout. This chunk fully covers DRAM and GMI arbitration controls, final arbitration controls, DRAM/GMI/IO priority controls, tag/response credit limits, tag reservation for VC0-VC7, and the opening shifts for `MMEA6_SDP_VCC_RESERVE0`. The `MMEA6_SDP_VCC_RESERVE0` masks and subsequent SDP reserve/request/misc fields continue after the requested range.

## Important APIs, Types, Functions, And Macros

There are no C APIs, structs, enums, functions, or inline helpers in this chunk. The entire public interface is generated macro data.

The macro naming contract is:

- `<REGISTER>__<FIELD>__SHIFT` gives the least-significant bit index for a register field.
- `<REGISTER>__<FIELD>_MASK` gives the already-shifted bit mask for the same field.
- Multi-field registers use repeated names such as `GROUP0`, `GROUP1`, `CID0`, `CID31`, `VC0`, `CS0`, and `BANK5` to expose indexed hardware fields without C arrays.
- Macros are integer constants with an `L` suffix on masks, for example `0x000000FFL`, and plain hexadecimal values for shifts.

Important macro families in the chunk include:

- `MMEA6_DRAM_*`: DRAM-side arbitration and priority fields for read/write traffic.
- `MMEA6_GMI_*`: GMI-side client mapping, arbitration, urgency, and priority fields.
- `MMEA6_ADDRNORM*`: address-normalization window, hole, NP2-channel, and global-control fields.
- `MMEA6_ADDRDEC*`: bank, hash, harvest, chip-select, address-selection, column-selection, and rank-map fields.
- `MMEA6_IO_*`: IO-side client mapping, combine-flush, arbitration, urgency, and priority fields.
- `MMEA6_SDP_*`: SDP arbitration, priority, tag, response credit, and virtual-channel reservation fields.

Common field layouts repeat across DRAM, GMI, and IO. Priority age registers have four 3-bit aging-rate fields and four 3-bit age-coefficient fields. Queuing/fixed registers have four 3-bit group coefficients. Urgency registers have four 3-bit urgency coefficients and four one-bit urgency-mode fields. Quantum registers have four 8-bit thresholds. Page/group-burst registers pack four 8-bit read/write or group limits.

## Control Flow

This header has no runtime control flow. The implicit use flow is compile-time and register-access driven:

1. Driver code includes the generated MMHUB 9.4.1 register headers.
2. Code selects a register through offset macros from `mmhub_9_4_1_offset.h`.
3. Code constructs or decodes bitfields using the `__SHIFT` and `_MASK` constants in this file, often through AMDGPU/SOC15 helpers.
4. Hardware observes the resulting MMIO register values when the driver programs MMHUB arbitration, address decoding, VM aperture, RAS, or diagnostic state.

The chunk itself does not decide when registers are written. That behavior lives in AMDGPU MMHUB/GMC/VM initialization, power-management, virtualization, RAS, and debug paths. This file supplies the bit layout those paths must obey.

## State And Persistence Behavior

The macros are compile-time constants and do not persist runtime state. They describe persistent hardware register layout, meaning they define how software interprets and writes MMHUB state that does persist in the device until reset or reprogramming.

Arbitration-related fields persist as hardware policy after programming. DRAM, GMI, and IO group mappings, virtual-channel maps, priority coefficients, urgency modes, urgency masks, burst limits, CAM depths, reorder limits, and quantum thresholds directly influence request ordering, fairness, latency, and bandwidth distribution.

Address-normalization and address-decoder fields persist as address-routing state. Base/limit/offset windows, hole controls, channel and interleave fields, bank configuration, address hashing, harvest enable, chip-select base/mask/configuration, column-selection, and rank-map selection fields determine how MMEA6 routes physical memory requests to DRAM/GMI resources.

SDP fields persist as request/response credit and final arbitration policy. Tag limits, read/write response credits, VC tag reservations, VC credit reservations, readonly VC flags, error-event and halt-request policy, and burst-stretch controls can affect forward progress and error response behavior.

Because this slice starts and ends on partial register definitions, consumers of generated documentation should combine it with adjacent chunks before treating the full source file as completely described.

## Dependencies And Integration Points

This header depends only on the C preprocessor, but it is tightly coupled to the generated AMDGPU MMHUB register model:

- `mmhub_9_4_1_offset.h` must define matching `mmMMEA6_*` register offsets.
- `mmhub_9_4_1_default.h` must define matching `mmMMEA6_*_DEFAULT` reset values where applicable.
- AMDGPU SOC15 register helpers use field masks and shifts to isolate and modify register fields without hard-coded bit arithmetic.
- MMHUB v9.4 runtime code uses the generated register model for GPU memory controller setup, VM hub programming, TLB invalidation, protection-fault handling, RAS/EDC handling, clock/power management, and register diagnostics.
- Hardware and firmware interfaces rely on the generated register layout matching the ASIC specification exactly.

Integration is mostly name-based. If a register or field is renamed in one generated header but not the others, C compilation may fail for direct references. More dangerous drift can still compile if stale masks remain unused until a specific runtime path or debug path touches that field.

## Risks And Edge Cases

The main correctness risk is bitfield drift. A wrong shift or mask can write the wrong hardware bits while leaving nearby fields unchanged, which can produce silent misconfiguration rather than an obvious crash.

The repeated register families create generation and review risk. DRAM, GMI, and IO priority fields use similar layouts with small differences; GMI and IO client maps each enumerate 32 client IDs; DRAM/GMI hash controls and chip-select decoders repeat across multiple banks and decoder instances. A single missing or shifted field can affect only one client, VC, bank, chip-select pair, or decoder instance.

Partial chunk boundaries are a documentation risk. This range begins after the `MMEA6_DRAM_WR_CAM_CNTL` heading and ends before the rest of `MMEA6_SDP_VCC_RESERVE0`. Merge/reconciliation must avoid treating these partial blocks as complete register descriptions.

Address-decoder fields are high blast-radius. Mistakes in base, mask, chip-select, column-selection, rank-map, hash, harvest, or channel fields can route memory to the wrong slice, bank, channel, or aperture. Such bugs may appear as data corruption, GPU hangs, RAS events, or performance anomalies.

Arbitration and credit fields are performance and forward-progress sensitive. Bad CAM depths, reorder limits, urgency masks, VC maps, tag limits, or response credits can cause starvation, excessive latency, underutilization, or deadlock-like behavior under load.

The macros carry no type safety. Any code can combine a shift from one register with a mask from another if names are misused. Review and generated-header consistency checks are the primary protection.

## Test Signals

Build tests should compile AMDGPU code that includes `mmhub_9_4_1_sh_mask.h`, especially paths that reference MMEA6 register fields through SOC15 field helpers.

Generated-header validation should verify that every full register represented in this slice has a matching offset macro and, where present, a matching default macro. It should also verify that each field has a coherent shift/mask pair, except for the known partial boundary cases at `MMEA6_DRAM_WR_CAM_CNTL` and `MMEA6_SDP_VCC_RESERVE0`.

Static consistency checks can validate mask geometry: each `_MASK` should align with its corresponding `__SHIFT`, repeated fields should not overlap, and same-layout register families should have equivalent field widths unless the ASIC specification says otherwise.

Runtime smoke tests on MMHUB 9.4.1 hardware should cover GART and VM setup, MMHUB initialization, TLB invalidation, protection-fault reporting, suspend/resume, power/clock gating, and memory traffic through DRAM, GMI, and IO paths.

Stress and performance tests are important for this slice because much of it describes arbitration, priority, urgency, and credit policy. Useful signals include memory bandwidth fairness, latency under mixed read/write traffic, GMI/IO traffic behavior, and absence of hangs under high outstanding-request pressure.

RAS and diagnostic tests should read address-decoder and MMEA status paths after initialization and under injected or simulated faults. Register-dump comparisons against generated offsets/defaults/masks can catch field drift before it becomes a runtime-only failure.

### subset-b-002857: lines 37904-40269

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mmhub/mmhub_9_4_1_sh_mask.h lines 37904-40269

## Scope

This chunk is a generated AMDGPU MMHUB 9.4.1 shift/mask header segment. It contains 2,170 C preprocessor `#define` entries for 32-bit MMIO register fields, plus generated register/address-block comments. There are no functions, structs, enums, variables, allocations, locks, branches, loops, or direct register reads/writes in this range.

The chunk starts in the middle of the `MMEA6_SDP_VCC_RESERVE0` register, covers the tail of the `mmhub_ea_mmeadec6` block, then enters `// addressBlock: mmhub_ea_mmeadec7` and covers `MMEA7` arbitration, address-normalization, address-hash, harvest, and address-decoder fields through the beginning of `MMEA7_ADDRDEC2_RM_SEL_CS01`.

Although the repository path is under a `ceph-client` source mirror, this source is Linux AMDGPU hardware register metadata, not Ceph filesystem logic.

## Purpose

`mmhub_9_4_1_sh_mask.h` provides the bit-level ABI for composing and decoding MMHUB 9.4.1 register values. This chunk's constants let driver code work with named fields instead of hard-coded bit positions when programming or inspecting memory-engine address arbitration, virtual-channel crediting, RAS/EDC status, error-injection controls, clock-gating controls, physical address normalization, DRAM/GMI hashing, chip-select decoding, bank/column/row-machine selection, and performance counters.

The exported convention is consistent across the generated header:

- `<REGISTER>__<FIELD>__SHIFT` gives the field's low bit position.
- `<REGISTER>__<FIELD>_MASK` gives the positioned 32-bit mask used to isolate or update that field.

These field constants are meaningful only when paired with `mmhub_9_4_1_offset.h`, which supplies register offsets such as `mmMMEA6_EDC_CNT`, `mmMMEA7_DRAM_RD_CLI2GRP_MAP0`, `mmMMEA7_ADDRNORM_BASE_ADDR0`, and `mmMMEA7_ADDRDEC2_COL_SEL_HI_CS23`, and with `mmhub_9_4_1_default.h`, which supplies reset/default register values.

## Important Macro Families

### MMEA6 SDP, performance, EDC, DSM, and status tail

The first part completes `MMEA6` fields that began in the prior chunk:

- `MMEA6_SDP_VCC_RESERVE1`, `MMEA6_SDP_VCD_RESERVE0`, and `MMEA6_SDP_VCD_RESERVE1` split virtual-channel credit reserves across `VC0_CREDITS` through `VC7_CREDITS` and include `DISTRIBUTE_POOL` flags on the high reserve registers.
- `MMEA6_SDP_REQ_CNTL` exposes request policy override bits for read, write, atomic, DRAM chaining, GMI chaining, and `INNER_DOMAIN_MODE`.
- `MMEA6_MISC` contains arbitration priority bits for DRAM/GMI/IO reads and writes, early write-return enables for VC0-VC7, link-manager dynamic/halt/reconnect/idle fields, and chip-select switching/favoring controls.
- `MMEA6_LATENCY_SAMPLING` selects sampler filters by target path (`DRAM`, `GMI`, `IO`), operation (`READ`, `WRITE`, atomic return/no-return), and virtual channel.
- `MMEA6_PERFCOUNTER_LO`, `MMEA6_PERFCOUNTER_HI`, `MMEA6_PERFCOUNTER0_CFG`, `MMEA6_PERFCOUNTER1_CFG`, and `MMEA6_PERFCOUNTER_RSLT_CNTL` define counter value, compare value, event-selection, enable, clear, start/stop trigger, and stop-on-saturate fields.
- `MMEA6_EDC_CNT`, `MMEA6_EDC_CNT2`, and `MMEA6_EDC_CNT3` expose small saturated count fields for single-error-corrected, double-error-detected, and single-error-detected conditions across DRAM, GMI, IO, return-tag, page, and MAM memories.
- `MMEA6_DSM_CNTL`, `MMEA6_DSM_CNTLA`, `MMEA6_DSM_CNTL2`, and `MMEA6_DSM_CNTL2A` define diagnostic/stress fields: irritator data, single-write enable, per-memory error-injection enable, injection-delay selectors, and a shared `INJECT_DELAY`.
- `MMEA6_CGTT_CLK_CTRL` defines on/off timing and soft clock/light-sleep override bits for write, read, return, and register paths.
- `MMEA6_EDC_MODE`, `MMEA6_ERR_STATUS`, `MMEA6_MISC2`, and `MMEA6_ADDRDEC_SELECT` define RAS mode/status behavior, SDP response/parity error flags, error clear/busy/FUE bits, arbitration swap/burst controls, and channel range selection for DRAM/GMI address decoders.

The visible `MMEA6` RAS fields are integrated by `amdgpu/mmhub_v9_4.c`, which includes this exact mask header and builds EDC/error-status tables using `SOC15_REG_ENTRY`, `SOC15_REG_FIELD`, and `REG_GET_FIELD`.

### MMEA7 DRAM and GMI arbitration

The `mmhub_ea_mmeadec7` address block starts at line 38359. It mirrors the same MMEA register shape for another memory-engine/address-decoder instance.

The DRAM and GMI read/write client maps use dense repeated bitfields:

- `MMEA7_DRAM_RD_CLI2GRP_MAP0/1`, `MMEA7_DRAM_WR_CLI2GRP_MAP0/1`, `MMEA7_GMI_RD_CLI2GRP_MAP0/1`, and `MMEA7_GMI_WR_CLI2GRP_MAP0/1` map client IDs `CID0` through `CID31` into four groups using 2-bit fields.
- `MMEA7_*_GRP2VC_MAP` maps group 0-3 into 3-bit virtual-channel values.
- `MMEA7_*_LAZY` provides per-group delay fields plus accumulated request threshold, timeout, and idle-max fields.
- `MMEA7_*_CAM_CNTL` configures CAM depth/behavior fields for the corresponding DRAM or GMI read/write path.
- `MMEA7_*_PAGE_BURST`, `*_PRI_AGE`, `*_PRI_QUEUING`, `*_PRI_FIXED`, `*_PRI_URGENCY`, and `*_PRI_QUANT_PRI1/2/3` describe page-burst and arbitration priority tuning by group.
- `MMEA7_GMI_RD_PRI_URGENCY_MASKING` and `MMEA7_GMI_WR_PRI_URGENCY_MASKING` provide one-bit masks for `CID0` through `CID31`; these are especially dense and easy to misuse because the field names themselves include `MASK`, producing generated names like `CID0_MASK_MASK`.

This block is pure metadata, but incorrect values would directly affect memory traffic arbitration if consumed by initialization, debug, or tuning code.

### MMEA7 address normalization and apertures

`MMEA7_ADDRNORM_BASE_ADDR0` through `BASE_ADDR5` define repeated address-range descriptors:

- `ADDR_RNG_VAL` enables the range.
- `LGCY_MMIO_HOLE_EN` controls legacy MMIO-hole handling.
- `INTLV_NUM_CHAN`, `INTLV_NUM_DIES`, `INTLV_NUM_SOCKETS`, and `INTLV_ADDR_SEL` describe interleave topology.
- `BASE_ADDR` occupies the high 20 bits of the register.

The matching `MMEA7_ADDRNORM_LIMIT_ADDR0` through `LIMIT_ADDR5` expose destination fabric ID and high limit address fields. `MMEA7_ADDRNORM_OFFSET_ADDR1/3/5` provide optional high-address offset enable/value fields. `MMEA7_ADDRNORMDRAM_HOLE_CNTL` and `MMEA7_ADDRNORMGMI_HOLE_CNTL` expose DRAM-hole valid/offset fields, and `MMEA7_ADDRNORMDRAM_NP2_CHANNEL_CFG` plus `MMEA7_ADDRNORMGMI_NP2_CHANNEL_CFG` describe non-power-of-two channel-space sizing.

These macros sit on the address-translation path from normalized GPU/system addresses toward DRAM or GMI fabric routing. Their correctness is critical for aperture and interleave programming.

### MMEA7 address decode, hashing, and harvesting

`MMEA7_ADDRDEC_BANK_CFG` and `MMEA7_ADDRDEC_MISC_CFG` define bank, bank-group, pseudo-channel, channel, chip-select, and row-machine masks and enable bits for DRAM and GMI decode.

`MMEA7_ADDRDECDRAM_ADDR_HASH_BANK0` through `BANK5`, `PC`, `PC2`, `CS0`, and `CS1` define XOR-based hash controls for DRAM address decoding. The GMI variants, `MMEA7_ADDRDECGMI_ADDR_HASH_*`, repeat the same shape. Bank and pseudo-channel hash fields include `XOR_ENABLE`, `COL_XOR`, `ROW_XOR`, and `BANK_XOR` masks; chip-select hash registers include `XOR_ENABLE` and a wide `NA_XOR`.

`MMEA7_ADDRDECDRAM_HARVEST_ENABLE` and `MMEA7_ADDRDECGMI_HARVEST_ENABLE` provide force-enable/value fields for bank bits B3-B5, which are used to account for harvested or disabled memory resources.

### MMEA7 address decoders 0-2

The chunk covers complete `MMEA7_ADDRDEC0_*` and `MMEA7_ADDRDEC1_*` families and most of `MMEA7_ADDRDEC2_*` through the start of `ADDRDEC2_RM_SEL_CS01`.

For each decoder:

- `BASE_ADDR_CS0` through `BASE_ADDR_CS3` and `BASE_ADDR_SECCS0` through `SECCS3` expose `CS_EN` and wide `BASE_ADDR` fields.
- `ADDR_MASK_CS01`, `ADDR_MASK_CS23`, `ADDR_MASK_SECCS01`, and `ADDR_MASK_SECCS23` define wide address-mask fields shared by chip-select pairs.
- `ADDR_CFG_CS01` and `ADDR_CFG_CS23` describe number of bank groups, row machines, row low/high bits, columns, banks, and high-column enable.
- `ADDR_SEL_CS01` and `ADDR_SEL_CS23` select address bit positions for bank 0-4 and row low/high; `ADDR_SEL2_*` carries bank 5.
- `COL_SEL_LO_*` and `COL_SEL_HI_*` select column bit positions for columns 0-15.
- `RM_SEL_*` selects row-machine bit positions and row-MSB inversion behavior. The line range ends just after the first `MMEA7_ADDRDEC2_RM_SEL_CS01` shift definitions begin, so the remainder of `ADDRDEC2_RM_SEL_*` belongs to the next chunk.

## Control Flow And Runtime Behavior

There is no runtime control flow in this header chunk. The effective control flow happens in consumers:

1. A driver source includes `mmhub_9_4_1_offset.h`, `mmhub_9_4_1_sh_mask.h`, and often `mmhub_9_4_1_default.h`.
2. Code reads a register with SOC15 helpers, composes or extracts fields with macros such as `REG_SET_FIELD`, `REG_GET_FIELD`, `SOC15_REG_FIELD`, `SOC15_REG_ENTRY`, or direct mask operations, then writes the updated register value.
3. Hardware persists the resulting register state until reset, suspend/resume save/restore, power-gating transitions, or explicit reprogramming.

`amdgpu/mmhub_v9_4.c` is the exact in-tree integration point for this generated header. In that file, MMEA EDC count registers for instances 0-7, including `MMEA6_EDC_CNT*` and `MMEA7_EDC_CNT*`, are listed in RAS error-count tables, and `MMEA*_ERR_STATUS` fields are used to detect SDP read/write response and data-parity errors. Other parts of the same driver use the generated MMHUB mask convention for VM, DAGB, clock-gating, and aperture programming.

## State And Persistence

This chunk declares no C storage, so it has no software persistence by itself. The persistent state is the hardware state represented by the registers:

- Credit, request policy, priority, arbitration, and lazy-timer fields affect live MMHUB traffic scheduling until changed or reset.
- Address normalization, address decoding, hash, harvest, chip-select, column, bank, and row-machine fields define routing of physical memory accesses and must match the ASIC memory topology.
- EDC count/status fields are hardware counters or status bits used by RAS collection and may be clear-on-write or clear-through-control depending on the hardware register semantics.
- DSM and error-injection fields can alter diagnostic behavior and should only be used under controlled RAS/test flows.
- Clock-gating override fields can change power/performance behavior and can mask real idle/busy behavior during debugging.

## Dependencies And Integration Points

Primary dependencies:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mmhub/mmhub_9_4_1_offset.h`: matching register offsets and base indices. For this chunk, `MMEA7` offsets run in the `0x3500` range and use base index `1`.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mmhub/mmhub_9_4_1_default.h`: reset/default values for the same registers. The defaults show non-zero DRAM/GMI arbitration, lazy, CAM, priority, address-mask/config/select, SDP, clock, and error-status values for `MMEA6` and `MMEA7`.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/mmhub_v9_4.c`: includes this header and consumes MMEA EDC/status masks through AMDGPU/SOC15 register helpers.
- AMDGPU helper macros such as `REG_SET_FIELD`, `REG_GET_FIELD`, `SOC15_REG_FIELD`, `SOC15_REG_ENTRY`, `RREG32_SOC15`, `WREG32_SOC15`, and offset variants.

The generated naming contract is the key integration surface. If a macro is renamed, duplicated incorrectly, or paired with the wrong generation's offset header, callers can still compile but program the wrong bits.

## Risks

- Boundary risk: line 37904 starts inside `MMEA6_SDP_VCC_RESERVE0`, and line 40269 ends inside `MMEA7_ADDRDEC2_RM_SEL_CS01`; reconciliation must merge adjacent chunks for complete register-family documentation.
- Generation-pairing risk: these masks must be used with `mmhub_9_4_1_offset.h` and `mmhub_9_4_1_default.h`, not another MMHUB generation with similar register names.
- Bitfield drift risk: a single wrong shift or mask can silently redirect writes to an unrelated hardware control bit.
- Dense repeated-field risk: client maps, urgency masks, and address-decode selectors are mechanically repetitive, so off-by-one client IDs or chip-select pair mix-ups are easy during manual edits.
- RAS/debug risk: EDC, error-status, DSM, and error-injection fields affect error counting, fault signaling, or injected failures. Incorrect masks can hide real errors, falsely report RAS events, or enable diagnostic behavior in normal operation.
- Memory-routing risk: address normalization, hash, harvest, and chip-select decode fields can misroute memory traffic if programmed inconsistently with actual memory topology.
- Power/performance risk: clock-gating overrides and arbitration/priority fields can change latency, bandwidth fairness, and power behavior.

## Test And Validation Signals

Useful validation for this chunk is mostly structural and hardware-facing:

- Compile coverage of `amdgpu/mmhub_v9_4.c` with this generated header included verifies that expected macro names are present.
- Static generated-header checks should confirm each `__SHIFT` has a matching `_MASK`, masks are 32-bit values, and repeated fields advance monotonically without overlap inside each register.
- Cross-header checks should confirm every register prefix in this chunk has matching `mm<REGISTER>` and `mm<REGISTER>_DEFAULT` entries where expected in the offset/default headers.
- RAS tests should exercise MMHUB EDC count collection for `MMEA6_EDC_CNT*` and `MMEA7_EDC_CNT*`, plus `MMEA*_ERR_STATUS` read/clear behavior.
- GPU bring-up, suspend/resume, and reset tests should confirm MMHUB traffic remains functional after register programming/restoration.
- Memory-topology validation should cover address normalization, chip-select decode, harvested-bank configurations, and DRAM/GMI address hashing on hardware variants with different channel/bank layouts.
- Performance and power tests should watch for regressions in bandwidth, latency, fairness, and clock-gating residency when arbitration or clock-control fields are changed.

### subset-b-002858: lines 40270-42638

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mmhub/mmhub_9_4_1_sh_mask.h lines 40270-42638

## Purpose

This chunk is generated AMDGPU MMHUB 9.4.1 register bitfield metadata. It defines C preprocessor `*_SHIFT` and `*_MASK` constants for the end of the `MMEA7` register family, all visible `mmhub_pctldec1` `PCTL1` power/control fields, the `VML1_1` L1 TLB status block, L1 performance-counter configuration/result fields, the `ATCL2_1` ATC L2 translation-cache block, and the first fields of `VML2PF1_VM_L2_CNTL`.

Although this repository path is under `distributed-fs/ceph-client`, the file is Linux AMD GPU driver hardware metadata, not Ceph filesystem logic. It has no executable behavior and no filesystem persistence.

The covered range provides field layouts for:

- The tail of `MMEA7_ADDRDEC2_RM_SEL_*`, `ADDRNORM*`, IO client/group mapping, read/write IO priority, SDP arbitration, SDP credit/reserve, latency/performance-counter, EDC, DSM/error-injection, clock-gating, error-status, and address-decoder selection registers.
- `PCTL1_CTRL`, deep-sleep/override/ignore registers, per-slice deep-sleep allow/busy bits, slice/UTCL2 misc controls, register-engine execute/index/data windows, and per-slice state-controller register-save ranges/exclusion sets.
- `VML1_1_MC_VM_MX_L1_TLB0..7_STATUS` busy and parity status fields.
- `VML1PL1_MC_VM_MX_L1_PERFCOUNTER0..3_CFG`, shared result control, and `VML1PR1` low/high counter readback fields.
- `ATCL2_1_ATC_L2_*` controls, cache-data inspection words, status/parity fields, clock/memory light-sleep controls, DSM error-injection controls, active transaction limits, and MM real-time class mapping.
- The first `VML2PF1_VM_L2_CNTL` fields at the chunk boundary, covering L2 cache enable, fragment processing, endian swap modes, PDE tag generation/split mode, LRU update-by-write, and default-page-out behavior. Later `VML2PF1` fields belong to the next chunk.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, callbacks, locks, allocations, or direct MMIO reads/writes in this chunk. The exported interface is the generated macro namespace:

- `<REGISTER>__<FIELD>__SHIFT` gives the bit offset of a field in a 32-bit MMHUB register.
- `<REGISTER>__<FIELD>_MASK` gives the corresponding unshifted register mask.

High-signal macro groups include:

- `MMEA7_IO_*`: client-ID to group maps for read/write CIDs 0-31, per-group age/queue/fixed/urgency priorities, urgency masking bitmaps, priority quanta, and read/write combine flush fields.
- `MMEA7_SDP_*`: DRAM/GMI/final burst arbitration, readonly VC flags, error event/halt request controls, per-target priority maps, tag and response credits, per-VC tag/VCC/VCD reserves, and request control.
- `MMEA7_EDC_*`, `MMEA7_DSM_*`, `MMEA7_ERR_STATUS`: SEC/DED counters, fault/event disposition, FED/FUE behavior, DSM error-injection setup, and error-status clear/busy flags for DRAM, IO, GMI, return-tag, command, data, and page memories.
- `PCTL1_*`: power-gating enable, deep-sleep permissions and overrides, per-slice `DS_ALLOW` and `CFG_DAGB_BUSY` state, register-engine execution, register-engine RAM windows, critical-register locks, state-controller save ranges, and exclusion sets for UTCL2 plus slices 0-4.
- `VML1_1_*` and `VML1PL1`/`VML1PR1_*`: L1 TLB busy/parity status and performance-counter selection, mode, enable, clear, trigger, saturation, and 48-bit result/compare fields.
- `ATCL2_1_*`: ATS/ATC translation read/write request credits, host translation request credits, cache invalidation mode, bank select, cache update/VMID/tag-index controls, cache-data readback, parity status, clock/light-sleep controls, DSM injection/counters, transaction limits, and MM group real-time classes.
- `VML2PF1_VM_L2_CNTL`: the opening VM L2 control fields for cache enablement, fragment processing, PTE/PDE endian swap, PDE0 tagging/split, LRU update-by-write, and default-page-out routing.

These masks are normally paired with register offsets from `mmhub_9_4_1_offset.h` and consumed by AMDGPU SOC15 helpers such as `SOC15_REG_FIELD`, `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32_SOC15`, and `WREG32_SOC15`. The offset header supplies the register address; this header supplies how to pack or decode each 32-bit value.

## Control Flow

This header chunk has no runtime control flow. It affects runtime behavior only through C preprocessing.

Typical consumer flow is:

1. MMHUB 9.4.x driver code includes `mmhub_9_4_1_offset.h` and `mmhub_9_4_1_sh_mask.h`.
2. Initialization, golden-register, power-management, VM hub, diagnostics, or error-reporting code selects a register by offset macro.
3. The code constructs or decodes fields with the generated `__SHIFT` and `_MASK` constants, often through AMDGPU field helpers.
4. SOC15 MMIO helpers perform the actual read or write against MMHUB hardware.

The header does not encode sequencing rules. It does not state when queues are idle, when deep-sleep or power-gating bits are firmware-owned, when cache invalidation has completed, how to clear sticky error status safely, or when register-engine commands are allowed. Those constraints live in MMHUB implementation code, firmware protocols, hardware specifications, and companion default/offset headers.

## State And Persistence Behavior

No software state is stored here. The macros describe hardware register state.

The represented hardware state includes:

- Persistent-until-reprogrammed configuration: MMEA7 address decoding, IO client grouping, priority/burst/credit policy, SDP arbitration, PCTL1 power/deep-sleep controls, PCTL1 save/restore windows, ATCL2 translation-cache modes, and the initial VM L2 control bits.
- Live or status-like state: MMEA7 error status, L1 TLB busy/parity status, ATCL2 busy/parity status, performance-counter result registers, and EDC SEC/DED counter fields.
- Trigger/control state: performance-counter `ENABLE`, `CLEAR`, `CLEAR_ALL`, start/stop triggers, `STOP_ALL_ON_SATURATE`, PCTL register-engine execute-now fields, MMEA7 error-status clear, and DSM write/error-injection controls.
- Debug and test state: DSM index/control registers and cache-data windows expose cache internals or inject errors for 4K/2M ATC L2 cache paths and MMEA7 internal memories.

Persistence is hardware-defined. Configuration registers may survive until reset, power-gating reset, suspend/resume restore, driver reinitialization, or explicit reprogramming. Status/counter fields can change continuously with traffic. This generated mask file cannot distinguish read-only, write-one-to-clear, write-trigger, sticky, firmware-owned, debug-only, or reserved semantics beyond the field names.

## Dependencies

This chunk depends on the generated AMDGPU register stack for MMHUB 9.4.1:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mmhub/mmhub_9_4_1_offset.h` provides the matching `mm<REGISTER>` offsets and base indices. The searched offset file contains matching entries for `PCTL1_*`, `VML1_1_*`, `ATCL2_1_*`, and `VML2PF1_*`.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/mmhub_v9_4.c` includes this mask header and uses `MMEA7_EDC_CNT*` and `MMEA7_ERR_STATUS` fields through SOC15 register-entry/field helpers for error-counter and reset/error handling tables.
- AMDGPU SOC15 register helpers and field macros consume the `*_SHIFT`/`*_MASK` constants to build register values and decode readbacks.
- Adjacent chunks of the same header are required for a complete per-file view. This chunk starts in the middle of `MMEA7_ADDRDEC2_RM_SEL_CS01` and ends inside `VML2PF1_VM_L2_CNTL`.

Sibling MMHUB generation headers are structurally similar but not interchangeable. Cross-generation names can compile while pointing at different bit layouts or offsets.

## Integration Points

Primary integration points are:

- MMHUB 9.4 driver initialization and golden-register programming for memory-hub arbitration, address decoding, VM translation caches, and power behavior.
- Error reporting and recovery paths in `amdgpu/mmhub_v9_4.c`, especially MMEA7 EDC counter reporting and error-status handling.
- GPUVM and IOMMU/ATS-related translation flows that rely on ATCL2, VML1, and VM L2 state for page translation, invalidation, cache policy, fault/default-page handling, and parity reporting.
- Power-management flows that program `PCTL1_CTRL`, deep-sleep override/ignore registers, per-slice allow registers, register save ranges, and clock/light-sleep controls.
- Diagnostics and profiling flows that use MMEA7 and L1 performance counters, TLB busy/parity status, ATCL2 status, cache-data windows, and DSM injection/counter fields.
- Multi-slice MMHUB programming. The repeated `PCTL1_SLICE0..4` field layouts imply looped or table-driven programming must pair each slice register offset with the exact same field definitions.

## Risks And Edge Cases

- Wrong-generation pairing is the main risk. Using MMHUB 9.4.1 masks with another generation's offsets or driver assumptions can silently pack the wrong bits.
- The chunk boundaries are artificial: it starts after the first two fields of `MMEA7_ADDRDEC2_RM_SEL_CS01` and ends before the rest of `VML2PF1_VM_L2_CNTL`. The later merge lane must combine adjacent chunks before treating either register family as complete.
- Repeated slice and client layouts invite text substitution bugs. `PCTL1_UTCL2_*` differs from `PCTL1_SLICE*_*` in index widths and execute pointer masks, so helpers must not assume all PCTL register-engine windows are identical.
- IO priority, urgency masking, credit, burst, and reserve fields are liveness- and performance-sensitive. Bad values can cause bandwidth throttling, unfair arbitration, downstream queue pressure, or memory-hub timeout symptoms.
- PCTL deep-sleep, power-gating, register-save, and critical-register-lock fields can interact with firmware or reset/resume sequencing. Updating them while blocks are active can lose state or destabilize access.
- ATCL2 cache invalidation, ATS request credits, bank selection, cache update mode, and VMID behavior affect translation correctness. Incorrect programming can surface as VM faults, stale translations, invalidation hangs, or host-translation stalls.
- Status/counter fields should not be treated as ordinary writable configuration unless the hardware spec explicitly says so. Error-status clear and DSM injection bits can destroy diagnostic evidence or intentionally create faults.
- `SETCLEAR`, execute-now, clear, and write-counter fields are command-like; read-modify-write helpers must preserve intended one-shot semantics.

## Test Signals

Useful validation signals include:

- Build coverage for AMDGPU MMHUB 9.4 paths that include `mmhub_9_4_1_offset.h` and `mmhub_9_4_1_sh_mask.h`.
- Static consistency checks that every field has both `__SHIFT` and `_MASK`, repeated slice/client families use expected masks, and offset/mask/default headers remain synchronized for MMHUB 9.4.1.
- Boot/init tests on ASICs using MMHUB 9.4.1, with attention to MMHUB bring-up, golden-register programming, VM hub setup, and error-counter table registration.
- GPUVM stress tests that exercise mapping/unmapping, TLB invalidation, ATS/ATC paths, mixed read/write IO traffic, page faults, and default-page-out behavior while checking for MMHUB faults or hangs.
- Power-management tests covering suspend/resume, reset, BACO/runtime power transitions, deep-sleep entry/exit, and state-controller register save/restore behavior.
- Diagnostic tests that read MMEA7 EDC/error status, L1 TLB parity/busy status, ATCL2 parity/busy status, and performance-counter results under known traffic.
- Regression indicators include ring timeouts, VM faults, stale translations after invalidation, parity/FED/FUE reports, unexpected EDC count increments, persistent busy bits after traffic drains, power-transition failures, or unexpected bandwidth/latency changes after register programming.

### subset-b-002859: lines 42639-45068

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mmhub/mmhub_9_4_1_sh_mask.h lines 42639-45068

## Scope And Purpose

This chunk is the final range of the generated MMHUB 9.4.1 shift/mask header. It contains no executable C code, types, or functions. Instead, it publishes preprocessor constants that describe bit positions and bit masks for late MMHUB virtual-memory, virtualization, aperture, ATS, XGMI, clock-gating, and performance-counter registers.

The covered range starts in the `mmhub_utcl2_vml2pfdec:1` address block with the tail of `VML2PF1_VM_L2_CNTL`, then completes the `VML2PF1` L2 control/status/fault register field macros. It then defines the `VML2VC1` VM-context block for contexts 0 through 15, invalidation engines 0 through 17, page-table base/start/end address registers, shared PF/VC/HV aperture and virtualization controls, and the final ATC/L2 and VM/L2 perf-counter controls. The file ends with the `_mmhub_9_4_1_SH_MASK_HEADER` include-guard close.

The purpose is to let AMDGPU code write and read named register fields through helper macros such as `REG_SET_FIELD`, paired with register offsets from `mmhub_9_4_1_offset.h` and reset defaults from `mmhub_9_4_1_default.h`. The direct in-tree consumer for this ASIC generation is `drivers/gpu/drm/amd/amdgpu/mmhub_v9_4.c`, which includes all three MMHUB 9.4.1 generated headers.

## Important APIs, Types, And Macro Families

The `VML2PF1_VM_L2_*` family describes physical-function L2 VM controls. Key fields include L2 cache enablement, fragment processing, PTE/PDE endian swap modes, LRU update behavior, default-page routing, PDE cache split/effective size, invalidation controls, bank selection, cache force-miss bits, parity status, dummy-page fault matching, identity aperture bounds, identity physical offset, and cache parity/clock-gating knobs.

The protection fault macros define both policy and observability. `VML2PF1_VM_L2_PROTECTION_FAULT_CNTL` and `CNTL2` provide clear/update controls, per-fault-class default-page enable bits, no-retry/retry crash bits, client interrupt masks, active page-migration PTE behavior, and retry fault interrupt enable. The status and address registers expose `MORE_FAULTS`, `WALKER_ERROR`, permission/mapping flags, `CID`, read/write and atomic attributes, `VMID`, VF/VFID identity, logical fault address, and default physical address fields.

The `VML2VC1_VM_CONTEXT0_CNTL` through `VML2VC1_VM_CONTEXT15_CNTL` families are repeated VMID context controls. Each context has fields for `ENABLE_CONTEXT`, page-table depth, page-table block size, retry-on-fault behavior, interrupt/default enable bits for range, dummy-page, PDE0, valid, read, write, and execute protection faults. The later `VML2VC1_VM_CONTEXTS_DISABLE` register provides one disable bit for each context 0 through 15.

The invalidation macros define 18 invalidation engines. Each engine has a semaphore register, request fields for per-VMID invalidate bits, `FLUSH_TYPE`, `FLUSH_UTCL2`, `CLEAR_PROTECTION_FAULT_STATUS_ADDR`, `LOG_REQUEST`, and a 4-bit `INVALIDATE_L2_PTES` field. Each engine also has an ack bit and low/high logical page range fields. In `mmhub_v9_4.c`, these offset distances populate `amdgpu_vmhub` fields used by common VM invalidation code.

The page-table address families publish 32-bit low and 4-bit high fields for each VM context's page-table base, start, and end addresses. AMDGPU writes these from GART and VM-manager state by shifting GPU addresses/PFNs into the register's page-number format.

The `VMSHAREDPF1_*`, `VMSHAREDVC1_*`, and `VMSHAREDHV1_*` blocks describe shared MMHUB controls. They include NB MMIO/PCI and top-of-DRAM controls, framebuffer offset, system aperture default address, steering, reset, memory power light-sleep, cacheable DRAM, local HBM, XGMI LFB controls, framebuffer/AGP/system aperture bounds, L1 TLB controls, per-VF framebuffer size/offset, MARC base/relocation/length windows, IOMMU/ATS controls, per-VF ATS enable bits, hypervisor-side UTCL2 clock-gating, active function ID, and XGMI GPUIOV enable bits for VF0-VF15 plus PF.

The final `ATCL2PFCNTR1`, `ATCL2PFCNTL1`, `VML2PL1`, and `VML2PR1` blocks define performance-counter data and control fields. They expose low/high counter values, compare value fields, event selection ranges, perf modes, enable/clear bits, global result-counter selection, start/stop triggers, enable-any, clear-all, and stop-on-saturate behavior.

## Control Flow And Runtime Use

There is no runtime control flow inside this header. Its behavior is entirely preprocessing: a consumer names a register block and field, and build-time macro expansion supplies the shift and mask constants for bit manipulation.

The usual runtime path is visible in `mmhub_v9_4.c`. GART enablement programs MMHUB instances by writing page-table base/start/end registers, system aperture registers, L1 TLB control, L2 cache control, VMID context control, and invalidation address ranges. Calls like `REG_SET_FIELD(tmp, VML2PF0_VM_L2_CNTL, ENABLE_L2_CACHE, 1)` rely on the same generated naming scheme as this chunk's `VML2PF1_*` macros. Instance and function-number variants are selected through matching offset names and per-hub register offsets.

Fault handling uses these field layouts when `mmhub_v9_4_set_fault_enable_default()` toggles protection-fault default-page routing and crash behavior. The `amdgpu_vmhub` initialization stores register offsets for context0 control, invalidation semaphore/request/ack, and L2 fault status/control so common GPUVM code can later drive invalidations and inspect fault state without hard-coding MMHUB register addresses.

Performance-counter and virtualization fields in this chunk are mostly register-interface surface. They may be used by diagnostics, firmware-oriented flows, SR-IOV/hypervisor setup, or future performance tooling even when not directly touched by the narrow `mmhub_v9_4.c` initialization path.

## State And Persistence Behavior

This header itself has no storage, allocation, persistence, I/O, or side effects. The constants become part of compiled driver code wherever included.

The hardware registers described here are persistent device state until reset or reprogramming. Important state includes VM context enable/depth/block-size configuration, page-table base/start/end ranges, L2 cache and TLB enablement, protection-fault policy, fault status/address latches, invalidation sem/request/ack state, aperture bounds, per-VF virtualization windows, ATS enablement, clock-gating controls, and perf-counter selection/counter values.

Some fields are clearly write-to-control or latch-clearing state, such as `CLEAR_PROTECTION_FAULT_STATUS_ADDR`, invalidation request bits, perf-counter `CLEAR`, and `CLEAR_ALL`. Others represent status sampled from hardware, such as L2 busy/parity bits, invalidation ack bits, fault status, active function ID, and counter values. The masks in this header do not encode access type, so callers must know from the register specification and driver sequence which fields are safe to write, read, or preserve.

## Dependencies And Integration Points

The header depends on its sibling generated register headers for complete use. `mmhub_9_4_1_offset.h` supplies the register addresses and base indices, while `mmhub_9_4_1_default.h` supplies reset/default values. This shift/mask file supplies the field-level layout used to preserve unrelated bits during read-modify-write operations.

The primary C integration point in this tree is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/mmhub_v9_4.c`. That file uses SOC15 register helpers such as `RREG32_SOC15`, `WREG32_SOC15_OFFSET`, and `SOC15_REG_OFFSET`, plus `REG_SET_FIELD`, to initialize MMHUB instances, VM contexts, apertures, L2 cache, invalidation ranges, and fault policies.

The macros integrate indirectly with broader AMDGPU subsystems: GMC/GART setup provides page-table and aperture values; GPUVM uses the `amdgpu_vmhub` register offsets for invalidations and VMID management; SR-IOV paths branch around PF-only programming; RAS and debug flows may inspect MMHUB status/counter/error registers; power-management and clock-gating code uses related UTCL2/MMHUB fields.

The generated naming convention is also an integration contract. `REG_SET_FIELD` expects symbols shaped as `<register>__<field>_MASK` and `<register>__<field>__SHIFT`; if either name or bit range drifts from the offset/default headers or from the ASIC register spec, register programming compiles but can program the wrong hardware bits.

## Risks And Edge Cases

Manual edits are high risk because the file is generated register metadata. A single wrong mask or shift can corrupt MMHUB address translation, invalidate the wrong VMIDs, route faults incorrectly, break SR-IOV isolation, or make perf/RAS/debug information misleading.

This chunk uses the `*1` register namespace, while the visible `mmhub_v9_4.c` initialization often programs `*0` registers plus a per-instance offset. That makes naming consistency important: users must select the register namespace that matches the offset being used rather than assuming all similarly named fields are interchangeable across PF/VC/HV blocks.

Repeated context and invalidation-engine macros are easy to misuse. Contexts 0-15 and engines 0-17 have similar field layouts but different address strides. Driver code must use the correct `ctx_distance`, `ctx_addr_distance`, `eng_distance`, and `eng_addr_distance`; otherwise a VMID or invalidate engine update can hit the wrong register.

Address split fields are narrow in their high half, commonly 4 bits after page-number shifts. Incorrect shifting, using byte addresses where page numbers are expected, or truncating high bits can silently constrain the GART/VM aperture or page-table address range.

Fault-control fields mix default-page routing, interrupt policy, retry behavior, active page migration, and crash-on-fault behavior in adjacent bits. Preserving unrelated bits during read-modify-write is essential, especially when toggling `CRASH_ON_NO_RETRY_FAULT`, `CRASH_ON_RETRY_FAULT`, or retry fault interrupts.

SR-IOV and hypervisor fields, including per-VF framebuffer sizing, per-VF ATS control, active function ID, and XGMI GPUIOV enablement, are security-sensitive. Wrong masks can expose memory apertures to the wrong function or leave translation/cache behavior inconsistent between PF and VFs.

Perf-counter fields include selection ranges and trigger controls. Incorrect mode, trigger, or clear handling can return plausible but wrong telemetry and can interfere with concurrent diagnostic users if counters are shared.

## Test Signals

Build coverage should compile the AMDGPU driver paths that include `mmhub_9_4_1_sh_mask.h`, especially `mmhub_v9_4.c`, with warnings treated seriously. Macro-name drift usually appears as compile failures in `REG_SET_FIELD` or SOC15 register references.

Static validation should compare this generated header against the corresponding ASIC register source used to produce `mmhub_9_4_1_offset.h` and `mmhub_9_4_1_default.h`. A useful check is that every field macro pair has both a `_MASK` and `__SHIFT`, and that masks align with their shifts and expected widths.

Runtime smoke tests should cover MMHUB GART enable/disable on supported hardware: page-table base programming, system aperture setup, L1 TLB/L2 cache enablement, VMID context setup, and invalidation request/ack completion across both MMHUB instances.

VM fault tests should deliberately trigger invalid, permission, read/write, and execute faults and verify status decoding, default-page routing, crash/no-crash policy, and interrupt behavior. Tests should include both normal PF paths and SR-IOV VF/PF configurations where PF-only registers are skipped or hypervisor fields apply.

Addressing tests should exercise high framebuffer/GART/VM addresses to catch low/high split mistakes in page-table base/start/end, aperture default address, identity aperture, and protection fault default address fields.

Invalidation tests should verify all 18 invalidation engines can program full-range and targeted-range invalidations, set the intended VMID bits, and observe the matching ack without disturbing neighboring engine registers.

Performance and diagnostic tests should program the ATC L2 and VM L2 perf counters, clear them, select events, run a known MMHUB workload, and verify counters increment and saturate/stop according to the control bits.
