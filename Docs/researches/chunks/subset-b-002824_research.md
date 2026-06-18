# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mmhub/mmhub_9_1_sh_mask.h lines 1-2337

## Scope

This chunk is the opening portion of the generated AMDGPU MMHUB 9.1 shift/mask header. It contains C preprocessor definitions for the `mmhub_dagbdec` address block, not executable driver code. The file uses the standard generated AMD register-field convention:

- `<REGISTER>__<FIELD>__SHIFT` gives the low bit position of a field.
- `<REGISTER>__<FIELD>_MASK` gives the raw 32-bit mask for that field.

The covered range starts with the license and `_mmhub_9_1_SH_MASK_HEADER` include guard, then defines DAGB0 read-side and write-side arbitration, credit, virtual-channel, bandwidth, outstanding-request, burst, lazy-timer, clock-gating, and pending-status fields. The chunk ends at line 2337 inside `DAGB0_WR_VC7_CNTL`, after `DAGB0_WR_VC7_CNTL__OSD_LIMITER_ENABLE_MASK`; `DAGB0_WR_VC7_CNTL__MAX_OSD_MASK` is on line 2338 and belongs to the next chunk/reconciliation context.

## Purpose

The purpose of this header section is to let MMHUB 9.1 driver code compose and decode MMIO register values for the DAGB0 decoder/arbiter path without hard-coding bit numbers. These fields describe how read and write clients are mapped to virtual channels, how bandwidth and outstanding request limits are applied, how credit pools and burst timers are configured, and how clock-gating/light-sleep overrides are controlled for the MMHUB data/address gateway.

Although this repository path is under `distributed-fs/ceph-client`, the source file is AMD GPU driver hardware metadata. It is unrelated to Ceph filesystem behavior except by being part of the mirrored source tree.

## Important Macro Families

Read client controls:

- `DAGB0_RDCLI0` through `DAGB0_RDCLI31` repeat the same 10 fields for 32 read clients: `VIRT_CHAN`, `CHECK_TLB_CREDIT`, `URG_HIGH`, `URG_LOW`, `MAX_BW_ENABLE`, `MAX_BW`, `MIN_BW_ENABLE`, `MIN_BW`, `OSD_LIMITER_ENABLE`, and `MAX_OSD`.
- These fields map each read client to one of the DAGB virtual channels, tune urgency thresholds, optionally enforce min/max bandwidth, and optionally limit outstanding transactions.

Read global and per-channel controls:

- `DAGB0_RD_CNTL` defines global read-side knobs: `SCLK_FREQ`, client and virtual-channel bandwidth-window sizes, IO level override, compliant VC selection, and shared VC count.
- `DAGB0_RD_GMI_CNTL` defines read-side GMI credit, level, max-burst, and lazy-timer fields.
- `DAGB0_RD_ADDR_DAGB` controls read address-DAGB enable bits, jump-ahead behavior, self-initialization disablement, and `WHOAMI`.
- `DAGB0_RD_OUTPUT_DAGB_MAX_BURST` and `DAGB0_RD_OUTPUT_DAGB_LAZY_TIMER` pack per-VC fields for VC0-VC7.
- `DAGB0_RD_ADDR_DAGB_MAX_BURST0..3` and `DAGB0_RD_ADDR_DAGB_LAZY_TIMER0..3` pack per-client values for clients 0-31 in groups of eight.
- `DAGB0_RD_VC0_CNTL` through `DAGB0_RD_VC7_CNTL` repeat per-virtual-channel storage credit, EA credit, max/min bandwidth, and max outstanding request fields.
- `DAGB0_RD_CNTL_MISC` defines storage pool credit, EA pool credit, IO EA credit, legacy coherency mode bits, and `UTCL2_CID`.
- `DAGB0_RD_TLB_CREDIT` defines normal and atomic TLB credit fields.

Read status/pending indicators:

- `DAGB0_RDCLI_ASK_PENDING`, `DAGB0_RDCLI_GO_PENDING`, `DAGB0_RDCLI_GBLSEND_PENDING`, `DAGB0_RDCLI_TLB_PENDING`, `DAGB0_RDCLI_OARB_PENDING`, and `DAGB0_RDCLI_OSD_PENDING` each expose a 32-bit `ID` mask for per-client pending state.

Write client controls:

- `DAGB0_WRCLI0` through `DAGB0_WRCLI31` mirror the read-client layout for write clients, with the same virtual channel, TLB credit check, urgency, min/max bandwidth, and outstanding request limiter fields.
- `DAGB0_WR_CNTL`, `DAGB0_WR_GMI_CNTL`, `DAGB0_WR_ADDR_DAGB`, `DAGB0_WR_OUTPUT_DAGB_MAX_BURST`, and `DAGB0_WR_OUTPUT_DAGB_LAZY_TIMER` mirror the global read-side register shapes for write-side address/data flow.
- `DAGB0_WR_ADDR_DAGB_MAX_BURST0..3` and `DAGB0_WR_ADDR_DAGB_LAZY_TIMER0..3` define per-client address-DAGB burst and lazy-timer tuning for clients 0-31.
- `DAGB0_WR_DATA_DAGB`, `DAGB0_WR_DATA_DAGB_MAX_BURST0..3`, and `DAGB0_WR_DATA_DAGB_LAZY_TIMER0..3` define equivalent write data-DAGB enable, identity, burst, and lazy-timer fields.
- `DAGB0_WR_VC0_CNTL` through the partial `DAGB0_WR_VC7_CNTL` define per-virtual-channel write-side storage/EA credits and bandwidth/outstanding limits. The final `MAX_OSD_MASK` for VC7 is just outside this exact line range.

Clock-gating and light-sleep controls:

- `DAGB0_RD_CGTT_CLK_CTRL`, `DAGB0_L1TLB_RD_CGTT_CLK_CTRL`, and `DAGB0_ATCVM_RD_CGTT_CLK_CTRL` define read-side `ON_DELAY`, `OFF_HYSTERESIS`, `SOFT_STALL_OVERRIDE`, and light-sleep override bits for write/read/return/register paths.
- `DAGB0_WR_CGTT_CLK_CTRL`, `DAGB0_L1TLB_WR_CGTT_CLK_CTRL`, and `DAGB0_ATCVM_WR_CGTT_CLK_CTRL` define the matching write-side clock-gating controls.

## Control Flow and Data Flow

This header has no runtime control flow. It participates in compile-time preprocessing only.

The implied consumer flow is:

1. Include the matching `mmhub_9_1_offset.h` register-address header and this `mmhub_9_1_sh_mask.h` field-layout header.
2. Select an MMHUB register such as `mmDAGB0_RDCLI0`, `mmDAGB0_RD_CNTL`, `mmDAGB0_WRCLI0`, or `mmDAGB0_WR_VC0_CNTL` from the offset header.
3. Use AMDGPU/SOC15 helper macros such as register read/write helpers and field set/get helpers to compose or decode 32-bit MMIO values using these `__SHIFT` and `_MASK` constants.
4. Let the caller enforce ordering, idleness, reset, firmware, and power-management sequencing. Those semantics are not represented in this generated header.

The data flow represented by the bitfields is hardware configuration state: per-client requests enter DAGB0, are assigned to virtual channels, consume TLB/storage/EA credits, are throttled by bandwidth and outstanding-request fields, and are shaped by burst and lazy-timer fields before leaving the MMHUB gateway. Pending-state registers provide status visibility for read clients, while clock-gating registers influence when parts of the path can stall, gate, or enter light sleep.

## State and Persistence Behavior

The macros persist no software state. They name bit positions for hardware MMIO registers whose state lives in the GPU.

Configuration-like state includes client-to-VC mappings, urgency thresholds, bandwidth windows, min/max bandwidth limits, outstanding request limits, storage and EA credits, TLB credits, GMI credit/level/burst/timer values, per-client burst and lazy-timer fields, `DAGB_ENABLE`, jump-ahead behavior, self-initialization disablement, `WHOAMI`, and clock-gating/light-sleep override values.

Volatile or observational state includes the read-client pending ID masks for ask, go, global-send, TLB, output arbiter, and outstanding-status domains. These status fields are hardware-produced and may change as requests drain or stall.

Action-like fields are mostly configuration actions rather than one-shot commands. Misprogramming enable bits, credit values, burst timers, or clock-gating overrides can alter live memory-traffic behavior immediately. The header does not encode reset defaults, reserved-bit policy, read-only/write-only access type, latch behavior, or safe update sequencing.

## Dependencies and Integration Points

Key dependencies:

- `mmhub_9_1_offset.h` supplies the matching MMIO offsets and base-index constants for these register names. For this chunk, the companion offset header maps registers such as `mmDAGB0_RDCLI0`, `mmDAGB0_RD_CNTL`, `mmDAGB0_WRCLI0`, and `mmDAGB0_WR_VC7_CNTL` to concrete MMHUB addresses.
- AMDGPU generated-register helper conventions depend on the exact suffixes `__SHIFT` and `_MASK`.
- Consumer code must include the SOC15 register helper stack that knows how to address MMHUB registers for the selected ASIC instance.
- Adjacent chunks are required for the complete MMHUB 9.1 field map; this chunk is only the first 2,337 lines of a 9,790-line header.

Observed integration points in this tree:

- `drivers/gpu/drm/amd/amdgpu/vcn_v1_0.c` includes `mmhub/mmhub_9_1_offset.h` and `mmhub/mmhub_9_1_sh_mask.h` alongside VCN 1.0 register headers, making MMHUB 9.1 fields available during VCN setup and control paths.
- `drivers/gpu/drm/amd/display/dc/resource/dcn10/dcn10_resource.c` includes the same MMHUB 9.1 offset and shift/mask headers in DCN 1.0 display resource code.
- Other MMHUB generation headers in the same directory follow the same register naming and repeated-field pattern, so cross-generation code and audits often compare these generated layouts against neighboring ASIC versions.

Primary hardware integration surfaces:

- MMHUB request arbitration and traffic shaping for read and write clients.
- Virtual-channel configuration across VC0-VC7.
- TLB/storage/EA credit accounting and throttling.
- GMI burst/timer behavior.
- Clock gating and light-sleep behavior for DAGB, L1 TLB, and ATCVM read/write paths.
- Read client pending diagnostics for hang or stall analysis.

## Risks and Edge Cases

- The largest risk is a mismatch between this shift/mask header and `mmhub_9_1_offset.h` or the ASIC register specification. The code can still compile while programming the wrong bits.
- This file is generated hardware metadata. Manual edits are high-risk because repeated families look nearly identical but map distinct clients, VCs, and offsets.
- Repeated client registers invite off-by-one mistakes. `RDCLI0..31` and `WRCLI0..31` share layouts but represent separate hardware clients.
- Packed per-client registers group clients 0-31 into groups of eight. Wrong group selection can silently tune a different client.
- Packed per-VC registers use 4-bit lanes for VC0-VC7. A wrong shift can affect an adjacent virtual channel.
- Bandwidth, credit, and outstanding-limit fields influence live memory-system behavior. Bad values can starve a client, overrun credits, reduce throughput, or contribute to GPU hangs.
- `CHECK_TLB_CREDIT` and TLB credit fields are tied to translation flow control. Incorrect values can interact badly with MMHUB VM/TLB invalidation and page-table traffic even though the VM registers are outside this chunk.
- Clock-gating fields may require idle or reset sequencing that is not visible in the header. Read-modify-write callers should preserve unrelated and reserved bits unless an ASIC-specific sequence intentionally writes a full default.
- Pending ID masks are status surfaces, not configuration knobs. Treating them as normal writable registers would be a consumer-code bug unless the hardware specification says otherwise.
- The exact requested chunk ends one line before the final mask for `DAGB0_WR_VC7_CNTL`. Whole-file reconciliation must not conclude that VC7 lacks `MAX_OSD_MASK`; it is present at line 2338, just outside this work item.

## Test and Verification Signals

Useful verification is mostly build, generated-header audit, and hardware integration coverage:

- Compile paths that include `mmhub_9_1_offset.h` and `mmhub_9_1_sh_mask.h`, including the VCN 1.0 and DCN 1.0 resource files observed in this tree.
- Static generated-header checks that each field has aligned `__SHIFT` and `_MASK` definitions, masks match the expected bit width, and repeated `RDCLI`, `WRCLI`, `RD_VC`, and `WR_VC` families are complete.
- Cross-check against `mmhub_9_1_offset.h` that every register family in this chunk has a companion `mm...` offset and base index.
- Cross-generation diff/audit against nearby MMHUB generated headers to catch unexpected layout drift for shared DAGB0 fields.
- Register readback after MMHUB initialization to confirm client VC mappings, bandwidth windows, credit fields, burst timers, and clock-gating controls decode as expected.
- GPU memory traffic stress tests covering read/write-heavy workloads, mixed display/video/compute traffic, VM pressure, and suspend/resume or reset recovery.
- Hang/stall diagnostics that compare `DAGB0_RDCLI_*_PENDING` status masks against expected in-flight clients when traffic is blocked or drained.
- Power-management tests that toggle clock gating/light sleep and verify that the DAGB, L1TLB, and ATCVM paths wake correctly without request loss or deadlock.

## Cross-Chunk Notes

This is the first chunk of the file and includes the license, include guard, and the start of `addressBlock: mmhub_dagbdec`. It covers complete read-side DAGB0 client/global/VC/status definitions and most write-side DAGB0 client/global/address/data/VC definitions through line 2337. The next chunk begins immediately after this range and should reconcile the final `DAGB0_WR_VC7_CNTL__MAX_OSD_MASK` line plus subsequent write-side miscellaneous, credit, pending, and later MMHUB field definitions.
