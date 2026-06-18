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
