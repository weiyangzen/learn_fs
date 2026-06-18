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
