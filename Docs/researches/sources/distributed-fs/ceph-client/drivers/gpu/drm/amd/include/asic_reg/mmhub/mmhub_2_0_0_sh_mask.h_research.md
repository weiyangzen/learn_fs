# Research: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mmhub/mmhub_2_0_0_sh_mask.h

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-002786`: lines 1-2453, `Docs/researches/chunks/subset-b-002786_research.md`
- `subset-b-002787`: lines 2454-4836, `Docs/researches/chunks/subset-b-002787_research.md`
- `subset-b-002788`: lines 4837-7297, `Docs/researches/chunks/subset-b-002788_research.md`
- `subset-b-002789`: lines 7298-7567, `Docs/researches/chunks/subset-b-002789_research.md`

## Chunk Research

### subset-b-002786: lines 1-2453

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mmhub/mmhub_2_0_0_sh_mask.h lines 1-2453

## Scope And Purpose

This chunk is the opening portion of the AMDGPU MMHUB 2.0.0 register mask header. It is a generated-style hardware contract file: each field in a 32-bit MMHUB register is exposed as a pair of preprocessor constants, `<REGISTER>__<FIELD>__SHIFT` and `<REGISTER>__<FIELD>_MASK`. There are no C functions, structs, enums, local variables, or executable branches in this range.

The covered source range starts with the MIT-style AMD license and include guard, then defines 2,162 mask/shift macros across 265 register-comment groups. Most of the range belongs to the `mmhub_dagbdec` address block, which describes DAGB0 read/write client arbitration, bandwidth, virtual-channel, TLB-credit, clock-gating, status, performance-counter, and reserved registers. The final part enters the `mmhub_mmea_mmeadec` address block and begins memory/DRAM client grouping and virtual-channel mapping definitions. The chunk ends at line 2453 after the first `MMEA0_DRAM_WR_LAZY__GROUP0_DELAY__SHIFT` macro, so that register's remaining fields are intentionally outside this chunk.

The companion offset header is `mmhub_2_0_0_offset.h`, not a `_d.h` file in this tree. It gives the register offsets and base indices; this header gives the bit layout used to compose or decode the 32-bit values at those offsets.

## Important APIs, Types, And Constants

There are no callable APIs or C types. The public interface is the macro namespace consumed by AMDGPU register helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `WREG32_SOC15*`, and `RREG32_SOC15*` in files that include this header.

The main constants in this chunk are:

- `DAGB0_RDCLI0` through `DAGB0_RDCLI18`: per-read-client control fields. Every client register uses the same layout: `VIRT_CHAN`, `CHECK_TLB_CREDIT`, `URG_HIGH`, `URG_LOW`, `MAX_BW_ENABLE`, `MAX_BW`, `MIN_BW_ENABLE`, `MIN_BW`, `OSD_LIMITER_ENABLE`, and `MAX_OSD`.
- `DAGB0_WRCLI0` through `DAGB0_WRCLI18`: matching per-write-client controls with the same virtual-channel, urgency, bandwidth, TLB-credit, and outstanding-request limiter fields.
- `DAGB0_RD_CNTL` and `DAGB0_WR_CNTL`: shared DAGB read/write control-window fields for SCLK frequency, client and virtual-channel max-bandwidth windows, IO level override/compliance, and shared VC count.
- `DAGB0_RD_GMI_CNTL` and `DAGB0_WR_GMI_CNTL`: GMI-facing credit, level, max-burst, and lazy-timer fields.
- `DAGB0_RD_ADDR_DAGB`, `DAGB0_WR_ADDR_DAGB`, and `DAGB0_WR_DATA_DAGB`: enable, jump-ahead, self-init-disable, and `WHOAMI` fields for address/data DAGB paths.
- Output, address-client, and data-client burst/lazy-timer registers: `*_OUTPUT_DAGB_MAX_BURST`, `*_OUTPUT_DAGB_LAZY_TIMER`, `*_ADDR_DAGB_MAX_BURST[0-2]`, `*_ADDR_DAGB_LAZY_TIMER[0-2]`, `*_DATA_DAGB_MAX_BURST[0-2]`, and `*_DATA_DAGB_LAZY_TIMER[0-2]`. These pack 4-bit values for VCs or clients into one 32-bit register.
- `DAGB0_RD_VC0_CNTL` through `DAGB0_RD_VC7_CNTL` and `DAGB0_WR_VC0_CNTL` through `DAGB0_WR_VC7_CNTL`: per-virtual-channel storage credit, EA credit, max/min bandwidth, OSD limiter, and max outstanding fields.
- `DAGB0_RD_CNTL_MISC` and `DAGB0_WR_CNTL_MISC`: storage-pool credit, EA-pool credit, IO EA credit, legacy cache-coherency mode bits, UTCL2 client ID, and HDP client ID.
- `DAGB0_RD_TLB_CREDIT` and `DAGB0_WR_TLB_CREDIT`: packed TLB0 through TLB5 credit fields.
- Pending/status bitmaps: `DAGB0_RDCLI_*_PENDING`, `DAGB0_WRCLI_*_PENDING`, `DAGB0_WRCLI_DBUS_*_PENDING`, `DAGB0_FIFO_EMPTY`, `DAGB0_FIFO_FULL`, `DAGB0_WR_CREDITS_FULL`, and `DAGB0_RD_CREDITS_FULL`.
- Write-side data and misc credit controls: `DAGB0_WR_DATA_CREDIT` and `DAGB0_WR_MISC_CREDIT`, including DLOCK VC credits, burst credits, atomic credit, OSD credit, and OSD DLOCK credit.
- `DAGB0_WRCLI_GPU_SNOOP_OVERRIDE` and `_VALUE`: full-width bitmaps controlling GPU snoop override enablement/value per client bit.
- `DAGB0_DAGB_DLY`, `DAGB0_CNTL_MISC`, and `DAGB0_CNTL_MISC2`: delay selection, EA VC remapping, bandwidth gap/init cycles, urgency boost/halt, clock-gating disable bits, busy-signal disable bits, swap control, and parity checking.
- `DAGB0_PERFCOUNTER_LO`, `DAGB0_PERFCOUNTER_HI`, `DAGB0_PERFCOUNTER0_CFG` through `2_CFG`, and `DAGB0_PERFCOUNTER_RSLT_CNTL`: performance-counter result, compare, event-select range, mode, enable, clear, start/stop trigger, global enable/clear, and stop-on-saturate fields.
- `DAGB0_RESERVE0` through `DAGB0_RESERVE131`: full-width reserved register masks. These preserve the generated register map alignment against the offset header.
- `MMEA0_DRAM_RD_CLI2GRP_MAP0/1` and `MMEA0_DRAM_WR_CLI2GRP_MAP0/1`: 2-bit client-ID to DRAM group maps for read and write clients 0-31.
- `MMEA0_DRAM_RD_GRP2VC_MAP` and `MMEA0_DRAM_WR_GRP2VC_MAP`: 3-bit mappings from DRAM groups 0-3 to virtual channels.
- `MMEA0_DRAM_RD_LAZY`: DRAM read group delay and request accumulation threshold/timeout/idle-max fields.
- `MMEA0_DRAM_WR_LAZY`: only the opening `GROUP0_DELAY__SHIFT` appears at this chunk boundary; masks and later shifts continue after line 2453.

## Control Flow And State Behavior

This file has no runtime control flow. The preprocessor substitutes constants into callers that perform MMIO register reads, writes, or read-modify-write updates.

Runtime state lives in the GPU MMHUB hardware registers. The DAGB0 client and VC fields configure traffic routing and quality-of-service behavior: virtual-channel selection, urgency thresholds, bandwidth windows, min/max bandwidth limits, outstanding request limits, and TLB-credit accounting. The control registers configure global read/write arbitration windows, GMI burst/lazy behavior, address/data DAGB enablement, and client/VC remapping.

The pending, FIFO, credit-full, and performance-counter registers are observable hardware status or counter state. Some fields are full-width bitmaps where each bit corresponds to a client, queue, or internal busy condition. Counter and result-control fields are stateful: `CLEAR`, `CLEAR_ALL`, `ENABLE`, trigger, and stop-on-saturate bits affect hardware counter accumulation and reset behavior.

Persistence is hardware-local. Values survive only according to MMHUB reset, power-gating, firmware, and driver initialization behavior. This header does not cache values, serialize register access, restore saved state, or protect callers from writing reserved or status-only fields.

## Dependencies And Integration Points

The immediate companion is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mmhub/mmhub_2_0_0_offset.h`. It places the `mmhub_dagbdec` block at base address `0x68000` and maps this chunk's DAGB0 registers from `mmDAGB0_RDCLI0` offset `0x0000` through `mmDAGB0_RESERVE131` offset `0x00ff`. It then starts `mmhub_mmea_mmeadec` with `mmMMEA0_DRAM_RD_CLI2GRP_MAP0` at `0x0100`, `mmMMEA0_DRAM_RD_LAZY` at `0x0106`, and `mmMMEA0_DRAM_WR_LAZY` at `0x0107`.

In this tree the header is included by `drivers/gpu/drm/amd/amdgpu/mmhub_v2_0.c`, which is the MMHUB 2.0 VM/GART/protection-fault implementation, and by `drivers/gpu/drm/amd/display/dc/irq/dcn30/irq_service_dcn30.c`, which pulls in MMHUB 2.0.0 register vocabulary alongside DCN 3.0 interrupt register definitions. Direct uses in `mmhub_v2_0.c` are mostly MMVM fields later in this same header, but the include establishes the ASIC-wide field namespace used by MMHUB code.

The same macro families appear in nearby generation headers such as `mmhub_9_1_sh_mask.h`, `mmhub_9_3_0_sh_mask.h`, and `mmhub_3_0_1_sh_mask.h`. Cross-generation similarities are useful for sanity checks, but the exact mask/shift values are generation-specific. For example, later headers can move or remove fields in `DAGB0_RD_CNTL`, so call sites must include the correct header for the target IP block.

## Risks And Edge Cases

- These macros are a hardware ABI. Any incorrect mask or shift can route traffic to the wrong virtual channel, change arbitration policy, alter TLB-credit behavior, or misread status bits while still compiling cleanly.
- Repeated client registers are visually repetitive. Copy/paste or regeneration errors can silently affect only one client, or can use a read-client macro for a write-client register with a same-shaped but wrong hardware target.
- Many registers pack repeated 2-bit, 3-bit, 4-bit, 5-bit, 6-bit, 7-bit, or 8-bit fields. Off-by-one shifts can produce plausible values while programming the wrong client/group/VC.
- Full-width masks such as `0xFFFFFFFFL` should be handled as unsigned 32-bit quantities. Signed promotion or printing through the wrong format can confuse debug output and register-dump comparisons.
- Pending, FIFO, credit, and performance-counter fields may be read-only, sticky, write-one-to-clear, or otherwise side-effectful depending on hardware semantics. The header only names bit positions; it does not encode access type.
- The reserved-register masks preserve map shape, not a promise that software can safely write those registers. Normal code should avoid touching `DAGB0_RESERVE*` unless a hardware programming guide explicitly requires it.
- The chunk boundary splits `MMEA0_DRAM_WR_LAZY`. Merge/reconciliation should combine this document with the next chunk before making whole-file statements about all fields in that register.

## Test And Validation Signals

There are no direct unit tests for this macro-only header chunk. Useful validation is compile-time, static, and hardware-oriented:

- Build AMDGPU configurations that include `mmhub_2_0_0_sh_mask.h`, especially MMHUB 2.0 and DCN 3.0 paths.
- Run static mask/shift consistency checks: single-bit masks should match their shift; multi-bit masks should be contiguous; repeated packed fields should be non-overlapping and cover the intended bit ranges; full-width masks should have shift zero.
- Compare `mmhub_2_0_0_sh_mask.h` against `mmhub_2_0_0_offset.h` so every register-comment group in this chunk has a matching `mm*` offset and `_BASE_IDX`.
- On supported hardware, compare MMHUB register dumps before and after VM/GART initialization, power transitions, and display initialization to confirm only expected MMHUB registers change.
- Exercise MMHUB protection-fault and VM invalidation paths in `mmhub_v2_0.c` for general include coverage, then inspect register dumps if DAGB0/DRAM QoS settings are changed by firmware or driver initialization.
- For performance-counter fields, validate that enabling, clearing, selecting events, and reading high/low counter parts produces monotonic or reset behavior expected by the hardware guide.

## Chunk Notes For Merge Lane

This is the first chunk of a larger `mmhub_2_0_0_sh_mask.h` register mask header. Whole-file research should treat it as the DAGB0 arbitration/QoS/status/performance-counter section plus the beginning of MMEA0 DRAM group mapping, and should defer complete coverage of `MMEA0_DRAM_WR_LAZY` to the following chunk.

### subset-b-002787: lines 2454-4836

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mmhub/mmhub_2_0_0_sh_mask.h lines 2454-4836

## Chunk Scope

This chunk is a middle slice of the generated AMD MMHUB 2.0.0 shift/mask header. It covers source lines 2454-4836 and contains only C preprocessor register-field constants: `<REGISTER>__<FIELD>__SHIFT` and `<REGISTER>__<FIELD>_MASK`. It starts inside the `MMEA0_DRAM_WR_LAZY` register definition and ends inside `MM_ATC_L2_CNTL2`, so both boundary registers require neighboring chunks for a complete whole-file merge.

The chunk is not executable C. Its purpose is to provide stable bitfield metadata for AMDGPU MMHUB programming code that composes, reads, masks, or decodes 32-bit MMHUB register values.

## Purpose And Hardware Area

The visible register definitions describe several MMHUB sub-blocks:

- `MMEA0_*` memory engine arbitration, DRAM/IO address decode, client grouping, SDP crediting, latency sampling, performance counters, EDC status, DSM control, clock gating, and error state.
- `mmhub_pctldec` / `PCTL*` power-control and register-engine fields, including deep-sleep controls, register save ranges, exclusions, PCTL RENG RAM access, execution triggers, tile idle thresholds, and PCTL performance counters.
- `mmhub_l1tlb_mmvml1pfdec`, `mmhub_l1tlb_mmvml1pldec`, and `mmhub_l1tlb_mmvml1prdec` L1 TLB status/performance-counter fields.
- The beginning of `mmhub_mmutcl2_mmatcl2dec`, covering `MM_ATC_L2_CNTL` and the first part of `MM_ATC_L2_CNTL2`, which are ATC L2 translation/cache-control fields.

Within the larger AMDGPU driver, this header is normally paired with generated offset headers and consumed by MMHUB/GC/gmc initialization, power-management, fault handling, debug/performance, and register read-modify-write helpers. The constants let callers avoid hard-coded bit arithmetic at the use site.

## Important Definitions

This chunk defines no functions, structs, enums, inline helpers, storage objects, or exported symbols. The important API surface is the macro naming contract.

Each field normally appears as two macros:

- `...__SHIFT`: the low bit position used before inserting or after extracting a field.
- `..._MASK`: the full field mask in the register's 32-bit value.

Major `MMEA0` register groups in this slice include:

- DRAM arbitration and throttling fields: `MMEA0_DRAM_RD_CAM_CNTL`, `MMEA0_DRAM_WR_CAM_CNTL`, `MMEA0_DRAM_PAGE_BURST`, read/write priority age, queuing, fixed, urgency, and quantum-priority registers.
- Address normalization and DRAM hole control: `MMEA0_ADDRNORM_BASE_ADDR*`, `MMEA0_ADDRNORM_LIMIT_ADDR*`, `MMEA0_ADDRNORM_OFFSET_ADDR1`, `MMEA0_ADDRNORMDRAM_HOLE_CNTL`, and non-power-of-two channel configuration.
- Address decode/hash/harvest fields: `MMEA0_ADDRDEC_BANK_CFG`, `MMEA0_ADDRDEC_MISC_CFG`, `MMEA0_ADDRDECDRAM_ADDR_HASH_*`, `MMEA0_ADDRDECDRAM_HARVEST_ENABLE`, and harvest address start/end registers.
- Chip-select decode programming: `MMEA0_ADDRDEC0_*` and `MMEA0_ADDRDEC1_*` base, mask, config, bank/row selection, column selection, and RM selection registers for CS01/CS23 and secondary chip-select variants.
- IO client mapping and priority fields: `MMEA0_IO_RD_CLI2GRP_MAP*`, `MMEA0_IO_WR_CLI2GRP_MAP*`, combine flush, group burst, read/write age/queuing/fixed/urgency/masking, and quantum-priority registers.
- SDP arbitration/credit fields: `MMEA0_SDP_ARB_DRAM`, `MMEA0_SDP_ARB_FINAL`, `MMEA0_SDP_DRAM_PRIORITY`, `MMEA0_SDP_IO_PRIORITY`, `MMEA0_SDP_CREDITS`, `MMEA0_SDP_TAG_RESERVE*`, `MMEA0_SDP_VCC_RESERVE*`, `MMEA0_SDP_VCD_RESERVE*`, and `MMEA0_SDP_REQ_CNTL`.
- Observability and reliability fields: `MMEA0_LATENCY_SAMPLING`, `MMEA0_PERFCOUNTER_LO/HI`, `MMEA0_PERFCOUNTER0_CFG`, `MMEA0_PERFCOUNTER1_CFG`, `MMEA0_PERFCOUNTER_RSLT_CNTL`, `MMEA0_EDC_CNT`, `MMEA0_EDC_CNT2`, `MMEA0_ERR_STATUS`, and `MMEA0_MISC2`.
- Power/clock/DSM fields: `MMEA0_DSM_CNTL`, `MMEA0_DSM_CNTLA`, `MMEA0_DSM_CNTL2`, `MMEA0_DSM_CNTL2A`, `MMEA0_CGTT_CLK_CTRL`, `MMEA0_EDC_MODE`, and `MMEA0_ADDRDEC_SELECT`.

The `PCTL` section contains:

- Global deep-sleep controls: `PCTL_MISC`, `PCTL_MMHUB_DEEPSLEEP`, `PCTL_MMHUB_DEEPSLEEP_OVERRIDE`, `PCTL_PG_IGNORE_DEEPSLEEP`, and `PCTL_PG_DAGB`.
- Register-engine access and execution fields for engines 0-2: `PCTL{0,1,2}_RENG_RAM_INDEX`, `PCTL{0,1,2}_RENG_RAM_DATA`, and `PCTL{0,1,2}_RENG_EXECUTE`.
- Save/restore range fields: `PCTL{0,1,2}_STCTRL_REGISTER_SAVE_RANGE0` through `RANGE4`, plus exclusion sets `EXCL_SET` and `EXCL_SET1`.
- Per-engine misc fields: `PCTL{0,1,2}_MISC` with critical-register locks, tile-idle thresholds, memory light-sleep enable, PGFSM command-done force, deep-sleep disconnect for PCTL1/PCTL2, register-engine execution triggers, and read-timer enable.
- PCTL performance counters: `PCTL_PERFCOUNTER_LO`, `PCTL_PERFCOUNTER_HI`, `PCTL_PERFCOUNTER0_CFG`, `PCTL_PERFCOUNTER1_CFG`, and `PCTL_PERFCOUNTER_RSLT_CNTL`.

The L1 TLB and ATC L2 section includes:

- `MMMC_VM_MX_L1_TLB0_STATUS` through `MMMC_VM_MX_L1_TLB7_STATUS`, each exposing `BUSY` and `FOUND_PARITY_ERRORS`.
- `MMMC_VM_MX_L1_PERFCOUNTER0_CFG` through `PERFCOUNTER3_CFG`, result control, and low/high counter value fields.
- `MM_ATC_L2_CNTL`, with translation request count controls, address-mod-dependent request behavior, cache invalidation mode, and default-page-out-to-system-memory enable.
- The visible part of `MM_ATC_L2_CNTL2`, with bank selection and L2 cache update/cache-tag/VMID-mode related fields.

## Control Flow

There is no runtime control flow in this chunk. Including code uses these macros through normal C preprocessor expansion. Effective control flow appears in consumers that do things such as:

- Build a register value by shifting a caller-selected field value by `__SHIFT` and masking with `_MASK`.
- Read a hardware register and decode individual fields with `_MASK` and `__SHIFT`.
- Perform read-modify-write operations where the mask clears a field and the shifted value inserts the replacement.
- Configure performance counter selection, enable, clear, and result controls for debug/telemetry paths.
- Poll status fields such as L1 TLB `BUSY` or parity-error bits after hardware operations.

Because the chunk is generated bit metadata, control-flow correctness depends on consumers using the paired shift/mask consistently and on the macro values matching the ASIC register specification.

## State And Persistence Behavior

The header itself has no state and persists no data. The fields it describes are hardware state:

- `ADDRDEC*`, `ADDRNORM*`, harvest, hash, and channel fields affect persistent-in-hardware address mapping while the GPU is initialized or active.
- Priority, burst, CAM, queueing, urgency, lazy-accumulation, and SDP credit fields tune arbitration behavior for MMHUB traffic classes and virtual channels.
- `PCTL*` fields control power-gating/deep-sleep behavior and register save/restore ranges that matter across low-power transitions.
- Performance-counter and latency-sampling fields represent transient observability state and debug instrumentation.
- EDC, parity, and error-status fields expose reliability counters or sticky hardware error conditions, depending on consumer handling in adjacent driver code.

State lifetime is therefore controlled by MMIO/SOC register programming code outside this header. Reloading the driver or resetting hardware can change the values even though the macro definitions are compile-time constants.

## Dependencies And Integration Points

This file depends only on the C preprocessor and the include guard from the whole header. There are no included headers in this chunk.

Practical dependencies are external and implicit:

- Generated register offset/address headers for `mmhub_2_0_0`, which provide register addresses corresponding to these field-layout macros.
- AMDGPU register helper macros/functions, commonly used to compose register values and perform MMIO reads/writes.
- ASIC-specific MMHUB/GMC code that knows when each register can be accessed, whether a field is writeable, reset-only, debug-only, or status-only, and what sequencing is safe around clock/power-gated blocks.
- Firmware/SMU/power-management paths that may also touch deep-sleep, power-gating, or register-save controls.

The comments `// addressBlock: ...` are important integration markers from the generator. They group registers by hardware decoder block and help later merge or audit scripts keep this chunk aligned with offset definitions and the hardware XML/source spec.

## Risks

- Boundary incompleteness: the chunk starts after the first field of `MMEA0_DRAM_WR_LAZY` and stops before the full `MM_ATC_L2_CNTL2` definition is visible. The final merged per-file report should reconcile neighboring chunks before claiming complete register coverage.
- Generated-header drift: any mismatch between these masks/shifts and the matching offset header or hardware spec can silently corrupt register programming. Build tests may pass while runtime MMIO behavior fails.
- Read/write semantic ambiguity: masks alone do not identify read-only, write-one-to-clear, sticky, reset-only, or protected fields. Consumers must rely on register documentation and established AMDGPU sequencing.
- Bitfield overlap errors are high impact. Many registers pack multiple fields into 32 bits; a wrong mask or shift can affect unrelated hardware behavior.
- Power-management hazards: `PCTL*` deep-sleep, register-save, and critical-lock fields can interact with power-gated or clock-gated hardware. Incorrect use can cause hangs, lost register state, or failed resume.
- Address-decode hazards: `MMEA0_ADDRDEC*`, `ADDRNORM*`, hash, harvest, and chip-select fields define memory mapping behavior. Wrong programming can break VRAM access, page translation, or memory channel routing.
- Debug/perf-counter side effects: clear/enable/result-control fields for perf counters can be destructive to in-flight measurements and should be coordinated with any shared debug tooling.

## Test Signals

Useful validation signals for this chunk are mostly build-time and hardware-integration oriented:

- Compile AMDGPU code that includes `mmhub_2_0_0_sh_mask.h` together with its matching offset headers; missing or renamed macros should fail at compile time.
- Static checks can verify every `__SHIFT` field has a matching `_MASK` and that masks align with the declared low bit and field width.
- Generator/regeneration diffs should be reviewed against the authoritative MMHUB 2.0.0 register specification, especially for address decode, PCTL, and ATC L2 fields.
- Hardware smoke tests should cover GPU initialization, VRAM access, VM fault handling, suspend/resume or runtime power management, and MMHUB reset paths.
- Debug/performance tests can exercise `MMEA0_*`, `PCTL_*`, and `MMMC_VM_MX_L1_*` performance counter enable/clear/read flows where supported by the ASIC.
- Reliability/error tests can inspect EDC/parity/status field reads, including `MMEA0_ERR_STATUS` and `MMMC_VM_MX_L1_TLB*_STATUS`, after controlled reset or error-injection scenarios if available.

## Cross-Chunk Notes

- Previous chunk should contain the start of `MMEA0_DRAM_WR_LAZY`, including at least `GROUP0_DELAY__SHIFT`.
- Next chunk should complete `MM_ATC_L2_CNTL2` and continue with `MM_ATC_L2_CACHE_DATA*`, `MM_ATC_L2_CNTL3`, and related ATC L2 definitions.
- The final per-file merge should not infer executable behavior from this header alone; it should combine this macro map with any adjacent generated register headers or consuming AMDGPU MMHUB code if those files are researched elsewhere.

### subset-b-002788: lines 4837-7297

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mmhub/mmhub_2_0_0_sh_mask.h lines 4837-7297

## Scope

This chunk is part of a generated AMDGPU MMHUB 2.0.0 shift/mask header. It contains C preprocessor constants for hardware register bit fields, not executable driver logic. Each field is represented by the generated AMD convention:

- `<REGISTER>__<FIELD>__SHIFT` for the field's low bit.
- `<REGISTER>__<FIELD>_MASK` for the raw 32-bit field mask.

The covered range starts mid-register in `MM_ATC_L2_CNTL2`, continues through MMHUB ATC L2, MMVM L2, VM context, invalidation, performance, SR-IOV framebuffer, MARC, IOMMU, and PCIe ATS field definitions, and ends after the first `MMVM_PCIE_ATS_CNTL_VF_0` field. The repository path is under `distributed-fs/ceph-client`, but this file is AMD GPU driver hardware metadata, not Ceph filesystem logic.

## Purpose

The purpose of this chunk is to keep MMHUB 2.0.0 driver code synchronized with the ASIC register specification for MMHUB address translation and IOMMU control. The macros let AMDGPU code compose and decode 32-bit MMIO register values with helper macros such as `REG_SET_FIELD` and `REG_GET_FIELD` while using companion offset headers for actual register addresses.

The main hardware surfaces described here are:

- ATC L2 translation-cache controls and status.
- MMVM L2 cache, page-walk, invalidation, protection-fault, identity-aperture, and parity/error controls.
- Sixteen VM contexts with repeated page-table control, base, start, and end registers.
- Eighteen invalidation engines with semaphore, request, acknowledgement, and address-range fields.
- MMVM L2 performance counters.
- SR-IOV virtual-function framebuffer size/offset windows.
- MARC base, relocation, length, enable, and read-only fields.
- IOMMU enable/performance-optimization and PCIe ATS enable fields.

## Important Macro Families

ATC L2 definitions:

- `MM_ATC_L2_CNTL2` defines bank selection, cache update mode, LRU update by write, tag-index swapping, VMID mode, and wildcard reference value fields.
- `MM_ATC_L2_CACHE_DATA0/1/2` define cache-entry readback/write data: register validity, cache-entry validity, cached attributes, virtual page address high/low, and physical page address.
- `MM_ATC_L2_CNTL3`, `MM_ATC_L2_STATUS`, and `MM_ATC_L2_STATUS2` expose invalidation delay, ATS request credits, clock-request hysteresis, busy state, and parity-error information.
- `MM_ATC_L2_MISC_CG`, `MM_ATC_L2_MEM_POWER_LS`, `MM_ATC_L2_CGTT_CLK_CTRL`, and `MM_ATC_L2_SDPPORT_CTRL` describe clock gating, memory light-sleep timing, soft override/stall controls, and SDP port clock-enable handshakes.

MMVM L2 and protection fault definitions:

- `MMVM_L2_CNTL`, `MMVM_L2_CNTL2`, `MMVM_L2_CNTL3`, `MMVM_L2_CNTL4`, and `MMVM_L2_CNTL5` control L2 cache enablement, fragment processing, endian swap modes, PDE/PTE cache behavior, default-page routing, invalidation controls, cache sizing/associativity/force-miss knobs, physical tap requests, IFIFO transaction limits, clock-gating overrides, and walker priority/small-fragment size.
- `MMVM_L2_STATUS` reports L2 busy, per-context/domain busy, and parity-error discovery for 4K PTE, bigK PTE, and PDE caches.
- `MMVM_DUMMY_PAGE_FAULT_*` and `MMVM_L2_PROTECTION_FAULT_DEFAULT_ADDR_*` define dummy/default page fault controls and fallback physical page addresses.
- `MMVM_L2_PROTECTION_FAULT_CNTL`, `CNTL2`, `MM_CNTL3`, and `MM_CNTL4` define clear/update behavior, default fault enables, retry/no-retry interrupt routing, active page migration behavior, crash-on-fault bits, and per-client no-retry masks.
- `MMVM_L2_PROTECTION_FAULT_STATUS` and `ADDR_LO32/HI32` decode latched fault details: more faults, walker error, permission faults, mapping error, client ID, read/write, atomic, VMID, VF flag, VFID, and faulting logical page.
- `MMVM_L2_CONTEXT1_IDENTITY_APERTURE_*` and `MMVM_L2_CONTEXT_IDENTITY_PHYSICAL_OFFSET_*` define identity-mapped logical aperture bounds and physical offsets for identity-access mode.
- `MMVM_L2_CACHE_PARITY_CNTL`, `MMVM_L2_IH_LOG_CNTL`, `MMVM_L2_IH_LOG_BUSY`, `MMVM_L2_GCR_CNTL`, and `MMVML2_WALKER_*_THROTTLE_*` cover parity checking/injection, interrupt-handler translation logging, per-VMID translation/invalidation busy state, GCR client selection, and page-walker macro/micro throttle windows.

VM context and invalidation definitions:

- `MMVM_CONTEXT0_CNTL` through `MMVM_CONTEXT15_CNTL` share the same layout: context enable, page-table depth, page-table block size, retry policy for permission/invalid/other faults, and interrupt/default handling for range, dummy-page, PDE0, valid, read, write, and execute protection faults.
- `MMVM_CONTEXTS_DISABLE` packs disable bits for contexts 0-15.
- `MMVM_INVALIDATE_ENG0_SEM` through `MMVM_INVALIDATE_ENG17_SEM` provide one semaphore bit per invalidation engine.
- `MMVM_INVALIDATE_ENG0_REQ` through `MMVM_INVALIDATE_ENG17_REQ` share the same request layout: 16-bit per-VMID invalidate request bitmap, flush type, invalidate L2 PTE/PDE0/PDE1/PDE2, invalidate L1 PTEs, clear protection fault status address, log request, and 4K-pages-only selection.
- `MMVM_INVALIDATE_ENG0_ACK` through `MMVM_INVALIDATE_ENG17_ACK` report per-VMID invalidate acknowledgements and semaphore state.
- `MMVM_INVALIDATE_ENG0_ADDR_RANGE_LO32/HI32` through `ENG17_ADDR_RANGE_LO32/HI32` define optional address-range invalidation state, including the low `S_BIT`, low logical page address bits, and high logical page address bits.
- `MMVM_CONTEXT0_PAGE_TABLE_BASE_ADDR_*` through `CONTEXT15_PAGE_TABLE_BASE_ADDR_*` hold page-directory-entry base addresses.
- `MMVM_CONTEXT0_PAGE_TABLE_START_ADDR_*` and `END_ADDR_*` through context 15 define logical page-number aperture start/end bounds.

Performance, virtualization, MARC, and ATS definitions:

- `MMMC_VM_L2_PERFCOUNTER0_CFG` through `PERFCOUNTER7_CFG` define selector start/end, mode, enable, and clear fields. `MMMC_VM_L2_PERFCOUNTER_RSLT_CNTL`, `MMMC_VM_L2_PERFCOUNTER_LO`, and `HI` provide selected counter readout, compare value, trigger selection, clear-all, enable-any, and stop-on-saturate behavior.
- `MMMC_VM_FB_SIZE_OFFSET_VF0` through `VF31` define 16-bit virtual-function framebuffer size and 16-bit offset fields for SR-IOV partitioning.
- `MMVM_IOMMU_MMIO_CNTRL_1` exposes `MARC_EN`.
- `MMMC_VM_MARC_BASE_LO/HI_0..3`, `MARC_RELOC_LO/HI_0..3`, and `MARC_LEN_LO/HI_0..3` define four MARC ranges with page-aligned base, relocation, length, enable, and read-only fields.
- `MMVM_IOMMU_CONTROL_REGISTER` exposes `IOMMUEN`; `MMVM_IOMMU_PERFORMANCE_OPTIMIZATION_CONTROL_REGISTER` exposes `PERFOPTEN`.
- `MMVM_PCIE_ATS_CNTL` exposes ATS `STU` and `ATC_ENABLE`; the chunk ends after `MMVM_PCIE_ATS_CNTL_VF_0__ATC_ENABLE`.

## Control Flow and Data Flow

This header has no runtime control flow. Its behavior is compile-time preprocessing. The implied consumer flow is:

1. Include the MMHUB 2.0.0 register offset header and this shift/mask header.
2. Select the appropriate `reg...` MMIO offset for an MMHUB register.
3. Use `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, or offset variants to compose, update, read, poll, or decode a 32-bit register.
4. Apply ordering, quiesce, reset, interrupt, and firmware coordination rules in the consumer driver code.

The field layout supports several regular data flows: MMHUB initialization programs L2 cache controls and context registers; VM update paths write page-table base/start/end registers; TLB invalidation paths write `MMVM_INVALIDATE_ENG*_REQ`, poll `ACK`, and coordinate with `SEM`; fault paths decode `MMVM_L2_PROTECTION_FAULT_STATUS` and address registers; SR-IOV setup writes VF framebuffer windows and VF ATS state; diagnostics configure performance counters, logging, parity injection, and read status registers.

Repository usage searches show these macro names are consumed by AMDGPU MMHUB generation files such as `amdgpu/mmhub_v3_*.c` and `amdgpu/mmhub_v4_*.c` with the same generated-header naming scheme. Those consumers initialize cache controls, context controls, invalidation requests, register spacing, and VM fault masks through AMD register helpers. This chunk itself only supplies the bit positions for the MMHUB 2.0.0 variant.

## State and Persistence Behavior

The macros persist no software state. The described state lives in hardware MMIO registers.

Durable configuration state includes L2 cache enablement and sizing, endian modes, identity aperture bounds, page-table bases and apertures for contexts 0-15, invalidation-engine address ranges, protection-fault policy, clock-gating/light-sleep settings, walker throttle limits, performance-counter configuration, VF framebuffer sizing, MARC mappings, IOMMU enablement, and ATS enablement.

Volatile or latched status includes ATC/MMVM busy bits, parity error information, per-domain busy state, protection-fault status/address, invalidation acknowledgements, per-VMID translation/invalidation logging busy bits, performance counter values, and fault/error discovery bits. Clear, latch, read-only, write-one-to-clear, and reset semantics are hardware-defined; the header exposes names and bit positions but not access rules.

Action-like fields include invalidation requests, protection-fault status clearing, performance-counter clear/clear-all, parity mismatch forcing, logging enable, crash-on-fault policy, and IOMMU/ATS enable bits. These fields can alter live memory-translation behavior and normally need strict sequencing around active GPU traffic.

## Dependencies and Integration Points

Key dependencies:

- The matching MMHUB 2.0.0 offset header must provide the corresponding register addresses for every `MM_ATC_*`, `MMVM_*`, and `MMMC_VM_*` register named here.
- AMDGPU register helpers depend on the exact generated suffixes `__SHIFT` and `_MASK`.
- MMHUB initialization, VM context setup, invalidation, reset recovery, suspend/resume, fault handling, SR-IOV, and diagnostics depend on these bit layouts matching the ASIC specification.
- Adjacent chunks are required for the complete file view. This chunk starts after earlier `MM_ATC_L2_CNTL2` fields and ends before the remaining `MMVM_PCIE_ATS_CNTL_VF_*` definitions.

Primary integration points:

- GPU virtual memory setup: context control, page-table base, start, and end registers define how MMHUB translates GPU virtual addresses.
- TLB and L2 invalidation: invalidation engines provide request/ack/semaphore flow and optional address-range invalidation for VMID-scoped cache maintenance.
- Fault handling and interrupts: protection-fault policy/status macros feed VM fault interrupt routing, retry behavior, page migration handling, and fault address decode.
- Power management: clock-gating, light-sleep, hysteresis, and soft override fields interact with power-gating and clock-gating sequences.
- SR-IOV and isolation: VF framebuffer size/offset fields, VF/VFID fault status, MARC ranges, and per-VF ATS controls are used to partition or identify virtualized traffic.
- Performance and diagnostics: L2 performance counters, parity controls, IH logging, busy status, and cache data registers support profiling and hardware debug.
- PCIe/IOMMU integration: IOMMU enable, performance optimization, ATC/ATS controls, and ATC L2 request/cache fields connect the MMHUB translation path to system IOMMU and PCIe address translation services.

## Risks and Edge Cases

- Header/offset generation mismatch is the highest risk. These masks can compile cleanly with the wrong register offsets but program the wrong hardware bits.
- The chunk boundary is artificial. A final per-file report must reconcile the preceding `MM_ATC_L2_CNTL2` fields and the following VF ATS fields to avoid incomplete register descriptions.
- Repeated register families invite off-by-one or wrong-distance errors. Contexts 0-15, invalidation engines 0-17, VFs 0-31, counters 0-7, and MARC ranges 0-3 have similar layouts but distinct offsets.
- VM context and aperture fields are safety-critical. Incorrect page-table depth, base, start, end, retry, or default fault policy can cause GPU VM faults, silent memory aliasing, or access outside intended apertures.
- Invalidation programming has liveness risk. Bad VMID masks, flush type, semaphore handling, or polling of `ACK` can leave stale translations, hang invalidation, or race active page-table updates.
- Fault controls can hide or over-escalate errors. Disabling interrupts/default routing may mask faults; enabling crash-on-fault bits can convert recoverable faults into GPU resets.
- Parity injection, force-miss, logging, and performance controls are diagnostic surfaces. Leaving them enabled outside tests can degrade performance, create artificial errors, or perturb timing-sensitive paths.
- SR-IOV framebuffer and MARC fields must preserve isolation. Misprogrammed VF size/offset, relocation, read-only, or enable fields can overlap guest apertures or expose host memory.
- Clock-gating and light-sleep fields may require idle-state sequencing not visible in the header. Read-modify-write should preserve reserved bits unless generation-specific code intentionally writes full defaults.
- ATS/IOMMU enablement depends on platform and PCIe/IOMMU state. Enabling ATC/ATS without matching system support or invalidation discipline can produce stale or unauthorized translations.

## Test and Verification Signals

Useful signals are mostly build, static audit, and hardware integration tests:

- Compile coverage for MMHUB 2.0.0 code paths that include the matching offset and shift/mask headers.
- Generated-header audits that every `__SHIFT` has a matching `_MASK`, masks align with shifts, repeated context/invalidation/VF/MARC families are complete, and companion offsets exist.
- Register readback tests after MMHUB initialization to confirm L2 cache controls, context controls, page-table bases, apertures, and invalidation engine spacing decode to expected values.
- GPU VM stress tests that exercise page-table updates, VMID switching, TLB invalidation, address-range invalidation, retry/no-retry faults, and suspend/resume or reset recovery.
- Fault-injection or negative-access tests that validate `MMVM_L2_PROTECTION_FAULT_STATUS`, fault address registers, interrupt routing, and clear behavior.
- SR-IOV tests with multiple VFs checking framebuffer partitioning, VF/VFID fault attribution, MARC isolation, and VF ATS enable/disable behavior.
- PCIe ATS/IOMMU tests on platforms with ATS enabled and disabled, verifying translation correctness and invalidation ordering.
- Performance/debug tests that configure L2 counters, parity controls, IH logging, cache data registers, and busy/status registers without causing hangs or persistent side effects.

## Cross-Chunk Notes

This chunk begins at line 4837, after earlier `MM_ATC_L2_CNTL2` fields have already been defined in the previous chunk. It ends at line 7297 immediately after `MMVM_PCIE_ATS_CNTL_VF_0__ATC_ENABLE_MASK`; definitions for additional ATS VF registers continue in the next chunk. The later merge/reconciliation lane should combine adjacent chunks before drawing whole-file conclusions for `mmhub_2_0_0_sh_mask.h`.

### subset-b-002789: lines 7298-7567

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mmhub/mmhub_2_0_0_sh_mask.h lines 7298-7567

## Scope

This chunk is the final section of the generated AMDGPU MMHUB 2.0.0 shift/mask header. It contains C preprocessor constants for register bit positions and masks, not executable code. The constants are paired with register offsets from `mmhub_2_0_0_offset.h`, reset/default values from `mmhub_2_0_0_default.h`, and AMDGPU register helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32_SOC15`, and `WREG32_SOC15`.

The range starts in the per-virtual-function PCIe ATS control register family at `MMVM_PCIE_ATS_CNTL_VF_1`, then covers shared MMUTCL2/MMVM PF and VC decode registers, L1 TLB control, ATC L2 performance counter result registers, ATC L2 performance counter configuration registers, and the closing `#endif` for the header.

## Purpose

The macros define the software contract for programming and decoding MMHUB 2.0.0 memory-management registers. MMHUB is the memory hub used by non-graphics clients in AMDGPU. These fields support:

- PCIe ATS/ATC enablement per SR-IOV virtual function.
- MMUTCL2 clock-gating timing and software override controls.
- PF-visible physical/system memory aperture registers, default fault page address routing, virtual reset request state, and light-sleep timing.
- VC-visible framebuffer, AGP, system aperture, and L1 TLB controls used while enabling or disabling GART/VM translation.
- ATC L2 performance counter reads, event selection, trigger setup, clear operations, and saturation behavior.

Because this is a generated register header, its main purpose is ABI-like accuracy: callers rely on the exact `REGISTER__FIELD__SHIFT` and `REGISTER__FIELD_MASK` names and values when composing 32-bit MMIO writes for this ASIC generation.

## Important Macro Families

PCIe ATS and SR-IOV virtual functions:

- `MMVM_PCIE_ATS_CNTL_VF_1` through `MMVM_PCIE_ATS_CNTL_VF_31` each expose only `ATC_ENABLE` at bit 31 (`0x80000000L`).
- The immediately preceding context in the same header includes the root `MMVM_PCIE_ATS_CNTL` fields (`STU` and `ATC_ENABLE`) and `MMVM_PCIE_ATS_CNTL_VF_0`; this chunk continues that repeated VF series.
- The matching offsets in `mmhub_2_0_0_offset.h` place the registers contiguously from `mmMMVM_PCIE_ATS_CNTL_VF_1` at `0x0809` through `mmMMVM_PCIE_ATS_CNTL_VF_31` at `0x0827`, with base index 0.

Clock gating and active function state:

- `MMUTCL2_CGTT_CLK_CTRL` defines `ON_DELAY`, `OFF_HYSTERESIS`, `SOFT_OVERRIDE_EXTRA`, `MGLS_OVERRIDE`, `SOFT_STALL_OVERRIDE`, and `SOFT_OVERRIDE`. The 2.0.0 default is `0x00000080`, so reset state has part of the `OFF_HYSTERESIS` field set.
- `MMMC_SHARED_ACTIVE_FCN_ID` has a 5-bit `VFID` field and a high-bit `VF` flag, allowing software or firmware to identify whether the active function is a PF or a VF.

PF shared MMVM decode registers:

- `MMMC_VM_NB_MMIOBASE` and `MMMC_VM_NB_MMIOLIMIT` are full 32-bit fields for northbridge MMIO aperture bounds.
- `MMMC_VM_NB_PCI_CTRL` exposes `MMIOENABLE` at bit 23; `MMMC_VM_NB_PCI_ARB` exposes `VGA_HOLE` at bit 3.
- `MMMC_VM_NB_TOP_OF_DRAM_SLOT1`, `MMMC_VM_NB_LOWER_TOP_OF_DRAM2`, and `MMMC_VM_NB_UPPER_TOP_OF_DRAM2` encode top-of-DRAM/TOM2 ranges, with high address fragments generally shifted by bit 23.
- `MMMC_VM_FB_OFFSET` is a 24-bit framebuffer offset field.
- `MMMC_VM_SYSTEM_APERTURE_DEFAULT_ADDR_LSB` and `_MSB` store the default physical page number used for unmapped or faulted system aperture accesses; the LSB register is 32 bits and the MSB register contributes 4 high bits.
- `MMMC_VM_STEERING` has a 2-bit `DEFAULT_STEERING` field and resets to `0x00000001`.
- `MMMC_SHARED_VIRT_RESET_REQ` exposes 31 VF reset request bits plus a PF bit at bit 31. `MMMC_SHARED_VIRT_RESET_REQ2` adds one additional VF bit.
- `MMMC_MEM_POWER_LS` defines light-sleep setup and hold timing; its reset default is `0x00000208`.
- `MMMC_VM_CACHEABLE_DRAM_ADDRESS_START` and `_END` define 20-bit cacheable DRAM aperture bounds.
- `MMMC_VM_APT_CNTL` contains `FORCE_MTYPE_UC` and `DIRECT_SYSTEM_EN`; the 2.0.0 version has only these two fields, while later MMHUB generations add additional APT policy bits.
- `MMMC_VM_LOCAL_HBM_ADDRESS_LOCK_CNTL`, `_START`, and `_END` define lock state and local HBM aperture bounds. The default end register is `0x000fffff`, meaning the full 20-bit field is set at reset.

VC shared MMVM decode registers:

- `MMMC_VM_FB_LOCATION_BASE` and `MMMC_VM_FB_LOCATION_TOP` describe the 24-bit framebuffer address window.
- `MMMC_VM_AGP_TOP`, `_BOT`, and `_BASE` describe the 24-bit AGP aperture programmed by the GART setup path.
- `MMMC_VM_SYSTEM_APERTURE_LOW_ADDR` and `_HIGH_ADDR` describe logical system aperture bounds with 30-bit fields.
- `MMMC_VM_MX_L1_TLB_CNTL` controls the MMHUB L1 TLB. It exposes `ENABLE_L1_TLB`, `SYSTEM_ACCESS_MODE`, `SYSTEM_APERTURE_UNMAPPED_ACCESS`, `ENABLE_ADVANCED_DRIVER_MODEL`, `ECO_BITS`, and `MTYPE`. Its default is `0x00000501`, and `mmhub_v2_0_init_tlb_regs()` rewrites key fields during GART enable.

ATC L2 performance counters:

- `MM_ATC_L2_PERFCOUNTER_LO` and `MM_ATC_L2_PERFCOUNTER_HI` provide the result readout. The low register is a full 32-bit counter fragment; the high register has a 16-bit high counter field plus a 16-bit `COMPARE_VALUE` field.
- `MM_ATC_L2_PERFCOUNTER0_CFG` and `MM_ATC_L2_PERFCOUNTER1_CFG` each expose 8-bit event select start/end fields, a 4-bit mode field, and `ENABLE`/`CLEAR` bits at bits 28 and 29.
- `MM_ATC_L2_PERFCOUNTER_RSLT_CNTL` selects the visible counter result and controls start/stop triggers, global enable, global clear, and stop-on-saturate behavior. Its reset/default value is `0x04000000`, so `STOP_ALL_ON_SATURATE` is set by default.

## Control Flow and Runtime Use

There is no function-level control flow in this header. Runtime control flow is in the MMHUB implementation files that include it. For MMHUB 2.0.0, `amdgpu/mmhub_v2_0.c` includes this header and its matching offset/default headers.

Key runtime flows supported by this chunk:

1. `mmhub_v2_0_gart_enable()` initializes GART and VM translation by calling aperture, TLB, cache, system-domain, identity-aperture, VMID, and invalidation setup routines.
2. `mmhub_v2_0_init_system_aperture_regs()` programs the AGP registers, system aperture low/high registers, default system aperture physical page registers, and protection fault default address registers. In SR-IOV VF mode it skips the AGP and system aperture low/high writes because those shared registers are PF-managed.
3. `mmhub_v2_0_init_tlb_regs()` reads `mmMMMC_VM_MX_L1_TLB_CNTL`, sets `ENABLE_L1_TLB`, `SYSTEM_ACCESS_MODE`, `ENABLE_ADVANCED_DRIVER_MODEL`, clears `SYSTEM_APERTURE_UNMAPPED_ACCESS`, sets `MTYPE` to uncached, and writes the register back.
4. `mmhub_v2_0_gart_disable()` disables all VM contexts and then clears `ENABLE_L1_TLB` and `ENABLE_ADVANCED_DRIVER_MODEL` in `MMMC_VM_MX_L1_TLB_CNTL`.
5. `mmhub_v2_0_update_medium_grain_clock_gating()` and `mmhub_v2_0_update_medium_grain_light_sleep()` use nearby MMHUB clock-gating registers; this chunk's `MMUTCL2_CGTT_CLK_CTRL` is part of the same clock/power-management register area even though the v2.0 code path directly toggles ATC L2 and DAGB registers.

The performance-counter macros define hardware observability controls, but the searched tree does not show an in-tree MMHUB 2.0 path actively programming `MM_ATC_L2_PERFCOUNTER*_CFG` with `REG_SET_FIELD`. They are still exported for debug/perf tooling or future driver paths that need the generated names.

## State and Persistence Behavior

The header itself stores no state. All state represented here lives in hardware MMIO registers and persists until GPU reset, power-domain loss, suspend/resume reinitialization, PF reprogramming, or explicit driver writes.

Important persistent hardware state:

- ATS enable bits for each VF determine whether a VF can use the address translation cache path. Incorrect persistence across reset or VF assignment would affect isolation and address translation behavior.
- System aperture, AGP, framebuffer, default page, local HBM, and cacheable DRAM bounds shape how MMHUB routes and translates memory accesses.
- `MMMC_VM_MX_L1_TLB_CNTL` controls whether L1 TLB caching and the advanced driver model are active. GART enable/disable paths intentionally mutate this register.
- Virtual reset request bits can be sticky coordination state between PF/VF management paths and should be treated as hardware-owned request state rather than ordinary scratch bits.
- ATC L2 performance counters are accumulating hardware state. `CLEAR`, `CLEAR_ALL`, and `STOP_ALL_ON_SATURATE` affect whether counters continue, reset, or stop when saturated.

The default header records reset values for the same register region: ATS defaults to disabled, APT control defaults to zero, L1 TLB control defaults to `0x00000501`, performance counters default to zero except result control with stop-on-saturate set, and the local HBM end field defaults to all ones in its 20-bit address field.

## Dependencies and Integration Points

Generated-register dependencies:

- `mmhub_2_0_0_offset.h` provides addresses such as `mmMMMC_VM_MX_L1_TLB_CNTL`, `mmMMMC_VM_SYSTEM_APERTURE_LOW_ADDR`, and `mmMM_ATC_L2_PERFCOUNTER_RSLT_CNTL`.
- `mmhub_2_0_0_default.h` provides the reset/default values used as safe initialization baselines.
- Other chunks of `mmhub_2_0_0_sh_mask.h` define the preceding main ATS register, VF0 ATS register, VM context registers, L2 cache/protection-fault registers, and invalidation engine fields that are programmed in the same MMHUB setup sequence.

Driver integration:

- `amdgpu/mmhub_v2_0.c` is the primary MMHUB 2.0 consumer. It programs GART apertures, system apertures, L1 TLB, L2 cache, VMID contexts, invalidation ranges, fault handling, and clock gating.
- Later MMHUB implementation files such as `mmhub_v3_0.c`, `mmhub_v3_3.c`, and `mmhub_v4_2_0.c` use equivalent field names where compatible, but offsets and some masks differ by generation. This chunk must stay paired with MMHUB 2.0.0 offsets and defaults.
- Display DC files include `mmhub_2_0_0_sh_mask.h` for generated register field visibility, but the searched direct uses of this chunk's functional fields are primarily in the AMDGPU MMHUB memory-management code.
- SR-IOV integration is visible through per-VF ATS registers, shared active-function IDs, virtual reset request registers, and driver branches such as `amdgpu_sriov_vf(adev)` that avoid programming PF-only shared aperture/cache registers from a VF.

## Risks and Edge Cases

- Mixing this mask header with offsets from another MMHUB generation can silently write the wrong bits. Later generations have similar names but different register layouts; for example, newer `MMMC_VM_APT_CNTL`, reset request, clock-gating, and framebuffer aperture layouts add or move fields.
- The chunk starts at `MMVM_PCIE_ATS_CNTL_VF_1`, so whole-file research must include the previous lines for the main ATS register and VF0. Treating this chunk alone as the complete ATS definition would miss the STU field and VF0 bit.
- Enabling `ATC_ENABLE` for the wrong VF can break isolation, translation correctness, or IOMMU/ATS expectations in SR-IOV deployments.
- Incorrect system aperture or framebuffer/AGP bounds can route MMHUB traffic to the wrong physical address range, causing VM faults, data corruption, or hangs.
- The default physical page registers are split across LSB/MSB page-number fields. Bad shifting when programming these fields can redirect faults/unmapped accesses to the wrong page.
- `MMMC_VM_MX_L1_TLB_CNTL` fields directly affect translation caching. Disabling the L1 TLB or advanced driver model at the wrong time can cause translation misses or performance collapse; enabling them before page-table/aperture setup can expose invalid translations.
- Virtual reset request registers are shared coordination points. Drivers should avoid treating them as local scratch state, especially under PF/VF management.
- Performance counter configuration can perturb observability if counters are not cleared, selected, or stopped consistently. The default stop-on-saturate bit means tests should account for counters ceasing to advance after saturation.

## Test and Verification Signals

Useful validation signals for this chunk are integration and hardware readback tests:

- Build coverage for MMHUB 2.0.0 paths that include `mmhub_2_0_0_sh_mask.h` and call `REG_SET_FIELD`/`REG_GET_FIELD` with these field names.
- Register readback after `mmhub_v2_0_gart_enable()` should show `MMMC_VM_MX_L1_TLB_CNTL.ENABLE_L1_TLB=1`, `ENABLE_ADVANCED_DRIVER_MODEL=1`, `SYSTEM_ACCESS_MODE=3`, and uncached `MTYPE` as programmed by `mmhub_v2_0_init_tlb_regs()`.
- Register readback after `mmhub_v2_0_gart_disable()` should show `ENABLE_L1_TLB=0` and `ENABLE_ADVANCED_DRIVER_MODEL=0`.
- GART/VM smoke tests should exercise AGP, framebuffer, and system aperture access ranges and confirm faults are redirected to configured default/fault pages rather than arbitrary memory.
- SR-IOV tests should verify VF paths do not attempt PF-only aperture/cache writes and that per-VF ATS enable/reset-request behavior is controlled by the expected function-management layer.
- Suspend/resume and GPU reset tests should confirm that aperture, TLB, and default page registers are restored after hardware state loss.
- Performance-counter validation can program `MM_ATC_L2_PERFCOUNTER0_CFG` or `1_CFG`, clear counters, enable triggers, generate MMHUB/ATC traffic, and read `MM_ATC_L2_PERFCOUNTER_LO/HI` while checking saturation and result-select behavior.

## Cross-Chunk Notes

This slice is the end of `mmhub_2_0_0_sh_mask.h`. It begins after the root `MMVM_PCIE_ATS_CNTL` and `MMVM_PCIE_ATS_CNTL_VF_0` definitions, so the final per-file document should merge this with the preceding chunk for a complete ATS description. It also relies on earlier chunks for VM context, invalidation, L2 cache, and protection-fault fields used by the same `mmhub_v2_0.c` setup sequence.
