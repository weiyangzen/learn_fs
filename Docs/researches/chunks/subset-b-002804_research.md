# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mmhub/mmhub_3_0_1_sh_mask.h lines 2367-4844

## Scope And Purpose

This chunk is a generated AMDGPU MMHUB 3.0.1 register field-mask header segment. It contains preprocessor constants only: each hardware register field is represented as a `<REGISTER>__<FIELD>__SHIFT` macro and a matching `<REGISTER>__<FIELD>_MASK` macro. There are no C functions, structs, enums, variables, storage allocations, locks, loops, branches, or direct MMIO operations in this range.

The covered range defines 2,122 macros across 335 register-comment groups and 7 address blocks. It starts in the middle of `DAGB0_SDP_PRIORITY_OVERRIDE`, then completes the late `mmhub_dagbdec` SDP control/status section. It then covers `mmhub_pctldec` power-control/deepsleep fields, L1 TLB status/performance and TLS window fields, SAW context fields, ATC L2 cache/control/status/clock-gating fields, and the beginning of MMVM L2 control/protection-fault fields. The chunk ends in the middle of `MMVM_L2_PROTECTION_FAULT_CNTL2`; the remaining masks for that register and later MMVM fields are outside this work item.

The companion offset header is `mmhub_3_0_1_offset.h`. That file gives register offsets and base indices; this header gives the bit positions used by AMDGPU register helpers to build and decode 32-bit MMHUB register values.

## Important APIs, Types, And Constants

There are no callable APIs or C types in this header chunk. The public interface is the generated macro namespace consumed by helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, and their offset variants in MMHUB driver code.

Important macro families in this slice are:

- `DAGB0_SDP_PRIORITY_OVERRIDE`, `DAGB0_SDP_RD_PRIORITY`, and `DAGB0_SDP_WR_PRIORITY`: priority override fields for two selected clients plus packed per-VC read/write priorities for SDP traffic.
- `DAGB0_SDP_RD_CLI2SDP_VC_MAP` and `DAGB0_SDP_WR_CLI2SDP_VC_MAP`: maps SRT, NRT, DLOCK, HRT, IO, and GMI request classes into SDP virtual channels.
- `DAGB0_SDP_ENABLE`, `DAGB0_SDP_CREDITS`, `DAGB0_SDP_TAG_RESERVE0/1`, `DAGB0_SDP_VCC_RESERVE0/1`, and `DAGB0_SDP_VCD_RESERVE0/1`: SDP enablement, tag limits, response credits, and reserved credits across VC0-VC7, including the `DISTRIBUTE_POOL` controls.
- `DAGB0_SDP_ERR_STATUS`: read/write response status, read-response data status/parity error, clear-status, busy-on-error, fatal-error interrupt, level interrupt, and ignore-fatal-data/error controls.
- `DAGB0_SDP_REQ_CNTL`, `DAGB0_SDP_MISC_AON`, `DAGB0_SDP_MISC`, `DAGB0_SDP_MISC2`, `DAGB0_SDP_ARB_CNTL0/1`, `DAGB0_SDP_CGTT_CLK_CTRL`, and `DAGB0_SDP_LATENCY_SAMPLING`: request pass/post-write and chain overrides, block levels, early write-return enables, client-group VC mapping, arbitration override/retry policy, clock-gating/light-sleep timing, and latency sampling filters.
- `PCTL_CTRL`: global MMHUB power-control bits for power-gating enablement, MMHUB deepsleep mode, RSMU/DAGB idle thresholds, protection-fault ignore policy, EA partial/full ack overrides, and RSMU read-timer controls.
- `PCTL_MMHUB_DEEPSLEEP_IB`, `PCTL_MMHUB_DEEPSLEEP_OVERRIDE`, `PCTL_MMHUB_DEEPSLEEP_OVERRIDE_IB`, `PCTL_PG_IGNORE_DEEPSLEEP`, and `PCTL_PG_IGNORE_DEEPSLEEP_IB`: deepsleep input, override, and ignore bitmaps for DS0-DS16 plus ATHUB/CANE/IB-oriented control bits.
- `PCTL_SLICE0_*` and `PCTL_SLICE1_*`: per-slice DAGB read/write busy configuration, deepsleep allow bitmaps, register-engine pointers, critical-register lock bits, tile idle thresholds, memory light-sleep enablement, deep-sleep disconnect behavior, execute-on-update, and read-timer enablement.
- `PCTL_RENG_*` and `PCTL_*_STCTRL_REGISTER_SAVE_*`: register-engine execution, RAM index/data windows, and state-controller save range/exclusion sets for UTCL2 and both slices.
- `PCTL_STATUS`, `PCTL_PERFCOUNTER_LO/HI`, `PCTL_PERFCOUNTER0_CFG`, `PCTL_PERFCOUNTER1_CFG`, and `PCTL_PERFCOUNTER_RSLT_CNTL`: power-control status and performance-counter result/configuration fields.
- `MMMC_VM_MX_L1_TLB0_STATUS` through `TLB7_STATUS`: busy and parity-error status for eight L1 TLB instances.
- `MMMC_VM_MX_L1_PERFCOUNTER0_CFG` through `3_CFG`, `MMMC_VM_MX_L1_PERFCOUNTER_RSLT_CNTL`, and result low/high registers: L1 performance counter event selection, enable/clear controls, compare value, trigger selection, global enable/clear, and stop-on-saturate fields.
- `MMMC_VM_MX_L1_TLS0_CNTL` and `MMMC_VM_MX_L1_TLS0_CNTL0` through `CNTL37`: TLS range enablement, default/request behaviour, snoop, atomic, client ID, VMID, volatile, LRU, priority, and virtual-address high-bit matching for 38 TLS windows.
- `MMMC_VM_MX_L1_TLS0_START_ADDR{0..37}_{LO32,HI32}` and `END_ADDR{0..37}_{LO32,HI32}`: low/high split address bounds for those TLS windows.
- `MMMC_VM_MX_L1_TLS0_INVALIDATE_STREAM_*`, `INVALIDATE_REQUEST_PENDING_*`, `PROTECTION_FAULT_STATUS`, protection-fault address registers, and IOMMU fault status/GVADDR registers: TLS invalidation, pending-request, fault decode, and fault-address fields.
- `MMVM_L2_SAW_CNTL`, `CNTL2`, `CNTL3`, `CNTL4`, `CONTEXT0_CNTL`, `CONTEXT0_CNTL2`, page-table base/start/end registers, `CONTEXTS_DISABLE`, and `PIPES_BUSY_*`: SAW L2 page-walk, retry, context, and pipe-busy controls.
- `MM_ATC_L2_CNTL`, `CNTL2`, `CACHE_DATA0..2`, `CNTL3`, `CNTL4`, `CNTL5`, `MM_GROUP_RT_CLASSES`, `STATUS`, `STATUS2`, `MISC_CG`, `MEM_POWER_LS`, `CGTT_CLK_CTRL`, and `SDPPORT_CTRL`: ATC L2 translation-cache policy, cache-data inspection, invalidation/update mode, ATS credits, clock-gating, memory light-sleep, busy/error status, and SDP port clock-enable controls.
- `MMVM_L2_CNTL`, `MMVM_L2_CNTL2`, `MMVM_L2_CNTL3`, `MMVM_L2_STATUS`, `MMVM_DUMMY_PAGE_FAULT_*`, `MMVM_INVALIDATE_CNTL`, `MMVM_L2_PROTECTION_FAULT_CNTL`, and the beginning of `MMVM_L2_PROTECTION_FAULT_CNTL2`: main MMVM L2 cache enablement, invalidation, bank/fragment/effective-size policy, busy/parity status, dummy-page fault controls, and protection-fault default/interrupt/crash policy.

## Control Flow And State Behavior

This header has no runtime control flow. The C preprocessor substitutes the constants into driver code that performs MMIO reads, writes, read-modify-write updates, status decoding, or debug printing.

Runtime state lives in MMHUB hardware registers. DAGB0 SDP fields affect request prioritization, VC mapping, credits, arbitration, error status, and clock/latency policy for the SDP-facing path. PCTL fields control and observe power-gating, deepsleep, register save/restore, and slice-level state-control behavior. L1 TLB/TLS fields represent TLB busy/parity status, performance-counter state, translation-local-storage windows, invalidation request state, and fault latches. ATC L2 fields control translation-cache policy and clock/light-sleep behavior. MMVM L2 fields configure the central VM translation cache, invalidate L1/L2 translation state, expose busy/parity status, and define how dummy-page and protection faults are treated.

Some fields are plainly stateful request or latch controls: `CLEAR_ERROR_STATUS`, performance-counter `CLEAR` and `CLEAR_ALL`, invalidation request/pending bits, cache invalidation bits, `CLEAR_PROTECTION_FAULT_STATUS_ADDR`, `ALLOW_SUBSEQUENT_PROTECTION_FAULT_STATUS_ADDR_UPDATES`, and crash-on-fault controls. The header names their bit positions but does not encode access type, reset values, ordering requirements, or polling rules.

Persistence is hardware-local. Register values survive only according to MMHUB reset, power-gating, firmware, and driver initialization/save-restore behavior. The header does not store state itself. Driver code such as `mmhub_v3_0_1.c` owns the software policy: it programs the L2 cache, TLB, protection fault defaults, VM contexts, invalidation engine metadata, and clock-gating/light-sleep bits using these masks.

## Dependencies And Integration Points

The immediate dependency is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mmhub/mmhub_3_0_1_offset.h`. In that file, the late DAGB0 SDP registers in this chunk run from `regDAGB0_SDP_RD_BW_CNTL` at offset `0x00a1` through `regDAGB0_SDP_LATENCY_SAMPLING` at `0x00b8` in base block `0x68000`. The PCTL block starts at base address `0x68e00` with `regPCTL_CTRL` at `0x0380`. L1 TLB status begins at base `0x69600` with `regMMMC_VM_MX_L1_TLB0_STATUS` at `0x0588`. The MMVM L2 block begins at `regMMVM_L2_CNTL` offset `0x0680`, with `regMMVM_L2_PROTECTION_FAULT_CNTL2` at `0x0689`.

The direct local consumer is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/mmhub_v3_0_1.c`, which includes both `mmhub_3_0_1_offset.h` and this `mmhub_3_0_1_sh_mask.h`. Direct integrations visible there include:

- `mmhub_v3_0_1_init_system_aperture_regs()`: writes protection-fault default address registers and sets `MMVM_L2_PROTECTION_FAULT_CNTL2__ACTIVE_PAGE_MIGRATION_PTE_READ_RETRY`.
- `mmhub_v3_0_1_init_tlb_regs()`: programs L1 TLB control fields from an earlier chunk of this same header.
- `mmhub_v3_0_1_init_cache_regs()`: uses `MMVM_L2_CNTL`, `MMVM_L2_CNTL2`, and `MMVM_L2_CNTL3` fields from this chunk to enable L2 cache, set default-page-out behavior, trigger L1/L2 invalidation, and tune bank/large-fragment policy.
- `mmhub_v3_0_1_gart_disable()`: clears L1 TLB enablement and disables `MMVM_L2_CNTL__ENABLE_L2_CACHE`, then clears `regMMVM_L2_CNTL3`.
- `mmhub_v3_0_1_set_fault_enable_default()`: uses `MMVM_L2_PROTECTION_FAULT_CNTL` masks in this chunk to switch range/PDE/NACK/dummy/valid/read/write/execute faults between default-page handling and crash-on-fault behavior.
- `mmhub_v3_0_1_update_medium_grain_clock_gating()`, `mmhub_v3_0_1_update_medium_grain_light_sleep()`, and `mmhub_v3_0_1_get_clockgating()`: read or modify `MM_ATC_L2_MISC_CG__ENABLE_MASK` and `MM_ATC_L2_MISC_CG__MEM_LS_ENABLE_MASK` from this chunk.

The same macro families are mirrored in neighboring generation files such as `mmhub_3_0_0_sh_mask.h`, `mmhub_3_0_2_sh_mask.h`, and later MMHUB versions. Those are useful for sanity checking generated patterns, but call sites must include the header matching the selected ASIC/IP version because field positions and client maps are generation-specific.

## Risks And Edge Cases

- These macros are a hardware ABI. A wrong shift or mask compiles cleanly but can program the wrong bit in MMHUB hardware, producing stale translations, bad arbitration, incorrect fault routing, hangs, or hard-to-debug power-state failures.
- The chunk starts inside `DAGB0_SDP_PRIORITY_OVERRIDE`; the omitted beginning contains the first fields for override slot 0. Whole-register documentation must merge this with the previous chunk.
- The chunk ends inside `MMVM_L2_PROTECTION_FAULT_CNTL2`; the masks after `CLIENT_ID_PRT_FAULT_INTERRUPT_MASK` and later fault/status/address fields are in the next chunk.
- Many repeated packed fields cover VCs, DS bits, slices, TLB instances, TLS windows, and address-window indices. Off-by-one shifts or incorrect register-family selection can affect only one client, VMID, window, or slice, making failures sparse and platform-dependent.
- Status, clear, invalidate, and performance-counter controls are mixed with ordinary configuration fields. Treating all masks as persistent settings can clear fault evidence, request unintended invalidations, reset counters, or leave fault status updates blocked.
- Protection-fault policy is security and stability sensitive. Misprogramming `*_ENABLE_DEFAULT`, `CLIENT_ID_NO_RETRY_FAULT_INTERRUPT`, `CRASH_ON_NO_RETRY_FAULT`, or `CRASH_ON_RETRY_FAULT` can either hide real faults behind dummy/default pages or escalate recoverable faults into GPU resets.
- L2 cache and invalidation fields are central to VM correctness. Incorrect `ENABLE_L2_CACHE`, `INVALIDATE_ALL_L1_TLBS`, `INVALIDATE_L2_CACHE`, VMID mode, bank selection, fragment size, or force-miss masks can leave stale translations after page-table updates.
- PCTL and ATC clock/light-sleep fields can fail only under suspend/resume, runtime power management, SR-IOV policy, low-power entry/exit, or specific display/media traffic mixes.
- Full-width masks such as address low words and register-engine data fields should be treated as unsigned 32-bit values. Signed promotion or wrong debug formatting can make register dumps misleading.
- Reserved and save-range/exclusion fields preserve generated register-map shape; their presence is not a guarantee that normal driver code may write arbitrary values safely.

## Test And Validation Signals

There are no direct unit tests for this macro-only header chunk. Useful validation signals are compile, static, and hardware integration checks:

- Build AMDGPU configurations that include `mmhub_v3_0_1.c`, `mmhub_3_0_1_offset.h`, and `mmhub_3_0_1_sh_mask.h`.
- Run static mask/shift checks: single-bit masks should equal `1U << shift`; multi-bit masks should be contiguous after shifting; repeated VC/DS/TLS/address fields should not overlap; full-width fields should have shift zero.
- Cross-check every register-comment group in this chunk against `mmhub_3_0_1_offset.h` so offsets, base indices, and generated register names stay aligned.
- Boot supported MMHUB 3.0.1 hardware and exercise GART enable/disable, VMID setup, page-table updates, and VM invalidations. Register dumps should show expected changes to `MMVM_L2_CNTL*`, protection-fault controls, and ATC clock-gating fields.
- Trigger or inspect VM protection faults to validate `MMVM_L2_PROTECTION_FAULT_CNTL`, `CNTL2`, and status decode paths used by `mmhub_v3_0_1_print_l2_protection_fault_status()`.
- Toggle medium-grain clock gating/light sleep and verify `MM_ATC_L2_MISC_CG__ENABLE_MASK` and `MEM_LS_ENABLE_MASK` round-trip through `set_clockgating()` and `get_clockgating()`.
- Use register dumps around suspend/resume or power-gating transitions to validate PCTL save ranges, deepsleep allow/override/ignore masks, and slice misc fields.
- For performance-counter fields, validate that enabling, clearing, trigger selection, high/low reads, and stop-on-saturate behavior match the hardware guide.

## Chunk Notes For Merge Lane

This is a middle chunk of `mmhub_3_0_1_sh_mask.h`. It should be merged with the previous chunk for the complete `DAGB0_SDP_PRIORITY_OVERRIDE` register and with the next chunk for the complete `MMVM_L2_PROTECTION_FAULT_CNTL2` and subsequent MMVM L2 protection-fault/status/address definitions. Whole-file research should treat this slice as the bridge from late DAGB0 SDP/QoS controls through power management, L1 TLB/TLS, ATC L2, and the start of MMVM L2 fault policy.
