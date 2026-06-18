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
